You have a big JavaScript object. You want a small JavaScript object made of some of its properties. This is one of the most common things we do as developers, and for flat objects the tools we have are fine.

But once the data gets **nested**, and especially once **arrays** show up, things start to get ugly. This post is about a weird fix that works better than it has any right to: describing the shape you want with GraphQL syntax.

## The problem

Say you've fetched a user from some API and you get back something like this:

```js
const user = {
  id: 42,
  username: "ada",
  email: "ada@example.com",
  passwordHash: "$2b$10$...",
  profile: {
    displayName: "Ada L.",
    bio: "Analytical engines enthusiast",
    avatar: { url: "https://cdn.example.com/ada.png", width: 256, height: 256 },
    internalNotes: "VIP, do not ban",
  },
  posts: [
    { id: 1, title: "Notes on the Engine", body: "...", views: 1200, draft: false },
    { id: 2, title: "Bernoulli Numbers", body: "...", views: 980, draft: true },
  ],
};
```

You want to send a trimmed version to the client: id, username, display name, avatar URL, and the id and title of each post. No email, no password hash, no internal notes.

### Attempt 1: destructuring

```js
const {
  id,
  username,
  profile: {
    displayName,
    avatar: { url },
  },
  posts,
} = user;

const publicUser = {
  id,
  username,
  profile: { displayName, avatar: { url } },
  posts: posts.map(({ id, title }) => ({ id, title })),
};
```

This works, but you write the shape **twice**: once to take it apart and once to put it back together. It also throws if `profile` or `avatar` is ever `undefined`, and the array needs its own `.map`.

### Attempt 2: lodash `pick`

```js
import pick from "lodash/pick";

pick(user, ["id", "username", "profile.displayName", "profile.avatar.url"]);
```

This is better. Dot paths handle nesting and missing values don't crash. But `pick` has no good answer for "this field from every item in this array." You're back to mapping by hand:

```js
{
  ...pick(user, ["id", "username", "profile.displayName", "profile.avatar.url"]),
  posts: user.posts.map((p) => pick(p, ["id", "title"])),
}
```

It's fine, but the shape you're after is scattered across string paths and code.

## Wait, we already have a language for this

Look at what we're trying to express:

> From this object, give me `id`, `username`, from `profile` give me `displayName` and the `url` of `avatar`, and for each of the `posts` give me `id` and `title`.

Now look at this:

```graphql
{
  id
  username
  profile {
    displayName
    avatar {
      url
    }
  }
  posts {
    id
    title
  }
}
```

That's a GraphQL query, and it describes **exactly** the shape we want. GraphQL was built for "here's a tree of fields, give me just this part of it." Nested objects are braces. Arrays are handled implicitly: if a field is a list, the selection applies to each item. The query looks just like the output.

Nothing about that syntax requires a GraphQL server, a schema, or a network request. It's just a nice way to describe a subset of a tree. So let's use it on plain objects.

## Option A: `graphql-anywhere`

Apollo shipped a small library called `graphql-anywhere` that has a `filter` function for this exact job:

```js
import gql from "graphql-tag";
import { filter } from "graphql-anywhere";

const PublicUser = gql`
  {
    id
    username
    profile {
      displayName
      avatar { url }
    }
    posts {
      id
      title
    }
  }
`;

const publicUser = filter(PublicUser, user);
```

It works, but `graphql-anywhere` hasn't been actively developed in years, and pulling in an old Apollo package to filter some objects feels heavy. So let's build our own. It's shorter than you'd think.

## Option B: build it yourself in ~30 lines

The official `graphql` package exports `parse`, which turns a query string into an AST (Abstract Syntax Tree). Parsing is all we need from it. We don't need a schema, validation, or execution.

A parsed query is a document with `definitions`. The first one is our operation, and it has a `selectionSet`: a list of `selections`, each of which is a `Field` with a `name`, an optional `alias`, and an optional nested `selectionSet` of its own.

So the algorithm is:

1. If the value is `null`/`undefined`, return it as-is.
2. If the value is an array, apply the selection to each item.
3. Otherwise, for each selected field, copy it over. If the field has its own selection set, recurse.

```js
import { parse } from "graphql";

export function select(query, data) {
  const doc = typeof query === "string" ? parse(query) : query;
  const operation = doc.definitions.find((d) => d.kind === "OperationDefinition");
  return applySelection(operation.selectionSet, data);
}

function applySelection(selectionSet, value) {
  if (value == null) return value;
  if (Array.isArray(value)) {
    return value.map((item) => applySelection(selectionSet, item));
  }

  const result = {};
  for (const selection of selectionSet.selections) {
    if (selection.kind !== "Field") continue;

    const key = selection.name.value;
    if (!(key in value)) continue;

    const outKey = selection.alias?.value ?? key;
    result[outKey] = selection.selectionSet
      ? applySelection(selection.selectionSet, value[key])
      : value[key];
  }
  return result;
}
```

And using it:

```js
const publicUser = select(
  `{
    id
    username
    profile {
      displayName
      avatar { url }
    }
    posts { id title }
  }`,
  user
);
```

```js
{
  id: 42,
  username: "ada",
  profile: { displayName: "Ada L.", avatar: { url: "https://cdn.example.com/ada.png" } },
  posts: [
    { id: 1, title: "Notes on the Engine" },
    { id: 2, title: "Bernoulli Numbers" },
  ],
}
```

No `.map`, no repeated shapes, and no crash if `avatar` is missing.

## Free features: aliases

Because we're reading a real GraphQL AST, we get some of GraphQL's syntax for free. **Aliases** already work in the code above, which means you can rename fields while you pick them:

```js
select(
  `{
    userId: id
    name: username
    profile {
      avatar: avatar { src: url }
    }
  }`,
  user
);
// { userId: 42, name: "ada", profile: { avatar: { src: "https://..." } } }
```

Renaming keys to match a frontend's expected shape is a common chore, and here it's just part of the query.

## Reusable shapes with fragments

The real power move is **fragments**. Say several of your responses include a post summary. Define the fragment once and spread it wherever you need it:

```graphql
fragment PostSummary on Post {
  id
  title
}

{
  username
  posts { ...PostSummary }
  pinnedPost { ...PostSummary }
}
```

The `on Post` part is required syntax, but we have no schema, so we just ignore it. Supporting fragments takes a few more lines: collect the fragment definitions up front, then expand spreads (and inline fragments) when you find them.

```js
export function select(query, data) {
  const doc = typeof query === "string" ? parse(query) : query;
  const fragments = {};
  let operation;

  for (const def of doc.definitions) {
    if (def.kind === "FragmentDefinition") fragments[def.name.value] = def;
    if (def.kind === "OperationDefinition") operation = def;
  }

  return applySelection(operation.selectionSet, data, fragments);
}

function applySelection(selectionSet, value, fragments) {
  if (value == null) return value;
  if (Array.isArray(value)) {
    return value.map((item) => applySelection(selectionSet, item, fragments));
  }

  const result = {};
  for (const selection of selectionSet.selections) {
    if (selection.kind === "FragmentSpread") {
      const fragment = fragments[selection.name.value];
      if (!fragment) throw new Error(`Unknown fragment: ${selection.name.value}`);
      Object.assign(result, applySelection(fragment.selectionSet, value, fragments));
      continue;
    }
    if (selection.kind === "InlineFragment") {
      Object.assign(result, applySelection(selection.selectionSet, value, fragments));
      continue;
    }

    const key = selection.name.value;
    if (!(key in value)) continue;

    const outKey = selection.alias?.value ?? key;
    result[outKey] = selection.selectionSet
      ? applySelection(selection.selectionSet, value[key], fragments)
      : value[key];
  }
  return result;
}
```

> ⚠️ One caveat: `Object.assign` does a shallow merge. If two fragments select different subfields of the same nested object, the second one wins instead of the two being combined. Real GraphQL merges them. If you need that, swap in a small recursive merge.

## Practical tips

**Parse once, not on every call.** Parsing isn't free. If you're filtering in a hot path, like every API response, parse the query at module load and pass the AST in:

```js
const PUBLIC_USER = parse(`{ id username profile { displayName } }`);

app.get("/users/:id", async (req, res) => {
  const user = await db.users.find(req.params.id);
  res.json(select(PUBLIC_USER, user));
});
```

**Get syntax highlighting.** If you tag your strings with `gql` (from `graphql-tag`) or a `/* GraphQL */` comment, most editors' GraphQL extensions will highlight and format them. A tiny `gql` wrapper that just returns `parse(strings.join(""))` works too.

**It's an allowlist, which is a good default for security.** Filtering by "fields to include" means a new `passwordResetToken` column added next month won't leak by accident. With `omit`-style denylists, it would.

## When *not* to do this

Let's be honest about the tradeoffs:

- **TypeScript loses track.** `select` returns `any` (or `unknown`) unless you add serious type-level work. Tools like GraphQL Code Generator can produce types, but only with a schema. If static types on your output matter a lot, a typed mapper function or a validation library like Zod (`schema.pick()` / `.strip()`) may suit you better.
- **It's a dependency.** `graphql` isn't tiny. If you're already using it, the cost is nothing. If you're not, think about whether ~100KB of parser is worth it for your use case, especially in a browser bundle.
- **Teammates may raise an eyebrow.** "Why is there GraphQL in our REST API?" is a fair question. A short comment pointing to this approach helps a lot.
- **Simple cases don't need it.** If you're picking three top-level keys, use destructuring. This approach pays off with nesting, arrays, and shapes you reuse.

## Wrapping up

GraphQL's query language turns out to be a great DSL (Domain-Specific Language) for one of the most boring jobs in JavaScript: "give me this part of that object." It handles nesting and arrays naturally, supports renaming and reusable fragments, and reads like the output it produces. Thanks to `graphql`'s `parse`, you can have it in about 30 lines, with no server or schema involved.

Is it a little weird? Sure. But the next time you're halfway through your fourth nested `.map(({ id, title }) => ({ id, title }))`, it might start to look less weird and more like the right tool.

Have you used GraphQL syntax outside of GraphQL? Let me know in the comments. 👇

---

That's about 1,400 words. I can save it as a `.md` file, adjust the tone, or add a cover image suggestion if you'd like.

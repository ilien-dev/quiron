# Grabbing Subsets of JS Object Properties with... GraphQL?

Here's a problem every JavaScript developer runs into eventually: you have a big object, and you only want a few of its properties. Maybe you're trimming an API response before sending it to the client. Maybe you're logging a user without dumping their password hash into your logs. Maybe you just want a smaller, cleaner object to pass around.

JavaScript gives us a few ways to do this, and none of them are perfect. So let's take a detour through the usual suspects, and then try something a little weird: using GraphQL syntax to pick properties off a plain JS object.

## The problem

Say we have this user object:

```javascript
const user = {
  id: 42,
  name: 'Ada Lovelace',
  email: 'ada@example.com',
  passwordHash: '$2b$10$...',
  address: {
    street: '12 St James Square',
    city: 'London',
    postcode: 'SW1Y 4JH',
    country: 'UK',
  },
  preferences: {
    theme: 'dark',
    notifications: {
      email: true,
      sms: false,
    },
  },
  createdAt: '1843-07-10',
};
```

We want a trimmed version with `id`, `name`, the `city` from the address, and the `theme` from preferences. Nothing else.

## Option 1: Just write it out

The most obvious approach:

```javascript
const trimmed = {
  id: user.id,
  name: user.name,
  address: {
    city: user.address.city,
  },
  preferences: {
    theme: user.preferences.theme,
  },
};
```

This works. It's explicit, it's readable, and there's no magic. But it's repetitive, and it gets noisy fast as the object gets deeper. You're typing `user.` over and over, and the shape you want is buried in assignment syntax.

## Option 2: Destructuring

Destructuring can make this a bit cleaner:

```javascript
const {
  id,
  name,
  address: { city },
  preferences: { theme },
} = user;

const trimmed = { id, name, address: { city }, preferences: { theme } };
```

Better, but now we have to describe the shape twice: once to pull the values out, and again to put them back together. And if `address` happens to be `undefined`, the whole thing throws.

## Option 3: Lodash `pick`

Lodash has `_.pick`, which takes paths:

```javascript
import pick from 'lodash/pick';

const trimmed = pick(user, ['id', 'name', 'address.city', 'preferences.theme']);
```

This is concise and handles nesting. It's probably what most people reach for. The downside is that paths are strings in an array, which isn't the most readable format for deeply nested data, and you don't get a clear visual of the output shape.

## A different idea: describe the shape you want

Look at what we're really doing here. We have a big data structure, and we want to describe the *shape* of the subset we care about. The result should mirror that description.

That's... exactly what GraphQL queries do.

```graphql
{
  id
  name
  address {
    city
  }
  preferences {
    theme
  }
}
```

If you've used GraphQL, this reads naturally. You list the fields you want, nest braces for nested objects, and the response comes back in exactly that shape. There's no duplication, no string paths, and the query looks like the output.

So why not use this syntax on plain objects?

## Using graphql-anywhere (or rolling your own)

There's an Apollo package called `graphql-anywhere` that runs a GraphQL query against arbitrary data with a custom resolver. Its `filter` utility does precisely what we want:

```javascript
import { filter } from 'graphql-anywhere';
import gql from 'graphql-tag';

const query = gql`
  {
    id
    name
    address {
      city
    }
    preferences {
      theme
    }
  }
`;

const trimmed = filter(query, user);
// {
//   id: 42,
//   name: 'Ada Lovelace',
//   address: { city: 'London' },
//   preferences: { theme: 'dark' }
// }
```

No schema, no server, no resolvers. Just a query and an object.

That said, `graphql-anywhere` is no longer actively maintained, and pulling in the whole Apollo toolchain for this might feel heavy. The good news is that building a tiny version yourself is a fun exercise, and it shows how simple the idea really is.

## Building a minimal version

We'll use the `graphql` package's parser to turn the query into an AST, then walk it alongside our object.

```javascript
import { parse } from 'graphql';

function pickWithQuery(obj, queryString) {
  const ast = parse(queryString);
  const selectionSet = ast.definitions[0].selectionSet;
  return applySelection(obj, selectionSet);
}

function applySelection(value, selectionSet) {
  if (value == null) return value;

  if (Array.isArray(value)) {
    return value.map((item) => applySelection(item, selectionSet));
  }

  const result = {};
  for (const selection of selectionSet.selections) {
    const key = selection.name.value;
    const alias = selection.alias ? selection.alias.value : key;
    const fieldValue = value[key];

    result[alias] = selection.selectionSet
      ? applySelection(fieldValue, selection.selectionSet)
      : fieldValue;
  }
  return result;
}
```

That's about 25 lines. Let's try it:

```javascript
const trimmed = pickWithQuery(user, `
  {
    id
    name
    address { city }
    preferences { theme }
  }
`);
```

And we get exactly the shape we asked for.

## Free features

Because we're working with a real GraphQL AST, a few nice things come along almost for free.

**Aliases.** GraphQL lets you rename fields in the output. Our implementation already handles this:

```javascript
pickWithQuery(user, `
  {
    userId: id
    displayName: name
    address { town: city }
  }
`);
// { userId: 42, displayName: 'Ada Lovelace', address: { town: 'London' } }
```

**Arrays.** Since we map over arrays, you can pick fields from lists of objects:

```javascript
const users = [user, anotherUser, yetAnotherUser];

pickWithQuery({ users }, `
  {
    users {
      id
      name
    }
  }
`);
```

**Null safety.** If `address` is missing, we return `null` or `undefined` for it instead of throwing. That's a real improvement over nested destructuring.

**Reusability.** Queries are just strings (or parsed documents), so you can define them once and reuse them. You could even cache the parsed AST to avoid reparsing every time:

```javascript
const PUBLIC_USER = parse(`
  {
    id
    name
    address { city country }
  }
`);
```

## Should you actually do this?

It depends.

**Reasons you might like it:**

- The query mirrors the output, so it's easy to see what you'll get.
- It handles deep nesting and arrays gracefully.
- If your team already uses GraphQL, the syntax is instantly familiar.
- Aliases give you renaming for free.

**Reasons to be cautious:**

- It adds a dependency on the `graphql` parser, which isn't tiny (around 40kb minified for the whole package, although you only need the parser).
- It's unfamiliar to people who haven't used GraphQL. Someone reading your code might be confused why there's a GraphQL query in a function that never talks to a server.
- There's a parsing cost at runtime, unless you pre-parse.
- Type inference is lost. TypeScript won't know the shape of the result unless you add tooling like GraphQL Code Generator or write types by hand.

For small, one-off picks, plain destructuring or `lodash/pick` is probably fine. But if you find yourself shaping lots of nested data, especially in something like a serialization layer or a BFF (backend-for-frontend) where you're trimming large payloads, the GraphQL approach can be surprisingly pleasant.

## Taking it further

If you like this idea, there's room to grow it:

- **Fragments.** Support `...on` and named fragments so you can compose reusable selections.
- **Arguments.** Use field arguments as transformations, like `createdAt(format: "YYYY")` or `name(upper: true)`.
- **Directives.** Implement `@include(if: $flag)` and `@skip` to conditionally include fields based on variables.
- **Tagged templates.** Wrap it in a `gql`-style tagged template so editors highlight the syntax.

At that point, you've basically reinvented a local GraphQL executor, which is a sign that the idea holds up pretty well.

## Wrapping up

GraphQL is usually pitched as an API technology, but at its core, a GraphQL query is just a clean way to describe the shape of data you want. That idea is useful anywhere, including on a plain old JavaScript object sitting in memory.

Next time you catch yourself writing `user.address.city` for the fifth time in a row, consider whether a tiny query might say it better. And even if you never ship this in production, writing the 25-line version is a great way to understand how GraphQL execution actually works under the hood.

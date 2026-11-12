# Three New Next.js Features and How to Use Them

Every major Next.js release brings a long changelog, and most of it you can skim. Next.js 16 is different. A few of its changes affect how you structure an app, especially around caching, which has confused people for years.

This post covers three features worth learning now:

1. **Cache Components** and the `"use cache"` directive
2. **`proxy.ts`**, the replacement for `middleware.ts`
3. **`updateTag()`, `refresh()`, and the revised `revalidateTag()`**

For each one, you'll see what problem it solves, how to turn it on, and code you can adapt.

---

## 1. Cache Components and `"use cache"`

### The problem

In older App Router versions, caching was mostly *implicit*. `fetch` calls were cached by default (and later weren't). Route segments became static or dynamic depending on which APIs you happened to call. You also had a set of exports like `dynamic`, `revalidate`, and `fetchCache` for overriding that behavior. Many developers learned the rules by shipping a stale page to production.

Cache Components flips the model. **Everything is dynamic by default, and you opt into caching explicitly.** Next.js then combines the cached and dynamic parts of a page with Partial Prerendering (PPR). The static shell is served instantly, and the dynamic holes are streamed in.

### Turning it on

Cache Components is opt-in through your config:

```ts
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  cacheComponents: true,
};

export default nextConfig;
```

### Using `"use cache"`

The `"use cache"` directive works much like `"use client"` or `"use server"`. You can put it at the top of a file, inside a component, or inside an async function:

```tsx
// app/products/page.tsx
import { Suspense } from 'react';
import { cacheLife, cacheTag } from 'next/cache';
import { CartBadge } from './cart-badge';

async function getProducts() {
  'use cache';
  cacheLife('hours');
  cacheTag('products');

  const res = await fetch('https://api.example.com/products');
  return res.json();
}

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <main>
      <header>
        <h1>Products</h1>
        <Suspense fallback={<span>…</span>}>
          <CartBadge />
        </Suspense>
      </header>

      <ul>
        {products.map((p: { id: string; name: string }) => (
          <li key={p.id}>{p.name}</li>
        ))}
      </ul>
    </main>
  );
}
```

Here's what each piece does:

- **`'use cache'`** marks `getProducts` as cacheable. The compiler generates a cache key from the function and its serializable arguments, so you don't write keys by hand.
- **`cacheLife('hours')`** sets how long the entry stays fresh. Built-in profiles include `'seconds'`, `'minutes'`, `'hours'`, `'days'`, `'weeks'`, and `'max'`, and you can define your own in `next.config.ts`.
- **`cacheTag('products')`** labels the entry so you can invalidate it later. We'll use this in section 3.

### What about dynamic data?

`CartBadge` probably reads cookies to find the user's cart. That's per-request data, so it can't be part of a cached shell. With Cache Components enabled, Next.js makes you handle this explicitly. If you access `cookies()`, `headers()`, or other request-time data outside a `<Suspense>` boundary, you'll get an error during development telling you to either cache the work or wrap it in Suspense.

That error can feel strict at first. It's actually useful, because the "why is my whole page dynamic?" question now gets answered at build time instead of in production.

```tsx
// app/products/cart-badge.tsx
import { cookies } from 'next/headers';

export async function CartBadge() {
  const cartId = (await cookies()).get('cart')?.value;
  const count = cartId ? await getCartCount(cartId) : 0;
  return <span>{count} items</span>;
}
```

The result is a page whose product list is prerendered and served from cache, while the cart badge streams in per request.

### Migration tip

When you enable `cacheComponents`, the old route segment configs (`export const dynamic = ...`, `export const revalidate = ...`) are no longer the way to control caching. Move them to `"use cache"` and `cacheLife`. Start with your highest-traffic pages, enable the flag, and fix the errors the dev server reports one at a time.

---

## 2. `proxy.ts` Replaces `middleware.ts`

### The problem

"Middleware" in Next.js never meant quite what it means in Express or Koa. It ran *before* routing, at the network boundary, and was mostly used for redirects, rewrites, header manipulation, and lightweight auth checks. The name made people expect a request pipeline they could stack logic into, and that led to some painful architectures.

Next.js 16 renames the file to describe what it does: it's a **proxy** that sits in front of your app.

### Migrating

You rename the file and the exported function:

```ts
// proxy.ts (formerly middleware.ts)
import { NextResponse, type NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const session = request.cookies.get('session');

  if (!session && request.nextUrl.pathname.startsWith('/dashboard')) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('from', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
```

The logic and the `matcher` config work the same way. There's also a codemod that does the rename for you:

```bash
npx @next/codemod@canary middleware-to-proxy .
```

### Things to know

- **`proxy.ts` runs on the Node.js runtime.** If you depend on the Edge runtime, you can keep using `middleware.ts` for now, but it's deprecated and will be removed in a future version.
- **Config flags were renamed** to match. For example, `skipMiddlewareUrlNormalize` is now `skipProxyUrlNormalize`. The codemod handles the common ones, but search your config to be sure.
- **Keep it thin.** The rename is also a hint about what belongs here. Do redirects, rewrites, and cheap checks on headers or cookies in the proxy. Do real authorization next to your data, in Server Components, Server Actions, or Route Handlers, where you can verify the session properly. A proxy check is a fast first filter, not your security boundary.

---

## 3. `updateTag()`, `refresh()`, and the Revised `revalidateTag()`

### The problem

Once you tag cached data, you need a way to invalidate it after a mutation. `revalidateTag()` has existed for a while, but it had a UX problem. After a user saved a change, they might briefly see the *old* value, because revalidation happened in the background. Developers also used it for cases where they didn't really want cache invalidation at all. They just wanted the page to re-fetch some live data.

Next.js 16 splits these use cases into three APIs.

### `updateTag()`: read-your-writes

Use `updateTag()` in a **Server Action** when the user who made a change needs to see it right away:

```ts
// app/products/actions.ts
'use server';

import { updateTag } from 'next/cache';

export async function renameProduct(id: string, name: string) {
  await db.product.update({ where: { id }, data: { name } });

  // Expire the cache and refresh it within this same request.
  updateTag('products');
}
```

The cached entry expires immediately, and the response to this action includes fresh data. The user never sees the stale name. `updateTag()` only works inside Server Actions, which fits its purpose: it's tied to a specific user's mutation.

### `revalidateTag(tag, profile)`: stale-while-revalidate

`revalidateTag()` now takes a **second argument**, a `cacheLife` profile. That makes the stale-while-revalidate behavior explicit:

```ts
import { revalidateTag } from 'next/cache';

// e.g. inside a webhook Route Handler from your CMS
export async function POST() {
  revalidateTag('products', 'max');
  return Response.json({ ok: true });
}
```

Visitors keep getting the cached version while a fresh one is generated in the background. This is the right choice when slightly stale content is fine, such as a CMS publish, a nightly import, or a product catalog edited by an admin rather than by the person viewing it. The single-argument form is deprecated, so add a profile when you upgrade.

### `refresh()`: re-fetch uncached data only

Sometimes the data that changed was never cached. Examples include a notification count, a live status indicator, or anything read per request. For those cases, use `refresh()`:

```ts
'use server';

import { refresh } from 'next/cache';

export async function markAllRead(userId: string) {
  await db.notification.updateMany({
    where: { userId },
    data: { read: true },
  });

  refresh();
}
```

`refresh()` doesn't touch the cache. It tells the client router to re-render the dynamic parts of the page so that uncached components, like our `CartBadge` from earlier, pick up the new state.

### Picking the right one

| Situation | API |
| --- | --- |
| User edits something and must see it immediately | `updateTag()` |
| Content changed elsewhere; brief staleness is fine | `revalidateTag(tag, 'max')` |
| Only uncached, per-request data changed | `refresh()` |

---

## How These Fit Together

These three features are connected:

- **Cache Components** make caching explicit: you mark what's cached with `"use cache"` and label it with `cacheTag`.
- **The new invalidation APIs** let you say exactly how those labels should be refreshed after a change.
- **`proxy.ts`** clarifies the edge of your app, so request-time logic stays small and real logic lives next to your data.

The overall direction is away from implicit behavior and toward code that states its intent. You write a bit more (a directive here, a Suspense boundary there), and in exchange you can predict what your app will do in production.

If you're upgrading an existing project, here's a reasonable order:

1. Run the `middleware-to-proxy` codemod. It's mechanical and low-risk.
2. Add a profile argument to your existing `revalidateTag()` calls.
3. Enable `cacheComponents` and migrate route by route, fixing the Suspense errors as they come up.
4. Swap `revalidateTag()` for `updateTag()` in Server Actions where users expect to see their own changes immediately.

Have you tried any of these yet? I'd like to hear in the comments how the Cache Components migration went for you, especially in larger codebases.

---

*Written against Next.js 16. APIs evolve quickly, so check the [official docs](https://nextjs.org/docs) for the latest details.*

---

It's about 1,400 words of prose, not counting code. The front matter has `published: false`, so it will save as a draft on dev.to. Want me to save it to a `.md` file or adjust the tone or length?

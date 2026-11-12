Next.js 16 changed how caching works, gave you finer control over invalidation, and renamed one of the framework's most misunderstood files. All three features in this post shipped with that release:

1. Cache Components and the `"use cache"` directive
2. The new invalidation APIs: `updateTag()`, `revalidateTag()` with a profile, and `refresh()`
3. `proxy.ts`, the replacement for `middleware.ts`

To follow along, you need Next.js 16 or later and Node.js 20.9+. The upgrade codemod handles most of the mechanical work:

```bash
npx @next/codemod@canary upgrade latest
```

## 1. Cache Components and `"use cache"`

Caching in the App Router used to be implicit. `fetch` calls were cached or not depending on the version, and routes switched between static and dynamic based on which APIs you touched. Working out why a page was stale often meant reading the docs twice.

Cache Components reverses the default. Everything runs at request time unless you say otherwise, and you opt in to caching with a directive.

Enable it in your config:

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
}

export default nextConfig
```

This flag replaces the older `experimental.ppr` and `experimental.dynamicIO` options.

Now mark what should be cached. The directive works at the top of a file, a component, or a single function:

```tsx
// app/products/page.tsx
import { Suspense } from 'react'
import { cookies } from 'next/headers'
import { cacheLife, cacheTag } from 'next/cache'
import { db } from '@/lib/db'

async function getProducts() {
  'use cache'
  cacheLife('hours')
  cacheTag('products')

  return db.product.findMany()
}

async function ProductList() {
  const products = await getProducts()
  return (
    <ul>
      {products.map((p) => (
        <li key={p.id}>{p.name}</li>
      ))}
    </ul>
  )
}

async function CartCount() {
  const cart = (await cookies()).get('cart')?.value
  const count = cart ? JSON.parse(cart).length : 0
  return <span>Cart ({count})</span>
}

export default function Page() {
  return (
    <main>
      <h1>Products</h1>
      <ProductList />
      <Suspense fallback={<span>Cart (…)</span>}>
        <CartCount />
      </Suspense>
    </main>
  )
}
```

A few things are happening here:

- **`getProducts` is cached.** The compiler generates the cache key from the function's arguments and any values it closes over, so you don't write key arrays by hand.
- **`cacheLife('hours')`** picks a built-in lifetime profile. Others include `'minutes'`, `'days'`, and `'max'`, and you can define your own in `next.config.ts`.
- **`cacheTag('products')`** labels the entry so you can invalidate it later.
- **`CartCount` is dynamic.** It reads cookies, so it sits inside a `<Suspense>` boundary.

The result is Partial Prerendering without extra configuration. The heading, the product list, and the cart fallback become a static shell that is served immediately. The real cart count streams in afterwards.

Two rules cause most of the errors:

- **Uncached data needs a Suspense boundary.** If you await something dynamic outside one, the build fails with an error about uncached data accessed outside `<Suspense>`. Either cache that data or wrap the component.
- **No request APIs inside a cached scope.** You can't call `cookies()` or `headers()` inside `"use cache"`. Read the value outside and pass it in as an argument, where it becomes part of the cache key:

```tsx
async function getRecommendations(userId: string) {
  'use cache'
  cacheLife('minutes')
  return db.recommendation.findMany({ where: { userId } })
}
```

Migrating an existing app is easiest one route at a time. Turn the flag on, let the build tell you which routes access uncached data, and decide for each whether it should be cached or streamed.

## 2. `updateTag()`, `revalidateTag()` and `refresh()`

Once caching is explicit, invalidation needs to be precise as well. Next.js 16 splits it into three functions, each with a clear job. All three are imported from `next/cache`.

### `updateTag()`: read your own writes

Use this in Server Actions when the user has just changed something and must see the result straight away:

```ts
// app/products/actions.ts
'use server'

import { updateTag } from 'next/cache'
import { db } from '@/lib/db'

export async function renameProduct(id: string, name: string) {
  await db.product.update({ where: { id }, data: { name } })
  updateTag('products')
}
```

`updateTag` expires the tagged entries immediately, and the response to the action contains fresh data. The user never sees the old name after saving. It only works inside Server Actions and throws if you call it elsewhere.

### `revalidateTag()`: stale-while-revalidate

`revalidateTag` now takes a second argument, a cache life profile. The single-argument form is deprecated.

```ts
// app/api/webhooks/cms/route.ts
import { revalidateTag } from 'next/cache'

export async function POST(request: Request) {
  const { type } = await request.json()

  if (type === 'product.updated') {
    revalidateTag('products', 'max')
  }

  return Response.json({ ok: true })
}
```

With a profile, tagged entries are marked stale rather than deleted. The next visitor gets the cached version instantly while a fresh one is generated in the background. That suits changes that come from outside the user's session, such as CMS webhooks, cron jobs, and background syncs, where a few seconds of staleness is fine and a slow response is not.

As a rule of thumb:

| Situation | Use |
|---|---|
| User submitted a form and expects to see the change | `updateTag(tag)` |
| Content changed externally, eventual consistency is fine | `revalidateTag(tag, 'max')` |
| Uncached data elsewhere on the page needs to update | `refresh()` |

### `refresh()`: re-render uncached data

Sometimes a Server Action changes something that isn't cached at all, such as a notification count rendered dynamically in the header. `refresh()` tells the client router to fetch that data again without touching the cache:

```ts
'use server'

import { refresh } from 'next/cache'
import { db } from '@/lib/db'

export async function markAsRead(id: string) {
  await db.notification.update({ where: { id }, data: { read: true } })
  refresh()
}
```

It's the server-side counterpart to calling `router.refresh()` on the client, and it is also limited to Server Actions.

## 3. `proxy.ts` replaces `middleware.ts`

The `middleware.ts` file was always misleadingly named. People assumed it behaved like Express middleware and tried to put full authentication, database calls, and heavy logic in it. What it really does is intercept requests at the network boundary, before they reach your app.

Next.js 16 renames it to match. The file is now `proxy.ts`, and the exported function is `proxy`:

```ts
// proxy.ts (project root, or inside src/)
import { NextResponse, type NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  const hasSession = request.cookies.has('session')

  if (!hasSession) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', request.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*'],
}
```

Migration is a rename, and there's a codemod for it:

```bash
npx @next/codemod@canary middleware-to-proxy .
```

Beyond the name, a few things change:

- **Runtime.** `proxy.ts` runs on the Node.js runtime, not Edge, so Node APIs and ordinary npm packages work without workarounds.
- **Edge is not supported in `proxy.ts`.** If you depend on the Edge runtime, `middleware.ts` still works for now, but it is deprecated and will be removed in a future version.
- **Config flags.** Options with "middleware" in the name were renamed. For example, `skipMiddlewareUrlNormalize` is now `skipProxyUrlNormalize`.

The Node.js runtime doesn't make the proxy a good place for heavy work, because it still runs on every matched request. Use it for redirects, rewrites, header manipulation, and optimistic checks.

The example above only checks that a session cookie exists. That is enough to send logged-out visitors to the login page, but it is not authorization. Verify the session where you read the data, in your Server Components, Server Actions, and route handlers.

## Wrapping up

The three features work together:

- **`"use cache"`** makes caching an explicit decision at the level of a function or component, with Partial Prerendering as the result.
- **`updateTag`, `revalidateTag`, and `refresh`** let you choose between immediate consistency, background revalidation, and a plain re-render.
- **`proxy.ts`** gives request interception an accurate name and a full Node.js runtime.

If you're upgrading an existing app, start with the proxy rename, which the codemod does for you. Then update your `revalidateTag` calls to pass a profile. Leave `cacheComponents` for last and adopt it route by route, since it changes rendering defaults across the whole app.

Which of these have you shipped to production so far? Let me know in the comments.

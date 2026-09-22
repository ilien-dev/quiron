# Three new Next.js features and how to use them

Next.js keeps moving fast. Every release seems to bring something that changes how we build React apps, and keeping up can feel like a part-time job. In this post I want to focus on three features that I think are worth your attention right now: Server Actions, Partial Prerendering, and the `after()` API. For each one I'll show what problem it solves, how to use it, and a few gotchas I'd watch out for.

## 1. Server Actions

### What they are

Server Actions let you define functions that run on the server and call them directly from your components, including from forms. You don't need an API route, a `fetch` call or any manual JSON parsing. You write a function, mark it with `'use server'`, and Next.js handles the network boundary for you.

Without them, a simple form submission usually took four steps:

1. Create an API route at `app/api/todos/route.ts`.
2. Write a client component with an `onSubmit` handler.
3. POST the form data to `/api/todos` with `fetch`.
4. Handle loading, errors, and revalidation yourself.

With Server Actions, most of that goes away.

### How to use them

Here's a basic example of adding a todo:

```tsx
// app/todos/actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { db } from '@/lib/db';

export async function addTodo(formData: FormData) {
  const title = formData.get('title');

  if (typeof title !== 'string' || title.trim() === '') {
    return { error: 'Title is required' };
  }

  await db.todo.create({ data: { title } });
  revalidatePath('/todos');
}
```

And the page that uses it:

```tsx
// app/todos/page.tsx
import { addTodo } from './actions';
import { db } from '@/lib/db';

export default async function TodosPage() {
  const todos = await db.todo.findMany();

  return (
    <main>
      <form action={addTodo}>
        <input name="title" placeholder="What needs doing?" />
        <button type="submit">Add</button>
      </form>

      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>{todo.title}</li>
        ))}
      </ul>
    </main>
  );
}
```

That's the whole thing. The form works even before JavaScript loads, because it's a real HTML form posting to the server. Once the client hydrates, Next.js intercepts the submission and handles it without a full page reload.

### Adding pending state

To show a loading state, you can use React's `useFormStatus` hook in a client component:

```tsx
'use client';

import { useFormStatus } from 'react-dom';

export function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Adding...' : 'Add'}
    </button>
  );
}
```

And for handling the returned error, `useActionState` gives you the result of the last action call:

```tsx
'use client';

import { useActionState } from 'react';
import { addTodo } from './actions';

export function TodoForm() {
  const [state, formAction] = useActionState(
    async (_prev: any, formData: FormData) => addTodo(formData),
    null
  );

  return (
    <form action={formAction}>
      <input name="title" />
      <SubmitButton />
      {state?.error && <p role="alert">{state.error}</p>}
    </form>
  );
}
```

### Gotchas

- Server Actions are public endpoints. Anyone can call them, so always validate input and check authorization inside the action. Don't assume the request came from your UI.
- Keep them small. I'd keep actions thin and have them call into a service layer you can test on its own, even though it's tempting to put all your business logic in the action.
- Use a validation library. Zod works really well here for parsing `FormData` into typed objects.

## 2. Partial Prerendering

### What it is

For a long time, Next.js made you choose per route: is this page static or dynamic? If one small part of the page depended on cookies or request headers, like a user avatar in the navbar, the entire route became dynamic.

Partial Prerendering (PPR) removes that all-or-nothing choice. It lets a single route have a static shell that's served instantly from the edge, with dynamic "holes" that stream in as they're ready.

### How to use it

First, enable it in your config. Depending on your Next.js version, this may still be behind an experimental flag:

```js
// next.config.js
module.exports = {
  experimental: {
    ppr: 'incremental',
  },
};
```

Then opt a route in:

```tsx
// app/product/[id]/page.tsx
export const experimental_ppr = true;
```

Now the important part is `Suspense`. Anything wrapped in a `Suspense` boundary that reads dynamic data becomes a dynamic hole. Everything else is prerendered.

```tsx
import { Suspense } from 'react';
import { ProductDetails } from './ProductDetails';
import { Recommendations } from './Recommendations';
import { CartButton } from './CartButton';

export default async function ProductPage({ params }) {
  const { id } = await params;

  return (
    <main>
      <ProductDetails id={id} />

      <Suspense fallback={<div className="skeleton">Loading cart...</div>}>
        <CartButton />
      </Suspense>

      <Suspense fallback={<div className="skeleton">Loading recommendations...</div>}>
        <Recommendations id={id} />
      </Suspense>
    </main>
  );
}
```

If `CartButton` reads cookies to figure out the user's cart, that's fine. The product details are static and show up immediately. The cart and recommendations stream in right after.

### Gotchas

- Your fallbacks matter now. They're part of the static shell, so design them to match the final layout and avoid layout shift.
- Dynamic APIs leak upward. If you call `cookies()` outside a `Suspense` boundary, the whole route falls back to dynamic rendering. Push those calls down into the smallest component that needs them.
- Check the build output. `next build` will tell you which routes are partially prerendered, and I use it to confirm my boundaries are where I think they are.

## 3. The `after()` API

### What it is

Sometimes you need to do work after sending a response: logging analytics, syncing to a third-party service, warming a cache. If you do that work before responding, the user waits for something they don't care about. If you do it in a fire-and-forget promise, you're taking a risk, because in serverless environments the function can be frozen before the promise finishes.

`after()` is the fix for this. It schedules a callback to run once the response has finished streaming, and the platform keeps the function alive until it completes.

### How to use it

```tsx
// app/api/checkout/route.ts
import { after } from 'next/server';
import { processOrder } from '@/lib/orders';
import { trackEvent } from '@/lib/analytics';

export async function POST(request: Request) {
  const body = await request.json();
  const order = await processOrder(body);

  after(async () => {
    await trackEvent('order_completed', { orderId: order.id });
  });

  return Response.json({ orderId: order.id });
}
```

The user gets their response as soon as the order is processed. The analytics call happens afterwards.

It works in Server Components and Server Actions too:

```tsx
// app/blog/[slug]/page.tsx
import { after } from 'next/server';
import { incrementViews } from '@/lib/views';

export default async function Post({ params }) {
  const { slug } = await params;
  const post = await getPost(slug);

  after(() => incrementViews(slug));

  return <article>{/* ... */}</article>;
}
```

### Gotchas

- Don't use it for critical work. If the operation must succeed for the request to count as successful, do it before responding. `after()` is for side effects you can afford to lose or retry.
- Errors won't reach the user. Log failures inside the callback, or you'll never know they happened.
- Request APIs are limited. In Server Components, you can't call `cookies()` or `headers()` inside the `after` callback. Read what you need beforehand and close over it.

## Using all three on one page

These three features fit together nicely. Imagine a product page. Partial Prerendering serves the product info instantly from a static shell while the personalized cart button streams in. A Server Action handles "Add to cart" with a plain form that works without JavaScript. And `after()` sends the analytics events once the action has responded, so the user isn't slowed down.

To me the pattern is that Next.js is pushing more of the work to the server while keeping the user experience fast. You ship less client-side JavaScript, you have fewer API routes to maintain, and you make fewer tradeoffs between static and dynamic.

## Where I'd start

If you're starting a new project on the App Router, I'd recommend trying all three:

1. Replace a simple API route plus `fetch` combo with a Server Action.
2. Turn on PPR for one route that has a small dynamic piece and see how the build output changes.
3. Move a non-critical side effect into `after()` and watch your response times drop.

Check the official Next.js docs for the latest details, since some of these APIs still change between releases.

Have you tried any of these yet? I'd love to hear how they're working for you in the comments.

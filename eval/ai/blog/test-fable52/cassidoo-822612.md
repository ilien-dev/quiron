Shopify themes are fine until you want full control over your storefront. Then you start fighting Liquid, theme limits, and app scripts that slow every page down.

Going headless fixes that. Shopify keeps doing the things it is good at (products, inventory, payments, taxes), and you build the storefront in Next.js. In this post we'll build a small but real shop: a product grid, a product page, and a cart that hands off to Shopify's checkout.

## What you need

- Node.js 20 or newer
- A Shopify store (a free development store from a Partner account works)
- Basic familiarity with React and the Next.js App Router

## 1. Get Storefront API access

The Storefront API is Shopify's GraphQL API for customer-facing data: products, collections, carts.

1. In your Shopify admin, install the **Headless** sales channel.
2. Create a storefront inside it.
3. Copy the **private access token**. We only call Shopify from the server, so the private token is the right one, and it never reaches the browser.
4. Make sure your products are published to the Headless channel, or your queries will return empty lists.

## 2. Create the Next.js app

```bash
npx create-next-app@latest my-shop --typescript --app
cd my-shop
```

Add your credentials to `.env.local`:

```bash
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
SHOPIFY_STOREFRONT_PRIVATE_TOKEN=your-private-token
```

Product images are served from Shopify's CDN, so allow that host in `next.config.ts`:

```ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [{ protocol: 'https', hostname: 'cdn.shopify.com' }],
  },
};

export default nextConfig;
```

## 3. Write a tiny Shopify client

You don't need a GraphQL library for this. One function around `fetch` is enough:

```ts
// lib/shopify.ts
const endpoint = `https://${process.env.SHOPIFY_STORE_DOMAIN}/api/2026-10/graphql.json`;

export async function shopifyFetch<T>(
  query: string,
  variables: Record<string, unknown> = {},
  revalidate?: number
): Promise<T> {
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Shopify-Storefront-Private-Token':
        process.env.SHOPIFY_STOREFRONT_PRIVATE_TOKEN!,
    },
    body: JSON.stringify({ query, variables }),
    ...(revalidate ? { next: { revalidate } } : { cache: 'no-store' as const }),
  });

  const json = await res.json();
  if (json.errors) throw new Error(json.errors[0].message);
  return json.data;
}
```

The third argument controls caching. Catalog pages pass a number of seconds and get cached. Cart operations pass nothing and always hit Shopify fresh.

Check the API version in the URL against Shopify's current release list, because versions are retired on a rolling schedule.

## 4. List your products

The home page is a Server Component, so we can fetch right inside it:

```tsx
// app/page.tsx
import Image from 'next/image';
import Link from 'next/link';
import { shopifyFetch } from '@/lib/shopify';

const PRODUCTS = `
  query Products {
    products(first: 12) {
      nodes {
        handle
        title
        featuredImage { url altText }
        priceRange { minVariantPrice { amount currencyCode } }
      }
    }
  }
`;

export default async function Home() {
  const { products } = await shopifyFetch<any>(PRODUCTS, {}, 60);

  return (
    <main className="grid grid-cols-2 gap-6 p-8 md:grid-cols-4">
      {products.nodes.map((p: any) => (
        <Link key={p.handle} href={`/products/${p.handle}`}>
          {p.featuredImage && (
            <Image
              src={p.featuredImage.url}
              alt={p.featuredImage.altText ?? p.title}
              width={600}
              height={600}
            />
          )}
          <h2>{p.title}</h2>
          <p>
            {new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: p.priceRange.minVariantPrice.currencyCode,
            }).format(Number(p.priceRange.minVariantPrice.amount))}
          </p>
        </Link>
      ))}
    </main>
  );
}
```

I used `any` to keep the snippet short. In a real project, generate types from the schema with GraphQL Codegen.

## 5. Build the product page

Each product has a `handle`, a URL-friendly slug that makes a natural dynamic route:

```tsx
// app/products/[handle]/page.tsx
import { notFound } from 'next/navigation';
import { shopifyFetch } from '@/lib/shopify';
import { addToCart } from '@/app/actions';

const PRODUCT = `
  query Product($handle: String!) {
    product(handle: $handle) {
      title
      description
      variants(first: 1) { nodes { id } }
    }
  }
`;

export default async function ProductPage({
  params,
}: {
  params: Promise<{ handle: string }>;
}) {
  const { handle } = await params;
  const { product } = await shopifyFetch<any>(PRODUCT, { handle }, 60);
  if (!product) notFound();

  return (
    <main className="p-8">
      <h1>{product.title}</h1>
      <p>{product.description}</p>
      <form action={addToCart}>
        <input
          type="hidden"
          name="variantId"
          value={product.variants.nodes[0].id}
        />
        <button type="submit">Add to cart</button>
      </form>
    </main>
  );
}
```

Two things to notice:

- **`params` is a Promise** in recent Next.js versions, so it has to be awaited.
- **You add variants to a cart, not products.** Even a product with no options has one default variant, and its ID is what the cart needs.

## 6. Add a cart with a Server Action

Carts live on Shopify's side. We create one, remember its ID in a cookie, and add lines to it:

```ts
// app/actions.ts
'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { shopifyFetch } from '@/lib/shopify';

const CART_CREATE = `
  mutation CartCreate($lines: [CartLineInput!]) {
    cartCreate(input: { lines: $lines }) {
      cart { id }
      userErrors { message }
    }
  }
`;

const CART_LINES_ADD = `
  mutation CartLinesAdd($cartId: ID!, $lines: [CartLineInput!]!) {
    cartLinesAdd(cartId: $cartId, lines: $lines) {
      cart { id }
      userErrors { message }
    }
  }
`;

export async function addToCart(formData: FormData) {
  const lines = [
    { merchandiseId: formData.get('variantId') as string, quantity: 1 },
  ];
  const cookieStore = await cookies();
  const cartId = cookieStore.get('cartId')?.value;

  if (cartId) {
    await shopifyFetch(CART_LINES_ADD, { cartId, lines });
  } else {
    const data = await shopifyFetch<any>(CART_CREATE, { lines });
    cookieStore.set('cartId', data.cartCreate.cart.id, {
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
    });
  }

  redirect('/cart');
}
```

The form on the product page posts straight to this function. There is no API route and no client-side state, and it works even with JavaScript disabled.

In production, check `userErrors` too. Shopify reports problems like "out of stock" there, not as top-level GraphQL errors.

## 7. Hand off to checkout

The cart page reads the cookie, fetches the cart, and links to `checkoutUrl`:

```tsx
// app/cart/page.tsx
import { cookies } from 'next/headers';
import { shopifyFetch } from '@/lib/shopify';

const CART = `
  query Cart($id: ID!) {
    cart(id: $id) {
      checkoutUrl
      cost { totalAmount { amount currencyCode } }
      lines(first: 50) {
        nodes {
          id
          quantity
          merchandise { ... on ProductVariant { product { title } } }
        }
      }
    }
  }
`;

export default async function CartPage() {
  const cartId = (await cookies()).get('cartId')?.value;
  const cart = cartId
    ? (await shopifyFetch<any>(CART, { id: cartId })).cart
    : null;

  if (!cart) return <p className="p-8">Your cart is empty.</p>;

  return (
    <main className="p-8">
      <ul>
        {cart.lines.nodes.map((line: any) => (
          <li key={line.id}>
            {line.quantity} × {line.merchandise.product.title}
          </li>
        ))}
      </ul>
      <p>
        Total: {cart.cost.totalAmount.amount}{' '}
        {cart.cost.totalAmount.currencyCode}
      </p>
      <a href={cart.checkoutUrl}>Checkout</a>
    </main>
  );
}
```

That `checkoutUrl` sends the customer to Shopify's hosted checkout. Payments, taxes, shipping rates, and PCI compliance stay Shopify's problem, which is the main reason to go headless on Shopify and not build a shop from scratch.

## 8. Deploy

Push the repo to GitHub, import it into Vercel (or any host that runs Next.js), and add the two environment variables. That's the whole deployment.

## Where to go next

You now have a working shop in about 200 lines of code. Some ideas for the next steps:

- **Variant selection**: query `options` and `variants`, and let customers pick a size or color.
- **Cart editing**: the `cartLinesUpdate` and `cartLinesRemove` mutations follow the same pattern as adding.
- **Instant updates**: use Shopify webhooks to call `revalidateTag` when a product changes, so you don't wait for the 60-second window.
- **Collections and search**: both are single queries on the Storefront API.
- **SEO**: add `generateMetadata` to the product page using the product's `seo` field.

If you build something with this, drop a link in the comments. I'd love to see it.

# Build your own online shop with Next.js and Shopify

Shopify is one of the easiest ways to run an online store. It handles inventory, payments, taxes, and shipping, which are all things you really don't want to build yourself. But the default Shopify themes don't always give you the control you want over how your site looks and feels.

A headless setup fixes that. You keep Shopify as the backend for products and checkout, and build the frontend however you like. In this tutorial we'll use Next.js and the Shopify Storefront API to build a simple shop with a product listing page, product detail pages, and a working cart that hands off to the Shopify checkout.

## What you need

- A Shopify store (a free development store through the Shopify Partners program works great)
- Node.js 18 or later
- Basic familiarity with React

## Step 1: Set up Shopify

First we need an access token for the Storefront API.

1. In your Shopify admin, go to **Settings → Apps and sales channels → Develop apps**.
2. Click **Create an app** and give it a name like "Next.js Storefront."
3. Under **Configuration**, find **Storefront API integration** and enable these scopes:
   - `unauthenticated_read_product_listings`
   - `unauthenticated_write_checkouts`
   - `unauthenticated_read_checkouts`
4. Click **Install app**, then copy the **Storefront API access token**.

While you're in there, add a few products to your store if it is empty. Give them images and prices so something can be displayed.

## Step 2: Create the Next.js app

```bash
npx create-next-app@latest my-shop
cd my-shop
```

I'll use the App Router and TypeScript, but the ideas apply either way.

Now create a `.env.local` file in the root of the project:

```bash
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
SHOPIFY_STOREFRONT_ACCESS_TOKEN=your-token-here
```

## Step 3: Write a Shopify fetch helper

The Storefront API is a GraphQL API. I like to write a tiny helper to make requests to it, so the same fetch code isn't repeated everywhere.

```ts
// lib/shopify.ts
const domain = process.env.SHOPIFY_STORE_DOMAIN;
const token = process.env.SHOPIFY_STOREFRONT_ACCESS_TOKEN;

export async function shopifyFetch<T>({
  query,
  variables = {},
}: {
  query: string;
  variables?: Record<string, unknown>;
}): Promise<T> {
  const res = await fetch(`https://${domain}/api/2024-07/graphql.json`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Storefront-Access-Token': token!,
    },
    body: JSON.stringify({ query, variables }),
    next: { revalidate: 60 },
  });

  const json = await res.json();

  if (json.errors) {
    console.error(json.errors);
    throw new Error('Shopify API error');
  }

  return json.data;
}
```

The `next: { revalidate: 60 }` option tells Next.js to cache the response and refresh it at most once a minute. That keeps the site fast, and product changes are still picked up fairly quickly.

## Step 4: Build the product listing page

First, a query to grab our products:

```ts
// lib/queries.ts
export const PRODUCTS_QUERY = `
  query Products {
    products(first: 20) {
      edges {
        node {
          id
          title
          handle
          featuredImage {
            url
            altText
          }
          priceRange {
            minVariantPrice {
              amount
              currencyCode
            }
          }
        }
      }
    }
  }
`;
```

And now the home page:

```tsx
// app/page.tsx
import Link from 'next/link';
import Image from 'next/image';
import { shopifyFetch } from '@/lib/shopify';
import { PRODUCTS_QUERY } from '@/lib/queries';

export default async function Home() {
  const data = await shopifyFetch<any>({ query: PRODUCTS_QUERY });
  const products = data.products.edges.map((edge: any) => edge.node);

  return (
    <main className="grid">
      {products.map((product: any) => (
        <Link key={product.id} href={`/products/${product.handle}`}>
          <Image
            src={product.featuredImage.url}
            alt={product.featuredImage.altText ?? product.title}
            width={400}
            height={400}
          />
          <h2>{product.title}</h2>
          <p>
            {product.priceRange.minVariantPrice.amount}{' '}
            {product.priceRange.minVariantPrice.currencyCode}
          </p>
        </Link>
      ))}
    </main>
  );
}
```

Because this is a Server Component, the Shopify request is made on the server and your access token never reaches the browser.

To make `next/image` work with the Shopify CDN, add it to your config:

```js
// next.config.js
module.exports = {
  images: {
    remotePatterns: [{ protocol: 'https', hostname: 'cdn.shopify.com' }],
  },
};
```

## Step 5: Product detail pages

Each product in Shopify has a `handle`, which is a URL-friendly slug. That handle is used for our dynamic route.

```ts
// lib/queries.ts
export const PRODUCT_QUERY = `
  query Product($handle: String!) {
    product(handle: $handle) {
      id
      title
      descriptionHtml
      featuredImage { url altText }
      variants(first: 10) {
        edges {
          node {
            id
            title
            price { amount currencyCode }
          }
        }
      }
    }
  }
`;
```

```tsx
// app/products/[handle]/page.tsx
import Image from 'next/image';
import { shopifyFetch } from '@/lib/shopify';
import { PRODUCT_QUERY } from '@/lib/queries';
import { AddToCart } from '@/components/AddToCart';

export default async function ProductPage({
  params,
}: {
  params: Promise<{ handle: string }>;
}) {
  const { handle } = await params;
  const { product } = await shopifyFetch<any>({
    query: PRODUCT_QUERY,
    variables: { handle },
  });

  const variant = product.variants.edges[0].node;

  return (
    <main>
      <Image
        src={product.featuredImage.url}
        alt={product.featuredImage.altText ?? product.title}
        width={600}
        height={600}
      />
      <h1>{product.title}</h1>
      <p>{variant.price.amount} {variant.price.currencyCode}</p>
      <div dangerouslySetInnerHTML={{ __html: product.descriptionHtml }} />
      <AddToCart variantId={variant.id} />
    </main>
  );
}
```

For simplicity I'm just using the first variant here. In a real shop you would let the user pick a size or color.

## Step 6: Add to cart and checkout

The Shopify Cart API lets us create a cart and get back a `checkoutUrl`. A Server Action does that for us, so the token stays on the server.

```ts
// app/actions.ts
'use server';

import { redirect } from 'next/navigation';
import { shopifyFetch } from '@/lib/shopify';

const CART_CREATE = `
  mutation CartCreate($lines: [CartLineInput!]!) {
    cartCreate(input: { lines: $lines }) {
      cart { checkoutUrl }
    }
  }
`;

export async function buyNow(variantId: string) {
  const data = await shopifyFetch<any>({
    query: CART_CREATE,
    variables: { lines: [{ merchandiseId: variantId, quantity: 1 }] },
  });

  redirect(data.cartCreate.cart.checkoutUrl);
}
```

```tsx
// components/AddToCart.tsx
import { buyNow } from '@/app/actions';

export function AddToCart({ variantId }: { variantId: string }) {
  return (
    <form action={buyNow.bind(null, variantId)}>
      <button type="submit">Buy now</button>
    </form>
  );
}
```

Clicking the button creates a cart in Shopify and sends the user straight to the hosted Shopify checkout, where payments, shipping, and taxes are all handled for you.

If you want a persistent cart with multiple items, the cart ID gets stored in a cookie, and then the `cartLinesAdd` mutation adds items to it. I think that's a good next step once the basics are working.

## Step 7: Deploy

Push your project to GitHub and import it into Vercel (or your host of choice). Remember to add your two environment variables in the project settings. And that's it, you have a live shop.

## Recap

In this tutorial we:

- Set up a Shopify app with Storefront API access
- Wrote a small GraphQL helper for Next.js
- Built a product listing page and dynamic product pages
- Used a Server Action to create a cart and redirect to checkout

From here you could add a multi-item cart, collections pages, search, or variant selection. What I like about going headless is that the frontend is entirely yours, so you can design it however you want while Shopify does the heavy lifting behind the scenes.

Happy building!

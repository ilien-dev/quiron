# Build your own online shop with Next.js and Shopify

Shopify is great at the hard parts of e-commerce: payments, taxes, inventory, fulfillment and fraud checks. Its themes are less great when you want full control over design, performance and the developer experience. Going **headless** gives you both. Shopify stays the commerce engine, and Next.js renders the storefront.

In this post we'll build a small but real shop. It will have a product listing, product pages, a cart and checkout. We'll use the Next.js App Router and the Shopify Storefront API, so there's no extra SDK to install. We'll call the API with plain `fetch`.

## What you'll need

- Node.js 20 or newer
- A Shopify store (a free development store from the Shopify Partners dashboard works fine)
- A few products added to that store

## Step 1: Get a Storefront API token

In your Shopify admin, install the **Headless** sales channel from the Shopify App Store. Create a storefront inside it, and you'll get a **public Storefront API access token**. This token is designed for use from browsers, and its permissions are limited to storefront data such as products, collections and carts.

While you're there, note your store domain, which looks like `your-store.myshopify.com`.

## Step 2: Create the Next.js app

```bash
npx create-next-app@latest my-shop --typescript --app --tailwind
cd my-shop
```

Add your credentials to `.env.local`:

```bash
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
SHOPIFY_STOREFRONT_TOKEN=your-public-token
SHOPIFY_API_VERSION=2025-10
```

Shopify releases a new API version every quarter. Pin a recent one and upgrade on purpose, so a release never surprises you.

Product images are served from Shopify's CDN, so allow that host in `next.config.ts`:

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [{ protocol: "https", hostname: "cdn.shopify.com" }],
  },
};

export default nextConfig;
```

## Step 3: A tiny Shopify client

Every Storefront API call is a GraphQL POST request to the same endpoint, so one helper is enough. Create `lib/shopify.ts`:

```ts
const endpoint = `https://${process.env.SHOPIFY_STORE_DOMAIN}/api/${process.env.SHOPIFY_API_VERSION}/graphql.json`;

type FetchOptions = {
  variables?: Record<string, unknown>;
  tags?: string[];
  cache?: RequestCache;
};

export async function shopifyFetch<T>(
  query: string,
  { variables, tags, cache = "force-cache" }: FetchOptions = {}
): Promise<T> {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Shopify-Storefront-Access-Token": process.env.SHOPIFY_STOREFRONT_TOKEN!,
    },
    body: JSON.stringify({ query, variables }),
    cache,
    next: tags ? { tags } : undefined,
  });

  const json = await res.json();
  if (json.errors) {
    throw new Error(json.errors.map((e: { message: string }) => e.message).join("\n"));
  }
  return json.data as T;
}
```

Two details matter here. First, GraphQL usually returns HTTP 200 even when a query fails, so we check `json.errors` explicitly. Second, the `tags` option lets us invalidate cached product data later, when a merchant edits something.

## Step 4: List products

Now let's write the product listing query. Add it to `lib/shopify.ts`:

```ts
export type Product = {
  id: string;
  handle: string;
  title: string;
  description: string;
  featuredImage: { url: string; altText: string | null } | null;
  priceRange: { minVariantPrice: { amount: string; currencyCode: string } };
  variants: { nodes: { id: string; title: string; availableForSale: boolean }[] };
};

const PRODUCT_FIELDS = `
  id handle title description
  featuredImage { url altText }
  priceRange { minVariantPrice { amount currencyCode } }
  variants(first: 10) { nodes { id title availableForSale } }
`;

export async function getProducts() {
  const data = await shopifyFetch<{ products: { nodes: Product[] } }>(
    `query { products(first: 12) { nodes { ${PRODUCT_FIELDS} } } }`,
    { tags: ["products"] }
  );
  return data.products.nodes;
}

export async function getProduct(handle: string) {
  const data = await shopifyFetch<{ product: Product | null }>(
    `query($handle: String!) { product(handle: $handle) { ${PRODUCT_FIELDS} } }`,
    { variables: { handle }, tags: ["products"] }
  );
  return data.product;
}

export function formatPrice({ amount, currencyCode }: { amount: string; currencyCode: string }) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: currencyCode }).format(
    Number(amount)
  );
}
```

Prices come back as strings in the store's currency. `Intl.NumberFormat` handles the formatting for you.

The home page is a Server Component, so it fetches data directly without `useEffect` or loading spinners. Put this in `app/page.tsx`:

```tsx
import Image from "next/image";
import Link from "next/link";
import { getProducts, formatPrice } from "@/lib/shopify";

export default async function Home() {
  const products = await getProducts();

  return (
    <main className="mx-auto max-w-6xl p-8">
      <h1 className="mb-8 text-3xl font-bold">Shop</h1>
      <ul className="grid grid-cols-2 gap-6 md:grid-cols-4">
        {products.map((p) => (
          <li key={p.id}>
            <Link href={`/products/${p.handle}`}>
              {p.featuredImage && (
                <Image
                  src={p.featuredImage.url}
                  alt={p.featuredImage.altText ?? p.title}
                  width={400}
                  height={400}
                  className="aspect-square rounded-lg object-cover"
                />
              )}
              <h2 className="mt-2 font-medium">{p.title}</h2>
              <p className="text-gray-600">{formatPrice(p.priceRange.minVariantPrice)}</p>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
```

## Step 5: Carts with Server Actions

Shopify's **Cart API** stores the cart on Shopify's side. We only need to remember the cart ID, and a cookie is a good place for it. Create `app/actions.ts`:

```ts
"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { shopifyFetch } from "@/lib/shopify";

const CART_FIELDS = `id checkoutUrl totalQuantity`;

export async function addToCart(formData: FormData) {
  const merchandiseId = formData.get("variantId") as string;
  const cookieStore = await cookies();
  const cartId = cookieStore.get("cartId")?.value;
  const lines = [{ merchandiseId, quantity: 1 }];

  if (cartId) {
    await shopifyFetch(
      `mutation($cartId: ID!, $lines: [CartLineInput!]!) {
        cartLinesAdd(cartId: $cartId, lines: $lines) { cart { ${CART_FIELDS} } }
      }`,
      { variables: { cartId, lines }, cache: "no-store" }
    );
  } else {
    const data = await shopifyFetch<{ cartCreate: { cart: { id: string } } }>(
      `mutation($lines: [CartLineInput!]) {
        cartCreate(input: { lines: $lines }) { cart { ${CART_FIELDS} } }
      }`,
      { variables: { lines }, cache: "no-store" }
    );
    cookieStore.set("cartId", data.cartCreate.cart.id, {
      httpOnly: true,
      sameSite: "lax",
      secure: true,
      path: "/",
    });
  }
}

export async function goToCheckout() {
  const cartId = (await cookies()).get("cartId")?.value;
  if (!cartId) return;
  const data = await shopifyFetch<{ cart: { checkoutUrl: string } | null }>(
    `query($cartId: ID!) { cart(id: $cartId) { checkoutUrl } }`,
    { variables: { cartId }, cache: "no-store" }
  );
  if (data.cart) redirect(data.cart.checkoutUrl);
}
```

Cart operations use `cache: "no-store"`, because you never want a cached cart. A production app should also check `userErrors` on each mutation and handle expired cart IDs. I've left that out to keep the example short.

## Step 6: The product page

Create `app/products/[handle]/page.tsx`:

```tsx
import Image from "next/image";
import { notFound } from "next/navigation";
import { getProduct, formatPrice } from "@/lib/shopify";
import { addToCart, goToCheckout } from "@/app/actions";

export default async function ProductPage({ params }: { params: Promise<{ handle: string }> }) {
  const { handle } = await params;
  const product = await getProduct(handle);
  if (!product) notFound();

  const variant = product.variants.nodes.find((v) => v.availableForSale);

  return (
    <main className="mx-auto grid max-w-5xl gap-10 p-8 md:grid-cols-2">
      {product.featuredImage && (
        <Image
          src={product.featuredImage.url}
          alt={product.featuredImage.altText ?? product.title}
          width={800}
          height={800}
          priority
          className="rounded-xl"
        />
      )}
      <div>
        <h1 className="text-3xl font-bold">{product.title}</h1>
        <p className="mt-2 text-xl">{formatPrice(product.priceRange.minVariantPrice)}</p>
        <p className="mt-6 text-gray-700">{product.description}</p>

        <form action={addToCart} className="mt-8">
          <input type="hidden" name="variantId" value={variant?.id ?? ""} />
          <button
            disabled={!variant}
            className="w-full rounded-lg bg-black px-6 py-3 text-white disabled:opacity-40"
          >
            {variant ? "Add to cart" : "Sold out"}
          </button>
        </form>

        <form action={goToCheckout} className="mt-3">
          <button className="w-full rounded-lg border px-6 py-3">Checkout</button>
        </form>
      </div>
    </main>
  );
}
```

Both buttons work without client-side JavaScript, because Server Actions submit as normal HTML forms. That's progressive enhancement at no extra cost. When the shopper checks out, they're redirected to Shopify's hosted checkout, which handles payments, discounts, shipping and taxes.

## Step 7: Keep the catalog fresh

Product data is cached, which makes it fast. You don't want prices to go stale, though. Add a route handler that Shopify can call through a webhook. Create `app/api/revalidate/route.ts`:

```ts
import { revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  if (req.nextUrl.searchParams.get("secret") !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ ok: false }, { status: 401 });
  }
  revalidateTag("products");
  return NextResponse.json({ ok: true });
}
```

In the Shopify admin, go to **Settings → Notifications → Webhooks**. Add webhooks for *Product update* and *Product create* that point to `https://your-site.com/api/revalidate?secret=...`. For production, verify the `X-Shopify-Hmac-Sha256` header instead of relying on a query string secret.

## Deploying

Push the project to GitHub and import it into Vercel or any host that supports Next.js. Add your environment variables there, and you're live. Your storefront is now statically fast and SEO friendly. Shopify still handles the parts of commerce you don't want to build yourself.

## Where to go next

- **Variant selection:** let shoppers choose a size or color using `selectedOptions`
- **A cart drawer:** query `cart.lines` and render it in a Client Component
- **Collections and search:** the `collections` query and the `query` argument on `products`
- **SEO:** use `generateMetadata` with product titles and images

Headless commerce can sound intimidating, but as you've seen, the core of a working shop fits in a handful of files. Happy shipping! 🛍️

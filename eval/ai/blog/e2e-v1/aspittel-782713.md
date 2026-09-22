# Build a serverless subscription site with Stripe

Subscriptions look simple from the outside. You show a pricing page, take a card and unlock the premium features. The hard part is everything around the payment: auth, webhooks, billing state, retries and cancellations, plus making sure people can't keep using features they stopped paying for.

We'll build the billing side of a serverless subscription site with:

- Next.js with TypeScript
- Stripe Checkout
- Stripe Customer Portal
- Serverless route handlers
- A database of your choice

The database and auth functions in the examples are generic, so you can swap in Postgres, DynamoDB, Supabase, Prisma, Auth.js, Clerk or whatever you already use.

## How the pieces fit

The app has four flows that matter:

1. A signed-in user chooses a plan.
2. The server creates a Stripe Checkout Session.
3. Stripe sends subscription events to our webhook.
4. The application stores the resulting access state in its database.

The database decides whether a user has premium access. The browser redirect doesn't. A success page only tells you the customer came back to your site, while a webhook is Stripe itself telling you that the payment or subscription state actually changed.

## Create your Stripe products

In the Stripe Dashboard, create a product, say "Pro Membership", and give it a recurring price with a monthly or yearly interval.

Each price gets an ID that looks like this:

```text
price_1AbcDefGhijkLMNO
```

Put that ID in an environment variable. Don't accept just any price ID from the browser, or a user could try to buy a price you never meant to sell, or one you archived.

Create a `.env.local` file:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

Only variables that start with `NEXT_PUBLIC_` end up in browser code. Your Stripe secret key and your webhook signing secret have to stay on the server.

Install Stripe’s Node library:

```bash
npm install stripe
```

Then make a client you can import anywhere:

```ts
// lib/stripe.ts
import Stripe from "stripe";

export const stripe = new Stripe(
  process.env.STRIPE_SECRET_KEY!
);
```

## Model billing state locally

A user or subscription record needs at least these fields:

```ts
type BillingRecord = {
  userId: string;
  stripeCustomerId: string | null;
  stripeSubscriptionId: string | null;
  stripePriceId: string | null;
  subscriptionStatus: string | null;
  currentPeriodEnd: Date | null;
};
```

Stripe is still the source of truth for billing. But if you copy the fields you need for access checks into your own database, pages load fast. You don't want to call Stripe every time someone opens a premium page.

The examples below assume your app has these helpers:

```ts
import {
  findUserById,
  findUserByStripeCustomerId,
  updateUserBilling,
} from "@/lib/db";

import { requireUser } from "@/lib/auth";
```

`requireUser()` should check the current session on the server and return a user you can trust, with at least an `id` and an `email`.

## Create a Checkout Session

Add a route handler at `app/api/checkout/route.ts`:

```ts
import { NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { requireUser } from "@/lib/auth";
import { findUserById, updateUserBilling } from "@/lib/db";

const allowedPrices = new Set([
  process.env.STRIPE_PRO_MONTHLY_PRICE_ID!,
]);

export async function POST(request: Request) {
  const user = await requireUser();
  const { priceId } = await request.json();

  if (!allowedPrices.has(priceId)) {
    return NextResponse.json(
      { error: "Invalid price" },
      { status: 400 }
    );
  }

  const billing = await findUserById(user.id);
  let customerId = billing.stripeCustomerId;

  if (!customerId) {
    const customer = await stripe.customers.create({
      email: user.email,
      metadata: {
        userId: user.id,
      },
    });

    customerId = customer.id;

    await updateUserBilling(user.id, {
      stripeCustomerId: customerId,
    });
  }

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    customer: customerId,
    line_items: [
      {
        price: priceId,
        quantity: 1,
      },
    ],
    success_url:
      `${process.env.NEXT_PUBLIC_APP_URL}/account?checkout=success`,
    cancel_url:
      `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    client_reference_id: user.id,
    metadata: {
      userId: user.id,
    },
    subscription_data: {
      metadata: {
        userId: user.id,
      },
    },
  });

  return NextResponse.json({ url: session.url });
}
```

A few things in this endpoint matter for security. It only works for a signed-in user, and it checks the price against an allowlist on the server. It creates one Stripe customer per user and saves the mapping, and it puts your own user ID in the Stripe metadata before creating the Checkout Session in subscription mode.

Reuse that customer ID for later purchases and for portal sessions. In production, put a unique constraint on `stripeCustomerId`, and make sure two requests arriving at the same time can't both create a customer.

Now hook a pricing button up to the endpoint:

```tsx
"use client";

import { useState } from "react";

export function SubscribeButton({
  priceId,
}: {
  priceId: string;
}) {
  const [loading, setLoading] = useState(false);

  async function subscribe() {
    setLoading(true);

    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ priceId }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error ?? "Checkout failed");
      }

      window.location.assign(data.url);
    } catch (error) {
      console.error(error);
      setLoading(false);
    }
  }

  return (
    <button onClick={subscribe} disabled={loading}>
      {loading ? "Opening checkout…" : "Subscribe"}
    </button>
  );
}
```

Stripe hosts the checkout form, so card details never touch your app.

## Handle Stripe webhooks

Create `app/api/stripe/webhook/route.ts`:

```ts
import Stripe from "stripe";
import { stripe } from "@/lib/stripe";
import {
  findUserByStripeCustomerId,
  updateUserBilling,
} from "@/lib/db";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const body = await request.text();
  const signature = request.headers.get("stripe-signature");

  if (!signature) {
    return new Response("Missing signature", { status: 400 });
  }

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch {
    return new Response("Invalid signature", { status: 400 });
  }

  switch (event.type) {
    case "customer.subscription.created":
    case "customer.subscription.updated":
    case "customer.subscription.deleted": {
      const subscription = event.data.object;
      await syncSubscription(subscription);
      break;
    }
  }

  return new Response("ok");
}

async function syncSubscription(
  subscription: Stripe.Subscription
) {
  const customerId =
    typeof subscription.customer === "string"
      ? subscription.customer
      : subscription.customer.id;

  const user = await findUserByStripeCustomerId(customerId);

  if (!user) {
    throw new Error(`Unknown Stripe customer: ${customerId}`);
  }

  const item = subscription.items.data[0];

  await updateUserBilling(user.id, {
    stripeSubscriptionId: subscription.id,
    stripePriceId: item?.price.id ?? null,
    subscriptionStatus: subscription.status,
    currentPeriodEnd: item
      ? new Date(item.current_period_end * 1000)
      : null,
  });
}
```

The signature check needs the exact raw request body. If you parse it as JSON before you call `constructEvent()`, the check will fail.

Stripe can retry events and send duplicates. Now and then related events also arrive out of order. So make your database updates idempotent. If you need stricter ordering, save each event's ID and creation time in a webhook events table and skip events you've already processed or that are older than what you have.

Register the deployed webhook URL in Stripe:

```text
https://example.com/api/stripe/webhook
```

To test locally, use the Stripe CLI:

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

It prints a temporary `whsec_...` signing secret. Put that in `.env.local`, restart the dev server and trigger a test subscription.

## Lock down premium features

Keep the access rule in one place, so you aren't comparing status strings all over the app:

```ts
const ACCESS_STATUSES = new Set([
  "active",
  "trialing",
]);

export function hasPremiumAccess(
  billing: BillingRecord
) {
  return (
    billing.subscriptionStatus !== null &&
    ACCESS_STATUSES.has(billing.subscriptionStatus) &&
    billing.currentPeriodEnd !== null &&
    billing.currentPeriodEnd > new Date()
  );
}
```

Whether a status like `past_due` still gets access is a product call. Some services give a grace period while Stripe retries the payment, and others cut access off right away.

Check this rule on the server every time:

```ts
export default async function PremiumPage() {
  const user = await requireUser();
  const billing = await findUserById(user.id);

  if (!hasPremiumAccess(billing)) {
    return <p>An active subscription is required.</p>;
  }

  return <PremiumDashboard />;
}
```

A hidden button in the browser is fine for the UI. It doesn't stop anyone from getting in.

## Add the Customer Portal

Stripe's hosted Customer Portal lets customers update their card, download invoices, switch plans or cancel (whichever of those you turn on in the Dashboard).

Create `app/api/billing-portal/route.ts`:

```ts
import { NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { requireUser } from "@/lib/auth";
import { findUserById } from "@/lib/db";

export async function POST() {
  const user = await requireUser();
  const billing = await findUserById(user.id);

  if (!billing.stripeCustomerId) {
    return NextResponse.json(
      { error: "No billing account found" },
      { status: 400 }
    );
  }

  const session =
    await stripe.billingPortal.sessions.create({
      customer: billing.stripeCustomerId,
      return_url:
        `${process.env.NEXT_PUBLIC_APP_URL}/account`,
    });

  return NextResponse.json({ url: session.url });
}
```

Call it from a "Manage billing" button and redirect to the URL it returns, the same way you did for Checkout.

## Before going live

Your live Stripe keys are only part of it. Check that:

- Live products and prices exist; test price IDs do not work in live mode.
- The production webhook endpoint uses its own signing secret.
- Database updates are idempotent and transactional.
- Checkout and portal endpoints require authentication.
- The server decides which prices are allowed.
- Premium APIs enforce access independently of the UI.
- Webhook failures get logged and someone watches them.
- Secrets never appear in browser bundles or source control.
- Your policies on cancellation, refunds, tax and privacy are clear.

Also test the payment paths: a successful payment, a declined card, a renewal and a failed renewal, a cancellation at period end and an immediate one, and webhook retries.

That's the whole setup: Checkout, webhooks, a local copy of the billing state and the Customer Portal, all of which fit the serverless model. Stripe takes the payments and runs the billing. Your app decides who gets access to what, and it does that quickly and in one place.
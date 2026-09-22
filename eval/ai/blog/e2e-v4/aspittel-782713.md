# Build a serverless subscription site with Stripe

From the outside, subscriptions look simple: you show a pricing page, collect a card and unlock the premium features. The hard part is everything around the payment. You need authentication and webhook handling and billing state -- and then there are retries and cancellations, and making sure people can't keep using features they stopped paying for.

We're going to build the billing foundation for a serverless subscription site, using:

- Next.js with TypeScript
- Stripe Checkout
- Stripe Customer Portal
- Serverless route handlers
- A database of your choice

The database and authentication functions in the examples are generic on purpose, so you can adapt them to Postgres, DynamoDB, Supabase, Prisma, Auth.js, Clerk or whatever else you're using.

## How it fits together

There are four flows that matter:

1. A signed-in user picks a plan.
2. The server creates a Stripe Checkout Session.
3. Stripe sends subscription events to our webhook.
4. The app saves the access state from those events in its database.

The important thing here is that the database decides whether a user has premium access, not the browser redirect. A success page only tells you the customer came back to your site! Webhooks are how Stripe tells you, with authority, that the payment and subscription state actually changed.

## Set up your Stripe products

In the Stripe Dashboard, create a product -- something like "Pro Membership". Add a recurring price to it and pick a monthly or yearly billing interval.

Stripe gives each price an ID that looks something like this:

```text
price_1AbcDefGhijkLMNO
```

Put that ID in an environment variable. Don't ever accept whatever price ID the browser sends you. If you do, a user could try to buy a price you didn't mean to sell, or one you archived.

Create a `.env.local` file:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

Only variables that start with `NEXT_PUBLIC_` get exposed to browser code. Your Stripe secret key and your webhook signing secret have to stay on the server.

Install Stripe's Node library:

```bash
npm install stripe
```

Then make a client you can reuse:

```ts
// lib/stripe.ts
import Stripe from "stripe";

export const stripe = new Stripe(
  process.env.STRIPE_SECRET_KEY!
);
```

## Keep billing state in your own database

At minimum, a user or subscription record should have:

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

Stripe is still the system of record for billing. But if you copy the fields you need for authorization into your own database, page loads stay fast -- you don't want to call Stripe every single time someone opens a premium page.

The examples below assume you have these helpers in your app:

```ts
import {
  findUserById,
  findUserByStripeCustomerId,
  updateUserBilling,
} from "@/lib/db";

import { requireUser } from "@/lib/auth";
```

`requireUser()` should check the current session on the server and give you back a user you can trust, with at least an `id` and an `email`.

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

A lot of security-sensitive stuff happens in this endpoint:

- It requires an authenticated user.
- It checks the selected price against an allowlist on the server.
- It creates one Stripe customer and saves the mapping.
- It puts our internal user ID in the Stripe metadata.
- It creates a Checkout Session in subscription mode.

Reuse the customer ID for future purchases and for portal sessions. In production you'll also want a uniqueness constraint on `stripeCustomerId`, and customer creation should be safe under concurrency so that two requests at the same time can't create duplicates.

Now let's hook a pricing button up to the endpoint:

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

Stripe hosts the checkout form, so your app never touches card details directly.

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

Signature verification needs the exact raw request body. If you parse it as JSON before you call `constructEvent()`, verification breaks.

Stripe can retry events and send duplicates, and once in a while it'll send related events out of order. So make your database updates idempotent. If you need stricter ordering, save each event's ID and creation timestamp in a webhook-events table and ignore events you've already processed or that are stale.

Register your deployed webhook URL in Stripe:

```text
https://example.com/api/stripe/webhook
```

For local testing, use the Stripe CLI:

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

That command prints a temporary `whsec_...` signing secret. Put it in `.env.local` and restart the dev server, then trigger a test subscription.

## Lock down premium features

Keep your access rule in one place instead of sprinkling status checks all over the app:

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

Whether a status like `past_due` still gets access is a product decision. Some services give people a grace period while Stripe retries the payment, and others cut off access right away.

Whatever you decide, enforce this rule on the server:

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

Hiding a button in the browser is nice for the UI, but it isn't authorization!

## Add the Customer Portal

Stripe's hosted Customer Portal lets customers update their payment methods, download invoices, switch plans or cancel, based on the settings you configure in the Dashboard.

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

Call this endpoint from a "Manage billing" button and redirect to the URL it returns, the same way we did for Checkout.

## Before you go live

Switching to your live Stripe keys is only one piece of being ready for production. Double check that:

- Live products and prices exist (test price IDs don't work in live mode).
- The production webhook endpoint has its own signing secret.
- Database updates are idempotent and transactional.
- The checkout and portal endpoints require authentication.
- The server controls which prices are allowed.
- Premium APIs enforce access on their own, not just through the UI.
- Webhook failures get logged and monitored.
- Secrets never end up in browser bundles or in source control.
- Your cancellation, refund, tax and privacy policies are clear.

You should also test a bunch of cases: successful payments, declined cards, renewals, cancellations at the end of the period, immediate cancellations, failed renewals and webhook retries.

That's the whole setup: Checkout, webhooks, a local copy of billing state and the Customer Portal. It's a pretty compact subscription architecture, and it fits the serverless model well. Stripe does the payment collection and the billing workflows, and your app keeps fast, explicit control over who gets to use what.

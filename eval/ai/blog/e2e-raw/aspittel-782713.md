# Build a Serverless Subscription Site with Stripe

Subscriptions look simple from the outside: show a pricing page, collect a card, and unlock premium features. The difficult part is everything around that payment—authentication, webhook handling, billing state, retries, cancellations, and preventing users from accessing features they no longer pay for.

In this tutorial, we’ll build the billing foundation for a serverless subscription site using:

- Next.js with TypeScript
- Stripe Checkout
- Stripe Customer Portal
- Serverless route handlers
- A database of your choice

The examples use generic database and authentication functions so you can adapt them to Postgres, DynamoDB, Supabase, Prisma, Auth.js, Clerk, or another stack.

## The architecture

Our application has four important flows:

1. A signed-in user chooses a plan.
2. The server creates a Stripe Checkout Session.
3. Stripe sends subscription events to our webhook.
4. The application stores the resulting access state in its database.

The database—not the browser redirect—decides whether a user has premium access.

That distinction matters. A success page only means the customer returned to your site. Webhooks are Stripe’s authoritative notification that payment and subscription state changed.

## Create your Stripe products

In the Stripe Dashboard, create a product such as “Pro Membership.” Add a recurring price to it, choosing a monthly or yearly billing interval.

Stripe gives each price an identifier resembling:

```text
price_1AbcDefGhijkLMNO
```

Store that identifier in an environment variable. Never accept arbitrary price IDs from the browser; otherwise, a user could attempt to purchase an unintended or archived price.

Create a `.env.local` file:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

Only variables prefixed with `NEXT_PUBLIC_` are exposed to browser code. Your Stripe secret key and webhook signing secret must remain server-side.

Install Stripe’s Node library:

```bash
npm install stripe
```

Then create a reusable client:

```ts
// lib/stripe.ts
import Stripe from "stripe";

export const stripe = new Stripe(
  process.env.STRIPE_SECRET_KEY!
);
```

## Model billing state locally

A minimal user or subscription record should contain:

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

Stripe remains the billing system of record, but copying the fields needed for authorization into your database keeps page loads fast. You should not call Stripe every time someone opens a premium page.

The examples below assume these application-specific helpers exist:

```ts
import {
  findUserById,
  findUserByStripeCustomerId,
  updateUserBilling,
} from "@/lib/db";

import { requireUser } from "@/lib/auth";
```

`requireUser()` should verify the current session on the server and return a trusted user containing at least an `id` and `email`.

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

This endpoint performs several security-sensitive operations:

- It requires an authenticated user.
- It validates the selected price against a server-side allowlist.
- It creates one Stripe customer and saves the mapping.
- It places the internal user ID in Stripe metadata.
- It creates a subscription-mode Checkout Session.

The customer ID should be reused for future purchases and portal sessions. In production, enforce uniqueness on `stripeCustomerId` and make customer creation concurrency-safe so two simultaneous requests cannot create duplicates.

Now connect a pricing button to the endpoint:

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

Stripe hosts the checkout form, so your application never handles card details directly.

## Process Stripe webhooks

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

Webhook signature verification requires the exact raw request body. Parsing it as JSON before calling `constructEvent()` will break verification.

Stripe can retry events, deliver duplicates, or occasionally deliver related events out of order. Make your database updates idempotent. For stricter ordering, store each event ID and creation timestamp in a webhook-events table, then ignore already-processed or stale events.

Register your deployed webhook URL in Stripe:

```text
https://example.com/api/stripe/webhook
```

For local testing, use the Stripe CLI:

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

The command prints a temporary `whsec_...` signing secret. Put it in `.env.local`, restart the development server, and trigger a test subscription.

## Authorize premium features

Centralize your access rule instead of scattering status comparisons throughout the application:

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

Whether statuses such as `past_due` retain access is a product decision. Some services provide a grace period while Stripe retries payment; others revoke access immediately.

Always enforce this rule on the server:

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

Hiding a button in the browser is useful for presentation, but it is not authorization.

## Add the Customer Portal

Stripe’s hosted Customer Portal lets customers update payment methods, download invoices, switch plans, or cancel according to settings you configure in the Dashboard.

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

Call this endpoint from a “Manage billing” button and redirect to the returned URL just as you did for Checkout.

## Before going live

Switching to live Stripe keys is only one part of production readiness. Verify that:

- Live products and prices exist; test price IDs do not work in live mode.
- The production webhook endpoint uses its own signing secret.
- Database updates are idempotent and transactional.
- Checkout and portal endpoints require authentication.
- Allowed prices are controlled by the server.
- Premium APIs enforce access independently of the UI.
- Webhook failures are logged and monitored.
- Secrets never appear in browser bundles or source control.
- Your cancellation, refund, tax, and privacy policies are clear.

You should also test successful payments, declined cards, renewals, cancellations at period end, immediate cancellations, failed renewals, and webhook retries.

With Checkout, webhooks, a local billing projection, and the Customer Portal, you now have a compact subscription architecture that fits the serverless model. Stripe handles payment collection and billing workflows, while your application retains fast, explicit control over who can access what.
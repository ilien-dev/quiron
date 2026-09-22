# Build a serverless subscription site with Stripe

From the outside a subscription looks simple. You show a pricing page, take a card and unlock the paid features. The hard part is everything around the payment: auth, webhooks, billing state, retries, cancellations, and making sure people lose access to features they've stopped paying for.

We'll build the billing side of a serverless subscription site using:

- Next.js with TypeScript
- Stripe Checkout
- Stripe Customer Portal
- Serverless route handlers
- A database of your choice

The database and auth functions in the examples are generic, so you can adapt them to Postgres, DynamoDB, Supabase, Prisma, Auth.js, Clerk or whatever else you use.

## How it fits together

There are four flows that matter:

1. A signed-in user picks a plan.
2. The server creates a Stripe Checkout Session.
3. Stripe sends subscription events to our webhook.
4. The app stores the access state that results in its database.

What decides whether a user has premium access is the database. The browser redirect doesn't. A success page only tells you the customer came back to your site. The webhook is Stripe's authoritative notice that the payment and subscription state changed.

## Set up Stripe

In the Stripe Dashboard, create a product such as "Pro Membership" and add a recurring price to it, monthly or yearly.

Stripe gives each price an ID that looks like this:

```text
price_1AbcDefGhijkLMNO
```

Put that ID in an environment variable. Don't accept any price ID the browser sends you, or a user could try to buy a price you didn't mean to sell, or one you've archived.

Create a `.env.local` file:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

Only variables that start with `NEXT_PUBLIC_` are exposed to browser code. The Stripe secret key and the webhook signing secret have to stay on the server.

Install Stripe's Node library:

```bash
npm install stripe
```

Then create a client you can reuse:

```ts
// lib/stripe.ts
import Stripe from "stripe";

export const stripe = new Stripe(
  process.env.STRIPE_SECRET_KEY!
);
```

## Keep a copy of the billing state

A minimal user or subscription record needs these fields:

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

Stripe is still the source of truth for billing. But copy the fields you need for access checks into your own database. Page loads stay fast that way, because you don't call Stripe every time someone opens a premium page.

The examples below assume you have these helpers in your app:

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

A lot of what this endpoint does is about security. It requires a logged-in user and checks the price against a list kept on the server. It creates one Stripe customer per user and saves the mapping, puts our own user ID in the Stripe metadata, and then creates a Checkout Session in subscription mode.

Reuse that customer ID for later purchases and for portal sessions. In production, put a unique constraint on `stripeCustomerId` and make customer creation safe under concurrency, so two requests that arrive at once can't create two customers.

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

## Handle the webhooks

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

Stripe can retry events and send duplicates. Now and then it also sends related events out of order. So make your database updates idempotent. If you need stricter ordering, store each event's ID and creation time in a webhook events table and ignore events you've already processed or that are older than what you have.

Register the deployed webhook URL in Stripe:

```text
https://example.com/api/stripe/webhook
```

To test locally, use the Stripe CLI:

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

It prints a temporary `whsec_...` signing secret. Put that in `.env.local` and restart the dev server. Then trigger a test subscription.

## Check access on the server

Keep the access rule in one place, so you don't end up with status comparisons all over the app:

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

Whether a status like `past_due` keeps access is a product decision. Some services give people a grace period while Stripe retries the payment. Others cut access off right away.

Always check the rule on the server:

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

Hiding a button in the browser is fine for how the page looks. It doesn't stop anyone from getting in.

## Add the Customer Portal

Stripe's hosted Customer Portal lets customers update their payment method, download invoices, switch plans or cancel, depending on what you've turned on in the Dashboard.

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

## Before you go live

Switching to live keys is only part of it. Check that:

- Live products and prices exist (test price IDs don't work in live mode).
- The production webhook endpoint has its own signing secret.
- Database updates are idempotent and run in transactions.
- The checkout and portal endpoints require a logged-in user.
- The server controls which prices are allowed.
- Premium APIs check access on their own, not just through the UI.
- Webhook failures get logged and someone watches them.
- Secrets never end up in browser bundles or in source control.
- Your cancellation, refund, tax and privacy policies are clear.

And test the paths people will actually hit: a successful payment, a declined card, a renewal and a failed renewal, a cancellation at period end and one that takes effect right away, and webhook retries.

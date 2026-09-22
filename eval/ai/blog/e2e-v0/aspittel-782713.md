# Build a serverless subscription site with Stripe

From the outside a subscription looks easy. You show a pricing page, take a card, and turn on the paid features. The hard part is all the stuff around the payment: auth, webhook handling, billing state, retries, cancellations, and making sure people can't keep using features they no longer pay for.

In this tutorial I'll walk you through the billing base I'd use for a serverless subscription site. We'll use:

- Next.js with TypeScript
- Stripe Checkout
- Stripe Customer Portal
- Serverless route handlers
- A database of your choice

The code calls generic database and auth functions so you can fit it to Postgres, DynamoDB, Supabase, Prisma, Auth.js, Clerk, or whatever else you run.

## The architecture

The app has four flows that matter:

1. A signed-in user picks a plan.
2. The server creates a Stripe Checkout Session.
3. Stripe sends subscription events to our webhook.
4. The app saves the access state that comes out of that in its database.

The database decides whether a user gets premium access. The browser redirect doesn't. That matters because a success page only tells you the customer came back to your site. Webhooks are how Stripe tells you, with authority, that the payment and subscription state changed.

## Create your Stripe products

In the Stripe Dashboard create a product, something like "Pro Membership." Add a recurring price to it with a monthly or yearly billing interval.

Stripe gives each price an ID that looks like this:

```text
price_1AbcDefGhijkLMNO
```

Put that ID in an environment variable. Don't ever take a price ID from the browser as is, or a user could try to buy a price you didn't mean to sell, or one you archived.

Create a `.env.local` file:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

Only variables that start with `NEXT_PUBLIC_` get sent to browser code. Your Stripe secret key and webhook signing secret have to stay on the server.

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

At the least, I'd want a user or subscription record to have these fields:

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

Stripe is still the billing system of record. But if we copy the fields we need for access checks into our own database, pages load fast. You don't want to call Stripe each time someone opens a premium page.

The code below assumes you already have these helpers in your app:

```ts
import {
  findUserById,
  findUserByStripeCustomerId,
  updateUserBilling,
} from "@/lib/db";

import { requireUser } from "@/lib/auth";
```

`requireUser()` should check the current session on the server and hand back a trusted user with at least an `id` and an `email`.

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

A lot of this endpoint is about security. It:

- requires a signed-in user.
- checks the chosen price against an allowlist on the server.
- creates one Stripe customer and saves the mapping.
- puts our own user ID in the Stripe metadata.
- creates a Checkout Session in subscription mode.

Reuse the customer ID for later purchases and portal sessions. In production you'll want a unique constraint on `stripeCustomerId`, and customer creation has to be safe under concurrency so two requests at the same time can't create duplicates.

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

Stripe hosts the checkout form, so our app never directly touches card details.

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

To verify the webhook signature you need exactly the raw request body. If you parse it as JSON before you call `constructEvent()` the check breaks.

Stripe can retry events and send duplicates, and occasionally it sends related events out of order. So make your database updates idempotent. If you need stricter ordering, save each event ID and its creation time in a webhook-events table, then skip events you've already handled or that are stale. Once we've deployed, we register the webhook URL in Stripe:

```text
https://example.com/api/stripe/webhook
```

When you're testing on your own machine, use the Stripe CLI to forward the events:

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

It prints a temporary `whsec_...` signing secret. Put that in `.env.local`, restart the dev server and trigger a test subscription.

## Gate the premium features

I like to keep the access rule in one place instead of scattering status checks all over the app:

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

Whether a status like `past_due` keeps access is a product call. Some services give people a grace period while Stripe retries the payment, and others cut access immediately.

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

Hiding a button in the browser is fine for the look of the page, but it isn't authorization.

## Add the Customer Portal

Stripe's hosted Customer Portal lets customers update their payment method, download invoices, switch plans or cancel, depending on the settings you pick in the Dashboard.

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

Swapping in live Stripe keys is only one piece of getting ready for production. Check that:

- Live products and prices exist. Test price IDs don't work in live mode.
- The production webhook endpoint has its own signing secret.
- Database updates are idempotent and run in transactions.
- The Checkout and portal endpoints require auth.
- The server controls which prices are allowed.
- Premium APIs check access themselves, whatever the UI shows.
- Webhook failures get logged and monitored.
- Secrets never end up in browser bundles or in source control.
- Your policies on cancellation, refunds, tax and privacy are clear.

I'd also test these cases: a good payment, a declined card, a renewal, a cancel at the end of the period, a cancel that takes effect right away, a failed renewal and webhook retries.

With Checkout, webhooks, a local copy of the billing state and the Customer Portal we now have a small subscription setup that fits the serverless model. Stripe takes the payments and runs the billing, and our app keeps fast, clear control over who can get to what.

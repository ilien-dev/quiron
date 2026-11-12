# Build a Serverless Subscription Site with Stripe

A subscription site looks simple from the outside: choose a plan, enter a card, unlock the good stuff.

Behind that flow are several systems that need to agree. Your authentication provider knows who the user is. Stripe knows what they purchased. Your application decides what they can access.

Let’s connect those pieces using Next.js serverless functions, a managed database, Stripe Checkout, and the Stripe customer portal.

We’ll build the core billing flow for a members-only content site with one monthly plan. The examples assume you already have authentication and a database; helpers such as `requireUser` and `db` represent your own integrations.

## 1. Map the subscription flow

Here’s the architecture:

```text
Signed-in user → Checkout function → Stripe Checkout
                                          ↓
Database ← Webhook processing ← Stripe events
    ↓
Protected content
```

The browser starts checkout, but your backend creates the Checkout Session. Stripe collects payment details on its hosted page.

Separately, Stripe sends events to your webhook endpoint. Your application uses those events to update subscription records.

That separation matters. A customer might close their browser immediately after paying. Their subscription must still activate.

The success page is useful feedback, but it should never be the authority that grants access.

Serverless functions fit this architecture well: checkout requests, billing portal requests, and webhook deliveries are short HTTP interactions. Persistent state belongs in your database, not in function memory.

## 2. Configure Stripe and your environment

In a Stripe sandbox, create a product called **Pro Membership** and a recurring monthly price. Copy its `price_...` identifier.

Install the server-side SDK:

```bash
npm install stripe
```

Add these environment variables:

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
APP_URL=http://localhost:3000
```

Keep the secret key and webhook secret on the server. Never give them a `NEXT_PUBLIC_` prefix.

Create a shared client:

```ts
// lib/stripe.ts
import Stripe from "stripe";

export const stripe = new Stripe(
  process.env.STRIPE_SECRET_KEY!
);
```

Commit your dependency lockfile so deployments use the same SDK version. Configure your webhook destination with a compatible API version, and review version changes before upgrading.

For this tutorial, use **snapshot events**, which provide the event objects expected by the webhook example below.

## 3. Store billing state separately from user profiles

A small schema is enough to start:

```text
users
  id
  stripe_customer_id UNIQUE

subscriptions
  stripe_subscription_id PRIMARY KEY
  user_id
  stripe_price_id
  status

stripe_events
  stripe_event_id PRIMARY KEY
  processing_status
```

Keep a separate subscription record rather than adding an `is_paid` boolean to the user.

Subscription states explain what is happening: a payment may be incomplete, a subscription may be active, or billing may have failed. A boolean loses that context.

Create or retrieve a Stripe Customer for each authenticated user, then persist the mapping. Make this operation safe under concurrent requests using database uniqueness and Stripe idempotency keys.

Use your internal user ID as the identity link. Email addresses can change and should not determine billing ownership.

Your subscription records also let you answer a useful question: does this user have *any* qualifying subscription?

## 4. Create a hosted Checkout Session

Add a server-side route:

```ts
// app/api/checkout/route.ts
import { stripe } from "@/lib/stripe";
import {
  requireUser,
  getOrCreateStripeCustomer,
} from "@/lib/billing";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const user = await requireUser(request);

  const customerId =
    await getOrCreateStripeCustomer(user);

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    customer: customerId,
    line_items: [
      {
        price: process.env.STRIPE_PRICE_ID!,
        quantity: 1,
      },
    ],
    subscription_data: {
      metadata: { userId: user.id },
    },
    success_url:
      `${process.env.APP_URL}/account?checkout=success`,
    cancel_url: `${process.env.APP_URL}/pricing`,
  });

  return Response.json({ url: session.url });
}
```

The price comes from server configuration. For multiple plans, accept a plan name and map it to an approved Price ID on the server.

Likewise, derive customer identity from the authenticated session. A browser-supplied customer ID would let users attempt billing operations against someone else’s account.

Your subscribe button calls this endpoint and redirects to the returned URL. Stripe’s [Checkout subscription guide](https://docs.stripe.com/payments/checkout/build-subscriptions) documents the hosted flow.

Before production, prevent accidental duplicate purchases. Reuse an open Checkout Session where appropriate, direct existing subscribers to account management, and use an idempotency key tied to a persisted checkout attempt. Disabling the button alone does not handle concurrent requests.

## 5. Verify and persist webhook events

Register these subscription events:

- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

For this simple site, subscription status drives access. Add invoice events when implementing payment-failure notifications or other invoice-specific workflows.

The endpoint must verify Stripe’s signature against the **raw request body**:

```ts
// app/api/stripe/webhook/route.ts
import { stripe } from "@/lib/stripe";
import { persistStripeEvent } from "@/lib/billing";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const signature =
    request.headers.get("stripe-signature");

  if (!signature) {
    return new Response("Missing signature", {
      status: 400,
    });
  }

  let event;

  try {
    event = stripe.webhooks.constructEvent(
      await request.text(),
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch {
    return new Response("Invalid signature", {
      status: 400,
    });
  }

  try {
    await persistStripeEvent(event);
    return Response.json({ received: true });
  } catch {
    return new Response("Persistence failed", {
      status: 500,
    });
  }
}
```

Here, `persistStripeEvent` is an adapter you implement. It durably inserts the event into a database inbox with a unique constraint on its ID. Duplicate deliveries should succeed without inserting duplicate work.

A background worker processes pending records. Configure a durable job trigger or scheduled worker so persisted events actually get processed. Don’t start an unawaited promise after returning: a serverless runtime may stop execution.

Returning `200` now means “we have safely stored this event.” Processing failures belong to the worker’s retry mechanism.

Stripe documents signature verification, retries, duplicates, and delivery-order limitations in its [webhook guide](https://docs.stripe.com/webhooks).

## 6. Turn subscription changes into access

For each subscription event, the worker retrieves the latest subscription from Stripe, resolves its customer to your stored user, and upserts the subscription record.

Check that its Price ID belongs to your membership catalog. An unrelated subscription should not unlock this site.

Retrieving current state helps avoid applying stale event snapshots. Still, serialize processing per subscription—or use an equivalent concurrency strategy—so overlapping workers cannot overwrite newer state with an older read.

Define your access policy explicitly:

| Subscription status | Access policy |
| --- | --- |
| `active` | Allow |
| `trialing` | Allow if trials are offered |
| `past_due` | Apply your chosen grace-period policy |
| Other statuses | Deny |

For this implementation, we’ll deny access during `past_due`. If you want a grace period, store and enforce its deadline.

A scheduled cancellation may leave a subscription active until its paid period finishes. Don’t revoke access merely because cancellation was requested. Follow the status transition when the subscription actually ends. Stripe’s [subscription event documentation](https://docs.stripe.com/billing/subscriptions/webhooks) describes these lifecycle changes.

Enforce access before reading or returning protected content:

```ts
const user = await requireUser(request);
const allowed = await hasMembership(user.id);

if (!allowed) {
  return new Response("Subscription required", {
    status: 403,
  });
}
```

Apply that check to content APIs and downloads too. Hiding a component does not protect its underlying data.

## 7. Let customers manage billing

Configure the Stripe customer portal to support the actions you want, such as updating payment methods and canceling subscriptions.

An authenticated server route can create a portal session:

```ts
const user = await requireUser(request);
const customerId = await getStoredCustomerId(user.id);

const portal = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: `${process.env.APP_URL}/account`,
});

return Response.json({ url: portal.url });
```

Redirect the user to that URL from a **Manage billing** button.

Always load the customer ID from your database. Configure portal features separately for testing and production, following Stripe’s [customer portal guide](https://docs.stripe.com/customer-management/integrate-customer-portal).

## 8. Test the lifecycle before launch

Forward sandbox events locally:

```bash
stripe listen \
  --forward-to localhost:3000/api/stripe/webhook
```

Use the signing secret printed by this listener for local testing.

Complete a real sandbox checkout, then verify activation, cancellation, failed payment behavior, duplicate event handling, and worker retries. Test that an unpaid user cannot fetch protected content directly.

On the success page, show “Confirming your subscription” while webhook processing catches up.

Finally, deploy your functions, configure live environment variables, create the live price, and register the production HTTPS webhook destination. Use a database connection strategy suited to serverless concurrency, and monitor pending events and processing failures.

You now have the foundation of a subscription site: hosted checkout, durable billing updates, protected content, and self-service account management. The next feature can be the one your members actually came for.

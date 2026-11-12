# Build a Serverless Subscription Site with Stripe

A subscription site needs more than a payment form. It needs to connect a payment to the right user, decide who can access paid content, and respond when a subscription changes.

Stripe handles the billing side: checkout, recurring payments, invoices, and a customer portal. Serverless functions provide the glue between Stripe and your application.

In this tutorial, we’ll build the core flow for a members-only site using Node.js, Stripe Checkout, and serverless functions. We’ll also cover the database and authentication pieces you need to connect to your own stack.

## What we’re building

The flow looks like this:

1. A user signs in and clicks **Subscribe**.
2. A serverless function creates a Stripe Checkout Session.
3. The user completes checkout on Stripe’s hosted page.
4. Stripe sends a webhook to your application.
5. Your application updates the user’s subscription record.
6. Protected routes check that record before serving paid content.
7. The user can manage billing through Stripe’s customer portal.

The code below uses standard `Request` and `Response` objects, as supported by many modern serverless frameworks. You’ll need to adapt the route exports and raw request handling to your hosting platform.

## Prerequisites

You’ll need:

- A Stripe account in test mode.
- A Node.js project and a serverless hosting platform.
- Authentication that gives your server a verified user ID.
- A database accessible from your serverless functions.
- The [Stripe CLI](https://docs.stripe.com/stripe-cli) for local webhook testing.

Install Stripe’s Node.js SDK:

```bash
npm install stripe
```

Create a product with a **recurring price** in the Stripe Dashboard. Copy the price ID, which starts with `price_`.

Add these environment variables to your local environment and hosting platform:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID=price_...
STRIPE_WEBHOOK_SECRET=whsec_...
APP_URL=http://localhost:3000
```

The webhook secret comes from the Stripe CLI during local testing and from your webhook endpoint configuration in production. Keep both it and your secret API key on the server.

Create a shared Stripe client:

```js
// lib/stripe.js
import Stripe from "stripe";

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
```

## Decide how to store access

Your database needs a way to connect an application user to a Stripe customer and subscription. A minimal model might look like this:

```text
users
  id
  email
  stripe_customer_id

subscriptions
  stripe_subscription_id
  user_id
  status
```

Treat the Stripe subscription ID as unique. For this example, we’ll grant access when a user has **any** subscription with a status of `active` or `trialing`.

That is a product decision: you may want a grace period for `past_due` subscriptions, or different access for different prices. The important part is to make the rule explicit and enforce it on the server.

The snippets below use a `db` object and `requireUser(request)` as placeholders. Implement these using your database and authentication provider. `requireUser` must verify the user’s session on the server and return a trusted user ID; it must not accept a user ID supplied by the browser.

## Create a Checkout Session

Create a serverless endpoint such as `/api/checkout`. It authenticates the request, finds or creates a Stripe customer, and starts a subscription Checkout Session.

```js
// api/checkout.js
import { stripe } from "../lib/stripe.js";
import { db } from "../lib/db.js";
import { requireUser } from "../lib/auth.js";

export async function POST(request) {
  const user = await requireUser(request);

  let customerId = await db.getStripeCustomerId(user.id);

  if (!customerId) {
    const customer = await stripe.customers.create(
      {
        email: user.email,
        metadata: { userId: user.id },
      },
      {
        // Prevent duplicate customer creation on retries.
        idempotencyKey: `customer-${user.id}`,
      }
    );

    customerId = customer.id;
    await db.setStripeCustomerId(user.id, customerId);
  }

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    customer: customerId,
    line_items: [
      {
        price: process.env.STRIPE_PRICE_ID,
        quantity: 1,
      },
    ],
    success_url: `${process.env.APP_URL}/success`,
    cancel_url: `${process.env.APP_URL}/pricing`,
  });

  return Response.json({ url: session.url });
}
```

Use your database’s uniqueness constraints and atomic operations to protect the user-to-customer mapping when requests happen concurrently. Also add your framework’s CSRF protection to authenticated, state-changing endpoints.

The price comes from a server-side environment variable. That prevents a visitor from changing the price ID in a browser request.

Your pricing page can now call the endpoint:

```html
<button id="subscribe">Subscribe</button>
<p id="error" role="alert"></p>

<script>
  document.querySelector("#subscribe").addEventListener("click", async () => {
    const button = document.querySelector("#subscribe");
    button.disabled = true;

    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
      });

      if (!response.ok) throw new Error("Unable to start checkout");

      const { url } = await response.json();
      window.location.assign(url);
    } catch {
      document.querySelector("#error").textContent =
        "Something went wrong. Please try again.";
      button.disabled = false;
    }
  });
</script>
```

If you use cookie-based authentication, configure this request and endpoint according to your application’s session and CSRF setup.

### Prevent accidental duplicate subscriptions

A user can click Subscribe again later, or open checkout in multiple tabs. Before launching, decide whether multiple subscriptions per user are allowed.

Stripe offers a Checkout setting that can redirect customers with an existing subscription to your site or the customer portal. You should also account for concurrent sessions in your own application if duplicate subscriptions would cause problems. See Stripe’s guide to [limiting customers to one subscription](https://docs.stripe.com/payments/checkout/limit-subscriptions).

## Handle subscription events

The success page is a useful confirmation screen, but it is not a reliable place to grant access. A customer might close the browser before reaching it, and some payment methods complete asynchronously. Stripe recommends using events for fulfillment. [Stripe: Handle post-payment events](https://docs.stripe.com/payments/existing-customers?platform=web&ui=stripe-hosted)

Instead, create a webhook endpoint. Stripe signs webhook requests; verify the signature using the **unmodified raw request body**. Parsing and re-serializing the JSON first can invalidate the signature. [Stripe: Verify webhook signatures](https://docs.stripe.com/webhooks/signature)

```js
// api/stripe-webhook.js
import { stripe } from "../lib/stripe.js";
import { db } from "../lib/db.js";

export async function POST(request) {
  const signature = request.headers.get("stripe-signature");
  const rawBody = await request.text();

  let event;

  try {
    event = stripe.webhooks.constructEvent(
      rawBody,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch {
    return new Response("Invalid webhook signature", { status: 400 });
  }

  try {
    if (event.type.startsWith("customer.subscription.")) {
      const subscription = event.data.object;

      // Fetch current state: webhook events can arrive out of order.
      const current = await stripe.subscriptions.retrieve(subscription.id);
      const customerId =
        typeof current.customer === "string"
          ? current.customer
          : current.customer.id;

      const user = await db.findUserByStripeCustomerId(customerId);

      if (!user) {
        throw new Error(`No user for Stripe customer ${customerId}`);
      }

      await db.upsertSubscription({
        stripeSubscriptionId: current.id,
        userId: user.id,
        status: current.status,
      });
    }

    return new Response("ok", { status: 200 });
  } catch (error) {
    console.error("Webhook processing failed", error);
    return new Response("Webhook processing failed", { status: 500 });
  }
}
```

Configure the endpoint to receive at least:

- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

These events keep the local record in sync as a subscription starts, changes, or ends. Fetching the current subscription helps when events arrive out of order. Your upsert must be safe to repeat because Stripe can deliver an event more than once.

For a production system, consider placing verified events on a durable queue and returning a successful response after the event is safely stored. Serialize updates per subscription or otherwise prevent concurrent workers from overwriting newer state with older state. Add reconciliation against Stripe as a recovery mechanism for missed or failed processing. Stripe documents delivery behavior and subscription events in its [webhook guidance](https://docs.stripe.com/webhooks) and [subscription webhook guide](https://docs.stripe.com/billing/subscriptions/webhooks).

## Protect paid content

Once the webhook updates your database, check access wherever you serve premium content:

```js
// api/members-content.js
import { db } from "../lib/db.js";
import { requireUser } from "../lib/auth.js";

export async function GET(request) {
  const user = await requireUser(request);

  const hasAccess = await db.userHasSubscriptionWithStatus(
    user.id,
    ["active", "trialing"]
  );

  if (!hasAccess) {
    return Response.json(
      { error: "An active subscription is required." },
      { status: 403 }
    );
  }

  return Response.json({
    content: "Welcome to the members-only area!",
  });
}
```

A hidden navigation link or client-side redirect can improve the interface, but it doesn’t protect the content. The server must check access before returning the content itself.

Webhook processing is asynchronous, so a customer might reach the success page before their access record is ready. Show a “Finishing your subscription…” message and retry the authenticated access check for a short period. If it still hasn’t updated, provide a way to contact support.

## Add a customer portal

Subscribers need a way to update their payment details and cancel. Stripe’s customer portal provides a hosted interface for these tasks; configure its available features in the Dashboard first. [Stripe: Customer portal](https://docs.stripe.com/customer-management)

Create an authenticated endpoint:

```js
// api/billing-portal.js
import { stripe } from "../lib/stripe.js";
import { db } from "../lib/db.js";
import { requireUser } from "../lib/auth.js";

export async function POST(request) {
  const user = await requireUser(request);
  const customerId = await db.getStripeCustomerId(user.id);

  if (!customerId) {
    return Response.json(
      { error: "No billing account found." },
      { status: 404 }
    );
  }

  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.APP_URL}/account`,
  });

  return Response.json({ url: session.url });
}
```

Call it from a **Manage billing** button and redirect the user to the returned URL, just as you did for Checkout. The customer ID comes from the authenticated user’s database record, so a visitor cannot choose another customer’s billing account.

A cancellation scheduled for the end of the billing period may leave the subscription active until that period ends. The webhook-driven status will reflect the subsequent change.

## Test the complete flow

Start your application locally, then forward Stripe events to your webhook:

```bash
stripe listen --forward-to localhost:3000/api/stripe-webhook
```

Copy the displayed `whsec_...` value into `STRIPE_WEBHOOK_SECRET` and restart your app if necessary.

In Stripe test mode, complete Checkout using the [test card details](https://docs.stripe.com/testing). Then verify the behavior from the user’s perspective:

- A signed-in user can start checkout and return to the site.
- The webhook creates or updates the correct subscription record.
- An active subscriber can access protected content.
- A user without access receives a `403`.
- Billing portal changes eventually appear in your database.
- Invalid webhook signatures receive a `400`, and processing failures can be retried.

Also test cancellation, a failed payment, duplicate event delivery, and the delay between checkout and webhook processing. Inspect events in the Stripe Dashboard or CLI when something doesn’t behave as expected.

## Go live

Before switching to live keys, create your live product and price, configure a live webhook endpoint and customer portal, and set your production environment variables. Confirm your authentication, database constraints, CSRF protection, monitoring, and subscription access rules with real deployment settings.

That’s the core of a serverless subscription site: Stripe manages billing, your webhook maintains a local view of subscription state, and your application decides which authenticated users can access paid content.

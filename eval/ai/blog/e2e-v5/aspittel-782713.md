# Build a Serverless Subscription Site with Stripe

In this tutorial, we'll build a paid membership site. Someone pays through Stripe Checkout, a Lambda function (created with AWS Amplify) makes them a Cognito user, and once they log in, the gated content is unlocked for them. That setup works well for a course or any other membership site, and you could adapt it to email a digital good to the buyer instead.

**Please note that I work as a Developer Advocate on the AWS Amplify team, if you have any feedback or questions about it, please reach out to me or ask on our discord - discord.gg/amplify!**

If you'd rather watch than read, there's a video version too:

{% youtube DLGF8neT8d0 %}

This post assumes you know intermediate [React](https://welearncode.com/beginners-guide-react-2020/), [AWS Amplify](https://docs.amplify.aws/), and Node.js. The backend doesn't care what's on the frontend, though, so you can use it with any frontend framework you like.

## Set up Stripe

First, create a [Stripe](https://stripe.com/) account and a product. Mine is a $20/month subscription. Then go to your [Checkout settings](https://dashboard.stripe.com/settings/checkout) and enable client-only checkout. You could do a fullstack integration instead, but client-only is a lot faster to get working, and the payment form is still hosted by Stripe, so your app never touches card details.

You'll need your API keys later -- they're on the [developers page](https://dashboard.stripe.com/test/developers) of the test dashboard.

## The frontend

Install the Amplify library and Stripe's JavaScript library:

```bash
npm install aws-amplify @stripe/stripe-js
```

The frontend sends the user to Stripe Checkout for the product. When the payment goes through, Stripe automatically redirects back to the home page. I didn't build an error page for this demo, so if you're shipping this, you'll definitely want one!

To test the purchase, use Stripe's test card number, `4242 4242 4242 4242`.

## The backend

The part that really does the work is a Lambda function. I named mine `stripedemofunction` and put it behind a REST API with the path `/webhook`. I also stored my Stripe secret key as a secret on the function, called `stripe_key`, so it never ends up in the code.

Inside the function's folder, install its two dependencies:

```bash
npm install aws-sdk stripe
```

The function uses the Stripe library to read the event and the AWS SDK to create the Cognito user for whoever just paid. After that, they can log in on the site and see the paid content.

Then tell Stripe where to send events. Add a webhook for the `payment_intent.succeeded` event. The endpoint URL is the API endpoint in your `aws-exports.js` file with `/webhook` on the end.

One caveat: my function doesn't check that the request really came from Stripe. A production app should [verify the webhook signature](https://stripe.com/docs/webhooks/signatures) before creating any users. Verification needs the exact raw request body, so don't parse it as JSON first or the check will fail.

## Clean up

If you were following along and don't want to keep the resources around, this tears everything down:

```bash
amplify delete
```

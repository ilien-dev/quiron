# Add Sign in with Apple to your React App using AWS Amplify!

Sign in with Apple is one of the easiest ways to offer social login. Users get a fast, privacy-friendly option, and you avoid storing another password. Apple also has specific requirements, though. If your app offers third-party or social login on iOS, App Store guidelines expect Sign in with Apple to be included, and it's a common request for web apps too.

In this post we'll add Sign in with Apple to a React app using AWS Amplify Gen 2. Amplify handles the Cognito user pool, the hosted UI redirect, and the token exchange. We'll handle the Apple setup, the backend configuration, and a small React component.

## What you'll need

- An AWS account with Amplify configured
- An Apple Developer account (paid, $99/year)
- Node.js 18 or later
- A React app bootstrapped with Vite, or any setup you prefer
- A domain you control, served over HTTPS. Apple does not allow `localhost` as a return URL for its web sign-in flow, so we'll address local testing later.

## Step 1: Create the Apple credentials

Sign in with Apple needs three pieces of information from the Apple Developer portal: a **Team ID**, a **Services ID** (your client ID), and a **private key**.

**Find your Team ID.** Open the [Apple Developer account page](https://developer.apple.com/account). Your 10-character Team ID is shown in the membership details.

**Create an App ID.** Go to *Certificates, Identifiers & Profiles → Identifiers* and create a new App ID. Enable the **Sign in with Apple** capability. This is required even for web-only flows.

**Create a Services ID.** Still under *Identifiers*, create a new **Services ID**. This is the identifier Cognito will use as the client ID. Enable **Sign in with Apple** on it and click **Configure**.

In the configuration screen:

- **Primary App ID:** select the App ID you just created
- **Domains and Subdomains:** enter your Amplify domain, without the protocol, for example `main.d1234abcd.amplifyapp.com`
- **Return URLs:** enter your Cognito domain callback. You'll get this value in Step 3, so come back to this field later. It follows this pattern:

```
https://<your-cognito-domain>.auth.<region>.amazoncognito.com/oauth2/idpresponse
```

**Create a key.** Under *Keys*, create a new key, enable **Sign in with Apple**, and link it to your primary App ID. Download the `.p8` file. Apple only lets you download it once, so store it somewhere safe. Note the 10-character **Key ID** shown on the page.

You now have four values: Team ID, Services ID, Key ID, and the contents of the `.p8` private key.

## Step 2: Configure the auth resource

Install the Amplify libraries if you haven't already:

```bash
npm install aws-amplify @aws-amplify/ui-react
npm install -D @aws-amplify/backend @aws-amplify/backend-cli
```

Open `amplify/auth/resource.ts` and define your auth resource. Amplify stores secrets in its secrets manager, so the Apple credentials never end up in your source code.

```typescript
import { defineAuth, secret } from '@aws-amplify/backend';

export const auth = defineAuth({
  loginWith: {
    email: true,
    externalProviders: {
      signInWithApple: {
        clientId: secret('APPLE_CLIENT_ID'),
        keyId: secret('APPLE_KEY_ID'),
        teamId: secret('APPLE_TEAM_ID'),
        privateKey: secret('APPLE_PRIVATE_KEY'),
        scopes: ['email', 'name'],
      },
      callbackUrls: [
        'http://localhost:5173/',
        'https://main.d1234abcd.amplifyapp.com/',
      ],
      logoutUrls: [
        'http://localhost:5173/',
        'https://main.d1234abcd.amplifyapp.com/',
      ],
    },
  },
});
```

A few notes on this file:

- `scopes` controls what Apple returns. Apple only sends a user's name on their **first** sign-in, so capture it then. Cognito stores it, so you won't lose it later.
- `callbackUrls` and `logoutUrls` must match exactly, including the trailing slash, what your app sends after sign-in.
- The `localhost` entries are useful for development, but Apple itself won't redirect back to localhost. We'll deal with that shortly.

Next, store the secrets in your sandbox environment:

```bash
npx ampx sandbox secret set APPLE_CLIENT_ID
npx ampx sandbox secret set APPLE_KEY_ID
npx ampx sandbox secret set APPLE_TEAM_ID
npx ampx sandbox secret set APPLE_PRIVATE_KEY
```

Each command prompts for a value. For `APPLE_PRIVATE_KEY`, paste the full contents of the `.p8` file, including the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines.

Then start the sandbox, which deploys your backend:

```bash
npx ampx sandbox
```

When the deployment finishes, Amplify writes `amplify_outputs.json` to your project root. It contains your Cognito domain and client configuration.

## Step 3: Finish the Apple return URL

Open `amplify_outputs.json` and find `auth.oauth.domain`. It will look something like `myapp-sandbox-abc123.auth.us-east-1.amazoncognito.com`. Use that domain to build the return URL from Step 1:

```
https://myapp-sandbox-abc123.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
```

Go back to your Services ID configuration in the Apple Developer portal and paste that URL into **Return URLs**. Save the changes.

If you're using a sandbox or a short-lived environment, the domain may change between deployments. Pin it to a stable environment or branch when you move toward production.

## Step 4: Wire up the React app

Configure Amplify once, at the top of your app. In `src/main.tsx`:

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Amplify } from 'aws-amplify';
import outputs from '../amplify_outputs.json';
import App from './App';

Amplify.configure(outputs);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

Now create a sign-in component. It uses `signInWithRedirect` to send the user to the Cognito hosted UI, which then forwards them to Apple:

```tsx
// src/components/AppleSignIn.tsx
import { signInWithRedirect, signOut } from 'aws-amplify/auth';

export function AppleSignIn() {
  return (
    <button
      onClick={() => signInWithRedirect({ provider: 'Apple' })}
      style={{
        background: '#000',
        color: '#fff',
        padding: '12px 20px',
        borderRadius: 8,
        border: 'none',
        cursor: 'pointer',
        fontSize: 16,
      }}
    >
       Sign in with Apple
    </button>
  );
}

export function SignOutButton() {
  return <button onClick={() => signOut()}>Sign out</button>;
}
```

After Apple redirects back to your app, Amplify exchanges the authorization code for tokens automatically. You can read the current user with `getCurrentUser` and `fetchUserAttributes`:

```tsx
// src/App.tsx
import { useEffect, useState } from 'react';
import { getCurrentUser, fetchUserAttributes, signInWithRedirect } from 'aws-amplify/auth';
import { Hub } from 'aws-amplify/utils';
import { AppleSignIn, SignOutButton } from './components/AppleSignIn';

export default function App() {
  const [user, setUser] = useState<string | null>(null);

  async function loadUser() {
    try {
      await getCurrentUser();
      const attrs = await fetchUserAttributes();
      setUser(attrs.name ?? attrs.email ?? 'Signed in');
    } catch {
      setUser(null);
    }
  }

  useEffect(() => {
    loadUser();
    const unsubscribe = Hub.listen('auth', ({ payload }) => {
      if (payload.event === 'signedIn') loadUser();
      if (payload.event === 'signedOut') setUser(null);
    });
    return unsubscribe;
  }, []);

  if (!user) return <AppleSignIn />;

  return (
    <div>
      <p>Welcome, {user}</p>
      <SignOutButton />
    </div>
  );
}
```

The `Hub` listener matters. After the redirect, the auth state changes once Amplify finishes the token exchange, and the listener catches that event so the UI updates without a page reload.

## Step 5: Test it

Apple's web flow requires a real HTTPS domain. You have two options for testing:

1. **Deploy a branch with Amplify Hosting.** Push your code, let the build finish, and test against the deployed URL. Make sure that URL is in both your Cognito `callbackUrls` and the Apple Services ID domains.
2. **Use a tunnel.** Tools like ngrok can expose your local Vite server over HTTPS. Add the tunnel URL to your Apple domains and to the Cognito callback URLs, then open the tunnel URL in your browser.

Once the redirect works, sign in with an Apple ID. On the first sign-in, Apple asks whether to share or hide your email. If you choose to hide it, Apple gives Cognito a private relay address, and that address is what you'll see in `fetchUserAttributes`. The same applies to name data: if the user doesn't share it on the first sign-in, you won't receive it later.

## Common pitfalls

- **`redirect_uri_mismatch` or an Apple error page:** The return URL in the Services ID must exactly match the Cognito `/oauth2/idpresponse` URL. Check for typos and stale domains after redeploying.
- **Name is missing:** Apple only sends the name on the first authorization. To test again, revoke the app under *Settings → Sign-In and Security → Sign in with Apple* on your Apple ID, then sign in again.
- **Private key errors:** Make sure the full `.p8` contents were stored, including the header and footer lines. A key with stripped line breaks will fail.
- **Works in sandbox, fails in production:** The Cognito domain and callback URLs are environment-specific. Add every production URL to the Amplify config and to the Apple domains.

## Wrapping up

Sign in with Apple takes some setup, mostly on Apple's side, but Amplify Gen 2 covers the parts that are tedious to build yourself. You get a Cognito user pool that federates with Apple, secrets kept out of your repo, and a React integration that needs only a couple of function calls.

From here you can add Google or other providers the same way, map Apple attributes into your own user profile table, or use the Cognito user ID as the key for your data. If you run into trouble, the most useful first check is the Return URL in the Apple portal. Most issues trace back to it.

Happy building!

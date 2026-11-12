# Use Next.js 12 on Netlify

Deploying a Next.js application involves more than uploading HTML files. Your app might include server-rendered pages, API routes, optimized images, and pages that refresh their content after deployment. The hosting platform needs to understand those features.

Netlify provides that connection through its Next.js runtime. In this guide, we’ll configure a Next.js 12 project, deploy it from Git, and check that server-side rendering works.

*Version note: This guide covers an existing Next.js 12 application. Netlify documents this version under its legacy v4 runtime. For a new project, start with a current Next.js release and its corresponding deployment documentation.* [Netlify runtime documentation](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/legacy-runtime/overview/)

**Start with a working local build**

Before changing deployment settings, make sure your application builds on your machine:

```bash
npm install
npm run build
```

Your `package.json` should include the usual Next.js scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

Commit your lockfile alongside your source code. That helps Netlify install the same dependency versions you tested locally.

Next.js 12 introduced a Rust-based compiler, along with features such as Middleware. Some features were experimental at launch, so check the documentation for your specific minor version before adopting an example. [Next.js 12 announcement](https://nextjs.org/blog/next-12)

**Configure the Netlify runtime**

For an existing Next.js 12 application, install the legacy runtime explicitly:

```bash
npm install --save-dev @netlify/plugin-nextjs@4
```

Create a `netlify.toml` file in your project root:

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

The build command creates your production application. The plugin adapts that output for Netlify, including the handling needed for dynamic features.

Use `.next` as the publish directory for this setup. A static export is a separate deployment approach and cannot run pages that require server-side rendering. Netlify’s legacy runtime documentation describes the supported rendering features and configuration. [Configuration reference](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/legacy-runtime/overview/)

**Connect your repository**

Push your project to a Git provider, then import the repository into Netlify.

Check that the build command and publish directory match your configuration. If the application lives inside a monorepo, also set the correct base directory so Netlify builds from the application’s folder.

Add any required environment variables before deploying. Keep private credentials in Netlify’s environment settings, and check that each variable is available in the deployment context where you need it.

Start the deployment and follow the build log. A successful local build is useful evidence, but the hosted build also checks dependency installation and runtime packaging.

**Verify a dynamic page**

A homepage loading successfully doesn’t prove that server-side rendering works. Add a small diagnostic page at `pages/server-check.js`:

```jsx
export async function getServerSideProps() {
  return {
    props: {
      renderedAt: new Date().toISOString(),
    },
  };
}

export default function ServerCheck({ renderedAt }) {
  return <p>Rendered on the server at: {renderedAt}</p>;
}
```

Deploy the change, visit `/server-check`, and refresh. The timestamp should update as requests trigger server rendering.

Then exercise the features your application actually uses: API routes, redirects, images, and any pages with incremental static regeneration. Check function logs if a route builds successfully but fails when requested.

**Watch the Middleware version**

Middleware changed during the Next.js 12 release cycle. Early examples use `pages/_middleware.js`; later releases use a root-level `middleware.js` file.

That makes copying an old tutorial surprisingly easy to get wrong. Match both the file location and API usage to your installed Next.js version. Netlify’s announcement for Next.js 12.2 explains the transition to stable Middleware support. [Next.js 12.2 on Netlify](https://www.netlify.com/blog/deploy-nextjs-12-2/)

Once deployment works, use preview deployments to test future changes before they reach production. A repeatable build and a few targeted checks make maintaining your Next.js 12 application much easier.

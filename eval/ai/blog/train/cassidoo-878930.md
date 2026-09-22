# Use Next.js 12 on Netlify

Next.js 12 brought faster builds, improved middleware, React 18 support, and a Rust-powered compiler. The good news is that you can deploy a Next.js 12 application to Netlify without giving up features such as server-side rendering, API routes, redirects, or image optimization.

This guide walks through the process from project creation to production deployment.

## Create a Next.js 12 application

Start by creating a project with the Next.js 12 release line:

```bash
npx create-next-app@12 my-next-app
cd my-next-app
```

Confirm the installed version:

```bash
npm list next
```

The output should show a `12.x` version. You can now run the development server:

```bash
npm run dev
```

Open `http://localhost:3000` and verify that the starter page loads.

## Push the project to Git

Netlify works best with a Git-based deployment workflow. Create a repository on your preferred Git provider, then commit and push the application:

```bash
git init
git add .
git commit -m "Create Next.js 12 application"
git branch -M main
git remote add origin https://github.com/your-name/my-next-app.git
git push -u origin main
```

Every future push can automatically trigger a new Netlify deployment.

## Import the repository into Netlify

Sign in to Netlify and choose **Add new site**, followed by **Import an existing project**. Connect your Git provider and select the repository.

Netlify should detect that the project uses Next.js and provide the appropriate defaults:

```text
Build command: npm run build
Publish directory: .next
```

Select **Deploy site** to start the first build.

Netlify’s Next.js runtime translates framework features into the platform services needed to run them. Static pages are delivered through the CDN, while dynamic functionality is handled using serverless or edge infrastructure.

## Configure the site explicitly

Automatic detection is usually enough, but you can make the build configuration visible by adding a `netlify.toml` file at the project root:

```toml
[build]
  command = "npm run build"
  publish = ".next"
```

Commit and push the file:

```bash
git add netlify.toml
git commit -m "Add Netlify configuration"
git push
```

Netlify will detect the new commit and rebuild the site.

Avoid configuring `next export` unless the application is intentionally fully static. Exporting removes access to features that require a Next.js server runtime, including server-side rendering and API routes.

## Add environment variables

Applications often depend on API keys or service URLs. Do not commit secrets to the repository. Add them through the site’s environment-variable settings in Netlify instead.

For example:

```text
API_URL=https://api.example.com
API_TOKEN=your-secret-token
```

Access server-only variables normally:

```js
const token = process.env.API_TOKEN
```

Variables that must be exposed to browser code require the `NEXT_PUBLIC_` prefix:

```text
NEXT_PUBLIC_SITE_URL=https://example.netlify.app
```

After changing an environment variable, trigger a new deployment so Next.js can include it during the appropriate build or runtime phase.

## Test dynamic features

Before calling the deployment complete, test more than the home page. Check any pages using `getServerSideProps`, API endpoints under `pages/api`, dynamic routes, redirects, and images rendered with `next/image`.

A simple API route can confirm that dynamic execution works:

```js
// pages/api/hello.js
export default function handler(req, res) {
  res.status(200).json({ message: "Hello from Netlify!" })
}
```

Deploy the change and visit `/api/hello`. You should receive the JSON response.

## Troubleshoot builds

If a deployment fails, open its build log first. Common causes include an unsupported Node.js version, missing environment variables, dependency conflicts, and code that relies on local files unavailable at runtime.

You can specify a Node.js version with an `.nvmrc` file:

```text
16
```

It is also helpful to reproduce the production build locally:

```bash
npm run build
npm start
```

Once the build succeeds, Netlify gives the site a public URL and continues deploying each push to your production branch. With Git-based previews for proposed changes and built-in support for Next.js features, Next.js 12 fits comfortably into Netlify’s deployment workflow.
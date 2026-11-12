Every modern web app eventually hits the same wall. The JavaScript bundle grows, the first load gets slower, and Lighthouse starts showing red numbers. Code splitting is the usual first fix: break the giant bundle into smaller chunks and load them on demand. But code splitting creates its own problem. When a user clicks a link to a lazily loaded route, they now have to wait for a network request that didn't exist before.

The answer is to combine two techniques that work well together: **prefetching**, which gets code onto the device before it's needed, and **caching**, which makes sure that code stays there. In this post we'll look at how each works, how to set them up in a typical build, and the mistakes that can quietly cancel out the gains.

## The Problem With "Load It Later"

Say you have a dashboard app with three routes: `/`, `/reports`, and `/settings`. Without splitting, all three ship in one `main.js`. With splitting, you might have:

```
main.4f2a91.js        (shell + home)
reports.a83c1d.js     (charts library, report views)
settings.19be07.js    (forms, validation)
```

The initial load is lighter, which is good. But when the user clicks "Reports", the browser has to:

1. Resolve DNS and open a connection (if not already open)
2. Request `reports.a83c1d.js`
3. Download it
4. Parse and execute it

On a fast connection that may be 50ms. On a mid-range phone over a spotty 4G connection, it can be over a second, and that delay shows up exactly when the user is waiting for something to happen.

Prefetching moves steps 1 through 3 into idle time *before* the click.

## Resource Hints: preload vs. prefetch vs. modulepreload

Browsers give us a few `<link>` hints. They sound similar but they do different jobs.

### `preload`: "I need this now"

```html
<link rel="preload" href="/fonts/inter.woff2" as="font" crossorigin>
```

`preload` is high priority. It tells the browser that the current page will definitely use this resource soon. Use it for critical assets the browser can't find early on its own, like fonts referenced from CSS or a hero image set via JavaScript.

Don't use `preload` for "maybe later" bundles. It competes with your critical resources for bandwidth.

### `prefetch`: "I'll probably need this next"

```html
<link rel="prefetch" href="/assets/reports.a83c1d.js">
```

`prefetch` is low priority. The browser fetches the resource when it's idle and stores it in the HTTP cache. When the user later navigates and the app requests that chunk, it comes from cache almost instantly.

This is the right tool for route chunks the user is *likely* to need.

### `modulepreload`: preload for ES modules

```html
<link rel="modulepreload" href="/assets/reports.a83c1d.js">
```

If you ship native ES modules (Vite does by default), `modulepreload` fetches the module and can also parse and compile it ahead of time. Vite automatically adds `modulepreload` for the dependencies of chunks it loads. It's more eager than `prefetch`, so treat it like `preload`: use it for things you'll need on this page.

### `preconnect`: warm up the connection

```html
<link rel="preconnect" href="https://cdn.example.com" crossorigin>
```

If your chunks live on a separate CDN origin, `preconnect` handles DNS, TCP, and TLS ahead of time. It's cheap and often overlooked.

## Prefetching With Your Bundler

You rarely want to write these tags by hand, since chunk filenames change on every build. Let the bundler do it.

### Webpack magic comments

Webpack supports inline comments on dynamic imports:

```js
const Reports = lazy(() =>
  import(/* webpackChunkName: "reports", webpackPrefetch: true */ './routes/Reports')
);
```

With `webpackPrefetch: true`, webpack injects a `<link rel="prefetch">` for that chunk once the parent chunk has loaded. There's also `webpackPreload: true`, but as discussed above, that's usually not what you want for routes.

### Vite and Rollup

Vite doesn't have a built-in prefetch comment, but you can trigger a dynamic import early, since a dynamic import is just a promise you can start whenever you like:

```js
const loadReports = () => import('./routes/Reports.jsx');
const Reports = lazy(loadReports);

// Somewhere after the initial render settles:
requestIdleCallback(() => loadReports());
```

Because module imports are cached by the module system, calling `loadReports()` twice doesn't fetch twice. The second call resolves from the existing promise.

## Smarter Prefetching: Intent-Based Loading

Prefetching *everything* on idle wastes data, which matters for users on metered connections. A better approach is to prefetch based on signals that the user is about to navigate.

### On hover or focus

```js
function PrefetchLink({ to, load, children }) {
  const prefetch = () => load();
  return (
    <Link to={to} onMouseEnter={prefetch} onFocus={prefetch} onTouchStart={prefetch}>
      {children}
    </Link>
  );
}

<PrefetchLink to="/reports" load={loadReports}>Reports</PrefetchLink>
```

The gap between hover and click is often 200–400ms, which is frequently enough to fetch a medium-sized chunk.

### On viewport visibility

For links further down the page, an `IntersectionObserver` works well:

```js
const observer = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (entry.isIntersecting) {
      const loader = loaders[entry.target.dataset.route];
      loader?.();
      observer.unobserve(entry.target);
    }
  }
});

document.querySelectorAll('a[data-route]').forEach((a) => observer.observe(a));
```

Libraries like Google's `quicklink` package this pattern for you.

### Respect the user's connection

Always check whether prefetching is appropriate:

```js
function shouldPrefetch() {
  const conn = navigator.connection;
  if (!conn) return true;
  if (conn.saveData) return false;
  return !/(^|-)2g$/.test(conn.effectiveType);
}
```

If the user has Data Saver turned on, don't spend their bandwidth guessing what they'll do next.

## Caching: Make Every Fetch Count Once

Prefetching only helps if the prefetched file is still in the cache when it's needed, and if it isn't downloaded again on the next visit. This is where HTTP caching comes in.

### Content-hashed filenames

The foundation is putting a content hash in every bundle filename:

```js
// webpack.config.js
output: {
  filename: '[name].[contenthash].js',
  chunkFilename: '[name].[contenthash].js',
}
```

Vite does this by default. When the file contents change, the filename changes, so you never have to worry about a stale cached version being served under the same URL.

### Long-lived, immutable cache headers

Since hashed files never change, you can tell browsers to cache them aggressively:

```
Cache-Control: public, max-age=31536000, immutable
```

The `immutable` directive tells the browser not to revalidate the file even when the user hits refresh. On repeat visits, unchanged chunks load with zero network requests.

Your HTML entry point is different. It references the hashed files, so it must stay fresh:

```
Cache-Control: no-cache
```

`no-cache` doesn't mean "don't cache." It means "revalidate before use," which is cheap with ETags and guarantees users pick up new deployments.

### Keep vendor code stable

If your app code and your dependencies live in the same chunk, every small app change invalidates the whole thing. Split them:

```js
optimization: {
  runtimeChunk: 'single',
  splitChunks: {
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendor',
        chunks: 'all',
      },
    },
  },
},
```

`runtimeChunk: 'single'` pulls webpack's small manifest into its own file so that changing one chunk doesn't change the hash of every other chunk. Now a typo fix in your app ships a new `main.[hash].js` while `vendor.[hash].js`, often the largest file, stays cached.

### Service workers for offline and precaching

For apps where repeat visits matter most, a service worker can precache chunks after the first visit. With Workbox:

```js
import { precacheAndRoute } from 'workbox-precaching';
precacheAndRoute(self.__WB_MANIFEST);
```

The build plugin injects a manifest of your hashed assets. After the first load, every route chunk is available offline and loads straight from the service worker cache. Just be deliberate: precaching your entire app on first visit is essentially prefetching everything, so the same data-cost concerns apply.

## Common Pitfalls

**Prefetching with the wrong cache headers.** If chunks are served with `no-store`, the prefetched response may be thrown away and fetched again. Check your CDN config.

**Prefetching across origins without CORS alignment.** If the prefetch request and the actual script request use different `crossorigin` modes, the browser may treat them as different cache entries and download twice. Keep them consistent.

**Overusing `preload`.** Chrome warns in the console when a preloaded resource isn't used within a few seconds. Those warnings are a signal you're competing with critical resources.

**Unstable chunk hashes.** If hashes change on every build even without code changes, your long-lived caching gives you nothing. Use deterministic module IDs (`optimization.moduleIds: 'deterministic'`, the default in webpack 5).

## Measure It

Don't trust intuition here, verify:

- In Chrome DevTools' **Network** panel, prefetched requests show "Lowest" priority, and later requests for the same file show `(prefetch cache)` or `(disk cache)` in the Size column.
- Use the **Performance** panel to compare route transition times with and without prefetching.
- Track real-user metrics like **Interaction to Next Paint (INP)** around navigation to confirm the change helps actual users, not just your laptop.

## Wrapping Up

Code splitting shrinks your initial load, but it moves cost to later interactions. Prefetching hides that cost by loading likely-needed chunks during idle time or on clear signs of user intent. Caching makes sure each byte is downloaded once: content-hashed filenames, `immutable` headers on assets, `no-cache` on HTML, and a stable vendor chunk.

Put together, the result is an app that starts fast, navigates instantly, and loads even faster on repeat visits. That's the kind of performance users notice, even if they never know why.

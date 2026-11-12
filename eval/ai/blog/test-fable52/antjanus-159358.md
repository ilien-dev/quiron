Most JavaScript performance advice focuses on shipping less code. That's the right first step, but once you've split your bundle into sensible chunks, a second question appears: *when* does each chunk get downloaded, and how often does a user have to download it again?

Those two questions map to two tools: **prefetching**, which moves downloads earlier so they're ready before the user needs them, and **caching**, which makes sure a download only happens once. They also depend on each other, since a prefetch is only useful if the result is stored somewhere the later request can find it.

This post walks through how to use both together.

## The starting point: code splitting

Prefetching and long-term caching both assume your app is already split into chunks. If everything is in one `bundle.js`, there's nothing to prefetch, and any one-line change invalidates the entire file.

The basic unit of splitting is the dynamic import:

```js
// Loaded only when the user opens the settings page
const openSettings = async () => {
  const { SettingsPanel } = await import('./SettingsPanel.js');
  render(SettingsPanel);
};
```

Bundlers turn each `import()` into a separate chunk. The initial load gets smaller, but the cost has moved: the user now waits on a network request when they click "Settings". Prefetching removes that wait.

## Resource hints: preload, prefetch, modulepreload

Browsers give you three related hints, and mixing them up is a common mistake.

| Hint | Meaning | Priority |
|---|---|---|
| `preload` | "I need this for the *current* page, fetch it now" | High |
| `modulepreload` | Same as preload, but for ES modules (also parses and compiles them) | High |
| `prefetch` | "I'll *probably* need this for a future navigation or interaction" | Lowest, during idle time |

```html
<!-- Needed for this page, discovered late -->
<link rel="modulepreload" href="/assets/chart-a1b2c3.js">

<!-- Likely needed soon, fetch when idle -->
<link rel="prefetch" href="/assets/settings-d4e5f6.js" as="script">
```

The rule of thumb is to use `preload` for things the current page will definitely use, and `prefetch` for things the user might use next. Using `preload` for speculative resources is actively harmful, because it competes with your critical resources for bandwidth. Chrome will also warn you in the console if a preloaded resource isn't used within a few seconds.

Browser support for `prefetch` has historically been uneven, with Safari in particular lagging. Since it's a hint, unsupported browsers simply ignore it, and the dynamic import still works as usual.

## Prefetching with your bundler

You rarely write those `<link>` tags by hand, because chunk filenames contain hashes that change on each build.

### webpack

webpack supports "magic comments" inside the import call:

```js
const openSettings = async () => {
  const { SettingsPanel } = await import(
    /* webpackPrefetch: true */
    /* webpackChunkName: "settings" */
    './SettingsPanel.js'
  );
  render(SettingsPanel);
};
```

With `webpackPrefetch: true`, webpack's runtime injects a `<link rel="prefetch">` for the chunk once the parent chunk has finished loading. There's also `webpackPreload: true`, which requests the chunk in parallel with its parent. Use that sparingly, for chunks you know are needed immediately.

### Vite

Vite takes a different approach. It automatically emits `modulepreload` links for the entry chunk's direct imports, and when a dynamic import fires, it preloads that chunk's own dependencies in parallel to avoid a request waterfall. It doesn't have a built-in equivalent of `webpackPrefetch`, so speculative prefetching is something you do yourself or through a plugin.

## Smarter prefetching: wait for a signal

Prefetching every lazy chunk on page load is easy, but wasteful. A better strategy is to wait for evidence of user intent.

### On hover or focus

A user who hovers over a link typically takes a couple hundred milliseconds to click it. That's often enough time to fetch a chunk:

```js
const prefetched = new Set();

function prefetchOnIntent(element, loader) {
  const run = () => {
    if (prefetched.has(loader)) return;
    prefetched.add(loader);
    loader().catch(() => prefetched.delete(loader));
  };
  element.addEventListener('mouseenter', run, { once: true });
  element.addEventListener('focus', run, { once: true });
  element.addEventListener('touchstart', run, { once: true, passive: true });
}

prefetchOnIntent(
  document.querySelector('#settings-link'),
  () => import('./SettingsPanel.js')
);
```

Calling `import()` early works as a prefetch because the module system caches the result. The later "real" import resolves instantly. The trade-off is that the module is also parsed and executed, unlike a `<link rel="prefetch">`, which only downloads. For most UI chunks that's fine, but be careful with modules that have side effects at the top level.

### When visible

For link-heavy pages, you can prefetch when a link scrolls into view:

```js
const observer = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    observer.unobserve(entry.target);
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = entry.target.dataset.chunk;
    document.head.appendChild(link);
  }
});

document.querySelectorAll('a[data-chunk]').forEach((a) => observer.observe(a));
```

Most meta-frameworks ship this behaviour. Next.js's `<Link>` prefetches when links enter the viewport, and SvelteKit and Remix offer hover- and viewport-based options. If you use a framework, check what it already does before adding your own.

### Respect the user's connection

Prefetching spends the user's data on a guess. Skip it when they've asked you to be frugal:

```js
function shouldPrefetch() {
  const conn = navigator.connection;
  if (!conn) return true;
  if (conn.saveData) return false;
  return !/(^|-)2g$/.test(conn.effectiveType);
}
```

`navigator.connection` isn't available in every browser, hence the fallback.

## Caching: make each download count

A prefetched chunk sits in the HTTP cache until it's needed. If your server sends it without cacheable headers, the browser may fetch it a second time when the real request arrives, and you'll have doubled the cost instead of removing it. So prefetching only works if caching is set up correctly.

### Content hashes in filenames

The foundation of long-term caching is putting a hash of the file's contents in its name:

```js
// webpack.config.js
module.exports = {
  output: {
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].js',
  },
};
```

Vite and other Rollup-based tools do this by default. If the content changes, the URL changes. If the URL is the same, the content is guaranteed to be the same.

### Cache headers

That guarantee lets you cache hashed assets as aggressively as possible:

```
# Hashed assets: /assets/settings.d4e5f6.js
Cache-Control: public, max-age=31536000, immutable

# HTML documents
Cache-Control: no-cache
```

`immutable` tells the browser not to revalidate even when the user reloads. `no-cache` on the HTML doesn't mean "don't store"; it means "check with the server before using". That check is how users pick up new deployments: fresh HTML points to new hashed URLs, and everything unchanged comes straight from cache.

Never apply the long-lived header to HTML or to unhashed files. You'd have no way to push an update to users who have them cached.

### Keep hashes stable

Content hashing only pays off if hashes don't change unnecessarily. Two settings matter in webpack:

```js
module.exports = {
  optimization: {
    runtimeChunk: 'single',
    moduleIds: 'deterministic',
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
  },
};
```

- **`runtimeChunk: 'single'`** extracts webpack's runtime, which contains the map of chunk names to hashes, into its own small file. Without it, that map lives in your entry chunk, so changing any chunk changes the entry chunk's hash too.
- **`moduleIds: 'deterministic'`** stops module IDs from shifting when you add or remove an unrelated import. It's the default in production mode, but worth knowing about.
- **The vendor cache group** separates dependencies from application code. Your app code changes on every deploy, while your dependencies might change once a month, so returning users can keep the vendor chunk cached.

Don't go further and put every package into its own chunk unless you've measured a benefit. Many small files compress less efficiently than a few larger ones.

## Going further with a service worker

The HTTP cache is controlled by the browser and can evict entries whenever it likes. A service worker gives you a cache you control. With Workbox, precaching your build output takes a few lines:

```js
// sw.js
import { precacheAndRoute } from 'workbox-precaching';

// The manifest is injected by the Workbox build plugin
precacheAndRoute(self.__WB_MANIFEST);
```

This downloads every listed chunk at install time and serves it cache-first afterwards, which is prefetching and caching in one step. Since it downloads everything, limit the precache manifest to chunks most users will need, and let runtime caching handle the rest.

## Measure the result

It's easy to make things worse with these techniques, so verify each change:

1. **Network panel**: prefetched requests should appear with "Lowest" priority, and the later real request should show "(prefetch cache)" or "(disk cache)" rather than a transfer size.
2. **Repeat visits**: reload after a deployment that touched one file. Only that chunk, the runtime and the HTML should be re-downloaded.
3. **Prefetch waste**: if you have analytics, compare the chunks you prefetch against the chunks users actually load. A chunk that's prefetched for everyone and used by 2% of users should be moved to hover-based loading.
4. **Field data**: watch Interaction to Next Paint for lazy-loaded interactions, and Largest Contentful Paint to confirm prefetching isn't competing with the initial render.

## Summary

- Split your code first, since both techniques depend on it.
- Use `preload`/`modulepreload` for what the current page needs and `prefetch` for what comes next.
- Prefetch on a signal of intent (hover, visibility) rather than all at once, and respect `saveData`.
- Use content-hashed filenames with `max-age=31536000, immutable`, and serve HTML with `no-cache`.
- Extract the runtime and vendor code so hashes stay stable between deploys.
- Check the network panel to confirm prefetched chunks are being reused and not fetched twice.

Set up this way, users download each chunk once, and it is usually already there when they need it.

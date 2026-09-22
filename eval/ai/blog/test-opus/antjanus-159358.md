# Using Prefetch and Caching For Better JavaScript Bundle Loading

Modern web apps ship a lot of JavaScript. Even with code splitting, users often wait for chunks to download the moment they click a link or open a modal. The good news is that browsers give us a set of tools to get ahead of that wait: resource hints like `prefetch` and `preload`, plus HTTP caching and service workers. Used together, they can make your app feel dramatically faster without changing a single line of business logic.

In this post, we'll walk through how prefetching works, how to combine it with caching, and some practical patterns you can drop into a webpack, Vite, or plain-HTML setup today.

## The Problem: Code Splitting Moves the Wait, It Doesn't Remove It

Code splitting is one of the best things you can do for initial load performance. Instead of shipping one giant `bundle.js`, you split your app into route-level or component-level chunks:

```javascript
const Settings = React.lazy(() => import('./pages/Settings'));
```

Now the Settings page only loads when the user navigates there. Your initial bundle is smaller, and your Time to Interactive improves.

But there's a catch. When the user *does* click "Settings," the browser has to go fetch that chunk over the network. On a slow connection, that could mean a spinner for a second or two. We traded a slower first load for slower navigation.

What we really want is to load those chunks *before* the user needs them, at a time when the browser isn't busy doing anything more important. That's exactly what prefetching is for.

## Prefetch vs. Preload

These two hints get confused a lot, so let's clear them up.

**`preload`** tells the browser: "You will need this resource for the current page, and soon. Fetch it with high priority."

```html
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
```

**`prefetch`** tells the browser: "The user will *probably* need this resource for a future navigation. Fetch it at low priority when you're idle."

```html
<link rel="prefetch" href="/static/js/settings.chunk.js">
```

The key differences:

| | `preload` | `prefetch` |
|---|---|---|
| Priority | High | Lowest |
| Used for | Current page | Future navigation |
| Timing | Immediately | When the browser is idle |
| Wasted if unused? | Yes, and the browser warns you | Yes, but cheaply |

A good rule of thumb: preload what you *know* you need right now, prefetch what you *think* you'll need next.

## Prefetching With Webpack Magic Comments

If you're using webpack, you get prefetching almost for free through magic comments:

```javascript
const Settings = React.lazy(() =>
  import(/* webpackPrefetch: true */ './pages/Settings')
);
```

When the parent chunk loads, webpack injects a `<link rel="prefetch">` tag for the Settings chunk into the document head. The browser will then fetch it during idle time. When the user eventually navigates to Settings, the chunk is already sitting in the cache.

There's also `webpackPreload: true`, which is useful for chunks that the current route needs in parallel with the parent, but use it sparingly. Preloading too much competes with your critical resources and can make things slower.

## Prefetching in Vite

Vite handles preloading of direct dynamic import dependencies automatically through its `modulepreload` polyfill. For prefetching routes the user might visit later, you can add the hints yourself:

```javascript
function prefetch(url) {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = url;
  document.head.appendChild(link);
}
```

Or, more simply, just trigger the dynamic import early. Calling `import()` returns a promise and caches the module, so calling it again later resolves instantly:

```javascript
const loadSettings = () => import('./pages/Settings');

// Warm it up
loadSettings();
```

## Smarter Prefetching: Prefetch on Intent

Prefetching everything upfront wastes bandwidth, especially on mobile. A better approach is to prefetch based on user intent. Two common signals are hover and viewport visibility.

### Prefetch on hover

When a user hovers over a link, there's usually 200–400ms before they actually click. That's often enough time to download a small chunk.

```javascript
function PrefetchLink({ to, loader, children }) {
  const handleMouseEnter = () => {
    loader();
  };

  return (
    <Link to={to} onMouseEnter={handleMouseEnter} onFocus={handleMouseEnter}>
      {children}
    </Link>
  );
}

<PrefetchLink to="/settings" loader={() => import('./pages/Settings')}>
  Settings
</PrefetchLink>
```

Note the `onFocus` handler: keyboard users deserve fast navigation too.

### Prefetch on visibility

For links further down the page, you can use `IntersectionObserver` to prefetch when they scroll into view. This is the approach libraries like Quicklink use, and it's what Next.js does with its `<Link>` component in production.

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const loader = loaders[entry.target.dataset.route];
      loader?.();
      observer.unobserve(entry.target);
    }
  });
});

document.querySelectorAll('a[data-route]').forEach((link) => {
  observer.observe(link);
});
```

### Respect the user's connection

Before prefetching anything, check whether the user has asked to save data or is on a slow connection:

```javascript
function shouldPrefetch() {
  const conn = navigator.connection;
  if (!conn) return true;
  if (conn.saveData) return false;
  return !/2g/.test(conn.effectiveType);
}
```

This is a small detail, but it makes a big difference for users on metered plans.

## Caching: Making Prefetched Bundles Stick

Prefetching only helps if the prefetched file is still in the cache when it's needed. That's where caching strategy comes in.

### Content hashing

The foundation of good bundle caching is putting a content hash in every filename:

```javascript
// webpack.config.js
output: {
  filename: '[name].[contenthash].js',
  chunkFilename: '[name].[contenthash].chunk.js',
}
```

Now each file's name changes only when its contents change. That means you can cache these files forever.

### Long-lived Cache-Control headers

With hashed filenames, set aggressive caching headers on your static assets:

```
Cache-Control: public, max-age=31536000, immutable
```

The `immutable` directive tells the browser not to bother revalidating the file, even on a reload. Your HTML, on the other hand, should *not* be cached this way, since it's the entry point that references the latest hashed filenames:

```
Cache-Control: no-cache
```

`no-cache` doesn't mean "don't cache." It means "always revalidate before using." That way users get fresh HTML, which points to bundles that are probably already cached.

### Splitting vendor code

Your dependencies change far less often than your application code. Splitting them into a separate chunk means a deploy that only touches your own code doesn't bust the cache for React, lodash, and friends:

```javascript
optimization: {
  splitChunks: {
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendors',
        chunks: 'all',
      },
    },
  },
  runtimeChunk: 'single',
}
```

The `runtimeChunk: 'single'` setting pulls webpack's runtime manifest into its own small file, which prevents it from invalidating your vendor hash on every build.

## Going Further With Service Workers

HTTP caching is great, but the browser can evict entries whenever it wants. If you need more control, a service worker lets you manage the cache yourself.

With Workbox, you can precache your bundles at install time:

```javascript
import { precacheAndRoute } from 'workbox-precaching';

precacheAndRoute(self.__WB_MANIFEST);
```

Workbox's build plugin injects the list of hashed assets into `__WB_MANIFEST`. When the service worker installs, it downloads everything in the background. On future visits, bundles are served straight from the cache, even offline.

For lazily loaded chunks you don't want to precache, a runtime caching route works well:

```javascript
import { registerRoute } from 'workbox-routing';
import { CacheFirst } from 'workbox-strategies';

registerRoute(
  ({ request }) => request.destination === 'script',
  new CacheFirst({ cacheName: 'js-chunks' })
);
```

Because the filenames are content-hashed, cache-first is safe here. A new version of a chunk will always have a new URL.

## Measuring the Impact

Don't take any of this on faith. Open Chrome DevTools, go to the Network tab, and throttle to "Fast 3G." Then:

1. Load the page and watch for low-priority requests marked as prefetch.
2. Navigate to a prefetched route and confirm the chunk shows `(prefetch cache)` or `(disk cache)` in the Size column.
3. Compare navigation time with and without prefetching.

Lighthouse and WebPageTest can also help you see the before-and-after difference on real-world metrics.

## Wrapping Up

Code splitting shrinks your initial load, but on its own it just moves the waiting around. Prefetching fills that gap by quietly loading what users are likely to need next, and a solid caching strategy makes sure that work isn't thrown away.

To recap:

- Use `preload` for critical resources on the current page, and `prefetch` for likely future navigations.
- Prefetch based on intent, like hover or visibility, rather than prefetching everything.
- Respect `saveData` and slow connections.
- Hash your filenames and cache static assets with `immutable`.
- Split vendor code and the runtime chunk to keep caches stable across deploys.
- Reach for a service worker when you need more control.

Put these together and your app will feel instant, even when it's shipping a lot of JavaScript. Happy optimizing!

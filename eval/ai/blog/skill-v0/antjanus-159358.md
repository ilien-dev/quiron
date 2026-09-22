# Using prefetch and caching for better JavaScript bundle loading

Modern web apps ship a lot of JavaScript. Even with code splitting, users often wait for chunks to download the moment they click a link or open a modal. Browsers give us a set of tools to get ahead of that wait: resource hints like `prefetch` and `preload`, plus HTTP caching and service workers. Used together, they can make your app feel a lot faster, and you don't have to change any of your app's business logic to get there.

In this post I'll cover how prefetching works, how I combine it with caching, and some patterns you can drop into a webpack, Vite, or plain HTML setup today.

## Code splitting moves the wait

Code splitting is one of the best things you can do for initial load performance. Instead of shipping one giant `bundle.js`, you split your app into route-level or component-level chunks:

```javascript
const Settings = React.lazy(() => import('./pages/Settings'));
```

Now the Settings page only loads when the user navigates there. Your initial bundle is smaller, and your Time to Interactive improves.

But there's a catch. When the user *does* click "Settings," the browser has to go fetch that chunk over the network. On a slow connection, that could mean a spinner for a second or two. We traded a slower first load for slower navigation.

What I want is to load those chunks *before* the user needs them, at a time when the browser isn't busy with anything more important. That's what prefetching is for.

## Prefetch vs. preload

People mix these two hints up a lot, so I'll explain both.

**`preload`** tells the browser: "You will need this resource for the current page, and soon. Fetch it with high priority."

```html
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
```

**`prefetch`** tells the browser: "The user will *probably* need this resource for a future navigation. Fetch it at low priority when you're idle."

```html
<link rel="prefetch" href="/static/js/settings.chunk.js">
```

The differences:

| | `preload` | `prefetch` |
|---|---|---|
| Priority | High | Lowest |
| Used for | Current page | Future navigation |
| Timing | Immediately | When the browser is idle |
| Wasted if unused? | Yes, and the browser warns you | Yes, but cheaply |

The rule of thumb I use: preload what you *know* you need right now, prefetch what you *think* you'll need next.

## Prefetching with webpack magic comments

If you're using webpack, you get it almost for free, with a comment inside the import:

```javascript
const Settings = React.lazy(() =>
  import(/* webpackPrefetch: true */ './pages/Settings')
);
```

When the parent chunk loads, a `<link rel="prefetch">` tag for the Settings chunk is added to the document head by webpack. The browser will then fetch it during idle time. When the user gets to Settings, the chunk is already sitting in the cache.

There's also `webpackPreload: true`, which is useful for chunks that the current route needs in parallel with the parent, but use it sparingly. Preloading too much competes with your critical resources and can make things slower.

## Prefetching in Vite

Vite handles preloading of direct dynamic import dependencies automatically with its `modulepreload` polyfill. For prefetching routes the user might visit later, you can add the hints yourself:

```javascript
function prefetch(url) {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = url;
  document.head.appendChild(link);
}
```

Or you can just call the dynamic import early. Calling `import()` returns a promise and caches the module, so calling it again later resolves right away:

```javascript
const loadSettings = () => import('./pages/Settings');

// Warm it up
loadSettings();
```

## Prefetch on intent

Prefetching everything up front wastes bandwidth, especially on mobile. I'd rather prefetch the chunk the user is about to need, and there are two good signals for that: the user hovers over a link, or the link scrolls into view.

### Prefetch on hover

When a user hovers over a link, there's usually 200 to 400ms before they click the link. That's often enough time to download a small chunk.

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

I put the same handler on `onFocus`, because keyboard users should get fast navigation too.

### Prefetch on visibility

For links further down the page, you can use `IntersectionObserver` to prefetch a link's chunk when the link scrolls into view. Libraries like Quicklink do this, and Next.js does this with its `<Link>` component in production.

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

Before I prefetch anything, I check whether the user has asked to save data or is on a slow connection:

```javascript
function shouldPrefetch() {
  const conn = navigator.connection;
  if (!conn) return true;
  if (conn.saveData) return false;
  return !/2g/.test(conn.effectiveType);
}
```

It's a small check, but it makes a big difference for users on metered plans.

## Caching: making prefetched bundles stick

Prefetching only helps if the prefetched file is still in the cache when it's needed. So the cache matters as much as the prefetch.

### Content hashing

Start by putting a content hash in every filename:

```javascript
// webpack.config.js
output: {
  filename: '[name].[contenthash].js',
  chunkFilename: '[name].[contenthash].chunk.js',
}
```

Now each file's name changes only when its contents change. That means you can cache these files forever.

### Long-lived Cache-Control headers

With hashed filenames, set aggressive caching headers on your static files:

```
Cache-Control: public, max-age=31536000, immutable
```

The `immutable` directive tells the browser not to bother revalidating the file, even on a reload. Your HTML should *not* be cached this way, since it's the entry point that references the latest hashed filenames:

```
Cache-Control: no-cache
```

`no-cache` doesn't mean "don't cache." It means "always revalidate before using." That way users always get fresh HTML, and the fresh HTML points to bundles that are probably already cached.

### Splitting vendor code

Dependencies usually change far less often than the app code, at least in the apps I've worked on. If you split them into a separate chunk, a deploy that only touches your code doesn't bust the cache for React, lodash and the rest:

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

The `runtimeChunk: 'single'` setting pulls webpack's runtime manifest into its own small file, so it doesn't change your vendor hash on every build.

## Going further with service workers

HTTP caching is great, but the browser can evict files from the cache whenever it wants. If you need more control, a service worker lets you manage the cache yourself.

With Workbox, you can precache your bundles at install time:

```javascript
import { precacheAndRoute } from 'workbox-precaching';

precacheAndRoute(self.__WB_MANIFEST);
```

The list of hashed files is injected into `__WB_MANIFEST` by Workbox's build plugin. When the service worker installs, the service worker downloads all of those files in the background. On later visits, bundles are served straight from the cache, even offline.

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

## Measuring it

Don't take any of this on faith. I open Chrome DevTools, go to the Network tab, and throttle to "Fast 3G." Then:

1. Load the page and watch for low-priority requests marked as prefetch.
2. Navigate to a prefetched route and check that the chunk shows `(prefetch cache)` or `(disk cache)` in the Size column.
3. Compare navigation time with and without prefetching.

Lighthouse and WebPageTest can also show you the before and after on real-world metrics.

## Summing up

Code splitting makes your initial load smaller, but on its own it just moves the wait around. Prefetching loads the chunks the user will probably need next, and caching makes sure those chunks are still there when the user needs them.

- Use `preload` for critical resources on the current page, and `prefetch` for likely future navigations.
- Prefetch on hover or when a link scrolls into view, instead of prefetching everything.
- Respect `saveData` and slow connections.
- Hash your filenames and cache static assets with `immutable`.
- Split vendor code and the runtime chunk to keep caches stable across deploys.
- Use a service worker when you need more control.

Put all of this together and your app will feel fast even when your app ships a lot of JavaScript.

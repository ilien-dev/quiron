# apropos

A simple way to serve up appropriate images for every visitor.

Every visitor arrives with a different screen, connection, and browser. A phone on a weak mobile signal doesn't need the same 4000-pixel hero photo as a desktop on fiber. apropos picks the right image for each request, so you don't have to pick one compromise size for everyone.

## Why apropos?

Most sites ship one of two things: an image that is too large for most visitors, or one that is too small for the rest. Fixing this by hand means exporting many variants, writing `srcset` markup, and keeping it all in sync. apropos automates that work:

- **Right size**: images are matched to the visitor's viewport and pixel density.
- **Right format**: modern formats such as AVIF and WebP are served to browsers that support them, with a safe fallback for the rest.
- **Right weight**: quality adapts to connection hints like `Save-Data` and `Downlink` when the browser provides them.
- **Right now**: variants are generated on first request and cached, so you never pre-build a matrix of files.

## Installation

```sh
npm install apropos
```

apropos requires Node.js 18 or newer.

## Quick start

Point apropos at a directory of original images and mount it in your server:

```js
import express from "express";
import { apropos } from "apropos";

const app = express();

app.use(
  "/img",
  apropos({
    source: "./originals",
    cache: "./.apropos-cache",
  })
);

app.listen(3000);
```

Now request an image and let apropos decide the details:

```html
<img src="/img/hero.jpg" alt="A mountain at sunrise" />
```

The server inspects the request headers (`Accept`, `Viewport-Width`, `DPR`, `Save-Data`) and responds with the best variant it can produce.

### Explicit sizes

If you'd rather be explicit, use query parameters:

```html
<img src="/img/hero.jpg?w=800&fit=cover&ratio=16:9" alt="A mountain at sunrise" />
```

Or generate a full responsive set with the helper:

```js
import { srcset } from "apropos/html";

srcset("/img/hero.jpg", { widths: [480, 800, 1200, 1600] });
// => "/img/hero.jpg?w=480 480w, /img/hero.jpg?w=800 800w, ..."
```

## How it works

1. A request arrives for an original image.
2. apropos reads the client hints and `Accept` header, then merges them with any explicit query parameters. Explicit parameters always win.
3. It rounds the target width to the nearest configured breakpoint, which keeps the number of cached variants small.
4. If a matching variant exists in the cache, it is served immediately. Otherwise it is generated, stored, and served.
5. Responses include `Vary` and long-lived `Cache-Control` headers so CDNs and browsers cache each variant correctly.

## Configuration

| Option        | Default                        | Description                                         |
| ------------- | ------------------------------ | --------------------------------------------------- |
| `source`      | required                       | Directory containing original images.               |
| `cache`       | `./.apropos-cache`             | Where generated variants are stored.                |
| `breakpoints` | `[320, 640, 960, 1280, 1920]`  | Widths apropos may round to.                        |
| `formats`     | `["avif", "webp", "jpeg"]`     | Output formats, in order of preference.             |
| `quality`     | `{ default: 80, saveData: 55 }`| Quality settings per scenario.                      |
| `maxWidth`    | `2560`                         | Upper limit, to prevent oversized output requests.  |
| `maxAge`      | `31536000`                     | Seconds used in the `Cache-Control` header.         |

## Using a CDN

apropos works well behind a CDN. Because responses depend on request headers, make sure your CDN respects the `Vary` header, or include `Accept` and the width hint in the cache key. If your CDN can't do this, prefer explicit query parameters, which produce distinct URLs for each variant.

## Security notes

- Only files inside `source` are ever read. Path traversal attempts are rejected.
- Requested dimensions are clamped to `maxWidth` so a single URL can't trigger an enormous resize.
- Input is decoded with a strict pixel limit to guard against decompression bombs.

## Command line

You can also warm the cache ahead of time, which is useful for deploys:

```sh
npx apropos warm ./originals --widths 640,1280 --formats avif,webp
```

Use `npx apropos clean` to remove cached variants that no longer have a matching original.

## Roadmap

- Art direction support (different crops per breakpoint)
- Remote origins such as S3-compatible storage
- Blur-up placeholders
- Framework adapters for Fastify, Hono, and Next.js

## Contributing

Bug reports and pull requests are welcome. Before opening a PR:

1. Open an issue describing the change, unless it's a small fix.
2. Run `npm test` and `npm run lint`.
3. Add tests for new behavior.

## License

MIT

---

That comes to roughly 740 words. I invented the API, options, and defaults since none were provided, so adjust them to match the actual implementation. I haven't saved this to a file, so tell me if you'd like it written to `README.md`.

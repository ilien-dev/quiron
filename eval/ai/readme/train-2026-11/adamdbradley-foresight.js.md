# foresight.js

> **Deprecated:** Foresight.js was developed before widespread support for the HTML `<picture>` element and responsive image attributes. For new projects, use native browser features such as `<picture>`, `srcset`, and `sizes`.

Foresight.js gave webpages the ability to determine whether a user’s device could benefit from high-resolution images before requesting those images from the server. It also assessed whether the current network connection was fast enough to justify downloading larger image files.

By considering both display capabilities and network connectivity, Foresight.js helped webpages request an appropriate image rather than delivering the same asset to every visitor.

## Why it existed

High-resolution displays can make standard images look soft or blurry. Serving larger images improves clarity, but those files also consume more bandwidth and can increase loading times, particularly on slower connections.

Foresight.js addressed this tradeoff by helping sites choose image resources according to the conditions under which a page was being viewed. Its goal was to provide sharper images where they were useful while avoiding unnecessary downloads where the additional detail offered little benefit.

This approach was especially valuable when responsive image selection was difficult to express directly in HTML.

## How it worked

Foresight.js considered two primary factors:

- **Display capability:** Whether the device’s display could take advantage of a higher-resolution image.
- **Network conditions:** Whether the connection appeared fast enough to retrieve a larger image efficiently.

Together, these signals informed which image resource the webpage should request. A capable display with sufficient connectivity could receive a high-resolution asset, while other conditions could favor a smaller alternative.

The decision happened before the selected image was requested, helping avoid downloading a standard image only to replace it immediately with a larger version.

Network estimates are inherently imperfect. Connection quality can change, and an estimate cannot guarantee the speed of every subsequent request.

## Project status

This project is deprecated and should be treated as a historical solution to responsive image delivery.

Modern browsers provide built-in mechanisms for describing alternative image sources and allowing the browser to select among them. These mechanisms integrate image selection into the browser’s loading behavior and generally provide a better foundation for new development.

Deprecation does not automatically mean that every existing integration has stopped working. However, continued use should be evaluated against the needs, browser support requirements, and maintenance expectations of the application.

## Migrating to native responsive images

For images that share the same content at different resolutions or dimensions, provide alternatives with `srcset`. Use `sizes` when the displayed width depends on the page layout.

Use the `<picture>` element when you need different image compositions or alternative formats.

```html
<img
  src="photo-640.jpg"
  srcset="photo-640.jpg 640w, photo-1280.jpg 1280w"
  sizes="(max-width: 640px) 100vw, 640px"
  alt="A descriptive explanation of the image"
>
```

These features let browsers choose an appropriate resource using information available to them. They do not reproduce every historical network-selection rule implemented by a JavaScript library.

When migrating an existing site, review image dimensions, compression, layout behavior, and fallback resources. Test representative devices and connection conditions to confirm that image quality and download costs remain appropriate.

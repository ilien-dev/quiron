# Quirón brand assets

All production variants derive from `source/quiron-master.png`. The centaur,
eight-point star, and wordmark are one identity; variants change only layout,
color theme, background, and output size.

## Which file to use

| Need | Light UI | Dark UI |
| --- | --- | --- |
| README hero | `hero/quiron-hero-light.png` | `hero/quiron-hero-dark.png` |
| Transparent horizontal logo | `logo/quiron-lockup-light.png` | `logo/quiron-lockup-dark.png` |
| Horizontal logo with background | `logo/quiron-lockup-on-light.png` | `logo/quiron-lockup-on-dark.png` |
| Transparent symbol | `symbol/quiron-symbol-light.png` | `symbol/quiron-symbol-dark.png` |
| Transparent name | `wordmark/quiron-wordmark-light.png` | `wordmark/quiron-wordmark-dark.png` |
| Square icon | `icon/quiron-icon-light-512.png` | `icon/quiron-icon-dark-512.png` |
| 192 px app icon | `icon/quiron-icon-light-192.png` | `icon/quiron-icon-dark-192.png` |
| Apple touch icon | `icon/apple-touch-icon-light.png` | `icon/apple-touch-icon-dark.png` |
| Browser favicon | `favicon/quiron-favicon-light.ico` | `favicon/quiron-favicon-dark.ico` |
| GitHub social preview (Settings → General) | `social/quiron-social-light.png` | `social/quiron-social-dark.png` |

PNG favicons are also available at 16, 32, 48, and 64 px.

## Palette

- Charcoal: `#20201E`
- Warm ivory: `#F7EEDB`
- Light background: `#FDF8EE`
- Dark background: `#181817`
- Terracotta: inherited directly from the approved master

The `light` suffix means dark ink intended for a light surface. The `dark`
suffix means ivory ink intended for a dark surface.

## Rebuild

ImageMagick is required. From the repository root:

```sh
scripts/build-brand-assets.sh
```

Do not edit individual output files. Update the approved master or the build
script, then rebuild the complete set so all variants remain consistent.

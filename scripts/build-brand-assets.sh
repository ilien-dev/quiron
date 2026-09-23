#!/usr/bin/env bash

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
brand_dir="$project_dir/assets/brand"
source_image="$brand_dir/source/quiron-master.png"

light_bg="#FDF8EE"
dark_bg="#181817"
dark_ink="#20201E"
light_ink="#F7EEDB"

if ! command -v magick >/dev/null 2>&1; then
  echo "ImageMagick (magick) is required." >&2
  exit 1
fi

if [[ ! -f "$source_image" ]]; then
  echo "Missing brand master: $source_image" >&2
  exit 1
fi

mkdir -p \
  "$brand_dir/hero" \
  "$brand_dir/logo" \
  "$brand_dir/symbol" \
  "$brand_dir/wordmark" \
  "$brand_dir/icon" \
  "$brand_dir/favicon"

# Extract the two approved components from the selected concept. The crop boxes
# intentionally exclude the small duplicate preview included in the concept sheet.
magick "$source_image" \
  -crop 730x660+180+95 +repage \
  -alpha off -fuzz 8% -transparent "#FDFBED" \
  -trim +repage \
  "$brand_dir/symbol/quiron-symbol-light.png"

magick "$source_image" \
  -crop 705x220+215+745 +repage \
  -alpha off -fuzz 8% -transparent "#FDFBED" \
  -trim +repage \
  "$brand_dir/wordmark/quiron-wordmark-light.png"

# Dark-theme masters keep the star unchanged while changing only charcoal ink.
magick "$brand_dir/symbol/quiron-symbol-light.png" \
  -fuzz 18% -fill "$light_ink" -opaque "$dark_ink" \
  "$brand_dir/symbol/quiron-symbol-dark.png"

magick "$brand_dir/wordmark/quiron-wordmark-light.png" \
  -fuzz 18% -fill "$light_ink" -opaque "$dark_ink" \
  "$brand_dir/wordmark/quiron-wordmark-dark.png"

# Transparent horizontal lockups. Symbol and name remain separate, with a fixed
# clear-space gap between them.
magick -size 1400x520 xc:none \
  \( "$brand_dir/symbol/quiron-symbol-light.png" -resize '520x440>' \) \
  -gravity west -geometry +40+0 -composite \
  \( "$brand_dir/wordmark/quiron-wordmark-light.png" -resize '720x220>' \) \
  -gravity east -geometry +40+0 -composite \
  "$brand_dir/logo/quiron-lockup-light.png"

magick -size 1400x520 xc:none \
  \( "$brand_dir/symbol/quiron-symbol-dark.png" -resize '520x440>' \) \
  -gravity west -geometry +40+0 -composite \
  \( "$brand_dir/wordmark/quiron-wordmark-dark.png" -resize '720x220>' \) \
  -gravity east -geometry +40+0 -composite \
  "$brand_dir/logo/quiron-lockup-dark.png"

# Logo cards with an explicit background.
magick -size 1400x520 "xc:$light_bg" \
  "$brand_dir/logo/quiron-lockup-light.png" -composite \
  "$brand_dir/logo/quiron-lockup-on-light.png"

magick -size 1400x520 "xc:$dark_bg" \
  "$brand_dir/logo/quiron-lockup-dark.png" -composite \
  "$brand_dir/logo/quiron-lockup-on-dark.png"

# Wide README heroes.
magick -size 1600x640 "xc:$light_bg" \
  \( "$brand_dir/symbol/quiron-symbol-light.png" -resize '560x500>' \) \
  -gravity west -geometry +100+0 -composite \
  \( "$brand_dir/wordmark/quiron-wordmark-light.png" -resize '760x235>' \) \
  -gravity east -geometry +100+0 -composite \
  "$brand_dir/hero/quiron-hero-light.png"

magick -size 1600x640 "xc:$dark_bg" \
  \( "$brand_dir/symbol/quiron-symbol-dark.png" -resize '560x500>' \) \
  -gravity west -geometry +100+0 -composite \
  \( "$brand_dir/wordmark/quiron-wordmark-dark.png" -resize '760x235>' \) \
  -gravity east -geometry +100+0 -composite \
  "$brand_dir/hero/quiron-hero-dark.png"

# Square icons on explicit light and dark backgrounds.
magick -size 512x512 "xc:$light_bg" \
  \( "$brand_dir/symbol/quiron-symbol-light.png" -resize '424x424>' \) \
  -gravity center -composite \
  "$brand_dir/icon/quiron-icon-light-512.png"

magick -size 512x512 "xc:$dark_bg" \
  \( "$brand_dir/symbol/quiron-symbol-dark.png" -resize '424x424>' \) \
  -gravity center -composite \
  "$brand_dir/icon/quiron-icon-dark-512.png"

magick "$brand_dir/icon/quiron-icon-light-512.png" -resize 192x192 \
  "$brand_dir/icon/quiron-icon-light-192.png"
magick "$brand_dir/icon/quiron-icon-dark-512.png" -resize 192x192 \
  "$brand_dir/icon/quiron-icon-dark-192.png"
magick "$brand_dir/icon/quiron-icon-light-512.png" -resize 180x180 \
  "$brand_dir/icon/apple-touch-icon-light.png"
magick "$brand_dir/icon/quiron-icon-dark-512.png" -resize 180x180 \
  "$brand_dir/icon/apple-touch-icon-dark.png"

# PNG and multi-resolution ICO favicons.
for favicon_size in 16 32 48 64; do
  magick "$brand_dir/icon/quiron-icon-light-512.png" -resize "${favicon_size}x${favicon_size}" \
    "$brand_dir/favicon/quiron-favicon-light-${favicon_size}.png"
  magick "$brand_dir/icon/quiron-icon-dark-512.png" -resize "${favicon_size}x${favicon_size}" \
    "$brand_dir/favicon/quiron-favicon-dark-${favicon_size}.png"
done

magick "$brand_dir/icon/quiron-icon-light-512.png" \
  -define icon:auto-resize=64,48,32,16 \
  "$brand_dir/favicon/quiron-favicon-light.ico"
magick "$brand_dir/icon/quiron-icon-dark-512.png" \
  -define icon:auto-resize=64,48,32,16 \
  "$brand_dir/favicon/quiron-favicon-dark.ico"

# Social preview cards (GitHub and Open Graph want 1280x640): the hero, scaled, with
# the tagline under the wordmark.
mkdir -p "$brand_dir/social"
tagline_font="$project_dir/assets/demo/fonts/Alegreya.ttf"
for theme in light dark; do
  if [[ $theme == light ]]; then bg=$light_bg; quiet="#6B665C"; else bg=$dark_bg; quiet="#A8A08F"; fi
  magick "$brand_dir/hero/quiron-hero-$theme.png" -depth 8 -resize 1280x512 \
    -background "$bg" -gravity center -extent 1280x640 \
    -gravity NorthWest -font "$tagline_font" -pointsize 34 -fill "$quiet" \
    -annotate +662+420 'An AI humanizer skill that' -annotate +662+462 'measures its own work' \
    -strip "$brand_dir/social/quiron-social-$theme.png"
done

# Copies for the GitHub Pages site in docs/.
site_dir="$project_dir/docs"
mkdir -p "$site_dir/img"
for theme in light dark; do
  magick "$brand_dir/hero/quiron-hero-$theme.png" -depth 8 -resize 1200x -strip -quality 82 \
    "$site_dir/img/hero-$theme.webp"
done
cp "$brand_dir/social/quiron-social-light.png" "$site_dir/img/og.png"
cp "$brand_dir/favicon/quiron-favicon-light-32.png" "$site_dir/img/favicon-32.png"
cp "$brand_dir/favicon/quiron-favicon-light.ico" "$site_dir/favicon.ico"
cp "$brand_dir/icon/apple-touch-icon-light.png" "$site_dir/img/apple-touch-icon.png"

echo "Brand assets rebuilt in $brand_dir and $site_dir"

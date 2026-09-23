#!/usr/bin/env bash
# Renders assets/demo/demo.html frame by frame with headless Chromium and joins the frames
# into assets/demo/quiron-demo-light.gif and quiron-demo-dark.gif with ffmpeg.
# Needs chromium (or CHROME=/path/to/chrome) and ffmpeg. Edit demo.html, not the GIFs.

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
demo="$project_dir/assets/demo"
chrome="${CHROME:-$(command -v chromium || command -v google-chrome || true)}"
fps=12          # smooth enough for a README; each GIF comes out near 250 KB
seconds=15      # demo.html's timeline ends at 10.5 s; the rest holds the final state
jobs="${JOBS:-8}"

for tool in "$chrome" ffmpeg; do
  if [[ -z "$tool" ]] || ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing ${tool:-chromium}: install Chromium and ffmpeg, or set CHROME." >&2
    exit 1
  fi
done

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
frames=$((fps * seconds))

for theme in light dark; do
  mkdir -p "$work/$theme"
  seq 0 $((frames - 1)) | xargs -P "$jobs" -I{} bash -c '
    t=$(awk "BEGIN { printf \"%.3f\", {} / $1 }")
    "$2" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --virtual-time-budget=3000 \
      --window-size=960,560 --user-data-dir="$3/profile-{}" \
      --screenshot="$3/$4/$(printf %04d {}).png" \
      "file://$5/demo.html?t=$t&theme=$4" >/dev/null 2>&1
    rm -rf "$3/profile-{}"
  ' _ "$fps" "$chrome" "$work" "$theme" "$demo"

  ffmpeg -loglevel error -y -framerate "$fps" -i "$work/$theme/%04d.png" \
    -vf "split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
    -loop 0 "$demo/quiron-demo-$theme.gif"
  echo "wrote $demo/quiron-demo-$theme.gif ($(du -h "$demo/quiron-demo-$theme.gif" | cut -f1))"
done

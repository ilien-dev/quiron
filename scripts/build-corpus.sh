#!/usr/bin/env bash
# Rebuild the human calibration corpus, then recalibrate the bands.
#
# The shipped bands.json came from dev.to posts published before 2022, so every
# text predates ChatGPT and is human by date. Texts are not redistributed with
# the skill; this script fetches them so the calibration is reproducible.
#
# Usage: build-corpus.sh [OUTDIR] [author ...]
set -euo pipefail
OUT="${1:-$HOME/.cache/im-human/corpus}"; shift || true
AUTHORS=("$@"); [ ${#AUTHORS[@]} -eq 0 ] && AUTHORS=(ben alvaromontoro lissy93 rachelsoderberg)
mkdir -p "$OUT"
for a in "${AUTHORS[@]}"; do
  curl -sS --max-time 20 "https://dev.to/api/articles?username=$a&per_page=100" \
  | python3 -c '
import json,sys
for art in json.load(sys.stdin):
    if art["published_at"] < "2022-01-01":
        print(art["id"])
' | while read -r id; do
    [ -f "$OUT/$id.md" ] && continue
    curl -sS --max-time 20 "https://dev.to/api/articles/$id" | python3 -c "
import json,sys,os
d=json.load(sys.stdin); b=d.get('body_markdown','')
if len(b.split())>350: open(os.path.join('$OUT', f'{d[\"id\"]}.md'),'w').write(b)
" || true
    sleep 0.3
  done
done
echo "corpus: $(ls "$OUT" | wc -l) texts in $OUT"
python3 "$(dirname "$0")/aimeter.py" --calibrate "$OUT"

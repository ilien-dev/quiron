#!/usr/bin/env bash
# Rebuild the Spanish human corpus from dev.to, then recalibrate bands-es.json.
#
# Posts tagged spanish, espanol or español and published before 2022, so every text
# predates ChatGPT. At most CAP posts per author (default 5), more than 350 words, and
# kept only if Spanish function words outnumber English ones, since the tags also hold
# English posts about learning Spanish. Texts are not redistributed; this script fetches
# them so the calibration is reproducible.
#
# Usage: build-corpus-es.sh [OUTDIR]        CAP=8 NO_CALIBRATE=1 build-corpus-es.sh ...
set -euo pipefail
OUT="${1:-$HOME/.cache/im-human/es}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
python3 - "$OUT" "${CAP:-5}" <<'PY'
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
out, cap = sys.argv[1], int(sys.argv[2])

def get(url):
    for wait in (2, 5, 15, 45, 90):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "im-human-corpus/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                return None
        except (urllib.error.URLError, TimeoutError, ValueError):
            pass
        time.sleep(wait)
    return None

ES = set("el la los las que de y en un una es por para con no se del al lo como pero más".split())
EN = set("the and of to is in that it for with as on this you are be but not".split())

def spanish(text):
    w = re.findall(r"[a-záéíóúñü]+", text.lower())
    return sum(x in ES for x in w) > 2 * sum(x in EN for x in w)

seen = {}
for tag in ("spanish", "espanol", "español"):
    for page in range(1, 200):
        arts = get(f"https://dev.to/api/articles?tag={urllib.parse.quote(tag)}&per_page=100&page={page}")
        if not arts:
            break
        for a in arts:
            if a["published_at"] < "2022-01-01":
                seen.setdefault(a["id"], a["user"]["username"])
        time.sleep(1)
print(f"indexed {len(seen)} pre-2022 posts", file=sys.stderr)

per_author, kept = {}, 0
with open(os.path.join(out, "titles.tsv"), "w") as idx:
    for aid, user in sorted(seen.items()):
        if per_author.get(user, 0) >= cap:
            continue
        d = get(f"https://dev.to/api/articles/{aid}")
        body = (d or {}).get("body_markdown") or ""
        if len(body.split()) > 350 and spanish(body):
            name = f"{user}-{aid}"
            open(os.path.join(out, name + ".md"), "w").write(body)
            idx.write(f"{name}\t{len(body.split())}\t{d['title']}\n")
            per_author[user] = per_author.get(user, 0) + 1
            kept += 1
        time.sleep(1)
print(f"spanish corpus: {kept} posts by {len(per_author)} authors in {out}", file=sys.stderr)
PY
[ -n "${NO_CALIBRATE:-}" ] || python3 "$HERE/aimeter.py" --calibrate "$OUT" \
  --ai "$HERE/../eval/ai/es/train" --out "$HERE/bands-es.json"

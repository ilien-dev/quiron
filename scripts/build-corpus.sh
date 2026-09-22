#!/usr/bin/env bash
# Rebuild the human calibration corpus, then recalibrate the bands.
#
# The shipped bands.json came from dev.to posts published before 2022, so every
# text predates ChatGPT and is human by date. Texts are not redistributed with
# the skill; this script fetches them so the calibration is reproducible.
#
# Each author contributes at most CAP posts (default 8), so a prolific author
# cannot set the band alone. Files are named AUTHOR-ID.md and titles go to
# OUTDIR/titles.tsv, which evaluate.py and the AI-text generation use.
#
# Usage: build-corpus.sh [OUTDIR] [author ...]
#        CAP=12 NO_CALIBRATE=1 build-corpus.sh ...
set -euo pipefail
OUT="${1:-$HOME/.cache/quiron/corpus}"; shift || true
AUTHORS=("$@")
[ ${#AUTHORS[@]} -eq 0 ] && AUTHORS=(aspittel emmabostian laurieontech rachelsoderberg
  swyx dabit3 heymichellemac tracycss kentcdodds ben jess nickytonline alvaromontoro
  codemouse92 cassidoo sylwiavargas bholmesdev chrisachard isaacdlyman jacobherrington
  helenanders26 antjanus deciduously rhymes)
mkdir -p "$OUT"
python3 - "$OUT" "${CAP:-8}" "${AUTHORS[@]}" <<'PY'
import json, os, sys, time, urllib.request, urllib.error
out, cap, authors = sys.argv[1], int(sys.argv[2]), sys.argv[3:]

def get(url):
    for wait in (1, 3, 9, 27):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "quiron-corpus/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                return None
        except (urllib.error.URLError, TimeoutError, ValueError):
            pass
        time.sleep(wait)
    return None

index = os.path.join(out, "titles.tsv")
seen = {l.split("\t")[0] for l in open(index)} if os.path.exists(index) else set()
with open(index, "a") as idx:
    for a in authors:
        have = sum(1 for n in os.listdir(out) if n.startswith(a + "-"))
        page = 1
        while have < cap:
            arts = get(f"https://dev.to/api/articles?username={a}&per_page=100&page={page}")
            if not arts:
                break
            for art in arts:
                if have >= cap:
                    break
                if art["published_at"] >= "2022-01-01" or f"{a}-{art['id']}" in seen:
                    continue
                d = get(f"https://dev.to/api/articles/{art['id']}")
                body = (d or {}).get("body_markdown") or ""
                if len(body.split()) > 350:
                    name = f"{a}-{art['id']}"
                    open(os.path.join(out, name + ".md"), "w").write(body)
                    idx.write(f"{name}\t{len(body.split())}\t{art['title']}\n")
                    seen.add(name)
                    have += 1
                time.sleep(0.4)
            page += 1
        print(f"{a}: {have}", file=sys.stderr)
PY
echo "corpus: $(ls "$OUT"/*.md | wc -l) texts in $OUT"
[ -n "${NO_CALIBRATE:-}" ] || python3 "$(dirname "$0")/aimeter.py" --calibrate "$OUT" \
  --ai "$(dirname "$0")/../eval/ai/blog/train"

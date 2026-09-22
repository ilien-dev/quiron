#!/usr/bin/env bash
# Rebuild the human fiction corpus, then recalibrate bands-fiction.json.
#
# Stories come from WritingPrompts (Fan, Lewis & Dauphin 2018, r/WritingPrompts), so
# every text predates ChatGPT. Four fixed pages of the train split, stories of 500 to
# 1,500 words, detokenized back to ordinary punctuation. Texts are not redistributed;
# this script fetches them so the calibration is reproducible.
#
# Usage: build-corpus-fiction.sh [OUTDIR]        NO_CALIBRATE=1 to skip calibration
set -euo pipefail
OUT="${1:-$HOME/.cache/quiron/fiction}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
python3 - "$OUT" <<'PY'
import json, os, re, sys, time, urllib.request
out = sys.argv[1]
API = ("https://datasets-server.huggingface.co/rows?dataset=euclaise/writingprompts"
       "&config=default&split=train&offset={}&length=100")

def detok(s):
    s = s.replace("<newline>", "\n")
    s = re.sub(r" ?\n ?", "\n", s).replace("``", '"').replace("''", '"')
    s = re.sub(r" (n't|'s|'re|'ve|'ll|'d|'m)\b", r"\1", s)
    s = re.sub(r"\b(ca|wo|do|does|did|is|are|was|were|could|should|would|have|has|had|"
               r"must|need|ai) n't", r"\1n't", s)
    s = s.replace("wan na", "wanna").replace("gon na", "gonna")
    s = re.sub(r" ([,.!?;:])", r"\1", s)
    s = re.sub(r"\( ", "(", s)
    s = re.sub(r" \)", ")", s)
    return re.sub(r'" ([^"]*?) "', r'"\1"', s).strip()

n = 0
with open(os.path.join(out, "prompts.tsv"), "w") as idx:
    for offset in (5000, 20000, 40000, 80000):
        req = urllib.request.Request(API.format(offset), headers={"User-Agent": "quiron-corpus/1.0"})
        for wait in (1, 3, 9, 27):
            try:
                rows = json.load(urllib.request.urlopen(req, timeout=30))["rows"]
                break
            except Exception:
                time.sleep(wait)
        else:
            sys.exit(f"could not fetch offset {offset}")
        for r in rows:
            story, prompt = r["row"]["story"], r["row"]["prompt"]
            if not prompt.startswith("[ WP ]"):
                continue
            story = detok(story)
            words = len(story.split())
            if 500 <= words <= 1500:
                name = f"wp-{r['row_idx']}"
                open(os.path.join(out, name + ".md"), "w").write(story + "\n")
                idx.write(f"{name}\t{words}\t{detok(prompt[6:]).strip()}\n")
                n += 1
print(f"fiction corpus: {n} stories in {out}", file=sys.stderr)
PY
[ -n "${NO_CALIBRATE:-}" ] || python3 "$HERE/aimeter.py" --calibrate "$OUT" \
  --ai "$HERE/../eval/ai/fiction/train" --out "$HERE/bands-fiction.json" --lexicon ai-lean-fiction.txt

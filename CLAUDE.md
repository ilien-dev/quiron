## What this is

A skill that makes any AI model's prose read like a person wrote it, checked against measured human baselines. `SKILL.md` is the skill, loaded as instructions; `scripts/` is the measuring apparatus. `~/.claude/skills/quiron` symlinks to this checkout, so every edit is live.

## The rule for every change

A change to the skill ships only if it is measured and the measurement shows an improvement. Opinion, intuition and "this reads better" do not count.

- Every pattern, lexicon word, band and number traces to research with a published corpus or to a run of the scripts. New claims get a source in `references/sources.md`. No source, no change.
- Measure before and after on the same texts. Report both numbers.
- An improvement moves assistant-register text toward the band and keeps known-human text inside it. A change that starts flagging human texts is a regression, even if it catches more AI text.
- Overshoot is a failure, not a win (TextPulse finding, top of `SKILL.md`). Prefer `overshot` getting rarer over a higher score.
- A number in `SKILL.md` or `references/` the scripts can reproduce is rerun when the code or bands change. A figure with no measurement behind it is removed.

## User-facing Markdown goes through /quiron

Any Markdown a person reads, new or edited (`README.md`, `assets/brand/README.md`, `eval/README.md`, any new one), is written with the `/quiron` skill and run through `scripts/check.sh` before commit. Not `SKILL.md` or `CLAUDE.md` (model instructions), and never `eval/ai/` (measurement data).

## Commands

Python 3 standard library only, no build.

```sh
python3 scripts/aimeter.py [--json] FILE     # 23 rates vs bands.json
python3 scripts/audit.py [--brief|--json] FILE   # checklist; exit code = number of FAILs
scripts/check.sh FILE [--ruled "note"|--status|--reset]   # one loop iteration
python3 scripts/aimeter.py --calibrate DIR   # rebuild bands.json from human texts
scripts/build-corpus.sh [OUTDIR] [author ...] # fetch pre-2022 dev.to corpus, then calibrate
python3 scripts/evaluate.py --human DIR [--ai-train DIR] NAME=DIR ...  # score the skill
python3 scripts/factdiff.py SOURCE REWRITE   # facts in the rewrite, not in the source
QUIRON_BANDS=scripts/bands-fiction.json ...  # other registers: fiction, es
```

Texts under ~120 words or 8 sentences return no measurement.

## Architecture

- `aimeter.py`: `prose()` strips markdown, `measure()` computes features, each scored against the p10–p90 band. `AI_REF` holds each feature's AI direction and median; it decides `AI side` vs `overshot`. Word lists live in `scripts/lexicons/`.
- `audit.py` `CHECKS`: one entry per Part A pattern, states PASS / FAIL / TELL / READ. FAIL only where ≤~5% of held-out human texts trip it (`evaluate.py` shows the rate), or the loop can never converge.
- `check.sh` keeps a streak in `.FILE.quiron.json`. Convergence is two consecutive clean passes with READ items ruled on in both.

`SKILL.md` (index), `references/patterns.md`, `CHECKS` and `AI_REF` describe the same patterns and numbers; change one, update the others. The band table in `references/numbers.md` mirrors `bands.json`. `SKILL.md` stays under 500 lines; detail goes in `references/`, one level deep.

Band files: `bands.json` (blog), `bands-fiction.json`, `bands-es.json`, built by `build-corpus*.sh`; each may carry `_lang`, `_lexicon`, `_plain`, `_thresholds` and learned AI directions. Human corpora are not committed; `eval/ai/` samples are.

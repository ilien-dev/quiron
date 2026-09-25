## What this is

A skill that makes any AI model's prose read like a person wrote it, checked against measured human baselines. `SKILL.md` is the skill; `scripts/` is the measuring apparatus. `~/.claude/skills/quiron` symlinks here, so every edit is live.

## The rule for every change

A change ships only if a measurement shows an improvement. "This reads better" does not count.

- Every pattern, word, band and number traces to a published corpus or a run of the scripts, with new sources in `references/sources.md`. A figure with no measurement behind it is removed; one the scripts can reproduce is rerun when code or bands change.
- Measure before and after on the same texts and report both. An improvement moves AI text toward the band and keeps human text inside it; flagging more human texts is a regression.
- Overshoot is a failure too (top of `SKILL.md`): prefer fewer `overshot` over a higher score.
- Rewrite rules are judged end to end with `eval/e2e/` on `dev`, then confirmed on `test` (`fic2` for fiction). A `dev`-only gain does not ship: two failed on `test`.

## User-facing Markdown goes through /quiron

Any Markdown a person reads (READMEs, `eval/README.md`, new docs) is written with `/quiron` and passes `scripts/check.sh` before commit. Not `SKILL.md`, `CLAUDE.md` or `eval/ai/`.

## Commands

Python 3 standard library only, no build (`eval/e2e/` also needs the claude CLI).

```sh
python3 scripts/aimeter.py [--json] FILE          # 23 rates vs bands.json
python3 scripts/audit.py [--brief|--json] FILE    # checklist; exit code = FAILs
scripts/check.sh FILE [--ruled "note"|--status|--reset]
python3 scripts/evaluate.py --human DIR [--ai-train DIR] NAME=DIR ...
python3 scripts/factdiff.py SOURCE REWRITE
scripts/build-corpus*.sh [OUTDIR]                 # fetch pre-2022 corpus, calibrate
python3 eval/e2e/harness.py rewrite SNAP REP [--set dev|test|es|fic|fic2]
python3 eval/e2e/report.py OLD NEW [--set ...]    # blind judges, paired per title
QUIRON_BANDS=scripts/bands-fiction.json ...       # other registers: fiction, es
```

## Architecture

- `aimeter.py`: each feature scored against the human p10–p90 band; `AI_REF` sets its AI direction, deciding `AI side` vs `overshot`.
- `audit.py` `CHECKS`: one per pattern, PASS / FAIL / TELL / READ. FAIL only where ≤~5% of held-out human texts trip it.
- `check.sh`: converged after two consecutive clean passes with READ items ruled on in both.

`SKILL.md`, `references/patterns.md`, `CHECKS` and `AI_REF` describe the same patterns; change one, update the others. The band table in `references/numbers.md` mirrors `bands.json`. `SKILL.md` stays under 500 lines, detail in `references/`, one level deep. Human corpora are not committed; `eval/ai/` samples are.

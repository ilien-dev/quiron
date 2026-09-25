## What this is

A skill that makes any AI model's prose read like a person wrote it, checked against measured human baselines. This checkout is the skill: the root `SKILL.md` is the instructions, `scripts/` the measuring apparatus. Agents here use them directly, not an installed copy. `AGENTS.md` symlinks to this file.

`main` is protected: work on a `feature/<lowercase-words-with-hyphens>` branch and open a pull request against `main`.

## The rule for every change

A change ships only if a measurement shows an improvement. Opinion and "this reads better" do not count.

- Every pattern, lexicon word, band and number traces to research with a published corpus (source in `references/sources.md`) or to a run of the scripts.
- Measure before and after on the same texts; report both numbers.
- An improvement moves assistant-register text toward the band and keeps known-human text inside it. Flagging human texts is a regression, even if it catches more AI text.
- Overshoot is a failure (TextPulse, top of `SKILL.md`): prefer `overshot` getting rarer over a higher score.
- Rerun any reproducible number in `SKILL.md` or `references/` when code or bands change; remove figures with no measurement behind them.
- Rewrite rules are judged end to end with `eval/e2e/` on `dev`, then confirmed on `test` (`fic2` for fiction). A `dev`-only gain does not ship: two failed on `test`.

## User-facing Markdown

Any Markdown a person reads (READMEs, `CONTRIBUTING.md`, any new one) is written by following the root `SKILL.md`, then run through `scripts/check.sh` before commit. Not model instructions (`SKILL.md`, `CLAUDE.md`), never `eval/ai/` (measurement data).

## Commands

Python 3 standard library only, no build (`eval/e2e/` is the exception). Texts under ~120 words or 8 sentences return no measurement.

```sh
python3 scripts/aimeter.py [--json] FILE     # 23 rates vs bands.json
python3 scripts/audit.py [--brief|--json] FILE   # checklist; exit code = number of FAILs
scripts/check.sh FILE [--ruled "note"|--status|--reset]   # one loop iteration
python3 scripts/aimeter.py --calibrate DIR   # rebuild bands.json from human texts
scripts/build-corpus.sh [OUTDIR] [author ...] # fetch pre-2022 dev.to corpus, then calibrate
python3 scripts/evaluate.py --human DIR [--ai-train DIR] NAME=DIR ...  # score the skill
python3 scripts/factdiff.py SOURCE REWRITE   # facts in the rewrite, not in the source
QUIRON_BANDS=scripts/bands-fiction.json ...  # other registers: fiction, es
python3 eval/e2e/harness.py rewrite SNAP REP [--set dev|test|es|fic|fic2]  # needs the claude CLI
python3 eval/e2e/report.py OLD NEW [--set ...]  # blind judges, paired per title
```

## Architecture

- `aimeter.py`: each feature scored against the p10–p90 band; `AI_REF` holds each feature's AI direction and median and decides `AI side` vs `overshot`.
- `audit.py` `CHECKS`: one entry per pattern, PASS / FAIL / TELL / READ. FAIL only where ≤~5% of held-out human texts trip it (`evaluate.py` shows the rate).
- `check.sh`: convergence is two consecutive clean passes with READ items ruled on in both.

`SKILL.md`, `references/patterns.md`, `CHECKS` and `AI_REF` describe the same patterns and numbers; change one, update the others. `references/numbers.md` mirrors `bands.json`. `SKILL.md` stays under 500 lines; detail goes in `references/`, one level deep. Band files (`bands.json`, `-fiction`, `-es`) come from `build-corpus*.sh`. Human corpora are not committed; `eval/ai/` samples are.

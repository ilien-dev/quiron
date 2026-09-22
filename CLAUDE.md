## What this is

A skill that improves how any AI model writes. It strips the habits that mark prose as machine-written and checks the result against measured human baselines, so the output reads like a person wrote it. `SKILL.md` is the skill itself, loaded as instructions. `scripts/` is the measuring apparatus. `~/.claude/skills/quiron` is a symlink to this checkout, so every edit is live.

## The rule for every change

A change to the skill ships only if it is measured and the measurement shows an improvement. Opinion, intuition and "this reads better" do not count.

- Every pattern, lexicon word, band and number traces to research with a published corpus or to a run of the scripts. New claims get a source in `SKILL.md` § Sources. No source, no change.
- Measure before and after on the same texts. Report both numbers.
- An improvement moves assistant-register text toward the band and keeps known-human text inside it. A change that starts flagging human texts is a regression, even if it catches more AI text.
- Overshoot is a failure, not a win (see the TextPulse finding at the top of `SKILL.md`). Prefer the `overshot` verdict getting rarer over a higher score.
- A number in `SKILL.md` that the scripts can reproduce is rerun when the code or bands change. A figure with no measurement behind it is removed.

## Commands

No build, no dependencies beyond Python 3 standard library.

```sh
python3 scripts/aimeter.py FILE              # 23 rates vs bands.json
python3 scripts/aimeter.py --json FILE
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

- `aimeter.py` strips markdown to prose (`prose()`), computes the features in `measure()`, and scores each against the p10–p90 band in `bands.json`. `AI_REF` holds the direction AI text sits for each feature and the measured AI median; that direction decides whether an out-of-band value is `AI side` or `overshot`. It loads the word lists in `scripts/lexicons/`.
- `audit.py` holds `CHECKS`, one entry per Part A pattern in `SKILL.md`, with states PASS / FAIL / TELL / READ. FAIL only where ≤~5% of held-out human texts trip it (`evaluate.py` shows the rate); otherwise TELL or READ, or the loop can never converge.
- `check.sh` runs both and keeps a streak in a sidecar `.FILE.quiron.json`. Convergence is two consecutive clean passes with READ items ruled on in both.

`SKILL.md`, `audit.py` `CHECKS` and `AI_REF` describe the same patterns and numbers. Changing one means updating the others. The band table in `SKILL.md` Part C mirrors `bands.json`.

Band files: `bands.json` (blog, `build-corpus.sh`), `bands-fiction.json`, `bands-es.json` (`build-corpus-*.sh`). Each may carry `_lang`, `_lexicon`, `_plain`, `_thresholds` and learned AI directions. Human corpora are not committed; the AI samples in `eval/ai/` are.

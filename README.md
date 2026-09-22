# im-human

A Claude Code skill that writes or rewrites prose so it reads as a person wrote it,
then checks the result with measurements instead of impressions.

`SKILL.md` is the skill itself. `scripts/` holds the measuring tools:

- `aimeter.py` scores a text on 21 rates against the calibrated bands in `bands.json`.
- `audit.py` and `check.sh` run the full checklist and the convergence loop.
- `evaluate.py` scores the skill itself: held-out human texts against AI texts and
  AI texts after the skill, with an independent word-frequency judge.
- `build-corpus.sh` builds the human corpus and recalibrates the bands.
- `lexicons/` holds the word lists the meter uses, each entry with its source.

## Install

Link this repository into your skills directory:

```sh
ln -s "$PWD" ~/.claude/skills/im-human
```

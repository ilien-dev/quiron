# im-human

A Claude Code skill that writes or rewrites prose so it reads as a person wrote it,
then checks the result with measurements instead of impressions.

`SKILL.md` is the skill itself. `scripts/` holds the measuring tools:

- `aimeter.py` scores a text against the calibrated bands in `bands.json`.
- `audit.py` and `check.sh` run the full check.
- `build-corpus.sh` builds a corpus to recalibrate the bands for another register.
- `lexicons/` holds the word lists the meter uses.

## Install

Link this repository into your skills directory:

```sh
ln -s "$PWD" ~/.claude/skills/im-human
```

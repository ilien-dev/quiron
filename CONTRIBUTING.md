# Contributing

Quirón is a skill plus the scripts that measure it. I judge a change by what those
scripts show, so read this before you open a pull request.

## Branches and pull requests

Nobody pushes to `main` directly, me included. Every change arrives as a pull
request against `main`.

Name the branch `feature/` and then a few words that say what it does, joined by hyphens:
`feature/spanish-fiction-bands` or `feature/fix-dash-count`. Lowercase letters, digits
and hyphens only, and at least two words after the slash. Any other name fails a check on
the pull request. You can't merge until you rename the branch.

Every pull request also needs my approval, and once I've given it, either of us can merge
it. A push after my approval has to be approved again.

## What a change needs

I merge a change to the skill only when a measurement shows it helps. "This reads better"
isn't enough.

Run the scripts on the same texts before and after your change and put both numbers in
the pull request. It counts as an improvement when assistant text moves toward the human
band and human text stays inside it. If your change starts flagging human texts, that's a
regression, even when it catches more AI text.

Anything new the skill claims needs a source with a published corpus in
`references/sources.md`, or a run of the scripts that shows it.

The scripts use the Python 3 standard library only. Please don't add dependencies.
`CLAUDE.md` lists the commands and explains how the files fit together.

## Markdown people read

If you edit a README or any other Markdown written for people, run it through
`scripts/check.sh` before you commit. `SKILL.md` and `CLAUDE.md` are instructions for the
model, so they don't need it, and neither do the samples in `eval/ai/`.

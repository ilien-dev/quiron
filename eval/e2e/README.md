# End-to-end harness

These scripts produce the September 2026 numbers in `references/numbers.md`: an assistant
rewrites a draft with a copy of the skill, and blind judges who read each rewrite alone
give the probability it was AI-written. Unlike the rest of the repo they need more than
the standard library: the Claude Code CLI for the rewriter and the Claude judges, the
Codex CLI for the GPT judges, and PyTorch with transformers in a separate virtualenv if you
want the local detectors.

Skill snapshots, one folder per rewrite, the judge cache and backups all go to
`$QUIRON_E2E`, by default `~/.cache/quiron-e2e`, and none of it is committed. Rewrites run
inside that folder with permissions bypassed and with only project settings loaded, which
keeps your own instructions, output style and MCP servers out of the runs.

## The sets

Each file in `sets/` has one row per title with the name, the assistant draft, the
author's notes or `-` when there are none, and for fiction the WritingPrompts prompt.
Paths are relative to the repo.

- `dev` has the 12 e2e titles and the 8 fresh ones. Rules were chosen on these.
- `test` has 18 other blog titles that were never used to choose anything.
- `es` has 30 Spanish titles.
- `fic` and `fic2` have 30 and 32 WritingPrompts stories and no notes.

Claude wrote the notes for `test` and `es` from each human post with `gennotes.py`, as terse
bullets like the ones in `eval/notes/` and in the post's language. The human originals are
not redistributed. The corpus scripts in `scripts/` fetch them to `~/corpus/`, and the
harness expects them there.

## Running a comparison

```sh
H=eval/e2e
python3 $H/harness.py snapshot new            # copy SKILL.md, references/, scripts/ as "new"
python3 $H/harness.py snapshot old /path/to/other/checkout
for r in 0 1 2; do python3 $H/harness.py rewrite new $r -j 6; done
python3 $H/report.py old new                  # judges every rewrite, compares per title
python3 $H/report.py old new --set test --reps "rt*"
```

Each rewrite lands in `work/SNAP/rREP/TITLE/final.md`. Titles already done are skipped, so
a run cut short by a usage limit can be restarted as it is. Set `REWRITER=claude-sonnet-5`
to change the model that rewrites. The report asks two Claude Opus 5.5 judges per text;
`--k 3 --g 2` gives the panel behind the September numbers, three Opus and two GPT-5.6.
Judge answers are cached by text, so a report reruns for free.

The report prints each version's mean P(AI) for both judge families and the share of
texts over 50. Then it gives the per-title difference from the first version, how many
titles got worse and a Wilcoxon signed-rank p. Add `--reasons` for the judges' most common
reasons. A fiction set switches the judge prompt by itself. To score any other files, such
as the human originals as a control, use `harness.py judge FILES`.

## The other scripts

The feature explorer computes candidate features and their AUC against held-out human
posts. That is how the redundancy feature and the 2024 to 2026 stylometry features were
checked and dropped. The rewrite detector fits a logistic regression that tells the
skill's rewrites from human posts on words used across many titles, then prints the words
that give the rewrites away.

The last script runs two detectors on a GPU, Binoculars with
Qwen2.5-3B and its instruct model, and the desklib DeBERTa classifier. It and the rewrite
detector need the virtualenv, whose python `QUIRON_DETECTOR_PY` points at. In our runs
Binoculars told Claude posts from human ones with an AUC of 0.93 but did not separate GPT
posts, and desklib scored most human dev.to posts as AI, so neither decides anything here.

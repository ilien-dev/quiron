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
- `hum` has 16 human posts from `~/corpus/blog` as the drafts, with no notes. It shows
  what the loop costs a text a person wrote.
- `devnn` is `dev` without the notes.
- `scr` and `scr2` have 20 assistant video scripts each, from `eval/ai/script/train-*`
  and `test-*`, with no notes and the video's title in the fourth column. `scr-es` and
  `scr2-es` are the same in Spanish, from `eval/ai/script-es/`. Rules were chosen on `scr`
  and `scr-es` and confirmed on the other two.
- `scrh` and `scrh-es` have 10 held-out human captions each, from `~/corpus/script` and
  `~/corpus/script-es`. They are local: their paths point into the corpus that
  `scripts/build-corpus-script.sh` fetches, and the captions are not in the repo. Nine of
  the ten English ones and all ten Spanish ones are on the same titles as `scr2` and
  `scr2-es`, so their names start with `h-`.

`mksets.py` writes the six script sets, and its docstring gives the rule that picks the
rows. A script set gets a rewriter prompt with the title in the set's language, and the
judges read only the narration (`harness.narration`), with a prompt of their own.
`scriptstats.py SET SNAP ...` prints what the rewrites did to the text: a few meter
features, the script patterns, fillers and ellipses, leftover markup, and how much of the
narration the meter's text filter drops.

Until November 2026 that filter dropped some of it. Where `spoken()` took out stacked
stage directions it left a run of blank lines, and `aimeter.prose()` read the run and the
next line as indented code. Assistant scripts lost 5% to 10% of their narration that way,
and human captions lost nothing. `spoken()` now closes those runs, so the `lost` column
should read 0%.

A row with no notes gets a prompt that says so and tells the rewriter not to stop and
ask. Sonnet 5.5 otherwise refuses to write `final.md` until it has the notes.

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

The video-script rounds compared three snapshots. `main` is the skill before the script
register, taken from `git archive origin/main` unpacked into a scratch folder and passed as
SRC. `rules` is commit `37a1cff`, which has the rules in `references/script.md`. `bands`
is the same commit with `--no-script-rules`, which deletes `references/script.md`, takes
out the two lines of `SKILL.md` that point to it and turns off the script checks (S1 to S7,
SE1 to SE8) in the snapshot's `audit.py`. The band files and the register's entry stay. If
one of those edits no longer matches the files, the command stops instead of making a
snapshot that is not what its name says. The rules did not beat `bands` and were removed
after that commit, so on a later tree the flag only turns the checks off. The numbers are
in `eval/results/script-e2e.txt` and `script-es-e2e.txt`.

```sh
git archive origin/main | tar -x -C /tmp/quiron-main
git archive 37a1cff | tar -x -C /tmp/quiron-rules
python3 $H/harness.py snapshot main /tmp/quiron-main
python3 $H/harness.py snapshot bands /tmp/quiron-rules --no-script-rules
python3 $H/harness.py snapshot rules /tmp/quiron-rules
REWRITER=claude-sonnet-5-5 python3 $H/harness.py rewrite rules 0 --set scr -j 6
JUDGE=claude-sonnet-5-5 GPT_MODEL=gpt-6.1-terra python3 $H/report.py bands rules --set scr --k 2 --g 1 --noise
```

A snapshot name is never reused once rewrites exist under it, because finished rewrites
are kept and would be judged together with the new ones.

Each rewrite lands in `work/SNAP/rREP/TITLE/final.md`. Titles already done are skipped, so
a run cut short by a usage limit can be restarted as it is. Set `REWRITER=claude-sonnet-5`
to change the model that rewrites. The report asks two Claude Opus 5.5 judges per text;
`--k 3 --g 2` gives the panel behind the September numbers, three Opus and two GPT-5.6.
Judge answers are cached by text, so a report reruns for free.

A cheaper panel works too. `JUDGE=claude-sonnet-5-5` swaps the Claude judge and
`GPT_MODEL=gpt-6.1-terra` the Codex model, for the GPT judge and for `REWRITER=codex`;
each model keeps its own cache entries. On 58 texts already judged by Opus (18 human
posts, 20 rewrites, 20 untouched drafts), Sonnet 5.5 gave the human posts 4.8, the
rewrites 12.4 and the drafts 79.2, against 5.9, 32.2 and 87.8 from Opus. Terra gave 6.3,
46.1 and 91.9. Sonnet agrees with Opus across the three groups (r = 0.96) and is easier on
rewrites, where the two still rank the texts alike (r = 0.67); Terra is the harder judge
(r = 0.55 with Opus on rewrites). The November 2026 rounds in `references/numbers.md` used
Sonnet 5.5 as the rewriter with this panel, `--k 2 --g 1`.

`--noise` prints how far one version moves by itself: the spread between two judges of
the same text, and the difference between two reps of the same snapshot. Between reps the
set mean moved by up to 3.1 points with the Opus panel and 2.1 with the Sonnet one, so a
smaller difference between two versions is not a result.

The report prints each version's mean P(AI) for both judge families and the share of
texts over 50. Then it gives the per-title difference from the first version, how many
titles got worse and a Wilcoxon signed-rank p. Add `--reasons` for the judges' most common
reasons. A fiction set switches the judge prompt by itself. On a script set the report also
measures each text against the script band file of its language and prints the mean count
of overshot and AI-side features per text, with a paired test on overshoot. The snapshot
name `draft` stands for the set's drafts as they are; for `scrh` those are the human
captions. To score any other files, such
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

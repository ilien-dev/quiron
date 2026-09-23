# eval

Everything needed to rerun the measurements in `SKILL.md` and `references/`, except the
human corpora, which are fetched by the `scripts/build-corpus*.sh` scripts and not
redistributed.

## What is here

- `ai/blog/`, `ai/fiction/`, `ai/es/`: assistant texts written in September 2026.
  - `train/`: Claude Opus, Claude Sonnet, Claude Haiku and GPT (Codex CLI), on titles
    from the human training split. Used to learn the AI directions, the lexicons and
    the thresholds, and to train the word-frequency judge.
  - `test-opus/`, `test-sonnet/`, `test-gpt/`: the same models on held-out titles.
    Never used to choose anything.
  - `blog/e2e-*`: twelve held-out posts (`titles/blog-e2e.txt`) untouched (`e2e-raw`)
    and after an assistant followed successive versions of the skill: `e2e-v0` (the
    first version), `e2e-v1`, `e2e-v3` (specifics and structure guidance), `e2e-v4`
    (plus two real posts by the same author as voice samples, listed in
    `samples-list/`), `e2e-v5` (plus the author's notes in `notes/`). `skill-v0` holds
    twelve earlier rewrites by the first version.
- `titles/`: the prompts, one line per text: name, the human text's word count, title.
  Every text was generated from the plain request a user would type: "Write a blog post
  for dev.to titled "…". Around N words." (Spanish: "Escribe un post para dev.to titulado
  "…". Unas N palabras."; fiction: "Write a short story for this Reddit WritingPrompts
  prompt: … Around N words."), with N the human text's length clamped to 600–1,400.
- `notes/`: terse factual notes extracted from each human post of the e2e set, standing
  in for what the author would hand a ghostwriter.
- `lexicon-pool-*.tsv`: the published candidate words each lexicon was selected from.
- `results/`: evaluate.py output per register, and the blind-judge rounds with their
  answer keys and scores.
- `evals.json`: the task prompts used to check that a new version of `SKILL.md` does no
  worse than the old one. Each prompt is run once per Claude model with each version, so
  both get the same inputs, and the outputs are scored with the scripts used everywhere
  else here.

## Rerun

```sh
scripts/build-corpus.sh ~/corpus/blog            # 167 dev.to posts, recalibrates bands.json
scripts/build-corpus-fiction.sh ~/corpus/fiction # 157 WritingPrompts stories
scripts/build-corpus-es.sh ~/corpus/es           # 241 Spanish dev.to posts

python3 scripts/evaluate.py --human ~/corpus/blog --ai-train eval/ai/blog/train \
    opus=eval/ai/blog/test-opus sonnet=eval/ai/blog/test-sonnet gpt=eval/ai/blog/test-gpt
QUIRON_BANDS=scripts/bands-fiction.json python3 scripts/evaluate.py \
    --human ~/corpus/fiction --ai-train eval/ai/fiction/train opus=eval/ai/fiction/test-opus ...
QUIRON_BANDS=scripts/bands-es.json python3 scripts/evaluate.py \
    --human ~/corpus/es --ai-train eval/ai/es/train opus=eval/ai/es/test-opus ...
```

The dev.to API returns an author's newest posts first, so a later rebuild can pick a
slightly different set if an author deletes a post; the WritingPrompts pages are fixed.

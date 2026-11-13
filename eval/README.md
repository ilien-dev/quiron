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
  - `train-2026-11/` and `test-opus55/`, `test-sonnet55/`, `test-fable52/`, `test-gpt61/`,
    `test-terra/`: the same titles written again in November 2026 by Claude Opus 5.5,
    Sonnet 5.5 and Haiku 5.5 and by GPT-6.1 (training), and by Opus 5.5, Sonnet 5.5, Fable
    5.2, GPT-6.1 and GPT-6.1 Terra (held out). `MANIFEST.tsv` in each register gives the
    folder, title, model id, date and prompt of every one of these texts. The September
    texts have no such record.
  - `blog/e2e-*`: twelve held-out posts (`titles/blog-e2e.txt`) untouched (`e2e-raw`)
    and after an assistant followed successive versions of the skill: `e2e-v0` (the
    first version), `e2e-v1`, `e2e-v3` (specifics and structure guidance), `e2e-v4`
    (plus two real posts by the same author as voice samples, listed in
    `samples-list/`), `e2e-v5` (plus the author's notes in `notes/`). `skill-v0` holds
    twelve earlier rewrites by the first version.
- `ai/pr/`, `ai/commit/`, `ai/readme/`, `ai/email/`: four more registers from November
  2026. The same models wrote them. The folders are the same too. Each text starts from
  the title of a human one, and `gensamples.py --titles` makes the title files. The email
  titles are Enron subject lines, so they stay out of the repo and the email texts are
  numbered.
- `ai/script/` and `ai/script-es/`: assistant video scripts written on 12 November 2026
  from the titles of the human captions, with the request "Write the script for a YouTube
  video titled "…". Around N words." (Spanish: "Escribe el guion de un video de YouTube
  titulado "…". Unas N palabras."). `train-gpt61`, `train-haiku55`, `train-opus55` and
  `train-sonnet55` hold 12 scripts each and train the bands. `test-opus55`, `test-sonnet55`,
  `test-fable52`, `test-gpt61` and `test-terra` hold 9 each in English and 5 in Spanish,
  and never choose anything. Scripts are kept as written, stage directions and speaker
  labels included, and `MANIFEST.tsv` gives the model, date and prompt of each.
- `titles/`: the prompts, one line per text: name, the human text's word count, title.
  Every text was generated from the plain request a user would type: "Write a blog post
  for dev.to titled "…". Around N words." (Spanish: "Escribe un post para dev.to titulado
  "…". Unas N palabras."; fiction: "Write a short story for this Reddit WritingPrompts
  prompt: … Around N words."), with N the human text's length clamped to 600–1,400.
- `titles/script-manifest.tsv` and `script-es-manifest.tsv`: every video examined for the
  human script corpus, with channel, upload date, caption track, word count and the status
  that kept or dropped it. `script[-es]-train-*.tsv` and `script[-es]-test-*.tsv` are the
  prompts of the assistant scripts, like the other title files.
- `gensamples.py`: writes those texts, one per title, through `claude -p` or `codex exec`
  from an empty folder. The current models often wrap a post in a ```` ```markdown ````
  block with dev.to front matter and add a comment to the user around it; the script
  keeps only the post.
- `script_candidates.py`, `script_channels.py`, `script_reasons.py`, `markup.py` and
  `band_compare.py` produce the video-script results: each candidate check counted on both
  sides, each feature counted per channel, the blind judges' reasons on narrations, the
  stage directions and labels per 1,000 spoken words, and a shipped band file applied to
  groups of texts without recalibrating.
- `notes/`: terse factual notes extracted from each human post of the e2e set, standing
  in for what the author would hand a ghostwriter.
- `lexicon-pool-*.tsv`: the published candidate words each lexicon was selected from.
- `results/`: evaluate.py output per register, the blind-judge rounds with their answer
  keys and scores, and the video-script files: `script.txt` and `script-es.txt` (bands,
  thresholds and held-out evaluation), `script-candidates.txt` and
  `script-es-candidates.txt` (every candidate check and the decision on it),
  `script-channels.txt` and `script-es-channels.txt`, `script-markup.txt` and
  `script-es-markup.txt`, `script-reasons.txt` and `script-es-reasons.txt`, and
  `script-e2e.txt` and `script-es-e2e.txt` (the end-to-end runs, with a verdict at the
  top). Every block in them has its command above it.
- `evals.json`: the task prompts used to check that a new version of `SKILL.md` does no
  worse than the old one. Each prompt is run once per Claude model with each version, so
  both get the same inputs, and the outputs are scored with the scripts used everywhere
  else here.

## Rerun

```sh
scripts/build-corpus.sh ~/corpus/blog            # 167 dev.to posts, recalibrates bands.json
scripts/build-corpus-fiction.sh ~/corpus/fiction # 157 WritingPrompts stories
scripts/build-corpus-es.sh ~/corpus/es           # 241 Spanish dev.to posts
scripts/build-corpus-work.sh pr ~/corpus/pr      # also commit, readme, email; needs GITHUB_TOKEN
scripts/build-corpus-script.sh en ~/corpus/script   # also es; needs yt-dlp and node

A=eval/ai/blog
python3 scripts/evaluate.py --human ~/corpus/blog --ai-train $A/train,$A/train-2026-11 \
    opus=$A/test-opus sonnet=$A/test-sonnet gpt=$A/test-gpt opus55=$A/test-opus55 \
    sonnet55=$A/test-sonnet55 fable52=$A/test-fable52 gpt61=$A/test-gpt61 terra=$A/test-terra
A=eval/ai/fiction
QUIRON_BANDS=scripts/bands-fiction.json python3 scripts/evaluate.py \
    --human ~/corpus/fiction --ai-train $A/train,$A/train-2026-11 opus=$A/test-opus ...
A=eval/ai/es
QUIRON_BANDS=scripts/bands-es.json python3 scripts/evaluate.py \
    --human ~/corpus/es --ai-train $A/train,$A/train-2026-11 opus=$A/test-opus ...

python3 eval/gensamples.py blog eval/titles/blog-test-opus.tsv claude-opus-5-5 eval/ai/blog/test-opus55

# video scripts: the commands for each file in eval/results/script*.txt are at its head
A=eval/ai/script
QUIRON_BANDS=scripts/bands-script.json python3 scripts/evaluate.py --human ~/corpus/script \
    --ai-train $A/train-gpt61,$A/train-haiku55,$A/train-opus55,$A/train-sonnet55 \
    opus55=$A/test-opus55 sonnet55=$A/test-sonnet55 fable52=$A/test-fable52 \
    gpt61=$A/test-gpt61 terra=$A/test-terra
python3 eval/script_candidates.py en           # then es, with scripts/bands-script-es.json for evaluate.py
```

`eval/results/blog.txt`, `fiction.txt` and `es.txt` hold the output of the three `evaluate.py`
runs from 12 November 2026, on corpora rebuilt that month: 159 blog posts, 157 stories and
237 Spanish posts that measure. The video-script files were written the same day, on 193
English and 107 Spanish captions from 17 and 13 channels.

The dev.to API returns an author's newest posts first, so a later rebuild can pick a
slightly different set if an author deletes a post; the WritingPrompts pages are fixed.

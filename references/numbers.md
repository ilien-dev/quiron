# Part C: the numbers

The bands, the AI directions, what the whole apparatus does on held-out texts, how to calibrate for another register, and what the skill does not do. Read it when a meter verdict surprises you or the text is in a register the shipped bands do not cover.

## Contents

- Where the numbers come from
- Blog bands
- Fiction bands
- Work registers: pull requests, commit messages, READMEs, email
- Video scripts, English and Spanish: the corpus, the bands, the checks, the end-to-end runs
- Four counter-intuitive results
- What the apparatus does on held-out texts
- What the loop does to a text
- The November 2026 rounds
- Checks measured and not shipped
- Calibrating for another register
- Part D: what this does not do

## The bands

The meter scores 23 features against a band built from real human texts, and reports
three states: inside the band, outside on the AI side, outside on the overshoot side. A
value within 5% of the band's width past an edge counts as inside, so one comma does not
flip a verdict.

### Where the numbers come from

**Where the numbers come from.** The blog band file was built by `build-corpus.sh` from
167 dev.to posts by 21 authors (at most 8 each), all published before 2022. The fiction
band file was built by `build-corpus-fiction.sh` from 157 WritingPrompts stories (Reddit,
2018, 500 to 1,500 words). Both predate ChatGPT. The assistant texts are in `eval/ai/`:
posts and stories written in September 2026 by Claude Opus, Claude Sonnet, Claude Haiku
and GPT (through the Codex CLI) from the same titles and prompts, with the plain request
a user would type. Every fourth human text is held out; the bands, the AI directions,
the lexicons and the thresholds were all chosen on the rest, and every figure below is
on the held-out texts unless it says otherwise.

In November 2026 the assistant side was written again, same titles and same request, by
the models then current: Claude Opus 5.5, Sonnet 5.5, Haiku 5.5 and GPT-6.1 for training
(`train-2026-11/`), and Opus 5.5, Sonnet 5.5, Fable 5.2, GPT-6.1 and GPT-6.1 Terra on the
held-out titles (`test-opus55/` and so on). `eval/ai/*/MANIFEST.tsv` records the model,
date and prompt of each text; the September texts have no such record. The AI medians
and directions in the three band files now come from both months together (96 blog posts,
64 stories, 64 Spanish posts); the human edges are unchanged, except the AI-lexicon band,
which follows the lexicon. The local human corpora were rebuilt in between, so the
November figures are on 40 held-out blog posts, 40 stories and 58 Spanish posts.

### Blog bands

**Blog posts** (`bands.json`). AI median and AI side are from the 96 training posts of
both months. AUC is the chance a held-out assistant post sits further to the AI side than
a held-out human post (40 of them), for the 42 September posts and the 70 November posts;
0.5 is no signal. *Either* means the direction was too weak on the training posts to
score, so only the band applies.

| feature | human p10–p90 | AI median | AI side | AUC Sept | AUC Nov |
|---|---|---|---|---|---|
| sentence-length CV | 0.43 – 0.72 | 0.49 | lower | 0.67 | 0.68 |
| mean sentence length | 14.1 – 24.4 | 15.1 | lower | 0.63 | 0.84 |
| long words (7+) /1k | 160 – 250 | 251 | higher | 0.76 | 0.71 |
| mean word length | 4.3 – 4.9 | 4.9 | higher | 0.80 | 0.73 |
| nominalizations /1k | 7.3 – 32.6 | 24.8 | higher | 0.67 | 0.64 |
| -ly adverbs /1k | 4.8 – 19.2 | 13.0 | either | – | – |
| passive voice /1k | 1.9 – 11.3 | 3.9 | lower | 0.67 | 0.76 |
| lexical diversity MATTR-50 | 0.763 – 0.850 | 0.841 | higher | 0.85 | 0.76 |
| first person /1k | 8.6 – 65.2 | 3.3 | lower | 0.79 | 0.81 |
| contractions /1k | 10.4 – 37.0 | 20.6 | either | – | – |
| questions /1k | 0 – 6.5 | 0.3 | either | – | – |
| repeated openers /100 | 0 – 11.9 | 3.2 | either | – | – |
| connective openers % | 0 – 14.3 | 2.9 | lower | 0.65 | 0.70 |
| commas /1k | 25.1 – 58.0 | 57.6 | higher | 0.81 | 0.72 |
| semicolons /1k | 0 – 3.4 | 0 | either | – | – |
| em dashes /1k | 0 – 2.7 | 0 | either | – | – |
| AI-lexicon words /1k | 0 – 1.6 | 2.1 | higher | 0.79 | 0.77 |
| lists of three /1k | 0 – 5.5 | 6.5 | higher | 0.88 | 0.79 |
| participial clauses /1k | 0 – 2.3 | 0.9 | either | – | – |
| plain words /1k | 43 – 95 | 56 | lower | 0.62 | 0.62 |
| parentheses /1k | 0 – 11.0 | 0.9 | lower | 0.67 | 0.75 |
| words per paragraph | 23.5 – 74.2 | 37.6 | either | – | – |
| headings /1k | 0 – 17.1 | 11.9 | higher | 0.78 | 0.68 |

Six directions held in September and are gone with both months together: -ly adverbs,
questions, repeated openers, semicolons, em dashes and participial clauses. Connective
openers gained one (lower). The November models are shorter in the sentence than the
September ones (0.84) and closer to people in word length, vocabulary range and headings.

### Fiction bands

**Fiction** (`bands-fiction.json`), 40 held-out human stories against 30 assistant stories.
The strongest features: headings (a title line on the story; no human story had one,
AUC 0.83), words per paragraph (human 26 – 106, AI median 22.5, lower, AUC
0.81), em dashes (human 0 – 0, AI 2.4, 0.79), sentence-length CV (0.45 – 0.76, AI 0.69,
*higher*, 0.77), lexical diversity (0.839, 0.77), contractions (*higher*, 0.75), mean word
length (0.73), commas (0.72). One learned direction did not hold up: nominalizations
looked higher in the training stories (0.61) and were lower in the held-out ones (0.38).
With the November stories added, nominalizations and first person lose their direction
and passive voice gains one (lower). On the 50 held-out November stories the strongest
features are words per paragraph (AI median 26.4, AUC 0.90), mean sentence length (11.4,
lower, 0.85) and contractions (0.76); the title heading (0.64) and the em dash (0.57)
have faded.

### Work registers: pull requests, commit messages, READMEs, email

Four band files added in November 2026, each built by `build-corpus-work.sh` from human
texts that predate ChatGPT and measured against texts the November models wrote from
the same titles ("Write the description for a pull request titled … in the … repository.
Around N words.", and the like for a commit subject, a project name and description, an
email subject). A quarter of the human texts is held out, as everywhere else.

| register | human texts | held-out humans clean | Opus 5.5, Sonnet 5.5, Fable 5.2 clean | GPT-6.1, Terra clean | C1 fails at |
|---|---|---|---|---|---|
| `bands-pr.json` | 170 descriptions of merged GitHub pull requests opened 2019 to 2021, at most 2 per author and 4 per repository | 98% of 43 | 89%, 67%, 89% | 43%, 43% | 4 |
| `bands-commit.json` | 132 commit messages with a long body from 17 projects (Linux, Git, PostgreSQL, Go and others), 2019 to 2021 | 97% of 33 | 67%, 100%, 100% | 0%, 20% | 3 |
| `bands-readme.json` | 170 READMEs of repositories last pushed before June 2021, one per owner | 100% of 43 | 78%, 78%, 89% | 0%, 25% | 4 |
| `bands-email.json` | 170 workplace emails from the Enron corpus, 1999 to 2002 (AESLC) | 98% of 43 | 67%, 89%, 88% | 12%, 75% | 4 |

What separates the assistant texts, on the training texts (AUC against all the human
ones): in pull requests, longer words (mean 5.2 against a human band of 4.3 to 5.0, 0.90),
more nominalizations (0.80), lists of three (0.85), no parentheses and little first
person; in commit messages, longer words (0.79) and a wider vocabulary (0.77), with no
first person and no connective openers; in READMEs, a wider vocabulary (0.91), lists of
three (11.9 per 1,000 words against a band that tops at 8.4, 0.91), few parentheses and
even sentences; in email, a wider vocabulary (0.91), more commas (0.84), lists of three
(0.82) and shorter sentences. The word-frequency judge calls 78% to 100% of the held-out
Opus 5.5, Sonnet 5.5 and GPT texts AI in every register. Fable 5.2 gets past it more
often: 89% in pull requests, 75% in email, 44% in READMEs and 29% in commit messages. It
also calls 18% of the human commit messages and 9% of the human emails AI.

Read these with their limits. The held-out assistant groups have 5 to 9 texts per model,
so each percentage moves by 11 to 20 points with one text. Only texts the meter can
measure are in the corpora, about 130 words and up: the usual two-line commit message and
the three-line email are not. The assistant wrote from a title alone, not from a diff or
a thread, so its text is more generic than what an agent writes with the change in front
of it. The Enron emails come with their paragraph breaks removed, so words per paragraph
is not scored for email (`_skip` in the band file). Their subject lines and mailbox names
are not in this repository: the email texts in `eval/ai/email/` are numbered, the three
written from a subject that named a person were left out, and `eval/titles/email-*.tsv`
is made locally by `gensamples.py --titles email`. The lexicon is the blog one; B1
failed no held-out human text in any of the four. And the rewrite rules were not run end
to end here: these files tell a draft from human text of its kind, and nothing yet shows
what the loop does to a pull request description. The checklist catches GPT-6.1 in all
four and lets most Claude drafts through, as it does in blog posts.

### Video scripts: English and Spanish

Two band files, `bands-script.json` and `bands-script-es.json`, built on 12 November 2026 for the narration of a YouTube video. They read the spoken words only: a band file with `"_spoken": true` makes the meter and the checklist call `aimeter.spoken()` first, which drops scene headings, stage directions, speaker labels, timestamps, word-count trailers, production notes and source lists and counts each as markup. Assistant scripts carry plenty of it (a median of 0 to 18.4 stage directions per 1,000 spoken words by folder in English, 7.3 to 13.5 in Spanish) and human captions carry none (`eval/results/script-markup.txt`, `script-es-markup.txt`, from `python3 eval/markup.py script ~/corpus/script OUT`). The rewrite keeps all of that markup where it was.

The register measures a draft and its checks catch a share of assistant scripts. The end-to-end runs below say what it does not do: it did not make a rewritten script read as human-written to blind judges.

**Corpus.** Manual captions of YouTube videos uploaded on or before 31 December 2021, so every text predates ChatGPT. Only manual tracks are read, never automatic ones. A video is kept when it has 300 to 3,000 spoken words, no more than five speaker changes, no more than two hesitations ("uh", "um"; "eh", "em", "o sea" in Spanish) per 1,000 words and normal punctuation. The channels are narrated explainers. `scripts/build-corpus-script.sh en|es [OUTDIR]` builds the corpus and needs `yt-dlp` (it uses `node` when `node` is on the path; manual captions download without it). It writes `eval/titles/script-manifest.tsv` and `script-es-manifest.tsv`, one row per video examined with its upload date, track, word count and status, so the choice can be audited. The texts are not redistributed.

| | English | Spanish |
|---|---|---|
| videos examined | 424 | 613 |
| kept as human scripts | 193 | 107 |
| channels | 17 (6 to 12 each) | 13 (3 to 12 each) |
| upload dates | 9 July 2009 to 11 November 2021 | 28 April 2013 to 10 November 2021 |
| median length | 1,177 words | 1,452 words |
| train, held out (every 4th file) | 144, 49 | 80, 27 |
| assistant scripts, train | 48 (12 each: GPT-6.1, Haiku 5.5, Opus 5.5, Sonnet 5.5) | 48 (same) |
| assistant scripts, test | 45 (9 each: Opus 5.5, Sonnet 5.5, Fable 5.2, GPT-6.1, Terra) | 25 (5 each) |

The English channels are 3Blue1Brown, CGP Grey, Every Frame a Painting, Johnny Harris, Kurzgesagt, LEMMiNO, Nerdwriter1, Oversimplified, PBS Space Time, Real Engineering, TED-Ed, Tom Scott, Veritasium, Vox, Vsauce, Wendover Productions and exurb1a. The Spanish ones are Academia Play, C de Ciencia, CuriosaMente, Date un Vlog, Derivando, El Robot de Platón, Jaime Altozano, La Hiperactina, Memorias de Pez, Pero eso es otra historia, QuantumFracture, Un Mundo Inmenso and VisualPolitik. The rest of the videos examined: in English 92 had no manual track, 59 were over 3,000 words, 59 unscripted, 11 under 300, 5 unpunctuated, 3 translated and 2 failed to download; in Spanish 399 had no manual track, 36 were unpunctuated, 33 failed to download, 17 were too long, 9 unscripted, 8 unavailable, 3 translated and 1 too short. Two more Spanish channels, Antroporama and Magic Markers, returned no listing under the handles tried; they are not in the corpus or the manifest. Spanish manual tracks are rarer, which is why 613 videos gave 107 scripts. The assistant scripts come from the plain request `Write the script for a YouTube video titled "…". Around N words.` (`Escribe el guion de un video de YouTube titulado "…". Unas N palabras.`), with the title and length of a human script on the training split; `eval/ai/script*/MANIFEST.tsv` records model, date and prompt for each. A caption is what was said, put into text by whoever captioned it, so the human side is narration with the captioner's punctuation and no paragraphs.

**Bands** (`bands-script.json`, `bands-script-es.json`). Built with `python3 scripts/aimeter.py --calibrate TRAIN --ai AI_TRAIN_DIRS --out FILE --spoken`; the exact commands, with every rebuild, are at the top of `eval/results/script.txt` and `script-es.txt`. Only the scored features are listed. *AUC, train* is the chance an assistant script sits further to the AI side than a human one on the 144 or 80 and 48 training scripts (the band file stores the chance that an AI value is the higher one; the table shows it from the AI side). *AUC, held out* is the range over the five test models against the held-out humans, from the section "The shipped state, in full" of the same results files. A range that crosses 0.5 means the models disagree. *Either* means the direction was too weak to score, so only the band applies.

English, 17 of 23 features scored:

| feature | human p10–p90 (median) | AI median | AI side | AUC, train | AUC, held out |
|---|---|---|---|---|---|
| sentence-length CV | 0.446 – 0.797 (0.579) | 0.531 | lower | 0.64 | 0.59 to 0.88 |
| mean sentence length | 13.1 – 25.4 (17.8) | 12.3 | lower | 0.93 | 0.88 to 0.94 |
| long words (7+) /1k | 141 – 250 (196) | 216 | higher | 0.66 | 0.50 to 0.86 |
| mean word length | 4.22 – 4.82 (4.53) | 4.71 | higher | 0.71 | 0.53 to 0.82 |
| nominalizations /1k | 5.8 – 35.6 (13.8) | 18.0 | higher | 0.61 | 0.37 to 0.79 |
| -ly adverbs /1k | 8.8 – 21.7 (14.5) | 13.0 | lower | 0.61 | 0.35 to 0.72 |
| passive voice /1k | 2.2 – 12.8 (6.0) | 5.0 | either | – | – |
| lexical diversity MATTR-50 | 0.77 – 0.833 (0.807) | 0.832 | higher | 0.81 | 0.70 to 0.88 |
| first person /1k | 1.8 – 34.6 (14.4) | 4.9 | lower | 0.72 | 0.59 to 0.80 |
| contractions /1k | 10.0 – 37.8 (21.9) | 24.1 | either | – | – |
| questions /1k | 0 – 10.1 (2.7) | 3.4 | either | – | – |
| repeated openers /100 | 0 – 9.1 (3.5) | 5.2 | higher | 0.64 | 0.55 to 0.76 |
| connective openers % | 7.1 – 28.7 (17.2) | 12.1 | lower | 0.70 | 0.57 to 0.68 |
| AI-lexicon words /1k | 0 – 1.79 (0.43) | 1.73 | higher | 0.70 | 0.38 to 0.73 |
| lists of three /1k | 0 – 5.15 (2.08) | 6.21 | higher | 0.81 | 0.70 to 0.88 |
| participial clauses /1k | 0 – 2.84 (1.01) | 1.04 | either | – | – |
| plain words /1k | 44 – 108 (75) | 62.5 | lower | 0.67 | 0.61 to 0.70 |

Spanish, 19 of 23 features scored:

| feature | human p10–p90 (median) | AI median | AI side | AUC, train | AUC, held out |
|---|---|---|---|---|---|
| sentence-length CV | 0.474 – 0.813 (0.601) | 0.518 | lower | 0.76 | 0.69 to 0.94 |
| mean sentence length | 14.6 – 29.1 (21.1) | 14.4 | lower | 0.88 | 0.79 to 0.93 |
| long words (7+) /1k | 218 – 303 (263) | 291 | higher | 0.73 | 0.54 to 0.97 |
| mean word length | 4.46 – 4.94 (4.74) | 4.85 | higher | 0.68 | 0.53 to 0.98 |
| nominalizations /1k | 11.7 – 34.8 (22.1) | 25.4 | higher | 0.63 | 0.39 to 0.85 |
| -mente adverbs /1k | 2.8 – 9.8 (5.9) | 3.9 | lower | 0.66 | 0.09 to 0.81 |
| passive voice /1k | 0 – 5.4 (2.1) | 1.4 | either | – | – |
| lexical diversity MATTR-50 | 0.755 – 0.825 (0.797) | 0.823 | higher | 0.83 | 0.76 to 1.00 |
| first person /1k | 1.1 – 14.6 (5.4) | 2.8 | lower | 0.65 | 0.46 to 0.74 |
| contractions /1k | 0 – 0 (0) | 0 | either | – | – |
| questions /1k | 0.45 – 10.7 (3.7) | 4.0 | either | – | – |
| repeated openers /100 | 0 – 6.1 (2.4) | 2.35 | either | – | – |
| connective openers % | 8.8 – 26.9 (18.2) | 16.4 | either | – | – |
| commas /1k | 34 – 77 (60) | 66.5 | higher | 0.67 | 0.12 to 0.59 |
| AI-lexicon words /1k | 0 – 0.48 (0) | 0 | either | – | – |
| lists of three /1k | 0 – 4.95 (2.23) | 5.55 | higher | 0.82 | 0.62 to 0.77 |
| participial clauses /1k | 0 – 2.53 (0.89) | 0.56 | either | – | – |
| plain words /1k | 24.8 – 51.7 (40.35) | 31.5 | lower | 0.65 | 0.41 to 0.78 |
| parentheses /1k | 0 – 5.09 (0.61) | 0 | lower | 0.73 | 0.70 to 0.76 |

Two features hold in both languages on every channel: shorter sentences (assistant median 12.3 and 14.4 words, the human median on the human side in 17 of 17 and 10 of 10 channels) and more lists of three (6.21 and 5.55 per 1,000 words against human medians of 2.08 and 2.22, on the human side in 17 of 17 and 10 of 10 channels). Lexical diversity is on the human side in 16 of 17 and 10 of 10 channels. In English the AI-lexicon rate is on the human side in 17 of 17; in Spanish it is 0 against 0, so only the band applies. The counts are in `eval/results/script-channels.txt` and `script-es-channels.txt`, from `QUIRON_BANDS=scripts/bands-script.json python3 eval/script_channels.py eval/titles/script-manifest.tsv ~/corpus/script AI_TRAIN_DIRS`. Spanish counts ten channels, the ones with four or more texts. In Spanish, GPT-6.1 writes more -mente adverbs and fewer commas than people (held-out AUC 0.09 and 0.12), against the direction the other four models give, which is why the ranges of those two features cross 0.5.

**Features switched off (`_skip`).** English: words per paragraph, headings, commas, em dashes, semicolons and parentheses. Spanish: words per paragraph, headings, semicolons and em dashes. Captions have no paragraphs or headings (a caption is one line, a human median of 1,186 words per paragraph in English), so those two say nothing. The other four depend on the captioner more than on the speaker. The rule, written before the numbers: a punctuation feature goes to `_skip` when fewer than three quarters of the counted channels sit on the human side of the AI median. In English commas had 11 of 17, and em dashes, semicolons and parentheses 0 of 17 (a tie at 0 per 1,000 words on both sides for the first two). In Spanish commas had 9 of 10 and parentheses 8 of 10, so they stay scored; semicolons and em dashes tie at 0.

**Thresholds** (`_thresholds`). English: C1 (rates on the AI side) fails at 4, T1 (tells together) at 6, B1 (AI-lexicon words) at 4. Spanish: C1 at 6, T1 at 4. They were picked from a grid with the human train scripts added (`eval/results/script.txt` and `script-es.txt`, "Shape patterns"): of the values that keep the train humans as clean as before the new checks and the held-out humans no less clean, the one that catches the most assistant scripts, a tie going to the higher value. Under the chosen ones 91% of the English and 96% of the Spanish train humans are clean. The choice looked at the held-out humans too, so the held-out clean rates below are optimistic.

**Checks.** They run only when the band file says `"_register": "script"`. Each rate is held-out humans, train humans, and the assistant test scripts pooled (`python3 eval/script_candidates.py en|es`, `eval/results/script-candidates.txt` and `script-es-candidates.txt`, section "Decisions"). The Spanish checks were written from the judges' reasons on Spanish texts and counted on Spanish texts on both sides; the English patterns were not translated. All are in `references/patterns.md`.

| check | what it finds | held-out humans | train humans | assistant test |
|---|---|---|---|---|
| S1 | a sentence opens with "Imagine" or "Picture this" | 1 of 49 | 8 of 144 | 31% |
| S2 | staged reveals: "here's the twist", "here's why", "then there's", "the honest answer", "sounds simple" | 6 of 49 | 23 of 144 | 49% |
| S3 | a request for comments ("let us know in the comments", "leave a comment") | 0 of 49 | 5 of 144 | 24% |
| S4 | "next time you" | 2 of 49 | 1 of 144 | 16% |
| S5 | a bare noun-phrase question ("The catch?") | 1 of 49 | 1 of 144 | 9% |
| S6 | two sentences on one opener: "No X. No Y.", "Maybe… Maybe…" | 0 of 49 | 4 of 144 | 11% |
| S7 (FAIL) | three of S1 to S6 in one script | 0 of 49 | 0 of 144 | 18% |
| SE1 (FAIL) | "quédate hasta el final" | 0 of 27 | 0 of 80 | Opus 5.5 2 of 5, Sonnet 5.5 4 of 5 |
| SE2 | "hoy te cuento", "hoy vamos a" | 3 of 27 | 8 of 80 | 36% |
| SE3 | a sentence opens with "imagina" | 2 of 27 | 4 of 80 | 44% |
| SE4 | "y aquí viene", "lo curioso es que", "dato curioso" | 1 of 27 | 4 of 80 | 32% |
| SE5 | a sentence opens with "entonces, ¿" | 2 of 27 | 5 of 80 | 36% |
| SE6 | a request for comments with a verb ("cuéntame", "déjanos", "escríbeme") | 1 of 27 | 4 of 80 | 52% |
| SE7 | "la próxima vez que" | 0 of 27 | 1 of 80 | 4% (one Fable 5.2 script) |
| SE8 (FAIL) | three of SE1 to SE7 in one script | 0 of 27 | 0 of 80 | 40% |

S1 to S6 and SE2 to SE7 are TELLs. S7 and SE8 are combined checks, like T1, and SE1 is a pattern no human caption used. Share of each model's scripts that fail S7: Opus 5.5 33%, Sonnet 5.5 33%, Fable 5.2 0%, GPT-6.1 11%, Terra 11%. SE1 fails 40%, 80%, 0%, 0%, 0% and SE8 40%, 60%, 20%, 40%, 40% in the same order. A FAIL needs at most 5% of the held-out humans, and in Spanish at most 5% of the train humans too, since one text is 4% of 27.

Eleven checks from the blog register, and the TELL state of B1, are switched off for English scripts, and one check for Spanish, because on scripts they fire on humans about as often as on assistants (`SCRIPT_OFF` and `SCRIPT_B1_TELL_OFF` in `audit.py`). The rule: a TELL whose pooled assistant rate is under twice its held-out human rate goes off. English: A1, A1b, A2b, A3, A4, A8, A9, A14b, A15, A26, A32 and the TELL state of B1 (one to three lexicon words: 47% of held-out humans, 60% of assistants; B1 still fails at four). Spanish: A2b (2 of 27 humans, 1 of 25 assistant scripts). A17, A20, A4b, A5 and B2 stay on in English, and B1, E1, E3 and E4 in Spanish (`script-candidates.txt`, "Existing checks in this register" and "re-applied on whole narrations").

**On held-out texts.** Checklist clean means no FAIL. The word-frequency judge is the one in `evaluate.py`, trained on the training texts of the same register. The "before" row reads the same texts with the blog or Spanish blog bands and no spoken filter.

| English | texts | checklist clean | blog bands, clean | word-frequency judge says AI | checklist AUC |
|---|---|---|---|---|---|
| human, held out | 49 | 94% (46 of 49) | 82% (40 of 49) | 2% | – |
| Opus 5.5 | 9 | 22% | 56% | 67% | 0.745 |
| Sonnet 5.5 | 9 | 33% | 67% | 44% | 0.887 |
| Fable 5.2 | 9 | 78% | 56% | 56% | 0.836 |
| GPT-6.1 | 9 | 33% | 33% | 67% | 0.963 |
| Terra | 9 | 44% | 44% | 67% | 0.963 |

| Spanish | texts | checklist clean | Spanish blog bands, clean | word-frequency judge says AI | checklist AUC |
|---|---|---|---|---|---|
| human, held out | 27 | 96% (26 of 27) | 96% (26 of 27) | 11% | – |
| Opus 5.5 | 5 | 20% | 80% | 100% | 0.993 |
| Sonnet 5.5 | 5 | 0% | 80% | 80% | 0.952 |
| Fable 5.2 | 5 | 60% | 80% | 100% | 0.985 |
| GPT-6.1 | 5 | 0% | 40% | 100% | 0.952 |
| Terra | 5 | 40% | 40% | 100% | 0.904 |

Sources: `eval/results/script.txt` and `script-es.txt`, section "The shipped state, in full" (clean share, judge, AUC; rerun with the command at its head) and the "Before and after on the same texts" blocks (the blog-bands column, from `eval/band_compare.py`; the "after" counts in the last block of "Shape patterns" agree with the clean column). Fable 5.2 is the model the English checks catch least, as in every other register: 78% of its scripts are clean against 56% under the blog bands. Read these with their limits. The thresholds, the switch-offs, the size of the combined checks (three, not two) and T1 were chosen with the held-out rates in view, so the held-out columns are optimistic; the train humans are 91% and 96% clean. The test folders hold 9 and 5 scripts per model, so one script moves a rate by 11 or 20 points. The assistant scripts were written from a title alone.

**What the blind judges say, on narrations.** `JUDGE=claude-sonnet-5-5 python3 eval/script_reasons.py en|es -k 2` (`eval/results/script-reasons.txt`, `script-es-reasons.txt`). Two Sonnet 5.5 judges read each narration alone and gave P(AI): human train captions 6.1 in English and 5.2 in Spanish (0 of 48 over 50), assistant train scripts 83.3 (48 of 48 over 50) and 81.8 (46 of 48). Held-out human captions, judged in the end-to-end runs, are at 7.8 and 8.1. Of 288 reasons on assistant scripts in English, 217 name even polish, 144 signposting or explainer scaffolding, 114 a tidy ending, 104 no personal voice and 80 rhetorical questions answered at once; the Spanish counts run the same way (190, 167, 144, 120, 87). On human captions the commonest reasons are caption artifacts (103), personal voice (96) and spontaneous speech (90). The checks above come from these reasons and from reading ten human and ten assistant scripts in full.

### Video scripts end to end

The same protocol as the blog rounds of November 2026 (`eval/e2e/README.md`): Claude Sonnet 5.5 rewrites an untouched assistant script with a copy of the skill, two Sonnet 5.5 judges and one GPT-6.1 Terra judge read the narration alone (`--k 2 --g 1`), and differences are paired per title with a Wilcoxon test. 20 scripts in each set: `scr` and `scr-es` (development), `scr2` and `scr2-es` (held out, chosen the same way and never used to choose anything). No notes and no stopping to ask. The judge reads only the narration, so the stage directions the rewrite keeps cannot help or hurt. Every line has its command in `eval/results/script-e2e.txt` and `script-es-e2e.txt` (a "Verdict" block at the top, the commands in the sections below it). "Over" is the mean number of features per text past the human band on the overshoot side, "AI side" those on the AI side.

Snapshots. *main* is the skill before the register (`origin/main`). *Bands only* is the register with its checks switched off (`harness.py snapshot NAME --no-script-rules`); in the tables and the held-out sentence it is the snapshot `bands2`, built on the rebuilt band files. The rule comparisons and the first "register alone" figures use the earlier snapshot `bands`, built on the band files of `c2e6f98` and named wherever it is used. *Ships* is the tree as it ships: the bands, the checks on and no script rules. Two rule sets were tried and are described below.

| English, `scr` | Claude judge | GPT judge | over | AI side |
|---|---|---|---|---|
| untouched drafts | 82.3 | 87.1 | 0.00 | 3.15 |
| main | 71.6 | 82.0 | 0.30 | 2.65 |
| bands only | 73.1 | 82.2 | 0.25 | 1.50 |
| ships | 72.3 | 81.9 | 0.23 | 1.52 |

| Spanish, `scr-es` | Claude judge | GPT judge | over | AI side |
|---|---|---|---|---|
| untouched drafts | 79.4 | 84.3 | 0.40 | 2.85 |
| main | 69.5 | 79.2 | 0.85 | 2.50 |
| bands only | 70.6 | 79.6 | 0.85 | 2.17 |
| ships | 69.4 | 79.9 | 0.70 | 2.12 |

On the held-out sets: English `scr2` drafts 75.5, bands only 69.3, ships 69.1; Spanish `scr2-es` drafts 81.5, bands only 70.2, ships 69.9. Human narrations: ten held-out captions per language are judged 7.8 (English) and 8.1 (Spanish), and the judges call none of them AI. How far one version moves by itself, the difference between its two reps in the set mean: 0.7 and 1.5 on `scr` (bands only, ships), 3.4 and 3.2 on `scr2`, 2.2 and 2.8 on `scr-es`, 3.4 and 3.7 on `scr2-es`. A difference under about three points means nothing.

**What the runs showed, four findings.**

1. **The register does not move the judges beyond what the skill on `main` already did.** Ships against main: English +0.7 (worse on 13 of 20 titles, p = 0.433), Spanish −0.1 (9 of 20, p = 0.778). The bands alone against main, snapshot `bands2`: English +1.5 (worse on 9 of 20, p = 0.396), Spanish +1.1 (8 of 20, p = 0.920); with the earlier snapshot `bands`: +1.0 (p = 0.381) and −0.5 (p = 0.295). They move the meter, not the reader: AI-side features per text fell from 2.65 to 1.50 and from 2.50 to 2.17 with `bands2` (1.32 and 2.12 with `bands`). The script checks on (`ships`) against off (`bands2`) while rewriting: −0.8 and −1.1 on the development sets, −0.2 and −0.3 on the held-out ones, all inside the noise. The checks do what they are written for, and no judge sees it: staged reveals fell from 0.60 to 0.15 per 1,000 words in English. They stay on, because they cost nothing measurable. Any rewrite cuts an untouched draft by 6 to 12 points (82.3 to 72.3, 79.4 to 69.4, 75.5 to 69.1, 81.5 to 69.9), and 88% to 98% of the rewrites are still judged AI.
2. **No rule for the shape of a script held, and two attempts made it worse.** See the list below. Both attempts moved sentence length into the band and the judges rated the rewrites more AI. No `references/script.md` ships.
3. **Rewriting a script a person wrote costs it.** Ten held-out human captions per language, one rewrite with what ships: English 7.8 to 14.2 (+6.4, worse on 8 of 10, p = 0.012; GPT-6.1 Terra 8.1 to 24.6), Spanish 8.1 to 15.2 (+7.1, 8 of 10, p = 0.012; Terra 11.6 to 29.5). The rewriter shortens and evens sentences: mean sentence length 18.9 to 15.3 and 19.9 to 15.2, CV 0.606 to 0.542 and 0.634 to 0.521, against what the bands ask of narration. None went over 50. So a script a person wrote is measured and not rewritten.
4. **The rewrites that ship overshoot more than the untouched drafts.** Features past the human band per text: English 0.00 to 0.23 on `scr` and 0.10 to 0.28 on `scr2`; Spanish 0.40 to 0.70 on `scr-es` and 0.30 to 0.82 on `scr2-es`. A draft with few features past the band comes back with more of them. `main` was never run on `scr2` or `scr2-es`, so overshoot against `main` is known on the development sets only: 0.30 to 0.23 in English and 0.85 to 0.70 in Spanish.

**What was tried and did not work.** All of it on whole narrations (`eval/results/script-e2e.txt`, `script-es-e2e.txt`).

- **Rules for the shape of a script, one per measured pattern** (`references/script.md` at commit `37a1cff`: longer sentences joined with "and", "but" or "so"; fewer lists of three; repeat the plain word; more first person; no "Imagine" opening, no staged reveal, no request for comments, no "next time you", no bare-noun question, no pairs of fragments; the Spanish equivalents). Against the bands alone, the earlier snapshot `bands` (72.6 and 69.0, not the 73.1 and 70.6 of `bands2`): English 72.6 to 75.0 (+2.5, worse on 13 of 20, p = 0.117; noise 0.6; GPT judge +1.3, p = 0.012), Spanish 69.0 to 74.2 (+5.2, worse on 17 of 20, p = 0.018; noise 2.1; GPT +3.3). Overshot fell (0.23 to 0.15, 0.80 to 0.45) and the rewrites did what the rules said: sentence length 13.2 to 16.8 and 14.6 to 18.3, "Imagine" openings and staged reveals nearly gone. The judges did not follow. The decision rule, set before any number, was to ship rules that beat the bands by more than the noise on `scr` and then confirm on `scr2`; they failed on `scr`, so `scr2` was never run for them.
- **The same rules without the sentence-length bullets** (one rep, against `bands`): English +2.1 (p = 0.240), Spanish +2.0 (p = 0.205). Removing the rule that lengthens sentences removed little of the loss.
- **A short rule, "keep sentences whole, join short ones to the band median, keep the narrator's I and we"** (called `join`), against what ships. English +5.1 (worse on 16 of 20, p = 0.004; GPT +2.2, p = 0.001), Spanish +1.8 (14 of 20, p = 0.167). Sentence length reached the band (18.1 and 20.6), overshot fell (0.23 to 0.10, 0.70 to 0.45), and the judges still rated the rewrites more AI. Its text is in both e2e files. Longer sentences alone do not read as human.
- **The register alone** (the bands without any rule, against main): +1.5 and +1.1 with `bands2`, +1.0 and −0.5 with `bands`; noise either way.
- **Candidates for checks that did not ship** (`script-candidates.txt`). Out by the rule, because humans use them as much as assistants do: the promise "in this video / today we" (14% of held-out humans, 22% of assistants), a question in the first three sentences (14%, 7%), a short question answered at once (53%, 71%), runs of very short sentences (14%, 24%), "Now" or "Well" openers under 1% (33% of held-out humans, 64% of assistants), em dashes (18%, 24%). Ellipses (51% of held-out humans, 16% of assistants), the tag ", right?", "you know", "kind of" and "basically" lean human. Spanish: "en este video" (30%, 36%), "es decir" (44%, 28%), "fascinante" (11%, 8%). Counted and never proposed, because a creator's sign-off is the channel's own call: "subscribe" (8% of held-out humans, 33% of assistants), "thanks for watching" (27%, 42%), sponsor reads (29% of held-out humans, no assistant script).
- **S3 as a FAIL.** Narrowed to a request ("let us know in the comments"), it passes the rule on the held-out humans (0 of 49, and 4 of 9 Opus 5.5 scripts). It stays a TELL because 5 of the 144 train captions ask for comments and a FAIL took the train humans from 91% clean to 88%, under the 90% they had before this register. A human creator asking for comments is the channel's choice. As a TELL it still feeds S7, and S7 leans on it: without S3, three of the other five fire on 2 of 45 assistant test scripts. The first version also had a bare "in the comments", which a mention ("someone in the comments") trips.
- **Two of S1 to S6 as the combined FAIL.** It fires on 42% of assistant test scripts with no held-out human and 5 of 144 train captions; it was found after looking at the held-out row, so S7 stays at three. In Spanish two of SE1 to SE7 fails 1 of 27 held-out humans and 6 of 80 train, so it is a TELL by the rule and not shipped.
- **S1 and S4 as FAILs.** S1 would fail 6 of 9 GPT-6.1 scripts and one clean held-out human; S4 would fail Terra and Sonnet 5.5 at 3 of 9 and two held-out humans (clean held-out humans 46 to 45 and 46 to 44 of 49). In Spanish "imagina" in the first three sentences and SE4 as FAILs each cost one held-out human, and SE6's bare "en los comentarios" would fail a clean one. "No te pierdas" was dropped from SE1 for the same reason. They are TELLs.
- **Left out because the audit cannot compute them.** A closing question that repeats the title's words (0 of 49 and 2 of 144 humans, 9% of assistants in English) needs the video title, which a caption or a user's script does not carry. "So, <question>?" in the last tenth meets the TELL rule in English now (0 of 49, 4 of 144, 9%) and is in no shipped check.
- **"Piénsalo como" in Spanish.** A FAIL by the rule (no human caption, Opus 5.5 2 of 5) but it fires on 3 of 73 assistant scripts, all by one model; two test texts of one model are not evidence.

**Limits.** The judges are Claude Sonnet 5.5 and GPT-6.1 Terra and the rewriter is Sonnet 5.5, so the Claude judge shares a family with the rewriter. Each language has one human corpus of narrated explainer channels, so the bands say nothing about a tutorial, a vlog or an interview. The held-out sets have 49 and 27 human scripts. No rewrite was judged by a person. The meter reads the narration only, as the judges do, so stage directions and layout are outside every number here. `factdiff.py` reads the raw script, so a number inside a stage direction counts as a fact, and a `*Word count: ~N*` trailer fails `--source` when the narration's length changes. `check.sh` hides the meter's "too short to measure" line, so a script with under 120 spoken words shows an empty rates block and can still report a clean pass (the same happens on `main` for any short text). `spoken()` leaves some shapes alone because reading them would move the assistant-side numbers above: labels in mixed case, a direction after a label, a bare `(V.O.)`, bold section heads with timings, `**bold**[x]`, a pipe inside a table cell and `<br>`; `prose()` still takes a line after four or more whitespace characters for indented code.

Rebuild the corpus and the bands:

```
scripts/build-corpus-script.sh en ~/corpus/script      # needs yt-dlp; uses node when on PATH
scripts/build-corpus-script.sh es ~/corpus/script-es
TRAIN=$(mktemp -d); ls ~/corpus/script/*.md | awk 'NR%4!=1' | xargs -I{} cp {} $TRAIN
QUIRON_BANDS=scripts/bands-script.json python3 scripts/aimeter.py --calibrate $TRAIN \
    --ai eval/ai/script/train-gpt61,eval/ai/script/train-haiku55,eval/ai/script/train-opus55,eval/ai/script/train-sonnet55 \
    --out scripts/bands-script.json --spoken
```

The Spanish command adds `--lang es --lexicon ai-lean-es.txt --plain human-lean-es.txt`. A calibration rewrites the band file's `_corpus`, so set it back to `script-train` by hand, as the results files record. The held-out evaluation is the `evaluate.py` command at the head of the section "The shipped state, in full".

### Four counter-intuitive results

Four are counter-intuitive and cost the most to get wrong:

**High lexical diversity is an AI marker, not a virtue.** Models swap synonyms; humans
repeat the same word. Writing "the page … the page … the page" reads human. This is the
property that does not move unless you name it, so when MATTR is above band, go back and
replace synonyms with the plain repeated word. It is high in both registers.

**Connective openers and parentheses are human markers.** TextPulse measured humans
opening 3% of sentences with a connective and models told to cut them cutting them to
zero. Half the assistant blog posts had no parentheses; the median human post had four
per 1,000 words.

**In fiction, "uneven" is the AI side.** Assistant stories have shorter, more uneven
sentences and far shorter paragraphs than human ones. Applying the blog advice (vary
sentence length, add short sentences) to a story pushes it further toward the model.

**Direction depends on the register.** Contractions are lower than human in GPT blog
posts and higher than human in assistant fiction. This is why each band file carries its
own directions, learned from assistant texts of that register (`--calibrate --ai`).

### What the apparatus does on held-out texts

**What the whole apparatus does, measured.** Checklist clean means no FAIL at all.

| group | texts | checklist clean | independent judge says AI |
|---|---|---|---|
| blog: human, held out | 42 | 98% | 0% |
| blog: Claude Opus, untouched | 14 | 86% | 14% |
| blog: Claude Sonnet, untouched | 14 | 14% | 79% |
| blog: GPT, untouched | 14 | 7% | 86% |
| fiction: human, held out | 40 | 100% | 0% |
| fiction: Claude Opus, untouched | 10 | 90% | 20% |
| fiction: Claude Sonnet, untouched | 10 | 10% | 40% |
| fiction: GPT, untouched | 10 | 0% | 90% |

The same table in November 2026, with both months' training texts behind the directions
and the judge, on the rebuilt corpora (`eval/results/`):

| group | texts | checklist clean | independent judge says AI |
|---|---|---|---|
| blog: human, held out | 40 | 100% | 3% |
| blog: Claude Opus 5.5 | 14 | 71% | 100% |
| blog: Claude Sonnet 5.5 | 14 | 57% | 100% |
| blog: Claude Fable 5.2 | 14 | 93% | 93% |
| blog: GPT-6.1 | 14 | 7% | 100% |
| blog: GPT-6.1 Terra | 14 | 29% | 93% |
| blog: September Opus, Sonnet, GPT | 14 each | 71%, 0%, 7% | 64%, 93%, 93% |
| fiction: human, held out | 40 | 97% | 0% |
| fiction: Opus 5.5, Sonnet 5.5, Fable 5.2 | 10 each | 80%, 60%, 100% | 100% each |
| fiction: GPT-6.1, GPT-6.1 Terra | 10 each | 40%, 80% | 100% each |
| Spanish: human, held out | 58 | 93% | 0% |
| Spanish: Opus 5.5, Sonnet 5.5, Fable 5.2 | 10 each | 60%, 90%, 80% | 70%, 90%, 70% |
| Spanish: GPT-6.1, GPT-6.1 Terra | 10 each | 0%, 50% | 100%, 80% |

The checklist sees less of each new Claude model than of the one before: Sonnet went from
0% clean in September to 57%, and Fable 5.2 passes almost untouched. Before the November
changes Opus 5.5 was at 79% clean, Sonnet 5.5 at 79%, Terra at 36% and Fable 5.2 at the same 93%. The
word-frequency judge still separates all of them once it has seen the new models' posts,
so the difference is in which words they use, and a regex list does not hold it.

The independent judge is a word-frequency classifier trained on other human and
assistant texts, which never sees the bands or the checklist, so tuning a text to the
meter cannot fool it by construction. Claude Opus is already close to the human range
in both registers; Sonnet and GPT are not.

### What the loop does to a text

**What the loop does to a text, measured on 12 blog posts** (6 GPT, 3 Sonnet, 3 Opus),
each rewritten by an assistant following a version of this skill. *Side-by-side*: a
fresh Claude Opus judge sees the human post and the assistant post on the same title and
picks the AI one. *Alone*: fresh Opus judges see mixed human and assistant posts one at a
time and give P(AI); "judged AI" is P > 50%.

| version | checklist clean | word-frequency judge | side-by-side picked | alone: mean P(AI), judged AI |
|---|---|---|---|---|
| untouched | 25% | 67% AI | 9 of 12 | 90%, 12 of 12 |
| first version of the skill | 100% | 25% AI | 9 of 12 | – |
| second version | 100% | 42% AI | 9 of 12 | – |
| third version (specifics, structure) | 100% | 33% AI | 12 of 12 | 82%, 12 of 12 |
| third + author's voice samples | 100% | 25% AI | 12 of 12 | 81%, 12 of 12 |
| third + samples + author's notes | 100% | 0% AI | 12 of 12 | 53% and 37% in two rounds, 10 of 24 |
| final, on 8 fresh titles, with notes and samples | 100% | – | – | 68%, 8 of 8 |
| human originals | 98% | 0% AI | – | 5% to 8% across three rounds, 0 of 32 |

Read it with its limits: twelve posts per row; judge and writers are the same model
family; the human posts date from 2018 to 2021, so a judge can spot an assistant post by
an API version released later (several did, though told not to judge dates). The
side-by-side judge, who knows one text of each pair is human, kept winning on the human
post's roughness (typos, profanity, emoji, run-on paragraphs), which this skill will not
fake. The alone judges are closer to a real reader, and there only the writer's own
material moved the result: from 90% to 37% to 68% depending on the round, 18 of 32 texts
still judged AI in total. On the fresh titles the rewriter had added coined maxims, and
the judges quoted them; that is why "Do not coin maxims" is now a rule. The honest
summary: the writer's material is necessary, the style rules keep it from sounding
generated, and neither makes a text indistinguishable from the writer's own rough post.

`scripts/evaluate.py` reruns all of this:

```
python3 scripts/evaluate.py --human CORPUS \
    --ai-train eval/ai/blog/train,eval/ai/blog/train-2026-11 \
    opus=eval/ai/blog/test-opus sonnet=eval/ai/blog/test-sonnet gpt=eval/ai/blog/test-gpt \
    opus55=eval/ai/blog/test-opus55 sonnet55=eval/ai/blog/test-sonnet55 \
    fable52=eval/ai/blog/test-fable52 gpt61=eval/ai/blog/test-gpt61 terra=eval/ai/blog/test-terra
```

### What the rewrite adds: the September 2026 rounds

A second end-to-end protocol, run on version 1.1.0 and each candidate change. 20 titles
(the 12 e2e titles and the 8 fresh ones), each rewritten three times from the assistant
draft and the author's notes by Claude Opus 5.5 running headless with the skill. Every
rewrite is read alone by three fresh Claude Opus 5.5 judges and two GPT-5.6 judges
(through the Codex CLI), each giving P(AI) with no hint that AI was involved. On the same
judges the human originals score 4.5 (Opus) and 6.5 (GPT), and the untouched drafts 88.5
and 92.9. Differences are per title, paired, with a Wilcoxon signed-rank test.

| version | Opus mean P(AI) | judged AI (Opus) | GPT mean P(AI) | vs 1.1.0 |
|---|---|---|---|---|
| 1.1.0 | 47.8 | 52% | 20.1 | – |
| sincerity markers named, *really* and *actually* out of the plain-word list | 45.7 | 45% | 19.7 | -2.0, p = 0.08 |
| build from the notes, drop the draft's scaffolding | 43.3 | 35% | 18.3 | -4.5, p = 0.09 |
| both, plus end sections on a fact and leave no trace of the draft (1.2.0) | 39.1 | 25% | 15.7 | -8.7, better on 18 of 20 titles, p = 0.001; GPT -4.3, p = 0.001 |
| no named plain-word list ("swap, never add") | 48.2 | 50% | 20.1 | +0.5, p = 0.72, not shipped |
| 1.2.0 plus the cold read (a fresh agent's reasons, acted on once) | 34.9 | 13% | 14.0 | -4.2 against 1.2.0, p = 0.055; GPT -1.8, p = 0.12 |

On 18 held-out titles never used to choose anything (two rewrites each), 1.2.0 against
1.1.0: Opus 36.7 to 31.8 (-4.9, better on 12 of 18, p = 0.055), GPT 15.1 to 14.6 (p =
0.42); human originals 5.0 and 6.5. With Claude Sonnet 5 as the rewriter (one rewrite per
dev title), 1.2.0 against 1.1.0: Opus 51.7 to 43.8 (-7.9, p = 0.07), GPT 18.7 to 15.5
(-3.2, p = 0.04), so the change is not specific to Opus. Nor to Claude: with GPT-5.6 through the Codex CLI as the rewriter, pointed at
SKILL.md (one rewrite per dev title, two Opus judges), the current version against 1.1.0
went from 67.0 to 55.3 (-11.6, p = 0.002; judged AI 100% to 75%). The same version
rewritten by Claude Opus scores 34.9, so the skill does most for the model it was tuned on. In Spanish, on the 30 Spanish test titles (dev.to posts in
Spanish before 2022, notes in Spanish, one rewrite each), the current version against
1.1.0: Opus 38.8 to 29.2 (-9.6, better on 24 of 30, p < 0.001), judged AI 20% to 3%; GPT
22.2 to 20.1 (p = 0.08). Human originals 5.2 and 10.7, untouched drafts 85.5 and 89.1.

The cold read on the 18 held-out titles, against 1.2.0 without it: Opus mean 31.8 to 31.5
(p = 0.95), but texts judged AI fell from 17% to 3%, and GPT 14.6 to 11.7 (-2.9, p =
0.001). Pooled over all 38 titles: Opus -2.3 (p = 0.16), GPT -2.3 (p = 0.001). The GPT
judges share no family with the rewriter or the cold reader, so the gain is not the
rewriter learning to please its own kind. It costs about a third more per rewrite (0.52
against 0.39 USD) and left the meter where it was. The meter did not move (checklist clean on 100% of
both, overshot 1.83 and 1.85 features per text), and rewrites with a figure or link in
no source fell from 4 of 60 to 1 of 60.

November 2026, two rewrites per title, two Opus judges and one GPT judge. The current
version against the same rewriter given the same draft and notes and one sentence of
instruction instead of the skill ("rewrite the text so it reads naturally, the way the
writer would write it; keep every fact from the notes and add none"): on the 20
development titles Opus 32.0 against 44.0 (-12.0, better on 18 of 20, p = 0.001), GPT 16.4
against 22.3 (p = 0.022); on the 18 held-out titles Opus 26.7 against 32.1 (better on 14
of 18, p = 0.011), GPT 14.0 against 16.2 (p = 0.025). The notes alone do not explain the
result. Given a human post as the draft instead (14 pre-2022 dev.to posts outside every
set, no notes), the rewrite read slightly more AI than the original: Opus 6.0 to 7.5
(worse on 8 of 14, p = 0.056), GPT 6.4 to 7.9 (p = 0.09). Two more posts were not
rewritten, because the skill stopped to ask for the notes. On a text a person wrote, the
loop costs a little.

Where the rules came from. The judges' 288 reasons for calling a 1.1.0 rewrite AI,
grouped: human cues present (70, counter-evidence), uniformly tidy prose (63), a line that
wraps a section up or a stock hand-off (58), safety and best-practice caveats nobody
asked for (23), draft residue such as `GIF_URL_HERE` (13), inserted voice ("Quite a lot,
honestly.", 10), tutorial scaffolding around the writer's story (18), a note about when
the post was written (6). And a word-frequency classifier trained on 175 human posts
against 128 of the skill's rewrites, with only words found in at least eight titles on
both sides, told them apart perfectly (leave-one-title-out AUC 1.00) on the rewriter's own
overshoot: *so* at 6.7 per 1,000 words against 4.0, *lot*, *too*, *back*, *gets*,
*honestly* (in 33% of rewrites, 2% to 5% of human posts, none of the notes); shorter
sentences (15.4 against 18.9 words); fewer semicolons, parentheses, questions,
exclamation marks and *we*. Taking the plain-word list out of the instructions did not
change that, so it stays; what moved the judges was content and structure.

### The November 2026 rounds: three instructions that did not ship

A cheaper panel, checked against the Opus one first. Claude Sonnet 5.5 rewrites, two
Sonnet 5.5 judges and one GPT-6.1 Terra judge read each rewrite alone. On 58 texts the
Opus judges had already scored (18 human posts, 20 rewrites, 20 untouched drafts), Sonnet
gave 4.8, 12.4 and 79.2 and Terra 6.3, 46.1 and 91.9, against 5.9, 32.2 and 87.8 from Opus:
the same order, with Sonnet easier on rewrites and Terra harder. With this rewriter and
panel the current version scores 15.0 (Sonnet) and 50.0 (Terra) on the 20 development
titles and 13.2 and 49.6 on the 18 held-out ones, two rewrites per title.

How far one version moves by itself, from the cached rewrites: between two reps of the
same snapshot the set mean differs by 0.1 to 3.1 points with the Opus panel and by 0.6
and 2.1 with the Sonnet one, and one title differs by 5 to 14 points (standard
deviation). A change that moves the mean by less than about three points has to show up
on both sets and both judges to count.

Three instructions were measured against that baseline, on both sets.

- **Order and ending from the notes.** A structure-only classifier separates assistant
  blog posts from human ones at 97.0 macro-F1, and at 96.1 after each post is reworded
  (SlopShape 2026); its strongest signals are an ending that restates the thesis, a
  synthesis stage and a thesis placed before the first section. The instruction: before
  writing, take from the notes the last fact (the post ends there), the place of the main
  point, and the dates and links, and add no stage the notes lack. Development titles:
  Sonnet 15.0 to 13.1 (worse on 5 of 20, p = 0.018), Terra 50.0 to 46.3 (p = 0.098).
  Held-out titles: 13.2 to 12.3 (worse on 9 of 18, p = 0.64) and 49.6 to 46.7 (p = 0.31).
  Pooled over the 38 titles, -1.5 (p = 0.061) and -3.4 (p = 0.048). The overshot count went
  from 1.83 to 2.03 features per text (higher on 18 titles, lower on 9, p = 0.19) and
  rewrites with a figure or link in no source from 3 to 5 of 76. A gain the size of the
  rep noise, not significant on the held-out titles, with overshoot no rarer: not shipped.
- **Undoing the overshoot.** On top of that, an instruction to read the `overshot` rows
  and put back the exact word or the adverb the rewrite had taken out. Overshot rose
  instead, to 2.19 (higher on 19 of 38 titles, lower on 6, p = 0.008). Terra fell by 11.5
  on the development titles (p = 0.001) and by 2.1 on the held-out ones (p = 0.62); Sonnet
  did not move on those (+0.0). Not shipped.
- **Leaving a human text alone.** Measure the draft first; with no notes and no FAIL,
  change only a TELL you would rule against. On 16 human posts given as drafts with no
  notes, the originals score 5.5 and 6.4, the current version's rewrites 6.5 and 8.2, and
  with the rule 5.7 and 6.9 (Sonnet -0.8, worse on 2 of 16, p = 0.15; Terra -1.3, p =
  0.31). On the 20 development drafts with the notes withheld it changed nothing: 67.0 to
  65.2 and 81.7 to 82.5. No measurable gain: not shipped. With Sonnet 5.5 rewriting, the
  loop costs a human text about one point, less than the 1.5 measured with Opus.

Rewriting without the notes leaves a draft where it was: 67.0 and 81.7 against 79.2 and
91.9 untouched, and 15.0 and 50.0 with the notes.

The November changes that did ship touch the meter and the checklist, not the
instructions: the band directions from both months, four lexicon words and the Spanish
bold-label check. Rewrites made with them were judged like the ones before. Development
titles: Sonnet 15.0 to 15.5 (p = 0.72), Terra 50.0 to 47.7 (p = 0.43). Held-out titles:
13.2 to 13.4 (p = 0.67) and 49.6 to 47.9 (p = 0.74). The 30 Spanish titles, one rewrite
each: 13.8 to 14.3 (p = 0.55) and 45.7 to 45.0 (p = 0.80). Overshot per text, 1.83 to 1.99
(higher on 15 of 38 titles, lower on 9, p = 0.15). They change what the checklist catches
in a draft, and they do not change what a reader makes of the rewrite.

Three instructions aimed at what blind judges and the 2026 literature name, and none
cleared the noise on the held-out titles. Together with the candidates below, that is
where the instructions stand: what still separates a rewrite from a human post is not
something another sentence in SKILL.md has moved.

### Fiction

The same protocol on WritingPrompts replies, rewritten with no notes (invented detail is
the task in fiction), one rewrite per story, two Opus judges. The version with the blog
changes barely moved stories against 1.1.0 (77.6 to 75.5 on 30 stories, every story still
judged AI; human replies 7.7). The judges' 873 reasons were about the story's shape:
callbacks and bookends (about 300), a clockwork arc (180), even polish (150), placed props
(120), a stated moral (100), similes at a steady rate (90). `references/fiction.md` turns
those into edits. Against the version without it: 75.2 to 69.3 on the 30 stories the
rules came from (better on 25), 74.0 to 69.7 on 32 held-out stories (better on 30, p <
0.001). On the meter, the word-frequency judge fell from 44% to 31% AI and the overshot
count rose from 0.84 to 1.02, still under the held-out humans' 1.2. A second round aimed at what the
judges still named (the rules had turned bookends into a quiet mundane last line in most
stories; one restrained, wry register across all of them) did not move them: 69.3 to
70.0, worse on 18 of 30. What is left is the premise and plot the draft chose.

### Checks measured and not shipped

Each of these was measured with the same held-out split and left out, so it is not
proposed again without new evidence. Human corpus: 176 dev.to posts (44 held out), rebuilt
in September 2026.

- **Stock phrases** (2 to 4 words, chosen on the training split). Phrases in at most 4% of
  human and at least 10% of assistant training posts: 41% of held-out human posts carry
  three or more, so the list flags people. Phrases in no human training post: AUC 0.53 to
  0.57 against held-out assistant posts, close to chance. Rewrites by the skill already sit
  at the human level on both lists (AUC 0.45 to 0.50).
- **Length as verbosity.** Opus 5.5 and Sonnet 5 asked for a dev.to post with no length
  wrote 1.41 and 1.27 times the words of the human post on the same title (AUC 0.67 and
  0.59, 25 posts). The extra is code and headings: prose alone was shorter than the
  human's (0.70 times), with shorter sentences. Headings are already a band; a length rule
  has no human text to compare a single post against.
- **Negated setup (A1c)**: a sentence of 12 words or fewer that only denies something,
  opening a paragraph or followed by the reframe ("What surprised me most wasn't a
  number."). As a checklist item it looked right: 7% of held-out human posts, 31% of
  assistant posts, held-out humans still 0% T1 FAIL, T1 FAIL on GPT posts from 7% to 36%.
  End to end it made rewrites worse. 20 titles (8 fresh), 52 rewrites per version, two
  fresh Opus judges each: mean P(AI) 43.6 without the check and 46.4 with it, higher on 13
  of 20 titles (Wilcoxon p = 0.036); on the fresh titles 34.6 against 40.5. The countable
  rates did not move. Many of the sentences it removed were ordinary ones from the
  author's notes ("The page isn't finished yet."), and the judges' reasons for the
  rewrites with the check were "too even" and "uniformly polished". It is kept as a review item
  the writer rules on (`audit.py --review`), outside the loop, T1 and `check.sh`. With
  that version of the skill, 40 more rewrites of the same 20 titles (two per title,
  headless, so no review questions) gave mean P(AI) 43.7 against 43.6 without it (+1.3
  per title, 95% CI -2.0 to +4.7, Wilcoxon p = 0.42), and the countable rates did not
  move. Negated setups were left in 5 of 40 rewrites, against 11 of 52 before.

- **Semantic redundancy** (the same claim twice within three sentences; Jakesch et al.
  2023 found it the most valid reader cue). On 2026 text it points the other way: human
  posts repeat more than assistant posts (AUC 0.24 to 0.37 against held-out humans).
- **Eight features from the 2024 to 2026 stylometry literature** (concessives, downtoners,
  adjective pairs, synthetic negation, ", which" relatives, personal asides, discourse
  particle openers, a prescriptive last paragraph): AUC 0.40 to 0.60 on 2026 assistant
  posts, close to chance.
- **Claude's chat words** from forums (*load-bearing*, *footgun*, *blast radius*, *the
  crux*, *the tell*): in no human or assistant blog post. They belong to chat and agent
  output, not this register.
- **A worked before/after example in SKILL.md** (a notes-built paragraph from a title
  outside every test set; Anthropic's guides call examples the most reliable way to steer
  Claude's style). On the 20 development titles it looked like a gain over the cold-read
  version (Opus -2.4, p = 0.06; GPT -2.1, p = 0.03). On the 18 held-out titles it was not:
  Opus +0.4 (p = 0.85), GPT +1.5 (p = 0.02, worse). No phrase of the example was copied.
- **Three more instructions from the judges' remaining reasons**, each against the
  cold-read version on the 20 development titles: colon lead-ins, clipped comment
  sentences and code retold in prose (Opus -1.9, p = 0.35; GPT -0.6); letting the notes set
  the length, since longer rewrites of the same title were judged more AI (r = 0.45 across
  479 rewrites; the instruction cut length 12%, Opus -2.0, p = 0.26; GPT 0.0). Neither
  moved the judges enough to ship. Style features such as plain words, contractions,
  sentence-length variation and lexical diversity had no within-title correlation with
  the judges' P(AI) (|r| < 0.13).
- **A condensed SKILL.md** (352 lines, a fifth fewer words, the evidence moved to the
  references): the same judges' P(AI) as the full file (35.2 against 34.9, p = 0.91) and
  the same cost per rewrite (0.52 USD, 13 turns), so it bought nothing measurable.
- **Placeholders and date notes as checklist items**: in 12 and 10 of 176 human posts
  (placeholders in code, "at the time of writing"), so they stay instructions only.
- **November 2026, the current models' own tells.** Graphite's zero-human trigrams for
  Claude Opus 5.5 ("this matters because", "taken together these", "the takeaway is",
  "just as importantly", "helps to understand") are in no human post here and in 0% to 14%
  of any assistant group, 2% of the November training posts: they belong to Graphite's
  article-from-a-brief prompt. The 2026 contrast forms ("not simply", "rather than
  merely", "less like X, more like Y", "without sacrificing") are each in 0% to 7% of the
  November groups. *Real* and *actual* as emphasis ("the real problem"), which readers
  of Claude name, is in 15% of held-out human posts and 43% to 50% of the Opus 5.5,
  Sonnet 5.5 and Fable 5.2 posts; as a TELL it raised the checklist AUC (Opus 5.5 0.71 to
  0.74) and made one held-out human post fail T1, and the rewrites already carry it less
  often than people (12%). *Matters* failed the same way (`references/word-choice.md`).
  A list of quoted spans that are in no source, for `factdiff.py`: 8 flagged in 76
  rewrites, 6 of them the text between two quotations. Rewrites of different titles do not
  share openings (the commonest three words open 4 of 40), so SlopBench's same-prompt
  measure has nothing to count here.
- **November 2026 upstream intake** (slop-score, Antislop, unslop, humanize, humanizer,
  stop-slop, no-ai-slop, avoid-ai-writing), on the rebuilt corpus (160 dev.to posts, 40
  held out; 157 stories; 245 Spanish posts). A cross-sentence contrast with any subject
  ("The hardest part wasn't X. It was Y.") raised the checklist AUC (0.860 to 0.873) and
  left held-out humans unflagged, but end to end it made rewrites worse on the development
  titles (Opus 32.0 to 34.0, p = 0.28; held-out 26.7 to 26.1). A feature for paragraphs
  that open on a word from the intro separated AI posts (AI-side AUC 0.879 to 0.881 blog,
  0.829 to 0.849 Spanish) and also made rewrites worse (Opus +1.8 dev, +2.4 held-out). Word
  lists: of 2,779 upstream entries one passed for blog; the fiction survivors flagged one
  more human story on held-out and on 117 fresh stories (FAIL 8.5% to 9.4%), and none of
  2,529 Antislop phrases passed. No gain or more humans flagged: plain "not X, but Y"
  (A1b on held-out humans 12.5% to 27.5%), "No X, no Y, no Z" chains (one held-out story),
  wider A9, A12, A16, A17 and A21/A22 phrase lists (no hits, or more human hits), a Title
  Case filter (A19 stopped catching AI), a proximity gate on A1, short self-answered
  questions, fillers ("in terms of", in 14% to 20% of human posts), bare-noun bullet
  lists, and features for staccato runs, callbacks, n-gram repetition, specific anchors,
  bold, punctuation spread, function-word entropy and paragraph uniformity. A copy gate
  against voice samples fired on 7 of 19 rewrites, all of them the author's own sign-off,
  which the notes also held.

### Calibrating for another register

**Calibrating for another register.** Academic prose, news, email and other languages
are different distributions, and the wrong band file sends you in the wrong direction.
Collect 30 or more texts you know are human in the target register, by several authors,
ideally before 2023, one file each, and if you can, 20 or more assistant texts of the same
kind; then:

```
python3 scripts/aimeter.py --calibrate HUMAN_DIR --ai AI_DIR --out bands-mine.json
QUIRON_BANDS=bands-mine.json python3 scripts/aimeter.py FILE
```

Without `--ai` the defaults in `AI_REF` apply: directions from the literature, checked
on blog posts. `--out` defaults to the
shipped `bands.json`, so name a new file.

A register whose texts carry markup around the words, such as stage directions and speaker
labels in a script, needs `--spoken`: the band file is then marked `"_spoken": true` and the
meter and the checklist read only the spoken words. Check which punctuation features depend
on whoever transcribed the text with `eval/script_channels.py`, which prints each channel's
median beside the AI median, and put the ones most channels do not separate in `_skip`
(video scripts, above).

## Part D: what this does not do

In the TextPulse prompting study, all 120 AI texts under every prompt from every model
received a GPTZero document AI probability of 1.00, including the texts that scored past
the human median on the 47-feature spectrum. All ten human passages received 0.00.

Surface stylometry and probability-based detection read different things. A detector
like GPTZero reads the probability of each token under a language model. A model asked
to write unevenly produces an uneven text whose every token is still the token that
model would produce.

So this skill makes text that reads as a person wrote it and that measures inside the
human range on every countable property. It does not defeat a perplexity-based detector,
and no prompt tested in the literature does.

Nor do style edits reach what conditioning on a writer does. In Chakrabarty et al.
(2026), cliché density explained only 16.4% of the penalty expert readers gave AI text;
most of the rest went away only when the model had learned from the writer's own work.
On this skill's blind test, the loop moved every measured rate into the human band and
did not change which post a strong model judge picked as AI (Part C).

A text Claude writes also carries a watermark. Claude models released since 2 August
2026 (older ones over the following months) pick among equally good words with a keyed
random source, the SynthID-Text method, so Anthropic's detection API can estimate that
Claude was involved. Nothing is visible and no style edit touches it: light editing leaves
it, a rewrite where every word changes removes it, and it is thin where Claude only
proofread a human text (Anthropic, *How Claude's text watermarking works*, 2026). This is
one more reason the writer's own words beat a rewrite.

One limit of the meter itself. `aimeter.prose()` drops a line that starts with four or
more whitespace characters, to skip indented code, and the match runs across line breaks:
four blank lines in a row, or a few blank lines with spaces in them, make it drop the line
after them, in every register. `spoken()` closes those runs in its own output, so scripts
are not affected, and `prose()` is left as it was so that the other bands keep measuring
what they measured.

Two more limits. Stylometric classifiers reach 86% to 90% accuracy at population scale
but produce unreliable individual verdicts: in TextPulse's classification study,
catching 99% of AI texts cost flagging 68% of human ones. And readers are no better:
blinded academic raters identified AI text 19% of the time (Cheng et al. 2025), while
people who use chatbots daily for writing caught 92.7% of AI articles (Russell et al.
2025). The skill writes for the second reader.

# Part C: the numbers

The bands, the AI directions, what the whole apparatus does on held-out texts, how to calibrate for another register, and what the skill does not do. Read it when a meter verdict surprises you or the text is in a register the shipped bands do not cover.

## Contents

- Where the numbers come from
- Blog bands
- Fiction bands
- Four counter-intuitive results
- What the apparatus does on held-out texts
- What the loop does to a text
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

### Blog bands

**Blog posts** (`bands.json`), 42 held-out human posts against 42 assistant posts. AUC is
the chance an assistant post sits further to the AI side than a human post; 0.5 is no
signal. *Either* means the direction was too weak on the training split to score, so
only the band applies.

| feature | human p10–p90 | AI median | AI side | AUC |
|---|---|---|---|---|
| sentence-length CV | 0.43 – 0.72 | 0.51 | lower | 0.64 |
| mean sentence length | 14.1 – 24.4 | 15.6 | lower | 0.62 |
| long words (7+) /1k | 160 – 250 | 253 | higher | 0.78 |
| mean word length | 4.3 – 4.9 | 4.9 | higher | 0.81 |
| nominalizations /1k | 7.3 – 32.6 | 26.7 | higher | 0.67 |
| -ly adverbs /1k | 4.8 – 19.2 | 16.0 | higher | 0.68 |
| passive voice /1k | 1.9 – 11.3 | 4.0 | lower | 0.67 |
| lexical diversity MATTR-50 | 0.763 – 0.850 | 0.850 | higher | 0.85 |
| first person /1k | 8.6 – 65.2 | 4.3 | lower | 0.79 |
| contractions /1k | 10.4 – 37.0 | 19.2 | either | – |
| questions /1k | 0 – 6.5 | 0 | lower | 0.55 |
| repeated openers /100 | 0 – 11.9 | 3.5 | lower | 0.56 |
| connective openers % | 0 – 14.3 | 3.3 | either | – |
| commas /1k | 25.1 – 58.0 | 56.2 | higher | 0.83 |
| semicolons /1k | 0 – 3.4 | 0 | lower | 0.60 |
| em dashes /1k | 0 – 2.7 | 1.1 | higher | 0.74 |
| AI-lexicon words /1k | 0 – 1.4 | 1.0 | higher | 0.69 |
| lists of three /1k | 0 – 5.5 | 7.2 | higher | 0.86 |
| participial clauses /1k | 0 – 2.3 | 1.6 | higher | 0.64 |
| plain words /1k | 43 – 95 | 55 | lower | 0.63 |
| parentheses /1k | 0 – 11.0 | 0 | lower | 0.67 |
| words per paragraph | 23.5 – 74.2 | 34.8 | either | – |
| headings /1k | 0 – 17.1 | 12.2 | higher | 0.75 |

### Fiction bands

**Fiction** (`bands-fiction.json`), 40 held-out human stories against 30 assistant stories.
The strongest features: headings (a title line on the story; no human story had one,
AUC 0.83), words per paragraph (human 26 – 106, AI median 22.5, lower, AUC
0.81), em dashes (human 0 – 0, AI 2.4, 0.79), sentence-length CV (0.45 – 0.76, AI 0.69,
*higher*, 0.77), lexical diversity (0.839, 0.77), contractions (*higher*, 0.75), mean word
length (0.73), commas (0.72). One learned direction did not hold up: nominalizations
looked higher in the training stories (0.61) and were lower in the held-out ones (0.38).

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
python3 scripts/evaluate.py --human CORPUS --ai-train eval/ai/blog/train \
    opus=eval/ai/blog/test-opus sonnet=eval/ai/blog/test-sonnet gpt=eval/ai/blog/test-gpt
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

Two more limits. Stylometric classifiers reach 86% to 90% accuracy at population scale
but produce unreliable individual verdicts: in TextPulse's classification study,
catching 99% of AI texts cost flagging 68% of human ones. And readers are no better:
blinded academic raters identified AI text 19% of the time (Cheng et al. 2025), while
people who use chatbots daily for writing caught 92.7% of AI articles (Russell et al.
2025). The skill writes for the second reader.

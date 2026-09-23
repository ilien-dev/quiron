# Part C: the numbers

The bands, the AI directions, what the whole apparatus does on held-out texts, how to calibrate for another register, and what the skill does not do. Read it when a meter verdict surprises you or the text is in a register the shipped bands do not cover.

## Contents

- Where the numbers come from
- Blog bands
- Fiction bands
- Four counter-intuitive results
- What the apparatus does on held-out texts
- What the loop does to a text
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

Two more limits. Stylometric classifiers reach 86% to 90% accuracy at population scale
but produce unreliable individual verdicts: in TextPulse's classification study,
catching 99% of AI texts cost flagging 68% of human ones. And readers are no better:
blinded academic raters identified AI text 19% of the time (Cheng et al. 2025), while
people who use chatbots daily for writing caught 92.7% of AI articles (Russell et al.
2025). The skill writes for the second reader.

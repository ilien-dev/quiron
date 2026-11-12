# Part C: the numbers

The bands, the AI directions, what the whole apparatus does on held-out texts, how to calibrate for another register, and what the skill does not do. Read it when a meter verdict surprises you or the text is in a register the shipped bands do not cover.

## Contents

- Where the numbers come from
- Blog bands
- Fiction bands
- Work registers: pull requests, commit messages, READMEs, email
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

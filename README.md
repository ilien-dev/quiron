<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/hero/quiron-hero-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/brand/hero/quiron-hero-light.png">
    <img alt="Quirón: a centaur holding up an eight-point star" src="assets/brand/hero/quiron-hero-light.png" width="720">
  </picture>
</p>

<p align="center">
  <b>A writing skill for AI models. It strips the habits that mark prose as machine-written,<br>
  then checks the result against measured human writing instead of a hunch.</b>
</p>

<p align="center">
  <img alt="Python 3 standard library only" src="https://img.shields.io/badge/python-3%20stdlib%20only-20201E?style=flat-square">
  <img alt="Registers: blog, fiction, Spanish" src="https://img.shields.io/badge/registers-blog%20%C2%B7%20fiction%20%C2%B7%20es-B5563A?style=flat-square">
  <img alt="Claude Code skill" src="https://img.shields.io/badge/Claude%20Code-skill-F7EEDB?style=flat-square&labelColor=20201E">
</p>

---

> [!IMPORTANT]
> **Use it responsibly.** Quirón is for text you write for yourself or your own team: a
> how-to guide, internal docs, meeting notes, a draft nobody outside the company will
> read. The point is text that feels close and easy to read, not text that pretends a
> person wrote it.
>
> Do not use it to pass AI writing off as human in public: social media, published
> articles, schoolwork, reviews, job applications, anything where the reader has a right
> to know who wrote it. Never use it to deceive or defraud anyone. It also does not beat
> AI detectors that read token probabilities, and it was not built to.

## What it does

Ask a model for a blog post and you get a recognisable shape: lists of three, a dash in
every paragraph, a heading every hundred words, a quotable line to close each section,
words like *seamless* and *robust*. Quirón gives the model a checklist of 33 such
patterns and a meter that says, in numbers, whether the fix landed or went too far.

Here is the meter on an assistant-written Stripe tutorial from `eval/ai/blog/`:

```text
$ python3 scripts/aimeter.py eval/ai/blog/e2e-raw/aspittel-782713.md

feature                   this   human band      verdict
long words (7+) /1k     353.83   159.68 - 250.46  above band, AI side
nominalizations /1k      55.21     7.29 - 32.65   above band, AI side
em dashes /1k             3.76     0.00 - 2.74    above band, AI side
lists of three /1k       11.29     0.00 - 5.51    above band, AI side
plain words /1k          33.88    43.19 - 95.24   below band, AI side
...
13/23 features inside the human band (p10-p90 of 167 human texts)

! triads: retries, cancellations, and preventing, refund, tax, and privacy
```

The rewrite of the same post, built from the author's own notes, scores 23 of 23.

## What backs it

Every rule and number traces to a published study or to a run of the scripts in this
repo. Nothing ships on "this reads better".

- **Human baselines.** The bands come from 167 dev.to posts and 157 WritingPrompts
  stories, all written before ChatGPT existed, plus a Spanish set. A quarter of each is
  held out and never used to pick anything.
- **2026 AI text on the same titles.** Claude Opus, Sonnet, Haiku and GPT wrote the
  comparison texts in `eval/ai/`, from the plain prompt a user would type.
- **Two failure modes.** Text can sit on the AI side of a band or *overshoot* past the
  human side. Overshoot is a tell too: models told to "write like a human" go choppier
  and plainer than any person does. The meter flags both.
- **Blind judges.** Fresh model judges read posts one at a time and guessed which were
  AI. That test produced the most important finding below.

How each number was measured, and where every rule comes from, is in [`SKILL.md`](SKILL.md) and
[`eval/README.md`](eval/README.md).

## Tips for text that reads human

The judges were not fooled by style edits alone. A rewrite that put every rate inside
the human band was still judged AI 12 times out of 12. What moved them was the writer's
own material. So:

- **Start from something real.** Your notes, a rough draft, a Slack thread, a post-mortem.
  A model writing from a blank prompt has to invent everything, and invented text reads
  invented.
- **Give it the specifics.** What happened, the real names, the numbers you know, the
  links, what went wrong. These are what readers notice.
- **Say what you think.** Your opinion, what you are unsure of, the mistake you made.
  The model cannot supply that without making it up.
- **Hand over a sample of your writing** so the model can match how you write.
- **Stop at the human range.** Two or three passes of the meter is normal. Chasing 23 of
  23 is how you overshoot.

## The name

Chiron (*Quirón* in Spanish) was the one centaur in Greek myth known for wisdom rather
than violence. He taught Achilles, Asclepius and Jason, and he healed. When a poisoned
arrow wounded him, his immortality meant he could not die from it, so he gave it up,
and Zeus set him among the stars. The logo shows him holding that star.

He fits the skill in two ways. He was a teacher of people, and this skill teaches a
model how people write. And he was half man, half horse: the text Quirón helps produce
is a hybrid too. The model does the drafting, and the human part has to come from you.

## Install

```sh
git clone <this repo> quiron
ln -s "$PWD/quiron" ~/.claude/skills/quiron
```

Then ask Claude Code to write or rewrite something, or call `/quiron`. The scripts run
on their own too:

```sh
python3 scripts/aimeter.py FILE        # 23 rates against the human bands
python3 scripts/audit.py --brief FILE  # the pattern checklist
scripts/check.sh FILE                  # one pass of the full loop
```

For fiction or Spanish, set `QUIRON_BANDS=scripts/bands-fiction.json` or
`scripts/bands-es.json`. Texts under about 120 words get no measurement.

## License

Free to use, copy and change, under the [GNU AGPL v3](LICENSE) with one added term
in [`NOTICE`](NOTICE). Any work built on Quirón has to stay open under the same license,
including a modified version offered as a network service, and has to credit the
original: "Based on Quirón by ilien", with a link to this repository.

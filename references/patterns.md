# Part A: structural patterns

The 33 patterns `scripts/audit.py` checks, with the measured rate for each and the fix. SKILL.md has the one-line index; read the entry here when a check flags it or you are unsure how to fix it.

## Contents

- 1. Not X but Y [TELL]
- 2. One-line closers and dramatic fragments [READ, TELL]
- 3. Sayings that sound deep [TELL; READ for "X is the Y of Z"]
- 4. Staged run-up before the point [TELL]
- 5. Arguing with no one [TELL]
- 6. Lists of three [rate, READ]
- 7. Repeated sentence openings, and the measured correction
- 8. Dashes [TELL, rate]
- 9. Stacked qualifiers [TELL]
- 10. Hyphenated pairs after a noun [TELL]
- 11. Passive voice [rate]
- 12. Inflated significance [TELL]
- 13. Vague connection [READ]
- 14. -ing clauses tacked on after a comma [TELL, rate]
- 15. Sales language [TELL]
- 16. Borrowed authority [TELL]
- 17. Avoiding is, are and has [TELL]
- 18. Bold labels on list items [READ]
- 19. Headings [TELL]
- 20. Curly quotes [TELL]
- 21. Chatbot residue [FAIL]
- 22. Knowledge-limit disclaimers [FAIL]
- 23. A heading repeated in the first sentence [READ]
- 24. Writing about the previous version [READ]
- 25. Structural uniformity [READ]
- 26. The summary section at the end [TELL]
- 27. Stock names [TELL]
- 28. Abstract "a mix of" bundles [TELL]
- 29. Stock sensory clichés, mostly fiction [TELL]
- 30. Showing, then explaining what it meant [READ]
- 31. Generic where a specific exists [READ]
- 32. Announcing what the post will cover [TELL]
- 33. Too many headings [rate]

Rates below are from this skill's run: the share of 167 pre-2022 dev.to posts (human)
and of 90 assistant posts written in 2026 on the same kind of titles (AI) in which
`audit.py` finds the pattern at least once.
State in brackets is what `audit.py` reports.

### 1. Not X but Y [TELL]

**Watch for:** it's not X, it's Y; not just / not only / not merely X, but Y; X rather
than Y; the contrast split across two sentences ("This does not mean X. It means Y.");
the clipped negative tail ("…, no guessing", "That's a favor, not a liability."); the
negated setup, a short sentence that only denies something, opening a paragraph or right
before the point ("What surprised me most wasn't a number.").
**Measured:** the family is in 38% of assistant training posts and 18% of human ones; "rather
than" alone was in 35% and 8% on the training split. "It's not X, it's Y" is in 5% of
human posts and 9% of assistant ones, so it cannot fail on sight. Across 22 models the
slop-score benchmark (Paech 2025) finds the construction at 2 to 13 times the human rate;
the rate, not a single use, is the tell. The negated setup is in 7% of held-out human posts
and 31% of assistant ones, but fixing it inside the loop made rewrites read more AI to
blind judges, so it is a review item only: `audit.py --review` lists it and the writer
decides (SKILL.md, "Review with the writer"). Blog bands only.
**Why it fails:** the negative half names something nobody claimed, so the positive half
sounds larger. It adds weight without adding a claim.
**Instead:** state the point. Keep the contrast only when the negative half corrects a
belief the reader actually holds, or when both halves carry information.

> It's not just about the beat riding under the vocals; it's part of the aggression.
> → The heavy beat adds to the aggressive tone.

### 2. One-line closers and dramatic fragments [READ, TELL]

**Watch for:** a one-sentence paragraph restating the paragraph above it; "That is the
real win."; "Read that again."; the same closer after several sections; a row of
fragments in running prose ("No aesthetic prior. No nostalgia."); every.single.word.
**Measured:** a short closing paragraph that shares words with the one above is in 27%
of human posts, so it is a READ, never a FAIL. Short list items are not fragments and are
not counted.
**In fiction it is the main tell.** Assistant stories average 29 words per paragraph
against 45 for human ones (AUC 0.72 on the training split), and fragment rows are in
28% of them against 13% of human stories. The paragraph that is one short line, again
and again, is how a model paces a scene.
**Instead:** cut a closer that repeats. A short sentence can carry emphasis when it
carries a new fact. Merge a row of fragments into a sentence with a specific claim.

### 3. Sayings that sound deep [TELL; READ for "X is the Y of Z"]

**Watch for:** the real question is, at its core, in reality, what really matters,
fundamentally, the deeper issue, the heart of the matter, X is the Y of Z, X becomes a
trap, the language of, the architecture of.
**Measured:** in 2% of posts on either side. Cheap to check, rare in 2026 output.
**Instead:** replace the saying with the specific claim underneath it.

### 4. Staged run-up before the point [TELL]

**Watch for:** Here's the thing, The thing is, Let's be honest, Real talk, Buckle up,
Without further ado, Here's what you need to know, And here's where it gets interesting;
and the softer Let's dive in, Let's explore, Let's break this down, Let's get started.
**Measured:** "Let's dive in" and its friends are in 5% of human dev.to posts and 7% of
assistant posts. It is a blog habit people had before chatbots.
**Instead:** remove the run-up and make the point.

### 5. Arguing with no one [TELL]

This isn't about, I'm not saying, To be clear, Don't get me wrong, This is not to say,
Some might say… but, One might be tempted to, It would be easy to just. Remove the
defense. If it holds a real claim, state the claim. Keep an objection the text answers in
full.

### 6. Lists of three [rate, READ]

Ideas arrive in threes to sound complete, whether the meaning has three parts or not. At
the sentence scale ("fast, reliable, and easy to use"), as three parallel examples, as
three short facts followed by a lesson.
**Measured:** the strongest single feature on held-out texts. Assistant posts run a
median of 7.2 lists of three per 1,000 words against 2.25 for humans (AUC 0.86), and the
Economist's 2026 study of four chatbots found the same. Check that each item adds a
distinct idea. Merge, keep two, or develop the strongest. Keep three real items when the
meaning has three.

### 7. Repeated sentence openings, and the measured correction

Several sentences starting with the same subject because repetition was handled by
rule: merge them or change the subject. **But do not eliminate repetition.** TextPulse
measured humans opening consecutive sentences with the same word 7.2 times per 100
transitions against 2.7 for AI rewrites; the band carries the range for your register.
Stay inside it rather than at zero.

### 8. Dashes [TELL, rate]

**Measured:** em dashes, en dashes or a spaced double hyphen appear in 27% of human
dev.to posts, and in the held-out assistant posts in 100% from Claude Sonnet, 79% from GPT
and 7% from Claude Opus. The em dash is now a signature of
vendor and version, not of AI in general: per 1,000 words GPT-4.1 wrote 10.6, Claude Opus
4.6 wrote 9.1, GPT-5.4 wrote 1.4 and Llama none (Freeburg 2026); the Economist found in
July 2026 that only Claude still used more than professional writers. Across six model
families the rate differs 200-fold. Its absence proves nothing.
**Instead:** unless the writer's own sample uses dashes, replace each with a period,
comma, colon or parentheses, or rewrite. Leave dashes in code, commands and paths alone.
In Spanish the raya is correct punctuation for asides and dialogue; do not remove it
there. In fiction the gap is wider: dashes are in 20% of the human stories and 81% of the
assistant ones, the strongest single fiction feature (AUC 0.88).

### 9. Stacked qualifiers [TELL]

to be fair, it's also possible, could potentially, might arguably, in some cases it may.
Keep a qualifier only when the meaning needs it. *Perhaps* and *tends to* are human
habits: Wikipedia's 2026 guide lists hedges among the signs of human writing.

### 10. Hyphenated pairs after a noun [TELL]

"the report is high-quality", "the service is real-time". Keep the hyphen before a noun,
drop it after.

### 11. Passive voice [rate]

**Measured, and the old advice was backwards for this register.** Reinhart et al. (2025)
found GPT-4o using the agentless passive at about half the human rate across six
registers. On this skill's run the assistant posts also sat lower (held-out median 4.0
per 1,000 words against 5.6 for humans, AUC 0.67). A passive is fine when the actor is unknown or
beside the point. Do not convert every passive to active.

### 12. Inflated significance [TELL]

stands as a testament, a pivotal moment, plays a key role, marking a shift, reflects a
broader, enduring legacy, setting the stage for, paving the way, evolving landscape; the
send-off ("the future looks bright", "only time will tell"). Keep the fact, drop the
significance. End on the last concrete fact.

### 13. Vague connection [READ]

associated with, connected to, linked to, tied to. Name the relationship the source
gives. If the source does not say, keep the vague wording rather than inventing a role.

### 14. -ing clauses tacked on after a comma [TELL, rate]

"…, highlighting its importance", "…, ensuring that users never wait", "…, making it
easy to deploy". **Measured:** GPT-4o writes present participial clauses at 5.3 times the
human rate, the largest grammatical gap Reinhart et al. found; on this skill's run the
rider after a comma is in 18% of assistant posts and 8% of human ones. Keep the fact.
Keep the rider only when the source supports what it claims, and prefer a second
sentence that says it plainly.

### 15. Sales language [TELL]

boasts, vibrant, exemplifies, nestled, in the heart of, groundbreaking, renowned, diverse
array, breathtaking, stunning, seamlessly integrates. State what the thing is.

### 16. Borrowed authority [TELL]

experts argue, observers have cited, industry reports, some critics, several
publications. Use the real source and what it said, or cut the claim. Never invent a
source.

### 17. Avoiding is, are and has [TELL]

serves as, stands as, functions as, operates as, boasts a. Use *is*, *are*, *has*. Geng
and Trotta (2024) measured a drop of over 10% in *is* and *are* in academic writing in
2023, with no change before it.

### 18. Bold labels on list items [READ]

A list where every item opens with a bold label and a colon. **Measured:** in 8% of posts
on both sides, so it is no signal in this register and only a READ. Turn it into prose
when the labels carry no information of their own.

### 19. Headings [TELL]

**Measured:** three in four headings in Title Case, with three or more headings, is in
14% of human posts and 62% of assistant posts (100% of the held-out Sonnet posts). Use sentence case unless the house style
says otherwise.
**Not tells, in this register:** emoji in headings (11% of human posts, no assistant
post) and a horizontal rule between sections (60% of human posts, no assistant post).
The old rule against them came from Wikipedia editing, where the register is different.
Do not add them to look human, either.

### 20. Curly quotes [TELL]

Curly quotes where the writer or format uses straight ones. Most editors curl quotes
automatically, so this is weak alone.

### 21. Chatbot residue [FAIL]

I hope this helps, Of course!, Certainly!, Great question!, You're absolutely right,
Should I continue, Is there anything else. Remove the wrapper, keep the content. *Let me
know if you have questions* at the end of a post is a sign-off people wrote long before
chatbots (it is in human dev.to posts), so it is not on this list.

### 22. Knowledge-limit disclaimers [FAIL]

as of my last update, up to my last training, while specific details are limited, based
on available information, not widely documented, it is believed that. State what the
source does not show, or cut the sentence. Never present a guess as a fact.

### 23. A heading repeated in the first sentence [READ]

A heading followed by a short paragraph that restates it. Remove the restatement.

### 24. Writing about the previous version [READ]

Documentation describing what the text replaced instead of current behavior. Mention the
previous version only in changelogs, release notes and migration guides.

### 25. Structural uniformity [READ]

Herbold et al. (2023) found "identical beginnings of the concluding sections of all
ChatGPT essays" and very similar opening sentences. Check the shape: sections that all
open with an abstract statement of the problem, paragraphs of near-identical length,
every section ending on the same move. Open one section with a concrete detail, let one
paragraph run long and another stop after two lines.

### 26. The summary section at the end [TELL]

**Measured:** a closing section headed Conclusion, Final thoughts, Wrapping up or Key
takeaways, or an "in conclusion", is in 62% of assistant posts and 14% of human posts. Readers notice it: in
Russell et al. (2025, ACL), experts who caught 92.7% of AI articles cited the ending in
13% of their explanations, "overly long and summarize everything". Wikipedia's 2026 guide
now lists the literal "In conclusion" as a sign of older models, but the summary ending
itself remains. End on the last thing worth saying. If the post needs a recap, make it
new: a decision, a caveat, the next step the writer actually took.

### 27. Stock names [TELL]

Invented people named Sarah or Emily in non-fiction (in 63% of GPT-4o and 70% of
Claude 3.5 articles in Russell et al.), and fiction names such as Elara, Kael, Seraphina
or Aris Thorne (Elara at up to 107,000 times the human rate in Antislop's creative
writing data). In non-fiction, never invent a person; in fiction, pick a name the story
earns.

### 28. Abstract "a mix of" bundles [TELL]

a mix of pride and fear, the weight of unspoken expectations, a flicker of hope. In the
LAMP corpus (Chakrabarty et al. 2025, CHI) the shape never appears in the human seed
paragraphs, and professional writers edited 54% of the ones the models wrote. Name the
specific feeling or show what the person did.

### 29. Stock sensory clichés, mostly fiction [TELL]

voice barely above a whisper, the air thick with, hung in the air, the pit of her
stomach, a smile playing on her lips, eyes never leaving, casting long shadows. Antislop
(2025) found "voice barely whisper" among the most over-used phrases of 69% of 67 models,
and "flickered" among the over-used words of 98.5%. Clichés were 17% of the 8,035 edits
professional writers made to model fiction in LAMP. **Measured here, these exact phrases
were rare in 2026 stories** (3% of the assistant training stories, 1% of human ones), and
*flickered* was in 6%: the models moved on, and the clichés that remain are the ones in
Part B's fiction lexicon.

### 30. Showing, then explaining what it meant [READ]

A sentence shows something, then a clause or a second sentence explains it: "…, a
reminder that…", "It was clear that she cared." Redundant exposition was 18% of the LAMP
edits, and it stayed constant even in the paragraphs rated best. Cut the explanation and
trust the reader.

### 31. Generic where a specific exists [READ]

No names, numbers, dates or first-hand detail where the subject has them; "various
factors", "in many ways"; claims that would fit any topic. Lack of specificity is a LAMP
category that models fail to fix in their own edits, and density and relevance were the
best predictors of what readers called slop (Shaib et al. 2025). Use the specifics the
source has. Never invent them.

### 32. Announcing what the post will cover [TELL]

"In this post, we'll…", "Whether you're a beginner or a seasoned pro…". **Measured:** in
21% of assistant posts and 10% of human posts. Start with the first real thing.

### 33. Too many headings [rate]

**Measured:** layout alone is a fingerprint: with every word replaced, the markdown
structure of a response identifies which model wrote it 73.1% of the time (Sun et al.,
ICML 2025), and telling the model to write plain text did not remove it. On this skill's
run, assistant posts carry a held-out median of 12.2 headings per 1,000 words against
6.6 for human posts (AUC 0.80 on training, 0.75 held out), about one heading every 77 words
against one every 150. Rewrites that fixed every word left them in place. Merge sections
that make one point, and do not give a two-paragraph idea its own heading. A story does
not need a title heading unless the user asked for one: no human story in the fiction
corpus had one, and most assistant stories did.

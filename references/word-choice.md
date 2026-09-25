# Part B: word choice

Which words mark assistant text in 2026, how the lexicons in `scripts/lexicons/` were chosen, and the plain words models leave out. Spanish is in `spanish.md`.

**The famous list is out of date.** Most of the 2023 marker words (delve, tapestry,
testament, realm, meticulous, pivotal, commendable) appeared in 1% or fewer of the 2026
assistant posts on this skill's run, the same as in the human posts. Juzek's LexA data
(2026) shows why: in GPT-5.2 *delve* is gone and *crucial*, *intricate* and
*additionally* are used less than humans use them, and Geng and Trotta (2025) found
*delve*, *intricate* and *realm* falling in arXiv abstracts from April 2024. They are
still worth removing when they appear, because older and open models use them heavily,
but their absence proves nothing.

**What is in `lexicons/ai-lean.txt`.** Every entry comes from a published list with a
measured human baseline (LexA by model and register; Kobak et al. 2025; Reinhart et al.
2025; Liang et al. 2024; Wikipedia's 2026 era lists), and was kept only if, on this
skill's run, it appeared in at most 4% of human posts and in at least 10% of assistant
posts. The 2026 survivors are words like *increasingly*, *significantly*, *consistently*,
*comprehensive*, *meaningful*, *merely*, *careful*, *remains*, *maintaining*: ordinary
words, used by models at many times the human rate. One of them is English. Three or more
distinct entries in one text fail B1, which none of the 42 held-out human posts did and
43% of the GPT posts did. Technical nouns that passed the same test (*architecture*,
*infrastructure*, *integration*, *handling*, *complexity*) were taken out again: they are
the field's vocabulary, and rewriters had to cut real terms to clear the check.

**The stronger signal is the plain words that are missing.** LexA lists the words GPT
uses at a tenth to a third of the human rate: *very, get, about, because, do, able,
said, told, lot, little, big, so, things, too, back, again, really, actually, never,
something, want, should, would*. On this skill's run, *very* was in 38% of the 168 human posts
and 10% of the 90 assistant posts, *able* in 35% and 7%, *quite* in 16% and 3%. The meter scores
their rate as `plain words`. Use them where they are the natural word; do not sprinkle
them to move a number, which is its own tell.

**The character of the signature**, which matters more than any list. TextPulse found
that among the 100 most AI-leaning words in rewrites, 44% are Latinate, mean length 9.1
characters; among the 100 most human-leaning, 10% and 5.5. Models reach for the elevated
member of every synonym pair. *Used* not *utilized*. *Use* not *leverage*. *Important*
not *pivotal*. *Show* not *showcase*. On this skill's run, mean word length separated
held-out posts with an AUC of 0.81, behind only lists of three, lexical diversity and
commas.

**Registers differ.** The news words (emphasize 314x, resilience 45x, dedication 44x in
GPT-4.1-mini, LexA) do not show up in technical blog posts at all. Nor, in 2026 fiction,
do Reinhart's GPT-4o fiction words (camaraderie 162x, palpable 95x, solace 95x, fleeting
84x, unspoken 102x): on this skill's run *tapestry*, *solace* and *palpable* were in no
assistant story, and *unspoken* in 2%. What did separate the 2026 stories came from the
Antislop list: *murmured*, *blinked*, *hummed* and *faintly*, and the stock name *Marcus*,
each in at most 5% of human stories and 5% to 15% of assistant ones; *whispered* was in
32% of assistant stories but also in up to 8% of human ones, too many to list. These are
in `ai-lean-fiction.txt`, which `bands-fiction.json` selects. One of them appeared in no
held-out human story and in 20% to 30% of the assistant ones.

**If you write with Claude.** Claude is the most identifiable model family in TextPulse's
*Modelometry* (73.7% and 63.9% attribution accuracy in academic and chat registers
against 14.3% chance). Its over-used academic words are in `claude-lean.txt` (*through,
across, substantially, mechanisms, fundamentally*); four or more distinct
ones is a TELL. Claude Sonnet also used em dashes in every post on this skill's run.

**Sincerity markers are Claude's, not the writer's.** Anthropic's own claude.ai system
prompts tell Claude to avoid *genuinely*, *honestly* and *straightforward* (Opus 4.8's
also *actually*). On this skill's run *genuinely* was in 1% of human posts and 50% of
Claude Sonnet ones, so it joined `ai-lean.txt` in September 2026 (Sonnet posts left
clean by the checklist fell from 14% to 0%, held-out human posts unchanged). *Honestly*
is in 5% of human posts, too many for the list, but the skill's own rewrites put it in
33%: state the opinion and leave its sincerity alone. *Actually* is in 24% of human posts
and 64% of Claude Opus ones, so it is left out of the plain-word advice even though LexA
found GPT under-using it.

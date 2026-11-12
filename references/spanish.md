# Spanish (español)

For Spanish blog posts and articles. Select the Spanish bands with `QUIRON_BANDS=scripts/bands-es.json` (path relative to this skill's directory).

**Spanish (español).** `bands-es.json` is built by `build-corpus-es.sh` from 241 Spanish
dev.to posts by 118 authors, all before 2022, and measured against 62 posts written in
Spanish by the same four assistants in 2026. Select it with
`QUIRON_BANDS=scripts/bands-es.json`; the meter then counts
Spanish forms (nominalizaciones en -ción/-miento/-dad, adverbios en -mente, pasiva con
*ser*, gerundio tras coma, conectores como *Sin embargo* o *Además*, listas con *y/o*).
What separates assistant Spanish from human Spanish on held-out posts (58 human; 30
assistant posts from September 2026 and 50 from November, by Claude Opus 5.5, Sonnet 5.5,
Fable 5.2, GPT-6.1 and GPT-6.1 Terra; AI medians from the 64 training posts of both months):

| rasgo | human p10–p90 | AI median | AUC sept. | AUC nov. |
|---|---|---|---|---|
| primera persona /1k | 0.7 – 27.8 | 0 | 0.90 | 0.89 |
| listas de tres /1k | 0 – 5.5 | 5.2 | 0.84 | 0.93 |
| longitud media de oración | 16.4 – 32.5 | 15.4 (lower) | 0.58 | 0.92 |
| diversidad léxica MATTR-50 | 0.753 – 0.824 | 0.831 | 0.82 | 0.81 |
| encabezados /1k | 0 – 16.0 | 14.2 | 0.87 | 0.79 |
| variación de longitud de oración | 0.44 – 0.82 | 0.48 (lower) | 0.68 | 0.74 |
| comas /1k | 22.9 – 70.7 | 48.4 | 0.75 | 0.65 |
| longitud media de palabra | 4.6 – 5.2 | 5.1 | 0.72 | 0.59 |

The November models write much shorter sentences than people do (0.92) and no longer
overuse adverbs in *-mente*: that direction, and the ones for questions and words per
paragraph, did not survive both months together and are now two-sided.

Three checks are Spanish-only: "no es X: es Y" (E1: 3% of held-out human posts; 16% of the
September training posts, 6% of the November ones), a closing "## Conclusión" or
"## Resumen" section (E2: 19% of held-out human posts; 50% to 100% of the Claude posts of
both months, none of the GPT-6.1 ones) and bold labels on list items (E4, November 2026:
14% of held-out human posts; 60% of Opus 5.5 posts, 40% of Sonnet 5.5, 70% of Fable 5.2,
none of the GPT ones). With E4 the checklist AUC rose from 0.70 to 0.82 for Opus 5.5 and
from 0.71 to 0.88 for Fable 5.2, and no more human posts failed.

With the directions from both months, 5% of held-out human posts fail C1 (7% before) and
93% pass the whole checklist clean (91% before); the assistant posts caught did not
change, except September's Sonnet (C1 40% to 10%) and GPT (100% to 90%).

**The Spanish folklore list is wrong for 2026 models.** *Cabe destacar*, *es importante
señalar*, *en el panorama actual*, *hoy en día*, *sumérgete*, *en conclusión* and the
gerund after a comma (*…, permitiendo que*) appeared in 2 of the 32 assistant training
posts (both *hoy en día* or *en el mundo digital*) and in 4% to 10% of the human ones. Likewise LexA's Spanish news words (*solidez*
37x, *entrelazar* 36x, *fortalecer* 29x, *significativo* 27x, *enfatizar* 18x, *fomentar*
17x) did not appear in technical posts from either side; only *fundamental*, *estricto* and
*vulnerabilidad* passed the same test the English lexicon did, and they are in
`ai-lean-es.txt`. The plain words that go missing in Spanish (LexA): *decir, hacer, tener,
ir, hay, muy, casi, algo, porque, ya, después, menos*. Alonso Simón et al. (2025) found the
same direction in GPT-3.5 and GPT-4 Spanish: fewer commas-per-sentence, fewer parentheses
and quotation marks, more sentences per text. The raya is correct Spanish punctuation for
asides and dialogue and is never a tell by itself.

**Spelling and layout calques from English are not usable either.** A 2026 Argentine
study (Giammatteo and Carranza, *Exlibris*) lists them for seven models, with no human
group. On this skill's texts: Title Case headings are in 5% of held-out human posts and
in none of the 112 assistant posts; a capital after the colon of a list label in 23% of
human posts and 0% to 60% of assistant ones by model; a colon straight after a verb
(*incluyen:*) in 19% and 0% to 20%; a comma before the final *y* in 15% and 0% to 50%. The
contrast variants readers quote (*no solo… sino también*, *no se limita a*, the semicolon
form) are in 0% to 6% of human posts and 0% to 10% of the November assistant ones. None of
them is checked.

**The notes-first rules hold in Spanish.** On 30 Spanish dev.to titles, rewrites built
from the author's notes with the September 2026 rules were judged AI by blind Claude Opus
judges 3% of the time, against 20% with version 1.1.0 (mean P(AI) 29.2 against 38.8, p <
0.001; human originals 5.2). `references/numbers.md` has the protocol.

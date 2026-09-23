# Spanish (español)

For Spanish blog posts and articles. Select the Spanish bands with `QUIRON_BANDS=scripts/bands-es.json` (path relative to this skill's directory).

**Spanish (español).** `bands-es.json` is built by `build-corpus-es.sh` from 241 Spanish
dev.to posts by 118 authors, all before 2022, and measured against 62 posts written in
Spanish by the same four assistants in 2026. Select it with
`QUIRON_BANDS=scripts/bands-es.json`; the meter then counts
Spanish forms (nominalizaciones en -ción/-miento/-dad, adverbios en -mente, pasiva con
*ser*, gerundio tras coma, conectores como *Sin embargo* o *Además*, listas con *y/o*).
What separates assistant Spanish from human Spanish on held-out posts:

| rasgo | human p10–p90 | AI median | AUC |
|---|---|---|---|
| primera persona /1k | 0.7 – 27.8 | 0 | 0.89 |
| diversidad léxica MATTR-50 | 0.753 – 0.824 | 0.829 | 0.85 |
| adverbios en -mente /1k | 1.8 – 11.7 | 12.8 | 0.82 |
| listas de tres /1k | 0 – 5.5 | 6.8 | 0.82 |
| encabezados /1k | 0 – 16.0 | 15.1 | 0.81 |
| longitud media de palabra | 4.6 – 5.2 | 5.1 | 0.79 |
| comas /1k | 22.9 – 70.7 | 56.5 | 0.74 |
| variación de longitud de oración | 0.44 – 0.82 | 0.50 (lower) | 0.73 |

Two checks are Spanish-only: "no es X: es Y" (in 3% of human posts and 16% of the
assistant training posts) and a closing "## Conclusión" or "## Resumen" section (14% and
78%).

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

# Video scripts: what is said

Read this before rewriting a video script, with `bands-script.json` for English and
`bands-script-es.json` for Spanish. Both measure only the narration, because the meter drops
the scene headings, stage directions, speaker labels and timestamps before it counts
anything. A rewrite works the same way: change what is said and leave every stage direction,
heading and label where it was, since whoever records the video needs them.

The rules come from YouTube captions uploaded before 2022 (193 in English, 107 in Spanish)
and from assistant scripts written on the same titles in November 2026. Blind judges who
read only the narration gave the human captions a mean P(AI) of 6.1 in English and 5.2 in
Spanish, and the assistant scripts 82.8 and 79.9. The counts are in
`eval/results/script.txt` and `script-es.txt`.

## What not to add

Human narration in the corpus is full of "you know", "kind of", "basically", "o sea" and
"pues", and it has ellipses, sponsor reads and nods to the channel's earlier videos. The
judges' most common human cue was a caption typo or a transcription error. Do not add any of
these, because they are what the captions happen to have and putting them in on purpose is
a disguise. Do not add a fact, number, anecdote or memory that the draft does not have
either.

## English

- **Longer sentences, joined the way people talk.** Assistant scripts average 12.3 words a
  sentence, and human ones run from 13.1 to 25.4 with a median of 17.8 on every one of 17
  channels. When the second sentence follows from the first, join the two with "and", "but"
  or "so". Do not cut a point into a row of fragments, and stop at the median: never go past
  25 words on average.
- **Fewer lists of three.** Assistant scripts have 6.3 per 1,000 words and human ones 0 to
  5.2 (median 2.1). Turn most of them into two items or one, and keep a three only when the
  thing really has three parts.
- **Repeat the plain word.** MATTR-50 is 0.833 in assistant scripts, at the top of the human
  band (0.77 to 0.833, median 0.807). Say "the tower" again instead of moving on to "the
  structure" and "the spire", but do not push it below 0.77.
- **Let the narrator be in the room.** First person is 4.8 per 1,000 words in assistant
  scripts against a human median of 14.4 (band 1.75 to 34.6). Human narrators talk to the
  viewer as themselves ("I'll show you", "let's look at"), so use that where the script
  already guides the viewer. Never give the narrator an experience or a memory the draft
  does not have.
- **Start with the thing, not "Imagine".** A sentence opens with "Imagine" or "Picture
  this" in 29% of assistant scripts and 2% of human ones (S1). Start with the fact or the
  scene.
- **No staged reveals.** "Here's the twist", "here's why", "then there's", "the honest
  answer" and "sounds simple" are in 47% of assistant scripts and 12% of human ones (S2).
  Say the thing.
- **No request for comments.** "Let me know in the comments" is in 24% of assistant scripts
  and in no held-out human one (S3). A mention of the comments is fine. A sign-off or a
  subscribe line is the channel's call, so leave it as the draft has it.
- **No "next time you…" closer.** It is in 11% of assistant scripts and 4% of human ones
  (S4).
- **No bare noun-phrase question answered at once.** "The catch? It costs twice as much."
  is in 9% of assistant scripts and 2% of human ones (S5). Write "It costs twice as much."
- **No pairs of fragments on one opener.** "No roads. No cars." or "Maybe… Maybe…" is in
  11% of assistant scripts and in no held-out human one (S6).

When a script has three of S1 to S6, the checklist fails it (S7). That happens in 13% of
assistant scripts and in no human one.

## Spanish

- **Frases más largas.** Assistant scripts average 14.4 words a sentence, and human ones run
  from 14.6 to 29.1 with a median of 21.1 on every one of 10 channels. Join two sentences
  with "y", "pero", "así que" or "porque" when one follows from the other, and never go past
  29 words on average.
- **Vary the length.** The sentence-length CV is 0.52 in assistant scripts against 0.47 to
  0.81 in human ones (median 0.60). Put a long sentence next to a short one, but do not go
  past 0.81 and do not get there with fragments.
- **Repeat words.** MATTR-50 is 0.822 against 0.755 to 0.825 (median 0.797). Repeat the
  plain noun instead of a synonym, and do not go below 0.755.
- **Fewer lists of three.** Assistant scripts have 5.5 per 1,000 words and human ones 0 to
  5.0 (median 2.2).
- **Never "quédate hasta el final".** No human caption uses it, and the checklist fails it
  (SE1).
- **No promise of what is coming.** "Hoy te cuento" or "hoy vamos a" is in 36% of assistant
  scripts and 11% of human ones (SE2). Start with the first real thing.
- **No sentence opening with "imagina".** It is in 40% of assistant scripts and 7% of human
  ones (SE3).
- **No "y aquí viene", "lo curioso es que" or "dato curioso".** These are in 24% of
  assistant scripts and 4% of human ones (SE4).
- **Do not close by asking the title back.** "Entonces, ¿…?" closes 36% of assistant
  scripts and 7% of human ones (SE5).
- **No request for comments.** "Cuéntame en los comentarios" is in 52% of assistant
  scripts and 4% of human ones (SE6).
- **No "la próxima vez que…".** It is in 4% of assistant scripts and in no human one (SE7).

When a script has three of SE1 to SE7, the checklist fails it (SE8). That happens in 36% of
assistant scripts and in no held-out human one.

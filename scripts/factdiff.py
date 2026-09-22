#!/usr/bin/env python3
"""List what a rewrite states that its source does not: the invented-fact check.

Every rewriter in this skill's tests slipped in small specifics while rewording
("in the same week", "next year", "in React 17", "laptops"), and none of the other
checks can see them, because an invented detail reads as more human, not less.
This compares the two texts and prints, for the rewrite only:

  numbers     figures that are not in the source (these set the exit code)
  number words  two, three, ... not in the source (a question, not a failure)
  names       capitalised words not in the source, outside sentence starts
  links       URLs not in the source
  time        time expressions (last year, the same week, in 2019) not in the source
  first       first-person experience claims (I've seen, we ran, I once) not in the source

Nothing here is proof. A name can be a pronoun-free rephrasing of one in the source,
and "one" can be a pronoun. Every line is a question for the rewriter: where does
this come from? Numbers and links with no source are the ones that are almost
always invented, so they alone set the exit code.

Code blocks and inline code are ignored on both sides.

Usage:
  factdiff.py SOURCE [SOURCE ...] REWRITE     e.g. the draft and the writer's notes
"""
import re, sys

NUM_WORDS = set("""two three four five six seven eight nine ten eleven twelve
twenty thirty forty fifty hundred thousand million billion half dozen
uno dos tres cuatro cinco seis siete ocho nueve diez cien mil millón millones""".split())
TIME = re.compile(
    r"\b(?:last|next|this|that|the same|the following|the previous|every) "
    r"(?:week|month|year|day|night|morning|quarter|summer|winter|spring|fall|weekend|sprint)\b"
    r"|\b(?:yesterday|tomorrow|recently|a few (?:days|weeks|months|years) ago|"
    r"(?:a few |a couple of |two |three |several )?(?:days|weeks|months|years) (?:ago|later))\b"
    r"|\bin (?:19|20)\d\d\b"
    r"|\b(?:el|la) (?:semana|mes|año) (?:pasad[oa]|que viene|siguiente)\b|\bhace (?:\w+ )?(?:días|semanas|meses|años)\b",
    re.I)
FIRST = re.compile(
    r"\b(?:I|we)(?:'ve| have| had)? (?:once |recently |finally |actually )?"
    r"(?:seen|used|tried|ran|run|built|shipped|learned|found|noticed|spent|worked|watched|"
    r"broke|fixed|debugged|migrated|wrote|lost|hit|met|started|switched)\b"
    r"|\bin my (?:experience|last job|team|company)\b|\bI remember\b", re.I)


def clean(text):
    text = re.sub(r"```.*?```|~~~.*?~~~", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`|\*\*|__", " ", text)
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    # heading and list markers, with their numbering, are layout, not facts
    return re.sub(r"^\s*(?:#{1,6}\s*(?:\d+[.)]\s*)?|[-*+]\s+|\d+[.)]\s+)", "", text, flags=re.M)


def facts(text):
    t = clean(text)
    low = t.lower()
    words = set(re.findall(r"[a-záéíóúñü']+", low))
    nums = set(re.findall(r"\b\d[\d.,:%]*\b", t))
    num_words = words & NUM_WORDS
    names = set()
    for sent in re.split(r"(?<=[.!?:])\s+|\n+", t):
        toks = re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü][\w'.-]*", sent)
        for tok in toks[1:]:
            if tok[0].isupper() and tok not in ("I", "I'm", "I've", "I'd", "I'll"):
                names.add(re.sub(r"'s$", "", tok.strip(".'")))
    links = set(re.findall(r"https?://[^\s)>\]]+", t))
    time = {m.group(0).lower() for m in TIME.finditer(t)}
    first = {m.group(0).lower() for m in FIRST.finditer(t)}
    return {"numbers": nums, "number words": num_words, "names": names, "links": links,
            "time": time,
            "first": first, "_words": words, "_low": low}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src = facts("\n\n".join(open(p, encoding="utf-8").read() for p in sys.argv[1:-1]))
    new = facts(open(sys.argv[-1], encoding="utf-8").read())
    hard = 0
    for key in ("numbers", "number words", "names", "links", "time", "first"):
        extra = sorted(x for x in new[key] - src[key]
                       # a name the source has in lower case is not new
                       if not (key == "names" and x.lower() in src["_words"])
                       and not (key != "names" and x.lower() in src["_low"]))
        if extra:
            if key in ("numbers", "links"):
                hard += len(extra)
            print(f"{key:12} not in the source: {', '.join(extra[:15])}")
    if not hard:
        print("no new numbers or links" + ("" if any(
            new[k] - src[k] for k in ("number words", "names", "time", "first"))
            else "; nothing new found"))
    return min(hard, 120)


if __name__ == "__main__":
    sys.exit(main())

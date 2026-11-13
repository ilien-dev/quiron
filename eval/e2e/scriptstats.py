#!/usr/bin/env python3
"""What the rewrites of a video-script set did to the text, per snapshot.

  scriptstats.py SET SNAP [SNAP ...]      ("draft" is the set's own drafts)

For each snapshot, the mean over its final.md files of:
- meter features on the spoken words (against the set's script band file);
- per 1,000 spoken words: sentences opening with Imagine / imagina, staged reveals,
  comment requests, fillers ("you know", "kind of", "basically", "um", "uh" / "o sea",
  "bueno", "pues", "este", "eh"), ellipses;
- leaks: texts whose narration still holds markup spoken() lets through (a sources label,
  "End of script", a word count, "Referencia técnica", "Guion original");
- lost: the share of the narration that aimeter.prose() drops after spoken(), and the number
  of texts losing more than 10%. prose() reads four or more blank lines plus the next line as
  indented code; spoken() leaves such runs where it removed stacked directions.
"""
import glob, os, re, statistics as st, sys

CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE)
import harness  # noqa: E402

SET = sys.argv[1]
os.environ["QUIRON_BANDS"] = harness.os.path.join(
    harness.REPO, "scripts", "bands-script-es.json" if SET.endswith("-es") else "bands-script.json")
sys.path.insert(0, os.path.join(harness.REPO, "scripts"))
import aimeter  # noqa: E402

KEYS = ["mean_sentence_len", "cv_sentence_len", "first_person_1k", "triads_1k", "mattr50"]
ES = SET.endswith("-es")
PAT = {
    "imagine": r"(?i)(?:^|[.!?¿¡]\s+)(?:now,? |so,? |ahora )?imagin",
    "reveals": r"(?i)\bhere's (?:the|why|how|what|where)\b|\bthen there's\b|\by aqu[ií] viene\b|\blo curioso es que\b|\bdato curioso\b",
    "comments": r"(?i)\b(?:let|tell) (?:me|us) (?:know )?(?:in the comments|below)\b|\bleave a comment\b|"
                r"\b(?:cu[eé]nta(?:me|nos)|d[eé]ja(?:me|nos)|escr[ií]be(?:me|nos)|dinos|d[ií]me)\b[^.!?]{0,30}\ben los comentarios\b",
    "fillers": (r"(?i)\b(?:o sea|bueno|pues|este|eh|em)\b" if ES else r"(?i)\b(?:you know|kind of|basically|um|uh)\b"),
    "ellipses": r"\.\.\.|…",
}
LEAK = re.compile(r"(?i)\bsources?:|end of script|referencia t[eé]cnica|fuentes[^.]{0,20}:|guion original"
                  r"|sugerencia de descripci|word count|recuento de palabras")


def files(snap, rows):
    if snap == "draft":
        return [os.path.join(harness.REPO, os.path.expanduser(r[1])) for r in rows]
    return [f for r in rows for f in sorted(glob.glob(os.path.join(harness.H, "work", snap, "r[0-9]", r[0], "final.md")))]


def lost(sp):
    full = len(aimeter.prose(re.sub(r"\n\s*\n", "\n\n", sp)).split())
    return 1 - len(aimeter.prose(sp).split()) / full if full else 0.0


def main():
    rows = harness.sets()[SET]
    for snap in sys.argv[2:]:
        fs = files(snap, rows)
        texts = [open(f, encoding="utf-8").read() for f in fs]
        sps = [aimeter.spoken(t) for t in texts]
        ms = [m for m in (aimeter.measure(t) for t in texts) if m]
        feats = " ".join(f"{k}={st.mean(m[k] for m in ms):.3g}" for k in KEYS) if ms else ""
        rates = " ".join(f"{k}={st.mean(len(re.findall(p, s)) / max(len(s.split()), 1) * 1000 for s in sps):.2f}"
                         for k, p in PAT.items())
        leaks = sum(bool(LEAK.search(harness.narration(t))) for t in texts)
        ls = [lost(s) for s in sps]
        print(f"{snap:12} files={len(fs):3} measured={len(ms):3} {feats} {rates} leaks={leaks}/{len(fs)} "
              f"lost={st.mean(ls):.1%} (>10%: {sum(x > 0.1 for x in ls)}, max {max(ls):.0%})")


if __name__ == "__main__":
    main()

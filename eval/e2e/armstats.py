#!/usr/bin/env python3
"""What the rewrites of the three November 2026 arms did to the draft, per snapshot.

  armstats.py SET SNAP [SNAP ...]       ("draft" is the set's own drafts)

SET is a video-script set (scr, scrn, scrs, scr2, ..., scrh); its rows give the draft and, in
the third column, the notes. For each snapshot, over its final.md files (every rep), against the
draft of the same row:

- facts: the mean per text of figures and links in final.md that are in neither the draft nor
  the notes (scripts/factdiff.py's two hard checks, with its own filters). On a row with notes
  the notes are a source; on a row without, the draft alone is.
- kept: the share of the draft's sentences that stand byte-identical in final.md. Sentences are
  the ones the meter counts (aimeter's SENT split of prose(spoken(text)), more than two words),
  compared after collapsing white space.
- mean sentence length and sentence-length CV, of the drafts and of the final.md files, and the
  number of texts whose final.md is not lower than its draft on both.

Sentence length and CV are the meter's own, on the spoken words, with the script band file of the
set's language.
"""
import glob, os, re, statistics as st, sys

CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE)
import harness  # noqa: E402

SET = sys.argv[1]
os.environ["QUIRON_BANDS"] = os.path.join(
    harness.REPO, "scripts", "bands-script-es.json" if SET.endswith("-es") else "bands-script.json")
sys.path.insert(0, os.path.join(harness.REPO, "scripts"))
import aimeter  # noqa: E402
import factdiff  # noqa: E402


def sentences(text):
    t = aimeter.prose(aimeter.spoken(text))
    return [re.sub(r"\s+", " ", s).strip() for s in aimeter.SENT.split(t) if len(s.split()) > 2]


def new_facts(source_texts, text):
    """Figures and links in text that no source has, counted the way factdiff.main counts them."""
    src = factdiff.facts("\n\n".join(source_texts))
    new = factdiff.facts(text)
    return sum(1 for k in ("numbers", "links") for x in new[k] - src[k] if x.lower() not in src["_low"])


def main():
    rows = harness.sets()[SET]
    for snap in sys.argv[2:]:
        kept, lens, cvs, dl, dc, both, facts, n, nmeas = [], [], [], [], [], 0, [], 0, 0
        for r in rows:
            draft = open(r[1], encoding="utf-8").read()
            notes = [open(r[2], encoding="utf-8").read()] if r[2] != "-" else []
            finals = ([r[1]] if snap == "draft" else
                      sorted(glob.glob(os.path.join(harness.H, "work", snap, "r[0-9]", r[0], "final.md"))))
            ds = sentences(draft)
            md = aimeter.measure(draft)
            for f in finals:
                text = open(f, encoding="utf-8").read()
                n += 1
                fs = sentences(text)
                kept.append(sum(s in set(fs) for s in ds) / len(ds) if ds else 0.0)
                facts.append(new_facts([draft] + notes, text))
                m = aimeter.measure(text)
                if m and md:
                    nmeas += 1
                    lens.append(m["mean_sentence_len"])
                    cvs.append(m["cv_sentence_len"])
                    dl.append(md["mean_sentence_len"])
                    dc.append(md["cv_sentence_len"])
                    both += m["mean_sentence_len"] >= md["mean_sentence_len"] and m["cv_sentence_len"] >= md["cv_sentence_len"]
        print(f"{snap:10} {SET:8} texts={n:3} facts_not_in_sources={st.mean(facts):.2f}/text "
              f"kept_identical={st.mean(kept):.1%} "
              f"mean_sentence_len {st.mean(dl):.1f} -> {st.mean(lens):.1f} cv {st.mean(dc):.3f} -> {st.mean(cvs):.3f} "
              f"not_lower_on_both={both}/{nmeas}")


if __name__ == "__main__":
    main()

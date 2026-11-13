#!/usr/bin/env python3
"""Score groups of texts against ONE band file, with no recalibration.

evaluate.py rebuilds the bands from --human every time, so it cannot say what an already
shipped band file does to a text. This does: it measures each text with the file named in
QUIRON_BANDS (default scripts/bands.json), counts the features outside the human band, and
runs the checklist (audit.py) under the same file. A band file marked "_spoken" reads only
the spoken words; any other reads the raw text, markup included.

Usage:
  QUIRON_BANDS=scripts/bands.json python3 eval/band_compare.py [--detail] NAME=PATH ...
  PATH is a folder, a file, or HUMAN_DIR@heldout (every 4th file by sorted name, the
  held-out quarter evaluate.py and gensamples.py use).
With --detail each text gets a line with its out-of-band features.
"""
import os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import aimeter, audit  # noqa: E402
import json  # noqa: E402


def paths(spec):
    if spec.endswith("@heldout"):
        d = os.path.expanduser(spec[:-len("@heldout")])
        names = [n for n in sorted(os.listdir(d)) if n.endswith((".md", ".txt"))]
        return [os.path.join(d, n) for i, n in enumerate(names) if i % 4 == 0]
    spec = os.path.expanduser(spec)
    if os.path.isfile(spec):
        return [spec]
    return [os.path.join(spec, n) for n in sorted(os.listdir(spec)) if n.endswith((".md", ".txt"))]


def main():
    args = sys.argv[1:]
    detail = "--detail" in args
    groups = [a.split("=", 1) for a in args if "=" in a]
    if not groups:
        sys.exit(__doc__)
    bands = json.load(open(aimeter.BANDS_FILE))
    skip = set(bands.get("_skip", []))
    print(f"bands: {aimeter.BANDS_FILE}  ({len(aimeter.AI_REF) - len(skip)} scored features)")
    print(f"{'group':18}{'n':>4}{'out of band, median':>22}{'AI side, mean':>15}{'clean checklist':>18}")
    for name, spec in groups:
        outs, side, clean, n = [], [], 0, 0
        for p in paths(spec):
            m = aimeter.measure(open(p, encoding="utf-8").read())
            if not m:
                continue
            v = {k: aimeter.verdict(k, m[k], bands[k]) for k in aimeter.AI_REF if k not in skip}
            bad = [k for k, x in v.items() if x != "ok"]
            n += 1
            outs.append(len(bad))
            side.append(sum(x.endswith("AI side") for x in v.values()))
            ok = not any(r[2] == "FAIL" for r in audit.run(p))
            clean += ok
            if detail:
                print(f"  {os.path.basename(p)}: {len(bad)} out ({', '.join(bad)}); "
                      f"checklist {'clean' if ok else 'FAIL'}")
        if n:
            print(f"{name:18}{n:>4}{st.median(outs):>22}{st.mean(side):>15.2f}"
                  f"{f'{clean} of {n} ({clean / n:.0%})':>18}")


if __name__ == "__main__":
    main()

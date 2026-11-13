#!/usr/bin/env python3
"""Which features a script rewrite pushes past the human band, and what it states that no source does.

  overstats.py SET SNAP [SNAP ...] [--facts]

For each snapshot, over its final.md files of the rows of SET (every rep): how many texts have each
feature on the overshot side and on the AI side, measured on the spoken words against the script
band file of the set's language (the same count report.py averages as "over" and "aiside"), most
frequent first. With --facts it also lists, for each text, the figures and links in final.md that
are in neither the draft nor the notes (scripts/factdiff.py's hard checks), with the text's name.
"""
import glob, json, os, subprocess, sys
from collections import Counter

CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE)
import harness  # noqa: E402

SET = sys.argv[1]
BANDS = os.path.join(harness.REPO, "scripts", "bands-script-es.json" if SET.endswith("-es") else "bands-script.json")
sys.path.insert(0, os.path.join(harness.REPO, "scripts"))
import factdiff  # noqa: E402


def verdicts(f):
    env = dict(os.environ, QUIRON_BANDS=BANDS, PYTHONUTF8="1")
    r = subprocess.run([sys.executable, os.path.join(harness.REPO, "scripts", "aimeter.py"), "--json", f],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    try:
        return json.loads(r.stdout)["verdicts"]
    except ValueError:
        return None


def main():
    rows = harness.sets()[SET]
    facts_on = "--facts" in sys.argv
    for snap in [a for a in sys.argv[2:] if not a.startswith("--")]:
        over, ai, n, tot_o, tot_a = Counter(), Counter(), 0, 0, 0
        extra = []
        for r in rows:
            for f in sorted(glob.glob(os.path.join(harness.H, "work", snap, "r[0-9]", r[0], "final.md"))):
                v = verdicts(f)
                if v is None:
                    continue
                n += 1
                for k, x in v.items():
                    if x.endswith("overshot"):
                        over[k] += 1
                        tot_o += 1
                    elif x.endswith("AI side"):
                        ai[k] += 1
                        tot_a += 1
                if facts_on:
                    src = factdiff.facts("\n\n".join(open(p, encoding="utf-8").read() for p in [r[1]] + ([r[2]] if r[2] != "-" else [])))
                    new = factdiff.facts(open(f, encoding="utf-8").read())
                    for k in ("numbers", "links"):
                        for x in sorted(new[k] - src[k]):
                            if x.lower() not in src["_low"]:
                                extra.append(f"{r[0]} {os.path.basename(os.path.dirname(os.path.dirname(f)))}: {k[:-1]} {x}")
        print(f"{snap:8} {SET}: {n} texts, overshot {tot_o / n:.2f} per text: " + ", ".join(f"{k} {c}" for k, c in over.most_common()))
        print(f"{'':8} {SET}: AI side {tot_a / n:.2f} per text: " + ", ".join(f"{k} {c}" for k, c in ai.most_common()))
        if facts_on:
            print(f"{'':8} {SET}: {len(extra)} figures or links in neither draft nor notes")
            for e in extra:
                print("   ", e)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the video-script sets in sets/: scr, scr2, scr-es, scr2-es, and the local human ones.

  mksets.py            write scr.tsv, scr2.tsv, scr-es.tsv, scr2-es.tsv, scrh.tsv, scrh-es.tsv

The rule, the same for every set, so anyone gets the same rows:
- scr / scr-es take 20 scripts from eval/ai/script[-es]/train-*, scr2 / scr2-es 20 from test-*.
  The model folders are taken in turn (sorted by name), one script at a time, until the set
  has 20: 5 per model on train (4 models), 4 on test (5 models).
- Within a folder the next script is, in this order: one with 400 to 1,500 spoken words
  (so rewrites stay affordable), the one whose channel is least used in the set so far,
  then the shortest if none is in that range, then the first by name.
- scrh / scrh-es take 10 held-out human captions (sorted by name, the 1st, 5th, ... file)
  from ~/corpus/script[-es], 400 to 1,500 words, the channels taken in turn by the same rule.
  Their names start with "h-", since scr2 holds assistant scripts on the same titles. Their
  paths point into ~/corpus, which build-corpus-script.sh fills; the captions are not in the
  repo.
The fourth column is the video's title, from eval/titles/script[-es]-manifest.tsv.
"""
import glob, os, sys
from collections import Counter

CODE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(CODE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import aimeter  # noqa: E402

LO, HI = 400, 1500


def titles(reg):
    out = {}
    for line in open(os.path.join(REPO, "eval", "titles", f"{reg}-manifest.tsv"), encoding="utf-8").read().splitlines()[1:]:
        c = line.split("\t")
        out[c[0]] = c[6]
    return out


def words(path):
    return len(aimeter.spoken(open(path, encoding="utf-8").read()).split())


def stem(path):
    return os.path.basename(path)[:-3]


def channel(path):
    return stem(path).split("-", 1)[0]


def pick(pools, n):
    """pools: one list of paths per model folder; take them in turn until n are chosen."""
    used, chosen, i = Counter(), [], 0
    pools = [list(p) for p in pools]
    while len(chosen) < n:
        pool = pools[i % len(pools)]
        i += 1
        if not pool:
            continue
        w = {p: words(p) for p in pool}
        best = min(pool, key=lambda p: (not LO <= w[p] <= HI, used[channel(p)],
                                        0 if LO <= w[p] <= HI else w[p], stem(p)))
        pool.remove(best)
        used[channel(best)] += 1
        chosen.append(best)
    return chosen


def row(path, title, rel=True):
    p = os.path.relpath(path, REPO).replace(os.sep, "/") if rel else path
    return f"{stem(path)}\t{p}\t-\t{title}\n"


def write(name, rows):
    with open(os.path.join(CODE, "sets", name + ".tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.writelines(rows)
    print(name, len(rows))


def main():
    for reg, suf in (("script", ""), ("script-es", "-es")):
        t = titles(reg)
        for split, name in (("train", "scr"), ("test", "scr2")):
            dirs = sorted(glob.glob(os.path.join(REPO, "eval", "ai", reg, f"{split}-*")))
            pools = [sorted(glob.glob(os.path.join(d, "*.md"))) for d in dirs]
            write(name + suf, [row(p, t[stem(p).split("-", 1)[1]]) for p in pick(pools, 20)])
        corpus = os.path.expanduser(f"~/corpus/{reg}")
        held = [p for i, p in enumerate(sorted(glob.glob(os.path.join(corpus, "*.md")))) if i % 4 == 0]
        held = [p for p in held if LO <= words(p) <= HI]
        by = {}
        for p in held:
            by.setdefault(channel(p), []).append(p)
        pools = [by[c] for c in sorted(by)]
        # one per channel in turn: the same rule, with each channel as its own pool
        chosen = pick(pools, 10)
        write("scrh" + suf, [f"h-{stem(p)}\t~/corpus/{reg}/{os.path.basename(p)}\t-\t{t[stem(p).split('-', 1)[1]]}\n"
                             for p in chosen])


if __name__ == "__main__":
    main()

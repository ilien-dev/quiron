#!/usr/bin/env python3
"""Does a feature separate people from assistants on every channel, or on a few?

Captions carry the captioner's punctuation, which differs by channel. A punctuation feature
whose human side holds for only a few channels measures the captioners, not the writers.
For each feature this prints the AI median, the median of every channel, and how many
channels sit on the human side of the AI median.

The human side is the side of the AI median where the pooled human median lies. When the
two medians are equal (em dashes, semicolons and parentheses are 0 for both) no channel
can be on the human side, so the count is 0. A channel with fewer than MIN_TEXTS texts in
the directory is left out of the count and named at the end. Texts are cut to their spoken
words first. Set QUIRON_BANDS to the register's band file so the language and lexicon match.

Usage:
  QUIRON_BANDS=scripts/bands-script.json \
  python3 eval/script_channels.py MANIFEST HUMAN_DIR AI_DIR[,AI_DIR...] [FEATURE ...]

HUMAN_DIR is the whole human corpus; like evaluate.py, only the training three quarters are read
(every 4th file by sorted name is held out). A channel is read from the manifest (the
text's video id is the end of its file name), else from the prefix of the file name.
"""
import csv, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import aimeter  # noqa: E402

MIN_TEXTS = 4


def channel_of(name, ids):
    stem = os.path.splitext(name)[0]
    for vid, chan in ids.items():
        if stem.endswith("-" + vid):
            return chan
    return stem.split("-", 1)[0]


def measured(directory, ids=None, train_only=False):
    rows = []
    for d in directory.split(","):
        names = [n for n in sorted(os.listdir(d)) if n.endswith((".md", ".txt"))]
        for i, name in enumerate(names):
            if not (train_only and i % 4 == 0):
                with open(os.path.join(d, name), encoding="utf-8") as f:
                    m = aimeter.measure(aimeter.spoken(f.read()))
                if m:
                    rows.append((channel_of(name, ids or {}), m))
    return rows


def main():
    args = sys.argv[1:]
    if len(args) < 3:
        sys.exit(__doc__)
    manifest, human_dir, ai_dir, only = args[0], args[1], args[2], args[3:]
    with open(manifest, encoding="utf-8", newline="") as f:
        ids = {r["id"]: r["channel"] for r in csv.DictReader(f, delimiter="\t")}
    human, ai = measured(human_dir, ids, train_only=True), measured(ai_dir)
    by = {}
    for chan, m in human:
        by.setdefault(chan, []).append(m)
    counted = sorted(c for c, ms in by.items() if len(ms) >= MIN_TEXTS)
    left_out = sorted((c, len(ms)) for c, ms in by.items() if len(ms) < MIN_TEXTS)
    print(f"{len(human)} human texts in {len(by)} channels, {len(ai)} AI texts; "
          f"{len(counted)} channels with {MIN_TEXTS}+ texts are counted")
    for key in (only or aimeter.AI_REF):
        h_all = st.median(m[key] for _, m in human)
        a = st.median(m[key] for _, m in ai)
        med = {c: st.median(m[key] for m in by[c]) for c in counted}
        if h_all > a:
            n = sum(v > a for v in med.values())
        elif h_all < a:
            n = sum(v < a for v in med.values())
        else:
            n = 0
        print(f"\n{aimeter.LABELS[key]} ({key}): AI median {a:.3g}, human median {h_all:.3g}, "
              f"{n} of {len(counted)} channels on the human side")
        print("  " + ", ".join(f"{c} {v:.3g}" for c, v in sorted(med.items())))
    if left_out:
        print("\nleft out of the count (fewer than %d texts): %s" %
              (MIN_TEXTS, ", ".join(f"{c} ({n})" for c, n in left_out)))


if __name__ == "__main__":
    main()

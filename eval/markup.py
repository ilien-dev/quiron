#!/usr/bin/env python3
"""Median markup per 1,000 spoken words (aimeter.markup_counts) for each model folder of
a script register, with the human training texts as a reference row.

  markup.py REGISTER HUMAN_DIR OUT
"""
import glob, os, statistics, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import aimeter

KEYS = ("stage", "speaker", "timestamp", "heading")


def row(label, files):
    counts = [aimeter.markup_counts(open(f, encoding="utf-8").read()) for f in files]
    return "%-16s %3d " % (label, len(files)) + " ".join(
        "%9.2f" % statistics.median(c[k] for c in counts) for k in KEYS)


def shown(path):
    """The path as printed in the header: the home folder as ~, so no local path reaches a results file."""
    home = os.path.expanduser("~").replace("\\", "/")
    p = path.replace("\\", "/")
    return "~" + p[len(home):] if p.startswith(home + "/") else p


def main():
    register, human, out = sys.argv[1:4]
    lines = ["# python3 eval/markup.py %s %s %s   (median per 1,000 spoken words)" % (register, shown(human), out),
             "%-16s %3s " % ("group", "n") + " ".join("%9s" % k for k in KEYS)]
    files = sorted(glob.glob(os.path.join(os.path.expanduser(human), "*.md")))
    lines.append(row("human-train", [f for i, f in enumerate(files) if i % 4]))  # as gensamples --titles
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai", register)
    for d in sorted(glob.glob(os.path.join(root, "*", ""))):
        lines.append(row(os.path.basename(d.rstrip("/\\")), sorted(glob.glob(d + "*.md"))))
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines))


main()

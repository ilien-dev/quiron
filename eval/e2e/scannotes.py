#!/usr/bin/env python3
"""scannotes.py : the longest run of words each script note shares with its human caption.

Reads eval/notes-script/*.txt against ~/corpus/script/NAME.md and eval/notes-script-es/*.txt
against ~/corpus/script-es/NAME.md, with the word rule of eval/script_reasons.py (words are runs of
letters and digits, lower-cased). Prints the files over four words, then the worst run per folder,
and exits 1 if any note shares a run of more than four words. The captions are local, so this is
run where the corpus is.
"""
import glob, os, re, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WORD = re.compile(r"[^\W_]+")


def hay(t):
    return " " + " ".join(m.group(0).lower() for m in WORD.finditer(t)) + " "


def longest(note, caption):
    h = hay(caption)
    ws = [m.group(0).lower() for m in WORD.finditer(note)]
    best = 0
    for i in range(len(ws)):
        n = best + 1
        while i + n <= len(ws) and " " + " ".join(ws[i:i + n]) + " " in h:
            best = n
            n += 1
    return best


def main():
    bad = 0
    for folder, corpus in (("notes-script", "script"), ("notes-script-es", "script-es")):
        worst, files = 0, sorted(glob.glob(os.path.join(REPO, "eval", folder, "*.txt")))
        for f in files:
            name = os.path.basename(f)[:-4]
            cap = open(os.path.expanduser(f"~/corpus/{corpus}/{name}.md"), encoding="utf-8").read()
            run = longest(open(f, encoding="utf-8").read(), cap)
            worst = max(worst, run)
            if run > 4:
                bad += 1
                print(f"{folder}/{name}.txt shares a run of {run} words")
        print(f"{folder}: {len(files)} notes, longest shared run {worst} words")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

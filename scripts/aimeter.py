#!/usr/bin/env python3
"""Measure prose against human baselines, with a ceiling as well as a floor.

Why a ceiling. TextPulse Research (2026, "Do AI Models Speak Human?") gave four
flagship models a detailed brief on what separates human prose from assistant
prose. Every model overshot every property the brief named: sentence-length
variation went to 0.58 where the human passages sit at 0.40, reading grade fell
to 13.8 where the journals were at 20.4, connective openers went to zero where
humans use them. Claude Opus 5 overshot furthest of the four, landing past the
human median on the human side. Writing that is more uneven and plainer than any
human wrote is its own tell, so every feature here is scored against a band.

Bands come from --calibrate over a corpus of texts known to be human. The
shipped band file was built from 28 dev.to posts published before 2022, the
register this is meant for. Recalibrate for any other register.

The AI reference column is from measured studies, and the direction it marks is
the direction preference tuning pushes:
  TextPulse Research 2026, 60,786 paired human/AI academic texts
  Kobak et al. 2025, Science Advances, 14.4M PubMed abstracts
  Liang et al., ICML 2024, ICLR peer reviews

Usage:
  aimeter.py FILE...               score files against the shipped bands
  aimeter.py --calibrate DIR       rebuild bands from a corpus of human texts
  aimeter.py --json FILE           machine-readable output
"""
import json, os, re, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "lexicons")
BANDS_FILE = os.path.join(HERE, "bands.json")


def _load(name):
    path = os.path.join(LEX, name)
    return set(open(path).read().split()) if os.path.exists(path) else set()


KOBAK = _load("kobak-excess-style.txt")
AI_LEAN = _load("ai-lean.txt")
CLAUDE_LEAN = _load("claude-lean.txt")
HUMAN_LEAN = _load("human-lean.txt")

# Words Kobak annotates as style words that are ordinary function words in any
# register. They fire on every English text and carry no signal here.
KOBAK_NOISE = set("""across address addresses addressing both between during into like this while
using including within through also since given both where when what which
research strategies distinct escalating""".split())

SENT = re.compile(r"(?<=[.!?])\s+")
CONTR = re.compile(r"\b\w+['’](?:s|re|ve|ll|d|m|t)\b", re.I)
FIRST = re.compile(r"\b(?:I|me|my|mine|we|us|our|ours)\b")
NOMIN = re.compile(r"\b\w{4,}(?:tion|sion|ment|ness|ity)s?\b", re.I)
LY = re.compile(r"\b\w{4,}ly\b", re.I)
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|get|gets|got)\s+"
    r"(?:\w+ed|known|built|made|given|taken|written|done|seen|kept|held|sent|left|"
    r"put|set|found|lost|drawn|shown|told|brought|caught|dealt|meant|paid|read|run)\b", re.I)
CONN = re.compile(
    r"^(?:However|Moreover|Furthermore|Additionally|Therefore|Thus|Consequently|"
    r"In addition|Also|But|And|So|Then|Still|Yet|Meanwhile|Instead|Nevertheless|"
    r"Nonetheless|Hence|Overall|Finally|First|Second|Third|Indeed|Besides)\b", re.I)
NOTBUT = re.compile(
    r"\bnot (?:just |only |merely |simply )?[^.!?;]{1,70}?\bbut\b"
    r"|\bis not [^.!?;]{1,50}?[.;] (?:it|that) is\b"
    r"|\brather than\b", re.I)
TRIAD = re.compile(r"\b\w+, \w+,? and \w+\b")
ADJ3 = re.compile(r"\b(\w+ly )?(\w+), (\w+), (\w+) (?:\w+)\b")
HEDGE = re.compile(
    r"\b(?:it is important to note|it is worth noting|in conclusion|in summary|"
    r"that said|at its core|the real question is|what really matters|let's dive|"
    r"let us delve|here's the thing|make no mistake)\b", re.I)

# Every feature: (label, direction preference tuning pushes it, AI reference)
# "hi" means AI writes it higher than humans, "lo" means lower.
AI_REF = {
    "cv_sentence_len":   ("lo", 0.376),
    "mean_sentence_len": (None, 24.8),
    "long_words_1k":     ("hi", 444),
    "mean_word_len":     ("hi", 6.12),
    "nominalizations_1k":("hi", 75),
    "ly_adverbs_1k":     ("hi", 17.9),
    "passive_1k":        ("hi", 20.9),
    "mattr50":           ("hi", 0.827),
    "first_person_1k":   ("lo", 2.19),
    "contractions_1k":   ("lo", 0.15),
    "questions_1k":      ("lo", 0.22),
    "repeated_openers":  ("lo", 2.7),
    "connective_openers":("lo", 5.6),
    "commas_1k":         ("hi", 71.2),
    "semicolons_1k":     ("hi", 4.47),
    "em_dashes_1k":      ("hi", 4.06),
    "ai_lexicon_1k":     ("hi", None),
}
LABELS = {
    "cv_sentence_len": "sentence-length CV", "mean_sentence_len": "mean sentence length",
    "long_words_1k": "long words (7+) /1k", "mean_word_len": "mean word length",
    "nominalizations_1k": "nominalizations /1k", "ly_adverbs_1k": "-ly adverbs /1k",
    "passive_1k": "passive voice /1k", "mattr50": "lexical diversity MATTR-50",
    "first_person_1k": "first person /1k", "contractions_1k": "contractions /1k",
    "questions_1k": "questions /1k", "repeated_openers": "repeated openers /100",
    "connective_openers": "connective openers %", "commas_1k": "commas /1k",
    "semicolons_1k": "semicolons /1k", "em_dashes_1k": "em dashes /1k",
    "ai_lexicon_1k": "AI-lexicon words /1k",
}


def prose(md):
    """Strip everything that is not the author's sentences."""
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = re.sub(r"~~~.*?~~~", "", md, flags=re.S)
    md = "\n".join(l for l in md.split("\n") if not l.lstrip().startswith("|"))
    md = re.sub(r"^\s{4,}\S.*$", "", md, flags=re.M)
    md = re.sub(r"^#{1,6} .*$", "", md, flags=re.M)
    md = re.sub(r"^\s*[-*+]\s+", "", md, flags=re.M)
    md = re.sub(r"^\s*\d+\.\s+", "", md, flags=re.M)
    md = re.sub(r"^>\s?", "", md, flags=re.M)
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"`[^`]+`", "CODE", md)
    md = re.sub(r"<[^>]+>", "", md)
    md = re.sub(r"https?://\S+", "URL", md)
    return md


def measure(text):
    t = prose(text)
    words = re.findall(r"[A-Za-z']+", t)
    n = len(words)
    if n < 120:
        return None
    low = [w.lower() for w in words]
    per1k = lambda c: round(c / n * 1000, 2)
    sents = [s.strip() for s in SENT.split(t) if len(s.split()) > 2]
    if len(sents) < 8:
        return None
    lens = [len(s.split()) for s in sents]
    opens = [s.split()[0].lower() for s in sents if s.split()]
    rep = sum(1 for a, b in zip(opens, opens[1:]) if a == b)
    mattr = (sum(len(set(low[i:i + 50])) / 50 for i in range(n - 49)) / (n - 49)
             if n >= 50 else 0)
    paras = [p.strip() for p in re.split(r"\n\s*\n", t) if len(p.split()) > 4]
    closers = [p for p in paras
               if len(SENT.split(p)) > 1 and len(SENT.split(p)[-1].split()) < 8]
    return {
        "_words": n, "_sentences": len(sents), "_paragraphs": len(paras),
        "cv_sentence_len": round(st.pstdev(lens) / st.mean(lens), 3),
        "mean_sentence_len": round(st.mean(lens), 1),
        "long_words_1k": per1k(sum(1 for w in words if len(w) >= 7)),
        "mean_word_len": round(sum(len(w) for w in words) / n, 2),
        "nominalizations_1k": per1k(len(NOMIN.findall(t))),
        "ly_adverbs_1k": per1k(len(LY.findall(t))),
        "passive_1k": per1k(len(PASSIVE.findall(t))),
        "mattr50": round(mattr, 3),
        "first_person_1k": per1k(len(FIRST.findall(t))),
        "contractions_1k": per1k(len(CONTR.findall(t))),
        "questions_1k": per1k(t.count("?")),
        "repeated_openers": round(rep / max(len(sents) - 1, 1) * 100, 1),
        "connective_openers": round(
            sum(1 for s in sents if CONN.match(s)) / len(sents) * 100, 1),
        "commas_1k": per1k(t.count(",")),
        "semicolons_1k": per1k(t.count(";")),
        "em_dashes_1k": per1k(len(re.findall(r"[—–]", t))),
        "ai_lexicon_1k": per1k(sum(1 for w in low if w in AI_LEAN)),
        "_flags": {
            "AI-lexicon words": sorted({w for w in low if w in AI_LEAN}),
            "Claude-family words": sorted({w for w in low if w in CLAUDE_LEAN}),
            "Kobak excess style words": sorted(
                {w for w in low if w in KOBAK and w not in KOBAK_NOISE}),
            "plain words kept (good)": sorted({w for w in low if w in HUMAN_LEAN}),
            "not-X-but-Y": NOTBUT.findall(t),
            "triads": TRIAD.findall(t),
            "hedge templates": HEDGE.findall(t),
            "short closers": f"{len(closers)}/{len(paras)} paragraphs"
                             if paras else "n/a",
        },
    }


def calibrate(directory):
    rows = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith((".md", ".txt")):
            continue
        m = measure(open(os.path.join(directory, name), encoding="utf-8").read())
        if m:
            rows.append(m)
    if len(rows) < 8:
        sys.exit(f"need at least 8 usable texts, got {len(rows)}")
    bands = {"_corpus": os.path.abspath(directory), "_texts": len(rows)}
    for key in AI_REF:
        vals = sorted(r[key] for r in rows)
        q = lambda p: vals[min(int(p * len(vals)), len(vals) - 1)]
        bands[key] = {"p10": q(0.10), "p50": q(0.50), "p90": q(0.90),
                      "min": vals[0], "max": vals[-1]}
    json.dump(bands, open(BANDS_FILE, "w"), indent=1)
    print(f"calibrated on {len(rows)} texts -> {BANDS_FILE}")
    for key in AI_REF:
        b = bands[key]
        print(f"  {LABELS[key]:28} p10 {b['p10']:>8}  median {b['p50']:>8}  p90 {b['p90']:>8}")


def verdict(key, got, band):
    """inside / below / above the human band, and whether that is the AI side."""
    lo, hi = band["p10"], band["p90"]
    if lo <= got <= hi:
        return "ok"
    side = "above" if got > hi else "below"
    push = AI_REF[key][0]
    if push and ((push == "hi" and side == "above") or (push == "lo" and side == "below")):
        return f"{side} band, AI side"
    return f"{side} band, overshot"


def report(path, as_json=False):
    m = measure(open(path, encoding="utf-8").read())
    if not m:
        print(f"{os.path.basename(path)}: too short to measure (need ~120 words, 8 sentences)")
        return
    bands = json.load(open(BANDS_FILE)) if os.path.exists(BANDS_FILE) else None
    if as_json:
        print(json.dumps({"file": path, "metrics": m,
                          "verdicts": {k: verdict(k, m[k], bands[k])
                                       for k in AI_REF if bands and k in bands}}, indent=1))
        return
    print(f"\n{os.path.basename(path)}  {m['_words']} words, "
          f"{m['_sentences']} sentences, {m['_paragraphs']} paragraphs\n")
    if not bands:
        sys.exit("no bands.json; run --calibrate DIR first")
    print(f"{'feature':30}{'this':>9}{'human band':>18}{'AI':>8}   verdict")
    bad = 0
    for key in AI_REF:
        b, got = bands[key], m[key]
        ai = AI_REF[key][1]
        v = verdict(key, got, b)
        if v != "ok":
            bad += 1
        band = f"{b['p10']} - {b['p90']}"
        print(f"{LABELS[key]:30}{got:>9}{band:>18}{(ai if ai is not None else '-'):>8}   "
              f"{'' if v == 'ok' else v}")
    print(f"\n{len(AI_REF) - bad}/{len(AI_REF)} features inside the human band"
          f" (p10-p90 of {bands['_texts']} human texts)\n")
    for label, v in m["_flags"].items():
        if isinstance(v, list):
            print(f"{'  ' if not v else '! '}{label}: {', '.join(v[:12]) if v else 'none'}"
                  f"{' …' if len(v) > 12 else ''}")
        else:
            print(f"  {label}: {v}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--calibrate":
        calibrate(args[1])
    elif args[0] == "--json":
        for p in args[1:]:
            report(p, as_json=True)
    else:
        for p in args:
            report(p)

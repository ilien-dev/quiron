#!/usr/bin/env python3
"""Candidate features: AUC of each group against held-out humans (0.5 = no signal).

  explore.py NAME=GLOB ...    first group must be the held-out humans
"""
import glob, os, re, sys, statistics as st
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import aimeter  # noqa

STOP = set("""a an the and or but if of to in on at by for with from as is are was were be been being it its
this that these those i you he she we they me my your our their his her them us not no so do does did have has had
can could will would should may might just also then than there here what which who when where why how all any
some more most very about into out up down over only own same such too s t don into because while each other
""".split())
SENT = re.compile(r"(?<=[.!?])\s+")
WORD = re.compile(r"[A-Za-z][A-Za-z'-]+")


def content(s):
    return {w.lower().rstrip("s") for w in WORD.findall(s) if w.lower() not in STOP and len(w) > 2}


def feats(md):
    t = aimeter.prose(md)
    words = WORD.findall(t)
    n = len(words)
    if n < 120:
        return None
    sents = [s for s in SENT.split(re.sub(r"\s+", " ", t)) if len(s.split()) > 3]
    cs = [content(s) for s in sents]
    red = 0
    for i in range(len(cs)):
        for j in range(i + 1, min(i + 4, len(cs))):
            a, b = cs[i], cs[j]
            if a and b and len(a & b) / len(a | b) >= 0.3:
                red += 1
    paras = [p for p in re.split(r"\n\s*\n", t) if len(p.split()) > 8]
    pc = [content(p) for p in paras]
    adj = [len(a & b) / len(a | b) for a, b in zip(pc, pc[1:]) if a | b]
    raw = re.sub(r"```.*?```", "", md, flags=re.S)
    per1k = lambda c: c / n * 1000
    caps = sum(1 for m in re.finditer(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-zA-Z]+", t, re.M))
    return {
        "redund_100s": red / max(len(sents), 1) * 100,
        "para_overlap": st.mean(adj) if adj else 0,
        "numbers_1k": per1k(len(re.findall(r"\b\d[\d.,]*\b", t))),
        "links_1k": per1k(len(re.findall(r"\]\(https?://|https?://", md))),
        "inline_code_1k": per1k(len(re.findall(r"`[^`\n]+`", raw))),
        "midcaps_1k": per1k(caps),
        "exclaim_1k": per1k(t.count("!")),
        "ellipsis_1k": per1k(t.count("...") + t.count("…")),
        "you_1k": per1k(len(re.findall(r"\byou(r|'re|'ll|'ve)?\b", t, re.I))),
        "list_items_1k": per1k(len(re.findall(r"^\s*(?:[-*+]|\d+\.)\s", raw, re.M))),
        "codeblocks_1k": per1k(md.count("```") / 2),
        "bold_1k": per1k(len(re.findall(r"\*\*[^*]+\*\*", raw))),
        "colon_1k": per1k(t.count(":")),
        "sent_start_so_and_but": sum(1 for s in sents if re.match(r"(So|And|But|Also|Now|Well|Oh|Anyway)\b", s)) / max(len(sents), 1) * 100,
        "concessive_1k": per1k(len(re.findall(r"\b(?:though|although|whereas|albeit)\b", t, re.I))),
        "downtoners_1k": per1k(len(re.findall(r"\b(?:barely|hardly|nearly|almost|slightly|somewhat|partly|partially|mildly|scarcely|a bit|a little|kind of|sort of|more or less)\b", t, re.I))),
        "adj_doublets_1k": per1k(len(re.findall(r"\b(?:a|an|the|is|are|was|were|more|most|both|so|and)\s+([a-z]{3,}(?:ful|ive|ous|al|ic|ent|ant|ble|less|ing|ed|y))\s+and\s+([a-z]{3,}(?:ful|ive|ous|al|ic|ent|ant|ble|less|ing|ed|y))\b", t))),
        "synth_neg_1k": per1k(len(re.findall(r"\b(?:no|none|nothing|nobody|nowhere|neither|nor|never)\b", t, re.I))),
        "which_rel_1k": per1k(len(re.findall(r",\s+which\s+(?:is|was|are|were|means|meant|makes|made|gives|allows|lets|leads|results|helps)\b", t))),
        "pers_aside_1k": per1k(len(re.findall(r"\([^()]{0,120}\b(?:I|I'm|I've|I'd|my|me|probably|I think)\b[^()]{0,120}\)", t))),
        "particle_open": sum(1 for s in sents if re.match(r"(?:Well|Now|Anyway|Oh|Look|Sure|OK|Okay|Mind you)\b", s)) / max(len(sents), 1) * 100,
        "prescr_close": (lambda ps: (len(re.findall(r"\b(?:should|must|need to|needs to|it's time to|let's|make sure|remember)\b", ps[-1], re.I)) + 1) / (len(re.findall(r"\b(?:should|must|need to|needs to|it's time to|let's|make sure|remember)\b", " ".join(ps[:-1]), re.I)) / max(len(ps) - 1, 1) + 1))(paras) if len(paras) > 2 else 1,
        "last_para_words": len(paras[-1].split()) if paras else 0,
        "first_para_words": len(paras[0].split()) if paras else 0,
    }


def auc(ai, hu):
    if not ai or not hu:
        return float("nan")
    s = sum((a > h) + 0.5 * (a == h) for a in ai for h in hu)
    return s / (len(ai) * len(hu))


def main():
    groups = []
    for arg in sys.argv[1:]:
        name, pat = arg.split("=", 1)
        fs = sorted(glob.glob(pat)) if "*" in pat else [l.strip() for l in open(pat) if l.strip()]
        vals = [v for v in (feats(open(f).read()) for f in fs) if v]
        groups.append((name, vals))
    keys = list(groups[0][1][0].keys())
    hname, hu = groups[0]
    print(f"{'feature':24}" + "".join(f"{g[0][:12]:>13}" for g in groups) + "   AUC(ai>human) per group")
    for k in keys:
        meds = "".join(f"{st.median(v[k] for v in g[1]):13.2f}" for g in groups)
        aucs = "  ".join(f"{auc([v[k] for v in g[1]], [v[k] for v in hu]):.2f}" for g in groups[1:])
        print(f"{k:24}{meds}   {aucs}")
    print("n:", [len(g[1]) for g in groups])


if __name__ == "__main__":
    main()

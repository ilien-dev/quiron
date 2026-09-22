#!/usr/bin/env python3
"""Walk every point this skill makes, one at a time, and report the state of each.

FAIL is reserved for tells that are wrong on sight. Anything a careful writer does
on purpose (a list of three real things, a sentence about the previous version)
comes back as READ with the evidence quoted, because a checker that fails a
legitimate list is a checker a loop can never satisfy.

aimeter.py answers "are the rates inside the human band". This answers the other
half: "has every pattern in Part A actually been checked on this text". It exists
so that a claim of coverage can be verified instead of felt.

Three states per item:
  PASS    nothing found by a check that can see this pattern
  FAIL    found, with the offending text quoted
  READ    no regex can settle this one; a person or the model must read and rule

Exit code is the number of FAIL items, so a loop can stop on zero.

Usage:
  audit.py FILE            full checklist
  audit.py --brief FILE    only FAIL and READ items
  audit.py --json FILE
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# (id, name, kind, pattern or None, note)
# kind: "re" regex over prose, "md" regex over raw markdown, "read" needs judgement
CHECKS = [
    ("A1", "not X but Y", "re",
     r"\bnot (?:just |only |merely |simply )?[^.!?;]{1,70}?\bbut\b"
     r"|\bis not [^.!?;]{1,50}?[.;]\s*(?:it|that) is\b|\brather than\b", None),
    ("A2a", "one-line closer paragraphs", "para", None,
     "a paragraph of one short sentence that restates the one above it"),
    ("A2b", "dramatic fragment rows", "frag", None,
     "three or more verbless fragments in a row, or word.spaced.emphasis"),
    ("A3", "sayings that sound deep", "re",
     r"\b(?:the real question is|at its core|in reality|what really matters|"
     r"fundamentally,|the deeper issue|the heart of the matter|is the \w+ of the \w+|"
     r"becomes a trap|the language of|the currency of|the architecture of)\b", None),
    ("A4", "staged run-up", "re",
     r"\b(?:let's dive|let us dive|let's explore|let's break this down|"
     r"here's what you need to know|now let's look|without further ado|"
     r"here's the thing|the thing is,|let's be honest|real talk|"
     r"here's (?:the|where) (?:part|it gets)|buckle up)\b", None),
    ("A5", "arguing with no one", "re",
     r"\b(?:this isn't (?:mainly )?about|i'm not saying|to be clear,|"
     r"don't get me wrong|this is not to say|some might say|"
     r"a tempting approach|one might be tempted|you might think.{0,30}but|"
     r"it would be easy to just)\b", None),
    ("A6a", "triads: x, y and z", "judge",
     r"\b[\w'`]+(?: [\w'`]+){0,3}, [\w'`]+(?: [\w'`]+){0,3},? and [\w'`]+(?: [\w'`]+){0,3}\b", None),
    ("A6c", "three parallel clauses in one sentence", "judge",
     r"[^.!?]*?\w+ \w+,[^.!?,]{10,}?,[^.!?,]{0,45}? and [^.!?]{5,}?[.!?]", None),
    ("A6b", "adjective triads", "judge",
     r"\ba \w+, \w+, \w+ \w+\b|\b\w+, \w+, (?:and )?(?:completely|entirely|utterly) \w+\b", None),
    ("A7", "repeated sentence openers", "metric", "repeated_openers",
     "a rate, not a binary: band is the verdict, and zero is as wrong as too many"),
    ("A8", "em and en dashes", "re", r"[—–]", None),
    ("A9", "stacked qualifiers", "re",
     r"\b(?:to be fair|it's also possible|could potentially|might arguably|"
     r"in some cases it may|this is an inference)\b", None),
    ("A10", "hyphenated pairs after a noun", "re",
     r"\bis (?:third-party|cross-functional|client-facing|data-driven|high-quality|"
     r"real-time|long-term|end-to-end|well-known)\b", None),
    ("A11", "passive voice rate", "metric", "passive_1k", None),
    ("A12", "inflated significance", "re",
     r"\b(?:stands as a testament|a pivotal moment|plays a key role|"
     r"marking a (?:shift|turning)|underscores its importance|reflects a broader|"
     r"enduring legacy|lasting legacy|setting the stage for|evolving landscape|"
     r"indelible mark|the future looks bright|exciting times ahead|"
     r"a step in the right direction)\b", None),
    ("A13", "vague connection", "judge",
     r"\b(?:is |are |was |were )?associated with\b|\bin association with\b"
     r"|\bconnected to\b|\bin connection with\b|\blinked to\b|\btied to\b", None),
    ("A14", "shallow -ing riders", "re",
     r",\s(?:highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|"
     r"contributing to|cultivating|fostering|encompassing|showcasing)\b", None),
    ("A15", "sales language", "re",
     r"\b(?:boasts|vibrant|profound|exemplifies|commitment to|natural beauty|"
     r"nestled|in the heart of|groundbreaking|renowned|diverse array|breathtaking|"
     r"must-visit|stunning|seamlessly integrates)\b", None),
    ("A16", "borrowed authority", "re",
     r"\b(?:experts (?:argue|believe|say)|observers have cited|industry reports|"
     r"some critics|several publications|studies (?:show|suggest) that)\b"
     r"|\bover \d[\d,.]* followers\b", None),
    ("A17", "avoiding is, are, has", "re",
     r"\b(?:serves as|stands as|functions as|operates as|represents an?"
     r"|boasts an?|maintains an?)\b", None),
    ("A18", "bold as decoration", "md", r"^\s*[-*]\s+\*\*[^*]+\*\*:", None),
    ("A19a", "Title Case headings", "md",
     r"^#{1,6} (?:[A-Z]\w+ ){2,}[A-Z]\w+\s*$", None),
    ("A19b", "emoji or arrows in headings", "md",
     r"^#{1,6}.*[→⇒\U0001F300-\U0001FAFF]", None),
    ("A19c", "a rule between every section", "md", None,
     "counted below"),
    ("A20", "curly quotes", "re", "[“”]", None),
    ("A21", "chatbot residue", "re",
     r"\b(?:i hope this helps|of course!|certainly!|great question|"
     r"you're absolutely right|would you like|want me to|should i continue|"
     r"let me know if)\b", None),
    ("A22", "knowledge-limit disclaimers", "re",
     r"\b(?:as of my|up to my last|while specific details are limited|"
     r"based on available information|not publicly available|"
     r"not widely documented|in the (?:provided|available) sources|"
     r"maintains a low profile|it is believed that)\b", None),
    ("A23", "heading repeated in first sentence", "md", None, "computed below"),
    ("A24", "writing about the previous version", "judge",
     r"\b(?:previously|formerly|used to|this replaces|instead of the old|"
     r"the (?:old|previous) (?:approach|version|implementation))\b", None),
    ("A25", "structural uniformity", "read", None,
     "do sections all open and close on the same move? are paragraphs the same length?"),
    ("B1", "AI-lexicon words", "lex", "ai-lean.txt", None),
    ("B2", "Claude-family words", "lexrate", "claude-lean.txt",
     "a rate: four or more distinct words is the signal, one or two is English"),
    ("B3", "hedge templates", "re",
     r"\b(?:it is important to note|it's important to note|it is worth noting|"
     r"in conclusion|in summary|that said,|make no mistake)\b", None),
    ("B4", "plain words kept", "lexgood", "human-lean.txt", None),
    ("C1", "the 17 rates", "metricall", None, None),
    ("V1", "voice survived the edit", "read", None,
     "opinions, mixed feelings, asides, a first-person choice the writer can explain"),
    ("V2", "no fact was added or lost", "read", None,
     "every number, name, date, quote and citation traceable to the source"),
]

SENT = re.compile(r"(?<=[.!?])\s+")


def prose(md):
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = "\n".join(l for l in md.split("\n") if not l.lstrip().startswith("|"))
    md = re.sub(r"^#{1,6} .*$", "", md, flags=re.M)
    md = re.sub(r"`[^`]+`", "CODE", md)
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"https?://\S+", "URL", md)
    return md


def run(path):
    raw = open(path, encoding="utf-8").read()
    body = re.sub(r"```.*?```", "", raw, flags=re.S)
    text = prose(raw)
    out = subprocess.run(
        [sys.executable, os.path.join(HERE, "aimeter.py"), "--json", path],
        capture_output=True, text=True)
    meter = json.loads(out.stdout) if out.stdout.strip().startswith("{") else None
    results = []

    for cid, name, kind, arg, note in CHECKS:
        state, detail = "PASS", ""
        if kind == "judge":
            hits = re.findall(arg, text, re.I)
            if hits:
                flat = [h if isinstance(h, str) else " ".join(x for x in h if x)
                        for h in hits]
                state = "READ"
                detail = "rule on each: " + " | ".join(
                    sorted(set(f.strip()[:38] for f in flat))[:4])
        elif kind == "re":
            hits = re.findall(arg, text, re.I)
            if hits:
                state = "FAIL"
                flat = [h if isinstance(h, str) else " ".join(x for x in h if x)
                        for h in hits]
                detail = "; ".join(sorted(set(f.strip() for f in flat))[:6])
        elif kind == "md":
            if arg:
                hits = re.findall(arg, body, re.M)
                if hits:
                    state, detail = "FAIL", "; ".join(str(h)[:50] for h in hits[:5])
            elif cid == "A19c":
                heads = len(re.findall(r"^#{1,6} ", body, re.M))
                rules = len(re.findall(r"^---\s*$", body, re.M))
                if heads and rules >= heads:
                    state, detail = "FAIL", f"{rules} rules for {heads} headings"
            elif cid == "A23":
                bad = []
                for m in re.finditer(r"^#{1,6} (.+)$", body, re.M):
                    head = set(re.findall(r"\w+", m.group(1).lower())) - {
                        "the", "a", "an", "of", "and", "to", "is", "in", "on", "for"}
                    after = body[m.end():m.end() + 400].strip().split("\n\n")
                    if not after or not head:
                        continue
                    first = set(re.findall(r"\w+", after[0].lower()))
                    if len(after[0].split()) < 14 and head and head <= first:
                        bad.append(m.group(1)[:40])
                if bad:
                    state, detail = "FAIL", "; ".join(bad[:4])
        elif kind == "para":
            paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
            bad = []
            for prev, p in zip(paras, paras[1:]):
                if len(p.split()) < 12 and len(SENT.split(p)) == 1 and len(prev.split()) > 25:
                    shared = set(re.findall(r"\w{5,}", p.lower())) & \
                             set(re.findall(r"\w{5,}", prev.lower()))
                    if shared:
                        bad.append(p[:50])
            if bad:
                state, detail = "FAIL", "; ".join(bad[:4])
        elif kind == "frag":
            # a fragment is a short clause with no finite verb; a row of them is the tell
            VERB = re.compile(r"\b(?:is|are|was|were|be|been|am|do|does|did|has|have|had|"
                              r"can|could|will|would|should|may|might|must|\w+s|\w+ed)\b", re.I)
            run_len, worst = 0, 0
            example = ""
            for s_ in SENT.split(text):
                s_ = s_.strip()
                if s_ and len(s_.split()) <= 5 and not VERB.search(s_):
                    run_len += 1
                    if run_len > worst:
                        worst, example = run_len, s_[:40]
                else:
                    run_len = 0
            spaced = re.findall(r"\b\w+\.\w+\.\w+\.", text)
            if worst >= 3 or spaced:
                state = "FAIL"
                detail = (f"{worst} verbless fragments in a row near '{example}'"
                          if worst >= 3 else "; ".join(spaced[:3]))
        elif kind == "lexrate":
            words = [w.lower() for w in re.findall(r"[A-Za-z']+", text)]
            lex = set(open(os.path.join(HERE, "lexicons", arg)).read().split())
            found = sorted(set(words) & lex)
            rate = round(sum(1 for w in words if w in lex) / max(len(words), 1) * 1000, 2)
            detail = f"{len(found)} distinct, {rate}/1k: {', '.join(found[:8])}" if found else "none"
            if len(found) >= 4 or rate > 4:
                state = "FAIL"
        elif kind in ("lex", "lexgood"):
            words = set(w.lower() for w in re.findall(r"[A-Za-z']+", text))
            lex = set(open(os.path.join(HERE, "lexicons", arg)).read().split())
            found = sorted(words & lex)
            if kind == "lex" and found:
                state, detail = "FAIL", ", ".join(found[:10])
            elif kind == "lexgood":
                state = "PASS" if found else "FAIL"
                detail = ", ".join(found[:10]) if found else "no plain everyday words found"
        elif kind == "metric":
            if meter:
                v = meter["verdicts"].get(arg, "?")
                if v != "ok":
                    state, detail = "FAIL", f"{meter['metrics'][arg]} ({v})"
                else:
                    detail = str(meter["metrics"][arg])
        elif kind == "metricall":
            if meter:
                bad = {k: v for k, v in meter["verdicts"].items() if v != "ok"}
                if bad:
                    state = "FAIL"
                    detail = "; ".join(f"{k} {meter['metrics'][k]} {v}"
                                       for k, v in list(bad.items())[:6])
                else:
                    detail = "all 17 inside the band"
        elif kind == "read":
            state, detail = "READ", note or ""
        results.append((cid, name, state, detail, note))
    return results


def main():
    brief = "--brief" in sys.argv
    as_json = "--json" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    fails = 0
    for path in paths:
        res = run(path)
        nf = sum(1 for r in res if r[2] == "FAIL")
        fails += nf
        if as_json:
            print(json.dumps({"file": path, "fails": nf,
                              "items": [dict(zip(("id", "name", "state", "detail"), r[:4]))
                                        for r in res]}, indent=1))
            continue
        print(f"\n{os.path.basename(path)}")
        print(f"{'':4}{'check':38}{'state':7}detail")
        for cid, name, state, detail, note in res:
            if brief and state == "PASS":
                continue
            mark = {"PASS": "  ", "FAIL": "!!", "READ": "??"}[state]
            print(f"{mark}{cid:5}{name:38}{state:7}{detail[:70]}")
        reads = sum(1 for r in res if r[2] == "READ")
        print(f"\n{len(res) - nf - reads} pass, {nf} fail, {reads} need a human read")
    return fails


if __name__ == "__main__":
    sys.exit(min(main(), 120))

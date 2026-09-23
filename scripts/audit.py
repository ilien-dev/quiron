#!/usr/bin/env python3
"""Walk every point this skill makes, one at a time, and report the state of each.

Every check here was run over held-out human texts and 2026 assistant texts on the
same titles (scripts/evaluate.py), and its state was chosen from what it did there.
A check that fires on more than about 5% of human texts cannot FAIL, however
often assistants trip it, because a loop that fails real human writing can never
converge. Those checks report TELL instead: a measured tendency, not an error.
One TELL is normal in human writing; several together are the signal, and the
combined check T1 fails on that.

aimeter.py answers "are the rates inside the human band". This answers the other
half: "has every pattern in Part A actually been checked on this text". It exists
so that a claim of coverage can be verified instead of felt.

Four states per item:
  PASS    nothing found by a check that can see this pattern
  FAIL    found, with the offending text quoted; almost no human text does this
  TELL    found; humans do it too, assistants more often; counts toward T1
  READ    no regex can settle this one; a person or the model must read and rule

Exit code is the number of FAIL items, so a loop can stop on zero.

Usage:
  audit.py FILE            full checklist
  audit.py --brief FILE    only FAIL, TELL and READ items
  audit.py --json FILE
  audit.py --sample PATH FILE  a file or folder of the writer's own texts: a TELL that
                               fires there too is their habit and is not counted
  audit.py --review [--json] FILE
                           sentences for the writer to decide on, one at a time; never
                           part of the checklist, T1 or check.sh, and the exit code is 0
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from aimeter import prose, lexicon_name, lang_guess, lang_warning, BANDED, LAYOUT, BANDS_FILE, LANG  # noqa: E402

# Thresholds for the combined checks. Chosen from a grid over held-out human posts and
# 2026 assistant posts: the setting that kept human texts failing the whole checklist
# near 5% while catching the most assistant posts (references/numbers.md has the numbers).
# A band file for another register can override any of them under "_thresholds".
AI_SIDE_MAX = 5      # C1 fails at this many rates outside the band on the AI side
OVERSHOT_MAX = 6     # C2 fails at this many rates outside the band on the far side
TELLS_MAX = 5        # T1 fails at this many TELL items at once
LEXICON_MIN = 3      # B1 fails at this many distinct AI-lexicon words


def _thresholds():
    try:
        return json.load(open(BANDS_FILE)).get("_thresholds", {})
    except (OSError, ValueError):
        return {}


globals().update({k: v for k, v in _thresholds().items()
                  if k in ("AI_SIDE_MAX", "OVERSHOT_MAX", "TELLS_MAX", "LEXICON_MIN")})

# (id, name, kind, pattern or None, note)
# kind: "re" FAIL on a regex over prose; "tell" TELL on a regex over prose;
# "tellmd" TELL on a regex over raw markdown; "judge" and "judgemd" READ with
# evidence, over prose and raw markdown; "read"
# needs judgement with no evidence to quote; other kinds are computed in run().
CHECKS = [
    ("A1", "it's not X, it's Y", "tell",
     r"\b(?:it|this|that)(?:'s| is| was) not\b[^.!?]{1,80}[.;,:]\s*(?:it|this|that)(?:'s| is| was)\b"
     r"|\b(?:it|this|that) (?:isn't|wasn't)\b[^.!?]{1,80}[.;,:]\s*(?:it|this|that)(?:'s| is| was)\b"
     r"|\bno \w+(?: \w+)?, (?:no \w+(?: \w+)?, )?just\b", None),
    ("A1b", "not just X but Y; X rather than Y; ..., not Y.", "tell",
     r"\bnot (?:just|only|merely|simply)\b[^.!?]{1,80}\bbut\b|\brather than\b"
     r"|,\s+not (?:a |an |the )?[\w'-]+(?: [\w'-]+)?[.!]"
     r"|\b(?:that's|this is|it's|that is) (?:a |an |the )?[\w'-]+(?: [\w'-]+)?, not\b", None),
    ("A2a", "one-line closer paragraphs", "para", None,
     "a paragraph of one short sentence that restates the one above it"),
    ("A2b", "dramatic fragment rows", "frag", None,
     "three or more verbless fragments in a row, or word.spaced.emphasis"),
    ("A3", "sayings that sound deep", "tell",
     r"\b(?:the real question is|at its core|in reality,|what really matters|"
     r"fundamentally,|the deeper issue|the heart of the matter|becomes a trap|"
     r"the (?:language|currency|architecture) of (?:the|our|modern)\b)", None),
    ("A3b", "X is the Y of Z", "judge", r"\bis the \w+ of (?:the |a )?\w+\b", None),
    ("A4", "staged run-up", "tell",
     r"\b(?:here's the thing|the thing is,|let's be honest|real talk|buckle up|"
     r"without further ado|here's what you need to know|"
     r"here's (?:the|where) (?:part|it gets))\b", None),
    ("A4b", "let's dive in and friends", "tell",
     r"\blet's (?:dive|jump) in(?:to)?\b|\blet us dive\b|\blet's explore\b|"
     r"\blet's break (?:this|it) down\b|\blet's get started\b", None),
    ("A5", "arguing with no one", "tell",
     r"\b(?:this isn't (?:mainly )?about|i'm not saying|to be clear,|"
     r"don't get me wrong|this is not to say|some might say|"
     r"a tempting approach|one might be tempted|it would be easy to just)\b", None),
    ("A6a", "triads: x, y and z", "judge",
     r"\b[\w'`]+(?: [\w'`]+){0,3}, [\w'`]+(?: [\w'`]+){0,3},? and [\w'`]+(?: [\w'`]+){0,3}\b", None),
    ("A6b", "adjective triads", "judge",
     r"\ba \w+, \w+, \w+ \w+\b|\b\w+, \w+, (?:and )?(?:completely|entirely|utterly) \w+\b", None),
    ("A8", "em and en dashes", "tell", r"[—–]|\s--\s", None),
    ("A9", "stacked qualifiers", "tell",
     r"\b(?:to be fair|it's also possible|could potentially|might arguably|"
     r"in some cases it may|this is an inference)\b", None),
    ("A10", "hyphenated pairs after a noun", "tell",
     r"\bis (?:third-party|cross-functional|client-facing|data-driven|high-quality|"
     r"real-time|long-term|end-to-end|well-known)\b", None),
    ("A12", "inflated significance", "tell",
     r"\b(?:stands as a testament|a pivotal moment|plays a key role|"
     r"marking a (?:shift|turning)|underscores its importance|reflects a broader|"
     r"enduring legacy|lasting legacy|setting the stage for|evolving landscape|"
     r"indelible mark|the future looks bright|exciting times ahead|"
     r"a step in the right direction|paves? the way|paving the way|only time will tell)\b", None),
    ("A13", "vague connection", "judge",
     r"\b(?:is |are |was |were )?associated with\b|\bin association with\b"
     r"|\bconnected to\b|\bin connection with\b|\blinked to\b|\btied to\b", None),
    ("A14", "shallow -ing riders", "tell",
     r",\s(?:highlighting|underscoring|emphasizing|reflecting|symbolizing|"
     r"cultivating|fostering|encompassing|showcasing)\b", None),
    ("A14b", "-ing clause tacked on after a comma", "tell",
     r",\s(?:ensuring|contributing to|making it|allowing|enabling|giving|leaving|creating)\b", None),
    ("A15", "sales language", "tell",
     r"\b(?:boasts|vibrant|exemplifies|natural beauty|nestled|in the heart of|"
     r"groundbreaking|renowned|diverse array|breathtaking|must-visit|stunning|"
     r"seamlessly integrates)\b", None),
    ("A16", "borrowed authority", "tell",
     r"\b(?:experts (?:argue|believe|say)|observers have cited|industry reports|"
     r"some critics|several publications)\b|\bover \d[\d,.]* followers\b", None),
    ("A17", "avoiding is, are, has", "tell",
     r"\b(?:serves as|stands as|functions as|operates as|boasts an?)\b", None),
    ("A18", "bold labels on list items", "judgemd",
     r"^\s*(?:[-*]|\d+\.)\s+\*\*[^*]+\*\*\s*[:—–-]", None),
    ("A19", "Title Case headings", "titlecase", None,
     "three or more headings, three in four of them in Title Case"),
    ("A20", "curly quotes", "tell", "[“”]", None),
    ("A21", "chatbot residue", "re",
     r"\b(?:i hope this helps|of course!|certainly!|great question|"
     r"you're absolutely right|should i continue|is there anything else)\b", None),
    ("A22", "knowledge-limit disclaimers", "re",
     r"\b(?:as of my|up to my last|while specific details are limited|"
     r"based on available information|not publicly available|"
     r"not widely documented|in the (?:provided|available) sources|"
     r"maintains a low profile|it is believed that)\b", None),
    ("A23", "heading repeated in first sentence", "heading", None, "computed below"),
    ("A24", "writing about the previous version", "judge",
     r"\b(?:previously|formerly|this replaces|instead of the old|"
     r"the (?:old|previous) (?:approach|version|implementation))\b", None),
    ("A25", "structural uniformity", "read", None,
     "do sections all open and close on the same move? are paragraphs the same length?"),
    ("A26", "summary section at the end", "tellmd",
     r"^#{1,6}\s*(?:conclusion|final thoughts|wrapping up|wrap-up|key takeaways|"
     r"the bottom line|summary|in summary|takeaways)\b|\b(?:in conclusion|to sum up|to wrap up)\b", None),
    ("A27", "stock names and titles", "tell",
     r"\b(?:Elara|Kael|Aldric|Seraphina|Aris Thorne|Elias Vance|Sarah Chen|Emily Carter)\b", None),
    ("A28", "abstract 'a sense of' bundles", "tell",
     r"\b(?:a|the) (?:mix|blend|flicker|pang|glimmer|wave|weight|tapestry|symphony|dance) of \w+ and \w+\b", None),
    ("A29", "stock sensory cliches", "tell",
     r"\b(?:voice (?:was )?barely (?:above )?a whisper|air (?:was )?thick with|"
     r"hung in the air|pit of (?:her|his|my) stomach|a smile playing on|eyes never leaving|"
     r"casting long shadows|let out a breath (?:she|he|I) didn't know)\b", None),
    ("A32", "announcing what the post will cover", "tell",
     r"\bin this (?:post|article|tutorial|guide),? (?:we|I)(?:'ll| will| are going to|'m going to)\b"
     r"|\bwhether you're\b", None),
    ("A30", "showing, then explaining what it meant", "read", None,
     "a clause or sentence that explains what the one before already showed"),
    ("A31", "generic where a specific exists", "read", None,
     "names, numbers, dates or first-hand detail the source has but the text dropped"),
    ("B1", "AI-lexicon words", "lex", None, "the band file's lexicon, ai-lean.txt by default"),
    ("B2", "Claude-family words", "lexrate", "claude-lean.txt",
     "a rate: four or more distinct words is the signal, one or two is English"),
    ("B3", "hedge templates", "tell",
     r"\b(?:it is important to note|it's important to note|it is worth noting|"
     r"make no mistake)\b", None),
    ("C1", "rates on the AI side", "aiside", None, None),
    ("C2", "rates overshot", "overshot", None, None),
    ("T1", "tells together", "tells", None, None),
    ("V1", "voice survived the edit", "read", None,
     "opinions, mixed feelings, asides, a first-person choice the writer can explain"),
    ("V2", "no fact was added or lost", "read", None,
     "every number, name, date, quote and citation traceable to the source"),
]

# Spanish checks, used when the band file says "_lang": "es". Measured on 241 pre-2022
# Spanish dev.to posts and 32 assistant posts written in Spanish in 2026. The folklore
# phrases (cabe destacar, en el panorama actual, sumérgete, en conclusión, the gerund
# after a comma) were in 2 of the 32 assistant posts and in 4% to 10% of the human
# ones, so they are not checked.
CHECKS_ES = [
    ("E1", "no es X: es Y", "tell",
     r"\bno es [^.!?]{1,60}[.;,:]\s*es\b|\bno se trata de [^.!?]{1,60}[.;,:]\s*se trata de\b",
     "3% of human posts, 16% of assistant posts"),
    ("E2", "sección de conclusión al final", "tellmd",
     r"^#{1,6}\s*(?:conclusi[oó]n|conclusiones|resumen|reflexi[oó]n final|reflexiones finales|"
     r"para terminar|cierre)\b", "14% of human posts, 78% of assistant posts"),
    ("E3", "residuo de chatbot", "re",
     r"\b(?:espero que (?:esto|este (?:post|artículo)) te (?:ayude|sea útil)|excelente pregunta|"
     r"te gustaría que)\b|¡claro!", None),
]
if LANG == "es":
    CHECKS = [c for c in CHECKS if c[0] in ("A2a", "A2b", "A6a", "A13", "A23", "A25",
                                            "A30", "A31", "B1")] + CHECKS_ES + [
        c for c in CHECKS if c[0] in ("C1", "C2", "T1", "V1", "V2")]

SENT = re.compile(r"(?<=[.!?])\s+")

# Review items: patterns a reader notices that the rewrite loop must not act on alone.
# A1c (negated setup) is in 7% of held-out human posts and 31% of assistant posts, but
# fixing it inside the loop made rewrites read more AI to blind judges (numbers.md,
# "Checks measured and not shipped"), so only the writer decides, sentence by sentence.
NEGSET = re.compile(r"\b(?:isn't|wasn't|aren't|weren't|is not|was not|are not|were not)\b", re.I)
NEGSET_SKIP = re.compile(r"\b(?:but|because|if|when|unless|so)\b", re.I)
REFRAME = re.compile(r"(?:it's|it is|it was|that's|that is|this is|what |the (?:real|actual|point|answer)|"
                     r"instead|rather)", re.I)
NEGSET_WHY = [
    "It denies something nobody said, so the sentence after it sounds bigger than it is.",
    "It sits where the point should be: {where}.",
    "A short 'X isn't Y.' sentence like this is in 31% of assistant blog posts and 7% of "
    "human ones (held-out dev.to posts).",
]


def review(path):
    """Negated setups, with the reasons a reader may take them for AI. Blog bands only."""
    if lexicon_name() != "ai-lean.txt":
        return []
    items = []
    for n, para in enumerate(re.split(r"\n\s*\n", prose(open(path, encoding="utf-8").read()))):
        ss = [s_.strip() for s_ in SENT.split(para.replace("\n", " ")) if s_.strip()]
        for i, s_ in enumerate(ss):
            nxt = ss[i + 1] if i + 1 < len(ss) else ""
            opens, reframed = i == 0, bool(REFRAME.match(nxt))
            if (len(s_.split()) <= 12 and s_.endswith(".") and NEGSET.search(s_)
                    and not NEGSET_SKIP.search(s_) and (opens or reframed)):
                where = ("it opens the paragraph, before the real point" if opens
                         else "right before the sentence that makes the real point")
                items.append({"id": "A1c", "name": "negated setup", "paragraph": n + 1,
                              "sentence": s_, "next": nxt,
                              "why": [w.format(where=where) for w in NEGSET_WHY]})
    return items
MINOR = set("a an the and or but of to in on for with vs at by from is as into via".split())


def flat(hits):
    return [h if isinstance(h, str) else " ".join(x for x in h if x) for h in hits]


def run(path, samples=()):
    """Every check on one text. A TELL that also fires in the writer's own sample
    texts is the writer's habit, not a tell: it is reported and not counted."""
    habits = {r[0] for p in samples for r in run(p) if r[2] == "TELL"}
    raw = open(path, encoding="utf-8").read()
    body = re.sub(r"```.*?```", "", raw, flags=re.S)
    text = prose(raw)
    sample_args = [x for p in samples for x in ("--sample", p)]
    out = subprocess.run(
        [sys.executable, os.path.join(HERE, "aimeter.py"), "--json", *sample_args, path],
        capture_output=True, text=True)
    meter = json.loads(out.stdout) if out.stdout.strip().startswith("{") else None
    verdicts = meter["verdicts"] if meter else {}
    results = []
    unbanded = lang_guess(raw) not in BANDED

    for cid, name, kind, arg, note in CHECKS:
        state, detail = "PASS", ""
        if kind in ("re", "tell", "judge", "tellmd", "judgemd"):
            hits = flat(re.findall(arg, body if kind.endswith("md") else text,
                                   re.I | re.M))
            if hits:
                state = {"re": "FAIL", "judge": "READ", "judgemd": "READ"}.get(kind, "TELL")
                detail = ("rule on each: " if kind.startswith("judge") else "") + " | ".join(
                    sorted(set(h.strip()[:80] for h in hits))[:5])
        elif kind == "titlecase":
            heads = [re.findall(r"[A-Za-z][\w'.-]*", h)
                     for h in re.findall(r"^#{1,6} (.+)$", body, re.M)]
            heads = [w for w in heads if len(w) >= 3]
            tc = [w for w in heads
                  if not any(x[0].islower() and x.lower() not in MINOR for x in w)
                  and any(x[0].isupper() for x in w[1:])]
            if len(heads) >= 3 and len(tc) >= 0.75 * len(heads):
                state, detail = "TELL", f"{len(tc)} of {len(heads)} headings"
        elif kind == "heading":
            bad = []
            for m in re.finditer(r"^#{1,6} (.+)$", body, re.M):
                head = set(re.findall(r"\w+", m.group(1).lower())) - MINOR
                after = body[m.end():m.end() + 400].strip().split("\n\n")
                if not after or not head:
                    continue
                first = set(re.findall(r"\w+", after[0].lower()))
                if len(after[0].split()) < 14 and head <= first:
                    bad.append(m.group(1)[:40])
            if bad:
                state, detail = "READ", "restates its heading? " + "; ".join(bad[:4])
        elif kind == "para":
            paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
            bad = []
            for prev, p in zip(paras, paras[1:]):
                if (len(p.split()) < 12 and len(SENT.split(p)) == 1 and len(prev.split()) > 25
                        and not p.rstrip().endswith(":")):
                    shared = set(re.findall(r"\w{5,}", p.lower())) & \
                             set(re.findall(r"\w{5,}", prev.lower()))
                    if shared:
                        bad.append(p[:50])
            if bad:
                state, detail = "READ", "a restatement? " + "; ".join(bad[:4])
        elif kind == "frag":
            # a fragment is a short clause with no finite verb; a row of them is the tell
            VERB = re.compile(r"\b(?:is|are|was|were|be|been|am|do|does|did|has|have|had|"
                              r"can|could|will|would|should|may|might|must|\w+s|\w+ed)\b", re.I)
            run_len, worst, example = 0, 0, ""
            # list items are allowed to be short; only running prose can have fragments
            no_lists = prose("\n".join(l for l in body.split("\n")
                                       if not re.match(r"\s*(?:[-*+]|\d+\.)\s", l)))
            for s_ in SENT.split(no_lists):
                s_ = s_.strip()
                if s_ and len(s_.split()) <= 5 and not VERB.search(s_):
                    run_len += 1
                    if run_len > worst:
                        worst, example = run_len, s_[:40]
                else:
                    run_len = 0
            spaced = re.findall(r"\b\w+\.\w+\.\w+\.", text)
            if worst >= 3 or spaced:
                state = "TELL"
                detail = (f"{worst} verbless fragments in a row near '{example}'"
                          if worst >= 3 else "; ".join(spaced[:3]))
        elif kind == "lexrate":
            words = [w.lower() for w in re.findall(r"[A-Za-z']+", text)]
            lex = load_lex(arg)
            found = sorted(set(words) & lex)
            rate = round(sum(1 for w in words if w in lex) / max(len(words), 1) * 1000, 2)
            detail = f"{len(found)} distinct, {rate}/1k: {', '.join(found[:8])}" if found else "none"
            if len(found) >= 4 or rate > 4:
                state = "TELL"
        elif kind == "lex":
            words = set(w.lower() for w in re.findall(r"[A-Za-z']+", text))
            found = sorted(min(e & words) for e in lex_entries(arg or lexicon_name()) if e & words)
            if found:
                state = "FAIL" if len(found) >= LEXICON_MIN else "TELL"
                detail = ", ".join(found[:10])
        elif kind in ("aiside", "overshot"):
            if meter:
                tag, cap = ("AI side", AI_SIDE_MAX) if kind == "aiside" else ("overshot", OVERSHOT_MAX)
                bad = [k for k, v in verdicts.items() if v.endswith(tag)
                       and (not unbanded or k in LAYOUT)]
                detail = f"{len(bad)} (fails at {cap}): " + ", ".join(
                    f"{k} {meter['metrics'][k]}" for k in bad[:6]) if bad else "none"
                if len(bad) >= cap:
                    state = "FAIL"
        elif kind == "tells":
            tells = [r[0] for r in results if r[2] == "TELL"]
            detail = f"{len(tells)} (fails at {TELLS_MAX}): {', '.join(tells)}" if tells else "none"
            if len(tells) >= TELLS_MAX:
                state = "FAIL"
        elif kind == "read":
            state, detail = "READ", note or ""
        if state == "FAIL" and unbanded and kind in ("lex", "aiside", "overshot", "tells"):
            # no band file or lexicon is measured for this language, so a count cannot fail it
            state, detail = "READ", "no band file for this language, rough guide only: " + detail
        if state == "TELL" and cid in habits:
            state, detail = "PASS", "the writer's own habit (also in the sample): " + detail
        results.append((cid, name, state, detail, note))
    return results


def lex_entries(name):
    """One set of forms per line; '#' starts a comment."""
    path = os.path.join(HERE, "lexicons", name)
    return [e for e in (set(line.split("#")[0].split()) for line in open(path)) if e]


def load_lex(name):
    return set().union(*lex_entries(name))


def main():
    brief = "--brief" in sys.argv
    as_json = "--json" in sys.argv
    args = sys.argv[1:]
    samples = []
    while "--sample" in args:
        i = args.index("--sample")
        target = args[i + 1] if i + 1 < len(args) else ""
        if not os.path.exists(target):
            sys.exit(f"--sample needs an existing file or directory, got: {target or 'nothing'}")
        samples += ([os.path.join(target, n) for n in sorted(os.listdir(target))
                     if n.endswith((".md", ".txt"))] if os.path.isdir(target) else [target])
        del args[i:i + 2]
    paths = [a for a in args if not a.startswith("--")]
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        sys.exit(f"no such file: {', '.join(missing)}")
    if "--review" in sys.argv:
        for path in paths:
            items = review(path)
            if as_json:
                print(json.dumps({"file": path, "items": items}, indent=1))
                continue
            print(f"\n{os.path.basename(path)}: {len(items)} to review")
            for k, it in enumerate(items, 1):
                print(f"\n{k}. {it['id']} {it['name']}, paragraph {it['paragraph']}")
                print(f"   \"{it['sentence']}\"")
                for w in it["why"]:
                    print(f"   - {w}")
        return 0
    fails = 0
    for path in paths:
        res = run(path, samples)
        nf = sum(1 for r in res if r[2] == "FAIL")
        fails += nf
        if as_json:
            print(json.dumps({"file": path, "fails": nf,
                              "items": [dict(zip(("id", "name", "state", "detail"), r[:4]))
                                        for r in res]}, indent=1))
            continue
        print(f"\n{os.path.basename(path)}")
        warn = lang_warning(open(path, encoding="utf-8").read())
        if warn:
            print(warn)
        print(f"{'':4}{'check':40}{'state':7}detail")
        for cid, name, state, detail, note in res:
            if brief and state == "PASS":
                continue
            mark = {"PASS": "  ", "FAIL": "!!", "TELL": "~ ", "READ": "??"}[state]
            print(f"{mark}{cid:5}{name:40}{state:7}{detail}")
        count = lambda s: sum(1 for r in res if r[2] == s)
        print(f"\n{count('PASS')} pass, {nf} fail, {count('TELL')} tell, "
              f"{count('READ')} need a human read")
    return fails


if __name__ == "__main__":
    sys.exit(min(main(), 120))

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
shipped band file was built by build-corpus.sh from 167 dev.to posts by 21
authors, all published before 2022, the register this is meant for. Recalibrate
for any other register.

The AI reference column is the median of 42 assistant posts written in 2026 on
held-out titles (see AI_REF). The directions come from the published studies:
  TextPulse Research 2026, working papers on paired human/AI academic texts
  Reinhart et al. 2025, PNAS, instruction-tuned models vs six human registers
  Kobak et al. 2025, Science Advances, 15.1M PubMed abstracts
  Juzek 2026 (LexA), word ratios by model and register

Usage:
  aimeter.py FILE...               score files against the shipped bands
  aimeter.py --calibrate DIR [--ai AI_DIR] [--out FILE] [--lexicon NAME]
                               [--lang es] [--plain NAME]
                                   rebuild bands from a corpus of human texts; with
                                   AI texts of the same register, also learn which
                                   side of each band is the AI side
  aimeter.py --json FILE           machine-readable output
  aimeter.py --sample PATH FILE    PATH: the writer's own texts; a rate outside the band
                                   on the same side as theirs is their habit, not a tell
"""
import json, os, re, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "lexicons")
BANDS_FILE = os.environ.get("QUIRON_BANDS") or os.path.join(HERE, "bands.json")


def _load(name):
    """Word list, one or more per line; '#' starts a comment."""
    path = os.path.join(LEX, name)
    if not os.path.exists(path):
        return set()
    return {w for line in open(path) for w in line.split("#")[0].split()}


def _meta_early():
    try:
        return {k: v for k, v in json.load(open(BANDS_FILE)).items() if k.startswith("_")}
    except (OSError, ValueError):
        return {}


def lexicon_name():
    """The AI-lean list for this register: the band file may name its own."""
    try:
        return json.load(open(BANDS_FILE)).get("_lexicon", "ai-lean.txt")
    except (OSError, ValueError):
        return "ai-lean.txt"


KOBAK = _load("kobak-excess-style.txt")
AI_LEAN = _load(lexicon_name())
CLAUDE_LEAN = _load("claude-lean.txt")
HUMAN_LEAN = _load(_meta_early().get("_plain", "human-lean.txt"))

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
    r"(?:(?:\w+ly|not|now|also|often|still|already)\s+){0,2}"
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
# Lists of three: "X, Y and Z" with items of one to three words. The Economist
# (2026) found more of them per sentence in chatbot prose; measured on this skill's
# dev.to corpus against 2026 assistant posts, AUC 0.86 on held-out texts.
# The second item may not open with a subordinator or article, so a clause that
# happens to hold two commas ("explain, because the X and the Y") is not a list.
TRIAD3 = re.compile(
    r"\b[\w'-]+(?:\s+[\w'-]+){0,2},\s+(?!(?:because|which|who|that|when|while|if|so|but|"
    r"and|or|the|a|an|many|some|to|of|in|on|for|with)\b)[\w'-]+(?:\s+[\w'-]+){0,2},?\s+"
    r"(?:and|or)\s+[\w'-]+", re.I)
# Present participial clause after a comma, semicolon, colon or dash ("..., making it
# easy"). A gerund opening a sentence ("Checking the signature is ...") is a subject,
# not a participial clause, and is not counted. Reinhart et al. 2025 (PNAS): GPT-4o
# 5.3x the human rate, instruction-tuned models 2-5x.
PARTICIPLE = re.compile(
    r"[,;:\u2014\u2013]\s*([A-Za-z]+ing)\s+(?:the|a|an|his|her|their|its|my|our|your|this|that|"
    r"these|those|to|in|on|at|with|from|for|by|into|through|over|up|down|out|it|them|him|"
    r"me|us|each|every|all|both|some|more|less|new|what|how|who|which)\b")
ING_NOUNS = set("""thing things nothing something anything everything morning evening
during string strings king ring wing bring spring sing sting swing ceiling building
meaning feeling setting settings wedding pudding heading padding""".split())
# Spanish. Band files with "_lang": "es" use these in place of the English ones.
# Contractions do not exist in Spanish (al, del are obligatory), so that feature is 0.
ES_WORD = re.compile(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+")
ES_FIRST = re.compile(r"\b(?:yo|me|mi|mis|mío|mía|míos|mías|conmigo|nosotros|nosotras|"
                      r"nos|nuestro|nuestra|nuestros|nuestras)\b", re.I)
ES_NOMIN = re.compile(r"\b\w{3,}(?:ción|sión|miento|dad|eza|ncia)(?:es|s)?\b", re.I)
ES_LY = re.compile(r"\b\w{3,}mente\b", re.I)
ES_PASSIVE = re.compile(
    r"\b(?:es|son|fue|fueron|era|eran|será|serán|ser|sido|siendo|sea|sean)\s+"
    r"(?:(?:\w+mente|muy|ya|también|no)\s+){0,2}\w+(?:ado|ada|ados|adas|ido|ida|idos|idas|"
    r"cho|cha|chos|chas|to|ta|tos|tas)\b", re.I)
ES_CONN = re.compile(
    r"^[¿¡]?(?:Sin embargo|Además|Asimismo|Por lo tanto|Por ende|Así que|Entonces|Pero|Y|"
    r"También|Aun así|No obstante|En cambio|Luego|Finalmente|Primero|Segundo|Tercero|"
    r"Por otro lado|De hecho|Incluso|Por último|En resumen|En conclusión|O sea)\b", re.I)
ES_TRIAD = re.compile(
    r"\b[\wáéíóúñü'-]+(?:\s+[\wáéíóúñü'-]+){0,2},\s+(?!(?:porque|que|cuando|si|pero|y|o|"
    r"el|la|los|las|un|una|de|en|con|para|por|como)\b)[\wáéíóúñü'-]+(?:\s+[\wáéíóúñü'-]+){0,2},?"
    r"\s+(?:y|e|o|u)\s+[\wáéíóúñü'-]+", re.I)
# the gerund tacked on after a comma ("..., permitiendo que ..."), the Spanish form of
# the participial rider; style guides call the gerund of consequence an error
ES_PARTICIPLE = re.compile(r"[,;:\u2014\u2013]\s*(\w+(?:ando|iendo|yendo))\b", re.I)
ES_ING_NOUNS = set()

PROFILES = {
    "en": dict(word=re.compile(r"[A-Za-z']+"), first=FIRST, contr=CONTR, nomin=NOMIN,
               ly=LY, passive=PASSIVE, conn=CONN, triad=TRIAD3, part=PARTICIPLE,
               ing_nouns=ING_NOUNS),
    "es": dict(word=ES_WORD, first=ES_FIRST, contr=None, nomin=ES_NOMIN, ly=ES_LY,
               passive=ES_PASSIVE, conn=ES_CONN, triad=ES_TRIAD, part=ES_PARTICIPLE,
               ing_nouns=ES_ING_NOUNS),
}


def band_meta():
    try:
        return {k: v for k, v in json.load(open(BANDS_FILE)).items() if k.startswith("_")}
    except (OSError, ValueError):
        return {}


LANG = band_meta().get("_lang", "en")

# The most frequent function words of each language. A text whose words are mostly from
# another list is being measured against the wrong band file, or against a language no
# band file covers, and the word-based verdicts are off.
_FUNCTION = {"en": {"the", "and", "of", "to", "is", "in", "that", "it", "with", "for"},
             "es": {"el", "la", "de", "que", "y", "en", "los", "las", "por", "para", "una", "es"},
             "fr": {"le", "les", "des", "est", "et", "du", "une", "pour", "dans", "qui", "pas", "ce"},
             "pt": {"não", "uma", "os", "do", "da", "em", "com", "para", "é", "um", "dos", "mas"},
             "de": {"der", "die", "das", "und", "ist", "nicht", "ein", "eine", "zu", "mit", "den", "auf"},
             "it": {"il", "che", "di", "non", "per", "una", "sono", "gli", "della", "con", "è", "un"}}
_NAMES = {"en": "English", "es": "Spanish", "fr": "French", "pt": "Portuguese",
          "de": "German", "it": "Italian"}
BANDED = ("en", "es")  # languages with a measured band file
# features that do not depend on the words of a language, only on layout and punctuation
LAYOUT = ("cv_sentence_len", "para_words", "headings_1k", "em_dashes_1k", "parens_1k")


def lang_guess(text):
    """The text's language, when its function words clearly say so; else the band file's."""
    words = re.findall(r"[^\W\d_]+", text.lower())
    hits = {k: sum(w in v for w in words) for k, v in _FUNCTION.items()}
    guess = max(hits, key=hits.get)
    return guess if hits[guess] >= 2 * max(hits.get(LANG, 0), 1) else LANG


def lang_warning(text):
    """A line telling the user to switch band files or how far to trust the numbers."""
    guess = lang_guess(text)
    if guess == LANG:
        return ""
    if guess in BANDED:
        name = {"es": "bands-es.json", "en": "bands.json"}[guess]
        return (f"WARNING: this text looks {_NAMES[guess]} but {os.path.basename(BANDS_FILE)} "
                f"is for {_NAMES[LANG]}. Set QUIRON_BANDS={os.path.join(HERE, name)} and run again.")
    return (f"NOTE: this text looks {_NAMES.get(guess, guess)}, and no band file is measured for it. "
            f"Only the layout features are shown, compared with {_NAMES[LANG]} writing as a rough "
            f"guide. Rate and lexicon FAILs are reported as READ.")


HEDGE = re.compile(
    r"\b(?:it is important to note|it is worth noting|in conclusion|in summary|"
    r"that said|at its core|the real question is|what really matters|let's dive|"
    r"let us delve|here's the thing|make no mistake)\b", re.I)

# Every feature: (direction assistant text sits relative to humans, AI reference).
# "hi" means assistant text runs higher than human text, "lo" lower, None means the
# direction depends on register or model and only the band is scored. Directions
# come from the published studies (TextPulse 2026; Reinhart et al. 2025, PNAS; the
# Economist 2026) and were each checked on this skill's own run: held-out pre-2022
# dev.to posts against 42 posts written in 2026 by Claude Opus, Claude Sonnet and
# GPT on the same titles. The AI reference is the median of those 42 posts.
AI_REF = {
    "cv_sentence_len":   ("lo", 0.513),
    "mean_sentence_len": (None, 15.6),
    "long_words_1k":     ("hi", 252.8),
    "mean_word_len":     ("hi", 4.92),
    "nominalizations_1k":("hi", 26.7),
    "ly_adverbs_1k":     ("hi", 16.0),
    "passive_1k":        ("lo", 3.74),
    "mattr50":           ("hi", 0.851),
    "first_person_1k":   ("lo", 4.36),
    "contractions_1k":   ("lo", 19.2),
    "questions_1k":      ("lo", 0.0),
    "repeated_openers":  ("lo", 3.55),
    "connective_openers":("lo", 3.3),
    "commas_1k":         ("hi", 56.2),
    "semicolons_1k":     (None, 0.0),
    "em_dashes_1k":      ("hi", 1.09),
    "ai_lexicon_1k":     ("hi", 1.80),
    "triads_1k":         ("hi", 7.2),
    "participles_1k":    ("hi", 2.25),
    "plain_words_1k":    ("lo", 55.0),
    "parens_1k":         ("lo", 0.0),
    "para_words":        (None, None),
    "headings_1k":       ("hi", 12.2),
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
    "ai_lexicon_1k": "AI-lexicon words /1k", "triads_1k": "lists of three /1k",
    "participles_1k": "participial clauses /1k", "plain_words_1k": "plain words /1k",
    "parens_1k": "parentheses /1k", "para_words": "words per paragraph",
    "headings_1k": "headings /1k",
}


def prose(md):
    """Strip everything that is not the author's sentences."""
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = re.sub(r"~~~.*?~~~", "", md, flags=re.S)
    md = "\n".join(l for l in md.split("\n") if not l.lstrip().startswith("|"))
    md = re.sub(r"^\s{4,}\S.*$", "", md, flags=re.M)
    md = re.sub(r"^#{1,6} .*$", "", md, flags=re.M)
    # a list item is its own sentence even without a full stop, or the whole list
    # would be measured as one long sentence
    md = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+(.*?)[:;,]?\s*$",
                lambda m: m.group(1) + ("" if m.group(1)[-1:] in ".!?" else "."),
                md, flags=re.M)
    md = re.sub(r"^>.*$", "", md, flags=re.M)  # a quotation is not the author's prose
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"`[^`]+`", "CODE", md)
    md = re.sub(r"<[^>]+>", "", md)
    md = re.sub(r"https?://\S+", "URL", md)
    return md


def measure(text):
    t = prose(text)
    P = PROFILES[LANG]
    words = P["word"].findall(t)
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
        "nominalizations_1k": per1k(len(P["nomin"].findall(t))),
        "ly_adverbs_1k": per1k(len(P["ly"].findall(t))),
        "passive_1k": per1k(len(P["passive"].findall(t))),
        "mattr50": round(mattr, 3),
        "first_person_1k": per1k(len(P["first"].findall(t))),
        "contractions_1k": per1k(len(P["contr"].findall(t))) if P["contr"] else 0.0,
        "questions_1k": per1k(t.count("?")),
        "repeated_openers": round(rep / max(len(sents) - 1, 1) * 100, 1),
        "connective_openers": round(
            sum(1 for s in sents if P["conn"].match(s)) / len(sents) * 100, 1),
        "commas_1k": per1k(t.count(",")),
        "semicolons_1k": per1k(t.count(";")),
        "em_dashes_1k": per1k(len(re.findall(r"[—–]", t))),
        "ai_lexicon_1k": per1k(sum(1 for w in low if w in AI_LEAN)),
        "triads_1k": per1k(len(P["triad"].findall(re.sub(r"\s+", " ", t)))),
        "participles_1k": per1k(sum(1 for m in P["part"].finditer(t)
                                    if m.group(1).lower() not in P["ing_nouns"])),
        "plain_words_1k": per1k(sum(1 for w in low if w in HUMAN_LEAN)),
        "parens_1k": per1k(t.count("(")),
        "para_words": round(n / max(len(paras), 1), 1),
        # assistant posts carry about twice the headings of human ones (AUC 0.75 held out)
        "headings_1k": per1k(len(re.findall(r"^#{1,6} ", re.sub(r"```.*?```", "", text,
                                                                 flags=re.S), re.M))),
        "_flags": {
            "AI-lexicon words": sorted({w for w in low if w in AI_LEAN}),
            "Claude-family words": sorted({w for w in low if w in CLAUDE_LEAN}),
            "Kobak excess style words": sorted(
                {w for w in low if w in KOBAK and w not in KOBAK_NOISE}),
            "not-X-but-Y": NOTBUT.findall(t),
            "triads": TRIAD.findall(t),
            "hedge templates": HEDGE.findall(t),
            "short closers": f"{len(closers)}/{len(paras)} paragraphs"
                             if paras else "n/a",
        },
    }


def bands_from(rows, ai_rows=None):
    """p10/p50/p90 of each feature over measured human texts.

    With ai_rows (assistant texts in the same register), each feature also gets the
    AI median and the direction AI text sits for this register, which then overrides
    the default in AI_REF. Directions differ by register: assistant fiction has
    shorter, more uneven sentences than human fiction, the opposite of blog posts.
    A feature whose AUC is between 0.4 and 0.6 gets no direction (two-sided).
    """
    bands = {"_texts": len(rows)}
    if ai_rows:
        bands["_ai_texts"] = len(ai_rows)
    for key in AI_REF:
        vals = sorted(r[key] for r in rows)
        q = lambda p: vals[min(int(p * len(vals)), len(vals) - 1)]
        bands[key] = {"p10": q(0.10), "p50": q(0.50), "p90": q(0.90),
                      "min": vals[0], "max": vals[-1]}
        if ai_rows:
            av = [r[key] for r in ai_rows]
            auc = sum((a > h) + 0.5 * (a == h) for a in av for h in vals) / (len(av) * len(vals))
            bands[key]["ai"] = round(st.median(av), 3)
            bands[key]["auc"] = round(auc, 3)
            bands[key]["push"] = "hi" if auc >= 0.6 else "lo" if auc <= 0.4 else None
    return bands


def measure_dir(directory):
    rows = []
    for name in sorted(os.listdir(directory)):
        if name.endswith((".md", ".txt")):
            m = measure(open(os.path.join(directory, name), encoding="utf-8").read())
            if m:
                rows.append(m)
    return rows


def calibrate(directory, ai_dir=None, out=None, lexicon=None, lang=None, plain=None):
    rows = measure_dir(directory)
    if len(rows) < 8:
        sys.exit(f"need at least 8 usable texts, got {len(rows)}")
    ai_rows = measure_dir(ai_dir) if ai_dir else None
    bands = {"_corpus": os.path.basename(os.path.abspath(directory)),
             **bands_from(rows, ai_rows)}
    out = out or BANDS_FILE
    try:  # keep the register's own lexicon and thresholds across a recalibration
        old = json.load(open(out))
        bands.update({k: old[k] for k in ("_lexicon", "_thresholds", "_lang", "_plain")
                      if k in old})
    except (OSError, ValueError):
        pass
    for key, val in (("_lexicon", lexicon), ("_lang", lang), ("_plain", plain)):
        if val:
            bands[key] = val
    json.dump(bands, open(out, "w"), indent=1)
    print(f"calibrated on {len(rows)} texts" +
          (f" and {len(ai_rows)} AI texts" if ai_rows else "") + f" -> {out}")
    for key in AI_REF:
        b = bands[key]
        extra = f"  AI {b['ai']:>8}  AUC {b['auc']:.2f} {b['push'] or '-'}" if ai_rows else ""
        print(f"  {LABELS[key]:28} p10 {b['p10']:>8}  median {b['p50']:>8}  p90 {b['p90']:>8}{extra}")


# A value within 5% of the band's width past an edge still counts as inside: one comma
# more should not flip a verdict. Measured on held-out texts, this cut human texts
# failing C1 from 7-11% to 5-6% and assistant posts caught by C1 from 88% to 83%.
MARGIN = 0.05


def verdict(key, got, band):
    """inside / below / above the human band, and whether that is the AI side."""
    lo, hi = band["p10"], band["p90"]
    slack = (hi - lo) * MARGIN
    if lo - slack <= got <= hi + slack:
        return "ok"
    side = "above" if got > hi else "below"
    push = band["push"] if "push" in band else AI_REF[key][0]
    if not push:
        return f"{side} band"
    if push and ((push == "hi" and side == "above") or (push == "lo" and side == "below")):
        return f"{side} band, AI side"
    return f"{side} band, overshot"


# Verdicts that tempt a rewriter into the wrong fix.
HINTS = {
    "first_person_1k": " (normal in tutorials and reference text; never invent a narrator)",
    "plain_words_1k": " (use them where they are the natural word; do not sprinkle)",
}


OVER_HINTS = {
    "plain_words_1k": " (second-person posts run high on 'you'; if the source did too, leave it)",
}


def sample_medians(paths):
    rows = [m for m in (measure(open(p, encoding="utf-8").read()) for p in paths) if m]
    return {k: st.median(r[k] for r in rows) for k in AI_REF} if rows else {}


def habit(key, got, band, sample):
    """The writer's own texts sit outside the band on the same side: their habit."""
    if key not in sample:
        return False
    lo, hi = band["p10"], band["p90"]
    return (got > hi and sample[key] > hi) or (got < lo and sample[key] < lo)


def report(path, as_json=False, sample=None):
    sample = sample or {}
    m = measure(open(path, encoding="utf-8").read())
    if not m:
        print(f"{os.path.basename(path)}: too short to measure (need ~120 words, 8 sentences)")
        return
    bands = json.load(open(BANDS_FILE)) if os.path.exists(BANDS_FILE) else None
    if as_json:
        print(json.dumps({"file": path, "metrics": m,
                          "verdicts": {k: "ok" if habit(k, m[k], bands[k], sample)
                                       else verdict(k, m[k], bands[k])
                                       for k in AI_REF if bands and k in bands}}, indent=1))
        return
    print(f"\n{os.path.basename(path)}  {m['_words']} words, "
          f"{m['_sentences']} sentences, {m['_paragraphs']} paragraphs\n")
    raw = open(path, encoding="utf-8").read()
    warn = lang_warning(raw)
    if warn:
        print(warn + "\n")
    if not bands:
        sys.exit("no bands.json; run --calibrate DIR first")
    # Without a band file for the language only the layout features mean anything, so the
    # word-based ones are not shown at all: a number on screen is a number someone chases.
    keys = list(AI_REF) if lang_guess(raw) in BANDED else [k for k in AI_REF if k in LAYOUT]
    print(f"{'feature':30}{'this':>9}{'human band':>18}{'AI':>8}   verdict")
    bad = 0
    for key in keys:
        b, got = bands[key], m[key]
        ai = b.get("ai", AI_REF[key][1])
        v = verdict(key, got, b)
        hint = (HINTS.get(key, "") if v.endswith("AI side")
                else OVER_HINTS.get(key, "") if v.endswith("overshot") else "")
        if v != "ok" and habit(key, got, b, sample):
            v, hint = "ok", f"writer's habit: their own texts sit at {sample[key]:.3g}"
        if v != "ok":
            bad += 1
        band = f"{b['p10']} - {b['p90']}"
        print(f"{LABELS[key]:30}{got:>9}{band:>18}{(ai if ai is not None else '-'):>8}   "
              f"{'' if v == 'ok' else v}{hint}")
    print(f"\n{len(keys) - bad}/{len(keys)} {'features' if len(keys) == len(AI_REF) else 'layout features'}"
          f" inside the human band (p10-p90 of {bands['_texts']} human texts)\n")
    if len(keys) < len(AI_REF):
        return  # the word flags below are English or Spanish patterns
    for label, v in m["_flags"].items():
        if LANG != "en" and label not in ("AI-lexicon words", "short closers"):
            continue  # the other flags are English patterns
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
        opt = lambda f: args[args.index(f) + 1] if f in args else None
        if opt("--lang"):  # measure the corpus with that language's patterns
            LANG = opt("--lang")
        if opt("--lexicon"):
            AI_LEAN = _load(opt("--lexicon"))
        if opt("--plain"):
            HUMAN_LEAN = _load(opt("--plain"))
        calibrate(args[1], ai_dir=opt("--ai"), out=opt("--out"), lexicon=opt("--lexicon"),
                  lang=opt("--lang"), plain=opt("--plain"))
    else:
        sample_paths = []
        while "--sample" in args:
            i = args.index("--sample")
            target = args[i + 1] if i + 1 < len(args) else ""
            if not os.path.exists(target):
                sys.exit(f"--sample needs an existing file or directory, got: {target or 'nothing'}")
            sample_paths += ([os.path.join(target, n) for n in sorted(os.listdir(target))
                              if n.endswith((".md", ".txt"))]
                             if os.path.isdir(target) else [target])
            del args[i:i + 2]
        missing = [a for a in args if a != "--json" and not os.path.isfile(a)]
        if missing:
            sys.exit(f"no such file: {', '.join(missing)}")
        if not os.path.exists(BANDS_FILE):
            sys.exit(f"band file not found: {BANDS_FILE}\nSet QUIRON_BANDS to bands.json, "
                     f"bands-fiction.json or bands-es.json in {HERE}, or build one with --calibrate DIR.")
        sample = sample_medians(sample_paths) if sample_paths else None
        as_json = "--json" in args
        for p in [a for a in args if a != "--json"]:
            report(p, as_json=as_json, sample=sample)

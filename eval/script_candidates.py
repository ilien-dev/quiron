#!/usr/bin/env python3
"""Count each candidate shape pattern of a video script on both sides, and say what it can be.

Every candidate is a regex or a rule over the spoken words, read the way audit.py reads a
text (spoken(), curly apostrophes made straight, prose(), case-insensitive, ^ at each line).
It reports the share of texts it fires on in: the human train three quarters, the held-out
quarter (every 4th file by sorted name), and every AI train and test folder. Only texts that
measure (120 words and 8 sentences) are counted, as in evaluate.py.

The verdict uses held-out humans and the pooled AI test folders only:
  FAIL  at most 5% of held-out humans and at least 30% of some test model; for Spanish the
        train humans must be at most 5% too, since 5% of 27 held-out texts is one text
  TELL  humans use it (train or held out) and the pooled AI test rate is at least twice the
        held-out human rate and twice the train human rate
  out   otherwise
Rows marked "count only" (subscribe, sponsor reads, sign-offs) are counted and never proposed.

Usage:
  python3 eval/script_candidates.py en|es [--show NAME]
"""
import os, re, sys

LANG = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
os.environ["QUIRON_BANDS"] = os.path.join(REPO, "scripts", f"bands-script{'-es' if LANG == 'es' else ''}.json")
sys.path.insert(0, os.path.join(REPO, "scripts"))
import aimeter  # noqa: E402

SUB = "script" if LANG == "en" else "script-es"
HUM = os.path.expanduser(f"~/corpus/{SUB}")
AI = os.path.join(REPO, "eval", "ai", SUB)
SENT = re.compile(r"(?<=[.!?])\s+")
F = re.I | re.M


class Text:
    def __init__(self, path, title):
        raw = open(path, encoding="utf-8").read()
        self.measures = aimeter.measure(raw) is not None
        raw = aimeter.spoken(raw).replace("’", "'").replace("‘", "'")
        self.text = aimeter.prose(raw)
        self.sents = [s.strip() for s in SENT.split(re.sub(r"\s+", " ", self.text)) if s.strip()]
        self.words = len(re.findall(r"[^\W\d_]+", self.text))
        self.title, self.path = title, path


# --- rule builders -----------------------------------------------------------------------
def rx(p):
    c = re.compile(p, F)

    def f(t):
        m = c.search(t.text)
        return m.group(0).strip() if m else ""
    return f


def count_rx(p, k):
    c = re.compile(p, F)
    return lambda t: str(len(c.findall(t.text))) if len(c.findall(t.text)) >= k else ""


def first(n, p):
    c = re.compile(p, re.I)
    return lambda t: next((s[:80] for s in t.sents[:n] if c.search(s)), "")


def last_frac(fr, p):
    c = re.compile(p, re.I)
    return lambda t: next((s[:80] for s in t.sents[-max(3, int(len(t.sents) * fr)):] if c.search(s)), "")


def qshare(th):
    def f(t):
        q = sum(s.endswith("?") for s in t.sents) / max(len(t.sents), 1)
        return f"{q:.2f}" if q >= th else ""
    return f


def short_q_answered(maxw):
    return lambda t: next((a + " " + b[:40] for a, b in zip(t.sents, t.sents[1:])
                           if a.endswith("?") and len(a.split()) <= maxw and not b.endswith("?")), "")


def short_run(k, maxw):
    def f(t):
        run = 0
        for s in t.sents:
            run = run + 1 if len(s.split()) <= maxw else 0
            if run >= k:
                return "run"
        return ""
    return f


def opener_share_below(p, lo):
    c = re.compile(p, re.I)

    def f(t):
        r = sum(bool(c.match(s)) for s in t.sents) / max(len(t.sents), 1)
        return f"{r:.3f}" if r < lo else ""
    return f


def rate_above(p, per_word):
    c = re.compile(p, F)
    return lambda t: "y" if len(c.findall(t.text)) / max(t.words, 1) > per_word else ""


def content_words(s, stop):
    return {w for w in re.findall(r"[^\W\d_']+", s.lower()) if w not in stop and len(w) > 2}


def title_question_at_end(stop):
    """a question in the last 10% that shares two content words with the title (needs the title)"""
    def f(t):
        tw = content_words(re.sub(r"\(.*?\)|\|.*$", "", t.title), stop)
        return next((s[:80] for s in t.sents[-max(3, len(t.sents) // 10):]
                     if s.endswith("?") and len(content_words(s, stop) & tw) >= 2), "")
    return f


def bookend(stop):
    """one of the last three sentences shares three content words with the first three"""
    def f(t):
        if len(t.sents) < 20:
            return ""
        a = set().union(*[content_words(s, stop) for s in t.sents[:3]])
        return next((s[:60] for s in t.sents[-3:] if len(content_words(s, stop) & a) >= 3), "")
    return f


def same_opener_pair(words):
    def f(t):
        for a, b in zip(t.sents, t.sents[1:]):
            wa, wb = (x.split()[0].lower().strip(",¿¡") if x.split() else "" for x in (a, b))
            if wa == wb and wa in words:
                return a[:40] + " | " + b[:40]
        return ""
    return f


def triple_opener(skip):
    def f(t):
        for a, b, c in zip(t.sents, t.sents[1:], t.sents[2:]):
            w = [x.split()[0].lower().strip("¿¡,") if x.split() else "" for x in (a, b, c)]
            if w[0] == w[1] == w[2] and w[0] not in skip:
                return a[:30] + " | " + b[:30]
        return ""
    return f


def neg_pair(p):
    c = re.compile(p, re.I)
    return lambda t: next((a + " " + b for a, b in zip(t.sents, t.sents[1:]) if c.match(a) and c.match(b)), "")


def moves(table, k, skip=()):
    def f(t):
        hit = [n for n, p in table.items() if n not in skip and re.search(p, t.text, F)]
        return ",".join(hit) if len(hit) >= k else ""
    return f


def either(*fs):
    return lambda t: next((r for r in (f(t) for f in fs) if r), "")


# --- English -----------------------------------------------------------------------------
S = r"(?:^|(?<=[.!?]\s))"
STOP_EN = set("the a an of to in and or is are was were how why what who when where does do did can could would "
              "will you your we our it its this that for on with from by be not".split())
EN = {
    "imagine": S + r"(?:now,? |so,? )?(?:imagine|picture this)\b",
    "heres": r"\bhere's (?:the (?:thing|twist|catch|kicker|problem|best part|honest part|strange part|weird part|"
             r"surprising part|part|real|key|deal|interesting)|where (?:it|things) gets?|why|how|what)\b",
    "thenthere": S + r"(?:and )?then (?:there's|comes)\b",
    "answer": r"\bthe (?:honest|short|real|simple) answer\b",
    "sounds": r"\bsounds (?:simple|easy|logical|straightforward|reasonable|obvious|crazy|impossible|absurd|ridiculous)\b",
    "npq": S + r"(?:the|its|their|his|her|our|your|my|that|this) \w+(?: \w+)?\?",
    "nexttime": r"\bnext time you\b",
    "comments": r"\b(?:tell|let) (?:me|us) (?:know )?(?:in the comments|below)\b|\bleave a comment\b|\bcomment below\b"
                r"|\bin the comments\b",
    "anaphora": S + r"no \w+(?: \w+){0,2}[.!]\s+no \w+(?: \w+){0,2}[.!]|" + S + r"maybe\b[^.!?]*[.!?]\s+maybe\b|"
                + S + r"which\b[^.!?]*[.!?]\s+which\b",
}
# the six checks shipped as S1-S6, as audit.py has them
EN_CHECKS = {"S1": EN["imagine"], "S2": EN["heres"] + "|" + EN["thenthere"] + "|" + EN["answer"] + "|" + EN["sounds"],
             "S3": EN["comments"], "S4": EN["nexttime"], "S5": EN["npq"], "S6": EN["anaphora"]}
CANDS_EN = [
    # the brief's starting list
    ("hook: Imagine/Picture this opens a sentence", rx(EN["imagine"])),
    ("hook: Imagine in the first 3 sentences", first(3, r"^(?:so,? |now,? )?(?:imagine|picture (?:this|yourself|a|an|the))\b")),
    ("hook: Imagine opens 2+ sentences", count_rx(r"(?:^|(?<=[.!?]\s))(?:now,? |so,? |and )?(?:imagine|picture this)\b", 2)),
    ("hook: Imagine you/a world/being...", rx(S + r"(?:now,? |so,? )?imagine (?:you|your|a world|if you|being|waking|living|stepping|standing|walking)\b")),
    ("hook: first sentence is a question", first(1, r"\?$")),
    ("hook: a question in the first 3", first(3, r"\?$")),
    ("promise: in this video / today we", rx(r"\bin this (?:video|episode)\b|\bby the end of (?:this|the) (?:video|episode)\b"
                                           r"|\btoday,? (?:we(?:'re| are| will|'ll)|i(?:'m| am| will|'ll))\b|\bin today's (?:video|episode)\b")),
    ("promise: we'll explore / look at", rx(r"\bwe(?:'ll| will| are going to|'re going to) (?:explore|look at|find out|break (?:it|this) down"
                                           r"|uncover|dig into|take a look|unpack|answer)\b")),
    ("promise: stay / stick with me", rx(r"\b(?:stay|stick) (?:with me|with us|around|until the end)\b|\bkeep watching\b")),
    ("Q answered: question <=6 words, then a statement", short_q_answered(6)),
    ("Q answered: question <=3 words, then a statement", short_q_answered(3)),
    ("Q answered: bare noun phrase (The catch?)", rx(EN["npq"])),
    ("Q answered: The answer? / The catch:", rx(S + r"the (?:answer|result|reason|problem|catch|twist|kicker|secret|truth|irony)(?: is)?[?:]")),
    ("Q answered: one-word question (Why?)", rx(S + r"(?:why|how|what|really|the result|so)\?")),
    ("recap: to recap / what does this mean", rx(r"\b(?:so,? )?to recap\b|\bwhat does (?:this|that|all (?:of )?this) (?:mean|tell us)\b"
                                                 r"|\bso,? to sum up\b|\bin short,|\blet's recap\b")),
    ("recap: so that's how / why / what / it", rx(r"\bso,? that's (?:how|why|what|it|the)\b")),
    ("transition: here's the X / here's why", rx(EN["heres"])),
    ("transition: here's the X (noun only)", rx(r"\bhere's the (?:thing|twist|catch|kicker|problem|best part|honest part|strange part"
                                                r"|weird part|surprising part|part|real|key|deal|interesting)\b")),
    ("transition: here's why / how / what", rx(r"\bhere's (?:why|how|what)\b")),
    ("transition: but here's", rx(r"\bbut here's\b")),
    ("transition: here's the twist / catch / kicker", rx(r"\bhere's the (?:twist|catch|kicker)\b|\bbut there's a catch\b|\bthe catch\?")),
    ("transition: that's where X comes in", rx(r"\bthat's where \w+(?: \w+)? comes? in\b|\bthis is where\b|\bthat's where things\b")),
    ("transition: (and) then there's / comes", rx(EN["thenthere"])),
    ("transition: the honest / short answer", rx(EN["answer"])),
    ("transition: sounds simple / logical", rx(EN["sounds"])),
    ("family: staged reveals (here's, then there's, the honest answer, sounds simple)",
     rx(EN["heres"] + "|" + EN["thenthere"] + "|" + EN["answer"] + "|" + EN["sounds"])),
    ("close: question with the title's words in the last 10%", title_question_at_end(STOP_EN)),
    ("close: So, <question>? in the last 10%", last_frac(0.1, r"^so,? (?:is|are|can|could|will|would|should|do|does|did|what|why|how|who|was|were)\b.*\?$")),
    ("close: bookend (end echoes the first 3 sentences)", bookend(STOP_EN)),
    ("close: next time you", rx(EN["nexttime"])),
    ("close: asking for comments", rx(EN["comments"])),
    ("count only: subscribe", rx(r"\bsubscrib")),
    ("count only: sponsor read", rx(r"\bsponsor|\bskillshare\b|\bbrilliant\.org|\bnordvpn\b|\bsquarespace\b|\bpatreon\b"
                                    r"|\bcuriositystream\b|\bnebula\b|\baudible\b")),
    ("count only: thanks for watching / see you next", rx(r"\bthanks? (?:you )?for watching\b|\bsee you (?:next time|in the next)\b")),
    # structure
    ("struct: questions are 10%+ of sentences", qshare(0.10)),
    ("struct: questions are 15%+ of sentences", qshare(0.15)),
    ("struct: 4 sentences of <=4 words in a row", short_run(4, 4)),
    ("struct: 3 sentences of <=3 words in a row", short_run(3, 3)),
    ("struct: under 8% of sentences open with And/But/So", opener_share_below(r"(?:and|but|so)\b", 0.08)),
    ("struct: under 1% of sentences open with Now/Well", opener_share_below(r"(?:now|well)\b", 0.01)),
    # from reading the texts and the judges' reasons
    ("read: Really X. fragment", rx(r"(?:^|(?<=[.!?]\s))Really[^.!?]{0,30}[.!]")),
    ("read: No X. No Y. / Maybe... Maybe... / Which... Which...", rx(EN["anaphora"])),
    ("read: think of it like / as", rx(r"\bthink of (?:it|this|them) (?:like|as)\b")),
    ("read: welcome to / welcome back", rx(r"\bwelcome (?:back|to)\b")),
    ("read: let's start / let's look at", rx(r"\blet's (?:start|begin|go back|rewind|take a (?:closer )?look|look at|break)\b")),
    ("read: Which means / That means opens a sentence", rx(S + r"(?:which|that|this) means\b")),
    ("read: ..., right? tag", rx(r", right\?")),
    ("read: em or en dash", rx(r"[—–]")),
    ("read: ellipsis", rx(r"…|\.\.\.")),
    ("read: you / your above 30 per 1,000 words", rate_above(r"\byou(?:r|'re|'ve|'ll|'d)?\b", 0.03)),
    ("read: you know / kind of / basically / I mean", rx(r"\byou know\b|\bkind of\b|\bsort of\b|\bbasically\b|\bi mean\b")),
    ("union: 2+ of the stock moves", moves({k: EN[k] for k in ("imagine", "heres", "thenthere", "sounds", "npq", "answer",
                                                                "nexttime", "comments")}, 2)),
    ("union: 3+ of the stock moves", moves({k: EN[k] for k in ("imagine", "heres", "thenthere", "sounds", "npq", "answer",
                                                                "nexttime", "comments")}, 3)),
    ("union: 2+ of the checks S1-S6", moves(EN_CHECKS, 2)),
    ("union: 3+ of the checks S1-S6", moves(EN_CHECKS, 3)),
    ("union: 3+ of S1-S6 without S3 (comments)", moves(EN_CHECKS, 3, ("S3",))),
]

# --- Spanish -----------------------------------------------------------------------------
SE = r"(?:^|(?<=[.!?…]\s)|(?<=[¿¡]))"
STOP_ES = set("el la los las un una unos unas de del al a en y o que es son fue por para con sin se su sus lo le les "
              "como qué cómo por qué quién cuál cuándo dónde no sí más muy este esta esto ese esa eso hay".split())
ES = {
    "imagina": SE + r"(?:ahora )?imagin(?:a|e|emos|aos|en)\b",
    "hoy": r"\bhoy (?:te (?:cuento|explico|voy a)|vamos a|veremos|descubriremos|os (?:cuento|explico|voy a)|repasamos"
           r"|conoceremos|hablamos)\b",
    "quedate": r"\bqu[eé]da(?:te|os) (?:hasta el final|conmigo)\b",
    "empecemos": r"\bempecemos\b|\bcomencemos\b|\bvamos all[aá]\b",
    "clave": r"\by aqu[ií] (?:est[aá]|viene|aparece|entra)\b|\baqu[ií] (?:est[aá] la clave|viene lo (?:bueno|interesante|curioso)"
             r"|est[aá] el truco)|\bahora viene\b|\blo (?:fascinante|curioso|interesante|sorprendente|incre[ií]ble) es que\b"
             r"|\bdato curioso\b|\bun detalle (?:fascinante|curioso)\b",
    "ojo": SE + r"pero (?:ojo|atenci[oó]n|cuidado|espera)\b",
    "proxima": r"\bla pr[oó]xima vez que\b",
    "entonces": SE + r"entonces, ¿",
    "comentarios": r"\b(?:cu[eé]nta(?:me|nos)|d[eé]ja(?:me|nos|lo)|d[ée]jamelo|escr[ií]be(?:me|nos)|dinos|d[ií]me)\b[^.!?]{0,30}"
                   r"\bcomentarios\b|\ben los comentarios\b",
}
CANDS_ES = [
    ("gancho: imagina abre una frase", rx(ES["imagina"])),
    ("gancho: imagina en las 3 primeras frases", first(3, r"^(?:ahora )?¿?imagin(?:a|e|emos|aos|en)\b")),
    ("gancho: la primera frase es pregunta", first(1, r"\?$")),
    ("gancho: una pregunta en las 3 primeras", first(3, r"\?$")),
    ("promesa: hoy te cuento / hoy vamos a / en este video", rx(ES["hoy"] + r"|\ben este (?:v[ií]deo|episodio)\b")),
    ("promesa: hoy te cuento / hoy vamos a", rx(ES["hoy"])),
    ("promesa: quédate hasta el final / no te pierdas", rx(ES["quedate"] + r"|\bno te (?:lo )?pierdas\b")),
    ("promesa: quédate hasta el final / conmigo", rx(ES["quedate"])),
    ("pregunta respondida: <=6 palabras y una afirmación", short_q_answered(6)),
    ("pregunta respondida: <=3 palabras y una afirmación", short_q_answered(3)),
    ("pregunta respondida: ¿El resultado?", rx(r"(?:^|(?<=[.!?]\s))¿(?:el|la|los|las|su|sus|lo|y el|y la|y los|y las) \w+(?: \w+)?\?")),
    ("pregunta respondida: buena pregunta", rx(r"\bbuena pregunta\b")),
    ("recapitulación: en resumen / resumiendo", rx(r"\ben resumen\b|\bresumiendo\b|\brecapitulando\b|\bpara resumir\b")),
    ("recapitulación: es decir,", rx(r"\bes decir,")),
    ("transición: y aquí viene / lo curioso es que", rx(ES["clave"])),
    ("transición: pero ojo / atención / espera", rx(ES["ojo"])),
    ("transición: empecemos / vamos allá", rx(ES["empecemos"])),
    ("cierre: entonces, ¿...?", rx(ES["entonces"])),
    ("cierre: pregunta con palabras del título en el último 10%", title_question_at_end(STOP_ES)),
    ("cierre: eco del comienzo en las 3 últimas frases", bookend(STOP_ES)),
    ("cierre: la próxima vez que", rx(ES["proxima"])),
    ("cierre: pedir comentarios", rx(ES["comentarios"])),
    ("count only: suscríbete", rx(r"\bsuscr[ií]b")),
    ("count only: patrocinio", rx(r"\bpatrocin|\bpatreon\b|\bpresentado por\b")),
    ("count only: nos vemos / gracias por ver", rx(r"\bnos vemos\b|\bgracias por (?:ver|vernos)\b")),
    ("struct: preguntas, 10%+ de las frases", qshare(0.10)),
    ("struct: preguntas, 15%+ de las frases", qshare(0.15)),
    ("struct: 4 frases de <=4 palabras seguidas", short_run(4, 4)),
    ("struct: 3 frases de <=3 palabras seguidas", short_run(3, 3)),
    ("struct: menos del 8% de frases abren con Y/Pero/Así que/Entonces", opener_share_below(r"¿?(?:y|pero|as[ií] que|entonces)\b", 0.08)),
    ("struct: menos del 1% abren con Bueno/Pues/Vale/Bien/Mira/Oye", opener_share_below(r"¿?(?:bueno|pues|vale|bien|mira|oye)\b", 0.01)),
    ("leído: No X. Ni Y.", neg_pair(r"(?:no|ni|sin) \w+(?: \w+){0,2}[.!]$")),
    ("leído: tres frases seguidas con la misma apertura", triple_opener({"el", "la", "y", "pero", "en", "los", "las"})),
    ("leído: así de simple / sencillo", rx(r"\bas[ií] de (?:simple|sencillo|f[aá]cil)\b")),
    ("leído: No es X. Es Y. en frases cortas", rx(SE + r"no es (?:un[ao]? |el |la )?\w+(?: \w+)?\. es\b")),
    ("leído: piénsalo como / así", rx(r"\bpiensa en (?:ello|esto|eso) como\b|\bpi[eé]nsalo (?:as[ií]|como)\b")),
    ("leído: fascinante", rx(r"\bfascinante")),
    ("leído: raya", rx(r"[—–]")),
    ("leído: puntos suspensivos", rx(r"…|\.\.\.")),
    ("leído: o sea / bueno, / pues / vale, / tipo", rx(r"\bo ?sea\b|\bbueno,|\bpues\b|\bvale,|\btipo\b")),
    ("union: 2+ de todas las movidas de arriba", moves(ES, 2)),
    ("union: 3+ de todas las movidas de arriba", moves(ES, 3)),
    ("union: 2+ de los checks SE1-SE7", moves(ES, 2, ("empecemos", "ojo"))),
    ("union: 3+ de los checks SE1-SE7", moves(ES, 3, ("empecemos", "ojo"))),
    ("union: 3+ de SE1-SE7 sin SE6 (comentarios)", moves(ES, 3, ("empecemos", "ojo", "comentarios"))),
]


def titles():
    out = {}
    for line in open(os.path.join(HUM, "titles.tsv"), encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3:
            out[p[0]] = p[2]
    for line in open(os.path.join(AI, "MANIFEST.tsv"), encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        m = re.search(r'"(.*)"', p[-1])
        if m:
            out[p[0] + "/" + p[1]] = m.group(1)
    return out


def main():
    show = sys.argv[sys.argv.index("--show") + 1] if "--show" in sys.argv else None
    tt = titles()
    names = sorted(n for n in os.listdir(HUM) if n.endswith(".md"))
    groups = {"h-train": [os.path.join(HUM, n) for i, n in enumerate(names) if i % 4 != 0],
              "h-held": [os.path.join(HUM, n) for i, n in enumerate(names) if i % 4 == 0]}
    for d in sorted(os.listdir(AI), key=lambda d: (not d.startswith("train"), d)):
        if os.path.isdir(os.path.join(AI, d)):
            groups[d] = [os.path.join(AI, d, n) for n in sorted(os.listdir(os.path.join(AI, d))) if n.endswith(".md")]
    texts = {}
    for g, ps in groups.items():
        rows = []
        for p in ps:
            stem = os.path.basename(p)[:-3]
            t = Text(p, tt.get(f"{g}/{stem}") or tt.get(stem, ""))
            if t.measures:
                rows.append(t)
        texts[g] = rows
    test = [g for g in texts if g.startswith("test-")]
    cols = list(texts)
    short = {g: g.replace("train-", "tr-").replace("test-", "te-") for g in cols}
    print(f"{'candidate':66}" + "".join(f"{short[g]:>11}" for g in cols) + f"{'AI test':>9}  verdict")
    print(f"{'texts':66}" + "".join(f"{len(texts[g]):>11}" for g in cols) + f"{sum(len(texts[g]) for g in test):>9}")
    for name, fn in (CANDS_ES if LANG == "es" else CANDS_EN):
        hits = {g: [t for t in texts[g] if fn(t)] for g in cols}
        rate = {g: len(hits[g]) / len(texts[g]) for g in cols}
        pooled = sum(len(hits[g]) for g in test) / sum(len(texts[g]) for g in test)
        held, train, top = rate["h-held"], rate["h-train"], max(rate[g] for g in test)
        if name.startswith("count only"):
            verdict = "counted, not proposed"
        elif held <= 0.05 and top >= 0.30 and (LANG == "en" or train <= 0.05):
            verdict = "FAIL"
        elif (held > 0 or train > 0) and pooled >= 2 * held and pooled >= 2 * train:
            verdict = "TELL"
        else:
            verdict = "out"
        cells = "".join(f"{f'{len(hits[g])}/{len(texts[g])}':>11}" for g in cols)
        print(f"{name[:66]:66}{cells}{pooled:>9.2f}  {verdict}")
        if show and show in name:
            for g in cols:
                for t in hits[g]:
                    print(f"     {short[g]} {os.path.basename(t.path)}: {fn(t)[:70]}")


if __name__ == "__main__":
    main()

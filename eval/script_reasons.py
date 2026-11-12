#!/usr/bin/env python3
"""Blind judges on video narrations: assistant train scripts against human train captions.

The judge reads only the spoken words (harness.narration: spoken(), prose(), one run of
plain text), with JPROMPT_SCR or JPROMPT_SCR_ES. The AI side is every script in the four
train folders; the human side is 48 train captions picked round-robin over channels (sorted)
in file-name order, the train three quarters being every file but the 1st, 5th, ... by
sorted name. Answers are cached by eval/e2e/harness.py, so a rerun with the same judge is free.

The output gives the mean P(AI) per group, the judges' reasons grouped by what they point at
(a reason can be in several groups; each group is a regex over the reason, printed with it),
and every reason. Human captions are not redistributed, so on the human side every quoted
span is cut to its first four words.

Usage:
  JUDGE=claude-sonnet-5-5 python3 eval/script_reasons.py en|es [-k 2] > eval/results/script[-es]-reasons.txt
"""
import os, re, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "e2e"))
import harness  # noqa: E402

LANG = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("en", "es") else sys.exit(__doc__)
K = int(sys.argv[sys.argv.index("-k") + 1]) if "-k" in sys.argv else 2
SUB = "script" if LANG == "en" else "script-es"
HUM = os.path.expanduser(f"~/corpus/{SUB}")
AI = os.path.join(harness.REPO, "eval", "ai", SUB)
N_HUMAN = 48

GROUPS = {
    "en": {
        "ai": [
            ("even polish, uniform, tidy", r"polish|uniform|\beven\b|evenly|smooth|clean|balanced|tidy|neat|consistent|measured|organi[sz]ed|error-free|no errors"),
            ("stock phrases and cliches", r"stock|clich|canned|boilerplate|trite|familiar phrase"),
            ("tidy ending: recap, moral, callback, button", r"recap|summar|wrap|moral|closing|closer|conclusion|ending|ends? (?:on|with)|callback|bookend|aphoris|lesson|takeaway|button"),
            ("no personal voice, generic, no specifics", r"personal|voice|idiosyncra|generic|quirk|no specific|lacks? specific|digression|anecdote|first-hand|lived"),
            ("rhetorical questions answered at once", r"rhetorical|question"),
            ("signposting and explainer scaffolding", r"signpost|scaffold|template|formula|textbook|listicle|structure|segment|section|numbered|countdown"),
            ("lists of three, parallelism, repetition", r"tricolon|triad|three|parallel|anaphor|repetition|repeated"),
            ("hedged, encyclopedic, even-handed", r"hedg|encyclopedic|even-handed|cautious|caveat|disclaimer|neutral|both sides|qualif"),
            ("stock reveals and transitions (here's the twist)", r"here's|twist|reveal|setup|set-up|pivot|transition|teaser|cliffhanger"),
            ("engagement closer, call to action", r"subscribe|comments?\b|engagement|call to action|call-to-action|\bcta\b|sign-off|signoff|outro|like and|tell us below"),
            ("short punchy fragments, staccato rhythm", r"fragment|punchy|staccato|short sentences|clipped|one-liner|cadence|rhythm"),
            ("hook opening (imagine, cold open)", r"\bhook|imagine|opening|opens? with|cold open|\bintro\b"),
            ("engineered jokes and quips", r"quip|jok|\bpun\b|\bgag|wry|cute|wink|humou?r"),
            ("contrast frames (not X, but Y)", r"\bnot x|antithe|isn't|not just|rather than|negat|reframe"),
            ("leftover markup, citations, notes", r"citation|bracket|sources?:|narrator|artifact|end of script|reference:|stage direction"),
        ],
        "human": [
            ("transcription or caption artifacts", r"transcri|caption|typo|capitali[sz]|slip|garbled|misheard|duplicat|stray|amara|subtitle|punctuation"),
            ("personal voice, opinions, anecdotes", r"personal|voice|opinion|anecdote|first-person|persona"),
            ("specific names, sources, numbers", r"specific|citation|reference|detail|data|statistic"),
            ("humour, swearing, irreverence", r"humou?r|jok|\bgag|swear|crude|irreveren|comed|\bwit\b|witty|sarcas|profan"),
            ("spontaneous speech: asides, self-corrections, filler", r"aside|self-correct|interrupt|digress|tangent|spontaneous|false start|filler|disfluen|hesitat|improvis|stumble"),
            ("channel identity: sponsor, Patreon, earlier videos", r"sponsor|patreon|skillshare|channel|previous video|earlier video|episode|signature|sign-off|podcast|style"),
            ("uneven or rambling structure", r"uneven|run-on|meander|rambl|messy|irregular|loose|unpolished|rough"),
            ("cues the judge read as AI", r"polish|tidy|formula|could fit ai|hint at|lean ai|ai-like|ai polish"),
        ],
    },
    "es": {
        "ai": [
            ("pulido uniforme, tono parejo", r"pulid|uniform|limpi|impecable|equilibr|homog|pulcr|ordenad|cuidad|parej|regular"),
            ("estructura de plantilla, señales de orden", r"estructura|plantilla|f[oó]rmula|formul|manual|esquem|secci[oó]n|enumera|primer[oa]\b|bloques|did[aá]ctic"),
            ("cierre de canal, llamada a la acción", r"suscr[ií]b|coment|llamada a la acci|\bcta\b|like|despedida|me gusta|campanita"),
            ("preguntas retóricas que se responden", r"ret[oó]ric|pregunta"),
            ("sin voz personal, genérico", r"personal|voz|idiosincr|gen[eé]ric|an[eé]cdota|digresi|propio|muletilla|titube"),
            ("cierre redondo: resumen, moraleja, eco", r"resum|cierre|conclusi|moralej|lecci[oó]n|redond|remate|aforism|eco\b|recapitul"),
            ("frases cortas, fragmentos, efecto", r"fragment|frases cortas|cortas|ritmo|cadencia|efectis|contundent|golpe|punch"),
            ("contrastes de fórmula (no es X, es Y)", r"no es [^,]*\. es|no es x|contraste|ant[ií]tesis|no solo|sino"),
            ("matices y cautelas constantes, tono enciclopédico", r"matiz|cautel|prudent|neutr|enciclop|equilibrado y caut"),
            ("gancho de apertura", r"gancho|imagina|apertura|arranque|abre con|empieza con"),
            ("transiciones de fórmula (pero ojo, aquí viene)", r"transici|pero ojo|aqu[ií] viene|aqu[ií] est[aá]|vamos al|hablemos|pasemos"),
            ("listas de tres, paralelismo", r"tres|tr[ií]ada|tricolon|paralel|an[aá]fora|repetici"),
            ("promesa: quédate hasta el final, hoy vamos a", r"qu[eé]date|hoy vamos|hoy te|promesa"),
            ("restos de marcas, fuentes o notas", r"referencia|fuente|metatexto|etiqueta|marcador|sugerencia de|instrucci|encabezado|guion original"),
        ],
        "human": [
            ("errores de transcripción o de escritura", r"transcri|subt[ií]tul|typo|errata|errores|tilde|falta|mayúscula|may[uú]scula|puntuaci"),
            ("voz personal, opiniones", r"personal|voz|opini[oó]n|an[eé]cdota|primera persona|autorreferenc"),
            ("humor, coloquialismo, tacos", r"humor|chiste|broma|coloquial|jerga|irreveren|taco|ironía|iron[ií]a|gracia"),
            ("marca del canal: patrocinio, libro, otros vídeos", r"canal|patrocin|patreon|promoci|libro|v[ií]deo anterior|otros? v[ií]deos?|episodio|comunidad|marca"),
            ("habla espontánea: digresiones, autocorrecciones, muletillas", r"digresi|autocorrec|muletilla|espont[aá]ne|improvis|titube|oral|hablad"),
            ("referencias concretas", r"concret|espec[ií]fic|referencia|cifra|dato"),
            ("estructura desordenada o irregular", r"desorden|irregular|salto|abrupt|repetitiv|desigual|torpe"),
            ("pistas que el juez leyó como IA", r"pulid|f[oó]rmula|plantilla|t[ií]pic[oa] de (?:la )?ia|podr[ií]a ser ia|aunque"),
        ],
    },
}


def humans():
    names = sorted(n for n in os.listdir(HUM) if n.endswith(".md"))
    train = [n for i, n in enumerate(names) if i % 4 != 0]
    by = {}
    for n in train:
        by.setdefault(n.split("-", 1)[0], []).append(n)
    out, r = [], 0
    while len(out) < N_HUMAN:
        for ch in sorted(by):
            if r < len(by[ch]) and len(out) < N_HUMAN:
                out.append(os.path.join(HUM, by[ch][r]))
        r += 1
    return out


def shorten(reason):
    """cut every quoted span to its first four words"""
    def cut(m):
        words = m.group(2).split()
        return m.group(1) + " ".join(words[:4]) + (" …" if len(words) > 4 else "") + m.group(3)
    for q in (r'(")([^"]{3,600})(")', r"(“)([^”]{3,600})(”)", r"(«)([^»]{3,600})(»)", r"(‘)([^’]{3,600})(’)",
              r"((?<!\w)')(.{3,600}?)('(?!\w))"):
        reason = re.sub(q, cut, reason)
    return reason


def main():
    hum = humans()
    ai = [os.path.join(AI, d, n) for d in sorted(os.listdir(AI)) if d.startswith("train-")
          for n in sorted(os.listdir(os.path.join(AI, d))) if n.endswith(".md")]
    jp = harness.JPROMPT_SCR_ES if LANG == "es" else harness.JPROMPT_SCR
    res = harness.judge_files(hum + ai, k=K, j=8, jp=jp)
    mean = lambda fs: st.mean(st.mean(r["p_ai"] for r in res[f] if r["p_ai"] is not None) for f in fs)
    over = lambda fs: sum(st.mean(r["p_ai"] for r in res[f] if r["p_ai"] is not None) > 50 for f in fs)
    print(f"# Blind judges on {'Spanish' if LANG == 'es' else 'English'} video narrations: "
          f"JUDGE={harness.JUDGE}, k={K}, prompt {'JPROMPT_SCR_ES' if LANG == 'es' else 'JPROMPT_SCR'}")
    print(f"# JUDGE={harness.JUDGE} python3 eval/script_reasons.py {LANG} -k {K}")
    print("# The judge reads the narration only (harness.narration). Human captions are not redistributed:")
    print("# on the human side every quoted span is cut to its first four words.\n")
    print(f"{'group':28}{'texts':>6}{'mean P(AI)':>12}{'over 50':>9}")
    print(f"{'human train captions':28}{len(hum):>6}{mean(hum):>12.1f}{over(hum):>9}")
    print(f"{'assistant train scripts':28}{len(ai):>6}{mean(ai):>12.1f}{over(ai):>9}")
    for d in sorted({os.path.basename(os.path.dirname(f)) for f in ai}):
        fs = [f for f in ai if os.path.basename(os.path.dirname(f)) == d]
        print(f"{'  ' + d:28}{len(fs):>6}{mean(fs):>12.1f}{over(fs):>9}")
    print(f"\nhuman texts judged: {', '.join(os.path.basename(f) for f in hum)}")
    for side, fs in (("ai", ai), ("human", hum)):
        reasons = [x for f in fs for r in res[f] for x in r["reasons"]]
        label = "assistant scripts" if side == "ai" else "human captions"
        print(f"\n## Reasons on the {label}: {len(reasons)}, grouped (a reason can be in several groups)")
        rows = [(sum(bool(re.search(rx, x, re.I)) for x in reasons), name, rx) for name, rx in GROUPS[LANG][side]]
        for n, name, rx in sorted(rows, key=lambda r: -r[0]):
            print(f"{n:5}  {name}    /{rx}/")
        none = sum(not any(re.search(rx, x, re.I) for _, rx in GROUPS[LANG][side]) for x in reasons)
        print(f"{none:5}  in none of these")
    for side, fs in (("ai", ai), ("human", hum)):
        print(f"\n## Every reason, {'assistant scripts' if side == 'ai' else 'human captions (quotes cut)'}")
        for f in fs:
            p = st.mean(r["p_ai"] for r in res[f] if r["p_ai"] is not None)
            name = os.path.basename(os.path.dirname(f)) + "/" + os.path.basename(f) if side == "ai" else os.path.basename(f)
            print(f"\n{name}  P(AI) {p:.1f}")
            for r in res[f]:
                for x in r["reasons"]:
                    print(f"  - {x if side == 'ai' else shorten(x)}")


if __name__ == "__main__":
    main()

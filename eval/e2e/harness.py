#!/usr/bin/env python3
"""End-to-end harness: rewrite drafts with a skill snapshot, then judge blind.

  harness.py snapshot NAME [SRC] [--no-script-rules]
                                          copy SKILL.md, references/, scripts/ from SRC (repo) to snaps/NAME
  harness.py rewrite SNAP REP [-j N] [--set dev|test|scr|...] [--names a,b]
  harness.py judge FILES... [-k 3] [-j N]  prints per-file mean P(AI); cached in judge-cache.jsonl
  harness.py report SNAP [SNAP...] [--set dev]
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, threading, statistics as st
from concurrent.futures import ThreadPoolExecutor

CODE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(CODE, "..", ".."))
H = os.environ.get("QUIRON_E2E", os.path.expanduser("~/.cache/quiron-e2e"))  # work data
os.makedirs(H, exist_ok=True)
CORPUS = os.path.expanduser("~/corpus/blog")
ISO = ["--setting-sources", "project", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
       "--no-session-persistence"]
MODEL = "claude-opus-5-5"
JUDGE = os.environ.get("JUDGE", MODEL)  # Claude judge; a non-default one gets its own cache keys
GPT = os.environ.get("GPT_MODEL", "gpt-5.6-sol")  # Codex rewriter and GPT judge
LOCK = threading.Lock()


def sets():
    out = {}
    for p in sorted(os.listdir(os.path.join(CODE, "sets"))):
        rows = [l.split("\t") for l in open(os.path.join(CODE, "sets", p), encoding="utf-8").read().splitlines() if l.strip()]
        for r in rows:
            r[1] = os.path.join(REPO, os.path.expanduser(r[1]))  # ~/corpus/... for human originals
            if r[2] != "-":
                r[2] = os.path.join(REPO, r[2])
        out[p[:-4]] = rows
    return out  # rows: name, draft_path, notes_path ("-" for none)[, fiction prompt]


def snapshot(name, src, no_script_rules=False):
    dst = os.path.join(H, "snaps", name)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    shutil.copy(os.path.join(src, "SKILL.md"), dst)
    for d in ("references", "scripts"):
        shutil.copytree(os.path.join(src, d), os.path.join(dst, d),
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "build-*.sh"))
    if no_script_rules:
        strip_script_rules(dst)
    print(dst)


# The "bands" snapshot of the video-script register: the band files and the register's entry
# in SKILL.md, without references/script.md, the line that sends the rewriter to it, or the
# script checks S1-S7 and SE1-SE8. Every edit must apply, or the snapshot is not what it says.
# The rules were tested at commit 37a1cff and did not ship; from a later tree with no
# references/script.md only the checks are turned off.
SCRIPT_RULE_EDITS = [
    ("SKILL.md", "- [references/script.md](references/script.md): the rewrite rules for video scripts.\n", ""),
    ("SKILL.md", " **Read [references/script.md](references/script.md) before rewriting a\n  script.**", ""),
]
SCRIPT_CHECK_EDIT = (os.path.join("scripts", "audit.py"), '_new = CHECKS_SCRIPT_ES if LANG == "es" else CHECKS_SCRIPT',
                     "_new = []")


def strip_script_rules(dst):
    rules = os.path.join(dst, "references", "script.md")
    edits = [SCRIPT_CHECK_EDIT]
    if os.path.exists(rules):
        os.remove(rules)
        edits += SCRIPT_RULE_EDITS
    for rel, old, new in edits:
        p = os.path.join(dst, rel)
        text = open(p, encoding="utf-8").read()
        if text.count(old) != 1:
            sys.exit(f"--no-script-rules: {rel} does not have exactly one {old!r}")
        open(p, "w", encoding="utf-8", newline="").write(text.replace(old, new))


PROMPT = ("Use the quiron skill. Rewrite this dev.to blog post draft (draft.md) so it reads like I "
          "wrote it. My notes about what actually happened are in notes.txt. Save the finished post "
          "as final.md in this folder.\n")


PROMPT_NONOTES = ("Use the quiron skill on this dev.to blog post draft (draft.md) so it does not read as "
                  "AI-written. I have no notes for it; work from the draft alone and do not stop to "
                  "ask me. Save the finished post as final.md in this folder.\n")


PROMPT_ES = ("Usa la skill quiron. Reescribe este borrador de post para dev.to (draft.md) para que "
             "suene a que lo escribí yo. Mis notas sobre lo que pasó de verdad están en notes.txt. "
             "Guarda el post terminado como final.md en esta carpeta.\n")
ES_NAMES = {r[0] for r in sets().get("es", [])}


FIC = {r[0]: r[3] for r in sets().get("fic", [])}
PROMPT_FIC = ("Use the quiron skill. This short story (draft.md) I generated as a reply to a Reddit "
              "WritingPrompts prompt sounds like AI. Rewrite it so it reads like a person wrote it. "
              "The prompt was: %s\nSave the finished story as final.md in this folder.\n")


# Video scripts: the fourth column is the video's title; a set named scr*-es gets Spanish.
PROMPT_SCR = ('Use the quiron skill. This video script (draft.md) I generated for a YouTube video titled "%s". '
              'Rewrite it so it does not read as AI-written. I have no notes; do not stop to ask. Keep the '
              'stage directions. Write the result to final.md.')
PROMPT_SCR_ES = ('Usa la skill quiron. Este guion de video (draft.md) lo generé para un video de YouTube titulado '
                 '"%s". Reescríbelo para que no se lea como escrito por una IA. No tengo notas; no te detengas a '
                 'preguntar. Conserva las acotaciones. Escribe el resultado en final.md.')
SCR = {r[0]: (PROMPT_SCR_ES if s.endswith("-es") else PROMPT_SCR) % r[3]
       for s, rows in sets().items() if s.startswith("scr") for r in rows}


def rewrite_prompt(name, notes):
    if name in SCR:
        return SCR[name]
    if name in FIC:
        return PROMPT_FIC % FIC[name]
    return PROMPT_ES if name in ES_NAMES else PROMPT if notes != "-" else PROMPT_NONOTES


def rewrite_one(snap, rep, row):
    name, draft, notes = row[:3]
    wd = os.path.join(H, "work", snap, f"r{rep}", name)
    if os.path.exists(os.path.join(wd, "final.md")):
        return name, "cached"
    if os.path.exists(wd):
        shutil.rmtree(wd)
    os.makedirs(os.path.join(wd, ".claude", "skills"))
    shutil.copytree(os.path.join(H, "snaps", snap), os.path.join(wd, ".claude", "skills", "quiron"))
    shutil.copy(draft, os.path.join(wd, "draft.md"))
    if notes != "-":
        shutil.copy(notes, os.path.join(wd, "notes.txt"))
    cmd = ["claude", "-p", "--model", os.environ.get("REWRITER", MODEL), *ISO, "--permission-mode", "bypassPermissions",
           "--output-format", "json", rewrite_prompt(name, notes)]
    if os.environ.get("REWRITER") == "codex":  # a non-Claude agent: point it at the skill file
        cmd = ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "--ignore-user-config",
               "-s", "workspace-write", "-m", GPT,
               "Read .claude/skills/quiron/SKILL.md and follow it as your instructions for this "
               "task; its paths are relative to that folder. " + cmd[-1]]
    try:
        r = subprocess.run(cmd, cwd=wd, capture_output=True, text=True, timeout=2400)
        open(os.path.join(wd, "run.json"), "w").write(r.stdout)
        ok = os.path.exists(os.path.join(wd, "final.md"))
        if ok:  # keep every finished rewrite outside the work tree
            bk = os.path.join(H, "backup", snap, f"r{rep}")
            os.makedirs(bk, exist_ok=True)
            shutil.copy(os.path.join(wd, "final.md"), os.path.join(bk, name + ".md"))
        return name, "ok" if ok else "NO FINAL: " + r.stderr[-300:]
    except subprocess.TimeoutExpired:
        return name, "timeout"


JPROMPT_FIC = """Below is a short story posted as a reply to a Reddit WritingPrompts prompt. Some replies were written by people, others were generated by an AI assistant. Estimate the probability, from 0 to 100, that this story was AI-generated. Judge the writing itself.

Reply with JSON only, no code fence: {"p_ai": <integer 0-100>, "reasons": ["<short cue, quoting the text where you can>", "..."]} with at most 3 reasons.

<story>
%s
</story>"""

JPROMPT = """Below is a blog post published on dev.to. Some posts on the site were written by people, others were generated by an AI assistant. Estimate the probability, from 0 to 100, that this post was AI-generated. Judge the writing itself; do not use dates, version numbers or how recent the technology is as evidence either way.

Reply with JSON only, no code fence: {"p_ai": <integer 0-100>, "reasons": ["<short cue, quoting the text where you can>", "..."]} with at most 3 reasons.

<post>
%s
</post>"""


# Video scripts: the judge reads the narration only, the same words aimeter measures under a
# "_spoken" band file. Captions have no paragraphs, emphasis or curly quotes, so the
# assistant scripts lose theirs too, or the layout would give them away before the writing.
JPROMPT_SCR = """Below is the narration of a YouTube video. Some narrations were written by people, others were generated by an AI assistant. Estimate the probability, from 0 to 100, that this narration was AI-generated. Judge the writing itself; do not use dates, version numbers or how recent the technology is as evidence either way.

Reply with JSON only, no code fence: {"p_ai": <integer 0-100>, "reasons": ["<short cue, quoting the text where you can>", "..."]} with at most 3 reasons.

<narration>
%s
</narration>"""

JPROMPT_SCR_ES = """Abajo está la narración de un video de YouTube. Algunas narraciones las escribieron personas y otras las generó un asistente de IA. Estima la probabilidad, de 0 a 100, de que esta narración la haya generado una IA. Juzga la escritura misma; no uses fechas, números de versión ni lo reciente de la tecnología como prueba en ningún sentido.

Responde solo con JSON, sin bloque de código: {"p_ai": <entero 0-100>, "reasons": ["<pista breve, citando el texto cuando puedas>", "..."]} con 3 razones como mucho.

<narracion>
%s
</narracion>"""
SCRIPT_PROMPTS = (JPROMPT_SCR, JPROMPT_SCR_ES)


def script_prompt(name):
    """JSCR=1 (or a set named scr*) gives the English prompt, JSCR=es (or scr*-es) the Spanish one."""
    return JPROMPT_SCR_ES if name == "es" or name.endswith("-es") else JPROMPT_SCR


def narration(text):
    """The spoken words of a script as one run of plain text."""
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import aimeter
    t = aimeter.prose(aimeter.spoken(text))
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"\*+|(?<!\w)_+|_+(?!\w)", "", t)
    return re.sub(r"\s+", " ", t).strip()


def cache_path():
    return os.path.join(H, "judge-cache.jsonl")


def load_cache():
    c = {}
    if os.path.exists(cache_path()):
        for l in open(cache_path()):
            d = json.loads(l)
            c[(d["h"], d["k"])] = d
    return c


def judge_one(text, k, cache, jp=None):
    h = hashlib.sha256(text.encode()).hexdigest()[:16]
    if (h, k) in cache:
        return cache[(h, k)]
    if isinstance(k, str) and k.startswith("g"):  # GPT judge through the Codex CLI
        cmd = ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "--ignore-user-config",
               "-m", GPT, "-c", 'model_reasoning_effort="medium"', "-s", "read-only", "-"]
        wd = os.path.join(H, "jwd-gpt")
    else:
        cmd = ["claude", "-p", "--model", JUDGE, *ISO, "--tools", "", "--output-format", "text"]
        wd = os.path.join(H, "jwd")
    for attempt in range(3):
        try:
            r = subprocess.run(cmd, cwd=wd, input=(jp or JPROMPT) % text, capture_output=True, text=True, timeout=900)
            m = re.search(r"\{.*\}", r.stdout, re.S)
            d = json.loads(m.group(0))
            rec = {"h": h, "k": k, "p_ai": int(d["p_ai"]), "reasons": d.get("reasons", [])}
            with LOCK:
                open(cache_path(), "a").write(json.dumps(rec) + "\n")
                cache[(h, k)] = rec
            return rec
        except Exception as e:  # noqa
            err = str(e)
    return {"h": h, "k": k, "p_ai": None, "reasons": ["ERROR " + err]}


def strip_front(text):
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).strip()


def judge_files(files, k=3, j=8, gpt=0, jp=None):
    os.makedirs(os.path.join(H, "jwd"), exist_ok=True)
    os.makedirs(os.path.join(H, "jwd-gpt"), exist_ok=True)
    cache = load_cache()
    ck = (lambda i: i) if JUDGE == MODEL else (lambda i: f"{JUDGE}:{i}")
    gk = (lambda i: f"g{i}") if GPT == "gpt-5.6-sol" else (lambda i: f"g:{GPT}:{i}")
    texts = {f: strip_front(open(f, encoding="utf-8").read()) for f in files}
    if jp in SCRIPT_PROMPTS:  # narration only, and cache keys of its own: the prompt is not in the key
        texts = {f: narration(t) for f, t in texts.items()}
        tag = "scr-es" if jp is JPROMPT_SCR_ES else "scr"
        ck0, gk0 = ck, gk
        ck, gk = (lambda i: f"{tag}:{ck0(i)}"), (lambda i: f"g{tag}:{gk0(i)}")
    jobs = [(f, ck(i)) for f in files for i in range(k)] + [(f, gk(i)) for f in files for i in range(gpt)]
    with ThreadPoolExecutor(j) as ex:
        res = list(ex.map(lambda fi: (fi[0], judge_one(texts[fi[0]], fi[1], cache, jp)), jobs))
    out = {}
    for f, rec in res:
        out.setdefault(f, []).append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("args", nargs="*")
    ap.add_argument("-j", type=int, default=6)
    ap.add_argument("-k", type=int, default=3)
    ap.add_argument("-g", type=int, default=0)
    ap.add_argument("--set", default="dev")
    ap.add_argument("--names")
    ap.add_argument("--no-script-rules", action="store_true")
    a = ap.parse_args()
    if a.cmd == "snapshot":
        snapshot(a.args[0], a.args[1] if len(a.args) > 1 else REPO, a.no_script_rules)
    elif a.cmd == "rewrite":
        snap, rep = a.args[0], a.args[1]
        rows = sets()[a.set]
        if a.names:
            rows = [r for r in rows if r[0] in a.names.split(",")]
        with ThreadPoolExecutor(a.j) as ex:
            for name, status in ex.map(lambda r: rewrite_one(snap, rep, r), rows):
                print(name, status, flush=True)
    elif a.cmd == "judge":
        res = judge_files(a.args, a.k, a.j, a.g, JPROMPT_FIC if os.environ.get("JFIC") else
                          script_prompt(os.environ["JSCR"]) if os.environ.get("JSCR") else None)
        for f, recs in res.items():
            ps = [r["p_ai"] for r in recs if r["p_ai"] is not None and not str(r["k"]).startswith("g")]
            pg = [r["p_ai"] for r in recs if r["p_ai"] is not None and str(r["k"]).startswith("g")]
            print(f"{st.mean(ps) if ps else float('nan'):6.1f} {st.mean(pg) if pg else float('nan'):6.1f}  {f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate assistant samples for eval/ai/ from the title files, one text per title.

  gensamples.py REGISTER TITLES.tsv MODEL OUTDIR [-j N]

REGISTER is blog, es or fiction. MODEL is a Claude model id (run through `claude -p`) or
a GPT one (run through `codex exec`). The prompt is the plain request documented in
eval/README.md. A ```markdown wrapper and the model's comments
outside it are dropped, as is dev.to front matter. Titles already written are skipped, and every text is logged with its
model and date in OUTDIR/../MANIFEST.tsv.
"""
import argparse, datetime, os, re, subprocess, sys, tempfile, threading
from concurrent.futures import ThreadPoolExecutor

PROMPTS = {
    "blog": 'Write a blog post for dev.to titled "%s". Around %d words.',
    "es": 'Escribe un post para dev.to titulado "%s". Unas %d palabras.',
    "fiction": "Write a short story for this Reddit WritingPrompts prompt: %s Around %d words.",
}
ISO = ["--setting-sources", "project", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
       "--no-session-persistence"]
LOCK = threading.Lock()
WD = tempfile.mkdtemp(prefix="quiron-gen-")  # empty folder: no project instructions leak in


FENCE = re.compile(r"^(`{3,})(?:markdown|md)[ \t]*$", re.M)


def clean(text):
    """The post itself: what is inside a ```markdown wrapper when the model used one
    (its comments to the user outside the wrapper are dropped), without front matter.
    Some models fence only the front matter and write the post after it."""
    m = FENCE.search(text)
    if m and not re.search(r"^#{1,6} ", text[:m.start()], re.M):  # a heading first: the post began
        rest = text[m.end():]
        ends = [e for e in re.finditer(r"^%s[ \t]*$" % re.escape(m.group(1)), rest, re.M)]
        if ends and re.fullmatch(r"\s*---\n.*?\n---\s*", rest[:ends[0].start()], re.S):
            text = rest[ends[0].end():]
        else:
            inner = rest[:ends[-1].start()] if ends else rest
            if len(inner.split()) >= 0.5 * len(text.split()):  # else a ```markdown example in the post
                text = inner
    return re.sub(r"\A\s*---\n.*?\n---\n", "", text, flags=re.S).strip()


def generate(model, prompt):
    if model.startswith("gpt"):
        cmd = ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "--ignore-user-config",
               "-m", model, "-s", "read-only", "-"]
    else:
        cmd = ["claude", "-p", "--model", model, *ISO, "--tools", "", "--output-format", "text"]
    r = subprocess.run(cmd, cwd=WD, input=prompt, capture_output=True, text=True, timeout=1200,
                       encoding="utf-8")
    return r.stdout.strip(), r.stderr[-300:]


def one(a, row):
    name, words, title = row
    out = os.path.join(a.outdir, name + ".md")
    if os.path.exists(out):
        return name, "cached"
    n = max(600, min(1400, int(words)))
    prompt = PROMPTS[a.register] % (title, n)
    for _ in range(2):
        text, err = generate(a.model, prompt)
        text = clean(text)
        if len(re.findall(r"\w+", text)) >= 200:
            break
    else:
        return name, "FAILED: " + err
    open(out, "w", encoding="utf-8", newline="\n").write(text + "\n")
    with LOCK:
        open(os.path.join(os.path.dirname(os.path.abspath(a.outdir)), "MANIFEST.tsv"), "a",
             encoding="utf-8", newline="\n").write("\t".join(
                 [os.path.basename(os.path.abspath(a.outdir)), name, a.model,
                  datetime.date.today().isoformat(), prompt.replace("\t", " ")]) + "\n")
    return name, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("register", choices=PROMPTS)
    ap.add_argument("titles")
    ap.add_argument("model")
    ap.add_argument("outdir")
    ap.add_argument("-j", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    rows = [l.split("\t", 2) for l in open(a.titles, encoding="utf-8").read().splitlines() if l.strip()]
    bad = 0
    with ThreadPoolExecutor(a.j) as ex:
        for name, status in ex.map(lambda r: one(a, r), rows):
            print(name, status, flush=True)
            bad += status.startswith("FAILED")
    sys.exit(bad)


if __name__ == "__main__":
    main()

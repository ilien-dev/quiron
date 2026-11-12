#!/usr/bin/env python3
"""Generate assistant samples for eval/ai/ from the title files, one text per title.

  gensamples.py REGISTER TITLES.tsv MODEL OUTDIR [-j N]

REGISTER is blog, es, fiction, pr, commit, readme, email, script or script-es. MODEL is a Claude model id
(run through `claude -p`) or a GPT one (run through `codex exec`). The prompt is the plain
request documented in eval/README.md. A ```markdown wrapper and the model's comments
outside it are dropped, as is dev.to front matter. Titles already written are skipped,
and every text is logged with its model and date in OUTDIR/../MANIFEST.tsv.

  gensamples.py --titles REGISTER HUMAN_DIR    write eval/titles/REGISTER-{train,test}-*.tsv
                                               from HUMAN_DIR/titles.tsv, the held-out
                                               quarter of the human texts going to test
"""
import argparse, datetime, hashlib, os, re, subprocess, sys, tempfile, threading
from concurrent.futures import ThreadPoolExecutor

PROMPTS = {
    "blog": 'Write a blog post for dev.to titled "%s". Around %d words.',
    "es": 'Escribe un post para dev.to titulado "%s". Unas %d palabras.',
    "fiction": "Write a short story for this Reddit WritingPrompts prompt: %s Around %d words.",
    # the title column already carries its quotes and context: "Fix X" in the a/b repository
    "pr": "Write the description for a pull request titled %s. Around %d words.",
    "commit": "Write the commit message for a commit with the subject %s. Around %d words.",
    "readme": "Write the README for a project called %s. Around %d words.",
    "email": "Write an email with the subject %s. Around %d words.",
    "script": 'Write the script for a YouTube video titled "%s". Around %d words.',
    "script-es": 'Escribe el guion de un video de YouTube titulado "%s". Unas %d palabras.',
}
WORK = ("pr", "commit", "readme", "email")
LENGTH = {"pr": (130, 500), "commit": (130, 500), "email": (130, 500), "readme": (300, 1200),
          "script": (300, 3000), "script-es": (300, 3000)}  # else 600-1400
ISO = ["--setting-sources", "project", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
       "--no-session-persistence"]
LOCK = threading.Lock()
WD = tempfile.mkdtemp(prefix="quiron-gen-")  # empty folder: no project instructions leak in


FENCE = re.compile(r"^(`{3,})(?:markdown|md)[ \t]*$", re.M)
# a commit message, an email or a PR description comes back in a bare or ```text block
FENCE_WORK = re.compile(r"^(`{3,})(?:markdown|md|text|txt|plaintext|gitcommit|email)?[ \t]*$", re.M)
SCRIPT = ("script", "script-es")  # kept as written: stage directions, labels and headings stay


def clean(text, register="blog"):
    """The post itself: what is inside a ```markdown wrapper when the model used one
    (its comments to the user outside the wrapper are dropped), without front matter.
    Some models fence only the front matter and write the post after it."""
    m = (FENCE_WORK if register in ("pr", "commit", "email") + SCRIPT else FENCE).search(text)
    if m and not re.search(r"^#{1,6} ", text[:m.start()], re.M):  # a heading first: the post began
        rest = text[m.end():]
        ends = [e for e in re.finditer(r"^%s[ \t]*$" % re.escape(m.group(1)), rest, re.M)]
        if ends and re.fullmatch(r"\s*---\n.*?\n---\s*", rest[:ends[0].start()], re.S):
            text = rest[ends[0].end():]
        else:
            inner = rest[:ends[-1].start()] if ends else rest
            if len(inner.split()) >= 0.5 * len(text.split()):  # else a ```markdown example in the post
                text = inner
    if register == "email":  # the subject goes in its own field, not in the body
        text = re.sub(r"\A\s*\**Subject:.*\n", "", text)
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
    lo, hi = LENGTH.get(a.register, (600, 1400))
    n = max(lo, min(hi, int(words)))
    prompt = PROMPTS[a.register] % (title, n)
    for _ in range(2):
        text, err = generate(a.model, prompt)
        text = clean(text, a.register)
        if len(re.findall(r"\w+", text)) >= (100 if a.register in WORK else 200):
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


# titles per model (train, test) for the registers that do not take every fourth title
SIZES = {"script": (12, 9), "script-es": (12, 5)}


def spread(pool, want):
    """want titles spread over channels and lengths, no random choice: channels take turns
    (the channel is the file name without its 11-character video id), and inside a channel
    titles come in the order of their sha1, so the same corpus gives the same pick."""
    by = {}
    for l in sorted(pool, key=lambda l: hashlib.sha1(l.split("\t")[0].encode()).hexdigest()):
        by.setdefault(l.split("\t")[0][:-12], []).append(l)
    picked = []
    while len(picked) < want and any(by.values()):
        for ch in sorted(by):
            if by[ch] and len(picked) < want:
                picked.append(by[ch].pop(0))
    return picked


def titles(register, human_dir):
    """Title files for a register: every fourth human text (sorted by file name) is held
    out, as in evaluate.py, and its title goes to the test models; the rest to training."""
    rows = [l for l in open(os.path.join(human_dir, "titles.tsv"), encoding="utf-8").read().splitlines()
            if l.strip()]
    rows.sort(key=lambda l: l.split("\t")[0] + ".md")
    held = [l for i, l in enumerate(rows) if i % 4 == 0]
    cal = [l for i, l in enumerate(rows) if i % 4]
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "titles")
    for split, pool, per, models in (("train", cal, 8, ("opus", "sonnet", "haiku", "gpt")),
                                     ("test", held, 10, ("opus", "sonnet", "fable", "gpt", "terra"))):
        if register in SIZES:
            per = min(SIZES[register][split == "test"], len(pool) // len(models))
            picked = spread(pool, per * len(models))
            picked.sort(key=lambda l: (int(l.split("\t")[1]), l))  # each model gets the whole length range
        else:
            want = per * len(models)
            picked = pool[::max(1, len(pool) // want)][:want]
        for k, m in enumerate(models):
            open(os.path.join(here, f"{register}-{split}-{m}.tsv"), "w", encoding="utf-8",
                 newline="\n").write("\n".join(picked[k::len(models)]) + "\n")
    print(f"{register}: {len(cal)} training titles and {len(held)} held-out ones to choose from")


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--titles":
        return titles(sys.argv[2], sys.argv[3])
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

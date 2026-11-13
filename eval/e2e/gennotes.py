#!/usr/bin/env python3
"""gennotes.py OUTDIR NAME... : terse author notes from the human text of the same name.

  CORPUS=blog    (default) the post ~/corpus/blog/NAME.md; Claude Opus 5.5 writes the notes
  CORPUS=script  the caption ~/corpus/script/NAME.md of a YouTube video; also script-es
                 (a corpus name starting with "script" switches the prompt to the video one,
                 and the default model to claude-sonnet-5-5)
  NOTES_MODEL=M  overrides the model in either mode (Opus was rate-limited in November 2026)

In script mode every note is scanned against its caption, the way eval/script_reasons.py scans
the judges' reasons: no run of more than four words may stand in both. A note with such a run is
asked again (up to three times) with the runs listed; a bullet that still shares one is dropped.
"""
import subprocess, os, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
out, names = sys.argv[1], sys.argv[2:]
os.makedirs(out, exist_ok=True)
CORPUS = os.environ.get("CORPUS", "blog")
SCRIPT = CORPUS.startswith("script")
MODEL = os.environ.get("NOTES_MODEL", "claude-sonnet-5-5" if SCRIPT else "claude-opus-5-5")
ex = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'notes', 'ben-844325.txt')).read()
PROMPT_POST = ("You are helping build an evaluation set. Below is a real blog post. Extract the terse factual notes its author would hand a ghostwriter: what happened, real names (projects, tools, people, companies), numbers, links (copy URLs exactly), and the author's opinions, doubts and mistakes. 6 to 18 bullets starting with '- ', terse fragments, no full prose, do not copy sentences verbatim, no headings, write the notes in the same language as the post, output only the bullets. Example of the format:\n")
PROMPT_SCRIPT = ("You are helping build an evaluation set. Below is the script of a real YouTube video, as its captions. Extract the terse factual notes its creator would hand a scriptwriter: what the video covers and in what order, real names (people, places, products, works, channels), numbers and dates, and the creator's own opinions, doubts, jokes and asides. 8 to 20 bullets starting with '- ', terse fragments, no full prose, do not copy sentences or runs of more than four words from the script, no headings, write the notes in the same language as the script, output only the bullets. Example of the format (from a blog post; the notes for a video have the same shape):\n")
import re
WORD = re.compile(r"[^\W_]+")
def words(t): return [m.group(0).lower() for m in WORD.finditer(t)]
def shared(note, caption, n=5):
    """Runs of at least n consecutive words of the note that also stand in the caption."""
    hay = " " + " ".join(words(caption)) + " "
    ws, out, i = words(note), [], 0
    while i < len(ws):
        k = n
        if i + k <= len(ws) and " " + " ".join(ws[i:i + k]) + " " in hay:
            while i + k + 1 <= len(ws) and " " + " ".join(ws[i:i + k + 1]) + " " in hay: k += 1
            out.append(" ".join(ws[i:i + k])); i += k
        else:
            i += 1
    return out
def ask(p):
    r = subprocess.run(['claude', '-p', '--model', MODEL, '--setting-sources', 'project', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--no-session-persistence', '--tools', ''], input=p, capture_output=True, text=True, encoding='utf-8', cwd=tempfile.gettempdir())
    return r.stdout.strip()
def gen(n):
    o = f'{out}/{n}.txt'
    if os.path.exists(o) and os.path.getsize(o) > 50: return n, 'cached'
    post = open(os.path.expanduser(f'~/corpus/{CORPUS}/{n}.md'), encoding='utf-8').read()
    tag = ("script", "script") if SCRIPT else ("post", "post")
    p = ((PROMPT_SCRIPT if SCRIPT else PROMPT_POST) + ex + f"\n\n<{tag[0]}>\n" + post + f"\n</{tag[1]}>")
    note = ask(p)
    if SCRIPT:
        for _ in range(3):
            runs = shared(note, post)
            if not runs: break
            note = ask(p + "\n\nA first version of the notes was:\n" + note + "\n\nThese runs of words stand in both the notes and the script: " + "; ".join(f'"{r}"' for r in runs) + ". Write the notes again with the same facts, in your own words, so that no run of five or more consecutive words is shared with the script. Output only the bullets.")
        if shared(note, post):  # drop what is still copied, bullet by bullet
            note = "\n".join(b for b in note.splitlines() if not shared(b, post))
    open(o, 'w', encoding='utf-8', newline='\n').write(note + '\n'); return n, len(note)
with ThreadPoolExecutor(8) as e:
    for x in e.map(gen, names): print(*x)

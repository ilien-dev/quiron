#!/usr/bin/env python3
"""gennotes.py OUTDIR NAME... : terse author notes from the human post, as for set-test."""
import subprocess, os, sys
from concurrent.futures import ThreadPoolExecutor
out, names = sys.argv[1], sys.argv[2:]
os.makedirs(out, exist_ok=True)
ex = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'notes', 'ben-844325.txt')).read()
def gen(n):
    o = f'{out}/{n}.txt'
    if os.path.exists(o) and os.path.getsize(o) > 50: return n, 'cached'
    post = open(os.path.expanduser(f'~/corpus/{os.environ.get("CORPUS","blog")}/{n}.md')).read()
    p = ("You are helping build an evaluation set. Below is a real blog post. Extract the terse factual notes its author would hand a ghostwriter: what happened, real names (projects, tools, people, companies), numbers, links (copy URLs exactly), and the author's opinions, doubts and mistakes. 6 to 18 bullets starting with '- ', terse fragments, no full prose, do not copy sentences verbatim, no headings, write the notes in the same language as the post, output only the bullets. Example of the format:\n" + ex + "\n\n<post>\n" + post + "\n</post>")
    r = subprocess.run(['claude', '-p', '--model', 'claude-opus-5-5', '--setting-sources', 'project', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--no-session-persistence', '--tools', ''], input=p, capture_output=True, text=True, cwd='/tmp')
    open(o, 'w').write(r.stdout.strip() + '\n'); return n, len(r.stdout)
with ThreadPoolExecutor(8) as e:
    for x in e.map(gen, names): print(*x)

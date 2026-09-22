#!/usr/bin/env python3
"""Block any CLAUDE.md in this repo from growing past its token budget.

Runs as a PostToolUse hook (Write/Edit/MultiEdit on a CLAUDE.md) and as a Stop
hook (catches edits made through Bash). Exit 2 sends stderr back to Claude.

No tokenizer ships with the standard library, so the count is an estimate:
characters / 3.5, a conservative ratio for English markdown. Nothing here
touches the network.
"""
import json, math, os, sys

BUDGET = 1000
CHARS_PER_TOKEN = 3.5

try:
    event = json.load(sys.stdin)
except ValueError:
    event = {}

root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
target = (event.get("tool_input") or {}).get("file_path")
if target:
    inside = os.path.abspath(target).startswith(os.path.abspath(root) + os.sep)
    if os.path.basename(target) != "CLAUDE.md" or not inside:
        sys.exit(0)
    paths = [target]
else:
    paths = [os.path.join(root, "CLAUDE.md")]

over = []
for p in paths:
    if not os.path.isfile(p):
        continue
    tokens = math.ceil(len(open(p, encoding="utf-8").read()) / CHARS_PER_TOKEN)
    if tokens > BUDGET:
        over.append((os.path.relpath(p, root), tokens))

if not over:
    sys.exit(0)

for path, tokens in over:
    print(
        f"{path} is ~{tokens} tokens (estimate: chars / {CHARS_PER_TOKEN}); "
        f"the limit is {BUDGET}. Rewrite the whole file to fit, do not just trim "
        f"the part you added: merge overlapping points, cut anything discoverable "
        f"by reading the code, keep every rule and command that still applies. "
        f"Do not mention this limit in the file.",
        file=sys.stderr,
    )
sys.exit(2)

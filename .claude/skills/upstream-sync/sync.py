#!/usr/bin/env python3
"""Keep local clones of quirón's reference repos current and say what changed.

    sync.py update            clone missing repos, move the rest to their default branch tip
    sync.py status            per repo: head, last reviewed commit, what is new since then
    sync.py diff OWNER/REPO   write what changed since the last review to a file, print its path
    sync.py mark OWNER/REPO [SHA]   record SHA (default: current head) as reviewed today
    sync.py tried [WORD ...]  search the ledger of every candidate already measured
    sync.py tried --check     validate the ledger (exit 1 on a bad entry)

The clones live in <repo root>/.upstream/owner__repo, are gitignored and are untrusted
data: this script only runs git on them, never their code. State is upstream.json beside
this script (committed). Python 3 standard library only; run with python3 -I.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEPTH = 50
TRIED = HERE / "tried.json"
TRIED_FIELDS = ("id", "date", "source", "kind", "target", "what", "outcome", "measured", "result",
                "reason", "retry_if")
OUTCOMES = ("shipped", "rejected", "deferred", "measured", "not-measurable")
DEEPEN_STEP = 200
DEEPEN_TRIES = 5
TIMEOUT = 300  # seconds per git call


class GitError(Exception):
    pass


def git(cwd, *args, check=True):
    # Never wait on a credential prompt (a deleted or private repo asks for one) or a hung
    # network: the repo is reported as failed and the run goes on.
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
    try:
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        raise GitError([f"git {args[0]} timed out after {TIMEOUT}s"])
    except FileNotFoundError:
        raise GitError(["git not found on PATH"])
    if check and r.returncode != 0:
        raise GitError((r.stderr or r.stdout).strip().splitlines()[-1:] or ["git failed"])
    return r


def toplevel():
    r = git(HERE, "rev-parse", "--show-toplevel", check=False)
    return Path(r.stdout.strip()) if r.returncode == 0 else HERE.parents[2]


def load_state(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_state(path, state):
    Path(path).write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")


def clone_dir(root, repo):
    return Path(root) / repo.replace("/", "__")


def url_of(entry):
    return entry.get("url") or f"https://github.com/{entry['repo']}.git"


def find(state, repo):
    for entry in state["repos"]:
        if entry["repo"] == repo:
            return entry
    sys.exit(f"unknown repo: {repo} (not in upstream.json)")


def head(path):
    return git(path, "rev-parse", "HEAD").stdout.strip()


def reachable(path, sha):
    """True if sha is in the clone's history, deepening a shallow clone to find it."""
    if not sha:
        return False
    for _ in range(DEEPEN_TRIES + 1):
        if git(path, "merge-base", "--is-ancestor", sha, "HEAD", check=False).returncode == 0:
            return True
        if git(path, "rev-parse", "--is-shallow-repository").stdout.strip() != "true":
            return False
        git(path, "fetch", "-q", "--no-tags", f"--deepen={DEEPEN_STEP}", "origin", check=False)
    return False


def default_branch(path):
    """The remote's current default branch, asked of the remote itself, so a renamed
    default branch (master -> main) is followed; a shallow clone only tracks the old one."""
    out = git(path, "ls-remote", "--symref", "origin", "HEAD").stdout
    for line in out.splitlines():
        if line.startswith("ref: refs/heads/") and line.endswith("\tHEAD"):
            return line[len("ref: refs/heads/"):-len("\tHEAD")]
    raise GitError(["remote reports no default branch"])


def short(sha):
    return sha[:7] if sha else "never"


def cmd_update(state, root):
    root.mkdir(parents=True, exist_ok=True)
    failed = 0
    for entry in state["repos"]:
        repo, path = entry["repo"], clone_dir(root, entry["repo"])
        try:
            if not (path / ".git").exists():
                git(root, "clone", "-q", f"--depth={DEPTH}", "--no-tags", url_of(entry), str(path))
                what = "cloned"
            else:
                git(path, "remote", "set-url", "origin", url_of(entry))
                branch = default_branch(path)
                git(path, "fetch", "-q", "--no-tags", f"--depth={DEPTH}", "origin",
                    f"+refs/heads/{branch}:refs/remotes/origin/{branch}")
                git(path, "reset", "-q", "--hard", f"origin/{branch}")
                git(path, "clean", "-q", "-fdx")
                what = "updated"
            print(f"{repo}: head {short(head(path))} ({what})")
        except GitError as e:
            failed += 1
            print(f"{repo}: failed: {e.args[0][0] if e.args[0] else 'git error'}")
    return 1 if failed else 0


def cmd_status(state, root, tried=TRIED):
    for entry in state["repos"]:
        repo, path, reviewed = entry["repo"], clone_dir(root, entry["repo"]), entry.get("reviewed")
        if not (path / ".git").exists():
            print(f"{repo}: not cloned (run update)")
            continue
        now = head(path)
        line = f"{repo} [{entry.get('weight', '?')}]: head {short(now)}, reviewed {short(reviewed)}"
        if reviewed == now:
            print(f"{line}, unchanged")
        elif not reachable(path, reviewed):
            note = "never reviewed" if not reviewed else "reviewed commit not reachable"
            print(f"{line}, {note}: read the whole tree")
        else:
            commits = git(path, "rev-list", "--count", f"{reviewed}..HEAD").stdout.strip()
            files = git(path, "diff", "--name-only", reviewed, "HEAD").stdout.split()
            print(f"{line}, {commits} new commits, {len(files)} files changed")
    print(f"deferred candidates: {len(state.get('deferred', []))}")
    entries = load_tried(tried)
    counts = {}
    for t in entries:
        counts[t.get("outcome")] = counts.get(t.get("outcome"), 0) + 1
    print(f"tried ledger: {len(entries)} entries ("
          + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())) + "); search it: sync.py tried WORD")
    return 0


def load_tried(path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("tried", [])


def cmd_tried(words, check, path=TRIED):
    entries = load_tried(path)
    if check:
        bad, seen = 0, set()
        for i, t in enumerate(entries):
            missing = [f for f in TRIED_FIELDS if not str(t.get(f, "")).strip()]
            problems = missing and [f"missing {', '.join(missing)}"] or []
            if t.get("outcome") not in OUTCOMES:
                problems.append(f"outcome must be one of {', '.join(OUTCOMES)}")
            if t.get("id") in seen:
                problems.append("duplicate id")
            seen.add(t.get("id"))
            for msg in problems:
                bad += 1
                print(f"entry {i} ({t.get('id', '?')}): {msg}")
        print(f"{len(entries)} entries, {bad} problems")
        return 1 if bad else 0
    words = [w.lower() for w in words]
    hits = [t for t in entries if all(w in " ".join(str(v) for v in t.values()).lower() for w in words)]
    for t in hits:
        print(f"{t['id']} [{t['outcome']}, {t['date']}] {t['kind']} -> {t['target']}: {t['what']}")
        print(f"    source: {t['source']}")
        print(f"    result: {t['result']}")
        print(f"    reason: {t['reason']}; retry only if: {t['retry_if']}")
    print(f"{len(hits)} of {len(entries)} entries match")
    return 0


def cmd_diff(state, root, repo):
    entry = find(state, repo)
    path = clone_dir(root, repo)
    if not (path / ".git").exists():
        sys.exit(f"{repo} is not cloned; run update first")
    reviewed = entry.get("reviewed")
    if reachable(path, reviewed):
        out = root / f"{path.name}.diff"
        log = git(path, "log", "--stat", "--format=commit %H%n%s%n", f"{reviewed}..HEAD").stdout
        diff = git(path, "diff", reviewed, "HEAD").stdout
        out.write_text(log + "\n" + diff, encoding="utf-8")
    else:
        if reviewed:
            print(f"{repo}: reviewed commit {short(reviewed)} not reachable; listing the whole tree")
        out = root / f"{path.name}.tree"
        out.write_text(git(path, "ls-files").stdout, encoding="utf-8")
    print(out)
    return 0


def cmd_mark(state, root, state_path, repo, sha):
    entry = find(state, repo)
    if not sha:
        path = clone_dir(root, repo)
        if not (path / ".git").exists():
            sys.exit(f"{repo} is not cloned; run update first or pass a SHA")
        sha = head(path)
    entry["reviewed"] = sha
    entry["reviewed_on"] = datetime.date.today().isoformat()
    save_state(state_path, state)
    print(f"{repo}: reviewed {short(sha)}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--state", type=Path, default=HERE / "upstream.json")
    p.add_argument("--dir", type=Path, default=None, help="clones (default <root>/.upstream)")
    p.add_argument("--tried", type=Path, default=TRIED, help="ledger (default tried.json beside this script)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("update")
    sub.add_parser("status")
    sub.add_parser("diff").add_argument("repo")
    m = sub.add_parser("mark")
    m.add_argument("repo")
    m.add_argument("sha", nargs="?")
    t = sub.add_parser("tried")
    t.add_argument("words", nargs="*")
    t.add_argument("--check", action="store_true")
    a = p.parse_args(argv)
    if a.cmd == "tried":
        return cmd_tried(a.words, a.check, a.tried)
    root = (a.dir or toplevel() / ".upstream").resolve()
    state = load_state(a.state)
    if a.cmd == "update":
        return cmd_update(state, root)
    if a.cmd == "status":
        return cmd_status(state, root, a.tried)
    if a.cmd == "diff":
        return cmd_diff(state, root, a.repo)
    return cmd_mark(state, root, a.state, a.repo, a.sha)


if __name__ == "__main__":
    sys.exit(main())

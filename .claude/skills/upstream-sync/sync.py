#!/usr/bin/env python3
"""Keep local clones of quirón's reference repos current and say what changed.

    sync.py update            clone missing repos, move the rest to their default branch tip
    sync.py status            per repo: head, last reviewed commit, what is new since then
    sync.py diff OWNER/REPO   write what changed since the last review to a file, print its path
    sync.py mark OWNER/REPO [SHA]   record SHA (default: current head) as reviewed today

The clones live in <repo root>/.upstream/owner__repo, are gitignored and are untrusted
data: this script only runs git on them, never their code. State is upstream.json beside
this script (committed). Python 3 standard library only; run with python3 -I.
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEPTH = 50
DEEPEN_STEP = 200
DEEPEN_TRIES = 5


class GitError(Exception):
    pass


def git(cwd, *args, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
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
                git(path, "remote", "set-head", "origin", "-a")
                branch = git(path, "rev-parse", "--abbrev-ref", "origin/HEAD").stdout.strip()
                branch = branch.split("/", 1)[1]
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


def cmd_status(state, root):
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
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("update")
    sub.add_parser("status")
    sub.add_parser("diff").add_argument("repo")
    m = sub.add_parser("mark")
    m.add_argument("repo")
    m.add_argument("sha", nargs="?")
    a = p.parse_args(argv)
    root = (a.dir or toplevel() / ".upstream").resolve()
    state = load_state(a.state)
    if a.cmd == "update":
        return cmd_update(state, root)
    if a.cmd == "status":
        return cmd_status(state, root)
    if a.cmd == "diff":
        return cmd_diff(state, root, a.repo)
    return cmd_mark(state, root, a.state, a.repo, a.sha)


if __name__ == "__main__":
    sys.exit(main())

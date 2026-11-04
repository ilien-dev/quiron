"""Tests for sync.py. Run: python3 -I .claude/skills/upstream-sync/test_sync.py"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYNC = HERE / "sync.py"


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


class Upstream:
    """A local bare repo standing in for a GitHub remote, plus a worktree to commit from."""

    def __init__(self, root, name, branch="main"):
        self.bare = root / f"{name}.git"
        self.work = root / f"{name}-work"
        git(root, "init", "-q", "--bare", f"--initial-branch={branch}", str(self.bare))
        git(root, "init", "-q", f"--initial-branch={branch}", str(self.work))
        git(self.work, "config", "user.email", "t@t")
        git(self.work, "config", "user.name", "t")
        git(self.work, "remote", "add", "origin", str(self.bare))
        self.branch = branch

    def commit(self, filename, text):
        (self.work / filename).write_text(text, encoding="utf-8")
        git(self.work, "add", filename)
        git(self.work, "commit", "-q", "-m", f"edit {filename}")
        git(self.work, "push", "-q", "origin", self.branch)
        return git(self.work, "rev-parse", "HEAD")

    @property
    def url(self):
        return self.bare.as_uri()


class SyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.clones = self.root / "clones"
        self.state = self.root / "upstream.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write_state(self, repos):
        self.state.write_text(json.dumps({"repos": repos, "deferred": []}), encoding="utf-8")

    def entry(self, name, upstream, reviewed=None):
        return {"repo": f"o/{name}", "url": upstream.url, "weight": "proven",
                "reviewed": reviewed, "reviewed_on": None}

    def run_sync(self, *args):
        return subprocess.run(
            [sys.executable, "-I", str(SYNC), "--state", str(self.state),
             "--dir", str(self.clones), *args],
            capture_output=True, text=True, encoding="utf-8")

    def load(self):
        return json.loads(self.state.read_text(encoding="utf-8"))

    def test_update_clones_then_updates(self):
        up = Upstream(self.root, "a")
        first = up.commit("x.md", "one")
        self.write_state([self.entry("a", up)])
        r = self.run_sync("update")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("cloned", r.stdout)
        self.assertEqual(git(self.clones / "o__a", "rev-parse", "HEAD"), first)
        second = up.commit("x.md", "two")
        r = self.run_sync("update")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("updated", r.stdout)
        self.assertEqual(git(self.clones / "o__a", "rev-parse", "HEAD"), second)

    def test_update_follows_default_branch(self):
        up = Upstream(self.root, "m", branch="master")
        head = up.commit("x.md", "one")
        self.write_state([self.entry("m", up)])
        r = self.run_sync("update")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(git(self.clones / "o__m", "rev-parse", "HEAD"), head)

    def test_update_failure_continues(self):
        good = Upstream(self.root, "g")
        head = good.commit("x.md", "one")
        bad = {"repo": "o/bad", "url": (self.root / "missing.git").as_uri(),
               "weight": "popular", "reviewed": None, "reviewed_on": None}
        self.write_state([bad, self.entry("g", good)])
        r = self.run_sync("update")
        self.assertEqual(r.returncode, 1)
        self.assertIn("o/bad: failed", r.stdout)
        self.assertEqual(git(self.clones / "o__g", "rev-parse", "HEAD"), head)

    def test_status_unchanged_and_new(self):
        up = Upstream(self.root, "s")
        up.commit("x.md", "one")
        self.write_state([self.entry("s", up)])
        self.run_sync("update")
        self.assertEqual(self.run_sync("mark", "o/s").returncode, 0)
        self.assertIn("unchanged", self.run_sync("status").stdout)
        up.commit("y.md", "two")
        self.run_sync("update")
        out = self.run_sync("status").stdout
        self.assertIn("1 new commits", out)
        self.assertIn("1 files changed", out)

    def test_diff_since_reviewed(self):
        up = Upstream(self.root, "d")
        reviewed = up.commit("old.md", "one")
        up.commit("new.md", "two")
        self.write_state([self.entry("d", up, reviewed)])
        self.run_sync("update")
        r = self.run_sync("diff", "o/d")
        self.assertEqual(r.returncode, 0, r.stderr)
        path = Path(r.stdout.strip().splitlines()[-1])
        text = path.read_text(encoding="utf-8")
        self.assertIn("new.md", text)
        self.assertNotIn("old.md", text)

    def test_diff_never_reviewed_lists_tree(self):
        up = Upstream(self.root, "t")
        up.commit("a.md", "one")
        up.commit("b.md", "two")
        self.write_state([self.entry("t", up)])
        self.run_sync("update")
        r = self.run_sync("diff", "o/t")
        self.assertEqual(r.returncode, 0, r.stderr)
        path = Path(r.stdout.strip().splitlines()[-1])
        self.assertTrue(path.name.endswith(".tree"))
        text = path.read_text(encoding="utf-8")
        self.assertIn("a.md", text)
        self.assertIn("b.md", text)

    def test_diff_unreachable_sha_falls_back(self):
        up = Upstream(self.root, "u")
        up.commit("a.md", "one")
        self.write_state([self.entry("u", up, "0" * 40)])
        self.run_sync("update")
        r = self.run_sync("diff", "o/u")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("not reachable", r.stdout)
        self.assertTrue(r.stdout.strip().splitlines()[-1].endswith(".tree"))

    def test_mark_writes_state(self):
        up = Upstream(self.root, "k")
        head = up.commit("a.md", "one")
        self.write_state([self.entry("k", up)])
        self.run_sync("update")
        r = self.run_sync("mark", "o/k")
        self.assertEqual(r.returncode, 0, r.stderr)
        repo = self.load()["repos"][0]
        self.assertEqual(repo["reviewed"], head)
        self.assertRegex(repo["reviewed_on"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.load()["deferred"], [])

    def test_unknown_repo_errors_without_write(self):
        up = Upstream(self.root, "z")
        up.commit("a.md", "one")
        self.write_state([self.entry("z", up)])
        before = self.state.read_bytes()
        for cmd in (("mark", "o/nope"), ("diff", "o/nope")):
            r = self.run_sync(*cmd)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("unknown repo", r.stderr)
        self.assertEqual(self.state.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()

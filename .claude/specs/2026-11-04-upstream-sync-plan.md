# Upstream Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A `/upstream-sync` project skill that keeps local clones of eight reference repos current and drives a weekly, measured intake into quirón.

**Architecture:** `sync.py` (stdlib + `git` subprocess) owns clones under `.upstream/` and the committed state file `upstream.json`; `SKILL.md` holds the weekly procedure that the model follows. Nothing ships with the published skill.

**Tech Stack:** Python 3 standard library (`unittest`, `subprocess`, `json`), git.

**Spec:** `.claude/specs/2026-11-04-upstream-sync-design.md`

## Global Constraints

- Python 3 standard library only; run as `python3 -I`.
- Clones are untrusted data: never execute or install anything from `.upstream/`.
- `.upstream/` is gitignored; clone dir name is `owner__repo`.
- `CLAUDE.md` budget: 1000 tokens (chars / 3.5), enforced by `.claude/hooks/claude-md-budget.py`; edit it through the `themis:themis` skill.
- Branch `feature/upstream-sync`; PR against `main`.

## Review Focus

- A repo whose default branch is not `main` (e.g. `master`): `update` must follow `origin/HEAD`, not a hard-coded name.
- `reviewed` SHA outside the shallow history: `diff` must deepen, and if the SHA is gone report it and fall back to a full-tree listing instead of crashing.
- No network / a repo deleted upstream: `update` reports that repo as failed and continues with the rest; exit code non-zero.
- `upstream.json` edited by hand with an unknown repo name passed to `diff`/`mark`: clear error, no write.
- Running from a subdirectory: paths resolve from the repo root (`git rev-parse --show-toplevel`), not cwd.

---

### Task 1: `sync.py` and its state file

**Files:**
- Create: `.claude/skills/upstream-sync/sync.py`
- Create: `.claude/skills/upstream-sync/upstream.json` (8 repos from the spec table, `reviewed: null`, `reviewed_on: null`, `deferred: []`)
- Create: `.claude/skills/upstream-sync/test_sync.py`
- Modify: `.gitignore` (add `.upstream/`)

**Interfaces (produces):**
- CLI: `sync.py update | status | diff REPO | mark REPO [SHA]`, global `--state PATH` and `--dir PATH` (defaults: `upstream.json` beside the script, `<toplevel>/.upstream`). `REPO` is `owner/repo`. Remote URL `https://github.com/{repo}.git`, overridable per entry by an optional `"url"` key (tests use local bare repos).
- `load_state(path) -> dict`, `save_state(path, state) -> None` (2-space JSON, trailing newline, key order kept).
- `clone_dir(root, repo) -> Path`.
- `update` prints one line per repo `repo: head <sha7> (cloned|updated|failed: reason)`; exit 1 if any failed.
- `status` prints `repo: head <sha7>, reviewed <sha7|never>, N new commits, M files changed` or `unchanged`, and the count of `deferred`.
- `diff` writes `.upstream/<owner__repo>.diff` (or `.tree` listing when `reviewed` is null or unreachable, with a printed note) and prints the path.
- `mark` sets `reviewed` (default current head) and `reviewed_on` (today ISO).

- [ ] **Step 1: Write failing tests** in `test_sync.py` (`unittest`, temp dirs, a local bare repo as upstream with `url` override):
  - `test_update_clones_then_updates`: first run clones, second after a new upstream commit moves head to it.
  - `test_update_follows_default_branch`: upstream default `master` works.
  - `test_update_failure_continues`: one bad url, one good → good updated, exit code 1.
  - `test_status_unchanged_and_new`: after `mark`, status says `unchanged`; after one upstream commit, `1 new commits`.
  - `test_diff_since_reviewed`: diff file contains the changed file name only from commits after `reviewed`.
  - `test_diff_never_reviewed_lists_tree` and `test_diff_unreachable_sha_falls_back`.
  - `test_mark_writes_state` and `test_unknown_repo_errors_without_write`.
- [ ] **Step 2:** `python3 -I .claude/skills/upstream-sync/test_sync.py` → failures (module missing).
- [ ] **Step 3:** Implement `sync.py`. Clone with `--depth 50 --no-tags`; update = `fetch --depth 50` + `remote set-head origin -a` + `reset --hard origin/HEAD` + `clean -fdx`. Before diffing, `fetch --deepen 200` up to 5 times until `reviewed` is reachable (`cat-file -e`).
- [ ] **Step 4:** Tests pass.
- [ ] **Step 5:** Real run: `python3 -I .claude/skills/upstream-sync/sync.py update` then `status` → all 8 cloned; `git status` shows `.upstream/` ignored.
- [ ] **Step 6:** Commit.

### Task 2: the skill and the CLAUDE.md pointer

**Files:**
- Create: `.claude/skills/upstream-sync/SKILL.md` (frontmatter `name: upstream-sync`, `description`, `disable-model-invocation: true`; body = the spec's weekly procedure steps 1–8, the improvement bar, the copy rule, the register rule, the `deferred` handling, the commands of Task 1)
- Modify: `CLAUDE.md` (via `themis:themis`): one line saying `.upstream/` holds reference clones, never committed or shipped, and the weekly intake is `/upstream-sync`; stay under the 1000-token budget.

- [ ] **Step 1:** Write `SKILL.md`; under 500 lines; English (model instructions).
- [ ] **Step 2:** Load `themis:themis`, add the line, run `python3 .claude/hooks/claude-md-budget.py < /dev/null` → exit 0.
- [ ] **Step 3:** Check the skill is listed: `claude` slash menu shows `/upstream-sync` (or the file parses: frontmatter is valid YAML).
- [ ] **Step 4:** Commit; push; open PR against `main` (PR description through `scripts/check.sh`).

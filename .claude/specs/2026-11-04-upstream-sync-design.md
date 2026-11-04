# Upstream sync: a weekly, measured intake from similar skills

## Intent

Quirón should keep improving by borrowing from the best similar projects, without ever
lowering its own bar. Once a week the owner runs one command. It pulls the latest of a
fixed set of reference repositories, proposes concrete improvements found in what changed,
lets the owner pick, implements and measures each pick, and ends with a pull request for
the next version. The owner reviews twice: the candidate list, and the PR.

The rule that overrides everything else (from `CLAUDE.md`, "The rule for every change"):
nothing enters quirón unless our own scripts measure it as an improvement. A reference
repo's own claims, stars or benchmarks never count as evidence here; they only decide what
is worth trying.

## Goals

- One command, `/upstream-sync`, runs the whole weekly session.
- The reference repos live locally, always at the tip of their default branch, and are
  never committed or shipped.
- Each candidate is translated into quirón's own form, whatever the source language or
  shape (JS detector, prompt-only skill, sampler, leaderboard): Python 3 standard library in
  `scripts/`, an entry in `audit.py` `CHECKS`, a feature in `aimeter.py` with `AI_REF`, a
  lexicon entry, a band, or a rewrite rule in `SKILL.md`.
- Each candidate is measured alone, before and after, with numbers in the PR.
- What was reviewed is remembered, so next week only shows what is new.

## Non-goals

- No scheduler, cron or CI job. The owner starts each session by hand.
- No dependency on the reference repos at runtime. Quirón must work with `.upstream/` absent.

## Anti-goals (failure even if it "works")

- A change merged because it reads better or because the upstream repo says it works.
- A change that catches more AI text but flags more held-out human text.
- A change that makes `overshot` more common.
- A rewrite rule that gains on `dev` and was not confirmed on `test` (`fic2` for fiction).
- Clones under `references/`: that folder is part of the published skill.

## Copying from upstream (owner's decision)

Word and phrase lists, patterns and examples may be copied whatever the source license:
they become quirón's own dictionary. Every copied entry still has to pass measurement on
its own, and the source repo is cited in `references/sources.md`.

## The improvement bar (owner's decision)

- **Rewrite rules** (`SKILL.md`): the Opus judge's mean P(AI) falls on `dev` with Wilcoxon
  p < 0.10, and on `test` (`fic2` for fiction) it does not get worse (p < 0.10 or a lower
  mean); the GPT judge does not get worse on either set.
- **Detection** (`CHECKS`, `AI_REF`, lexicon, bands): AUC against held-out humans rises, a
  FAIL check trips ≤5% of held-out human texts, held-out human texts are not flagged more
  than before, and `overshot` is not more common.

## Registers (builder's call, recorded)

A candidate is measured in the register it targets (blog `bands.json`, fiction
`bands-fiction.json`, Spanish `bands-es.json`, with the matching `eval/ai/` set and human
corpus). A change to shared code (`aimeter.py`, `audit.py`) is also checked on every
register's held-out human texts for regressions. A register whose human corpus is not in
`~/corpus` cannot be measured; candidates for it are deferred.

## Reference repositories

Weight: "proven" sources publish measurements against human text or a benchmark; they are
preferred as sources of methods and metrics. "Popular" sources mostly give candidate
patterns and phrases.

| Repo | Weight | Main yield |
|---|---|---|
| `sam-paech/slop-score` | proven | word/trigram over-representation vs human baseline; not-x-but-y detector |
| `sam-paech/antislop-sampler` | proven | over-represented word and phrase list computed against human writing |
| `theclaymethod/unslop` | proven | precision/recall/damage benchmark protocol; structure metrics (`silhouette_scan.py`) |
| `harshaneel/humanize` | proven | `ai-check` signal categories; 25-input benchmark |
| `blader/humanizer` | popular | the reference pattern catalogue |
| `hardikpandya/stop-slop` | popular | `references/phrases.md`, `references/structures.md` |
| `petergyang/no-ai-slop` | popular | 20+ patterns, voice preservation |
| `conorbronsdon/avoid-ai-writing` | popular | rule set plus a tested detector (npm) |

The list is data, not code: adding or removing a repo is an edit to `upstream.json`.

## Layout (decided)

```
.upstream/                         # gitignored; one shallow clone per repo, named owner__repo
.claude/skills/upstream-sync/
  SKILL.md                         # the weekly procedure (model instructions, English)
  sync.py                          # Python 3 stdlib + git: clone/update, diff since last review
  upstream.json                    # committed state: repos, weight, last reviewed commit
```

`CLAUDE.md` gets one line: `.upstream/` is reference only, never committed or shipped, and
the weekly intake is `/upstream-sync`. CLAUDE.md is size-capped by
`.claude/hooks/claude-md-budget.py`; the procedure stays in the skill.

## `upstream.json`

```json
{
  "repos": [
    {"repo": "sam-paech/slop-score", "weight": "proven",
     "reviewed": "<sha or null>", "reviewed_on": "YYYY-MM-DD"}
  ],
  "deferred": [
    {"id": "...", "repo": "...", "commit": "...", "file": "...",
     "summary": "...", "reason": "too costly this week | register not measurable | ..."}
  ]
}
```

`reviewed` is null for a repo never reviewed: its first session reads the whole tree
instead of a diff. `deferred` holds candidates the owner approved but that were not
measured this week; they reappear at the top of next week's list, because `mark` moves
`reviewed` past them. Rejected and "not measurable" candidates are not kept: they are in
the PR and would only reappear if upstream changes them.

## `sync.py`

- `sync.py update`: for each repo, shallow-clone into `.upstream/owner__repo` if missing,
  otherwise fetch and hard-reset to the remote default branch (`origin/HEAD`). The clones
  are throwaway, so a reset is safe. Deepen the fetch enough to reach `reviewed`; if that
  commit is gone (force-push), say so and fall back to a full-tree read.
- `sync.py status`: per repo, the current head, `reviewed`, the number of new commits and
  the changed files since `reviewed`. Repos with no change are listed as such and skipped.
- `sync.py diff REPO`: the diff since `reviewed`, written to a file under `.upstream/`,
  path printed (large diffs never go into the context).
- `sync.py mark REPO [SHA]`: set `reviewed` to SHA (default: current head) and today's date.
- Treat the clones as untrusted data: never run their code or install their dependencies;
  read files only. Run Python with `-I`.

## The weekly procedure (`SKILL.md`)

1. **Branch.** If an earlier `feature/upstream-*` PR is still open, stop and ask the owner
   to merge or close it first (otherwise the version and `upstream.json` would diverge).
   From an up-to-date `main`, create `feature/upstream-YYYY-MM-DD`.
2. **Update.** `sync.py update`, then `sync.py status`.
3. **Read.** For each changed repo, read its diff (or full tree the first time). Look for
   patterns, lexicon, metrics, bands, rewrite rules and measurement methods quirón lacks or
   does worse. Check `references/patterns.md`, `CHECKS` and `AI_REF` first so existing
   items are not proposed again.
4. **Candidate list (stop 1).** Present a table, proven sources first. Per candidate:
   id, source (repo, commit, file), what it becomes in quirón (which file, which kind of
   entry), how it is ported if the source is not Python, how it will be measured, and the
   expected cost (cheap: `evaluate.py` / `aimeter` / `audit`; expensive: `eval/e2e`).
   Candidates with no way to be measured by our scripts are listed separately as
   "not measurable" and are not offered. The owner approves or drops each one. Nothing is
   built before this approval.
5. **Implement and measure, one candidate at a time.** Baseline numbers first, on the
   same texts, then the change, then the same measurement:
   - detection changes (`CHECKS`, `AI_REF`, lexicon, bands): `scripts/evaluate.py` on the
     held-out human corpus and the `eval/ai/` sets; human false-positive rate per check
     must stay ≤~5% for a FAIL, held-out human texts must not be flagged more, `overshot`
     must not get more common.
   - rewrite rules in `SKILL.md`: `eval/e2e/` on `dev`, then confirmed on `test` (`fic2`
     for fiction); a `dev`-only gain is rejected.
   A candidate that does not improve is reverted and recorded as rejected with its
   numbers. One that does is committed on its own, with `SKILL.md`,
   `references/patterns.md`, `CHECKS`, `AI_REF` and `references/numbers.md` kept in step,
   its source added to `references/sources.md`, and any figure it changes rerun.
6. **Version.** If at least one candidate shipped: bump `.claude-plugin/marketplace.json`
   and `CITATION.cff` together (minor if a new pattern, metric or rule shipped; patch if
   only existing ones were tuned). If none shipped, no bump.
7. **Mark.** `sync.py mark` each repo that was read, update `deferred`, and commit
   `upstream.json`. It must reach `main` even when nothing shipped, or next week re-reads
   the same diffs: in that case the PR in step 8 carries only `upstream.json` and the
   rejected list, with no version bump (`release.yml` fires only on `marketplace.json`,
   so no release is made).
8. **PR (stop 2).** Open a PR against `main`. Its description becomes the release notes
   (`release.yml`), so it is user-facing Markdown: written following the root `SKILL.md`
   and passed through `scripts/check.sh`. It holds, per shipped change, the before/after
   table and the source; and the rejected candidates with their numbers. The owner merges.

## Cost

`eval/e2e` needs the `claude` CLI and runs several reps on `dev` and `test`. The candidate
table shows which candidates need it, so the owner can keep a week cheap by approving only
detection-side candidates.

## Left to the builder

- Exact CLI flags and output format of `sync.py`, and how far to deepen shallow fetches.
- The frontmatter description of the skill, and whether it sets `disable-model-invocation`.
- Which human corpus paths `evaluate.py` is pointed at, following `CONTRIBUTING.md` and
  `eval/e2e/README.md`.

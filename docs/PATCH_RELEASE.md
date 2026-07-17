# Patch-Day Release Procedure

When a new STS2 patch ships, the only data change needed is a **one- or two-line
append to `backend/patch_taxonomy.py`**. The frontend patch filter is fully
data-driven off `GET /api/analytics/distinct-versions`, so it needs no code
changes — it picks up the new version automatically once the backend deploys.

This procedure is a **deliberate exception** to the normal
qa-first-then-promote workflow (`.claude/CLAUDE.md`): production cannot wait for
unrelated QA work to finish before it sees a new patch. Because the change is a
single trivial data line guarded by a gate test, it goes to **both `qa` and
`main` directly** on patch day.

> This exception applies **only** to a patch-day append to
> `patch_taxonomy.py`. Any other change — code, schema, multi-line, or touching
> other files — follows the normal branch → QA → user-tested → promote flow.

---

## The workflow (agent-driven)

An agent is notified of a release and runs these steps. The human makes the
actual taxonomy edit; the agent prepares the branch, gates on the test, and
performs the git operations.

### 1. Prepare a branch off `qa`

```bash
git switch qa && git pull --ff-only origin qa      # integrate others' work first
git worktree add ../wt-patch-release -b feat/patch-release qa
```

(If a `feat/patch-release` branch/worktree already exists from a prior patch
day, remove it first — see Cleanup — so you start from current `qa`.)

### 2. Hand off to the human for the edit

Before the human edits anything, the agent **reminds them to switch to the
worktree** and gives them the exact command. The taxonomy must be edited in the
worktree, **not** the shared `qa` tree — an edit in the wrong tree either gets
committed under the wrong branch or swept into another agent's work.

```bash
cd ../wt-patch-release      # edit backend/patch_taxonomy.py HERE, not in the qa tree
```

The agent then **waits** for the human to edit `backend/patch_taxonomy.py`. The
human signals completion by saying **"done"**. The agent does not poll or guess.

**How to edit the taxonomy** (full rules live in the file's own docstring):

- Append to the **end** of `PATCHES` (oldest-first, so newest goes at the
  bottom).
- A **beta-branch** release is a standalone 2-tuple: `("v0.109.0", "Beta Patch")`.
- A **main-branch** release that brought main in line with beta is a 3-tuple
  whose third element lists the beta versions it incorporated:
  ```python
  ("v0.109.1", "Patch", ["v0.109.0", "v0.108.0"]),
  ```
  Every version named in that children list must **also** keep its own
  top-level row (the test enforces this).
- The `tag` is decorative (UI label only). Nothing branches on its text.

### 3. Run the gate test

```bash
python3 backend/test_patch_taxonomy.py
```

It must print all checks passing and exit `0`. It fails (non-zero exit) on a
malformed tuple, a duplicate top-level version, a child that names a
nonexistent version, or a tree that won't build. **Do not proceed on a
failure** — report the message (it names the offending entry) and wait for a
corrected edit.

### 4. Commit on the feature branch

Stage **only** `patch_taxonomy.py` (and, the first time this procedure lands,
the test + this doc). Never `git add -A` — other agents' files may be in the
tree.

```bash
git add backend/patch_taxonomy.py
git commit -m "Add <version> to patch taxonomy"
```

### 5. Push to `qa`

```bash
git switch qa && git pull --ff-only origin qa
git merge --squash feat/patch-release
git commit -m "Add <version> to patch taxonomy"
python3 backend/test_patch_taxonomy.py        # gate again on the integrated tree
git push origin qa
```

### 6. Cherry-pick the same commit to `main`

The identical one-line change goes to production. Use cherry-pick so both
branches carry the **same** canonical change rather than two hand-authored
commits that could drift.

> **Ask the human for a one-word go-ahead before pushing `main`.** The
> patch-day exception authorizes this push, but project rules require a prompt
> before any `main` operation. Confirm, then push.

```bash
git switch main && git pull --ff-only origin main
git cherry-pick qa                            # the squash commit just made on qa
python3 backend/test_patch_taxonomy.py        # gate on main too
git push origin main                          # only after the go-ahead
git switch qa
```

### 7. Clear the cache

The patch tree is served through the 24h-TTL analytics cache. Remind the human
to clear it so the new version appears immediately instead of after expiry:

```bash
python3 backend/admin_cli.py --clear-cache
```

### 8. Clean up

```bash
git worktree remove ../wt-patch-release
git branch -d feat/patch-release
```

---

## Quick checklist

- [ ] Branch `feat/patch-release` off current `qa` (worktree).
- [ ] Human edits `patch_taxonomy.py`; signals **"done"**.
- [ ] `python3 backend/test_patch_taxonomy.py` passes.
- [ ] Squash-merge → `qa`, re-run test, push `qa`.
- [ ] Get go-ahead → cherry-pick to `main`, re-run test, push `main`.
- [ ] Remind human to clear the cache.
- [ ] Remove the worktree and branch.

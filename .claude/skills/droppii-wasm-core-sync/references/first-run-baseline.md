# First-Run Baseline (No State File Yet)

If `.core-sync-state.json` does not exist in the JS repo, this skill has never run against it before. Do not assume the JS repo is fully behind Core `dev` from the beginning of history — a prior manual sync already happened once.

## Known baseline (as of 2026-07-29 audit)

- JS `main` HEAD commit `1d5b50d` is functionally equivalent to Core `dev` PR#2 (`32c543ac`, `feat/add-new-type-log-message`) — this was the last point of effective sync, established by manually diffing JS's one prior manual sync commit (`5055d10`, "sync patch-10") against Core history.
- Core `dev` HEAD at that time was `902c93f1` (PR#42).
- Full audit of PR#3–#42 against this baseline is documented in `plans/260729-sync-js-wasm-with-core-dev/plan.md` in the JS repo, if that file is still present — treat it as already-decided prior work, not something to re-audit from scratch.

## What to do on a genuine first run

1. Check whether `plans/260729-sync-js-wasm-with-core-dev/plan.md` (or a similarly named prior audit) exists in the JS repo. If it does, treat its conclusions as already-settled: the 11 PRs it lists as "needs JS port" are the Step 3/4 output for the PR#3–#42 range — don't re-derive them, just carry them into Step 5 onward (port, if not already ported; otherwise mark as already-covered).
2. Confirm with the user whether those 11 PRs have already been manually ported since that plan was written (check JS git log for matching commits/messages) before assuming they're still outstanding.
3. Seed `.core-sync-state.json` with `lastSyncedCoreSha: "32c543ac"` (PR#2) only if none of the 11 PRs have been ported yet. If some have been manually ported already, seed with the actual highest Core PR SHA that's been covered, and record the rest as the remaining port backlog for this run.
4. From here on, every subsequent run reads the real state file — this baseline logic only applies once.

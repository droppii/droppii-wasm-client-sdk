# Audit Methodology: Classifying Core PRs for JS Port

## Goal

For every Core `dev` merge commit after the last-synced SHA, decide: does this PR change anything a JS consumer of `assets/openIM.wasm` can observe? If yes, port it. If no, skip it.

## Why not trust branch names

Branch names lie. Observed in the `droppii/openimsdk-core` history:
- `feat/add-avatar-group` — sounds JS-relevant, is actually Core-internal only, no `wasm/` diff.
- `feat/Func-createMergeMsg` — sounds like a Core-internal helper, actually changes the indexdb schema for `LocalConversation` (adds `MaxSeq`, `MinSeq`, `MsgDestructTime`, `IsMsgDestruct`) — JS-relevant.

Always read the diff. Never classify from the branch or PR title alone.

## Step-by-step

1. List candidate merge commits:
   ```bash
   git -C <core-path> log origin/dev --merges --first-parent --oneline <last-synced-sha>..origin/dev
   ```
2. For each merge commit `<sha>`, diff against its first parent, restricted to `wasm/`:
   ```bash
   git -C <core-path> diff <sha>^1 <sha> -- wasm/
   ```
   Empty output → no `wasm/` change → **no action needed**, skip to next commit.
3. If non-empty, read the full diff (not just `--stat`) for that path. Look specifically for:
   - New or changed `js.Global().Set("<name>", ...)` registrations — these are the actual JS-facing export surface.
   - New methods added to any `wasm_wrapper` package file (`wasm/wasm_wrapper/*.go`).
   - New fields added to structs that get `json.Marshal`'d back across the wasm boundary (check `sdk_struct.go` and any indexdb temp/local structs under `wasm/`).
   - Changes to `wasm/cmd/main.go` (this is where every export is registered — a new line here is a strong signal of a new JS-facing method).
4. Classify:
   - **Needs JS port** — any of the above changed in a way still present at Core `dev` HEAD (see net-effect check below).
   - **No action needed** — internal refactor, logic-only change with no new/changed export or struct field, or a schema-guard/bugfix that doesn't change the JS-facing signature.

## Net-effect check (reverts and superseding PRs)

A field or export can be added in one PR and reverted in a later one before you ever see it — don't act on an intermediate state. When multiple related PRs touch the same symbol, diff the **oldest pre-change commit against the current Core `dev` HEAD** for that specific file/symbol, not each PR in isolation:

```bash
git -C <core-path> diff <last-synced-sha> origin/dev -- wasm/path/to/file.go
```

If the net diff for that symbol is empty, mark all contributing PRs as "no action needed" with a note explaining the wash (e.g. "field added in PR#3, reverted in PR#8/#9 — net effect: no change").

## Worked example

See `plans/260729-sync-js-wasm-with-core-dev/plan.md` in the JS repo (if present) for a full worked audit table covering Core PR#3–#42, including:
- A 3-PR wash (`IsInternal` field added then reverted twice — net: no action).
- A PR classified as "needs verification only" rather than "port" (PR#17, changed the `wasm_exec.js` Go runtime shim itself, not a `wasm_wrapper` export — see note below).
- A PR whose branch name (`feat/Func-createMergeMsg`) didn't match its actual effect (indexdb schema fields, not merge-message logic).

## Special case: `wasm/cmd/static/wasm_exec.js` changes

If a Core PR changes the Go WASM runtime shim itself (e.g. renaming the import object from `go` to `gojs`, changing global API surface used by the shim), this is not a normal "port a method" task. Flag it separately: confirm whether the JS repo's `assets/wasm_exec.js` is hand-maintained or pulled from a Core build artifact. If hand-maintained, the shim needs manual review against the Go runtime change. If pulled from Core's build pipeline, no action is needed in this skill's scope — note it in the report and move on (this skill does not touch `assets/`).

## Output format expected by `scripts/audit_core_prs.py`

The script only automates step 1–2 (listing commits + wasm/ touch detection) — it cannot judge relevance itself. Its output is one row per candidate commit:
```
<sha>  PR#<n or ?>  <branch-name>  <changed-files-under-wasm/, comma-joined>
```
Read each listed commit's diff manually (step 3–4 above) before building the final audit table.

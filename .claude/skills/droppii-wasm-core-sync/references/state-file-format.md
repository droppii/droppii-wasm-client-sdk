# `.core-sync-state.json` Schema

Lives at the JS repo root. Tracks the last Core `dev` commit successfully synced into JS `main`, so each future run only needs to diff forward from here.

```json
{
  "lastSyncedCoreSha": "902c93f1",
  "lastSyncedCorePr": 42,
  "lastSyncedAt": "2026-07-29",
  "jsCommit": "1d5b50d",
  "portedPrs": [3, 5, 8, 9, 17, 19, 23, 27, 30, 31, 39]
}
```

Field meaning:
- `lastSyncedCoreSha` — Core `dev` commit SHA (short or long, be consistent) that this sync run brought the JS repo up to date with. This is the `--since` value for the next run.
- `lastSyncedCorePr` — highest Core PR number covered by this sync, for human readability.
- `lastSyncedAt` — ISO date (`YYYY-MM-DD`) of the sync run. Get via `date +%Y-%m-%d`, not model knowledge.
- `jsCommit` — JS repo commit SHA this state was written at (the version-bump commit from Step 10, once known).
- `portedPrs` — every Core PR number classified as "needs JS port" OR "no action needed" in this run (full audited range), so a future run doesn't need to re-audit already-decided PRs even if they show up again in a `--since` range overlap.

## Update procedure

After Step 9 (write state) in the main workflow:
1. Read existing `.core-sync-state.json` (or start from `{}` if this is the first sync run using this skill — see `references/first-run-baseline.md`).
2. Set `lastSyncedCoreSha`/`lastSyncedCorePr` to the Core `dev` HEAD fetched at the start of this run.
3. Append newly audited PR numbers (ported and skipped) to `portedPrs`, deduplicated.
4. Set `lastSyncedAt` to today.
5. Leave `jsCommit` for a follow-up amend once the version-bump commit SHA is known, or set it in the same commit that bumps the version (Step 10) since both files change together.

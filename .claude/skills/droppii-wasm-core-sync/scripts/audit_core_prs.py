#!/usr/bin/env python3
"""List Core merge commits since a given SHA that touch wasm/.

Does NOT decide relevance. It only surfaces candidate commits and the
wasm/-scoped file list; a human (or the calling skill workflow) still reads
each diff to classify it (see references/audit-methodology.md).

Usage:
    audit_core_prs.py <core-repo-path> --since <sha-or-tag> [--branch dev] [--json]
"""
import argparse
import json
import subprocess
import sys


def run_git(repo_path, args):
    result = subprocess.run(
        ["git", "-C", repo_path] + args,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def list_merge_commits(repo_path, since, branch):
    out = run_git(
        repo_path,
        [
            "log",
            f"origin/{branch}",
            "--merges",
            "--first-parent",
            "--pretty=format:%H%x09%s",
            f"{since}..origin/{branch}",
        ],
    )
    commits = []
    for line in out.splitlines():
        if not line.strip():
            continue
        sha, subject = line.split("\t", 1)
        commits.append({"sha": sha, "subject": subject})
    return commits


def wasm_touched_files(repo_path, sha):
    out = run_git(
        repo_path,
        ["diff", "--name-only", f"{sha}^1", sha, "--", "wasm/"],
    )
    files = [line for line in out.splitlines() if line.strip()]
    return files


def extract_branch_name(subject):
    # Merge commit subjects are typically "Merge pull request #N from org/branch-name"
    if " from " in subject:
        return subject.split(" from ", 1)[1].strip()
    return subject


def extract_pr_number(subject):
    if subject.startswith("Merge pull request #"):
        rest = subject[len("Merge pull request #"):]
        num = ""
        for ch in rest:
            if ch.isdigit():
                num += ch
            else:
                break
        return int(num) if num else None
    return None


def audit(repo_path, since, branch="dev"):
    commits = list_merge_commits(repo_path, since, branch)
    results = []
    for commit in commits:
        files = wasm_touched_files(repo_path, commit["sha"])
        if not files:
            continue
        results.append(
            {
                "sha": commit["sha"],
                "pr": extract_pr_number(commit["subject"]),
                "branch": extract_branch_name(commit["subject"]),
                "subject": commit["subject"],
                "wasm_files": files,
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_path", help="Path to local Core repo clone")
    parser.add_argument("--since", required=True, help="SHA or tag to diff forward from (exclusive)")
    parser.add_argument("--branch", default="dev", help="Core branch to audit (default: dev)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of table")
    args = parser.parse_args()

    try:
        results = audit(args.repo_path, args.since, args.branch)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    if not results:
        print(f"No wasm/-touching merge commits found after {args.since} on {args.branch}.")
        return

    print(f"{'SHA':<10} {'PR':<6} {'Branch':<50} {'wasm/ files changed'}")
    for r in results:
        sha_short = r["sha"][:9]
        pr = f"#{r['pr']}" if r["pr"] else "?"
        branch = r["branch"][:48]
        files = ", ".join(r["wasm_files"])
        print(f"{sha_short:<10} {pr:<6} {branch:<50} {files}")
    print(f"\n{len(results)} candidate commit(s). Read each diff before classifying — see references/audit-methodology.md.")


if __name__ == "__main__":
    main()

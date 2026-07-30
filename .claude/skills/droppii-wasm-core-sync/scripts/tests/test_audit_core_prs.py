"""Tests for audit_core_prs.py using a throwaway local git repo (no network)."""
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from audit_core_prs import audit, extract_branch_name, extract_pr_number  # noqa: E402


def git(repo, *args):
    subprocess.run(["git", "-C", repo] + list(args), check=True, capture_output=True)


def write(repo, relpath, content):
    full = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


class TestExtractHelpers(unittest.TestCase):
    def test_extract_pr_number(self):
        self.assertEqual(
            extract_pr_number("Merge pull request #19 from droppii/feat/button"), 19
        )
        self.assertIsNone(extract_pr_number("Some other commit"))

    def test_extract_branch_name(self):
        self.assertEqual(
            extract_branch_name("Merge pull request #19 from droppii/feat/button"),
            "droppii/feat/button",
        )
        self.assertEqual(extract_branch_name("plain commit subject"), "plain commit subject")


class TestAuditRepo(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.origin = os.path.join(self.tmpdir, "origin.git")
        self.work = os.path.join(self.tmpdir, "work")

        subprocess.run(["git", "init", "--bare", self.origin], check=True, capture_output=True)
        subprocess.run(["git", "clone", self.origin, self.work], check=True, capture_output=True)

        git(self.work, "config", "user.email", "test@example.com")
        git(self.work, "config", "user.name", "Test")

        write(self.work, "README.md", "root\n")
        git(self.work, "add", ".")
        git(self.work, "commit", "-m", "init")
        git(self.work, "branch", "-M", "dev")
        git(self.work, "push", "-u", "origin", "dev")

        self.baseline_sha = subprocess.run(
            ["git", "-C", self.work, "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

        # PR A: touches wasm/ -> should be a candidate
        git(self.work, "checkout", "-b", "feat/add-sticker")
        write(self.work, "wasm/wasm_wrapper/wasm_msg.go", "func CreateStickerMessage() {}\n")
        git(self.work, "add", ".")
        git(self.work, "commit", "-m", "add sticker wasm export")
        git(self.work, "checkout", "dev")
        git(self.work, "merge", "--no-ff", "-m", "Merge pull request #39 from droppii/feat/add-sticker", "feat/add-sticker")

        # PR B: internal only, no wasm/ touch -> should NOT be a candidate
        git(self.work, "checkout", "-b", "feat/internal-refactor")
        write(self.work, "internal/logic.go", "func internalOnly() {}\n")
        git(self.work, "add", ".")
        git(self.work, "commit", "-m", "internal refactor")
        git(self.work, "checkout", "dev")
        git(self.work, "merge", "--no-ff", "-m", "Merge pull request #40 from droppii/feat/internal-refactor", "feat/internal-refactor")

        git(self.work, "push", "origin", "dev")

    def test_audit_finds_only_wasm_touching_pr(self):
        results = audit(self.work, self.baseline_sha, branch="dev")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["pr"], 39)
        self.assertIn("wasm/wasm_wrapper/wasm_msg.go", results[0]["wasm_files"])

    def test_audit_empty_when_since_is_head(self):
        head = subprocess.run(
            ["git", "-C", self.work, "rev-parse", "origin/dev"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        results = audit(self.work, head, branch="dev")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Tests for scripts/get-diff.sh behavior.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestGetDiff(unittest.TestCase):

    def setUp(self):
        self.script = os.path.join(BASE_DIR, "scripts", "get-diff.sh")
        self.temp_repo = tempfile.mkdtemp()
        # Initialize test git repo
        subprocess.run(["git", "init"], cwd=self.temp_repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "TestUser"], cwd=self.temp_repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.temp_repo, check=True)

        # Initial commit
        test_file = os.path.join(self.temp_repo, "hello.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("line 1\n")
        subprocess.run(["git", "add", "."], cwd=self.temp_repo, check=True)
        subprocess.run(["git", "commit", "-m", "feat: init"], cwd=self.temp_repo, check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.temp_repo, ignore_errors=True)

    def test_outside_git_repo_fails(self):
        empty_dir = tempfile.mkdtemp()
        try:
            proc = subprocess.run([self.script], cwd=empty_dir, capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0, "Must fail when run outside git repo")
            self.assertIn("Error:", proc.stderr)
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)

    def test_uncommitted_working_changes_detected_by_default(self):
        test_file = os.path.join(self.temp_repo, "hello.txt")
        with open(test_file, "a", encoding="utf-8") as f:
            f.write("line 2 (working edit)\n")

        # Run get-diff.sh without arguments
        proc = subprocess.run([self.script], cwd=self.temp_repo, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("working edit", proc.stdout, "Default get-diff.sh must capture uncommitted working edits")

    def test_clean_working_tree_defaults_to_head_commit(self):
        test_file = os.path.join(self.temp_repo, "hello.txt")
        with open(test_file, "a", encoding="utf-8") as f:
            f.write("committed line 2\n")
        subprocess.run(["git", "add", "."], cwd=self.temp_repo, check=True)
        subprocess.run(["git", "commit", "-m", "feat: second"], cwd=self.temp_repo, check=True, capture_output=True)

        # Repo is clean: should show latest commit
        proc = subprocess.run([self.script], cwd=self.temp_repo, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("committed line 2", proc.stdout, "When clean, get-diff.sh should show HEAD commit diff")

    def test_explicit_revision_or_range(self):
        test_file = os.path.join(self.temp_repo, "hello.txt")
        with open(test_file, "a", encoding="utf-8") as f:
            f.write("second line\n")
        subprocess.run(["git", "add", "."], cwd=self.temp_repo, check=True)
        subprocess.run(["git", "commit", "-m", "feat: second"], cwd=self.temp_repo, check=True, capture_output=True)

        proc = subprocess.run([self.script, "HEAD~1..HEAD"], cwd=self.temp_repo, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("second line", proc.stdout)

    def test_invalid_revision_fails(self):
        proc = subprocess.run([self.script, "non_existent_ref_999"], cwd=self.temp_repo, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "Must exit with non-zero for invalid revision")
        self.assertIn("Error:", proc.stderr)

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Tests for install.sh script execution.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestInstaller(unittest.TestCase):

    def setUp(self):
        self.installer = os.path.join(BASE_DIR, "install.sh")
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_installer_exists_and_help(self):
        self.assertTrue(os.path.isfile(self.installer), "install.sh must exist")
        proc = subprocess.run([self.installer, "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, "--help should exit with 0")
        self.assertIn("Usage:", proc.stdout)

    def test_install_custom_target(self):
        target_skills_dir = os.path.join(self.temp_dir, "skills")
        proc = subprocess.run([self.installer, "--target", target_skills_dir], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Installer failed with: {proc.stderr}")

        installed_skill = os.path.join(target_skills_dir, "simplifeyn", "SKILL.md")
        self.assertTrue(os.path.isfile(installed_skill), "SKILL.md must exist in target directory")

    def test_install_check_mode(self):
        target_skills_dir = os.path.join(self.temp_dir, "skills")
        # Install first
        subprocess.run([self.installer, "--target", target_skills_dir], check=True, capture_output=True)

        # Run check
        proc = subprocess.run([self.installer, "--check", "--target", target_skills_dir], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"--check failed: {proc.stderr}")
        self.assertIn("up to date", proc.stdout.lower())

    def test_check_mode_fails_when_missing_or_modified(self):
        target_skills_dir = os.path.join(self.temp_dir, "skills")
        # 1. Not installed yet -> should fail with exit code 1
        proc = subprocess.run([self.installer, "--check", "--target", target_skills_dir], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "--check must exit non-zero when target is not installed")

        # 2. Install
        subprocess.run([self.installer, "--target", target_skills_dir], check=True, capture_output=True)

        # 3. Modify an installed file
        skill_md = os.path.join(target_skills_dir, "simplifeyn", "SKILL.md")
        with open(skill_md, "a", encoding="utf-8") as f:
            f.write("\n# drifted\n")

        proc2 = subprocess.run([self.installer, "--check", "--target", target_skills_dir], capture_output=True, text=True)
        self.assertNotEqual(proc2.returncode, 0, "--check must exit non-zero when an installed file has drifted")

    def test_permissions_and_directories_preserved(self):
        target_skills_dir = os.path.join(self.temp_dir, "skills")
        subprocess.run([self.installer, "--target", target_skills_dir], check=True, capture_output=True)

        installed_dir = os.path.join(target_skills_dir, "simplifeyn")
        self.assertTrue(os.path.isdir(os.path.join(installed_dir, "references")))
        self.assertTrue(os.path.isdir(os.path.join(installed_dir, "assets")))
        self.assertTrue(os.path.isdir(os.path.join(installed_dir, "scripts")))

        diff_script = os.path.join(installed_dir, "scripts", "get-diff.sh")
        self.assertTrue(os.path.isfile(diff_script))
        self.assertTrue(os.access(diff_script, os.X_OK), "Installed scripts/get-diff.sh must be executable")

if __name__ == "__main__":
    unittest.main()

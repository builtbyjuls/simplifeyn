#!/usr/bin/env python3
"""
Tests for skill structure, frontmatter, and reference integrity.
"""
import os
import re
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestSkillStructure(unittest.TestCase):

    def setUp(self):
        self.skill_md = os.path.join(BASE_DIR, "SKILL.md")
        self.readme_md = os.path.join(BASE_DIR, "README.md")
        self.license_file = os.path.join(BASE_DIR, "LICENSE")
        self.install_sh = os.path.join(BASE_DIR, "install.sh")

    def test_required_root_files_exist(self):
        self.assertTrue(os.path.isfile(self.skill_md), "SKILL.md must exist in root")
        self.assertTrue(os.path.isfile(self.readme_md), "README.md must exist in root")
        self.assertTrue(os.path.isfile(self.license_file), "LICENSE must exist in root")
        self.assertTrue(os.path.isfile(self.install_sh), "install.sh must exist in root")
        self.assertTrue(os.access(self.install_sh, os.X_OK), "install.sh must be executable")

    def test_skill_frontmatter(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        # Check frontmatter exists
        self.assertTrue(content.startswith("---"), "SKILL.md must start with YAML frontmatter delimiter ---")
        frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        self.assertIsNotNone(frontmatter_match, "SKILL.md must contain valid YAML frontmatter")

        frontmatter = frontmatter_match.group(1)
        self.assertIn("name: simplifeyn", frontmatter, "Frontmatter must contain 'name: simplifeyn'")
        self.assertIn("description:", frontmatter, "Frontmatter must contain 'description:'")

    def test_skill_sections(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        required_sections = [
            "Core Debrief Structure",
            "In One Sentence",
            "The Tangible Picture",
            "The Ladder",
            "Where the Picture Breaks",
            "Quality Audit Checklist",
        ]
        for section in required_sections:
            self.assertIn(section, content, f"SKILL.md must contain section '{section}'")

    def test_toggleable_support(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Toggle Mode", content, "SKILL.md must describe Toggle Mode")
        self.assertIn("/simplifeyn on", content, "SKILL.md must support '/simplifeyn on'")
        self.assertIn("/simplifeyn off", content, "SKILL.md must support '/simplifeyn off'")
        self.assertIn("Persistence", content, "SKILL.md must specify persistence across session turns")

    def test_brevity_constraints(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Brevity", content, "SKILL.md must have a section on Brevity")
        self.assertIn("word", content.lower(), "SKILL.md must specify word bounds")
        self.assertIn("preamble", content.lower(), "SKILL.md must forbid preambles")

    def test_ascii_flowchart_guideline(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("ASCII", content, "SKILL.md must mention ASCII flow diagram/chart")
        self.assertTrue(
            any(k in content.lower() for k in ["flow diagram", "flowchart", "mechanism flow"]),
            "SKILL.md must guide the creation of an ASCII mechanism flow/diagram"
        )

    def test_references_exist(self):
        ref_dir = os.path.join(BASE_DIR, "references")
        self.assertTrue(os.path.isdir(ref_dir), "references/ directory must exist")

        required_refs = [
            "voice.md",
            "analogies.md",
            "ladder.md",
            "failure-modes.md",
        ]
        for ref in required_refs:
            ref_path = os.path.join(ref_dir, ref)
            self.assertTrue(os.path.isfile(ref_path), f"references/{ref} must exist")

    def test_assets_and_scripts_exist(self):
        assets_dir = os.path.join(BASE_DIR, "assets")
        self.assertTrue(os.path.isdir(assets_dir), "assets/ directory must exist")
        self.assertTrue(os.path.isfile(os.path.join(assets_dir, "worked-examples.md")), "assets/worked-examples.md must exist")

        scripts_dir = os.path.join(BASE_DIR, "scripts")
        self.assertTrue(os.path.isdir(scripts_dir), "scripts/ directory must exist")
        get_diff = os.path.join(scripts_dir, "get-diff.sh")
        self.assertTrue(os.path.isfile(get_diff), "scripts/get-diff.sh must exist")
        self.assertTrue(os.access(get_diff, os.X_OK), "scripts/get-diff.sh must be executable")

        audit_script = os.path.join(scripts_dir, "audit_debrief.py")
        self.assertTrue(os.path.isfile(audit_script), "scripts/audit_debrief.py must exist")

if __name__ == "__main__":
    unittest.main()

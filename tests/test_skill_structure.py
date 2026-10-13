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
        self.assertIn("Use when", frontmatter, "Frontmatter description must contain 'Use when' trigger context")
        self.assertNotIn("disable-model-invocation:", frontmatter, "Non-standard disable-model-invocation should be omitted")

    def test_skill_sections(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        required_sections = [
            "Core Debrief Structure",
            "In One Sentence",
            "The Tangible Picture",
            "The Ladder",
            "Where the Picture Breaks",
            "The Ice-Water Test",
            "Where the Machine Snaps",
            "Quality Audit Checklist",
            "Always-On Project Rule",
        ]
        for section in required_sections:
            self.assertIn(section, content, f"SKILL.md must contain section '{section}'")

    def test_ice_water_test_documented(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            skill_content = f.read()
        self.assertIn("The Ice-Water Test", skill_content, "SKILL.md must document The Ice-Water Test")

        with open(self.readme_md, "r", encoding="utf-8") as f:
            readme_content = f.read()
        self.assertIn("Ice-Water Test", readme_content, "README.md must document The Ice-Water Test")
        self.assertIn("Challenger", readme_content, "README.md must connect Ice-Water Test to Feynman's Challenger demonstration")

    def test_where_machine_snaps_documented(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            skill_content = f.read()
        self.assertIn("Where the Machine Snaps", skill_content, "SKILL.md must document Where the Machine Snaps")

        with open(self.readme_md, "r", encoding="utf-8") as f:
            readme_content = f.read()
        self.assertIn("Where the Machine Snaps", readme_content, "README.md must document Where the Machine Snaps")
        self.assertIn("Boundary Condition", readme_content, "README.md must explain boundary conditions under Feynman philosophy")

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
        self.assertTrue(
            "2 to 5" in content or "2-5" in content,
            "SKILL.md must specify 2 to 5 line ASCII mechanism flow diagram"
        )

        # Check all diagram blocks in SKILL.md and assets/worked-examples.md
        for file_path in [self.skill_md, os.path.join(BASE_DIR, "assets", "worked-examples.md")]:
            with open(file_path, "r", encoding="utf-8") as f:
                fc = f.read()
            diagram_blocks = re.findall(r"```text\s*\n([\s\S]*?)```", fc)
            for block in diagram_blocks:
                if "[" in block and "--->" in block:
                    lines = [ln for ln in block.strip().splitlines() if ln.strip()]
                    self.assertTrue(
                        2 <= len(lines) <= 5,
                        f"Diagram in {os.path.basename(file_path)} must have 2-5 lines (found {len(lines)} lines):\n{block}"
                    )

    def test_banned_words_missing_fails_loudly(self):
        import subprocess
        code = (
            "import sys, os; "
            f"sys.path.insert(0, {repr(os.path.join(BASE_DIR, 'scripts'))}); "
            "import audit_debrief; "
            "audit_debrief.load_banned_words('/nonexistent/path/banned-words.txt')"
        )
        proc = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(proc.returncode, 0, "audit_debrief must fail loudly if banned-words.txt is missing")
        self.assertIn("FileNotFoundError", proc.stderr)

    def test_analogy_lenses_and_fallback_support(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            skill_content = f.read()

        self.assertIn("--as=", skill_content, "SKILL.md must document lens parameter --as=<theme>")
        self.assertIn("fallback", skill_content.lower(), "SKILL.md must document fallback rules for ill-fitting lenses")
        self.assertIn("explore other lenses", skill_content.lower(), "SKILL.md must document exploration footer")

        analogies_path = os.path.join(BASE_DIR, "references", "analogies.md")
        with open(analogies_path, "r", encoding="utf-8") as f:
            analogies_content = f.read().lower()

        required_domains = ["kitchen", "warehouse", "workshop", "transit", "office", "gaming"]
        for domain in required_domains:
            self.assertIn(domain, analogies_content, f"analogies.md must document the '{domain}' domain")

    def test_dynamic_audience_lenses_and_targeted_ladder_rung(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            skill_content = f.read().lower()

        self.assertIn("vibe-coder", skill_content, "SKILL.md must document 'vibe-coder' audience lens")
        self.assertIn("junior-dev", skill_content, "SKILL.md must document 'junior-dev' audience lens")
        self.assertIn("senior-dev", skill_content, "SKILL.md must document 'senior-dev' audience lens")
        self.assertTrue(
            any(k in skill_content for k in ["targeted rung", "targeted single-line rung", "targeted level"]),
            "SKILL.md must document targeted ladder rung for active audience level"
        )

        ladder_path = os.path.join(BASE_DIR, "references", "ladder.md")
        with open(ladder_path, "r", encoding="utf-8") as f:
            ladder_content = f.read().lower()

        self.assertIn("vibe-coder", ladder_content, "ladder.md must document vibe-coder level")
        self.assertIn("junior-dev", ladder_content, "ladder.md must document junior-dev level")
        self.assertIn("senior-dev", ladder_content, "ladder.md must document senior-dev level")

    def test_references_exist(self):
        ref_dir = os.path.join(BASE_DIR, "references")
        self.assertTrue(os.path.isdir(ref_dir), "references/ directory must exist")

        required_refs = [
            "voice.md",
            "analogies.md",
            "ladder.md",
            "failure-modes.md",
            "banned-words.txt",
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

    def test_complexity_gating_documented(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Complexity Gating", content, "SKILL.md must contain a section on Complexity Gating")
        self.assertIn("Skip Criteria", content, "SKILL.md must document Skip Criteria")
        self.assertIn("Debrief Triggers", content, "SKILL.md must document Debrief Triggers")
        self.assertIn("[Simplifeyn debrief skipped", content, "SKILL.md must document skipped format marker")

    def test_readme_documents_gating(self):
        with open(self.readme_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Complexity Gating", content, "README.md must document Complexity Gating")
        self.assertIn("/simplifeyn skip", content, "README.md must document '/simplifeyn skip'")

    def test_skills_sh_installation_documented(self):
        with open(self.readme_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("npx skills add builtbyjuls/simplifeyn", content, "README.md must document 'npx skills add builtbyjuls/simplifeyn'")
        self.assertIn("skills.sh", content.lower(), "README.md must reference skills.sh ecosystem")

    def test_always_on_rule_synchronized(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            skill_content = f.read()
        with open(self.readme_md, "r", encoding="utf-8") as f:
            readme_content = f.read()

        self.assertIn("7. Lens Footer", skill_content, "SKILL.md always-on rule must contain 7. Lens Footer")
        self.assertIn("7. Lens Footer", readme_content, "README.md always-on rule must contain 7. Lens Footer")

    def test_linter_form_only_note_in_skill(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            skill_content = f.read()

        self.assertTrue(
            any(k in skill_content.lower() for k in ["form check", "heuristic form", "structural sections", "factual accuracy"]),
            "SKILL.md must note that the audit linter verifies form/structure, not factual domain accuracy"
        )

    def test_word_budget_consistency(self):
        with open(self.skill_md, "r", encoding="utf-8") as f:
            skill_content = f.read()
        with open(self.readme_md, "r", encoding="utf-8") as f:
            readme_content = f.read()

        self.assertIn("170", skill_content, "SKILL.md must state target under 170 prose words")
        self.assertIn("250", skill_content, "SKILL.md must state hard ceiling of 250 total words")
        self.assertIn("170", readme_content, "README.md must state target under 170 prose words")
        self.assertIn("250", readme_content, "README.md must state hard ceiling of 250 total words")

        self.assertNotIn("150 prose words", skill_content, "SKILL.md must not contain stale '150 prose words'")
        self.assertNotIn("150 prose words", readme_content, "README.md must not contain stale '150 prose words'")
        self.assertNotIn("220 words", skill_content, "SKILL.md must not contain stale '220 words'")
        self.assertNotIn("220 words", readme_content, "README.md must not contain stale '220 words'")

    def test_combined_audience_and_theme_documented(self):
        with open(self.readme_md, "r", encoding="utf-8") as f:
            readme_content = f.read()
        self.assertIn("for junior-dev as gaming", readme_content, "README.md must document combined audience and theme lens")

if __name__ == "__main__":
    unittest.main()



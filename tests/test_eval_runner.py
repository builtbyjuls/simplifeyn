#!/usr/bin/env python3
"""
Unit tests for the Feynman Index Evals & Leaderboard Harness (scripts/eval_runner.py).
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import eval_runner


class TestEvalRunner(unittest.TestCase):
    def setUp(self):
        self.perfect_debrief = (
            "### 1. In One Sentence\n"
            "The app now skips login checks unless an environment switch turns the locks on.\n\n"
            "### 2. The Tangible Picture\n"
            "An office turnstile with its locking arm unlatched, letting anyone walk through until a receptionist flips the wall toggle.\n\n"
            "```text\n"
            "[ Visitor ] ---> [ Unlocked Turnstile ] ---> [ Office Floor ]\n"
            "(HTTP Call)       (Skip Token Check)          (Private Route)\n"
            "                         |\n"
            "        [ Flip Wall Toggle ---> Arm Locks Down ]\n"
            "          (AUTH_REQUIRED=\"true\")  (Check Token)\n"
            "```\n\n"
            "Where the picture breaks: an unlocked turnstile clicks audibly, but an open web route admits thousands silently.\n\n"
            "### 3. The Ladder\n"
            "- **Level (Vibe Coder):** Pages open without passwords during local tests, but anyone on the web can view private account data if deployed.\n\n"
            "### 4. The Screen Test\n"
            "Open an incognito browser window, open your profile page, and verify it loads without asking for a password.\n\n"
            "### 5. The Danger Zone (Prompt Safety)\n"
            "- What Can Break: Deploying without the flag exposes all account data to public scraping.\n"
            "- Guardrail (If Prompting Next): Tell your AI: Keep auth open during local tests, but restore default locks before merging.\n\n"
            "### 6. What Was Left Out\n"
            "Session cookie expiration and role checks were omitted.\n"
        )

    def test_calculate_score_perfect_debrief(self):
        result = eval_runner.score_debrief(self.perfect_debrief)
        self.assertTrue(result["passed"])
        self.assertGreaterEqual(result["score"], 90)
        self.assertIn(result["grade"], ["A+", "A"])
        self.assertEqual(result["breakdown"]["mechanism_purity"], 25)
        self.assertEqual(result["breakdown"]["honest_limits"], 25)
        self.assertEqual(result["breakdown"]["audience_calibration"], 20)
        self.assertEqual(result["breakdown"]["empirical_verification"], 15)

    def test_calculate_score_banned_buzzwords_penalty(self):
        flawed_debrief = self.perfect_debrief.replace(
            "The app now skips login checks",
            "The app basically simply streamlines login checks",
        )
        result = eval_runner.score_debrief(flawed_debrief)
        self.assertLess(result["breakdown"]["mechanism_purity"], 25)
        self.assertFalse(result["passed"])
        self.assertGreaterEqual(len(result["banned_words_found"]), 2)

    def test_calculate_score_missing_breaking_point(self):
        flawed_debrief = self.perfect_debrief.replace(
            "Where the picture breaks: an unlocked turnstile clicks audibly, but an open web route admits thousands silently.\n\n",
            "",
        )
        result = eval_runner.score_debrief(flawed_debrief)
        self.assertEqual(result["breakdown"]["honest_limits"], 15)
        self.assertFalse(result["passed"])

    def test_calculate_score_excessive_words_penalty(self):
        bloated_prose = "extra word " * 180
        flawed_debrief = self.perfect_debrief + "\n\n" + bloated_prose
        result = eval_runner.score_debrief(flawed_debrief)
        self.assertLess(result["breakdown"]["brevity_density"], 10)
        self.assertFalse(result["passed"])

    def test_calculate_score_missing_ice_water_test(self):
        flawed_debrief = self.perfect_debrief.replace("### 4. The Screen Test\n", "### 4. Other Notes\n")
        result = eval_runner.score_debrief(flawed_debrief)
        self.assertLess(result["breakdown"]["empirical_verification"], 15)

    def test_eval_transcript_fixture(self):
        fixture_path = os.path.join(BASE_DIR, "assets", "transcripts", "02-security-flag-claude-sonnet-5.5.md")
        self.assertTrue(os.path.isfile(fixture_path), "Fixture must exist")
        with open(fixture_path, "r", encoding="utf-8") as f:
            content = f.read()

        section = content.split("## 3. Simplifeyn Output: Level (Vibe Coder - Default)")[1].split("\n---\n")[0]
        if "> **Prompt:**" in section:
            section = section.split("\n\n", 1)[1].strip()

        result = eval_runner.score_debrief(section)
        self.assertTrue(result["passed"], f"Fixture should pass eval: {result.get('errors')}")
        self.assertGreaterEqual(result["score"], 90)

    def test_benchmark_aggregation(self):
        transcripts_dir = os.path.join(BASE_DIR, "assets", "transcripts")
        leaderboard = eval_runner.run_benchmark(transcripts_dir)
        self.assertIn("models", leaderboard)
        self.assertIn("overall_avg_score", leaderboard)
        self.assertIn("total_evals", leaderboard)
        self.assertGreater(leaderboard["total_evals"], 0)

        # Confirm models present in assets/transcripts are benchmarked
        model_names = [m["model"] for m in leaderboard["models"]]
        self.assertTrue(any("Claude Sonnet" in m for m in model_names))
        self.assertTrue(any("Gemini" in m for m in model_names))

    def test_json_and_markdown_output(self):
        res = eval_runner.score_debrief(self.perfect_debrief)
        json_out = eval_runner.format_score_json(res)
        self.assertIn('"score":', json_out)
        self.assertIn('"grade":', json_out)

        md_out = eval_runner.format_score_markdown(res)
        self.assertIn("Feynman Scorecard", md_out)
        self.assertIn("Mechanism Purity", md_out)


if __name__ == "__main__":
    unittest.main()

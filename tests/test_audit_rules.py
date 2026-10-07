#!/usr/bin/env python3
"""
Tests for audit_debrief.py validator logic.
"""
import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

class TestAuditDebrief(unittest.TestCase):

    def test_import_audit_module(self):
        try:
            import audit_debrief
        except ImportError:
            self.fail("Could not import audit_debrief from scripts directory")

    def test_banned_words_detected(self):
        import audit_debrief

        bad_text = (
            "## In One Sentence\n"
            "Basically, this is a simple cache that obviously optimizes requests.\n"
            "## The Tangible Picture\n"
            "Imagine a desk.\n"
            "## The Ladder\n"
            "Level 0: it is easy.\n"
            "Level 1: it is fast.\n"
            "## Where the Picture Breaks\n"
            "It breaks at scale.\n"
        )
        result = audit_debrief.audit_text(bad_text)
        self.assertFalse(result["passed"], "Text with 'basically', 'obviously', 'simple' should fail")
        self.assertTrue(len(result["banned_words_found"]) > 0, "Should identify banned words found")

    def test_well_formed_explanation_passes(self):
        import audit_debrief

        good_text = (
            "## In One Sentence\n"
            "Incoming requests now check local memory before touching the database disk, keeping the 100 most recent records within arms reach.\n\n"
            "## The Tangible Picture\n"
            "A short-order cook keeping salt and pepper shakers directly on the prep counter instead of walking across the kitchen to the pantry every time an order arrives.\n\n"
            "## The Ladder\n"
            "- **Level 0 (Kitchen Table):** We stop walking across the warehouse for things people ask for every two seconds; we keep them right on the front table.\n"
            "- **Level 1 (Practitioner):** An in-memory cache keyed by item ID sits in front of SQLite, cutting read queries by 90% at the cost of 4MB RAM.\n"
            "- **Level 2 (Maintainer):** Cache entries expire after 60 seconds; cache stampedes on startup are mitigated by mutex locking around stale fetches.\n\n"
            "## Where the Picture Breaks\n"
            "The cook analogy assumes only one cook; if multiple server instances run in parallel, their prep counters can become out of sync until keys expire.\n\n"
            "## What Was Left Out\n"
            "Distributed cache synchronization across clusters was deferred until we have multiple replica nodes.\n"
        )
        result = audit_debrief.audit_text(good_text)
        self.assertTrue(result["passed"], f"Well-formed text should pass audit, but failed with: {result.get('errors')}")

    def test_missing_what_was_left_out_fails(self):
        import audit_debrief

        text_without_section_5 = (
            "## In One Sentence\n"
            "Incoming requests check local memory.\n\n"
            "## The Tangible Picture\n"
            "A cook keeping salt on the counter.\n\n"
            "## The Ladder\n"
            "- Level 0: simple.\n"
            "- Level 1: technical.\n\n"
            "## Where the Picture Breaks\n"
            "Breaks with multiple cooks.\n"
        )
        result = audit_debrief.audit_text(text_without_section_5)
        self.assertFalse(result["passed"], "Omitting 'What Was Left Out' must fail audit")
        self.assertIn("What Was Left Out", result["missing_sections"])

    def test_flexible_headings_pass(self):
        import audit_debrief

        # Headings matching SKILL.md format: h3 with numbers
        h3_text = (
            "### 1. In One Sentence\n"
            "Incoming requests check local memory.\n\n"
            "### 2. The Tangible Picture\n"
            "A cook keeping salt on the counter.\n\n"
            "### 3. The Ladder\n"
            "- Level 0: kitchen table.\n"
            "- Level 1: practitioner.\n\n"
            "### 4. Where the Picture Breaks\n"
            "Breaks with multiple cooks.\n\n"
            "### 5. What Was Left Out\n"
            "Distributed caching was deferred.\n"
        )
        result = audit_debrief.audit_text(h3_text)
        self.assertTrue(result["passed"], f"H3 numbered headings should pass audit: {result.get('errors')}")

    def test_cli_file_not_found_handled(self):
        import subprocess
        audit_script = os.path.join(BASE_DIR, "scripts", "audit_debrief.py")
        proc = subprocess.run(
            [sys.executable, audit_script, "non_existent_file_12345.md"],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 1, "CLI must exit with code 1 for non-existent file")
        self.assertNotIn("Traceback", proc.stderr, "CLI should not output unhandled Python traceback")
        self.assertIn("Error:", proc.stderr, "CLI should print user-friendly Error message")

    def test_excessive_verbosity_flagged(self):
        import audit_debrief

        # Generate a verbose text > 250 words
        filler = "The mechanism operates across multiple boundaries and performs tasks repeatedly without pause. " * 30
        verbose_text = (
            "### 1. In One Sentence\n"
            f"Here is what happened: {filler}\n\n"
            "### 2. The Tangible Picture\n"
            "A cook in a kitchen.\n\n"
            "### 3. The Ladder\n"
            "- Level 0: kitchen table.\n"
            "- Level 1: practitioner.\n\n"
            "### 4. Where the Picture Breaks\n"
            "Breaks at scale.\n\n"
            "### 5. What Was Left Out\n"
            "Left out details.\n"
        )
        result = audit_debrief.audit_text(verbose_text)
        self.assertFalse(result["passed"], "Debrief exceeding 250 words must fail audit for verbosity")
        self.assertTrue(any("verbose" in err.lower() or "word count" in err.lower() for err in result["errors"]))

    def test_conversational_preambles_flagged(self):
        import audit_debrief

        fluffy_text = (
            "Sure! I have completed implementing the feature. Here is what changed:\n\n"
            "### 1. In One Sentence\n"
            "Incoming requests check local memory.\n\n"
            "### 2. The Tangible Picture\n"
            "A cook keeping salt on the counter.\n\n"
            "### 3. The Ladder\n"
            "- Level 0: kitchen table.\n"
            "- Level 1: practitioner.\n\n"
            "### 4. Where the Picture Breaks\n"
            "Breaks with multiple cooks.\n\n"
            "### 5. What Was Left Out\n"
            "Deferred clustering.\n\n"
            "Hope this helps! Let me know if you need anything else."
        )
        result = audit_debrief.audit_text(fluffy_text)
        self.assertFalse(result["passed"], "Debrief with conversational preambles/postambles must fail audit")
        self.assertTrue(any("preamble" in err.lower() or "conversational" in err.lower() or "pleasantr" in err.lower() for err in result["errors"]))

    def test_lean_concise_debrief_passes(self):
        import audit_debrief

        lean_text = (
            "### In One Sentence\n"
            "When a server fails, we double the wait before each retry and add a random wobble so clients do not stampede at once.\n\n"
            "### The Picture\n"
            "A host telling guests to wait 1 minute, then 2, then 4, with a dice roll so they do not all knock at once. Breaks if clients share the same clock seed.\n\n"
            "### The Ladder\n"
            "- **Level 0 (Plain):** Your computer waits twice as long each time instead of pestering the busy site every second.\n"
            "- **Level 1 (Code):** `fetchWithRetry` now uses exponential backoff with jitter. Trade-off: up to 7.5s worst-case latency to eliminate stampedes.\n"
            "- **Level 2 (Edge):** Retries blindly on 4xx client errors; delays over 6 retries exceed 1 minute without deadline budget.\n\n"
            "### What Was Left Out\n"
            "Shared circuit breaker telemetry deferred to next PR.\n"
        )
        result = audit_debrief.audit_text(lean_text)
        self.assertTrue(result["passed"], f"Lean debrief should pass: {result.get('errors')}")

if __name__ == "__main__":
    unittest.main()

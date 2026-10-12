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
            "Incoming requests now check local memory before touching the database disk, keeping the 100 most recent records within reach.\n\n"
            "## The Tangible Picture\n"
            "A short-order cook keeping salt and pepper shakers directly on the prep counter instead of walking to the pantry for every order.\n\n"
            "```text\n"
            "[ Order Slip ] ---> [ Check Prep Table ] ---> [ Dish Ready ]\n"
            " (Incoming Req)       (In-Memory Cache)         (Fast Return)\n"
            "```\n\n"
            "## Where the Picture Breaks\n"
            "Assumes one cook; if multiple server instances run in parallel, their prep counters can become out of sync until keys expire.\n\n"
            "## The Ladder\n"
            "- **Level 0 (Kitchen Table):** We stop walking across the room for things people ask for constantly; we keep them on the front table.\n"
            "- **Level 1 (Practitioner):** An in-memory cache keyed by item ID sits in front of SQLite, cutting read queries by 90% at the cost of 4MB RAM.\n"
            "- **Level 2 (Maintainer):** Cache entries expire after 60 seconds; cache stampedes on startup are mitigated by mutex locking around stale fetches.\n\n"
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
            "```text\n"
            "[ Customer Order ] ---> [ Salt on Counter ] ---> [ Meal Served ]\n"
            " (Incoming Read)          (Cached Record)          (Fast Reply)\n"
            "```\n\n"
            "### 3. The Ladder\n"
            "- **Level 0 (Plain):** Keep things on the counter.\n"
            "- **Level 1 (Code):** Uses local memory dictionary.\n"
            "- **Level 2 (Edge):** Memory cap is 100 entries.\n\n"
            "### 4. Where the Picture Breaks\n"
            "Breaks with multiple cooks sharing one prep table.\n\n"
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

        # Generate a verbose text > 150 prose words
        filler = "The mechanism operates across multiple boundaries and performs tasks repeatedly without pause. " * 25
        verbose_text = (
            "### 1. In One Sentence\n"
            f"Here is what happened: {filler}\n\n"
            "### 2. The Tangible Picture\n"
            "A cook in a kitchen.\n\n"
            "```text\n"
            "[ Order ] ---> [ Kitchen ]\n"
            "```\n\n"
            "### 3. The Ladder\n"
            "- Level 0: kitchen table.\n"
            "- Level 1: practitioner.\n"
            "- Level 2: maintainer.\n\n"
            "### 4. Where the Picture Breaks\n"
            "Breaks at scale.\n\n"
            "### 5. What Was Left Out\n"
            "Left out details.\n"
        )
        result = audit_debrief.audit_text(verbose_text)
        self.assertFalse(result["passed"], "Debrief exceeding prose budget must fail audit for verbosity")
        self.assertTrue(any("verbose" in err.lower() or "word count" in err.lower() for err in result["errors"]))

    def test_conversational_preambles_flagged(self):
        import audit_debrief

        fluffy_text = (
            "Sure! I have completed implementing the feature. Here is what changed:\n\n"
            "### 1. In One Sentence\n"
            "Incoming requests check local memory.\n\n"
            "### 2. The Tangible Picture\n"
            "A cook keeping salt on the counter.\n\n"
            "```text\n"
            "[ Order ] ---> [ Counter ]\n"
            "```\n\n"
            "### 3. The Ladder\n"
            "- Level 0: kitchen table.\n"
            "- Level 1: practitioner.\n"
            "- Level 2: maintainer.\n\n"
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
            "A host telling guests to wait 1 minute, then 2, then 4, with a dice roll so they do not all knock at once.\n\n"
            "```text\n"
            "[ Turned Guest ] ---> [ Dice Roll & Wait ] ---> [ Knock Door ]\n"
            " (Failed Request)       (Exponential Jitter)      (Retry Call)\n"
            "```\n\n"
            "Where the Picture Breaks: clients sharing the same seed can synchronize anyway.\n\n"
            "### The Ladder\n"
            "- **Level 0 (Plain):** Your computer waits twice as long each time instead of pestering the busy site every second.\n"
            "- **Level 1 (Code):** `fetchWithRetry` now uses exponential backoff with jitter. Trade-off: up to 7.5s worst-case latency to eliminate stampedes.\n"
            "- **Level 2 (Edge):** Retries blindly on 4xx client errors; delays over 6 retries exceed 1 minute without deadline budget.\n\n"
            "### What Was Left Out\n"
            "Shared circuit breaker telemetry deferred to next PR.\n"
        )
        result = audit_debrief.audit_text(lean_text)
        self.assertTrue(result["passed"], f"Lean debrief should pass: {result.get('errors')}")

    def test_official_worked_example_passes(self):
        import audit_debrief
        worked_examples_path = os.path.join(BASE_DIR, "assets", "worked-examples.md")
        with open(worked_examples_path, "r", encoding="utf-8") as f:
            content = f.read()

        good_marker = "### [GOOD] The Simplifeyn Debrief Output"
        self.assertIn(good_marker, content)
        good_section = content.split(good_marker, 1)[1].strip()
        result = audit_debrief.audit_text(good_section)
        self.assertTrue(result["passed"], f"Official worked-example [GOOD] debrief must pass audit: {result.get('errors')}")

    def test_debrief_with_ascii_flowchart_passes(self):
        import audit_debrief

        flow_text = (
            "### 1. In One Sentence\n"
            "When a server fails, we double the wait before each retry and add a random wobble so clients do not stampede at once.\n\n"
            "### 2. The Tangible Picture\n"
            "A host telling turned-away guests to wait with a dice roll so they do not all knock at once.\n\n"
            "```text\n"
            "[ Turned-Away Guest ] ---> [ Roll Dice & Wait ] ---> [ Knock on Door ]\n"
            "    (Server 5xx Error)       (2^attempt + Jitter)       (Next Retry Attempt)\n"
            "                                      |\n"
            "                      [ Out of Patience? ---> Walk Away ]\n"
            "                        (Retries Exhausted)   (Throw Error)\n"
            "```\n\n"
            "Where the Picture Breaks: clients sharing the same seed can synchronize anyway.\n\n"
            "### 3. The Ladder\n"
            "- **Level 0 (Plain):** Your machine waits twice as long each time instead of pestering the busy site every second.\n"
            "- **Level 1 (Code):** `fetchWithRetry` now doubles delay with up to 500ms jitter, trading 7.5s worst-case latency to eliminate stampedes.\n"
            "- **Level 2 (Edge):** Retries all exceptions indiscriminately including 4xx errors; retries past 6 exceed 1 minute without deadline budget.\n\n"
            "### 4. What Was Left Out\n"
            "Circuit breaker state sharing across clients was deferred.\n"
        )
        result = audit_debrief.audit_text(flow_text)
        self.assertTrue(result["passed"], f"Debrief with ASCII flowchart must pass audit: {result.get('errors')}")

    def test_debrief_with_lens_footer_passes(self):
        import audit_debrief

        text_with_footer = (
            "### 1. In One Sentence\n"
            "When a server fails, we double the wait before each retry and add a random wobble so clients do not stampede at once.\n\n"
            "### 2. The Tangible Picture\n"
            "A host telling turned-away guests to wait with a dice roll so they do not all knock at once.\n\n"
            "```text\n"
            "[ Turned-Away Guest ] ---> [ Roll Dice & Wait ] ---> [ Knock on Door ]\n"
            "    (Server 5xx Error)       (2^attempt + Jitter)       (Next Retry Attempt)\n"
            "```\n\n"
            "Where the Picture Breaks: clients sharing the same seed can synchronize anyway.\n\n"
            "### 3. The Ladder\n"
            "- **Level 0 (Plain):** Your machine waits twice as long each time instead of pestering the busy site every second.\n"
            "- **Level 1 (Code):** `fetchWithRetry` now doubles delay with up to 500ms jitter, trading 7.5s worst-case latency to eliminate stampedes.\n"
            "- **Level 2 (Edge):** Retries all exceptions indiscriminately including 4xx errors; retries past 6 exceed 1 minute without deadline budget.\n\n"
            "### 4. What Was Left Out\n"
            "Circuit breaker state sharing across clients was deferred.\n\n"
            "Explore other lenses: /simplifeyn as warehouse | as workshop | as transit\n"
        )
        result = audit_debrief.audit_text(text_with_footer)
        self.assertTrue(result["passed"], f"Debrief with lens exploration footer must pass: {result.get('errors')}")

    def test_debrief_with_fallback_note_passes(self):
        import audit_debrief

        text_with_fallback = (
            "Note on lens: A 'kitchen' analogy distorts hardware memory fences; falling back to 'workshop' (latches & spring-loaded valves) for honest mechanics.\n\n"
            "### 1. In One Sentence\n"
            "CPU instructions now wait for an explicit latch to release before touching shared memory addresses.\n\n"
            "### 2. The Tangible Picture\n"
            "A spring latch holding back a mechanical lever until the previous gear rotation clicks into place.\n\n"
            "```text\n"
            "[ Memory Write ] ---> [ Spring Latch Guard ] ---> [ Lever Release ]\n"
            "   (Store Buffer)           (Memory Barrier)          (RAM Commit)\n"
            "```\n\n"
            "Where the Picture Breaks: physical springs have mechanical delay, while CPU fences execute in clock cycles.\n\n"
            "### 3. The Ladder\n"
            "- **Level 0 (Plain):** A physical gate stops the machine from writing on the board until the reader finishes reading.\n"
            "- **Level 1 (Code):** Inserted `atomic_thread_fence(memory_order_release)` to prevent out-of-order store reordering.\n"
            "- **Level 2 (Edge):** Prevents stale reads across CPU cores on weakly-ordered architectures like ARM.\n\n"
            "### 4. What Was Left Out\n"
            "Cache coherency bus snooping hardware details were omitted.\n"
        )
        result = audit_debrief.audit_text(text_with_fallback)
        self.assertTrue(result["passed"], f"Debrief with fallback lens note must pass: {result.get('errors')}")

    def test_banned_words_includes_optimized_and_streamline(self):
        import audit_debrief

        text_with_buzzwords = (
            "### 1. In One Sentence\n"
            "This change optimized database latency and streamlined queries.\n\n"
            "### 2. The Tangible Picture\n"
            "A cook in a kitchen.\n\n"
            "```text\n"
            "[ Order ] ---> [ Kitchen ]\n"
            "```\n\n"
            "Where the Picture Breaks: breaks when kitchen burns.\n\n"
            "### 3. The Ladder\n"
            "- **Level 0 (Plain):** Faster cook.\n"
            "- **Level 1 (Code):** Better queries.\n"
            "- **Level 2 (Edge):** Memory limit.\n\n"
            "### 4. What Was Left Out\n"
            "Nothing omitted.\n"
        )
        result = audit_debrief.audit_text(text_with_buzzwords)
        self.assertFalse(result["passed"], "Debrief with 'optimized' or 'streamlined' must fail audit")
        self.assertTrue(any("optimize" in b.lower() or "streamline" in b.lower() for b in result["banned_words_found"]))

    def test_ladder_must_have_three_levels_and_three_bullets(self):
        import audit_debrief

        # Missing Level 2
        text_missing_l2 = (
            "### 1. In One Sentence\n"
            "Requests check memory before disk.\n\n"
            "### 2. The Tangible Picture\n"
            "A cook in a kitchen.\n\n"
            "```text\n"
            "[ Order ] ---> [ Table ]\n"
            "```\n\n"
            "Where the Picture Breaks: breaks when out of room.\n\n"
            "### 3. The Ladder\n"
            "- **Level 0 (Plain):** Fast table.\n"
            "- **Level 1 (Code):** In-memory dict.\n\n"
            "### 4. What Was Left Out\n"
            "Clustering deferred.\n"
        )
        result = audit_debrief.audit_text(text_missing_l2)
        self.assertFalse(result["passed"], "Ladder missing Level 2 must fail audit")

    def test_missing_ascii_diagram_fails_audit(self):
        import audit_debrief

        text_without_diagram = (
            "### 1. In One Sentence\n"
            "Requests check memory before disk.\n\n"
            "### 2. The Tangible Picture\n"
            "A cook keeping salt on the counter.\n\n"
            "Where the Picture Breaks: breaks with multiple cooks.\n\n"
            "### 3. The Ladder\n"
            "- **Level 0 (Plain):** Fast table.\n"
            "- **Level 1 (Code):** In-memory dict.\n"
            "- **Level 2 (Maintainer):** Memory limit.\n\n"
            "### 4. What Was Left Out\n"
            "Clustering deferred.\n"
        )
        result = audit_debrief.audit_text(text_without_diagram)
        self.assertFalse(result["passed"], "Debrief missing ASCII diagram in picture must fail audit")

    def test_in_one_sentence_must_be_single_sentence(self):
        import audit_debrief

        multi_sentence_text = (
            "### 1. In One Sentence\n"
            "Requests check memory first. Then they check the database disk. Finally they write back.\n\n"
            "### 2. The Tangible Picture\n"
            "A cook in a kitchen.\n\n"
            "```text\n"
            "[ Order ] ---> [ Kitchen ]\n"
            "```\n\n"
            "Where the Picture Breaks: breaks when full.\n\n"
            "### 3. The Ladder\n"
            "- **Level 0 (Plain):** Fast table.\n"
            "- **Level 1 (Code):** In-memory dict.\n"
            "- **Level 2 (Maintainer):** Memory limit.\n\n"
            "### 4. What Was Left Out\n"
            "Clustering deferred.\n"
        )
        result = audit_debrief.audit_text(multi_sentence_text)
        self.assertFalse(result["passed"], "'In One Sentence' section with multiple sentences must fail audit")

    def test_prose_word_budget_calculation(self):
        import audit_debrief

        good_text = (
            "### 1. In One Sentence\n"
            "When a server fails, we double the wait before each retry and add a random wobble so clients do not stampede at once.\n\n"
            "### 2. The Tangible Picture\n"
            "A host telling turned-away guests to wait with a dice roll so they do not all knock at once.\n\n"
            "```text\n"
            "[ Turned Guest ] ---> [ Roll Dice & Wait ] ---> [ Knock Door ]\n"
            " (5xx Error)            (Exponential Jitter)      (Retry Call)\n"
            "```\n\n"
            "Where the Picture Breaks: clients sharing the same seed can synchronize anyway.\n\n"
            "### 3. The Ladder\n"
            "- **Level 0 (Plain):** Your machine waits twice as long each time instead of pestering the busy site every second.\n"
            "- **Level 1 (Code):** `fetchWithRetry` now doubles delay with up to 500ms jitter, trading 7.5s worst-case latency to eliminate stampedes.\n"
            "- **Level 2 (Maintainer):** Retries all exceptions indiscriminately including 4xx errors; retries past 6 exceed 1 minute without deadline budget.\n\n"
            "### 4. What Was Left Out\n"
            "Circuit breaker state sharing across clients was deferred.\n\n"
            "Explore other lenses: /simplifeyn as transit | as workshop\n"
        )
        result = audit_debrief.audit_text(good_text)
        self.assertTrue(result["passed"], f"Well-formed debrief should pass: {result.get('errors')}")
        self.assertLessEqual(result.get("prose_word_count", 999), 150)

if __name__ == "__main__":
    unittest.main()

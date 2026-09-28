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

if __name__ == "__main__":
    unittest.main()

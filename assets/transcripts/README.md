# Real Model Transcript Fixtures

This directory stores real before/after model interaction transcripts across four key scenarios:

1. **Retry / Backoff Logic Change:** A change introducing exponential backoff, jitter, or retry loops.
2. **Security Flag Flip:** Modifying security parameters (e.g., `AUTH_REQUIRED = True -> False` or `ssl: true -> false`).
3. **Config / CI Pipeline Modification:** Changes to build scripts, test runners, or runtime configuration requiring debrief.
4. **Docs / Trivial Edits:** Pure documentation, whitespace, or typo fixes that trigger a gated skip.

> Note: To ensure authentic benchmark fidelity, transcript fixtures must reflect real model outputs rather than synthetic samples.

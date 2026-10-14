# Real Model Transcript Fixtures

This directory stores real before/after model interaction transcripts across benchmark scenarios:

1. **Retry / Backoff Logic Change (Active):** A change introducing exponential backoff, jitter, or retry loops across Gemini 3.8 Flash, Claude Sonnet 3.5, and Claude Opus.
2. **Security Flag Flip (Target):** Modifying security parameters (e.g., `AUTH_REQUIRED = True -> False` or `ssl: true -> false`).
3. **Config / CI Pipeline Modification (Target):** Changes to build scripts, test runners, or runtime configuration requiring debrief.
4. **Docs / Trivial Edits (Target):** Pure documentation, whitespace, or typo fixes that trigger a gated skip.

> Note: To ensure authentic benchmark fidelity, transcript fixtures must reflect real model outputs rather than synthetic samples.

## File Naming Convention

Transcript fixtures follow the pattern `{scenario-id}-{scenario-slug}-{model-slug}.md`:
- `01-retry-backoff-gemini-3.8-flash.md`
- `01-retry-backoff-claude-sonnet-5.5.md`
- `01-retry-backoff-claude-opus-5.5.md`
- `02-security-flag-gemini-3.8-flash.md`

Including the model identifier in the filename allows benchmarking multiple models against the same scenario without bloating a single file.

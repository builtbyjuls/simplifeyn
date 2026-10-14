# Real Model Transcript Fixtures

This directory stores real before/after model interaction transcripts across benchmark scenarios:

1. **Retry / Backoff Logic Change:** A change introducing exponential backoff, jitter, or retry loops (Gemini 3.8 Flash, Claude Sonnet 5.5, Claude Opus).
2. **Security Flag Flip:** Modifying security parameters, e.g. `AUTH_REQUIRED = True -> False` or `ssl: true -> false` (Gemini 3.8 Flash, Claude Sonnet 5.5).
3. **Config / CI Pipeline Modification:** Changes to test runners, worker concurrency, or CI flags requiring debrief (Gemini 3.8 Flash, Claude Sonnet 5.5).
4. **Docs / Trivial Edits:** Pure documentation, whitespace, or typo fixes that trigger a gated skip (Gemini 3.8 Flash, Claude Sonnet 5.5).

> Note: To ensure authentic benchmark fidelity, transcript fixtures must reflect real model outputs rather than synthetic samples.

## File Naming Convention

Transcript fixtures follow the pattern `{scenario-id}-{scenario-slug}-{model-slug}.md`:
- `01-retry-backoff-gemini-3.8-flash.md`
- `01-retry-backoff-claude-sonnet-5.5.md`
- `01-retry-backoff-claude-opus-5.5.md`
- `02-security-flag-gemini-3.8-flash.md`
- `02-security-flag-claude-sonnet-5.5.md`
- `03-config-ci-gemini-3.8-flash.md`
- `03-config-ci-claude-sonnet-5.5.md`
- `04-docs-trivial-gemini-3.8-flash.md`
- `04-docs-trivial-claude-sonnet-5.5.md`

Including the model identifier in the filename allows benchmarking multiple models against the same scenario without bloating a single file.

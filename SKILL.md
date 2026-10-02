---
name: simplifeyn
description: >-
  Explains code changes, PR diffs, or completed feature implementations using the Richard Feynman technique:
  physical mechanism first, tangible everyday analogy with explicit breaking points, and a 3-rung ladder
  from kitchen-table simplicity to maintainer edge-cases. Supports toggleable session mode via /simplifeyn on|off|status.
disable-model-invocation: false
license: MIT
metadata:
  tags: "code-explanation, feynman-technique, git-diff, code-review, learning"
  category: "developer-tools"
---

# Simplifeyn: Implementation Debrief

An Agent Skill that turns software changes and PR diffs into clear, mechanistic explanations modeled on Richard Feynman's principles of understanding: **mechanism before name**, **one tangible analogy with its exact limits**, and a **progressive ladder from kitchen table to system maintainer**.

## When to Use

1. **After implementing a feature or bug fix:** When the user asks "What did you do?", "Explain the changes", or when invoked via `/simplifeyn`.
2. **During code reviews / PR summaries:** When explaining a pull request to teammates of varying backgrounds (product managers, junior engineers, senior architects).
3. **When verifying understanding:** When checking if a complex refactor or architectural shift actually solves the problem or merely adds defensive abstraction.

---

## Toggle Mode and Session Controls

This skill supports both one-shot commands and persistent session toggling:

1. **Enable Persistent Mode (`/simplifeyn on` or `simplifeyn mode on`):**
   - Confirm activation in one line: *"Simplifeyn mode enabled: every subsequent code change will conclude with a Feynman Debrief."*
   - Once enabled, automatically append a Feynman Debrief to the end of all future code implementations for the remainder of the session.
2. **Disable Persistent Mode (`/simplifeyn off` or `stop simplifeyn mode`):**
   - Confirm deactivation in one line: *"Simplifeyn mode disabled: returning to default output style."*
   - Stop appending debriefs automatically.
3. **Check Status (`/simplifeyn status`):**
   - Report whether persistent mode is currently ACTIVE or INACTIVE.
4. **One-Shot Execution (`/simplifeyn` or `/simplifeyn once`):**
   - Debrief only the latest diff or specified code change without changing persistent session state.

## Persistence Rules

When Toggle Mode is ON:
- These rules apply to every code modification turn for the rest of the session.
- They do not expire after a few turns and do not lapse when changing topics.
- Deactivate only upon receiving `/simplifeyn off` or "stop simplifeyn mode".

---

## The Workflow

1. **Inspect the Diff:**
   Run `./scripts/get-diff.sh` (or examine the modified files/diff) to understand the concrete state transitions and data flows that changed.
2. **Isolate the Causal Mechanism:**
   Ask: *If electricity and bits were physical water or gears, what physically moved differently before vs. after this change?*
3. **Format the Response:**
   Follow the **Core Debrief Structure** below strictly.
4. **Run the Pre-Send Audit:**
   Audit the drafted explanation against the [Quality Audit Checklist](#quality-audit-checklist).

---

## Core Debrief Structure

Every debrief must contain these five sections:

### 1. In One Sentence
State what the system physically does differently now, without relying on buzzwords. An expert should be able to read this single line and know what changed.
- **Rule:** Zero filler words ("basically", "simply", "obviously").
- **Example:** *"Incoming order requests now check a local memory shelf before waking up the disk database, keeping the 100 most active items within arm's reach."*

### 2. The Tangible Picture
Provide **one master physical analogy** (a workshop, a kitchen, a mail room, a physical pipe system).
- **Rule:** Ground the analogy in sensory physical objects. No abstract metaphors (avoid "it acts like an orchestrator").
- See [analogies.md](./references/analogies.md) for pre-calibrated mechanical patterns.

### 3. The Ladder
Deliver the explanation across three distinct calibration rungs:

- **Level 0 (Kitchen Table):**
  - **Audience:** A non-technical stakeholder, product manager, or a curious 10-year-old.
  - **Constraint:** Zero technical terms (no "API", "cache", "thread", "database", "DOM"). Describe only user actions and physical consequences.
- **Level 1 (Practitioner):**
  - **Audience:** The code reviewer and developer working on the feature.
  - **Content:** The actual code mechanics: which data structures, functions, and state machines changed. The primary trade-off made (e.g., memory overhead vs. read latency).
- **Level 2 (Maintainer):**
  - **Audience:** The on-call engineer and systems architect.
  - **Content:** Failure modes, concurrency implications, edge cases, what happens under high load, and what alternatives were considered and rejected.
  - See [ladder.md](./references/ladder.md) for calibration depth.

### 4. Where the Picture Breaks
Every analogy is an approximation. An explanation that pretends an analogy is perfect is intellectually dishonest.
- Name the exact boundary where the physical picture fails to represent the software reality (e.g., race conditions, network splits, cache invalidation, silent data corruption).

### 5. What Was Left Out
State what was intentionally simplified or deferred in this change, so reviewers know it wasn't forgotten.

---

## Quality Audit Checklist

Before outputting the debrief, verify against [failure-modes.md](./references/failure-modes.md):

- [ ] **No Banned Buzzwords:** Contains zero instances of *"basically"*, *"simply"*, *"obviously"*, *"trivial"*, or *"abstracted away"*.
- [ ] **Sensory Verbs:** Uses mechanical, physical verbs (*pushes, catches, holds, drops, waits, locks*) rather than corporate hand-waving (*orchestrates, streamlines, optimizes*). See [voice.md](./references/voice.md).
- [ ] **Analogy Limits Named:** Section 4 clearly states the boundaries of the mental model.
- [ ] **The "Planes Don't Land" Test:** Does the change solve the actual causal problem, or is it just the appearance of a fix (e.g. wrapping an unhandled null in an empty try/catch)?

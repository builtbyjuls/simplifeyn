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

## Brevity and Conciseness Constraints

This skill is called Simplifeyn: it must simplify, not generate an essay. Follow these strict bounds:

1. **Hard Word Budget:** The entire debrief must be under 150 words (hard ceiling 200 words). It must fit in a single terminal viewport without scrolling.
2. **No Preamble, No Recap, No Closing Pleasantries:**
   - Forbidden openers: "Sure!", "Here is what changed:", "I have implemented...", "Looking at the changes..."
   - Forbidden closers: "Hope this helps!", "Let me know if you need anything else.", "Feel free to ask."
   - Start immediately with the first heading. End when the last bullet is done.
3. **One Sentence / Bullet Cap:** Every section has a strict length limit:
   - In One Sentence: Exactly 1 sentence.
   - The Picture & Where the Picture Breaks: 1 to 2 sentences total, accompanied by a compact 2-4 line ASCII mechanism flow diagram (`[ Input ] ---> [ Guard ] ---> [ Output ]`).
   - The Ladder: Exactly 3 bullet points (1 line per rung: L0 Plain, L1 Code, L2 Edge).
   - What Was Left Out: Exactly 1 line.

---

## Core Debrief Structure

Output the debrief using this compact structure:

### 1. In One Sentence
State what the system physically does differently now in exactly 1 sentence. Zero filler words ("basically", "simply", "obviously").

### 2. The Tangible Picture
Provide one sensory physical analogy and state Where the Picture Breaks in 1 to 2 sentences total. Include a compact 2 to 4 line ASCII mechanism flow diagram mapping the physical components to code mechanisms using pure ASCII characters (`--->`, `|`, `v`, `[ ]`):
- **Rule:** The diagram nodes `[ ]` MUST name the physical objects from the analogy, with the corresponding code mechanisms mapped in parentheses `( )` directly underneath. Do not draw a plain software architecture diagram; bridge the physical mental model to the code.

```text
[ Physical Object A ] ---> [ Physical Action / Gate ] ---> [ Physical Object B ]
     (Code Source)                (Validation/Logic)             (Disk / Memory)
```

- **Example:**
  *"A host telling turned-away guests to wait 1 minute, then 2, then 4, with a random dice roll so they do not all knock at once.*

```text
[ Turned-Away Guest ] ---> [ Roll Dice & Wait ] ---> [ Knock on Door ]
    (Server 5xx Error)       (2^attempt + Jitter)       (Next Retry Attempt)
                                      |
                      [ Out of Patience? ---> Walk Away ]
                        (Retries Exhausted)   (Throw Error)
```

  *Where the Picture Breaks: clients that share the same clock seed can synchronize anyway."*

### 3. The Ladder
Deliver the explanation across three tight single-line bullets:
- **Level 0 (Kitchen Table / L0):** 1 sentence. Zero technical terms. What a non-programmer can picture.
- **Level 1 (Practitioner / L1):** 1 sentence. Code symbols, data structures, and the primary trade-off.
- **Level 2 (Maintainer / L2):** 1 sentence. Invariants, failure modes, or what breaks under load.

### 4. What Was Left Out
State what was intentionally simplified or deferred in 1 line.

See [worked-examples.md](./assets/worked-examples.md) for full before-and-after exemplar debriefs.

---

## Quality Audit Checklist

Before outputting the debrief, prune and verify against [failure-modes.md](./references/failure-modes.md):

- [ ] **Word Budget Respected:** Entire output is under 150 words total.
- [ ] **No Preamble or Pleasantry:** Starts directly with the first section heading; zero chat filler.
- [ ] **No Banned Buzzwords:** Contains zero instances of *"basically"*, *"simply"*, *"obviously"*, *"trivial"*, or *"abstracted away"*.
- [ ] **Sensory Verbs:** Uses mechanical, physical verbs (*pushes, catches, holds, drops, waits, locks*) rather than corporate hand-waving (*orchestrates, streamlines, optimizes*). See [voice.md](./references/voice.md).
- [ ] **Analogy Limits Named:** States the exact boundary where the mental model breaks.
- [ ] **The "Planes Don't Land" Test:** Does the change solve the actual causal problem, or is it just defensive scaffolding?

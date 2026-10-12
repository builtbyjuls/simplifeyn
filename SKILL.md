---
name: simplifeyn
description: >-
  Explains code changes, PR diffs, or completed feature implementations using the Richard Feynman technique:
  physical mechanism first, tangible everyday analogy with explicit breaking points, and a 3-rung ladder
  from kitchen-table simplicity to maintainer edge-cases. Use when the user asks "what did you do?",
  "explain the changes", during PR reviews, or after completing code implementations. Supports toggleable session mode via /simplifeyn on|off|status.
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
   - Report whether persistent mode is currently ACTIVE or INACTIVE, and list active lens if set.
4. **One-Shot Execution (`/simplifeyn` or `/simplifeyn once`):**
   - Debrief only the latest diff or specified code change without changing persistent session state.
5. **Themed Lens Selection (`/simplifeyn as <theme>` or `/simplifeyn --as=<theme>`):**
   - Direct the debrief to draw analogies from a specific physical domain (`kitchen`, `warehouse`, `workshop`, `transit`, `office`, `gaming`).
   - Also supported with persistence: `/simplifeyn on as <theme>` (or `/simplifeyn on --as=<theme>`).
6. **One-Turn Skip (`/simplifeyn skip` or `--no-debrief`):**
   - Suppress the debrief for the current turn without disabling persistent session mode.

## Persistence Rules

When Toggle Mode is ON:
- Assess diff complexity first using the **Complexity Gating** rules below.
- If the change is trivial or cosmetic, output a standard 1-sentence note and append `[Simplifeyn debrief skipped: cosmetic/trivial change without causal mechanism shift]`.
- If the change introduces non-trivial logic, state changes, or new behavior, append the full Feynman Debrief.
- These rules apply to every code modification turn for the rest of the session.
- They do not expire after a few turns and do not lapse when changing topics.
- Deactivate only upon receiving `/simplifeyn off` or "stop simplifeyn mode".
- **Note on Session State:** Agent Skills are instructions provided to the AI model, not persistent background daemons. Session toggling (`/simplifeyn on`) is an in-context behavioral instruction (best-effort across long contexts). For guaranteed repository-wide debriefs across every new session, use the [Always-On Project Rule](#always-on-project-rule) in `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`.

---

## Complexity Gating: When to Debrief vs. When to Skip

Not every code change warrants a full Feynman debrief. Over-explaining a 1-line typo fix, dependency bump, or formatting tweak creates noise. The agent must evaluate diff complexity before deciding whether to debrief:

### Skip Criteria (Do NOT Debrief)
Skip the Feynman debrief when the change matches any of these conditions:
1. **Documentation, Lockfiles, and Ignores Only:** Changes touch only documentation (`.md`, `.txt`, `.rst`), package lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`), or repository ignores (`.gitignore`, `.editorconfig`, `LICENSE`). Changes to runtime configs (`.json`, `.yml`, `.yaml`, `.toml`) containing logic, security flags, or build/CI commands must be debriefed.
2. **Cosmetic and Styling:** Pure formatting, whitespace, comment clarifications, lint fixes, or variable renames without behavioral shifts.
3. **Trivial One-Liners:** Modifying a static display string or comment without architectural consequence.
4. **Conventional Commit Signals:** Commits prefixed with `docs:`, `chore:`, `style:`, `ci:`, `build:`, or trivial `fix(typo):`.

**Behavior When Skipped:** Output a standard concise summary sentence followed by:
`[Simplifeyn debrief skipped: cosmetic/trivial change without causal mechanism shift]`

### Debrief Triggers (Must Debrief)
Always produce a full Feynman debrief when:
1. **Causal Mechanism Shift:** Data moves, transforms, or persists through different stages, states, or threads than before.
2. **Concurrency, Performance, or Scale:** Caching, locks, debouncing, exponential backoff, rate limiting, async loops, or race condition fixes.
3. **New Features and Contract Changes:** New public APIs, schema migrations, state machines, or business logic.
4. **Security, Auth, or Runtime Config:** Any change altering authentication flags (`AUTH_REQUIRED`), SSL/TLS settings, permissions, or CI test steps.
5. **Conventional Commit Signals:** Commits prefixed with `feat:`, `perf:`, non-trivial `fix:`, or structural `refactor:`.
6. **Explicit Invocation:** The user explicitly typed `/simplifeyn`, or asked *"explain what you did"*.

---

## The Workflow

1. **Inspect the Diff:**
   Run `git diff` (or `./scripts/get-diff.sh` if available) to understand the concrete state transitions and data flows that changed.
2. **Isolate the Causal Mechanism:**
   Ask: *If electricity and bits were physical water or gears, what physically moved differently before vs. after this change?*
3. **Format the Response:**
   Follow the **Core Debrief Structure** below strictly.
4. **Run the Pre-Send Audit:**
   Verify the debrief against the [Quality Audit Checklist](#quality-audit-checklist). When running in CLI or CI environments, execute `python3 scripts/audit_debrief.py` to programmatically validate the debrief.

---

## Brevity and Conciseness Constraints

This skill is called Simplifeyn: it must simplify, not generate an essay. Follow these strict bounds:

1. **Hard Word Budget:** Target under 150 words of explanatory prose (excluding markdown headers and fenced ASCII flow blocks; hard ceiling: 220 words total). Must fit in a single terminal viewport without scrolling.
2. **No Preamble, No Recap, No Closing Pleasantries:**
   - Forbidden openers: "Sure!", "Here is what changed:", "I have implemented...", "Looking at the changes..."
   - Forbidden closers: "Hope this helps!", "Let me know if you need anything else.", "Feel free to ask."
   - Start immediately with the first heading (Section 1). Conclude after Section 4 (What Was Left Out) and the lens exploration footer without conversational sign-offs.
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
(Network Drop / Reset)   (2^attempt + Jitter)       (Next Retry Attempt)
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

Conclude with a single tight exploration footer suggesting 2 to 3 alternative lenses:
`Explore other lenses: /simplifeyn as <theme1> | as <theme2> | as <theme3>`

See [worked-examples.md](./assets/worked-examples.md) for full before-and-after exemplar debriefs.

---

## Themed Analogy Lenses & Fallback Rules

Users can select a preferred physical domain using `--as=<theme>` or `/simplifeyn as <theme>` (`kitchen`, `warehouse`, `workshop`, `transit`, `office`, `gaming`). See [analogies.md](./references/analogies.md) for catalog definitions.

### The Analogy Fit Check & Fallback Rule
1. **Strong Fit:** If the requested lens naturally maps to the causal mechanics, use it.
2. **Poor Fit / Distortion:** If the requested lens would obscure the code or require misleading mental acrobatics, **do not fake it**.
3. **The Fallback Note:** State the reason honestly in 1 line and fall back to the accurate domain:
   *`Note on lens: A '<theme>' analogy distorts <concept>; falling back to '<accurate-theme>' (<objects>) for honest mechanics.`*

---

## Quality Audit Checklist

Before outputting the debrief, prune and verify against [failure-modes.md](./references/failure-modes.md):

- [ ] **Word Budget Respected:** Explanatory prose is under 150 words (excluding diagram block and headings; hard ceiling 220 total words).
- [ ] **No Preamble or Pleasantry:** Starts directly with the first section heading; zero chat filler.
- [ ] **No Banned Buzzwords:** Contains zero instances of *"basically"*, *"simply"*, *"obviously"*, *"trivial"*, *"optimized"*, *"streamlined"*, or *"abstracted away"*.
- [ ] **Sensory Verbs:** Uses mechanical, physical verbs (*pushes, catches, holds, drops, waits, locks*) rather than corporate hand-waving (*orchestrates, streamlines, optimizes*). See [voice.md](./references/voice.md).
- [ ] **ASCII Mechanism Flow:** Contains a fenced pure-ASCII flow mapping physical analogy objects in `[ ]` to code mechanisms in `( )` underneath.
- [ ] **Complete Ladder:** Contains exactly 3 single-line rungs: Level 0 (Plain), Level 1 (Code & trade-offs), and Level 2 (Invariants & failure modes).
- [ ] **Analogy Limits Named:** States the exact boundary where the mental model breaks.
- [ ] **The "Planes Don't Land" Test:** Does the change solve the actual causal problem, or is it just defensive scaffolding?

---

## Always-On Project Rule

To enforce Feynman debriefs repository-wide across every session without relying on session memory, add this block to your repository's `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`:

```markdown
## Post-Implementation Debrief
Whenever you complete a feature implementation, bug fix, or significant code modification, conclude your response with a lean Feynman Debrief (< 150 words prose, zero conversational preamble):
1. In One Sentence: The physical delta without buzzwords (1 sentence).
2. The Tangible Picture: One mechanical analogy and where the picture breaks, with an ASCII mechanism flow diagram (1-2 sentences).
3. The Ladder: Exactly 3 single-line rungs: Level 0 (zero jargon) -> Level 1 (code & trade-offs) -> Level 2 (failure modes & scale ceilings).
4. What Was Left Out: Deferred concerns and assumptions (1 line).
5. Lens Footer: Suggest alternative lenses.
If the change is trivial (pure docs, lockfiles, formatting), output a 1-line note and append:
`[Simplifeyn debrief skipped: cosmetic/trivial change without causal mechanism shift]`
```

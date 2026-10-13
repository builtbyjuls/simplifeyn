---
name: simplifeyn
description: >-
  Explains code changes, PR diffs, or completed feature implementations using the Richard Feynman technique:
  physical mechanism first, tangible everyday analogy with explicit breaking points, and an audience-calibrated
  ladder (defaults to vibe-coder prompt safety; supports junior-dev and senior-dev lenses, or --full). Use when the user
  asks "what did you do?", "explain the changes", during PR reviews, or after completing code implementations.
  Supports toggleable session mode via /simplifeyn on|off|status.
license: MIT
metadata:
  tags: "code-explanation, feynman-technique, git-diff, code-review, learning"
  category: "developer-tools"
---

# Simplifeyn: Implementation Debrief

An Agent Skill that turns software changes and PR diffs into clear, mechanistic explanations modeled on Richard Feynman's principles of understanding: **mechanism before name**, **one tangible analogy with its exact limits**, and an **audience-calibrated ladder from vibe coder to system maintainer**.

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
   - Debrief only the latest diff or specified code change without changing persistent session state (defaults to `vibe-coder` audience).
5. **Audience Lens Selection (`/simplifeyn for <audience>` or `/simplifeyn --for=<audience>`):**
   - Calibrate the debrief to a specific audience role (`vibe-coder`, `junior-dev`, `senior-dev`). Defaults to `vibe-coder`.
   - Can be combined with persistent mode or themes: `/simplifeyn for senior-dev as transit`.
6. **Themed Lens Selection (`/simplifeyn as <theme>` or `/simplifeyn --as=<theme>`):**
   - Direct the debrief to draw analogies from a specific physical domain (`kitchen`, `warehouse`, `workshop`, `transit`, `office`, `gaming`).
   - Also supported with persistence: `/simplifeyn on as <theme>` (or `/simplifeyn on --as=<theme>`).
7. **One-Turn Skip (`/simplifeyn skip` or `--no-debrief`):**
   - Suppress the debrief for the current turn without disabling persistent session mode.
8. **Targeted Micro-Commands (`/simplifeyn theme <theme>` and `/simplifeyn ladder <role>`):**
   - `/simplifeyn theme <theme>`: Generate and output ONLY Section 2 (The Tangible Picture & ASCII diagram) for the specified theme without repeating invariant sections.
   - `/simplifeyn ladder <role>`: Generate and output ONLY Section 3 (The Ladder) targeted rung for the specified role (vibe-coder, junior-dev, senior-dev, or --full).

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
1. **Documentation, Lockfiles, and Ignores Only:** Changes touch only documentation (`.md`, `.txt`, `.rst`), package lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`), or repository ignores (`.gitignore`, `.editorconfig`, `LICENSE`).
2. **Cosmetic and Styling:** Pure formatting, whitespace changes, or comment-only edits with zero modifications to executable statements.
3. **Conventional Commit Signals:** Commits prefixed with `docs:`, `chore:`, or `style:`.

> **Note on Code & Config:** Code and configuration files are **never skipped by size**. Even a 1-line edit to logic, conditions (`age >= 18` vs `age > 18`), arithmetic (`+` vs `-`), timeouts (`timeout = 0`), permissions (`chmod 0o777`), user privileges (`USER root`), or URLs (`http` vs `https`) alters runtime behavior and warrants a debrief.

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

1. **Inspect the Diff & Project Surface:**
   Run `git diff` (e.g. `git diff HEAD~1` or `git diff --cached`) directly in the project repository as the primary method. If `simplifeyn` is installed or cloned, you can alternatively locate and execute `get-diff.sh` (e.g. `$(find ~/.gemini/config/skills ~/.gemini/skills ~/.claude/skills ~/.agents/skills -name get-diff.sh 2>/dev/null | head -n1)` or `<skill-dir>/scripts/get-diff.sh`), which prints `=== Project Context ===` (detecting whether the project has a Web/UI App, Headless Backend, CLI Tool, etc.).
   **Ground Against Project Memory:** Always check project memory and rules files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`) if present. If project memory explicitly notes that certain surfaces (like dashboards, UI, streaming frontends) are deferred, or if the project surface indicates a headless backend or CLI without a UI, NEVER hallucinate phantom dashboards, browser previews, or upload buttons. Ground all verification actions in the actual system surface.
2. **Isolate the Causal Mechanism:**
   Ask: *If electricity and bits were physical water or gears, what physically moved differently before vs. after this change?*
3. **Format the Response:**
   Follow the **Core Debrief Structure** below strictly.
4. **Run the Pre-Send Audit:**
   Verify the debrief against the [Quality Audit Checklist](#quality-audit-checklist). When running in CLI or CI environments, execute `python3 scripts/audit_debrief.py` to programmatically validate the debrief format.
   > **Note on Linter Scope:** The audit script verifies structural sections, word count bounds, banned crutches, and format rules (heuristic form check). It does not evaluate the factual accuracy of domain claims.

---

## Brevity and Conciseness Constraints

This skill is called Simplifeyn: it must simplify, not generate an essay. Follow these strict bounds:

1. **Hard Word Budget:** Target under 170 words of explanatory prose (excluding markdown headers and fenced ASCII flow blocks; hard ceiling: 250 words total). Must fit in a single terminal viewport without scrolling.
2. **No Preamble, No Recap, No Closing Pleasantries:**
   - Forbidden openers: "Sure!", "Here is what changed:", "I have implemented...", "Looking at the changes..."
   - Forbidden closers: "Hope this helps!", "Let me know if you need anything else.", "Feel free to ask."
   - Start immediately with the first heading (Section 1). Conclude after Section 6 (What Was Left Out) and the lens exploration footer without conversational sign-offs.
3. **One Sentence / Bullet Cap:** Every section has a strict length limit:
   - In One Sentence: Exactly 1 sentence.
   - The Picture & Where the Picture Breaks: 1 to 2 sentences total, accompanied by a compact 2-5 line ASCII mechanism flow diagram (`[ Input ] ---> [ Guard ] ---> [ Output ]`).
   - The Ladder: 1 targeted single-line rung for active audience (default vibe-coder: `- **Level (Vibe Coder):** ...`), or exactly 3 rungs if full ladder mode is requested (--full). Do NOT output 3 rungs unless --full is requested.
   - The Screen Test / The Ice-Water Test: Exactly 1 physical sensory action (1 sentence; in-browser/preview if Web UI exists, or 1-line curl/command/log check if headless).
   - The Danger Zone / Where the Machine Snaps: Exactly 1-2 sentences naming boundary limits and stopping conditions (safe boundary or protective guardrail; zero unprompted feature tasks).
   - What Was Left Out: Exactly 1 line.

---

## Core Debrief Structure

Output the debrief using this compact structure:

### 1. In One Sentence
State what the system physically does differently now in exactly 1 sentence. Zero filler words ("basically", "simply", "obviously").

### 2. The Tangible Picture
Provide one sensory physical analogy and state Where the Picture Breaks in 1 to 2 sentences total. Include a compact 2 to 5 line ASCII mechanism flow diagram mapping the physical components to code mechanisms using pure ASCII characters (`--->`, `|`, `v`, `[ ]`):
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
Deliver the explanation calibrated to the active audience level. By default, Simplifeyn calibrates for the **vibe-coder** audience and provides exactly 1 targeted single-line rung:
- **Level (Vibe Coder):** 1 sentence. Focuses on what changes on screen or in user flow, how components connect, and what prompt to avoid next without confusing syntax or abstract buzzwords.

> **CRITICAL RULE:** Do NOT output 3 rungs by default. Output ONLY the 1 targeted rung for the active audience (`- **Level (Vibe Coder):** ...`). Provide all 3 progressive rungs (`Level 0` -> `Level 1` -> `Level 2`) ONLY if the user explicitly requested `/simplifeyn --full`.

When invoked for another audience (e.g. `/simplifeyn for junior-dev` or `/simplifeyn for senior-dev`), provide the single targeted rung for that level:
- **Level (Junior Dev):** 1 sentence. Code symbols, data structures, and the fundamental programming patterns at play.
- **Level (Senior Dev):** 1 sentence. Invariants, concurrency boundaries, latency/memory trade-offs, and scale ceilings.

If full ladder mode is requested (`/simplifeyn --full`), provide all 3 progressive single-line rungs (Level 0 / Vibe Coder -> Level 1 / Junior Dev -> Level 2 / Senior Dev).

### 4. The Screen Test (or The Ice-Water Test)
State exactly 1 sensory action the user can take right now to observe the mechanism in action:
- **For Vibe Coders (Default):**
  - **When Web UI exists:** Use heading `### 4. The Screen Test` -- a tangible, no-code action in the app preview or browser (e.g. toggle Wi-Fi, click a preview button, observe visual loading countdown) rather than terminal commands or DevTools panels.
  - **When Headless Backend / API / CLI (No UI):** Use heading `### 4. The Ice-Water Test` (or `### 4. The Screen Test` without phantom UI) -- provide a concrete 1-line command or verification action (e.g. run a 1-line `curl` command with sample payload, trigger a CLI command, or check application output logs). **Zero hallucinated dashboards, preview forms, or browser buttons.** Ground the verification entirely in the actual project surface and respect deferred boundaries in project memory.
- **For Junior & Senior Devs:** Use heading `### 4. The Ice-Water Test` -- a direct DevTools, curl, or test execution command.

### 5. The Danger Zone (Prompt Safety) (or Where the Machine Snaps)
State the physical boundary limit or failure condition:
- **For Vibe Coders (Default):** Use heading `### 5. The Danger Zone (Prompt Safety)`:
  - `- What Can Break:` Name the real-world product or system failure consequence in plain English (e.g. charging customers twice, hanging on dead servers, fluttering sensors flooding the alerts table). Zero abstract engineering terms.
  - **Stopping Condition vs. Guardrail:**
    - If the implementation is complete and safe for current scale: state `- Safe Boundary: Safe to leave as-is for normal traffic. No further prompt needed.`
    - If future prompts could easily regress this: state `- Guardrail (If Prompting Next): [protective constraint to mention if the user ever modifies this area in future turns]`.
    - **CRITICAL - Zero Unprompted Backlog:** Never prescribe a new feature or task as a mandatory next step. Never force an infinite prompt-stacking loop by telling the user what feature to build next.
- **For Junior & Senior Devs:** Use heading `### 5. Where the Machine Snaps` -- state the exact code mechanism limit in 1 sentence (concurrency race, memory ceiling, unindexed database bottleneck, missing idempotency keys).

### 6. What Was Left Out
State what was intentionally simplified or deferred in 1 line.

Conclude with a single tight exploration footer suggesting the other 2 audience lenses and alternative theme lenses:
`Explore other lenses: /simplifeyn for <other-role-1> | for <other-role-2> | as <theme>`

See [worked-examples.md](./assets/worked-examples.md) for full before-and-after exemplar debriefs.

---

## Dynamic Audience Lenses

Simplifeyn supports dynamic audience calibration using `/simplifeyn for <audience>` or `--for=<audience>`:

1. **vibe-coder (Default):** Calibrated for creators directing AI agents through natural conversation. 100% free of engineering jargon (*POST, mutating, idempotency, endpoints, 4xx/5xx, telemetry, jitter, rethrowing, DevTools*). Focuses on screen behavior, plain-English user risks, and actionable prompts to keep the AI on rails.
2. **junior-dev:** Calibrated for learners mastering codebase patterns. Focuses on exact code symbols, function roles, syntax structures, and core programming concepts.
3. **senior-dev:** Calibrated for systems maintainers. Focuses on invariants, concurrency boundaries, scale ceilings, and edge-case transport/state failures.

---

## Themed Analogy Lenses & Fallback Rules

Users can select a preferred physical domain using `--as=<theme>` or `/simplifeyn as <theme>` (`kitchen`, `warehouse`, `workshop`, `transit`, `office`, `gaming`). See [analogies.md](./references/analogies.md) for catalog definitions.

### The Analogy Fit Check & Fallback Rule
1. **Strong Fit:** If the requested lens naturally maps to the causal mechanics, use it.
2. **Poor Fit / Distortion:** If the requested lens would obscure the code or require misleading mental acrobatics, **do not fake it**.
3. **The Fallback Note:** State the reason honestly in 1 line and fall back to the accurate domain:
   *`Note on lens: A '<theme>' analogy distorts <concept>; falling back to '<accurate-theme>' (<objects>) for honest mechanics.`*

---

## Invariant Anchoring Protocol (Same Commit Preservation)

When the user re-invokes `/simplifeyn` on the **same commit** with a different lens or theme (e.g. `/simplifeyn as transit` after `/simplifeyn for junior-dev`), prevent semantic drift across factual sections:

1. **Anchor to the Prior Debrief:**
   - Anchor to the previous debrief in the active conversation history.
   - Do NOT re-analyze the commit from scratch or invent new wording for sections that are immutable facts of the code change.
2. **Commit Invariants (Frozen Sections):**
   - **Section 1 (In One Sentence):** The physical delta is an immutable fact of the commit. Keep it identical to the prior debrief.
   - **Section 4 (The Screen Test / The Ice-Water Test):** The physical verification action is grounded in the codebase and does not change when changing metaphor.
   - **Section 5 (The Danger Zone / Where the Machine Snaps):** The code stress boundary or safe limit does not change when changing metaphor.
   - **Section 6 (What Was Left Out):** The deferred architectural scope is an immutable fact of the commit. Keep it identical to the prior debrief.
3. **Variant Sections (What Changes):**
   - **Theme Switch (`as <theme>` or `/simplifeyn theme <theme>`):** ONLY regenerate Section 2 (The Tangible Picture & ASCII diagram). Keep Section 1, 4, 5, and 6 word-for-word identical to the prior debrief.
   - **Audience Switch (`for <role>` or `/simplifeyn ladder <role>`):** ONLY swap Section 3 (The Ladder), while re-framing Section 4 and 5 in that role's vocabulary. Keep Section 1 and Section 6 identical.

---

## Quality Audit Checklist

Before outputting the debrief, prune and verify against [failure-modes.md](./references/failure-modes.md):

- [ ] **Word Budget Respected:** Explanatory prose is under 170 words (excluding diagram block and headings; hard ceiling 250 total words).
- [ ] **No Preamble or Pleasantry:** Starts directly with the first section heading; zero chat filler.
- [ ] **No Banned Buzzwords:** Contains zero instances of hand-waving crutches or empty buzzwords listed in [banned-words.txt](./references/banned-words.txt) (*basically*, *simply*, *just*, *obviously*, *trivial*, *optimized*, *streamlined*, *under the hood*, *seamless*, *self-explanatory*, *abstracted away*).
- [ ] **Sensory Verbs:** Uses mechanical, physical verbs (*pushes, catches, holds, drops, waits, locks*) rather than corporate hand-waving (*orchestrates, streamlines, optimizes*). See [voice.md](./references/voice.md).
- [ ] **ASCII Mechanism Flow:** Contains a fenced pure-ASCII flow mapping physical analogy objects in `[ ]` to code mechanisms in `( )` underneath.
- [ ] **Calibrated Ladder Included:** Contains either 1 targeted single-line rung for the active audience level (Vibe Coder, Junior Dev, Senior Dev) or all 3 rungs for full ladder mode.
- [ ] **Analogy Limits Named:** States the exact boundary where the mental model breaks.
- [ ] **Surface Grounding Respected:** Verification action matches the real project surface (browser preview for Web UI; curl, CLI command, or log check for headless backends/APIs). Zero hallucinated UI dashboards or phantom buttons.
- [ ] **The Ice-Water Test Included:** Contains exactly 1 physical action in the browser, terminal, or DevTools to observe the mechanism in action.
- [ ] **Where the Machine Snaps Included:** Identifies the exact code failure boundary under load, concurrency, or subsequent modifications.
- [ ] **The "Planes Don't Land" Test:** Does the change solve the actual causal problem, or is it just defensive scaffolding?

---

## Always-On Project Rule

To enforce Feynman debriefs repository-wide across every session without relying on session memory, add this block to your repository's `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`:

```markdown
## Post-Implementation Debrief
Whenever you complete a feature implementation, bug fix, or significant code modification, conclude your response with a lean Feynman Debrief (< 170 words prose, zero conversational preamble):
1. In One Sentence: The physical delta without buzzwords (1 sentence).
2. The Tangible Picture: One mechanical analogy and where the picture breaks, with an ASCII mechanism flow diagram (1-2 sentences).
3. The Ladder: 1 targeted single-line rung for active audience (default vibe-coder: Level (Vibe Coder)) or all 3 progressive rungs if requested with --full (Level 0 -> Level 1 -> Level 2).
4. The Screen Test (or The Ice-Water Test for dev audiences): 1 physical action in browser/preview or terminal to observe the mechanism (1 sentence).
5. The Danger Zone (Prompt Safety) (or Where the Machine Snaps for dev audiences): What Can Break and Safe Boundary / Guardrail (1-2 sentences).
6. What Was Left Out: Deferred concerns and assumptions (1 line).
7. Lens Footer: Suggest alternative lenses.
If the change is trivial (pure docs, lockfiles, formatting), output a 1-line note and append:
`[Simplifeyn debrief skipped: cosmetic/trivial change without causal mechanism shift]`
```

# Simplifeyn (`simplifeyn`)

[![Agent Skills Standard](https://img.shields.io/badge/Agent%20Skills-Standard-blue.svg)](https://agentskills.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![CI](https://github.com/builtbyjuls/simplifeyn/actions/workflows/ci.yml/badge.svg)](https://github.com/builtbyjuls/simplifeyn/actions/workflows/ci.yml)

> **An Agent Skill that explains code changes, PR diffs, and feature implementations the way Richard Feynman explained physics: physical mechanism first, one honest everyday analogy with its exact limits, and a ladder from kitchen-table simplicity to maintainer edge cases.**

Compatible with **Claude Code**, **Google Antigravity CLI**, **OpenAI Codex CLI**, **Cursor**, and any tool supporting the [Agent Skills open standard](https://agentskills.io).

---

## The Problem with AI Code Summaries

When AI agents implement features or fix bugs, they default to reciting files and jargon:

> *"I updated `UserService` to inject an LRU cache with eviction policies and wrapped the query in thread-safe locks, optimizing latency and streamlining database interactions."*

**Why this fails:**
1. **Recites names instead of physical causality:** It tells you what classes exist, not what actually moves under the hood.
2. **Hides trade-offs and limits:** It pretends the solution has zero costs or memory overhead.
3. **Alienates reviewers:** Teammates, junior developers, and product managers can't evaluate whether the mental model is sound.

---

## The Simplifeyn Alternative

`simplifeyn` forces the AI coding agent into Richard Feynman's cognitive model while enforcing strict brevity (< 150 prose words, zero conversational filler):

1. **In One Sentence:** The physical delta in plain language (1 sentence). Zero buzzwords (`basically`, `simply`, `optimized`, `streamlined`).
2. **The Tangible Picture & Limits:** One sensory, mechanical analogy, ASCII flow diagram, and its breaking limit in the same breath (1-2 sentences).
3. **The Ladder:** Exactly 3 tight, single-line bullets:
   * **Level 0 (Kitchen Table):** Zero jargon. Understandable by a non-technical stakeholder or curious 10-year-old.
   * **Level 1 (Practitioner):** Code mechanics, data structures, state transitions, and real-world trade-offs.
   * **Level 2 (Maintainer):** Failure modes, invariants, concurrency, scale ceilings, and rejected alternative approaches.
4. **The Ice-Water Test:** 1 physical sensory action in the browser, terminal, or DevTools to watch the mechanism work right now (1 sentence).
5. **What Was Left Out:** Explicitly names what was simplified or deferred in 1 line.

### The Feynman Philosophy: The "Ice-Water Test"

During the 1986 Rogers Commission hearing investigating the Space Shuttle Challenger disaster, NASA officials and contractors presented dense statistical models and hundreds of pages of engineering jargon. Richard Feynman cut through the noise with a single physical experiment: he clamped a piece of the shuttle's rubber O-ring and dunked it into a simple glass of ice water sitting on his desk. When unclamped, the cold rubber remained stiff and failed to recover.

Feynman lived by the experimental principle:
> *"It doesn't matter how beautiful your theory is, it doesn't matter how smart you are. If it doesn't agree with experiment, it's wrong."*

For developers and vibe coders directing AI coding agents, theoretical explanations ("optimizes lifecycle execution with debounced mutations") are useless without physical verification. **The Ice-Water Test** requires the AI to give you one concrete, 10-second sensory action (e.g., throttling DevTools to offline, clicking twice rapidly, inspecting a network panel) so you can witness the physical mechanism with your own eyes.

### Brevity & Anti-Verbosity Constraints
- **Word Budget:** Target < 150 words of explanatory prose (excluding diagram block & headings; hard ceiling 220 total words). Fits completely in a standard terminal viewport without scrolling.
- **Zero Chat Filler:** No preambles ("Sure!", "Here is what changed:"), no postambles ("Hope this helps!"). Starts directly with the first section heading and stops after the last bullet.

**-> [See a complete Before vs. After Worked Example](./assets/worked-examples.md)**

---

## Installation

### Quick Install (One-Liner)

Install directly to your coding assistant with zero cloning:

```bash
# Latest main:
curl -fsSL https://raw.githubusercontent.com/builtbyjuls/simplifeyn/main/install.sh | bash

# Pinned release (v0.1.0):
curl -fsSL https://raw.githubusercontent.com/builtbyjuls/simplifeyn/v0.1.0/install.sh | bash
```

Or target a specific client via pipe:

```bash
curl -fsSL https://raw.githubusercontent.com/builtbyjuls/simplifeyn/main/install.sh | bash -s -- --claude
curl -fsSL https://raw.githubusercontent.com/builtbyjuls/simplifeyn/main/install.sh | bash -s -- --antigravity
```

### From Source

Clone and run the installer:

```bash
git clone https://github.com/builtbyjuls/simplifeyn.git /tmp/simplifeyn
cd /tmp/simplifeyn

# Auto-detect your installed tools and install
./install.sh

# Or target a specific client:
./install.sh --antigravity   # Installs to ~/.gemini/skills/
./install.sh --claude        # Installs to ~/.claude/skills/
./install.sh --codex         # Installs to ~/.agents/skills/
./install.sh --cursor        # Installs to ~/.cursor/skills/
./install.sh --project       # Installs to current repo: .agents/skills/
```

### Manual Drop-in (One Folder)

Copy the `simplifeyn` folder into whichever skill directory your CLI uses:

* **Antigravity CLI:** `~/.gemini/skills/simplifeyn/`
* **Claude Code:** `~/.claude/skills/simplifeyn/`
* **OpenAI Codex CLI:** `~/.agents/skills/simplifeyn/`
* **Cursor:** `~/.cursor/skills/simplifeyn/`

> [!NOTE]
> Installation paths for Cursor (`~/.cursor/skills`), Codex (`~/.agents/skills`), and Antigravity (`~/.gemini/skills`) reflect typical convention across multi-agent environments but may vary depending on CLI version. In addition, while the target budget is under 150 prose words, complex real-world diffs may expand up to the hard ceiling of 220 words.

---

## Usage

### Mode 1: Toggleable Session Mode (Recommended)

Turn Feynman debriefing on or off dynamically during your session:

```bash
# Turn ON: every subsequent code change will conclude with a Feynman Debrief
/simplifeyn on

# Check whether debrief mode is currently active
/simplifeyn status

# Turn OFF: return to normal output style
/simplifeyn off

# Skip the debrief for the current turn only (while leaving persistent mode active):
/simplifeyn skip
```

> **Note on Session State:** Agent Skills provide instructions to your AI coding agent, not an OS background process. Mode 1 is an in-session instruction (best-effort across long context windows). For a guaranteed, repository-wide rule across all sessions and agent restarts, use **Mode 4: Always-On Project Rule** below.

### Complexity Gating: When Debriefs Run vs. Skip

Simplifeyn avoids over-explaining trivial edits (like pure documentation or lockfile updates). The skill applies automatic complexity gating:

* **Skipped (`[Simplifeyn debrief skipped: cosmetic/trivial change without causal mechanism shift]`):**
  - Docs, Lockfiles & Ignores: Changes touching only `.md`, `.txt`, `.rst`, lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`), or repository ignores (`.gitignore`, `.editorconfig`, `LICENSE`).
  - Cosmetic: Formatting, whitespace changes, or comment-only revisions with zero executable code modifications.
  - Conventional commits: Commits prefixed with `docs:`, `chore:`, or `style:`.
* **Debriefed:**
  - Code & Config files are **never skipped by size**: Even 1-line changes to timeouts (`timeout = 0`), retries (`max_retries = 0`), arithmetic (`+` vs `-`), index math (`len(xs) - 1`), bounds (`>=` vs `>`), permissions (`0o777`), users (`USER root`), shell flags (`set +e`), or protocols (`http` vs `https`) alter runtime behavior and trigger a debrief.
  - Causal mechanism shifts: Data flows through different paths, buffers, or states.
  - Concurrency & Performance: Caching, locks, retries, jitter, debounce, or race conditions.
  - New features & refactors: New endpoints, state machines, business logic.
  - Security & Runtime Configs: Altering auth flags (`AUTH_REQUIRED`), SSL/TLS settings, permissions, or CI test steps.
  - Conventional commits: `feat:`, `perf:`, non-trivial `fix:`, structural `refactor:`.
  - Explicit invocation: `/simplifeyn` or user asks for explanation.


### Mode 2: Themed Lenses (`as <theme>` or `--as=<theme>`)

Direct the debrief toward a specific physical domain (`kitchen`, `warehouse`, `workshop`, `transit`, `office`, `gaming`):

```bash
# One-shot with specific lens:
/simplifeyn as kitchen
/simplifeyn --as=warehouse
/simplifeyn HEAD~1 as transit

# Persistent mode locked to a lens:
/simplifeyn on as workshop
```

If a requested lens fundamentally distorts the code mechanism, Simplifeyn enforces Feynman honesty: it outputs a 1-line disclaimer and falls back to the accurate domain.

### Mode 3: One-Shot Command

Run once for the latest change or a specific commit without enabling session persistence:

```bash
/simplifeyn
# or for a specific commit:
/simplifeyn HEAD~1
```

Or ask the agent in plain language:
> *"Explain what you just implemented using the Feynman technique."*

### Mode 4: Always-On Project Rule

If you want your agent to conclude **every** feature implementation or bug fix with a Feynman Debrief automatically across the whole repo, add this block to your project's `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`:

```markdown
## Post-Implementation Debrief
Whenever you complete a feature implementation, bug fix, or significant code modification, conclude your final response with a lean Feynman Debrief (< 150 words, zero pleasantries or preamble):
1. In One Sentence: The physical delta without buzzwords (1 sentence).
2. The Tangible Picture: One mechanical analogy and where the picture breaks (1-2 sentences).
3. The Ladder: 3 single-line rungs: Level 0 (zero jargon) -> Level 1 (practitioner) -> Level 2 (maintainer).
4. The Ice-Water Test: 1 physical action in the app/terminal to watch the mechanism work (1 sentence).
5. What Was Left Out: Deferred concerns and assumptions (1 line).
```

---

## Quality Linter & Test Suite

This repository is built with **Test-Driven Development (TDD)** and includes an automated audit linter to verify that explanations adhere to Feynman principles:

> **Scope of the Linter:** The linter verifies structural sections, word count boundaries, banned buzzwords, and stylistic tone (heuristic form check). It does not evaluate the factual domain accuracy of technical claims.

```bash
# Run the test suite
python3 -m unittest discover tests

# Audit an explanation draft
python3 scripts/audit_debrief.py my_explanation.md
# Or via pipe:
cat response.txt | python3 scripts/audit_debrief.py --stdin

# Check if a git diff warrants a debrief (Complexity Gating)
python3 scripts/audit_debrief.py --check-diff git_diff.patch
# Or pass commit message to test conventional commit heuristics:
python3 scripts/audit_debrief.py --check-diff --commit-msg "docs: update guide" git_diff.patch
```

---

## Repository Structure

```text
simplifeyn/
|-- SKILL.md                  # Main Agent Skill specification
|-- README.md                 # Documentation and guide
|-- install.sh                # Universal installer
|-- LICENSE                   # MIT License
|-- references/
|   |-- voice.md              # Style forensics, banned buzzwords, sensory verbs
|   |-- analogies.md          # Reference catalog of computing analogies & breaking points
|   |-- ladder.md             # Multi-tier calibration (Kitchen Table -> Maintainer)
|   \-- failure-modes.md      # 5 critical ways technical explanations fail & fixes
|-- assets/
|   \-- worked-examples.md    # Real PR diff with Before/After contrast
|-- scripts/
|   |-- audit_debrief.py      # Automated linter against lazy jargon
|   \-- get-diff.sh           # Git diff extractor helper
\-- tests/                    # Automated TDD test suite
```

---

## Contributing

Contributions and feedback are welcome! Areas to explore:
- New physical analogies and breaking points added to `references/analogies.md`.
- Real-world worked examples in `assets/worked-examples.md`.
- Additional edge case tests in `tests/`.

---

## License

[MIT](./LICENSE) (c) 2026 Julius. Use it, fork it, ship it.

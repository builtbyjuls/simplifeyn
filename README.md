# Simplifeyn (`simplifeyn`)

[![Agent Skills Standard](https://img.shields.io/badge/Agent%20Skills-Standard-blue.svg)](https://agentskills.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![CI](https://github.com/builtbyjuls/simplifeyn/actions/workflows/ci.yml/badge.svg)](https://github.com/builtbyjuls/simplifeyn/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](./tests)

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

`simplifeyn` forces the AI coding agent into Richard Feynman's cognitive model while enforcing strict brevity (< 150 words total, zero conversational filler):

1. **In One Sentence:** The physical delta in plain language (1 sentence). Zero buzzwords (`basically`, `simply`, `optimized`).
2. **The Tangible Picture & Limits:** One sensory, mechanical analogy and its breaking limit in the same breath (1-2 sentences).
3. **The Ladder:** Exactly 3 tight, single-line bullets:
   * **Level 0 (Kitchen Table):** Zero jargon. Understandable by a non-technical stakeholder or curious 10-year-old.
   * **Level 1 (Practitioner):** Code mechanics, data structures, state transitions, and real-world trade-offs.
   * **Level 2 (Maintainer):** Failure modes, invariants, concurrency, scale ceilings, and rejected alternative approaches.
4. **What Was Left Out:** Explicitly names what was simplified or deferred in 1 line.

### Brevity & Anti-Verbosity Constraints
- **Word Budget:** Hard cap under 150 words total; fits completely in a standard terminal viewport without scrolling.
- **Zero Chat Filler:** No preambles ("Sure!", "Here is what changed:"), no postambles ("Hope this helps!"). Starts directly with the first section heading and stops after the last bullet.

**-> [See a complete Before vs. After Worked Example](./assets/worked-examples.md)**

---

## Installation

### Quick Install (One-Liner)

Install directly to your coding assistant with zero cloning:

```bash
curl -fsSL https://raw.githubusercontent.com/builtbyjuls/simplifeyn/main/install.sh | bash
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

### 2. Manual Drop-in (One Folder)

Copy the `simplifeyn` folder into whichever skill directory your CLI uses:

* **Antigravity CLI:** `~/.gemini/skills/simplifeyn/`
* **Claude Code:** `~/.claude/skills/simplifeyn/`
* **OpenAI Codex CLI:** `~/.agents/skills/simplifeyn/`
* **Cursor:** `~/.cursor/skills/simplifeyn/`

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
```

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
4. What Was Left Out: Deferred concerns and assumptions (1 line).
```

---

## Quality Linter & Test Suite

This repository is built with **Test-Driven Development (TDD)** and includes an automated audit linter to verify that explanations adhere to Feynman principles:

```bash
# Run the test suite
python3 -m unittest discover tests

# Audit an explanation draft
python3 scripts/audit_debrief.py my_explanation.md
# Or via pipe:
cat response.txt | python3 scripts/audit_debrief.py --stdin
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

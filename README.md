# Simplifeyn (`simplifeyn`)

[![Agent Skills Standard](https://img.shields.io/badge/Agent%20Skills-Standard-blue.svg)](https://agentskills.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![CI](https://github.com/builtbyjuls/simplifeyn/actions/workflows/ci.yml/badge.svg)](https://github.com/builtbyjuls/simplifeyn/actions/workflows/ci.yml)

> **An Agent Skill that explains code changes, PR diffs, and feature implementations the way Richard Feynman explained physics: physical mechanism first, one honest everyday analogy with its exact limits, and an audience-calibrated ladder from vibe coder to system maintainer.**

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

`simplifeyn` forces the AI coding agent into Richard Feynman's cognitive model while enforcing strict brevity (< 170 prose words, zero conversational filler):

1. **In One Sentence:** The physical delta in plain language (1 sentence). Zero buzzwords (`basically`, `simply`, `optimized`, `streamlined`).
2. **The Tangible Picture & Limits:** One sensory, mechanical analogy, ASCII flow diagram, and its breaking limit in the same breath (1-2 sentences).
3. **The Ladder:** Calibrated to the active audience (defaults to 1 targeted single-line rung; all 3 rungs with `--full`):
   * **Level (Vibe Coder):** (Default) App behavior, state/event flow, and prompt-stacking safety without syntax jargon.
   * **Level (Junior Dev):** Code symbols, data structures, and foundational programming patterns.
   * **Level (Senior Dev):** Invariants, concurrency boundaries, latency/memory trade-offs, and scale ceilings.
4. **The Ice-Water Test:** 1 physical sensory action in the browser, terminal, or DevTools to watch the mechanism work right now (1 sentence).
5. **Where the Machine Snaps:** The exact code stress boundary, concurrency race, or prompt-stacking failure limit (1 sentence).
6. **What Was Left Out:** Explicitly names what was simplified or deferred in 1 line.

### The Feynman Philosophy: Experiments & Physical Boundaries

Richard Feynman's approach to science and engineering rested on two immutable foundations:

1. **The Physical Experiment ("The Ice-Water Test"):** During the 1986 Rogers Commission hearing on the Challenger disaster, NASA officials presented dense statistical risk models. Feynman cut through the bureaucratic fog with a simple tabletop experiment: he clamped a sample of the shuttle's rubber O-ring seal and dunked it into a glass of ice water at his desk. When released, the stiff rubber failed to rebound. In under ten seconds, everyone saw the causal truth.
   > *"It doesn't matter how beautiful your theory is, it doesn't matter how smart you are. If it doesn't agree with experiment, it's wrong."*
   For vibe coders directing AI coding agents, theoretical jargon ("optimizes mutation lifecycle") is unprovable without physical verification. **The Ice-Water Test** requires the AI to give you one concrete, 10-second sensory action (e.g., throttling DevTools to offline, clicking twice rapidly, inspecting a network panel) to witness the mechanism work.

2. **The Boundary Condition ("Where the Machine Snaps"):** Feynman taught that an engineer does not understand a physical machine until they know the exact conditions under which it ceases to work. In the Challenger investigation, the O-ring was not flawed in general; it lost elasticity specifically below 32 deg F (0 deg C).
   In software, while *Where the Picture Breaks* defines the limits of the everyday metaphor, **Where the Machine Snaps** identifies the physical stress threshold of the code itself. For vibe coders who build via iterative "prompt stacking", this prevents disaster: if the AI uses an in-memory dictionary or non-idempotent mutation, naming where the machine snaps alerts the developer before their next prompt triggers a catastrophic regression.

### Brevity & Anti-Verbosity Constraints
- **Word Budget:** Target < 170 words of explanatory prose (excluding diagram block & headings; hard ceiling 250 total words). Fits completely in a standard terminal viewport without scrolling.
- **Zero Chat Filler:** No preambles ("Sure!", "Here is what changed:"), no postambles ("Hope this helps!"). Starts directly with the first section heading and stops after the last bullet.

**-> [See a complete Before vs. After Worked Example](./assets/worked-examples.md)**

---

## Installation

### Via `skills.sh` Ecosystem (Recommended)

Install directly using the open Agent Skills ecosystem installer (`skills.sh`):

```bash
npx skills add builtbyjuls/simplifeyn
```

### From Source (Review First)

Clone and inspect the repository before running the local installer:

```bash
git clone https://github.com/builtbyjuls/simplifeyn.git
cd simplifeyn

# Auto-detect your installed tools and install
./install.sh

# Or target a specific client:
./install.sh --antigravity   # Installs to ~/.gemini/config/skills/
./install.sh --claude        # Installs to ~/.claude/skills/
./install.sh --codex         # Installs to ~/.agents/skills/
./install.sh --cursor        # Installs to ~/.cursor/skills/
./install.sh --project       # Installs to current repo: .agents/skills/
```

### Manual Drop-in (One Folder)

Copy the `simplifeyn` folder into whichever skill directory your CLI uses:

* **Antigravity CLI:** `~/.gemini/config/skills/simplifeyn/`
* **Claude Code:** `~/.claude/skills/simplifeyn/`
* **OpenAI Codex CLI:** `~/.agents/skills/simplifeyn/`
* **Cursor:** `~/.cursor/skills/simplifeyn/`

> [!NOTE]
> Installation paths for Cursor (`~/.cursor/skills`), Codex (`~/.agents/skills`), and Antigravity (`~/.gemini/config/skills`) reflect typical convention across multi-agent environments but may vary depending on CLI version. In addition, while the target budget is under 170 prose words, complex real-world diffs may expand up to the hard ceiling of 250 words.

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


### Mode 2: Audience Lenses (`for <audience>` or `--for=<audience>`)

Calibrate the debrief to your technical comfort level (`vibe-coder`, `junior-dev`, `senior-dev`):

```bash
# Defaults to vibe-coder (app behavior, prompt safety, 1 targeted ladder rung):
/simplifeyn

# Target learning junior engineers (code symbols, patterns, trade-offs):
/simplifeyn for junior-dev

# Target systems maintainers (invariants, concurrency, scale limits):
/simplifeyn for senior-dev

# Combine audience with a themed lens:
/simplifeyn for junior-dev as gaming
/simplifeyn for senior-dev as transit
```

### Mode 3: Themed Lenses (`as <theme>` or `--as=<theme>`)

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

### Invariant Anchoring Protocol (Same Commit Preservation)

When re-invoking `/simplifeyn` on the same commit with a different lens or theme (e.g. `/simplifeyn as transit` after `/simplifeyn for junior-dev`), Simplifeyn anchors to the prior debrief in conversation history to prevent semantic drift:
* **Frozen Invariants:** Section 1 (In One Sentence), Section 4 (Verification Test), Section 5 (Failure Limit), and Section 6 (What Was Left Out) remain immutable facts of the commit.
* **Variant Swap:** Switching theme (`as <theme>`) regenerates *only* Section 2 (The Tangible Picture & ASCII diagram). Switching audience (`for <audience>`) swaps *only* Section 3 (The Ladder) while re-framing Section 4 and 5 in that role's vocabulary.

### Mode 4: Targeted Micro-Commands

Inspect or swap individual sections without re-running the entire 6-section debrief:

```bash
# Output only a new Tangible Picture & ASCII diagram for a specific theme:
/simplifeyn theme transit
/simplifeyn theme warehouse

# Output only the targeted ladder rung for a specific audience:
/simplifeyn ladder junior-dev
/simplifeyn ladder senior-dev
```

### Mode 5: One-Shot Command

Run once for the latest change or a specific commit without enabling session persistence:

```bash
/simplifeyn
# or for a specific commit:
/simplifeyn HEAD~1
```

Or ask the agent in plain language:
> *"Explain what you just implemented using the Feynman technique."*

### Mode 6: Always-On Project Rule

If you want your agent to conclude **every** feature implementation or bug fix with a Feynman Debrief automatically across the whole repo, add this block to your project's `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`:

```markdown
## Post-Implementation Debrief
Whenever you complete a feature implementation, bug fix, or significant code modification, conclude your response with a lean Feynman Debrief (< 170 words prose, zero conversational preamble):
1. In One Sentence: The physical delta without buzzwords (1 sentence).
2. The Tangible Picture: One mechanical analogy and where the picture breaks, with an ASCII mechanism flow diagram (1-2 sentences).
3. The Ladder: 1 targeted single-line rung for active audience (default vibe-coder: Level (Vibe Coder)) or all 3 progressive rungs if requested with --full (Level 0 / Vibe Coder -> Level 1 / Junior Dev -> Level 2 / Senior Dev).
4. The Ice-Water Test: 1 physical action in the browser/terminal to observe the mechanism (1 sentence).
5. Where the Machine Snaps: 1 code boundary limit / prompt-stacking failure condition (1 sentence).
6. What Was Left Out: Deferred concerns and assumptions (1 line).
7. Lens Footer: Suggest alternative lenses.
If the change is trivial (pure docs, lockfiles, formatting), output a 1-line note and append:
`[Simplifeyn debrief skipped: cosmetic/trivial change without causal mechanism shift]`
```

### Mode 7: Automated GitHub Action PR Reviewer

Explain pull requests automatically using the Richard Feynman technique on every PR:

```yaml
# .github/workflows/simplifeyn.yml
name: Simplifeyn PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  feynman-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Simplifeyn PR Reviewer
        uses: builtbyjuls/simplifeyn@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          api-key: ${{ secrets.GEMINI_API_KEY || secrets.ANTHROPIC_API_KEY || secrets.OPENAI_API_KEY }}
          audience: 'vibe-coder'     # vibe-coder (default) | junior-dev | senior-dev | full
          skip-cosmetic: 'true'      # skips trivial doc/lockfile PRs automatically
          strict-audit: 'true'       # enforces < 170 words and zero buzzwords
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
|-- action.yml                # Reusable GitHub Action for PR reviews
|-- install.sh                # Universal installer
|-- LICENSE                   # MIT License
|-- references/
|   |-- voice.md              # Style forensics, banned buzzwords, sensory verbs
|   |-- analogies.md          # Reference catalog of computing analogies & breaking points
|   |-- ladder.md             # Audience calibration (Vibe Coder -> Junior -> Senior)
|   \-- failure-modes.md      # 5 critical ways technical explanations fail & fixes
|-- assets/
|   \-- worked-examples.md    # Real PR diff with Before/After contrast
|-- scripts/
|   |-- audit_debrief.py      # Automated linter against lazy jargon
|   |-- get-diff.sh           # Git diff extractor helper
|   \-- pr_reviewer.py        # GitHub Action PR Reviewer engine
\-- tests/                    # Automated TDD test suite
```

---

## Security & Capability Transparency

`simplifeyn` adheres strictly to the security expectations of the Agent Skills standard and Trust Hub audits:

1. **Zero Remote Execution (No Unreviewed Shell Piping):**
   - The repository does not provide, encourage, or execute unreviewed remote script piping from URLs into a shell.
   - `install.sh` operates 100% locally on existing files within a cloned repository and performs zero remote downloads or network calls.
2. **Read-Only Inspection:**
   - `scripts/get-diff.sh` only executes read-only git status and diff commands (`git rev-parse`, `git ls-files`, `git diff`, `git show`). It never modifies repository state, writes to untrusted locations, or touches the network.
3. **Offline AST Analysis:**
   - `scripts/audit_debrief.py` is a self-contained Python heuristic linter that analyzes text structure and string length. It has zero network connectivity and executes zero external subcommands during debrief analysis.
4. **Indirect Prompt Injection Defense:**
   - Ingested diff content is sandboxed within `<untrusted_diff>` and `</untrusted_diff>` boundary markers with nested tag escaping.
   - The skill instructions explicitly direct agents to treat diff data strictly as passive code, ignoring any embedded instructions, prompt injection overrides, or tool invocation requests.

---

## Contributing

Contributions and feedback are welcome! Areas to explore:
- New physical analogies and breaking points added to `references/analogies.md`.
- Real-world worked examples in `assets/worked-examples.md`.
- Additional edge case tests in `tests/`.

---

## License

[MIT](./LICENSE) (c) 2026 Julius. Use it, fork it, ship it.

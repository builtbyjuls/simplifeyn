# Calibration of the Feynman Debrief Ladder

The ladder is a multi-tier structure that communicates software changes across different technical audiences without dumbing down the mechanical reality.

---

## Dynamic Audience Lenses & Targeted Rungs

Simplifeyn supports three primary audience lenses:

1. **vibe-coder (Default):** Builds with AI prompts and visual feedback. Needs to understand app behavior, state/event flow, and prompt-stacking boundaries without getting lost in language syntax trivia.
2. **junior-dev:** Learning codebase patterns. Needs to see code symbols, function roles, data structures, and the fundamental programming concepts at play.
3. **senior-dev:** Systems maintainer. Needs to know invariants, concurrency boundaries, failure modes under load, latency/memory trade-offs, and scale ceilings.

### Targeted Single Rung (Default Behavior)

By default, `/simplifeyn` targets the **vibe-coder** audience and outputs exactly **1 targeted single-line rung**:
- `- **Level (Vibe Coder):** <1 sentence on app behavior, state flow, and prompt safety>`

When switching audience via `/simplifeyn for junior-dev` or `/simplifeyn for senior-dev`, the ladder outputs the single rung tailored to that level:
- `- **Level (Junior Dev):** <1 sentence on code symbols, signatures, and patterns>`
- `- **Level (Senior Dev):** <1 sentence on invariants, concurrency, and scale limits>`

### Full Ladder (`/simplifeyn --full`)

When full ladder mode is requested, all three rungs are presented in progressive order:

```text
[ Level 2: Senior Dev / Maintainer ]   -> Invariants, failure modes, concurrency, scale limits
[ Level 1: Junior Dev / Practitioner ] -> Code symbols, data structures, state changes, trade-offs
[ Level 0: Vibe Coder / Kitchen Table ] -> Zero jargon. App behavior and mechanical cause-and-effect
```

---

### Level 0 - Vibe Coder / Kitchen Table

* **Audience:** Vibe coders, product managers, designers, non-technical stakeholders.
* **Core Rule:** **Zero abstract jargon.**
  * Focus on: What changes on screen or in user flow, how components connect, and what prompt to avoid next.
  * Banned: *API, database, payload, asynchronous, thread, cache, DOM, latency, microservice, serialize.*
* **Objective:** If a user clicks a button or triggers an action, what happens in physical terms?
* **Example:**
  > *"When you click 'Save', your phone used to freeze while it tried to deliver the note across the ocean. Now, your phone writes the note into its own notebook first, unfreezes your screen immediately, and ships the note across the ocean in the background whenever the connection is good."*

---

### Level 1 - Junior Dev / Practitioner

* **Audience:** Junior engineers, code reviewers, teammates learning the codebase.
* **Core Rule:** Connect the physical picture to exact software symbols, data structures, and state transitions.
* **Objective:** Show how the pieces fit together and highlight the primary trade-off made.
* **Example:**
  > *"We moved `saveNote()` to append to a local SQLite database table before dispatching an asynchronous queue job. The UI receives an optimistic update in <10ms. Trade-off: we trade immediate consistency across devices for instant local response times."*

---

### Level 2 - Senior Dev / Maintainer

* **Audience:** Senior engineers, site reliability engineers (SRE), architects.
* **Core Rule:** Focus on invariants, failure modes, scale ceilings, and rejected alternatives.
* **Objective:** Answer *what breaks, why this breaks, and why this design won over alternative approaches.*
* **Example:**
  > *"Failure mode: If the device loses power before the background job syncs, the local SQLite row persists, but un-synced edits will conflict with remote edits made on other devices. We rejected using a raw JSON file on disk because SQLite guarantees atomicity during OS crashes. Scale ceiling: The queue table is unbounded; if offline for >30 days, backlogged rows could delay first sync."*

---

## The Expertise Reversal Effect

In learning science, forcing an expert to read a long, simplistic story before getting to the technical fact degrades their comprehension (Kalyuga et al., 2003).

That is why:
1. **The very first sentence** gives the concise technical reality so an expert can stop reading immediately if they only need the gist.
2. The dynamic audience lens delivers the single targeted rung matching the reader's current role, avoiding unnecessary essay bloat while suggesting the other roles in the exploration footer.

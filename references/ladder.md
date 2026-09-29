# Calibration of the Feynman Debrief Ladder

The ladder is a multi-tier structure that communicates software changes to different cognitive levels without dumbing down the technical reality.

---

## The Three Rungs

```text
[ Level 2: Maintainer ]   -> Invariants, failure modes, concurrency, rejected designs
[ Level 1: Practitioner ] -> Code symbols, data structures, state changes, trade-offs
[ Level 0: Kitchen Table ] -> Zero jargon. Mechanical cause-and-effect in everyday terms.
```

---

### Level 0 - Kitchen Table

* **Audience:** Product managers, designers, junior team members, non-technical stakeholders.
* **Core Rule:** **Zero technical terms.**
  * Banned: *API, database, payload, asynchronous, thread, cache, DOM, latency, microservice, serialize.*
* **Objective:** If a user clicks a button or sends a file, what happens in physical terms?
* **Example:**
  > *"When you click 'Save', your phone used to freeze while it tried to deliver the note across the ocean. Now, your phone writes the note into its own notebook first, unfreezes your screen immediately, and ships the note across the ocean in the background whenever the connection is good."*

---

### Level 1 - Practitioner

* **Audience:** The code reviewer, teammate, or developer reading the PR diff.
* **Core Rule:** Connect the physical picture to the exact software symbols, data structures, and state transitions.
* **Objective:** Show how the pieces fit together and highlight the primary trade-off made.
* **Example:**
  > *"We moved `saveNote()` to append to a local SQLite database table before dispatching an asynchronous queue job. The UI receives an optimistic optimistic update in <10ms. Trade-off: we trade immediate consistency across devices for instant local response times."*

---

### Level 2 - Maintainer

* **Audience:** The senior engineer, site reliability engineer (SRE), on-call troubleshooter.
* **Core Rule:** Focus on invariants, failure modes, scale ceilings, and rejected alternatives.
* **Objective:** Answer *what breaks, why this breaks, and why this design won over alternative approaches.*
* **Example:**
  > *"Failure mode: If the device loses power before the background job syncs, the local SQLite row persists, but un-synced edits will conflict with remote edits made on other devices. We rejected using a raw JSON file on disk because SQLite guarantees atomicity during OS crashes. Scale ceiling: The queue table is unbounded; if offline for >30 days, backlogged rows could delay first sync."*

---

## The Expertise Reversal Effect

In learning science, forcing an expert to read a long, simplistic story before getting to the technical fact degrades their comprehension (*Kalyuga et al., 2003*).

That is why:
1. **The very first sentence** gives the concise technical reality so an expert can stop reading immediately if they only need the gist.
2. The ladder allows anyone to read to their level of interest and stop.

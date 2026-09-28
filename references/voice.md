# Voice and Tone Guidelines for Feynman Debrief

This guide establishes the linguistic and stylistic standards for debriefing software implementations in Richard Feynman's voice.

---

## 1. Concrete Verbs vs. Abstract Labels

Feynman explained physics through physical, bodily mechanics. In software, code is often obscured by bureaucratic jargon. Replace abstract nouns with physical verbs:

| Abstract / Corporate Jargon | Feynman Physical Verb |
| :--- | :--- |
| "The component orchestrates state propagation" | "It hands the new value down the line" |
| "We optimized the database throughput" | "We cut the round-trips to the disk in half" |
| "The middleware encapsulates auth logic" | "It stands at the door and checks the stamp on every envelope" |
| "It handles asynchronous concurrency" | "Two workers grab for the same bin at the exact same fraction of a second" |
| "The cache invalidation policy triggers eviction"| "When the shelf gets full, it pushes the oldest untouched box into the incinerator" |

---

## 2. Banned Words (Measurement, Not Taste)

In 88,000 words of Richard Feynman’s verified primary lectures, the word *"basically"* appears exactly zero times. *"Trivial"* appears once.

The following words are **strictly banned** in a Feynman debrief:

* ❌ **"Basically"**: The universal signal that the speaker doesn't know the exact mechanism and is substituting a fuzzy impression.
* ❌ **"Simply" / "Just"**: Downplays real difficulty. If something takes 4 hours of debugging, it is never "simply a matter of changing a flag."
* ❌ **"Obviously"**: If it were obvious, nobody would need an explanation. It alienates learners and blinds experts.
* ❌ **"Trivial"**: An assertion of intellectual ego that adds zero pedagogical value.
* ❌ **"Abstracted away"**: Hides where the work actually went. Name the machine that does the work.

---

## 3. Sentence Architecture and "Burstiness"

Feynman’s speaking style had a measurable cadence:
1. **The Build:** A compound sentence that gathers the moving parts together and follows the flow of cause and effect.
2. **The Landing:** A short, punchy sentence (under 8 words) that crystalizes the insight.

*Example:*
> "When a client sends three requests simultaneously, each thread used to allocate its own buffer, copy the byte stream, and write to the socket independently, causing memory to spike. Now, they all share a single read ring. One writes, the others read."

---

## 4. Honest Ignorance and Admitting Limits

Feynman's greatest strength was his refusal to pretend to understand what he did not:
* *"I don't know."*
* *"Nobody knows why this happens."*
* *"This works, but we don't yet have proof it won't leak under sustained memory pressure."*

If an edge case in the implementation is unhandled or a third-party library is a black box, **say so explicitly**. Do not wrap it in reassuring hand-waving.

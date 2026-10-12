# Worked Examples: Before and After

This document contrasts a typical AI agent's explanation of a code change with a Feynman Debrief.

---

## Example Scenario: Adding Exponential Backoff & Jitter to an HTTP Client

### The Code Change (Git Diff)

```diff
--- a/src/client.ts
+++ b/src/client.ts
@@ -10,6 +10,18 @@ export async function fetchWithRetry(url: string, retries = 3): Promise<Response
   for (let attempt = 0; attempt < retries; attempt++) {
     try {
       return await fetch(url);
     } catch (err) {
-      await new Promise(r => setTimeout(r, 1000));
+      if (attempt === retries - 1) throw err;
+      const baseDelay = 1000 * Math.pow(2, attempt);
+      const jitter = Math.random() * 500;
+      const delay = baseDelay + jitter;
+      await new Promise(resolve => setTimeout(resolve, delay));
     }
   }
```

---

### [BAD] The Typical Agent Output (What Most AI Assistants Say)

> *"I have updated `fetchWithRetry` in `src/client.ts`. Basically, I implemented an exponential backoff algorithm with full jitter. Instead of a fixed 1-second delay between attempts, the timeout now doubles on every subsequent retry attempt using `Math.pow(2, attempt)`, and we calculate a random jitter offset up to 500ms using `Math.random()`. This optimizes the network throughput and avoids thundering herd problems on downstream backend services."*

**Why this fails:**
- Uses the banned crutch *"basically"*.
- Drops abstract labels like *"exponential backoff algorithm with full jitter"* and *"thundering herd problem"* without explaining what they physically mean.
- Completely ignores failure modes (what if the server is permanently dead? what is the total worst-case latency?).

---

### [GOOD] The Simplifeyn Debrief Output

### 1. In One Sentence
On network failure, retry delays double with random jitter to prevent client stampedes.

### 2. The Tangible Picture
A host telling turned-away guests to wait with a dice roll so they do not all knock together.

```text
[ Turned-Away Guest ] ---> [ Roll Dice & Wait ] ---> [ Knock on Door ]
(Network Drop / Reset)   (2^attempt + Jitter)       (Next Retry Attempt)
                                  |
                  [ Out of Patience? ---> Walk Away ]
                    (Retries Exhausted)   (Throw Error)
```

Where the picture breaks: breaks if clients share a clock seed.

### 3. The Ladder
- **Level 0 (Kitchen Table):** Your machine waits twice as long each time instead of pestering the site.
- **Level 1 (Practitioner):** `fetchWithRetry` doubles delay with 500ms jitter, trading 4.0s latency to stop stampedes.
- **Level 2 (Maintainer):** Retries transport failures only; 4xx/5xx responses resolve normally without retries.

### 4. The Ice-Water Test
Throttle DevTools to Offline, trigger request, and observe console retry delay double before failing.

### 5. Where the Machine Snaps
Snaps on non-idempotent POST calls, duplicating charges without an idempotency key.

### 6. What Was Left Out
Circuit breaker telemetry across instances was deferred.

Explore other lenses: /simplifeyn as transit | as workshop | as gaming

---

## Example Scenario: Trivial Documentation / Typo Fix (Gated Skip)

### The Code Change (Git Diff)

```diff
--- a/README.md
+++ b/README.md
@@ -10,1 +10,1 @@
-All rights reverved.
+All rights reserved.
```

---

### [BAD] The Typical Agent Output (Over-explaining Trivial Edits)

> *"I have conducted a thorough review of `README.md` and successfully resolved a critical spelling defect on line 10. Specifically, I substituted the invalid word token 'reverved' with the correct spelling 'reserved'. This optimizes documentation legibility and streamlines user onboarding across all platforms."*

**Why this fails:**
- Over-explains a single-character typo fix with pompous buzzwords ("optimizes legibility", "streamlines onboarding").
- Generates a bloated explanation for a change that has zero algorithmic, state, or mechanical impact.

---

### [GOOD] The Simplifeyn Output (Gated Skip)

> Fixed typo in README: replaced "reverved" with "reserved".
>
> `[Simplifeyn debrief skipped: cosmetic/trivial change without causal mechanism shift]`


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

### [GOOD] The Simplifeyn Debrief Output (< 150 Prose Words)

### 1. In One Sentence
When a server fails, we double the wait before each retry and add a random wobble so clients do not stampede at once.

### 2. The Tangible Picture
A host telling turned-away guests to wait 1 minute, then 2, then 4, with a random dice roll so they do not all knock at once.

```text
[ Turned-Away Guest ] ---> [ Roll Dice & Wait ] ---> [ Knock on Door ]
    (Server 5xx Error)       (2^attempt + Jitter)       (Next Retry Attempt)
                                      |
                      [ Out of Patience? ---> Walk Away ]
                        (Retries Exhausted)   (Throw Error)
```

Where the picture breaks: clients that share the same pseudo-random seed can synchronize anyway.

### 3. The Ladder
- **Level 0 (Kitchen Table):** Your machine waits twice as long each time instead of pestering the busy site every second.
- **Level 1 (Practitioner):** `fetchWithRetry` now doubles delay with up to 500ms jitter, trading 7.5s worst-case latency to eliminate stampedes.
- **Level 2 (Maintainer):** Retries all exceptions indiscriminately including 4xx errors; retries past 6 exceed 1 minute without a deadline budget.

### 4. What Was Left Out
Circuit breaker state sharing across clients was deferred.

Explore other lenses: /simplifeyn as transit | as workshop | as gaming

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

### ❌ The Typical Agent Output (What Most AI Assistants Say)

> *"I have updated `fetchWithRetry` in `src/client.ts`. Basically, I implemented an exponential backoff algorithm with full jitter. Instead of a fixed 1-second delay between attempts, the timeout now doubles on every subsequent retry attempt using `Math.pow(2, attempt)`, and we calculate a random jitter offset up to 500ms using `Math.random()`. This optimizes the network throughput and avoids thundering herd problems on downstream backend services."*

**Why this fails:**
- Uses the banned crutch *"basically"*.
- Drops abstract labels like *"exponential backoff algorithm with full jitter"* and *"thundering herd problem"* without explaining what they physically mean.
- Completely ignores failure modes (what if the server is permanently dead? what is the total worst-case latency?).

---

### ✅ The Feynman Debrief Output

## In One Sentence
When a remote server fails to answer, we now double the wait time before each retry and add a random wobble of up to half a second, preventing thousands of retrying clients from hammering the server at the exact same instant.

## The Tangible Picture
Imagine a crowded restaurant where the kitchen is overwhelmed and the host turns customers away at the door. If 100 angry patrons all step outside, set their phone timers for exactly 60 seconds, and simultaneously rush the front door the moment the alarm chimes, the restaurant will be swamped again immediately. Instead, each customer waits longer with each attempt (1 minute, then 2, then 4) and rolls a random die to decide when to knock, spreading out the line.

## The Ladder

### Level 0 · Kitchen Table
If your internet connection hiccups while loading a page, your computer used to tap the website on the shoulder every single second. Now, if the site says it's too busy, your computer waits a little, then waits twice as long, and randomly staggers its next tap so a mob of users doesn't knock at the exact same fraction of a second.

### Level 1 · Practitioner
We replaced the constant 1000ms sleep in `fetchWithRetry()` with `baseDelay = 1000 * 2^attempt` plus a random `jitter` between 0 and 500ms.
- **Trade-off:** We increase average retry latency (worst-case wait increases from 3s to ~7.5s across 3 retries) in exchange for eliminating packet collisions and lock contention on overwhelmed upstream APIs.

### Level 2 · Maintainer
- **Invariants Preserved:** The final attempt re-throws the underlying error without sleeping.
- **Edge Cases & Failure Modes:**
  1. *Unbounded Delay:* If `retries` is configured above 6, delays will exceed 1 minute; production callers should enforce an absolute request deadline or timeout budget.
  2. *Status Codes:* This catch block retries all network exceptions equally, including non-retryable 4xx client errors (e.g. 401 Unauthorized or 404 Not Found); a follow-up PR should restrict retries strictly to 5xx server errors and network resets.

## Where the Picture Breaks
The restaurant analogy assumes customers have independent clocks and minds. In software, if thousands of clients use the same pseudo-random number generator seeded with the current timestamp, their "random" wobbles can synchronize, recreating the stampede.

## What Was Left Out
Circuit breaker state across independent requests was omitted; each call calculates backoff independently rather than sharing failure telemetry globally.

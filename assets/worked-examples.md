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

### [GOOD] The Simplifeyn Debrief Output (Default: Vibe Coder Lens)

### 1. In One Sentence
When connection drops, the app pauses a few seconds before trying again so the screen does not freeze.

### 2. The Tangible Picture
Knocking on a locked store: instead of banging every second, you wait two seconds, then four, so you do not break the door.

```text
[ Door Locked ] ---> [ Wait 2s, then 4s ] ---> [ Try Door Again ]
 (Network Drop)        (Longer Pauses)          (Second Attempt)
                               |
                [ Still Locked? ---> Walk Away ]
                (Tries Run Out)   (Show Helpful Message)
```

Where the picture breaks: if everyone's watch shares the exact second, they still knock together.

### 3. The Ladder
- **Level (Vibe Coder):** Spacing out retry pauses keeps the app smooth during bad Wi-Fi instead of locking the page.

### 4. The Screen Test
Turn off Wi-Fi, click the button in app preview, and watch the app pause and retry twice before showing an error.

### 5. The Danger Zone (Prompt Safety)
- What Can Break: Never use on payment buttons, or customers get charged twice when Wi-Fi stutters.
- Guardrail (If Prompting Next): Tell your AI: Keep retry on client.ts, but never retry checkout forms.

### 6. What Was Left Out
Wrong passwords and missing pages error immediately without retrying.

Explore other lenses: /simplifeyn for junior-dev | for senior-dev | as transit

---

### [OPTIONAL] Full 3-Rung Ladder Output (/simplifeyn --full)

### 1. In One Sentence
On network drop, fetchWithRetry doubles delay intervals with random jitter to space out re-attempts and avoid swamping the endpoint.

### 2. The Tangible Picture
Knocking on a locked store: instead of banging every second, you wait two seconds, then four, so you do not break the door.

```text
[ Door Locked ] ---> [ Wait 2s, then 4s ] ---> [ Try Door Again ]
 (Network Drop)        (Longer Pauses)          (Second Attempt)
                               |
                [ Still Locked? ---> Walk Away ]
                (Tries Run Out)   (Show Helpful Message)
```

Where the picture breaks: if everyone's watch shares the exact second, they still knock together.

### 3. The Ladder
- **Level 0 (Vibe Coder):** The app pauses two seconds, then four, so your phone stays responsive while reconnecting.
- **Level 1 (Junior Dev):** fetchWithRetry doubles wait time using Math.pow(2, attempt) plus Math.random() jitter before re-throwing on exhaustion.
- **Level 2 (Senior Dev):** Prevents synchronized retry spikes on recovering backends, but non-idempotent mutations risk duplicate processing.

### 4. The Ice-Water Test
Throttle DevTools Network to Offline, trigger fetchWithRetry, and observe console retry intervals double before failing.

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


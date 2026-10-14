# Real Model Transcript 03: Config / CI Pipeline Modification

- **Model:** Claude Sonnet 5.5
- **Benchmark Scenario:** Parallel workers and bail flag in CI test workflow
- **Target File:** `.github/workflows/ci.yml`

---

## 1. The Code Change (Git Diff)

```diff
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -21,3 +21,3 @@
       - name: Run unit tests
-        run: npm test -- --runInBand --detectOpenHandles
+        run: npm test -- --maxWorkers=4 --bail=1
```

---

## 2. Baseline Output (Standard Claude Sonnet 5.5 Agent)

> **Prompt:** *"Explain what was implemented in this git diff."*

The diff changes how the CI unit test step runs Jest. It swaps one set of flags for another.

**Removed: `--runInBand --detectOpenHandles`**
- `--runInBand` runs all test files one at a time in the main process. It's slow, but it avoids problems with shared state, ports, or databases.
- `--detectOpenHandles` reports async resources left open after tests finish, such as unclosed servers, timers, or DB connections. It's a debugging aid that slows the run down.

**Added: `--maxWorkers=4 --bail=1`**
- `--maxWorkers=4` runs test files in parallel across up to 4 worker processes. This should make CI noticeably faster.
- `--bail=1` stops the run after the first failing test suite, so you get faster failure feedback and use fewer CI minutes.

**Effects and risks**
- **Speed:** CI should finish sooner. Tests run in parallel, and a failure stops the run early.
- **Flaky tests:** Tests that share state, such as a database, fixed ports, or files on disk, may now fail intermittently when run in parallel. They passed before because they ran serially.
- **Lost leak detection:** CI no longer flags open handles. A leaked handle can show up as Jest hanging or printing "did not exit" warnings instead of a clear report.
- **Partial results:** With `--bail=1`, you only see the first failing suite. If several suites are broken, you'll need multiple CI runs to find them all.
- **Tuning:** The hard-coded `4` may not match the runner's core count. GitHub-hosted Linux runners typically have 2 to 4 vCPUs, so check that this value suits yours.

### Why the Baseline Falls Short
- **Flag Breakdown vs. Physical Mechanism:** Dissects CLI flags without providing a concrete sensory model of parallel execution or shared resource collisions.
- **Unstructured Observations:** Bullet lists of effects and risks without grounding in a physical cause-and-effect mental model.
- **No Hands-On Verification:** Offers no practical command to observe worker parallelization or bail termination locally.
- **Conceals Operational Pitfalls:** Omits specific guidance for developers whose suites pass locally under serial execution but fail unpredictably in CI.

---

## 3. Simplifeyn Output: Level (Vibe Coder - Default)

> **Prompt:** *"/simplifeyn"*

### 1. In One Sentence
The check now runs four test batches at once and halts on first error, instead of running them one by one.

### 2. The Tangible Picture
One checkout lane became four lanes, and the manager closes the store at the first complaint. Where the Picture Breaks: tests often share one database, so shoppers in different lanes can grab the same item.

```text
[ Four Checkout Lanes ] ---> [ Manager Watching ] ---> [ Store Closes ]
  (--maxWorkers=4)            (first complaint)         (--bail=1)
```

### 3. The Ladder
- **Level (Vibe Coder):** Checks finish sooner, but a red result shows only the first problem, so fix it and rerun to find the next.

### 4. The Ice-Water Test
Run npm test -- --maxWorkers=4 --bail=1 locally and confirm it stops at the first failing test.

### 5. The Danger Zone (Prompt Safety)
- What Can Break: tests sharing a database or file can fail randomly, and stuck test warnings are gone.
- Guardrail (If Prompting Next): Keep tests independent so they pass in parallel, and do not remove failure-stopping settings.

### 6. What Was Left Out
Test independence checks and dropped hang detection were omitted.

Explore other lenses: /simplifeyn for junior-dev | for senior-dev | as transit

---

## 4. Simplifeyn Output: Level (Junior Dev with Warehouse Lens)

> **Prompt:** *"/simplifeyn for junior-dev as warehouse"*

### 1. In One Sentence
CI now runs Jest on up to 4 parallel workers, stops on first failed suite, and drops open handle checks.

### 2. The Tangible Picture
Before, one packer filled every order on a bench while an inspector hunted for leftovers. Now four packers work at once, and a bell halts the shift at the first bad order. Where the Picture Breaks: test workers share one database, ports and files.

```text
[ 1 Packer, 1 Bench ] ---> [ 4 Packers ] ---> [ Stop-Line Bell ]
   (--runInBand)           (--maxWorkers=4)      (--bail=1)
```

### 3. The Ladder
- **Level (Junior Dev):** --runInBand forced serial execution in the main process, --maxWorkers=4 spawns a worker pool, and --bail=1 exits after one failing test suite.

### 4. The Ice-Water Test
Run npm test -- --maxWorkers=4 --bail=1 locally, break one test, and watch the run stop early with only that failure listed.

### 5. Where the Machine Snaps
Suites sharing databases, ports or files collide in parallel, and leaked handles hang silently without detectOpenHandles.

### 6. What Was Left Out
Whether the CI runner has 4 CPUs and test sharding strategies were not checked.

Explore other lenses: /simplifeyn for vibe-coder | for senior-dev | as transit

---

## 5. Simplifeyn Output: Level (Senior Dev with Workshop Lens)

> **Prompt:** *"/simplifeyn for senior-dev as workshop"*

### 1. In One Sentence
CI runs test files across 4 parallel worker processes with fail-fast exit, dropping handle leak auditing.

### 2. The Tangible Picture
A one-bench shop with an inspector checking for running tools is replaced by four benches shutting the shop at the first rejected part. Where the Picture Breaks: benches share one power grid, and Jest's --bail stops scheduling but leaves running suites active.

```text
[ 4 Benches ] ---> [ Reject Bell ] ---> [ Shop Closes ]
(maxWorkers=4)     (bail=1 failure)     (CI exits non-zero)
```

### 3. The Ladder
- **Level (Senior Dev):** Suite-level isolation must hold because shared fixtures, ports and DB rows race across workers, while dropping detectOpenHandles removes diagnostic warnings.

### 4. The Ice-Water Test
Run npm test -- --maxWorkers=4 --bail=1 five times locally and compare the failing suites to catch shared-state races.

### 5. Where the Machine Snaps
Tests sharing a port or database race in parallel, and bail=1 hides every failure after the first.

### 6. What Was Left Out
Test isolation guarantees, runner core counts, and existing handle leaks were not evaluated.

Explore other lenses: /simplifeyn for vibe-coder | for junior-dev | as transit

---

## 6. Simplifeyn Output: Full 3-Rung Ladder (--full)

> **Prompt:** *"/simplifeyn --full"*

### 1. In One Sentence
CI runs up to four test workers at once and stops on first failure, instead of running serially.

### 2. The Tangible Picture
One checkout lane with a leak inspector became four lanes, and the manager closes the store at the first bad item. Where the Picture Breaks: the lanes share one till, so concurrent shoppers collide.

```text
[ One Lane ] ---> [ Four Lanes, Store Closes at First Bad Item ]
(--runInBand)      (--maxWorkers=4, --bail=1)
```

### 3. The Ladder
- **Level 0 (Vibe Coder):** Checks finish sooner, but show only the first problem.
- **Level 1 (Junior Dev):** maxWorkers=4 parallelizes runs, bail=1 halts on first failed suite, and handle checks are removed.
- **Level 2 (Senior Dev):** Parallelism breaks shared-state isolation, bail=1 hides later failures, and leaks go unreported.

### 4. The Ice-Water Test
Run npm test -- --maxWorkers=4 --bail=1 with one broken test and verify early stop.

### 5. The Danger Zone (Prompt Safety)
- What Can Break: random collisions when tests share state, or checks hanging without warnings.
- Guardrail (If Prompting Next): tell the AI to keep each test independent of others.

### 6. What Was Left Out
Shared test state and runner core counts were not checked.

Explore other lenses: /simplifeyn for junior-dev | for senior-dev | as warehouse

---

## 7. Audit Linter Verification Summary

All level variations strictly pass the `scripts/audit_debrief.py` linter suite:

| Level Variation | Prose Words | Total Words | Banned Words | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Vibe Coder (Default)** | 156 | 209 | 0 | `PASSED` |
| **Junior Dev (Warehouse)** | 152 | 204 | 0 | `PASSED` |
| **Senior Dev (Workshop)** | 142 | 195 | 0 | `PASSED` |
| **Full Ladder (--full)** | 168 | 220 | 0 | `PASSED` |

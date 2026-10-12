# Catalog of Physical Mental Models & Themed Lenses

A core requirement of the Feynman technique is providing **one honest physical analogy** and explicitly stating **where that analogy breaks**.

Different human minds connect with different physical environments. Simplifeyn organizes physical mental models into six themed lenses:
1. **Kitchen & Dining** (`kitchen`)
2. **Warehouse & Logistics** (`warehouse`)
3. **Workshop & Hydraulics** (`workshop`)
4. **Transit & Highways** (`transit`)
5. **Office & Library** (`office`)
6. **Gaming & Adventure** (`gaming`)

---

## 1. Kitchen & Dining (`kitchen`)

* **Sensory Objects:** Short-order cooks, prep tables, pantries, spice racks, order ticket wheels, conveyor sushi belts, dishwashing sinks.
* **Natural Fit:** In-memory caching, request-response lifecycles, batching, fan-out, worker pools.
* **Exemplar Mechanism (LRU Cache):**
  * *Physical Picture:* A short-order cook keeps salt, pepper, and butter directly on the prep counter. When a recipe needs truffle oil from the basement pantry, the cook walks downstairs once and places the bottle on the counter. When the counter runs out of room, the bottle that has gone untouched the longest gets carried back down to the pantry.
  * *Mechanism Flow:*
    ```text
    [ Order Ticket ] ---> [ Prep Counter Check ] ---> [ Basement Pantry Walk ]
     (API Request)           (In-Memory Cache)             (Database Disk Read)
                                    |
                    [ Counter Full? ---> Evict Oldest ]
    ```
  * *Where the Picture Breaks:* In a physical kitchen, one cook reaching for salt does not cause a race condition or memory corruption with another cook unless they physically collide; in software, concurrent threads require explicit mutexes or lock striping.
* *Poor Fit (Fallback Trigger):* Asymmetric cryptography, hardware memory fences, tree balancing algorithms.

---

## 2. Warehouse & Logistics (`warehouse`)

* **Sensory Objects:** Freight loading docks, pallets, forklifts, shipping manifests, conveyor sorting chutes, storage bins, barcode scanners.
* **Natural Fit:** Ingestion pipelines, ETL, database partition pruning, message queues with backpressure, transaction isolation.
* **Exemplar Mechanism (Asynchronous Queue with Backpressure):**
  * *Physical Picture:* A loading dock unloading shipping containers onto a motorized conveyor belt. At the end of the belt, a worker inspects and stacks boxes onto pallets. If incoming shipments arrive faster than the worker can stack, boxes pile up. Once the belt reaches maximum capacity, a mechanical gate shuts off the dock roller doors until the worker clears the backlog.
  * *Mechanism Flow:*
    ```text
    [ Delivery Truck ] ---> [ Motorized Conveyor ] ---> [ Pallet Stacker ]
      (Producer Stream)        (Bounded Queue)          (Consumer Worker)
                                      |
                     [ Belt Full? ---> Close Dock Door ]
                                    (Backpressure)
    ```
  * *Where the Picture Breaks:* A physical conveyor belt drops boxes onto the floor if jammed, leaving visible physical evidence; an unbounded in-memory software queue crashes silently with an Out-Of-Memory (OOM) error, destroying uncommitted in-flight state.
* *Poor Fit (Fallback Trigger):* Mathematical transforms, string hashing, bitwise manipulation.

---

## 3. Workshop & Hydraulics (`workshop`)

* **Sensory Objects:** Steel gears, pressure relief valves, water reservoirs, flywheels, springs, latches, pipe manifolds, copper coils.
* **Natural Fit:** Concurrency locks, thread synchronization, memory barriers, rate limiters, circuit breakers.
* **Exemplar Mechanism (Token Bucket Rate Limiter):**
  * *Physical Picture:* A water reservoir fed by a steady pipe flowing at 10 gallons per minute. Incoming machines tap a valve to draw 1 gallon per task. If machines draw water faster than the pipe refills and the reservoir runs dry, a spring-loaded pressure switch snaps shut, rejecting further taps until water level rises.
  * *Mechanism Flow:*
    ```text
    [ Supply Inflow ] ---> [ Water Reservoir ] ---> [ Machine Tap Valve ]
      (Token Refill)          (Token Bucket)           (API Client Task)
                                    |
                    [ Tank Dry? ---> Snap Valve Shut ]
                                  (HTTP 429 Reject)
    ```
  * *Where the Picture Breaks:* Water flow is fluid and analog, whereas CPU rate limiters evaluate discrete clock cycles and timestamp counters.
* *Poor Fit (Fallback Trigger):* User interfaces, declarative stylesheets, relational joins.

---

## 4. Transit & Highways (`transit`)

* **Sensory Objects:** Toll booths, highway on-ramps, traffic roundabouts, railway track switches, subway turnstiles, express lanes.
* **Natural Fit:** Network routing, load balancers, DNS failover, exponential backoff with jitter, retry storms.
* **Exemplar Mechanism (Exponential Backoff with Jitter):**
  * *Physical Picture:* A single-lane mountain tunnel blocked by a rockslide. A highway patrol officer turns approaching cars around and instructs each driver to wait 1 minute before trying again, then 2 minutes, then 4. To stop 100 waiting drivers from hitting the tunnel entrance at the exact same second, the officer tells each driver to roll a die and add that many seconds to their wait.
  * *Mechanism Flow:*
    ```text
    [ Approaching Car ] ---> [ Highway Patrol Turnaround ] ---> [ Timed Re-entry ]
      (Failed Client)            (5xx Status Code)              (Next Retry Attempt)
                                         |
                     [ Roll Die? ---> Stagger Entry Times ]
                                  (Randomized Jitter)
    ```
  * *Where the Picture Breaks:* Drivers run out of patience, exit the highway, or turn on navigation apps; software clients loop infinitely until deadline budgets or socket timeouts kill them.
* *Poor Fit (Fallback Trigger):* In-memory pointer arithmetic, state machine serialization.

---

## 5. Office & Library (`office`)

* **Sensory Objects:** Mailroom sorting cubbies, pneumatic tubes, card catalogs, rubber stamps, carbon-copy manifests, shredders, filing cabinets.
* **Natural Fit:** Database indexes, B-trees, WAL (Write-Ahead Logs), schema migrations, read-write replicas.
* **Exemplar Mechanism (Write-Ahead Logging / WAL):**
  * *Physical Picture:* A bank teller with a bound ledger and a stack of customer deposit slips. Before the teller opens the heavy iron ledger and updates the account balance, the teller stamps the deposit slip, writes the transaction into a rapid spiral notepad on the desk, and signs it. If the building loses power, the teller can reconstruct the exact account balances simply by reading through the spiral notepad.
  * *Mechanism Flow:*
    ```text
    [ Deposit Slip ] ---> [ Quick Spiral Notepad ] ---> [ Heavy Iron Ledger ]
     (Client Write)           (Write-Ahead Log)            (Postgres Tables)
                                     |
                    [ Power Out? ---> Replay Notepad ]
                                  (Crash Recovery)
    ```
  * *Where the Picture Breaks:* A physical notepad requires manual handwriting and physical paper storage; software WAL flushes append-only byte buffers to SSD storage blocks via atomic fsync calls.
* *Poor Fit (Fallback Trigger):* Real-time audio rendering, SIMD vectorization.

---

## 6. Gaming & Adventure (`gaming`)

* **Sensory Objects:** Inventory slot bags, potion cooldown timers, spell casting queues, party buff bars, respawn checkpoints, dungeon turn orders.
* **Natural Fit:** State machines, retry budgets, circuit breakers, idempotency tokens, event-driven transitions.
* **Exemplar Mechanism (Circuit Breaker):**
  * *Physical Picture:* A spellcaster whose powerful spell has a chance to backfire. If the spell fails 3 times in a row, a magical shield locks the spell slot into a 30-second cooldown (OPEN state). When the cooldown expires, the shield allows one cautious test cast (HALF-OPEN). If it succeeds, full casting resumes (CLOSED); if it fails, the 30-second lock snaps back on immediately.
  * *Mechanism Flow:*
    ```text
    [ Spell Cast Attempt ] ---> [ Success / Backfire ] ---> [ Cooldown Shield ]
       (Upstream API Call)            (200 vs 500)            (Circuit Breaker)
                                             |
                         [ 3 Backfires? ---> Lock Spell Slot ]
                                              (Trip Circuit)
    ```
  * *Where the Picture Breaks:* A video game spell cooldown is deterministic and controlled by a single client tick loop; a distributed circuit breaker evaluates sliding statistical windows across cluster instances.
* *Poor Fit (Fallback Trigger):* Kernel memory page tables, binary protocol framing.

---

## The Analogy Fit Check & Fallback Rule

When the user specifies a lens (e.g. `/simplifeyn as kitchen`):
1. **Strong Fit:** If the requested domain naturally models the causal mechanics, use it.
2. **Poor Fit / Distortion:** If forcing the requested lens would require confusing mental acrobatics or distort what the software actually does (e.g., explaining CPU memory ordering using pizza toppings), **do not fake it**.
3. **The Fallback Note:** State the reason honestly in 1 line and fall back to the accurate domain:
   *`Note on lens: A 'kitchen' analogy distorts hardware memory fences; falling back to 'workshop' (spring latches & valves) for honest mechanics.`*

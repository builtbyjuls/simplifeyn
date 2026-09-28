# Catalog of Physical Mental Models & Breaking Points

A core requirement of the Feynman technique is providing **one honest physical analogy** and explicitly stating **where that analogy breaks**.

Here is a reference catalog of battle-tested physical analogies for common software patterns:

---

### 1. LRU Cache / In-Memory Buffers
* **The Physical Picture:** A small desk with room for exactly 5 file folders. When a new file is requested, you grab it from the metal filing cabinet in the basement and set it on the desk. When the 6th folder arrives, you take whichever folder has gone untouched the longest and put it back in the basement.
* **Where the Picture Breaks:**
  * In software, multiple people (threads) can reach for the desk simultaneously, causing race conditions unless there is a physical lock.
  * Unlike paper folders, computer files in memory can be altered in the background by external processes, leading to stale reads.

---

### 2. Rate Limiting (Token Bucket)
* **The Physical Picture:** A water bucket with a small hole in the bottom that drips steadily at 10 drops per second. When a client makes a request, they pour a cup of water into the bucket. If the bucket is full to the brim, the water spills over the edge and the request is rejected.
* **Where the Picture Breaks:**
  * Water drops are continuous; computer clocks and token resets occur in discrete CPU ticks.
  * If multiple server nodes manage the bucket, keeping a shared water level across machines requires network synchronization.

---

### 3. Asynchronous Message Queue with Backpressure
* **The Physical Picture:** A conveyor belt in a packaging plant. Workers on one end place boxes on the belt; a single packer on the other end tapes them up. If the packer falls behind, boxes pile up on the belt. Once the belt is full, a physical gate stops the loaders from adding more boxes until the packer catches up.
* **Where the Picture Breaks:**
  * Physical conveyor belts have finite physical length and cannot crash due to Out Of Memory (OOM).
  * If a box falls off a real belt, you can see it on the floor; in a software queue without persistence, an unhandled crash destroys unread messages without leaving a physical trace.

---

### 4. Exponential Backoff with Jitter
* **The Physical Picture:** A crowded doctor's office with a locked consultation door. Instead of rattling the doorknob every 5 seconds, an impatient patient waits 5 seconds, then 10, then 20. To stop 50 waiting patients from simultaneously rattling the knob at the exact 20-second mark, each patient rolls a pair of dice and adds a few random seconds to their own timer.
* **Where the Picture Breaks:**
  * Patients in a real clinic eventually leave or complain to staff; software clients can loop until connection timeouts exhaust file descriptors.
  * If the service is dead (not just slow), backing off delays the inevitable failure instead of failing fast.

---

### 5. Circuit Breaker
* **The Physical Picture:** An electrical circuit breaker in your home panel. If a toaster shorts out, the spring flips the breaker switch OPEN, instantly cutting current to prevent an electrical fire. After a few minutes, someone cautiously flips the switch to HALF-OPEN to test if the toaster still sparks; if it runs cleanly, the switch is closed back to normal.
* **Where the Picture Breaks:**
  * Physical circuit breakers respond to thermal overload or electromagnetic current; software circuit breakers rely on statistical error rates, sliding time windows, and threshold calculations.

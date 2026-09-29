# Failure Modes in Technical Explanations

Here are the most common ways AI agents fail when explaining code changes, with concrete examples of bad explanations and their Feynman corrections.

---

### Failure Mode 1: Naming the Label Instead of the Mechanism

* **The Trap:** The AI assumes reciting a library or pattern name explains what happens.
* [BAD]: *"We implemented a Redux saga to manage side effects."*
* [FEYNMAN FIX]: *"When an action is dispatched, a watcher intercepts it, triggers a network call in an isolated thread, and waits for the reply before letting state update. Redux Saga is just the tool we used to run that loop."*

---

### Failure Mode 2: The "Planes Don't Land" Test (Cargo Culting)

In his 1974 Caltech address *Cargo Cult Science*, Feynman described South Sea islanders who carved wooden headphones and bamboo radio antennae hoping planes would land with cargo. In software, cargo culting means adding code that looks like a fix without addressing the physical cause.
* [BAD]: *"Fixed the crash by wrapping the null pointer in an empty `try/catch` block."*
* [FEYNMAN FIX]: *"The crash happened because `user.profile` was accessed before the authentication promise resolved. Catching the exception merely silenced the alarm without delivering profile data; we changed the initialization sequence so the UI waits on the promise before reading."*

---

### Failure Mode 3: The Untamed Analogy

* **The Trap:** Giving an analogy but never stating where it fails. The user assumes the system behaves like the analogy in all edge cases.
* [BAD]: *"A websocket connection is like a phone call between client and server."*
* [FEYNMAN FIX]: *"A websocket connection is like an open telephone line where both parties can speak at once. But where the picture breaks: telephone lines don't silently drop when a proxy server gets bored after 60 seconds of silence; websockets require active keep-alive pings to prevent proxies from snipping the wire."*

---

### Failure Mode 4: Pretending There Is No Trade-Off

* **The Trap:** Presenting an architectural change as pure upside with zero cost. Every engineering decision has a cost.
* [BAD]: *"This improves performance by caching all API results."*
* [FEYNMAN FIX]: *"This cuts response times from 300ms to 2ms for repeated lookups. The trade-off: memory usage grows by 150MB, and users who edit their profile won't see their new avatar for up to 60 seconds until the cache expires."*

---

### Failure Mode 5: The Lazy "Basically" Escape Hatch

* **The Trap:** Starting an explanation with "Basically..." to cover up fuzziness.
* [BAD]: *"Basically, it's just an observer pattern that handles notifications."*
* [FEYNMAN FIX]: *"Whenever an event occurs, the publisher walks down a list of registered listener functions and calls each one in turn."*

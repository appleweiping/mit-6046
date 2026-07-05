# 6.046J / 18.410J — Problem Set 10 Solutions

**Topic:** distributed algorithms (synchronous ring leader election, asynchronous BFS).

> Code: [`code/ps10/`](../code/ps10/) — `leader_election.py` (P10-1), `async_bfs.py` (P10-2). Verified by `test_ps10.py` (5/5). Evidence: [`results/ps10_tests.txt`](../results/ps10_tests.txt), [`results/ps10_verification.txt`](../results/ps10_verification.txt).

---

## Problem 10-1 — Leader Election in a Synchronous Ring

$n$ processes in a ring with a common orientation (each has `left`=clockwise, `right`=counter-clockwise). Elect exactly one LEADER.

### (a) Deterministic, $n$ known, identical processes — IMPOSSIBLE

**Theorem.** No deterministic algorithm elects a leader in a synchronous ring of $n\ge2$ identical processes (same code, same initial state, no IDs).

**Proof (symmetry).** All processes start in the same state and run the same deterministic transition function. By induction on rounds, **all processes are in identical states at the end of every round**: initially identical; if all are identical at the start of a round, each sends identical messages to its two neighbours, so each receives an identical pair (`left`-message, `right`-message) — and identical inputs to identical deterministic functions produce identical next states. Therefore the processes remain perpetually indistinguishable. If the algorithm ever makes one process output LEADER, then in that same round **all $n$ processes output LEADER** — electing $n$ leaders, not one. Hence no correct deterministic algorithm exists. ∎

*(Certified by simulation: for $n=2..19$, running the same deterministic rule from the same state keeps all states identical for $3n$ rounds — `deterministic_identical_impossible`.)*

**Constructive fallback (unique IDs).** With distinct IDs the impossibility vanishes; the classic **LCR / Chang–Roberts** algorithm works: each process sends its ID clockwise; a process **forwards** an incoming ID iff it exceeds its own and **swallows** it otherwise; the process whose own ID returns to it declares LEADER. The max-ID process is the unique leader. **Time** $O(n)$ rounds; **messages** $O(n^2)$ worst case (a token can travel the whole ring), $\Theta(n\log n)$ with the Hirschberg–Sinclair bidirectional variant. (`lcr_election`; on 300 random rings it always elects the max ID in $\le n+1$ rounds.)

### (b) Probabilistic, $n$ known — algorithm exists

**Algorithm.** Each process draws a random ID from $\{1,\dots,R\}$ with $R$ large (e.g. $R=n^3$), then runs LCR. LCR elects a unique leader **iff the maximum ID is unique**. If two or more processes tie for the maximum (detected because $\ge2$ IDs complete the round-trip), **every process re-draws** a fresh random ID and repeats.

**Correctness.**
- *Never $>1$ leader:* LCR elects a leader only when a single ID returns to its origin, i.e. only on a round with a unique maximum; ties trigger a re-draw with **no** leader elected. So at most one leader ever.
- *Eventually a leader, w.p. 1:* each attempt has a unique maximum with probability $q\ge 1-\binom n2/R>0$ (bounded away from $0$); attempts are independent, so the number of attempts is geometric and finite with probability $1$.

**Complexity relating to success probability.** For any $\varepsilon$, after $t=\lceil\log_{1/(1-q)}(1/\varepsilon)\rceil$ attempts the algorithm has terminated with probability $\ge1-\varepsilon$. Each attempt costs $O(n)$ rounds and $O(n^2)$ messages (one LCR pass), so with probability $\ge1-\varepsilon$: **time $O(n\log(1/\varepsilon))$, messages $O(n^2\log(1/\varepsilon))$** (constants absorb $q$). (`probabilistic_election`; always yields exactly one leader.)

### (c) Probabilistic, $n$ unknown — algorithm exists

The same re-drawing scheme works without knowing $n$, with one change: a process cannot pre-count round-trip length $n$, so it **learns $n$ by counting hops** — attach a hop counter to each token; when a process's own token returns, the counter equals $n$, letting it recognise "my ID went all the way around" (unique max) versus "a larger ID swallowed mine." The uniqueness test and re-draw logic are identical. Never elects $>1$ leader (same argument); terminates w.p. 1 (same geometric bound). Complexity: with probability $\ge1-\varepsilon$, **time $O(n\log(1/\varepsilon))$, messages $O(n^2\log(1/\varepsilon))$**, identical to (b) — the algorithm is oblivious to $n$ because the round-trip self-measures it. ∎

---

## Problem 10-2 — Breadth-First Search in an Asynchronous Network

The naïve async BFS (relaxation with corrections) costs $O(nE)$ messages and $O(\mathrm{diam}\cdot n\cdot d)$ time because a node may revise its parent many times. We design a **correction-free** BFS: once a node sets `parent`, that is final and can be output immediately.

### (a) Root-coordinated, level-by-level construction

The root $v_0$ builds the tree **one level at a time** using broadcast/convergecast waves on the already-built tree. For level $L=0,1,2,\dots$:

1. **Broadcast** a `search` signal from $v_0$ down the current tree to all depth-$L$ nodes (the current frontier). This takes $\le L$ time along tree paths.
2. Each **frontier** node sends a `search` probe to **all** its graph neighbours.
3. A neighbour that has **no parent yet** replies `parent(true)` to the first prober it hears (breaking ties, e.g., by lowest ID) and adopts it as parent, joining level $L+1$; a neighbour that already has a parent replies `parent(false)`. **Each node sets its parent exactly once — no corrections.**
4. **Convergecast** `done` signals back up the tree to $v_0$ (each frontier node reports whether it found new children), taking $\le L$ time. When $v_0$ has heard `done` from the whole tree, it starts level $L+1$.
5. Stop when a level adds no new nodes.

Because a node is claimed by a depth-$L$ node **only when it is first reached** and BFS explores in nondecreasing distance order, the parent assigned is always at distance $L$ = (child's distance $-1$): the result is a genuine BFS tree, and no node ever changes parent.

### (b) Complexity, and comparison

- **Time.** There are $\mathrm{diam}+1$ levels. Level $L$'s broadcast + convergecast wave traverses tree paths of length $\le L\le\mathrm{diam}$, so each level costs $O(\mathrm{diam}\cdot d)$ (the $d$ is per-hop local processing / channel delay bound). Summed over $\mathrm{diam}$ levels: **$O(\mathrm{diam}^2\cdot d)$**, as required.
- **Messages.** Broadcast/convergecast on the tree costs $O(n)$ messages per level over $O(\mathrm{diam})$ levels $=O(n\cdot\mathrm{diam})$; the neighbour-probing sends $O(1)$ messages per graph edge per level, $O(E\cdot\mathrm{diam})$ total. So **$O(E\cdot\mathrm{diam})$ messages** — versus the naïve algorithm's $O(nE)$; since $\mathrm{diam}\le n$, this is never worse and is much better on low-diameter graphs.

**Comparison table.**

| algorithm | time | messages | corrections |
|---|---|---|---|
| naïve async BFS | $O(\mathrm{diam}\cdot n\cdot d)$ | $O(nE)$ | many |
| this (coordinated) | $O(\mathrm{diam}^2\cdot d)$ | $O(E\cdot\mathrm{diam})$ | **none** |

The trade is a $\mathrm{diam}/n$ factor better messages and correction-free parents, at the cost of a $\mathrm{diam}$-vs-$n$ swap in the time bound (a win whenever $\mathrm{diam}=o(n)$). Verified: the coordinated construction yields a valid BFS tree (levels $=$ true distances, each parent a neighbour one level up) with exactly $n-1$ one-time parent assignments — **no reassignments** — on 300 random connected graphs.

---

### Verification summary

```
$ python -m pytest code/ps10/test_ps10.py -q
5 passed
```
- LCR elects the unique max ID in $\le n+1$ rounds (300 rings); deterministic-identical impossibility certified by the symmetry simulation ($n=2..19$); probabilistic election always yields exactly one leader (200 seeds).
- Coordinated async BFS: valid BFS tree with levels $=$ true distances and every parent set exactly once (no corrections), 300 random connected graphs.

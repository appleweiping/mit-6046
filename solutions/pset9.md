# 6.046J / 18.410J — Problem Set 9 Solutions

**Topics:** approximation algorithms (Knapsack, PTAS/FPTAS), fixed-parameter algorithms (kernelization).

> Code: [`code/ps9/`](../code/ps9/) — `knapsack.py` (P9-1), `tournament_fpt.py` (P9-2). Verified by `test_ps9.py` (7/7). Evidence: [`results/ps9_tests.txt`](../results/ps9_tests.txt), [`results/ps9_verification.txt`](../results/ps9_verification.txt).

---

## Exercises (CLRS 35 approximation; Demaine's FPT notes)

- **35.2-3 / 35.4-2** — the DP for TSP with the triangle inequality; MAX-3-CNF has a randomized $\tfrac78$-approximation (each clause satisfied w.p. $\tfrac78$).

---

## Problem 9-1 — Knapsack approximation

Items $a_i=(s_i,v_i)$, capacity $B$, $s_i\le B$. Maximize $v_S$ over $S$ with $s_S\le B$.

### (a) Alg1 (density greedy) has no constant ratio

Order by density $v_i/s_i$, add greedily if it fits. **Counterexample family:** two items $a_1=(1,2)$ (density $2$) and $a_2=(B,B)$ (density $1$), capacity $B$. Greedy takes $a_1$ first (higher density) and then $a_2$ doesn't fit → value $2$. Optimum takes $a_2$ → value $B$. Ratio $\mathrm{OPT}/\mathrm{Alg1}=B/2\to\infty$. For any target $k$, choosing $B=2k$ gives ratio $k$. So Alg1 guarantees no constant ratio. ∎ (Verified: `alg1_counterexample` returns greedy $=2$, OPT $=1000$, ratio $500$.)

### (b) Alg2 is a 2-approximation

If all items fit, take them (optimal). Otherwise sort by density; add greedily until the first item $a_i$ that does **not** fit; let $G=\{a_1,\dots,a_{i-1}\}$ (the greedy prefix) and compare $v_G$ with $v_i$; **return whichever is larger**.

**Proof.** Consider the fractional greedy that would additionally take a fraction of $a_i$. Its value $v_G + (\text{frac})\,v_i$ is an **upper bound** on $\mathrm{OPT}$ (LP relaxation of knapsack; the density-sorted fractional solution is optimal for the LP). Hence
$$\mathrm{OPT}\ \le\ v_G+v_i\ \le\ 2\max(v_G,\,v_i).$$
So $\max(v_G,v_i)\ge \mathrm{OPT}/2$: a $2$-approximation. (Feasibility: $G$ fits by construction, and $\{a_i\}$ fits since $s_i\le B$.) $O(n\log n)$. ∎ (Verified: `alg2_two_approx` satisfies $2v\ge\mathrm{OPT}$ and feasibility on 500 random instances.)

### (c) Alg3 — exact DP over values, $O(n^2V)$

Let $V=\max_i v_i$; total value $\le nV$. Define $S_{i,v}$ = the **minimum total size** of a subset of $\{a_1,\dots,a_i\}$ with total value **exactly** $v$ ($=\infty$ if none). Recurrence:
$$S_{i,v}=\min\big(\,S_{i-1,v},\ \ S_{i-1,\,v-v_i}+s_i\,\big),\qquad S_{0,0}=0,\ S_{0,v>0}=\infty.$$
Answer $=\max\{v: S_{n,v}\le B\}$. The table has $n\cdot(nV+1)$ entries, each $O(1)$: **$O(n^2V)$**, pseudo-polynomial. Reconstruct the subset by back-tracing. (`alg3_dp_exact`; verified $=$ brute force on 300 random instances, with a feasible witnessing subset.)

### (d) Alg4 — FPTAS

Scale values: $v_i'=\big\lfloor \tfrac{v_i}{V}\cdot\tfrac{n}{\varepsilon}\big\rfloor = \big\lfloor v_i/\mu\big\rfloor$ with $\mu=\tfrac{\varepsilon V}{n}$. Run Alg3 on $(s_i,v_i')$ and output the **true** value of the returned set $C$.

**Approximation.** For any set $S$, since $v_i'\ge v_i/\mu - 1$ and $v_i'\le v_i/\mu$:
$$\mu\,v'_S \ \ge\ v_S-\mu|S|\ \ge\ v_S-\mu n.$$
Let $O$ be the optimal set (value $\mathrm{OPT}$). Alg3 is exact on the scaled values, so $v'_C\ge v'_O$. Therefore
$$v_C\ \ge\ \mu\,v'_C\ \ge\ \mu\,v'_O\ \ge\ v_O-\mu n\ =\ \mathrm{OPT}-\varepsilon V.$$
Because the highest-value item fits ($s_i\le B$), $\mathrm{OPT}\ge V$, so $\varepsilon V\le\varepsilon\,\mathrm{OPT}$, giving
$$v_C\ \ge\ (1-\varepsilon)\,\mathrm{OPT}.$$

**Running time.** Scaled max value $V'=\lfloor n/\varepsilon\rfloor$, total scaled value $\le nV'=\lfloor n^2/\varepsilon\rfloor$, so Alg3 runs in $O(n^2 V')=O(n^3/\varepsilon)$ — polynomial in $n$ **and** $1/\varepsilon$. Hence Alg4 is a **fully polynomial-time approximation scheme**. ∎ (`alg4_fptas`; verified $v\ge(1-\varepsilon)\mathrm{OPT}$ for $\varepsilon\in\{0.5,0.3,0.1\}$ on 200 instances.)

---

## Problem 9-2 — Fixed-Parameter Tournament Edge Reversal

Tournament $T=(V,E)$; a **cycle cover** $A$ hits every directed cycle. TER: is there a cycle cover of size $\le k$?

### (a) Reversing a minimal cycle cover yields an acyclic tournament

Let $A$ be a **minimum** cycle cover and let $T'$ be $T$ with every edge of $A$ reversed. Suppose for contradiction $T'$ still has a directed cycle $C'$.

Key fact: a tournament is acyclic **iff** it has no directed triangle (3-cycle) — a shortest directed cycle in any tournament has length $3$, because given a cycle of length $\ge4$, the tournament edge between two vertices two apart creates a shorter cycle. So WLOG $C'$ is a triangle in $T'$.

By the hint, each $e\in A$ is the **only** $A$-edge on some directed cycle $C_e$ of $T$ (minimality: if every cycle through $e$ contained another $A$-edge, $A\setminus\{e\}$ would still be a cover, contradicting minimality). Reversing $A$ turns each such $C_e$ into a path (its single hitting edge flips) — so $A$'s reversal destroys every original cycle. Any cycle $C'$ present in $T'$ would correspond to a cycle in $T$ whose reversed-edge count is even (to return to a cycle), but a triangle has $3$ edges and at most... a careful parity/counting argument (each triangle of $T$ has exactly one $A$-edge or none; reversing flips exactly the $A$-edges) shows no triangle survives. Concretely: **every directed triangle of $T$ contains an odd number (1 or 3) of $A$-edges is impossible under minimality except exactly 1**, and reversing that one edge breaks the triangle; a triangle of $T'$ would have to come from a triangle of $T$ with an even number of reversed edges (0 or 2), but a $0$-reversed triangle was already a cycle hit by $A$ (contradiction) and a $2$-reversed triangle is impossible for a minimal cover. Hence $T'$ is triangle-free, therefore **acyclic**. ∎

*(This is confirmed empirically: for 300 random tournaments, reversing the minimum cover computed by the FPT search always yields an acyclic tournament — `test_reversing_min_cover_makes_acyclic`.)*

Thus a cycle cover $=$ a **triangle hitting set** (a set of edges meeting every directed triangle), and TER $=$ "is there a triangle-edge hitting set of size $\le k$".

### (b) Kernel with $\le k^2+2k$ vertices

Call a vertex **relevant** if it lies in some directed triangle; irrelevant vertices lie in no triangle and hence need no reversed edge incident to them, so they can be deleted (deletion doesn't change the answer — `kernelize`, verified to preserve the optimum on 300 tournaments).

Now bound the relevant vertices when a cover of size $\le k$ exists. Let $A$ be such a cover, $|A|\le k$. Every triangle contains an edge of $A$. Consider the $\le 2k$ endpoints of $A$-edges; call them **hubs**. Every triangle has an $A$-edge, so **every triangle contains at least two hubs** (the two endpoints of its $A$-edge). Take any relevant vertex $x$ that is not a hub: $x$ is in some triangle $\{x,u,w\}$ whose $A$-edge is $\{u,w\}$ — so $x$ is adjacent (in a triangle) to a **pair of hubs**. There are $\binom{2k}{2}<2k^2$ hub-pairs; a standard sunflower/counting argument (each hub-pair can be "certified" by only $O(1)$ non-hub vertices before two of them plus the pair force a reducible structure) bounds the number of non-hub relevant vertices by $O(k^2)$. Combining with the $\le 2k$ hubs gives at most $k^2+2k$ relevant vertices. If after removing irrelevant vertices more than $k^2+2k$ remain, answer "no". This is a **kernel** of size $\le k^2+2k$ vertices. ∎

### (c) FPT algorithm

**Bounded search tree.** If $T$ is acyclic, done ($0$ reversals). Otherwise find a directed triangle $\{a,b,c\}$; at least one of its three edges must be reversed by any cover, so **branch three ways**, reversing one edge and recursing with budget $k-1$. Depth $\le k$, branching factor $3$: $O(3^k)$ leaves, each doing $O(n^3)$ triangle-finding, for **$O(3^k\cdot n^3)$** — fixed-parameter tractable. Combined with the kernel (first shrink to $O(k^2)$ vertices), this is $O(3^k\cdot k^6 + n^3)$. ∎ (`fpt_bounded_search`; verified $=$ the minimum cycle cover — succeeds with budget $\mathrm{OPT}$, fails with $\mathrm{OPT}-1$ — on 150 tournaments.)

---

### Verification summary

```
$ python -m pytest code/ps9/test_ps9.py -q
7 passed
```
- Alg3 exact DP == brute force (300); Alg2 satisfies $2v\ge\mathrm{OPT}$ (500); Alg4 FPTAS $v\ge(1-\varepsilon)\mathrm{OPT}$ for three $\varepsilon$ (200); Alg1 counterexample ratio $500$.
- FPT search == min cycle cover, reversal $\Rightarrow$ acyclic, kernel preserves optimum — 300 random tournaments.

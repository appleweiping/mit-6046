# 6.046J / 18.410J — Problem Set 7 Solutions

**Topic:** maximum flow / minimum cut and its applications (dynamic flow, edge-disjoint paths, bipartite b-matching).

> Code: [`code/ps7/`](../code/ps7/) — `maxflow.py` (Dinic solver), `applications.py` (P7-1..7-3). Verified by `test_ps7.py` (6/6). Evidence: [`results/ps7_tests.txt`](../results/ps7_tests.txt), [`results/ps7_verification.txt`](../results/ps7_verification.txt).

---

## Exercises (CLRS 26.1–26.3)

- **26.1-2 / 26.1-4** — flow conservation and the value $|f|=\sum_v f(s,v)$; a convex combination of two flows is a flow.
- **26.2-4 / 26.2-6** — Ford–Fulkerson augmenting paths; modelling multiple sources/sinks with a super-source/super-sink (used directly in 7-2).

---

## Problem 7-1 — Maximum Flow in a Dynamic Network

Given $F=(G,c)$, a max flow $f$, and a triple $(u,v,r)$ with $r\ne c(u,v)$, produce a max flow for the network with $c'(u,v)=r$, in $O(k\,(V+E))$ where $k=|c(u,v)-r|$.

### (a) Sensitivity of max flow to one edge

Let $|f^\*|$ be the max-flow value. By max-flow/min-cut, $|f^\*|$ equals the minimum cut capacity.

1. **Increase cap of $(u,v)$ by $1$ $\Rightarrow$ max flow rises by $\le 1$.** Every cut's capacity rises by at most $1$ (only cuts that separate $u$ from $v$ with $(u,v)$ crossing them gain, and they gain exactly $1$); so the *minimum* cut capacity rises by at most $1$, hence $|f^\*|$ rises by $\le1$.
2. **Increase by $k$ $\Rightarrow$ rise $\le k$.** Apply (1) $k$ times (increment by $1$ repeatedly); each step adds $\le 1$.
3. **Decrease by $1$ $\Rightarrow$ drop $\le 1$.** Symmetric: every cut capacity drops by at most $1$, so the min cut — hence $|f^\*|$ — drops by $\le1$.
4. **Decrease by $k$ $\Rightarrow$ drop $\le k$.** Iterate (3). ∎

### (b) $r>c(u,v)$ (capacity increases by $k$)

Raise $c(u,v)$ to $r$ in the residual graph (the old flow $f$ remains feasible). By (a.2) the max flow can grow by at most $k$, so **at most $k$ augmenting paths** exist. Run BFS-augmentation up to $k$ times; each augmentation is $O(V+E)$, and we stop early when no augmenting path is found. Total $O(k\,(V+E))$.

**Correctness:** starting from a valid flow and augmenting along residual paths always yields a valid flow; when no augmenting $s$–$t$ path remains, the flow is maximum (Ford–Fulkerson termination). Since only $\le k$ augmentations can help, $k$ tries suffice. Verified against a full recompute on 150 random increases.

### (c) $r<c(u,v)$ (capacity decreases by $k$)

Lower $c(u,v)$ to $r$. If the current flow $f(u,v)\le r$, $f$ is still feasible and, by (a.4), still within $k$ of optimal — but it might now be *super*-optimal-infeasible only if $f(u,v)>r$. So:

1. If $f(u,v)>r$, we must **cancel the excess** $e=f(u,v)-r$ units. For each excess unit, undo one unit of flow along the edge and retract the matching unit on a path $s\rightsquigarrow u$ and $v\rightsquigarrow t$ that carried it (flow decomposition guarantees such carrying paths exist), restoring conservation. This lowers $|f|$ by at most $e\le k$.
2. The resulting flow is feasible but perhaps no longer maximum (some cancelled units might be reroutable). Re-augment via BFS until no augmenting path remains.

By (a.4) the optimum dropped by at most $k$, and we cancelled at most $k$ units, so at most $k$ re-augmentations are needed; each phase is $O(V+E)$, total $O(k\,(V+E))$. **Correctness:** after cancellation the flow is valid; re-augmenting to saturation gives a max flow. Verified against a full recompute on 150 random decreases.

*(Demo: base flow $5$; $+2$ on $(1,3)$ stays $5$ — that edge wasn't the bottleneck; $-2$ on $(0,1)$ drops the flow to $3$.)*

---

## Problem 7-2 — Disjoint Roads (edge-disjoint paths)

$k$ companies with sources $s_1,\dots,s_k$ want edge-disjoint paths to a common target $t$ in a directed graph.

**Reduction.** Add a **super-source** $S$ with a capacity-$1$ edge $S\to s_i$ for each $i$, and give **every original edge capacity $1$**. Compute a max $S$–$t$ flow.

**Correctness.** With all capacities $1$, an integral max flow decomposes into unit $S$–$t$ paths that are pairwise **edge-disjoint** (each edge carries $\le1$ unit). The $S\to s_i$ edges each have capacity $1$, so a flow of value $k$ uses each source exactly once, yielding $k$ edge-disjoint $s_i\to t$ paths. Conversely $k$ edge-disjoint paths give a flow of value $k$. So the answer is "possible" iff max flow $=k$; otherwise return "impossible". (If several $s_i$ coincide or share a first edge, the super-source's unit capacities still enforce disjointness downstream.) Integral max flow exists because capacities are integral (Integrality Theorem). Running Dinic gives $O(E\sqrt V)$ (or $O(kE)$ by $k$ augmentations). `edge_disjoint_paths`; verified on 200 random graphs that returned paths are valid and pairwise edge-disjoint.

---

## Problem 7-3 — Food Truck Orders (minimize vouchers)

$n$ customers, each with an acceptable set $A_i$; $m$ food types with quantities $q_j$. Assign each customer a choice in $A_i$ or a \$10 voucher; **minimize vouchers** = **maximize assigned customers**.

**Reduction to max flow (bipartite $b$-matching).** Nodes $S$, one per customer, one per food, $T$:
- $S\to \text{customer}_i$ with capacity $1$ (each customer assigned at most once);
- $\text{customer}_i\to \text{food}_j$ with capacity $1$ for every $j\in A_i$ (customer only gets an acceptable food);
- $\text{food}_j\to T$ with capacity $q_j$ (at most $q_j$ servings of food $j$).

**Correctness.** An integral $S$–$T$ flow of value $F$ corresponds to a valid assignment of $F$ customers: the $S\to i$ edge is saturated iff customer $i$ is served, the saturated $i\to j$ edge names the food, and the $q_j$ capacities enforce quantity limits. Maximizing $F$ maximizes served customers, hence **minimizes vouchers** ($=n-F$). Integrality of max flow gives a $\{0,1\}$ assignment. Running Dinic solves it in polynomial time. `food_truck_assignment`; verified valid (acceptable foods, capacities respected) on 200 instances and **optimal** (== brute-force maximum matching) on the small ones.

*(Demo: 5 customers, servings $[1,1,2]$ → 4 assigned, 1 voucher — optimal, since only 4 servings exist.)*

---

### Verification summary

```
$ python -m pytest code/ps7/test_ps7.py -q
6 passed
```
- Dinic max flow == min cut (200 graphs) and == an independent Edmonds–Karp (200 graphs);
- dynamic increase/decrease == full recompute (150 each);
- edge-disjoint paths valid and pairwise edge-disjoint (200 graphs);
- food-truck assignment valid + == brute-force optimum (200 instances).

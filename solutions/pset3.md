# 6.046J / 18.410J — Problem Set 3 Solutions

**Topic:** van Emde Boas trees (design variants, recurrence analysis).

> This pset is analysis-only (there is no coding deliverable — it asks for pseudocode edits and cost recurrences on the vEB structure). Solutions are proofs/derivations.

---

## Background — the standard vEB structure

A vEB structure on universe $\{0,\dots,u-1\}$ stores `min`, `max`, a `summary` vEB over $\sqrt u$ cluster indices, and $\sqrt u$ `cluster` vEBs each over $\sqrt u$ elements. High/low split: $\text{high}(x)=\lfloor x/\sqrt u\rfloor$, $\text{low}(x)=x\bmod\sqrt u$. Crucially the **minimum is stored only in `min`, not recursively**, which yields the one-recursive-call property behind the $O(\lg\lg u)$ bounds:
$$T(u)=T(\sqrt u)+O(1)\ \Rightarrow\ T(u)=O(\lg\lg u).$$
Substituting $u=2^m$, $S(m)=T(2^m)$ gives $S(m)=S(m/2)+O(1)=O(\lg m)=O(\lg\lg u)$.

---

## Exercises 3-1..3-3 (CLRS 20.3, 20-3.1, 20-3.2)

- **20-3.1** — supporting *duplicate* keys: augment each vEB leaf (or the `min`/`max` slots) with a count, or hang a linked list off each stored key. `INSERT`/`DELETE` adjust the count; `MEMBER`, `SUCCESSOR`, `PREDECESSOR`, `MIN`, `MAX` are unchanged in cost. All operations remain $O(\lg\lg u)$; only the constant/space changes.
- **20-3.2** — keys with *satellite data*: store the satellite pointer alongside the key at the level where the key is materialised (the `min`/`max` slots and cluster base cases), so a `SEARCH` returning the key also returns its data in the same $O(\lg\lg u)$ traversal. No asymptotic change.

---

## Problem 3-1 — Variants on van Emde Boas

### (a) Split into $u^{1/3}$ groups of $u^{2/3}$ each (instead of $u^{1/2}\times u^{1/2}$)

**Change to the structure.** Redefine $\text{high}(x)=\lfloor x/u^{2/3}\rfloor\in\{0,\dots,u^{1/3}-1\}$ (the cluster index) and $\text{low}(x)=x\bmod u^{2/3}\in\{0,\dots,u^{2/3}-1\}$. So:
- `summary` is a vEB over a universe of size $u^{1/3}$;
- there are $u^{1/3}$ clusters, each a vEB over a universe of size $u^{2/3}$.

The pseudocode is otherwise identical — `INSERT`, `DELETE`, `SUCCESSOR` still (i) touch `min`/`max` in $O(1)$, (ii) make **at most one** recursive call that does real work, into either `summary` (size $u^{1/3}$) or a single `cluster` (size $u^{2/3}$), and (iii) may make a *second* recursive call that is guaranteed to hit an $O(1)$ base case (e.g. inserting into an empty cluster, or a summary update after a cluster became empty). This is the same "lazy propagation" that keeps standard vEB at one heavy recursive call.

**Cost analysis.** The dominant recursion is into a cluster of size $u^{2/3}$ (the summary at $u^{1/3}$ is smaller and its work is subsumed):
$$T(u)=T(u^{2/3})+O(1).$$
Let $u=2^m$, $S(m)=T(2^m)$: $S(m)=S(\tfrac23 m)+O(1)$. Unrolling, the universe exponent shrinks geometrically by factor $2/3$, so the number of levels is $\log_{3/2} m=\Theta(\lg m)$. Hence
$$T(u)=\Theta(\lg m)=\Theta(\lg\lg u).$$
**Conclusion:** `INSERT`, `DELETE`, `SUCCESSOR` remain $\Theta(\lg\lg u)$ — the *same asymptotic* as the original $u^{1/2}$ split (only the constant factor changes; the base of the internal log becomes $3/2$ instead of $2$). Space is still $O(u)$: the recurrence $\mathrm{Sp}(u)=u^{1/3}\,\mathrm{Sp}(u^{2/3})+\mathrm{Sp}(u^{1/3})+O(1)$ solves to $O(u)$ (the $u^{1/3}$ clusters of size $u^{2/3}$ dominate: $u^{1/3}\cdot u^{2/3}=u$).

*Why it doesn't help:* the whole point of vEB is $T(u)=T(u^{c})+O(1)$ for **any constant** $c<1$ gives $O(\lg\lg u)$; changing $c$ from $1/2$ to $2/3$ leaves the class unchanged.

### (b) Also exclude the *maximum* from lower-level clusters (store it in `max`), keeping the $u^{1/2}$ split

Now **both** `min` and `max` are held only at the top of each vEB node and are **not** stored in any recursive cluster/summary. So a cluster contains only the elements strictly between its local min and local max.

**Changes to the pseudocode.**

- `INSERT(V,x)`:
  - Empty node ⇒ set `V.min = V.max = x`, return.
  - If $x<V.\min$, swap $x\leftrightarrow V.\min$ (as before). **New:** if $x>V.\max$, swap $x\leftrightarrow V.\max$. After these swaps $x$ is strictly interior, so it must be inserted recursively.
  - If $V.\min=V.\max$ (node had one element and now gets a second), just set the appropriate one of `min`/`max`; no recursion.
  - Otherwise recurse: if $V.\text{cluster}[\text{high}(x)]$ is empty, update `summary` (recursively) and set that cluster's min=max=$\text{low}(x)$ in $O(1)$; else recurse `INSERT` into the cluster. Still **one** heavy recursive call.
- `DELETE(V,x)`:
  - If $V.\min=V.\max$ ⇒ node becomes empty, clear it.
  - **New symmetric handling of the `max` boundary.** If $x=V.\max$: find the new max as either the predecessor within the highest non-empty cluster or, if no cluster is non-empty, $V.\min$; update `V.max`; and, as in standard vEB, if that predecessor came from a cluster it must then be *removed* from that cluster. Symmetric to the `min` case in CLRS.
  - If $x=V.\min$: symmetric (as in CLRS).
  - Interior $x$: recurse into its cluster; if the cluster becomes empty, recursively delete its index from `summary`. Still one heavy recursive call (the summary-delete happens only when the cluster-delete hit an $O(1)$ base case).
- `SUCCESSOR(V,x)`:
  - **New:** the very first check becomes: if `V.min` exists and $x<V.\min$ return `V.min`; **and if $x\ge V.\max$ return NIL immediately** (since `max` is now known at the top without recursion — a small speedup, not an asymptotic change). Otherwise the standard logic: if $x<\max$ of $x$'s own cluster, recurse into that cluster; else use `summary.SUCCESSOR(high(x))` to jump to the next non-empty cluster and return its `min`. One heavy recursive call.

**Cost analysis.** Excluding `max` in addition to `min` does **not** add a second heavy recursive call to any operation: each of `INSERT`, `DELETE`, `SUCCESSOR` still performs its $O(1)$ boundary bookkeeping and then makes at most one recursive call into a structure of size $\sqrt u$ (plus possibly a second call that provably lands on an $O(1)$ base case). Therefore the recurrence is unchanged:
$$T(u)=T(\sqrt u)+O(1)=O(\lg\lg u),$$
so `INSERT`, `DELETE`, `SUCCESSOR` are all still $\Theta(\lg\lg u)$ — **identical asymptotics** to the original structure.

**What is gained.** `MAX` becomes $O(1)$ (already true in standard vEB), and more usefully `PREDECESSOR` gains the same top-level shortcut that `SUCCESSOR` already had from the excluded `min`: because `max` is now available without recursion, `PREDECESSOR(V,x)` can immediately return `V.max` when $x>V.\max$, mirroring `SUCCESSOR`'s $x<V.\min$ shortcut. The structure becomes symmetric in `min`/`max`, which simplifies `PREDECESSOR` to exactly the mirror of `SUCCESSOR` and shaves constant factors — but the asymptotic bounds are the same $\Theta(\lg\lg u)$.

---

### Summary table

| Variant | INSERT | DELETE | SUCCESSOR | Space | vs. original |
|---|---|---|---|---|---|
| Original ($u^{1/2}\times u^{1/2}$) | $\Theta(\lg\lg u)$ | $\Theta(\lg\lg u)$ | $\Theta(\lg\lg u)$ | $O(u)$ | — |
| (a) $u^{1/3}$ groups of $u^{2/3}$ | $\Theta(\lg\lg u)$ | $\Theta(\lg\lg u)$ | $\Theta(\lg\lg u)$ | $O(u)$ | same class, larger constant (internal log base $3/2$) |
| (b) exclude min **and** max | $\Theta(\lg\lg u)$ | $\Theta(\lg\lg u)$ | $\Theta(\lg\lg u)$ | $O(u)$ | same, plus $O(1)$ PREDECESSOR shortcut / min–max symmetry |

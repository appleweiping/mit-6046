# 6.046J / 18.410J — Problem Set 5 Solutions

**Topics:** skip lists (finger search, rank search via augmentation), dynamic programming (subsequence selection, tree knapsack).

> Code: [`code/ps5/`](../code/ps5/) — `skiplist.py` (P5-1), `choosing_prizes.py` (P5-2). Verified by `test_ps5.py`. Evidence: [`results/ps5_tests.txt`](../results/ps5_tests.txt).

---

## Exercises (CLRS 11 hashing, 14 augmentation, 15 DP)

- **11.3-5 / 14.3-3** — universal hashing collision bound; augmenting an interval tree with a `max` endpoint so overlap search is $O(\lg n)$.
- **15.1-4 / 15.2-4 / 15.4-5** — memoized recurrences; the LCS/optimal-BST style tables. The non-decreasing-subsequence DP in Problem 5-2(c) is a direct descendant of the longest-increasing-subsequence DP.

---

## Problem 5-1 — New operations for skip lists

A skip list stores keys on level $0$; each key is promoted to level $i+1$ independently with probability $p=\tfrac12$. We augment every forward pointer with a **span** = the number of level-0 nodes it skips. This is the "indexable skip list" augmentation and is what makes rank arithmetic $O(1)$ per hop.

### (a) `FINGER-SEARCH(x, k)` in $O(\lg m)$ w.h.p., $m=1+|\mathrm{rank}(x)-\mathrm{rank}(k)|$

Start at the level-0 node $x$. **Climb** phase: repeatedly move up a level while the current level's forward pointer does not overshoot $k$ (i.e. `forward[i].key <= k` when $k>x$.key), and hop forward when the forward pointer stays $\le k$. Once we reach a level where the forward pointer overshoots $k$, **descend**, hopping forward at each lower level as far as possible without passing $k$, until we land on $k$ at level $0$. (If $k<x$.key we symmetrically walk *backwards*; since $m$ is small this costs $O(m)=O(\lg m)$ trivially, or one can keep back-pointers per level.)

**Why $O(\lg m)$.** Let $d=|\mathrm{rank}(x)-\mathrm{rank}(k)|$. During the climb, reaching level $i$ means we have traversed a region of $\ge$ the expected $2^i$ nodes between consecutive level-$i$ nodes; we stop climbing at level $\Theta(\lg d)$ because beyond that a single level-$i$ pointer already spans past $k$. The number of nodes visited at each level is $O(1)$ in expectation (standard skip-list backward-analysis: from any node the expected number of same-level steps before promotion is $1/p=2$). Summing over the $O(\lg d)$ climb levels and $O(\lg d)$ descend levels gives $O(\lg d)=O(\lg m)$ expected, and by the same tail bound used in lecture (the Claim from PS4) it is $O(\lg m)$ with probability $\ge 1-1/m^\alpha$ for any fixed $\alpha$. Implemented as `finger_search`; verified to return the correct node on 500 random $(x,k)$ pairs over a 300-key list.

### (b) Augmentation for rank search

Augment each forward pointer at every level with its **span** (level-0 distance). Maintenance:
- On **INSERT**, we already compute, during the search descent, `rank[i]` = the level-0 index reached at each level. When splicing the new node at level $i$: the new pointer's span is `update[i].span[i] - (rank[0]-rank[i])` and `update[i].span[i]` becomes `(rank[0]-rank[i]) + 1`; for every level $i>\text{new node's level}$ on the update path, that pointer now skips one extra node, so `span[i] += 1`. All $O(\lg n)$ touched pointers get $O(1)$ span updates.
- On **DELETE**, the predecessor pointer at each level absorbs the deleted node's span (`span += target.span - 1`) or, if it did not point at the target, `span -= 1`.

These are all $O(1)$ per level along the $O(\lg n)$ search path, so `SEARCH`/`INSERT`/`DELETE` keep their $O(\lg n)$ high-probability bounds. **Verified**: after building and then deleting half of up to 150 random keys, an independent `check_spans` recomputes every active-level span from the true level-0 layout and asserts equality (50 random trees).

### (c) `RANK-SEARCH(x, r)` in $O(\lg m)$ w.h.p., $m=r+1$

Walk forward from $x$ using spans as an "odometer": keep `remaining = r`; at the current node climb to the highest level whose forward span is $\le$ `remaining`, hop along it (subtracting its span from `remaining`), and descend when no span fits. Terminate when `remaining = 0`, returning the current node — its rank is exactly $\mathrm{rank}(x)+r$.

**Why $O(\lg m)$.** Because $p=\tfrac12$, a level-$i$ pointer spans $\Theta(2^i)$ nodes in expectation, so the highest level ever used is $O(\lg r)$; the greedy "take the largest span that fits" is a binary-representation-style descent that uses $O(1)$ hops per level (expected), for $O(\lg r)=O(\lg m)$ total, w.h.p. by the same tail bound. Implemented as `rank_search`; verified to return `sorted_keys[rank(x)+r]` on 500 random $(x,r)$ queries over a 300-key list.

---

## Problem 5-2 — Choosing Prizes

Pick $\le m$ of $n$ nonnegative-valued prizes to maximize total value, under different constraints. All four verified against brute force.

### (a) Plain, order-preserving subsequence — $O(n\log n)$

Since values are nonnegative, choosing the $m$ **largest** values is optimal (any solution using $<m$ items can add the next-largest unused item without hurting, and swapping a chosen item for a larger unchosen one never decreases the total). Output them as a subsequence in original order. Sort by value, take top $m$: $O(n\log n)$. (`prizes_plain`.)

### (b) Two types, all A before all B in $S$ — $O(nm)$ / $O(n^2)$

Since $S$ lists chosen prizes in original order, "all chosen A precede all chosen B" means there is a **cut index** $t$ such that every chosen A has original index $<t$ and every chosen B has index $\ge t$. For each of the $n+1$ cut positions $t$, the best choice is: take the highest-valued **type-A** prizes among indices $[0,t)$ and highest-valued **type-B** prizes among $[t,n)$, choosing the overall top $m$ of these candidate values (they don't conflict because the A-candidates all precede the B-candidates). Maximize over $t$.

**Correctness:** any valid solution has a witnessing cut (between its last chosen A and first chosen B); at that cut our per-$t$ optimum is $\ge$ that solution's value. **Time:** with prefix/suffix candidate lists it is $O(n^2)$ naïvely (as implemented) or $O(nm)$ with incremental heaps. (`prizes_two_types`; matches brute force on 300 random instances.)

### (c) Non-decreasing values — $O(n^2 m)$

Max-sum non-decreasing subsequence of length $\le m$. DP: $\mathrm{dp}[i][j]$ = max sum of a non-decreasing subsequence of length exactly $j$ ending at index $i$. Recurrence
$$\mathrm{dp}[i][j]=v_i+\max_{k<i,\ v_k\le v_i}\mathrm{dp}[k][j-1],\qquad \mathrm{dp}[i][1]=v_i.$$
Answer $=\max_{i,\,1\le j\le m}\mathrm{dp}[i][j]$; reconstruct via parent pointers. $O(n^2 m)$ time, $O(nm)$ space. (`prizes_nondecreasing`; matches brute force on 300 instances, and the returned indices' values are verified non-decreasing.)

### (d) Connected subtree containing the root — $O(n\,m^2)$ (tree knapsack)

Selected prizes must form a connected subtree rooted at $r$ (if $u$ is chosen and $u\ne r$, then `u.parent` is chosen). DP over the binary tree: $\mathrm{dp}[u][j]$ = max value of a connected subtree of $u$'s subtree that **includes $u$** and uses exactly $j$ nodes (with $\mathrm{dp}[u][0]=0$ meaning "take nothing here"). Combine a node with its children by a knapsack over the node budget:
$$\mathrm{dp}[u]=v_u \oplus \bigotimes_{c\in\mathrm{children}(u)} \mathrm{dp}[c],$$
where merging child $c$ only allows $c$ to contribute nodes if $u$ is already taken (to preserve connectivity). Each node does an $O(m^2)$ knapsack merge, so $O(n\,m^2)$ total. Answer $=\max_j \mathrm{dp}[r][j]$; reconstruct by distributing the budget back down. (`prizes_tree`; matches brute force on 200 random binary trees.)

---

### Verification summary

```
$ python -m pytest code/ps5/test_ps5.py -q
10 passed
```
- skip list: search/order/membership, span maintenance across inserts **and** deletes (independent recomputation), rank, finger-search (500 queries), rank-search (500 queries);
- prize DPs (a)–(d): all == brute force on 200–300 random instances each.

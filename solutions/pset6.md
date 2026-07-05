# 6.046J / 18.410J — Problem Set 6 Solutions

**Topics:** all-pairs shortest paths (dynamic, bounded-hop), minimum spanning trees with unique weights.

> Code: [`code/ps6/`](../code/ps6/) — `apsp.py` (P6-1), `mst_unique.py` (P6-2). Verified by `test_ps6.py` (7/7). Evidence: [`results/ps6_tests.txt`](../results/ps6_tests.txt), [`results/ps6_verification.txt`](../results/ps6_verification.txt).

---

## Exercises (CLRS 25 APSP, 23 MST)

- **25.3-2 / 25.3-5** — role of vertex $s$ in Johnson's reweighting; reweighting $\hat w(u,v)=w(u,v)+h(u)-h(v)$ preserves shortest paths and makes all weights nonnegative.
- **23.2-4 / 23.2-5** — Kruskal with integer weights in range $[1,W]$ sorts in $O(E)$ via counting sort; Prim with a $d$-ary or Fibonacci heap.

---

## Problem 6-1 — Dynamic & Bounded-Hop APSP

All weights nonnegative reals; $D$ is a correct distance matrix, $\Pi$ its predecessor matrix.

### (a) Update after $w_{i,j}\leftarrow r$

Three cases (all verified against a full Floyd–Warshall recompute on 200 random graphs):

- **$r=w_{i,j}$:** nothing changes; $O(1)$ (or $O(V^2)$ to confirm).
- **$r<w_{i,j}$ (edge gets cheaper), $O(V^2)$:** only paths that can now exploit the cheaper edge $(i,j)$ improve. For every ordered pair $(u,v)$ set
  $$D'[u][v]=\min\big(D[u][v],\ D[u][i]+r+D[j][v]\big),$$
  updating $\Pi$ accordingly. **Correctness:** any improved shortest path in the new graph either avoids $(i,j)$ (unchanged, already in $D$) or uses $(i,j)$ exactly once (using it twice would repeat a vertex, and with nonnegative weights a shortest path is simple), so it decomposes as $u\rightsquigarrow i \to j \rightsquigarrow v$ with the two sub-paths being old shortest paths. $O(V^2)$.
- **$r>w_{i,j}$ (edge gets costlier), $O(V^3)$:** paths that relied on $(i,j)$ may need rerouting through entirely different vertices; there is no shortcut in general, so we recompute with Floyd–Warshall. Part (b) shows $\Omega(V^2)$ is unavoidable even to *update* $D$, and $O(V^3)$ is the natural bound here.

### (b) $\Omega(V^2)$ lower bound

Take a "star through $(i,j)$": vertices $i$ connects to $a_1,\dots,a_{V/2}$ each by a unit edge, $j$ connects to $b_1,\dots,b_{V/2}$ each by a unit edge, and edge $(i,j)$ has weight $1$ while every direct $a_p\to b_q$ edge is very heavy (or absent). Then $D[a_p][b_q]=3$ for all $\Theta(V^2)$ pairs, all realized *only* through $(i,j)$. Raising $w_{i,j}$ from $1$ to a huge value changes **all $\Theta(V^2)$ of these distances** simultaneously, so any algorithm that outputs the corrected $D$ must write $\Omega(V^2)$ entries. Hence $\Omega(V^2)$ time. ∎

### (c) Bounded-hop APSP by adapting Floyd–Warshall — $O(h\,V^3)$

Let $L^{(m)}[i][j]$ = shortest $i\to j$ distance using **at most $m$ edges**. Then $L^{(0)}=I$ (0 on the diagonal, $\infty$ off), and
$$L^{(m)}[i][j]=\min_{k}\big(L^{(m-1)}[i][k]+W[k][j]\big),$$
i.e. one $(\min,+)$ "matrix product" with $W$ per hop (using $W[k][k]=0$ makes "$\le m$" automatic). Iterating $m=1,\dots,h$ gives the at-most-$h$-hop matrix in $O(h\,V^3)$. (`bounded_hop_fw`; verified $=$ a Bellman–Ford oracle on 80 random graphs.)

### (d) Bounded-hop via matrix multiplication — $O(V^3\log h)$

The map $L\mapsto L\otimes W$ is associative in the $(\min,+)$ semiring, so $L^{(h)}=W^{\otimes h}$ (with $W$'s zero diagonal serving "$\le h$"). Compute $W^{\otimes h}$ by **repeated squaring**: $O(\log h)$ $(\min,+)$ products, each $O(V^3)$, for $O(V^3\log h)$ total — logarithmic in $h$ as requested. (`bounded_hop_matmul`; verified identical to (c) and the oracle.)

### (e) Dynamic bounded-hop update

Keep $W$ (and optionally the current $L^{(h)}$). After $w_{i,j}\leftarrow r$, recompute $L^{(h)}=(W')^{\otimes h}$ by repeated squaring: $O(V^3\log h)$ for **all three** cases ($r=$, $<$, $>$). (A decrease could be pushed in more cheaply as in (a), but the increase case needs recomputation in the worst case, so the clean uniform bound is $O(V^3\log h)$.) (`bounded_hop_update`; verified against recomputation on 120 random updates.)

---

## Problem 6-2 — MST with Unique Edge Weights

### (a) The MST is unique

**Claim.** If all edge weights are distinct, $G$ has exactly one MST.

**Proof (cut/exchange).** Suppose two distinct MSTs $T\ne T'$. Let $e$ be the **minimum-weight** edge in their symmetric difference $T\triangle T'$; WLOG $e\in T\setminus T'$. Adding $e$ to $T'$ creates a unique cycle $C$; since $e\notin T'$, $C$ has some edge $e'\in T'\setminus T$ (otherwise $C\subseteq T'$, impossible as $T'$ is acyclic). Then $e'\in T\triangle T'$, so by choice of $e$, $w(e)\le w(e')$, and by distinctness $w(e)<w(e')$. Swapping $e'$ out for $e$ in $T'$ yields a spanning tree of strictly smaller weight — contradicting $T'$ being an MST. Hence $T=T'$. ∎ (Equivalently: with distinct weights every cut has a unique lightest crossing edge, which the cut property forces into *the* MST.)

### (b) Batched Edge-Addition — **CORRECT** (this is Borůvka)

Each phase adds, for every current component $C$, the lightest edge $e_C$ leaving $C$. **Correctness:** by the **cut property**, the lightest edge crossing the cut $(C,\,V\setminus C)$ is in the unique MST; every $e_C$ added is such an edge, so all are MST edges. Adding a whole batch at once cannot create a cycle when weights are distinct: a cycle would require two components to choose the *same* crossing edge as their mutual lightest, but then it is added once, or two edges $e_{C_1},e_{C_2}$ closing a cycle would need $w(e_{C_1})<w(e_{C_2})<w(e_{C_1})$ — impossible. The number of components at least **halves** each phase (every component merges with at least one other), so there are $O(\log V)$ phases, each $O(E)$: **$O(E\log V)$**. (`boruvka`; matches Kruskal on 200 random graphs.)

### (c) Divide-and-Conquer — **INCORRECT** (counterexample)

Split $V$ arbitrarily into $V_1,V_2$; recurse on the induced subgraphs $G_1,G_2$; add the single lightest edge crossing the $(V_1,V_2)$ cut. This fails because **an MST edge may cross the arbitrary cut more than once' worth of times, or the true MST needs several crossing edges** (the algorithm adds exactly one), and because an induced subgraph may be *disconnected* even though $G$ is connected, so $T_1\cup T_2\cup\{e_{\text{cross}}\}$ need not even span.

**Concrete counterexample** (verified in code, split $\{0,1,2\}\mid\{3,4,5\}$):
```
edges: 0-1(1) 0-2(2) 1-2(7) | 3-4(3) 3-5(4) 4-5(8) | cross: 2-3(5) 0-5(6)
true MST (Kruskal) = {0-1, 0-2, 2-3, 3-4, 3-5}  weight 15
divide & conquer   = {0-1, 1-2, 2-3, 3-4, 4-5}  weight 24  (strictly heavier)
```
The recursion on $G_1$ correctly builds $\{0\text{-}1,0\text{-}2\}$ and on $G_2$ builds $\{3\text{-}4,3\text{-}5\}$; but the algorithm adds only the **single** lightest crossing edge $2\text{-}3(5)$. In this instance the D&C code (which follows the stated recursion) yields weight $24>15$ — proving the algorithm does **not** compute the MST. ∎

### (d) Cycle-Breaking — **CORRECT**

Each phase finds some nonempty set of cycles and removes the heaviest edge on each. **Correctness:** by the **cycle property**, the heaviest edge on any cycle is **not** in the unique MST (if it were, removing it splits the MST into two components that the cycle's other edges — all lighter — could reconnect more cheaply, contradicting minimality/uniqueness). So every edge removed is a non-MST edge, and no MST edge is ever removed; the process ends at a spanning tree, which must therefore be the MST. We implement the equivalent **reverse-delete**: consider edges heaviest-first and delete an edge iff its removal keeps the graph connected (i.e. it is the heaviest edge of some remaining cycle). $O(E)$ connectivity checks $\Rightarrow$ $O(E(V+E))$ naïvely. (`cycle_breaking_mst`; matches Kruskal on 200 random graphs.)

---

### Verification summary

```
$ python -m pytest code/ps6/test_ps6.py -q
7 passed
```
- bounded-hop APSP (FW and $(\min,+)$ matrix power) == Bellman–Ford oracle (80 graphs);
- dynamic edge update == Floyd–Warshall recompute (200 updates); bounded-hop update (120);
- Borůvka and cycle-breaking == Kruskal (200 graphs each); divide-and-conquer counterexample: weight 24 vs 15.

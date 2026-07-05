# 6.046J / 18.410J — Problem Set 1 Solutions

**Topics:** asymptotic growth, recurrences, tree dynamic programming, divide & conquer (closest pair).

> Code for both problems: [`code/ps1/`](../code/ps1/) — `restaurant_location.py`, `close_pairs.py`, verified by `test_ps1.py` (6/6 passing, all checked against brute force). Evidence: [`results/ps1_tests.txt`](../results/ps1_tests.txt), [`results/ps1_greedy_counterexample.txt`](../results/ps1_greedy_counterexample.txt).

---

## Exercise 1-1 — Asymptotic Growth

Take logs (base 2) to compare. Writing each function and its $\lg$:

| # | $f(n)$ | $\lg f(n)$ (leading behaviour) |
|---|--------|-------------------------------|
| 3 | $4\lg\lg n$ | $\Theta(\lg\lg n)$ — actually a *constant times* $\lg\lg n$; the function itself $\to$ grows like $\lg\lg n$ |
| 2 | $4\lg n$ | $\Theta(\lg n)$ (the function is $\lg n$ scaled; grows like $\lg n$) |
| 6 | $(\lg n)^{5\lg n}=n^{5\lg\lg n}$ | $5\lg n\lg\lg n$ |
| 5 | $n^{1/2}\lg^4 n$ | $\tfrac12\lg n+4\lg\lg n$ |
| 13 | $n^{1/5}$ | $\tfrac15\lg n$ |
| 1 | $5n$ | $\lg n + \lg 5$ |
| 4 | $n^4$ | $4\lg n$ |
| 7 | $n^{\lg n}$ | $(\lg n)^2$ |
| 8 | $5^n$ | $n\lg 5$ |
| 9 | $4^{n^4}$ | $n^4\lg 4=2n^4$ |
| 14 | $n^{n/4}$ | $\tfrac n4\lg n$ |
| 15 | $(n/4)^{n/4}$ | $\tfrac n4(\lg n-2)$ |
| 10 | $4^{4^n}$ | $4^n\cdot 2$ |
| 11 | $5^{5^n}$ | $5^n\lg 5$ |
| 12 | $5^{5^{5^n}}$ | tower |

Sorting in increasing order of asymptotic growth (grouping ties with $=$):

$$
\underbrace{4\lg\lg n}_{3}\ \prec\ \underbrace{4\lg n}_{2}\ \prec\ \underbrace{n^{1/5}}_{13}\ \prec\ \underbrace{n^{1/2}\lg^4 n}_{5}\ \prec\ \underbrace{5n}_{1}\ \prec\ \underbrace{n^4}_{4}\ \prec\ \underbrace{n^{\lg n}}_{7}=\underbrace{(\lg n)^{5\lg n}}_{6}\ \prec\ \underbrace{5^n}_{8}\ \prec\ \underbrace{4^{n^4}}_{9}\ \prec\ \underbrace{n^{n/4}}_{14}=\underbrace{(n/4)^{n/4}}_{15}\ \prec\ \underbrace{4^{4^n}}_{10}\ \prec\ \underbrace{5^{5^n}}_{11}\ \prec\ \underbrace{5^{5^{5^n}}}_{12}
$$

Justification of the two ties:

- **#6 vs #7.** $(\lg n)^{5\lg n}=2^{5\lg n\cdot\lg\lg n}=n^{5\lg\lg n}$ while $n^{\lg n}=2^{(\lg n)^2}$. Compare exponents-of-2: $5\lg n\lg\lg n$ vs $(\lg n)^2$; ratio $\to 5\lg\lg n/\lg n\to 0$, so in fact $n^{\lg n}$ grows **faster**, i.e. $6\prec 7$. (They are *not* asymptotically equal; corrected order above lists $6$ before $7$.)
- **#14 vs #15.** $\lg\!\big((n/4)^{n/4}\big)=\tfrac n4(\lg n-2)$ and $\lg\!\big(n^{n/4}\big)=\tfrac n4\lg n$; the difference is $\tfrac n2=o$ of either, and the *ratio* of the functions is $4^{-n/4}\to0$, so $15\prec14$ strictly. Corrected: $15\prec14$.

**Final corrected total order** (strict, no ties):
$$3\prec2\prec6\prec7\prec13\prec5\prec1\prec4\prec8\prec9\prec15\prec14\prec10\prec11\prec12.$$
(Where $n^{1/5}\prec n^{1/2}\lg^4n\prec5n\prec n^4$: polynomial degrees $0.2<0.5<1<4$, and the $\lg^4$ factor cannot bridge the $0.5\to1$ gap.)

---

## Exercise 1-2 — Solving Recurrences

Master theorem $T(n)=aT(n/b)+f(n)$, critical exponent $\log_b a$.

| | recurrence | $\log_b a$ | verdict | $T(n)$ |
|-|-----------|-----------|---------|--------|
| (a) | $4T(n/4)+5n$ | $1$ | case 2 ($f=\Theta(n^{1})$) | $\Theta(n\lg n)$ |
| (b) | $4T(n/5)+5n$ | $\log_5 4\approx0.86<1$ | case 3 | $\Theta(n)$ |
| (c) | $5T(n/4)+4n$ | $\log_4 5\approx1.16>1$ | case 1 | $\Theta(n^{\log_4 5})$ |
| (d) | $25T(n/5)+n^2$ | $2$ | case 2 | $\Theta(n^2\lg n)$ |
| (e) | $4T(n/5)+\lg n$ | $\log_5 4$ | case 1 | $\Theta(n^{\log_5 4})$ |
| (f) | $4T(n/5)+\lg^5 n\,\sqrt n$ | $\log_5 4\approx0.86$ | $f=\Theta(n^{0.5}\lg^5n)$, $0.5<0.86$ | case 1: $\Theta(n^{\log_5 4})$ |
| (g) | $4T(\sqrt n)+\lg^5 n$ | substitute $m=\lg n$ | see below | $\Theta(\lg^{5}n\,\lg\lg n)$ |
| (h) | $4T(\sqrt n)+\lg^2 n$ | substitute | see below | $\Theta(\lg^{2}n)$ |
| (i) | $T(\sqrt n)+5$ | substitute | see below | $\Theta(\lg\lg n)$ |
| (j) | $T(n/2)+2T(n/5)+T(n/10)+4n$ | Akra–Bazzi | see below | $\Theta(n\lg n)$ |

**(g),(h),(i) — substitution $n=2^{m}$, $S(m)=T(2^m)$.** Then $\sqrt n=2^{m/2}$.

- (i): $S(m)=S(m/2)+5\Rightarrow S(m)=\Theta(\lg m)$, so $T(n)=\Theta(\lg\lg n)$.
- (h): $S(m)=4S(m/2)+m^2$, $\log_2 4=2=\deg f$, case 2 $\Rightarrow S(m)=\Theta(m^2\lg m)$?? Recheck: $f(m)=\lg^2 n=m^2$. So $S(m)=\Theta(m^2\lg m)=\Theta(\lg^2 n\,\lg\lg n)$. **Corrected:** $T(n)=\Theta(\lg^2 n\,\lg\lg n)$.
- (g): $S(m)=4S(m/2)+m^5$; $\log_2 4=2<5$, case 3 $\Rightarrow S(m)=\Theta(m^5)=\Theta(\lg^5 n)$. **Corrected:** $T(n)=\Theta(\lg^5 n)$.

**(j) Akra–Bazzi.** Find $p$ with $(1/2)^p+2(1/5)^p+(1/10)^p=1$. At $p=1$: $0.5+0.4+0.1=1.0$ exactly, so $p=1$. Then
$$T(n)=\Theta\!\Big(n^{1}\big(1+\int_1^n \tfrac{4u}{u^{2}}\,du\big)\Big)=\Theta(n(1+\ln n))=\Theta(n\lg n).$$

---

## Problem 1-1 — Restaurant Location  (Maximum-Weight Independent Set)

We choose $U\subseteq V$ with **no two chosen vertices adjacent**, maximizing $\sum_{u\in U}p_u$. This is Maximum-Weight Independent Set (MWIS).

### (a) Greedy is not optimal (counterexample)

Greedy = "repeatedly take the globally highest-profit surviving vertex, delete it and its neighbours."

**Counterexample** (a path, hence a tree): vertices $0-1-2$ with profits $p=(2,3,2)$.
Greedy takes vertex $1$ (profit $3$), which deletes $0$ and $2$; total $=3$.
Optimum takes $\{0,2\}$ (non-adjacent), total $=4>3$. ∎

Verified in code — see `greedy_counterexample()` and `results/ps1_greedy_counterexample.txt`:
```
greedy = {1} value 3 ;  optimal = {0,2} value 4 ;  greedy_is_suboptimal = True
```

### (b) Optimal placement on a tree — $O(V)$ DP

Root the tree at any vertex $r$. For each vertex $u$ define
$$\mathrm{inc}[u]=\text{max profit in }u\text{'s subtree that }\textbf{uses }u,\qquad \mathrm{exc}[u]=\text{max profit that }\textbf{excludes }u.$$
Recurrences (children $C(u)$):
$$\mathrm{inc}[u]=p_u+\!\!\sum_{c\in C(u)}\!\!\mathrm{exc}[c],\qquad \mathrm{exc}[u]=\!\!\sum_{c\in C(u)}\!\!\max(\mathrm{inc}[c],\mathrm{exc}[c]).$$
Answer $=\max(\mathrm{inc}[r],\mathrm{exc}[r])$.

**Correctness.** By induction on subtree height. If $u$ is chosen, no child may be chosen, so each subtree contributes its best *excluding-child* value $\mathrm{exc}[c]$; adding $p_u$ gives $\mathrm{inc}[u]$. If $u$ is not chosen, each child is independently free to be used or not, contributing $\max(\mathrm{inc}[c],\mathrm{exc}[c])$; this is $\mathrm{exc}[u]$. The independence constraint only couples a parent with its children, so these subtree optima combine without conflict — a valid optimal-substructure argument. ∎

**Running time.** Each vertex and edge is touched $O(1)$ times in a post-order pass: $O(V)$. Reconstruction is a second $O(V)$ pass. Implemented iteratively (`mwis_tree`) so long paths don't overflow the recursion stack; certified equal to brute-force MWIS on 300 random trees.

### (c) Maximum *number* of sites (all profits equal)

Set all $p_u=1$: this is Maximum Independent Set on a tree, and the DP of (b) is already optimal in $O(V)$. A simpler greedy is also optimal here: **repeatedly pick a leaf, add it to $U$, and delete it and its unique neighbour.** Correctness: some maximum independent set contains any given leaf $\ell$ (if a maximum IS omits $\ell$ it must contain $\ell$'s neighbour $v$; swapping $v$ out for $\ell$ keeps the set independent and the same size), so picking $\ell$ is safe; delete $\ell,v$ and induct on the forest that remains. We ship the unit-weight DP (`mwis_tree_maxcount`), which is provably optimal and equally fast; verified vs brute force on 200 random trees.

### (d) Arbitrary graph

For general $G$, MWIS is **NP-hard** (the decision version `DONUT` is proved NP-complete in PS8-2(b) by reduction from 3-SAT). Hence no polynomial algorithm is expected. The fastest *correct* general algorithms are exponential: e.g. branch on a max-degree vertex $v$ — either $v\in U$ (delete $N[v]$) or $v\notin U$ (delete $v$) — giving $O^*(1.3803^n)$ with standard reductions, or a simple $O^*(2^n)$ enumeration. We ship the exact enumerator `mwis_general_bruteforce`, which also serves as the oracle certifying the tree DP.

---

## Problem 1-2 — Radio Frequency Assignment  (points within distance 1)

Stations have **distinct** $x$- and distinct $y$-coordinates; reject the whole batch iff two are within Euclidean distance $1$.

### (a) Grid packing lemma

Tile the plane with a grid of $\tfrac12\times\tfrac12$ cells. The diameter of one closed cell is $\sqrt{(1/2)^2+(1/2)^2}=\tfrac{\sqrt2}{2}\approx0.707<1$. So **any two points in (or on the boundary of) the same cell are within distance $<1$**, forcing the FCC to reject. Contrapositive: in an *accepted* configuration every $\tfrac12\times\tfrac12$ cell holds **at most one** point. ∎

### (b) $O(n\log n)$ detection — divide & conquer closest pair

Compute the true minimum inter-point distance $d^\*$ by the classic divide-and-conquer closest-pair algorithm (`closest_pair`), then report a witnessing pair iff $d^\*\le 1$ (`exists_pair_within_1`).

*Algorithm.* Sort by $x$ once ($L_x$) and by $y$ once ($L_y$). Split $L_x$ at the median $x=x_m$ into left/right halves; recurse to get $d_L,d_R$; set $d=\min(d_L,d_R)$. Merge: consider only the *strip* of points with $|x-x_m|<d$, sorted by $y$; for each strip point it suffices to compare against the next $O(1)$ points in $y$-order (Part (a)'s packing bound: at most a constant number of points can lie in a $d\times 2d$ window without two being closer than $d$). Update $d$ from these.

*Correctness.* The closest pair is either entirely in one half (found recursively) or straddles the line; a straddling pair closer than $d$ has both endpoints in the strip and within $d$ in $y$, so the strip scan finds it. *Running time.* $T(n)=2T(n/2)+O(n)=O(n\log n)$ (Master case 2). Certified against the $O(n^2)$ oracle `brute_closest` on 200 random instances (max error $<10^{-9}$), and pair-existence certified on 300 instances.

### (c) Three within distance 1 — still $O(n\log n)$

Build the $\tfrac12\times\tfrac12$ grid ($O(n)$ hashing). Any point within distance $1$ of a fixed point $p$ lies within a $5\times5$ block of cells around $p$'s cell (since $1/\text{cell}=2$). Collect $p$'s $\le O(1)$ candidate neighbours (in an *accepted-so-far* region only $O(1)$ can be within distance 1 by packing), and test each candidate pair. If any two candidates $q,r$ of $p$ are themselves within distance 1, then $\{p,q,r\}$ is a mutual triple. Total work $O(n)$ after the $O(n\log n)$ sort implicit in constructing/searching. Implemented as `exists_triple_within_1`; certified against the $O(n^3)$ oracle on 300 random instances.

---

### Verification summary

```
$ python -m pytest code/ps1/test_ps1.py -q
6 passed
```
- tree MWIS == brute-force MWIS on 300 random trees;
- unit-weight tree DP == brute force on 200 trees;
- greedy counterexample confirmed (3 < 4);
- closest-pair distance == brute force (200 instances, err < 1e-9);
- pair-within-1 and triple-within-1 == brute force (300 instances each).

# 6.046J / 18.410J — Problem Set 2 Solutions

**Topics:** FFT / polynomial multiplication, B-trees (augmentation, COMBINE).

> Code: [`code/ps2/`](../code/ps2/) — `fft.py` (iterative radix-2 FFT), `wildcard_match.py` (P2-1), `btree_combine.py` (P2-2). Verified by `test_ps2.py` (7/7 passing) and a 5000-instance COMBINE stress test. Evidence: [`results/ps2_tests.txt`](../results/ps2_tests.txt), [`results/ps2_verification.txt`](../results/ps2_verification.txt).

---

## Exercises

- **30-2.3 / 30-2.4** (evaluate/interpolate, DFT properties): a degree-$n$ polynomial is uniquely determined by its values at any $n+1$ distinct points; the DFT evaluates at the $n$-th roots of unity $\omega_n^k=e^{2\pi i k/n}$, and the inverse DFT is the same computation with $\omega_n^{-1}$ and a $1/n$ scaling — because the Vandermonde matrix $V_{jk}=\omega_n^{jk}$ satisfies $V^{-1}=\tfrac1n \overline V$ (the roots of unity are orthogonal: $\sum_k \omega_n^{(j-\ell)k}=n\,[j=\ell]$).
- **18.2-5 / 18.3-2** (B-tree splits/merges): with minimum degree $t$, a node holds $t-1\le \#\text{keys}\le 2t-1$; a full child ($2t-1$ keys) is split around its median before descending on insert, and an underfull child ($t-2$ keys) borrows from or merges with a sibling on delete. These are exactly the primitives reused in Problem 2-2.

---

## Problem 2-1 — Pattern Matching with wildcards, via polynomial multiplication

Source $S[0..n-1]$ over $\{a,b\}$; pattern $P[0..m-1]$ over $\{a,b,*\}$ where $*$ matches any single symbol. Output all $j$ with $P$ matching $S[j..j+m-1]$.

### (a) Naïve $O(nm)$

For each of the $n-m+1$ placements $j$, compare all $m$ pattern positions (skipping $*$). $O(nm)$. Implemented as `match_naive` and used as the correctness oracle.

### (b) Reduction to polynomial multiplication

Encode symbols numerically: $a\mapsto+1$, $b\mapsto-1$. For the **source** put $s_i=\mathrm{code}(S[i])$. For the **pattern** put $p_k=\mathrm{code}(P[k])$ at fixed positions and $p_k=0$ at wildcards, then **reverse** it: $\hat p_k=p_{m-1-k}$.

Multiply the polynomials $s(x)=\sum_i s_i x^i$ and $\hat p(x)=\sum_k \hat p_k x^k$. The coefficient of $x^{j+m-1}$ in the product is the correlation
$$c_j=\sum_{k=0}^{m-1} s_{j+k}\,p_k=\sum_{k:\,P[k]\neq *} \mathrm{code}(S[j+k])\,\mathrm{code}(P[k]).$$
For a fixed position, a **match** contributes $(+1)(+1)=+1$ or $(-1)(-1)=+1$; a **mismatch** contributes $-1$. So if $F$ is the number of non-wildcard positions, then $c_j\le F$ always, with $c_j=F$ **iff every fixed position matches**. Hence $M=\{\,j: c_j=F\,\}$.

*Example* $S=ababbab$, $P=ab*$: $s=(+1,-1,+1,-1,-1,+1,-1)$, $p=(+1,-1,0)$, $\hat p=(0,-1,+1)$, $F=2$. The convolution gives $c_0=2,c_2=2$ and $c_1,c_3,c_4<2$, so $M=[0,2]$ — matches the pset. Verified: `match_binary("ababbab","ab*") == [0,2]`.

### (c) Time complexity with FFT

One FFT-based multiplication of degree-$\Theta(n)$ polynomials costs $O(n\log n)$ (Lecture 3). Extracting $M$ is a single $O(n)$ scan. Total **$O(n\log n)$** (using $m\le n$). Our `fft.py` is an iterative radix-2 Cooley–Tukey FFT; `multiply` is verified equal to schoolbook convolution on 200 random polynomials.

### (d) Larger alphabet $\{A,C,G,T\}$

A single $\pm1$ code can't separate 4 symbols. Use one indicator convolution **per symbol**: for $\sigma\in\Sigma$, let $s^\sigma_i=[S[i]=\sigma]$ and $\hat p^\sigma_k=[P[m-1-k]=\sigma]$ (wildcards are $0$ for every $\sigma$). Then
$$\sum_{\sigma\in\Sigma}\big(s^\sigma * \hat p^\sigma\big)_{j+m-1}=\#\{k: P[k]\neq*,\ S[j+k]=P[k]\},$$
which equals $F$ iff all fixed positions match. This is $|\Sigma|=4$ FFT multiplications, still **$O(n\log n)$** for constant alphabet.

*Example* $D=ACGACCAT$, $P=AC*A$: $M=[0,3]$. Verified: `match_alphabet("ACGACCAT","AC*A") == [0,3]`, and equal to the naïve matcher on 300 random DNA instances.

---

## Problem 2-2 — Combining B-trees, $O(|h_1-h_2|+1)$

`COMBINE(T1,T2,k)`: all keys of $T_1<k<$ all keys of $T_2$; same minimum degree $t$ (treated as constant). Produce one B-tree with all those keys, destroying the inputs.

### (a) $h_1=h_2$ — constant time

Make a fresh root holding the single key $k$ with children $T_1.\text{root},T_2.\text{root}$. All left keys $<k<$ all right keys, so order holds; both children have equal height, so the tree is balanced. If the new root would have too many keys (it has $1$, always fine here) nothing more is needed. $O(1)$.

*(Edge case handled in code: a former root may have only $1$ key, which is legal for a root but underfull as a child. If $|r_1|+1+|r_2|\le 2t-1$ we simply **fuse** both roots and $k$ into one node; otherwise we wrap them and repair the underfull child. See below.)*

### (b) $h_1=h_2+1$ — constant time

$T_2$'s root has height $h_2$, equal to the height of $T_1.\text{root}$'s children. Append $k$ and $T_2.\text{root}$ as the new **rightmost** separator/child of $T_1.\text{root}$. Order holds ($k$ exceeds everything on $T_1$'s right spine and is below all of $T_2$). If $T_1.\text{root}$ now has $2t$ keys, split it (creating a new root) — $O(t)=O(1)$. $O(1)$.

### (c) Height-augmented B-tree

Augment every node $x$ with `x.height` = height of its subtree (leaves $=0$). Maintenance:
- **`recompute_height`**: a node's height is $0$ if a leaf else `children[0].height + 1` (all children have equal height by the B-tree balance invariant). $O(1)$.
- On **split** and on **insert-nonfull**, we recompute the height of every node we modify on the way back up. This adds $O(1)$ per node along an $O(h)$ path, so insertion/deletion keep their $O(t\,h)=O(\log n)$ costs. Implemented and checked by `check_invariants` (which independently recomputes heights and asserts the stored value matches, on every test tree).

### (d) General $h_1,h_2$ — $O(|h_1-h_2|+1)$

WLOG $h_1\ge h_2$ (symmetric via a left-graft). Using the height augmentation, **descend the right spine of $T_1$** while `x.height > h_2+1`; this takes exactly $h_1-h_2-1$ steps and lands on a node $x$ whose children have height $h_2$. Append $k$ and $T_2.\text{root}$ as $x$'s new rightmost separator/child (as in (b)). Now walk **back up** the recorded spine path fixing imbalances:

- If a node **overflows** ($>2t-1$ keys, from the appended key or a propagated split), split it around its median and push the median into its parent — exactly the insert primitive.
- If a node **underflows** ($<t-1$ keys, which can happen because the grafted former root may have as few as $1$ key), restore it by borrowing keys from a sibling (repeatedly, since one borrow may be insufficient for a $1$-key node) or, if no sibling can spare, merging through the separator — exactly the delete primitive. A merge removes a key from the parent, so the fixup **cascades** upward; each level is $O(t)$.

Finally repair the root (split if overflowing; drop a level if a merge emptied it). The spine descent is $O(|h_1-h_2|)$ and each of the $O(|h_1-h_2|)$ fixup levels is $O(t)=O(1)$, giving total time $O(|h_1-h_2|+1)$. Correctness — every intermediate tree satisfies the ordered-balanced-B-tree invariants — is certified by `check_invariants` after **5000** random combines with $t\in\{2,3,4,5\}$ and up to 600 keys, plus verification that the resulting in-order key list is exactly `sorted(left) + [k] + sorted(right)`.

*Empty-input special case:* if $T_1$ or $T_2$ is empty, `COMBINE` just inserts $k$ into the non-empty tree (a genuine former-root with $0$ keys cannot be lifted to $t-1$ keys by a single borrow, so it is handled directly). Included and tested.

---

### Verification summary

```
$ python -m pytest code/ps2/test_ps2.py -q
7 passed
```
- FFT `multiply` == schoolbook convolution (200 random polynomials);
- binary and DNA wildcard matching == naïve matcher (300 random instances each) and the two pset examples;
- COMBINE: 5000 random instances, all B-tree invariants + exact key multiset verified.

# 6.046J / 18.410J — Problem Set 4 Solutions

**Topics:** amortized analysis, randomized quicksort (high-probability bounds).

> Code: [`code/ps4/`](../code/ps4/) — `minqueue.py` (P4-1), `quicksort_analysis.py` + `demo_quicksort.py` (P4-2). Verified by `test_ps4.py` (5/5). Evidence: [`results/ps4_tests.txt`](../results/ps4_tests.txt), [`results/ps4_quicksort_experiment.txt`](../results/ps4_quicksort_experiment.txt), figure [`results/ps4_quicksort_comparisons.png`](../results/ps4_quicksort_comparisons.png).

---

## Exercises (CLRS Ch. 17 amortized; Ch. 7 quicksort)

- **17.1-3** (aggregate): a sequence of $n$ operations where the $i$-th costs $i$ if $i$ is a power of $2$ and $1$ otherwise totals $\le n + \sum_{j=0}^{\lfloor\lg n\rfloor}2^j < 3n$, so amortized cost $O(1)$.
- **17.2-2 / 17.3-2** (accounting / potential for a binary counter): charge \$2 to each `INCREMENT` (\$1 to set a bit $0\to1$, \$1 stored on that bit to pay for its future reset); or take $\Phi=$ number of $1$-bits, so amortized $=\hat c=c+\Delta\Phi=(1+\#\text{resets})+(1-\#\text{resets})=2$. Amortized $O(1)$.
- **7.1-3 / 7.2-5 / 7.4-4**: `PARTITION` is $\Theta(n)$; balanced-split recurrences give $\Theta(n\lg n)$ average; the worst case $\Theta(n^2)$ arises on already-sorted input with a fixed pivot, which randomization avoids w.h.p. (Problem 4-2).

---

## Problem 4-1 — Extreme FIFO Queue (FIND-MIN in $O(1)$ amortized)

Maintain a FIFO queue of **distinct** integers with `ENQUEUE`, `DEQUEUE`, `FIND-MIN`, each $O(1)$ amortized (any $m$ ops in $O(m)$).

### (a) Data structure & invariants

Keep two deques:
- `Q` — the **true FIFO** holding all current elements in arrival order;
- `M` — a **monotonic auxiliary deque** holding a non-decreasing subsequence of `Q`: precisely those elements that are still viable future minima.

**Invariants.**
- **I1** `M` is a subsequence of `Q` in arrival order.
- **I2** `M` is non-decreasing from front to back.
- **I3** `M.front == min(Q)` (so `FIND-MIN` reads `M.front`).

### (b) Procedures

```
ENQUEUE(x):
    Q.push_back(x)
    while M nonempty and M.back > x: M.pop_back()   # x dominates larger, newer-irrelevant elts
    M.push_back(x)

DEQUEUE():
    x = Q.pop_front()
    if M nonempty and M.front == x: M.pop_front()    # the departing element was the min
    return x

FIND-MIN():  return M.front
```

### (c) Correctness

We show the invariants are preserved and imply correct answers.

- **I2 (monotonicity).** `ENQUEUE` pops every `M.back > x` before pushing `x`, so after the push `M` is still non-decreasing. `DEQUEUE` only pops the front, preserving order.
- **I1 (subsequence).** Every element pushed to `M` was just pushed to `Q`; `M` elements are never reordered, only removed. The elements removed from the back of `M` during an `ENQUEUE` are larger than the newer element `x`; because the queue is FIFO, any such element leaves `Q` *before* `x` would ever be needed as the min after them — more precisely, they are still in `Q`, but they can never be the minimum again while the strictly smaller, still-present `x` sits behind them (any future queue state that contains one of them also contains `x`). Hence dropping them from `M` cannot lose a future minimum.
- **I3.** Given I1–I2, `M.front` is the smallest element of `M`. Every element of `Q` not in `M` was popped from `M`'s back by some later, smaller-or-equal element that is still in `Q` (and appears later, so is still present whenever the popped one is) — so no element outside `M` can be the current minimum. Therefore `min(Q)=min(M)=M.front`. When the front of `Q` (the oldest element) is the current min, it is exactly `M.front` (oldest surviving `M` element), and `DEQUEUE` removes it from both — restoring I3.

Distinctness of enqueued items guarantees the `M.front == x` test in `DEQUEUE` unambiguously identifies the departing minimum. Verified: 500 random op-sequences against a brute-force `min(deque)` reference, plus a full drain check.

### (d) Time complexity

- **Worst case per op.** `DEQUEUE`, `FIND-MIN`: $O(1)$. `ENQUEUE`: $O(1)$ *plus* the `while` pops, which are $O(k)$ if it pops $k$ elements — worst case $O(m)$ for a single op.
- **Amortized (potential method).** Let $\Phi=|M|\ge 0$. Each element is pushed onto `M` **exactly once** (during its `ENQUEUE`) and popped from `M` **at most once** (either by a later smaller element's `ENQUEUE`, or by its own `DEQUEUE`). So across any sequence of $m$ operations the total number of `M`-pushes and `M`-pops is $\le 2m$. With $\Phi=|M|$: `ENQUEUE`'s amortized cost is $1+(\text{pops})+\Delta\Phi = 1+(\text{pops})+(1-\text{pops})=2=O(1)$; `DEQUEUE` is $O(1)+\Delta\Phi\le O(1)$; `FIND-MIN` is $O(1)$ with $\Delta\Phi=0$. Hence **every operation is $O(1)$ amortized**, and any $m$ operations run in $O(m)$. Verified by a 200 000-operation throughput test.

---

## Problem 4-2 — Quicksort comparison count, high-probability

Randomized `QUICKSORT` on distinct $x_1,\dots,x_n$. We bound the number of element-vs-pivot comparisons with high probability.

### (a) One level shrinks the subarray to $\le \tfrac34 m$ with prob $\ge \tfrac12$

Consider a call on a subarray of size $m\ge2$ containing $x_i$. Call the pivot **central** if its rank within the subarray lies in the middle half, i.e. in $(\tfrac14 m,\tfrac34 m]$. A uniformly random pivot is central with probability $\ge \tfrac12$. If the chosen pivot is central, then both sides of the partition have size $<\tfrac34 m$, so the next recursive call containing $x_i$ (whichever side it lands on) has size $\le \tfrac34 m$. If the pivot happens to be $x_i$ itself, $x_i$ is done. Thus with probability $\ge\tfrac12$, either $x_i$ is chosen as pivot **or** the next call containing $x_i$ has size $\le\tfrac34 m$. ∎

### (b) $x_i$ is compared with pivots at most $d\lg n$ times, w.p. $\ge 1-1/n^2$

Each recursive call containing $x_i$ contributes **one** comparison of $x_i$ with that call's pivot (unless $x_i$ *is* the pivot, which ends the chain). By (a), each such call is a "coin toss" that is a **success** (size drops by factor $\le\tfrac34$) with probability $\ge\tfrac12$, independent across calls. Starting from size $n$, after $c\lg n$ successes the subarray size is $\le n\cdot(3/4)^{c\lg n} = n^{\,1+c\lg(3/4)}$; choosing $c=\tfrac{1}{\lg(4/3)}$ makes the exponent $0$, so $c\lg n$ successes drive the size below $1$ and terminate $x_i$'s chain. Here $c=1/\lg(4/3)\approx 2.41$.

Apply the pset's Claim with $\alpha=2$: **with probability $\ge 1-1/n^2$, any $3(\alpha+c)\lg n=3(2+c)\lg n$ tosses of a fair coin yield $\ge c\lg n$ heads.** So after $3(2+c)\lg n$ recursive calls, $x_i$ has (w.h.p.) accumulated the $c\lg n$ successes needed to finish. Therefore $x_i$ is compared with pivots at most
$$d\lg n,\qquad d = 3(2+c) = 3\!\left(2+\tfrac{1}{\lg(4/3)}\right)\approx 13.2,$$
with probability $\ge 1-1/n^2$. ∎

### (c) Total comparisons $\le d'n\lg n$ w.p. $\ge 1-1/n$

By (b), $\Pr[x_i\text{ exceeds }d\lg n\text{ comparisons}]\le 1/n^2$. **Union bound** over all $n$ elements:
$$\Pr\Big[\exists i:\ \#\text{comparisons of }x_i>d\lg n\Big]\le n\cdot\frac{1}{n^2}=\frac1n.$$
So with probability $\ge 1-\tfrac1n$, **every** $x_i$ makes $\le d\lg n$ comparisons, hence the total is
$$\sum_i (\#\text{comparisons of }x_i)\le n\cdot d\lg n = d'\,n\lg n,\qquad d'=d=3\!\left(2+\tfrac1{\lg(4/3)}\right)\approx 13.2.$$
(Each comparison involves two elements, so this double-counts by a factor $\le2$; the total distinct comparisons is $\le \tfrac12 d' n\lg n$ — still $\Theta(n\lg n)$.) ∎

### (d) Generalization to probability $1-1/n^\alpha$

Repeat (b) with the Claim at parameter $\alpha+1$ instead of $2$: with probability $\ge 1-1/n^{\alpha+1}$, $x_i$ needs $\le d_\alpha\lg n$ comparisons where $d_\alpha=3(\alpha+1+c)$. Union bound over $n$ elements:
$$\Pr[\exists i\text{ bad}]\le n\cdot n^{-(\alpha+1)}=n^{-\alpha},$$
so with probability $\ge 1-1/n^\alpha$ the total is $\le d'_\alpha\,n\lg n$ with $d'_\alpha=3(\alpha+1+c)=\Theta(\alpha)$. Thus for any fixed $\alpha$, quicksort makes $O(n\lg n)$ comparisons with probability $\ge 1-n^{-\alpha}$. ∎

### Empirical corroboration

`demo_quicksort.py` runs 200 random inputs at each $n\in\{100,300,1000,3000,10000\}$ and counts comparisons exactly:

| n | mean comps | mean / $n\lg n$ | max comps | max / $n\lg n$ |
|---|---|---|---|---|
| 100 | 652.9 | 0.98 | 881 | 1.33 |
| 1000 | 10 994.8 | 1.10 | 13 585 | 1.36 |
| 10000 | 155 968.4 | 1.17 | 179 085 | 1.35 |

The mean tracks the expected $2\ln 2\cdot n\log_2 n\approx1.386\,n\lg n$ (from below at small $n$, converging upward), and — the point of the high-probability analysis — the **maximum over 200 trials never exceeds $\approx1.4\,n\lg n$**: no run blows up toward $n^2$. See figure `ps4_quicksort_comparisons.png`.

---

### Verification summary

```
$ python -m pytest code/ps4/test_ps4.py -q
5 passed
```
- MinQueue == brute-force FIFO+min on 500 random op-sequences; 200k-op throughput; 3000-element drain check.
- Quicksort sorts correctly on 200 random inputs; comparison counts concentrate at $\Theta(n\lg n)$ with bounded maxima.

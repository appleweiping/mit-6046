"""PS5 Problem 5-2: Choosing Prizes -- four DP variants.

Given n prizes with nonnegative integer values, pick at most m of them to
maximize total value, under different structural constraints.  Each function
returns (best_value, chosen_indices/prizes).

(a) plain: pick the m largest values (as a subsequence in original order).
(b) two types A,B: all chosen A's must precede all chosen B's in S.
(c) non-decreasing: chosen values must form a non-decreasing subsequence.
(d) tree: chosen prizes form a connected subtree containing the root.

A brute-force oracle is provided for each and used in the tests.
"""
from __future__ import annotations

import itertools
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# (a) at most m, maximise sum, order preserved
# ---------------------------------------------------------------------------
def prizes_plain(values: List[int], m: int) -> Tuple[int, List[int]]:
    """Pick <= m prizes maximising the sum; return (value, chosen indices in
    original order).  Since values are nonnegative, take the m largest.
    O(n log n)."""
    order = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
    chosen = sorted(order[:m])
    return sum(values[i] for i in chosen), chosen


# ---------------------------------------------------------------------------
# (b) two types, all A before all B in the output subsequence
# ---------------------------------------------------------------------------
def prizes_two_types(values: List[int], types: List[str], m: int) -> Tuple[int, List[int]]:
    """All type-A picks precede all type-B picks in S (S follows original order).

    Split at some index p (0..n): choose some A-prizes from among indices < p
    that are type A, and some B-prizes from indices >= p that are type B... but
    the "A before B in S" with S in original order means: there is a cut position
    c such that every chosen A has original index < index of every chosen B.
    Equivalent: pick a boundary rank; A's chosen come from a prefix, B's from the
    suffix.  DP over (prefix boundary, count) is O(n*m); we implement the clean
    O(n*m) version: for each split point t in 0..n, best = (top A-values among
    first t that are A) + (top B-values among last n-t that are B), with total
    count <= m.  We precompute prefix/suffix best-k sums.
    """
    n = len(values)
    # bestA[t][j] = max sum of j type-A prizes among indices [0, t)
    # We only need, for each t, the sorted A-values in prefix; combine with suffix B.
    # Compute prefixA sorted desc incrementally, suffixB sorted desc incrementally.
    best = -1
    best_choice: List[int] = []

    # Precompute, for each boundary t, top A-values in [0,t) and top B-values in [t,n)
    # prefix_A_vals[t] = list of A values (with idx) in [0,t)
    prefixA: List[List[Tuple[int, int]]] = [[] for _ in range(n + 1)]
    for t in range(1, n + 1):
        prefixA[t] = prefixA[t - 1][:]
        if types[t - 1] == "A":
            prefixA[t].append((values[t - 1], t - 1))
    suffixB: List[List[Tuple[int, int]]] = [[] for _ in range(n + 2)]
    for t in range(n, -1, -1):
        suffixB[t] = suffixB[t + 1][:] if t + 1 <= n + 1 else []
        if t < n and types[t] == "B":
            suffixB[t].append((values[t], t))

    for t in range(n + 1):
        A = sorted(prefixA[t], reverse=True)
        B = sorted(suffixB[t], reverse=True)
        # choose a of A and b of B, a+b<=m, maximise sum -> greedily merge top values
        merged = sorted(A + B, reverse=True)[:m]
        s = sum(v for v, _ in merged)
        if s > best:
            best = s
            best_choice = sorted(i for _, i in merged)
    return best, best_choice


# ---------------------------------------------------------------------------
# (c) chosen values form a non-decreasing subsequence, length <= m
# ---------------------------------------------------------------------------
def prizes_nondecreasing(values: List[int], m: int) -> Tuple[int, List[int]]:
    """Max-sum non-decreasing subsequence of length <= m.  DP:
    dp[i][j] = max sum of a non-decreasing subseq ending exactly at i with j items.
    O(n^2 m)."""
    n = len(values)
    if n == 0 or m == 0:
        return 0, []
    NEG = float("-inf")
    dp = [[NEG] * (m + 1) for _ in range(n)]
    parent = [[None] * (m + 1) for _ in range(n)]
    for i in range(n):
        dp[i][1] = values[i]
        for k in range(i):
            if values[k] <= values[i]:
                for j in range(2, m + 1):
                    if dp[k][j - 1] != NEG and dp[k][j - 1] + values[i] > dp[i][j]:
                        dp[i][j] = dp[k][j - 1] + values[i]
                        parent[i][j] = (k, j - 1)
    best = 0
    end = None
    for i in range(n):
        for j in range(1, m + 1):
            if dp[i][j] > best:
                best = dp[i][j]
                end = (i, j)
    chosen: List[int] = []
    cur = end
    while cur is not None:
        i, j = cur
        chosen.append(i)
        cur = parent[i][j]
    chosen.reverse()
    return best, chosen


# ---------------------------------------------------------------------------
# (d) connected subtree containing the root, at most m nodes
# ---------------------------------------------------------------------------
def prizes_tree(value: List[int], left: List[int], right: List[int], m: int,
                root: int = 0) -> Tuple[int, List[int]]:
    """Binary tree (left[i], right[i] are child indices or -1).  Choose <= m
    prizes forming a connected subtree rooted at `root` maximising value.
    Tree knapsack: dp[u][j] = best value of a connected subtree of u's subtree
    that INCLUDES u and uses exactly j nodes.  Combine children by knapsack.
    O(n * m^2)."""
    NEG = float("-inf")

    def children(u):
        cs = []
        if left[u] != -1:
            cs.append(left[u])
        if right[u] != -1:
            cs.append(right[u])
        return cs

    # dp[u] : list where dp[u][j] = best value using exactly j nodes of subtree(u),
    # connected and including u; dp[u][0] = 0 (take nothing -> value 0, allowed).
    dp: dict = {}

    def solve(u):
        cs = children(u)
        # start: using u alone
        cur = [NEG] * (m + 1)
        cur[0] = 0            # take nothing in this subtree
        cur[1] = value[u]     # take just u
        for c in cs:
            solve(c)
            child = dp[c]
            merged = [NEG] * (m + 1)
            for j in range(m + 1):
                if cur[j] == NEG:
                    continue
                for jc in range(0, m + 1 - j):
                    # child contributes jc nodes; if jc>0 it must include c, and u
                    # must already be taken (j>=1) to stay connected.
                    if jc > 0 and j == 0:
                        continue
                    cv = child[jc] if jc > 0 else 0
                    if cv == NEG:
                        continue
                    if cur[j] + cv > merged[j + jc]:
                        merged[j + jc] = cur[j] + cv
            cur = merged
        dp[u] = cur

    solve(root)
    best = max(v for v in dp[root] if v != NEG)
    # reconstruction: re-run picking the argmax (simple: recompute chosen set)
    chosen = _reconstruct_tree(value, left, right, m, root, dp, best)
    return best, chosen


def _reconstruct_tree(value, left, right, m, root, dp, best):
    # Greedy reconstruction: find j achieving best at root, then split among children.
    def children(u):
        cs = []
        if left[u] != -1:
            cs.append(left[u])
        if right[u] != -1:
            cs.append(right[u])
        return cs

    NEG = float("-inf")
    chosen: List[int] = []

    def rebuild(u, budget, target):
        # target = dp value we must achieve using exactly `budget` nodes incl. u (if budget>0)
        if budget == 0:
            return
        chosen.append(u)
        remaining = budget - 1
        val_needed = target - value[u]
        cs = children(u)
        # distribute remaining among children to hit val_needed
        # brute over compositions (m small)
        _distribute(cs, 0, remaining, val_needed, {}, dp, rebuild)

    def _distribute(cs, idx, rem, need, alloc, dp, rebuild):
        if idx == len(cs):
            if rem == 0 and need == 0:
                for c, jc in alloc.items():
                    if jc > 0:
                        rebuild(c, jc, dp[c][jc])
                return True
            return False
        c = cs[idx]
        for jc in range(rem + 1):
            cv = dp[c][jc] if jc > 0 else 0
            if cv == NEG:
                continue
            alloc[c] = jc
            if _distribute(cs, idx + 1, rem - jc, need - cv, alloc, dp, rebuild):
                return True
        alloc.pop(c, None)
        return False

    # find budget j giving best
    for j in range(m + 1):
        if dp[root][j] == best:
            rebuild(root, j, best)
            break
    return sorted(chosen)


# ===========================================================================
# brute-force oracles
# ===========================================================================
def brute_plain(values, m):
    n = len(values)
    best, bc = 0, []
    for r in range(min(m, n) + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(values[i] for i in combo)
            if s > best:
                best, bc = s, list(combo)
    return best, bc


def brute_two_types(values, types, m):
    n = len(values)
    best, bc = 0, []
    for r in range(min(m, n) + 1):
        for combo in itertools.combinations(range(n), r):
            # in original order, all A's before all B's
            seq_types = [types[i] for i in combo]
            # valid iff no 'A' appears after a 'B'
            seen_b = False
            ok = True
            for tt in seq_types:
                if tt == "B":
                    seen_b = True
                elif seen_b:
                    ok = False
                    break
            if ok:
                s = sum(values[i] for i in combo)
                if s > best:
                    best, bc = s, list(combo)
    return best, bc


def brute_nondecreasing(values, m):
    n = len(values)
    best, bc = 0, []
    for r in range(min(m, n) + 1):
        for combo in itertools.combinations(range(n), r):
            vals = [values[i] for i in combo]
            if all(vals[k] <= vals[k + 1] for k in range(len(vals) - 1)):
                s = sum(vals)
                if s > best:
                    best, bc = s, list(combo)
    return best, bc


def brute_tree(value, left, right, m, root=0):
    n = len(value)
    # enumerate all connected subtrees containing root of size <= m
    best = value[root]
    best_set = {root}

    def children(u):
        return [c for c in (left[u], right[u]) if c != -1]

    # frontier expansion
    from itertools import combinations
    # collect all nodes; a connected subtree rooted at root is any subset S with
    # root in S and each non-root node's parent in S.
    parent = [-1] * n
    for u in range(n):
        for c in children(u):
            parent[c] = u
    for size in range(1, min(m, n) + 1):
        for combo in combinations(range(n), size):
            s = set(combo)
            if root not in s:
                continue
            if all(u == root or parent[u] in s for u in s):
                val = sum(value[u] for u in s)
                if val > best:
                    best, best_set = val, s
    return best, sorted(best_set)

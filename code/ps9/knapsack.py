"""PS9 Problem 9-1: Knapsack approximation algorithms.

Items a_i with integer size s_i and value v_i, capacity B (s_i <= B).  Maximize
total value of a subset with total size <= B.

  alg1_density_greedy   : (a) greedy by density -- NO constant ratio.
  alg2_two_approx       : (b) greedy-or-single -- provably a 2-approximation.
  alg3_dp_exact         : (c) exact DP over achievable values, O(n^2 V).
  alg4_fptas            : (d) FPTAS via value scaling + Alg3, (1-eps)-approx in
                          time poly(n, 1/eps).

An independent brute-force exact solver certifies Alg3 and bounds the others.
"""
from __future__ import annotations

import itertools
import math
from typing import List, Tuple

Item = Tuple[int, int]  # (size, value)


def _total(items, subset):
    s = sum(items[i][0] for i in subset)
    v = sum(items[i][1] for i in subset)
    return s, v


# ---------------------------------------------------------------------------
# (a) density greedy
# ---------------------------------------------------------------------------
def alg1_density_greedy(items: List[Item], B: int) -> Tuple[int, List[int]]:
    order = sorted(range(len(items)), key=lambda i: items[i][1] / items[i][0], reverse=True)
    size = 0
    chosen = []
    for i in order:
        if size + items[i][0] <= B:
            size += items[i][0]
            chosen.append(i)
    return sum(items[i][1] for i in chosen), sorted(chosen)


def alg1_counterexample():
    """No constant ratio: item0 tiny/high-density but low value, item1 fills B
    with huge value.  Greedy grabs item0 first, then item1 doesn't fit."""
    # densities: item0 = 2/1 = 2 ; item1 = k/k = 1  -> greedy takes item0 only.
    k = 1000
    items = [(1, 2), (k, k)]     # sizes, values
    B = k
    val, _ = alg1_density_greedy(items, B)   # takes item0 (value 2)
    opt = k                                   # take item1
    # ratio opt/greedy = k/2 -> unbounded as k grows
    return {"items": items, "B": B, "greedy_value": val, "opt_value": opt,
            "ratio": opt / val}


# ---------------------------------------------------------------------------
# (b) 2-approximation
# ---------------------------------------------------------------------------
def alg2_two_approx(items: List[Item], B: int) -> Tuple[int, List[int]]:
    n = len(items)
    if sum(s for s, _ in items) <= B:
        return sum(v for _, v in items), list(range(n))
    order = sorted(range(n), key=lambda i: items[i][1] / items[i][0], reverse=True)
    size = 0
    prefix = []
    i_break = None
    for pos, i in enumerate(order):
        if size + items[i][0] <= B:
            size += items[i][0]
            prefix.append(i)
        else:
            i_break = i
            break
    prefix_val = sum(items[i][1] for i in prefix)
    break_val = items[i_break][1] if i_break is not None else 0
    if break_val > prefix_val:
        return break_val, [i_break]
    return prefix_val, sorted(prefix)


# ---------------------------------------------------------------------------
# (c) exact DP over values, O(n^2 V) using S_{i,v} = min size for value exactly v
# ---------------------------------------------------------------------------
def alg3_dp_exact(items: List[Item], B: int) -> Tuple[int, List[int]]:
    n = len(items)
    V = max((v for _, v in items), default=0)
    Vmax = n * V
    INF = float("inf")
    # S[v] = min total size achieving total value exactly v using items seen so far
    S = [INF] * (Vmax + 1)
    S[0] = 0
    choice = [[False] * (Vmax + 1) for _ in range(n)]  # choice[i][v]: item i used to reach v
    parent = [[-1] * (Vmax + 1) for _ in range(n + 1)]
    # DP with reconstruction: process items, track predecessor value
    prev = S[:]
    take = [[None] * (Vmax + 1) for _ in range(n)]
    for i in range(n):
        s_i, v_i = items[i]
        cur = prev[:]
        for v in range(Vmax, v_i - 1, -1):
            if prev[v - v_i] + s_i < cur[v]:
                cur[v] = prev[v - v_i] + s_i
                take[i][v] = True
        prev = cur
    best_v = 0
    for v in range(Vmax + 1):
        if prev[v] <= B:
            best_v = v
    # reconstruct
    chosen = []
    v = best_v
    for i in range(n - 1, -1, -1):
        if v >= items[i][1] and take[i][v]:
            # ambiguous reconstruction; recompute forward-safe below
            pass
    chosen = _reconstruct_knapsack(items, B, best_v)
    return best_v, chosen


def _reconstruct_knapsack(items, B, target_value):
    """Recompute a min-size subset achieving exactly target_value (<=B)."""
    n = len(items)
    INF = float("inf")
    Vmax = target_value
    # dp[i][v] = min size using first i items to reach value exactly v
    dp = [[INF] * (Vmax + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for i in range(1, n + 1):
        s_i, v_i = items[i - 1]
        for v in range(Vmax + 1):
            dp[i][v] = dp[i - 1][v]
            if v >= v_i and dp[i - 1][v - v_i] + s_i < dp[i][v]:
                dp[i][v] = dp[i - 1][v - v_i] + s_i
    chosen = []
    v = target_value
    for i in range(n, 0, -1):
        s_i, v_i = items[i - 1]
        if v >= v_i and dp[i - 1][v - v_i] + s_i == dp[i][v] and dp[i][v] != INF:
            chosen.append(i - 1)
            v -= v_i
    return sorted(chosen)


# ---------------------------------------------------------------------------
# (d) FPTAS
# ---------------------------------------------------------------------------
def alg4_fptas(items: List[Item], B: int, eps: float) -> Tuple[int, List[int]]:
    n = len(items)
    V = max((v for _, v in items), default=0)
    if V == 0:
        return 0, []
    scale = (eps * V) / n
    if scale <= 0:
        return alg3_dp_exact(items, B)
    scaled = [(s, int(v / scale)) for (s, v) in items]  # floor(v_i / scale)
    _, chosen = alg3_dp_exact(scaled, B)
    # report the TRUE value of the chosen set
    true_val = sum(items[i][1] for i in chosen)
    return true_val, chosen


# ---------------------------------------------------------------------------
# brute-force exact oracle
# ---------------------------------------------------------------------------
def brute_exact(items: List[Item], B: int) -> Tuple[int, List[int]]:
    n = len(items)
    best_v = 0
    best = []
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(items[i][0] for i in combo)
            if s <= B:
                v = sum(items[i][1] for i in combo)
                if v > best_v:
                    best_v, best = v, list(combo)
    return best_v, best

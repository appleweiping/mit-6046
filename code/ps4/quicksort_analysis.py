"""PS4 Problem 4-2: Quicksort comparison-count analysis (empirical verification).

The pset proves, via high-probability tail bounds, that randomized QUICKSORT
makes at most d' n lg n comparisons with probability >= 1 - 1/n (and, with the
generalization in (d), >= 1 - 1/n^alpha).  Here we *implement* randomized
quicksort, count comparisons exactly, and empirically confirm that the count
concentrates at Theta(n lg n) and essentially never exceeds a small constant
times n lg n -- corroborating the analytical bound.
"""
from __future__ import annotations

import math
import random
import statistics
from typing import List, Tuple


def quicksort_count(a: List[int], rng: random.Random) -> Tuple[List[int], int]:
    """Randomized quicksort; returns (sorted list, #element-vs-pivot comparisons)."""
    comps = 0

    def qs(arr: List[int]) -> List[int]:
        nonlocal comps
        if len(arr) <= 1:
            return arr
        pivot = arr[rng.randrange(len(arr))]
        less, equal, greater = [], [], []
        for x in arr:
            # each element (except the pivot instance) is compared to the pivot
            comps += 1
            if x < pivot:
                less.append(x)
            elif x > pivot:
                greater.append(x)
            else:
                equal.append(x)
        comps -= len(equal)  # don't count the pivot compared with itself/dupes
        return qs(less) + equal + qs(greater)

    return qs(list(a)), comps


def experiment(sizes, trials_per_size, seed=0):
    """For each n, run many random inputs and report comparison-count stats
    against the n lg n reference."""
    rng = random.Random(seed)
    rows = []
    for n in sizes:
        counts = []
        for _ in range(trials_per_size):
            a = list(range(n))
            rng.shuffle(a)
            sorted_a, c = quicksort_count(a, rng)
            assert sorted_a == list(range(n))
            counts.append(c)
        nlogn = n * math.log2(n) if n > 1 else 1
        mean = statistics.mean(counts)
        mx = max(counts)
        rows.append({
            "n": n,
            "trials": trials_per_size,
            "mean_comps": mean,
            "max_comps": mx,
            "n_lg_n": nlogn,
            "mean_ratio": mean / nlogn,
            "max_ratio": mx / nlogn,
        })
    return rows

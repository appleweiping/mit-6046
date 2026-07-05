"""PS9 verification:
  - Alg3 exact DP == brute-force knapsack; Alg2 is a >=1/2 approximation; Alg4
    FPTAS achieves >= (1-eps) * OPT; Alg1 counterexample confirmed;
  - tournament FPT search == minimum cycle cover; kernelization preserves the
    minimum; reversing a min cover yields an acyclic tournament (fact a).
"""
import random

import pytest

from knapsack import (alg1_counterexample, alg1_density_greedy,
                     alg2_two_approx, alg3_dp_exact, alg4_fptas, brute_exact)
from tournament_fpt import (Tournament, fpt_bounded_search, is_acyclic,
                          kernelize, min_cycle_cover_bruteforce)


def random_items(n, rng, B, max_val=20):
    # pset assumption: every item fits, i.e. s_i <= B
    return [(rng.randint(1, B), rng.randint(1, max_val)) for _ in range(n)]


def test_alg3_exact_matches_bruteforce():
    rng = random.Random(0)
    for _ in range(300):
        n = rng.randint(0, 10)
        B = rng.randint(1, 30)
        items = random_items(n, rng, B)
        v, chosen = alg3_dp_exact(items, B)
        bv, _ = brute_exact(items, B)
        assert v == bv, (items, B, v, bv)
        # chosen is feasible and achieves v
        assert sum(items[i][0] for i in chosen) <= B
        assert sum(items[i][1] for i in chosen) == v


def test_alg1_counterexample():
    ce = alg1_counterexample()
    assert ce["greedy_value"] == 2
    assert ce["opt_value"] == 1000
    assert ce["ratio"] == 500  # unbounded family


def test_alg2_is_2_approx():
    rng = random.Random(1)
    for _ in range(500):
        n = rng.randint(1, 12)
        B = rng.randint(1, 30)
        items = random_items(n, rng, B)
        v, chosen = alg2_two_approx(items, B)
        opt, _ = brute_exact(items, B)
        # feasible
        assert sum(items[i][0] for i in chosen) <= B
        assert sum(items[i][1] for i in chosen) == v
        # 2-approximation: v >= opt/2
        assert 2 * v >= opt, (items, B, v, opt)


def test_alg4_fptas():
    rng = random.Random(2)
    for _ in range(200):
        n = rng.randint(1, 10)
        B = rng.randint(1, 30)
        items = random_items(n, rng, B, max_val=50)
        opt, _ = brute_exact(items, B)
        for eps in (0.5, 0.3, 0.1):
            v, chosen = alg4_fptas(items, B, eps)
            assert sum(items[i][0] for i in chosen) <= B
            # FPTAS guarantee: v >= (1 - eps) * opt
            assert v >= (1 - eps) * opt - 1e-9, (items, B, eps, v, opt)
            assert v <= opt


# ------------------------- tournament -------------------------
def random_tournament(n, rng):
    arcs = set()
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < 0.5:
                arcs.add((u, v))
            else:
                arcs.add((v, u))
    return Tournament(n, arcs)


def test_fpt_matches_min_cover():
    rng = random.Random(3)
    for _ in range(150):
        n = rng.randint(1, 6)
        T = random_tournament(n, rng)
        opt = min_cycle_cover_bruteforce(T)
        # fpt with budget opt should succeed, budget opt-1 should fail
        assert fpt_bounded_search(T, opt) is not None
        if opt > 0:
            assert fpt_bounded_search(T, opt - 1) is None


def test_reversing_min_cover_makes_acyclic():
    rng = random.Random(4)
    for _ in range(150):
        n = rng.randint(1, 6)
        T = random_tournament(n, rng)
        opt = min_cycle_cover_bruteforce(T)
        cover = fpt_bounded_search(T, opt)
        assert cover is not None
        assert is_acyclic(T.reverse(cover))  # fact (a)


def test_kernelize_preserves_optimum():
    rng = random.Random(5)
    for _ in range(150):
        n = rng.randint(1, 6)
        T = random_tournament(n, rng)
        opt = min_cycle_cover_bruteforce(T)
        K = kernelize(T)
        opt_k = min_cycle_cover_bruteforce(K)
        assert opt_k == opt, (n, opt, opt_k)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

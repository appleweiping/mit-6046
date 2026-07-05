"""PS1 verification: tree MWIS vs brute force, and closest-pair / distance-1
detection vs brute force, on many random instances."""
import random

import pytest

from close_pairs import (brute_closest, brute_pair_within_1,
                         brute_triple_within_1, closest_pair,
                         exists_pair_within_1, exists_triple_within_1)
from restaurant_location import (greedy_counterexample, make_graph,
                                 mwis_general_bruteforce, mwis_tree,
                                 mwis_tree_maxcount)


def random_tree(n, rng):
    edges = [(rng.randrange(i), i) for i in range(1, n)]  # each node -> earlier node
    return make_graph(n, edges), edges


def test_tree_mwis_matches_bruteforce():
    rng = random.Random(1)
    for _ in range(300):
        n = rng.randint(1, 9)
        tree, edges = random_tree(n, rng)
        profit = [rng.randint(0, 20) for _ in range(n)]
        val, chosen = mwis_tree(profit, tree)
        bval, _ = mwis_general_bruteforce(profit, tree)
        assert val == bval, (profit, edges, val, bval)
        # returned set is independent and achieves the value
        assert all(not (tree[u] & chosen) for u in chosen)
        assert sum(profit[u] for u in chosen) == val


def test_tree_maxcount_matches_bruteforce():
    rng = random.Random(2)
    for _ in range(200):
        n = rng.randint(1, 9)
        tree, _ = random_tree(n, rng)
        val, chosen = mwis_tree_maxcount(tree)
        bval, _ = mwis_general_bruteforce([1] * n, tree)
        assert val == bval
        assert all(not (tree[u] & chosen) for u in chosen)


def test_greedy_is_suboptimal():
    ce = greedy_counterexample()
    assert ce["greedy_is_suboptimal"] is True
    assert ce["greedy_value"] == 3 and ce["optimal_value"] == 4


def test_closest_pair_matches_bruteforce():
    rng = random.Random(3)
    for _ in range(200):
        n = rng.randint(2, 40)
        xs = rng.sample(range(-1000, 1000), n)
        ys = rng.sample(range(-1000, 1000), n)
        pts = [(x / 137.0, y / 149.0) for x, y in zip(xs, ys)]  # distinct x, distinct y
        d, _ = closest_pair(pts)
        bd = brute_closest(pts)
        assert abs(d - bd) < 1e-9, (pts, d, bd)


def test_pair_within_1_matches_bruteforce():
    rng = random.Random(4)
    for _ in range(300):
        n = rng.randint(2, 30)
        xs = rng.sample(range(-200, 200), n)
        ys = rng.sample(range(-200, 200), n)
        pts = [(x / 50.0, y / 50.0) for x, y in zip(xs, ys)]
        got = exists_pair_within_1(pts)
        exp = brute_pair_within_1(pts)
        assert (got is None) == (exp is None)


def test_triple_within_1_matches_bruteforce():
    rng = random.Random(5)
    for _ in range(300):
        n = rng.randint(3, 30)
        xs = rng.sample(range(-200, 200), n)
        ys = rng.sample(range(-200, 200), n)
        pts = [(x / 45.0, y / 45.0) for x, y in zip(xs, ys)]
        got = exists_triple_within_1(pts)
        exp = brute_triple_within_1(pts)
        assert (got is None) == (exp is None)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

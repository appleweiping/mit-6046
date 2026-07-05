"""PS6 verification:
  - bounded-hop APSP (FW and matrix-power) == Bellman-Ford oracle;
  - dynamic edge update == full Floyd-Warshall recompute;
  - Boruvka and cycle-breaking == Kruskal MST; divide-and-conquer counterexample.
"""
import math
import random

import pytest

from apsp import (INF, bounded_hop_fw, bounded_hop_matmul, bounded_hop_update,
                 brute_bounded_hop, floyd_warshall, update_edge)
from mst_unique import (boruvka, cycle_breaking_mst, dc_counterexample,
                       divide_and_conquer_mst, kruskal)


def random_weight_matrix(n, rng, p=0.5):
    W = [[INF] * n for _ in range(n)]
    for i in range(n):
        W[i][i] = 0.0
    for i in range(n):
        for j in range(n):
            if i != j and rng.random() < p:
                W[i][j] = rng.randint(1, 20)
    return W


def close(A, B, eps=1e-9):
    n = len(A)
    for i in range(n):
        for j in range(n):
            a, b = A[i][j], B[i][j]
            if a == INF or b == INF:
                if a != b:
                    return False
            elif abs(a - b) > eps:
                return False
    return True


def test_floyd_warshall_matches_bounded_full():
    rng = random.Random(0)
    for _ in range(50):
        n = rng.randint(1, 7)
        W = random_weight_matrix(n, rng)
        D, _ = floyd_warshall(W)
        # with h = n-1 hops, bounded == full APSP (nonnegative weights)
        Dh = brute_bounded_hop(W, max(1, n - 1))
        assert close(D, Dh)


def test_bounded_hop_fw_and_matmul():
    rng = random.Random(1)
    for _ in range(80):
        n = rng.randint(1, 7)
        W = random_weight_matrix(n, rng)
        h = rng.randint(1, 6)
        ref = brute_bounded_hop(W, h)
        assert close(bounded_hop_fw(W, h), ref)
        assert close(bounded_hop_matmul(W, h), ref)


def test_dynamic_update_matches_recompute():
    rng = random.Random(2)
    for _ in range(200):
        n = rng.randint(2, 7)
        W = random_weight_matrix(n, rng)
        i, j = rng.sample(range(n), 2)
        r = rng.randint(1, 20)
        D_upd, _ = update_edge(W, i, j, r)
        W2 = [row[:] for row in W]
        W2[i][j] = r
        D_ref, _ = floyd_warshall(W2)
        assert close(D_upd, D_ref), (n, i, j, r)


def test_bounded_hop_dynamic_update():
    rng = random.Random(3)
    for _ in range(120):
        n = rng.randint(2, 6)
        W = random_weight_matrix(n, rng)
        h = rng.randint(1, 5)
        i, j = rng.sample(range(n), 2)
        r = rng.randint(1, 20)
        got = bounded_hop_update(W, h, i, j, r)
        W2 = [row[:] for row in W]
        W2[i][j] = r
        ref = brute_bounded_hop(W2, h)
        assert close(got, ref)


# ------------------------- MST -------------------------
def random_unique_graph(n, rng, p=0.5):
    edges = []
    w = 1
    weights = list(range(1, n * n + 5))
    rng.shuffle(weights)
    wi = 0
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                edges.append((i, j, float(weights[wi])))
                wi += 1
    # ensure connected: add a random spanning path
    perm = list(range(n))
    rng.shuffle(perm)
    have = {(min(u, v), max(u, v)) for u, v, _ in edges}
    for a in range(n - 1):
        u, v = perm[a], perm[a + 1]
        if (min(u, v), max(u, v)) not in have:
            edges.append((u, v, float(weights[wi])))
            wi += 1
            have.add((min(u, v), max(u, v)))
    return edges


def test_boruvka_equals_kruskal():
    rng = random.Random(10)
    for _ in range(200):
        n = rng.randint(1, 12)
        edges = random_unique_graph(n, rng)
        assert boruvka(n, edges) == kruskal(n, edges)


def test_cycle_breaking_equals_kruskal():
    rng = random.Random(11)
    for _ in range(200):
        n = rng.randint(1, 12)
        edges = random_unique_graph(n, rng)
        assert cycle_breaking_mst(n, edges) == kruskal(n, edges)


def test_divide_and_conquer_is_incorrect():
    n, edges = dc_counterexample()
    true_mst = kruskal(n, edges)
    dc = set(divide_and_conquer_mst(n, edges))
    # the D&C result differs from (is worse than / not equal to) the true MST
    true_w = sum(w for u, v, w in edges if (min(u, v), max(u, v)) in true_mst)
    ew = {(min(u, v), max(u, v)): w for u, v, w in edges}
    dc_w = sum(ew[e] for e in dc if e in ew)
    assert dc != true_mst
    assert dc_w > true_w  # strictly heavier => provably not the MST


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

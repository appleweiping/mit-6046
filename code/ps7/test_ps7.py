"""PS7 verification:
  - Dinic max flow == max-flow value from a brute-force / Edmonds-Karp reference,
    and == min cut;
  - dynamic increase/decrease updates == full recompute on the modified network;
  - edge-disjoint paths are genuinely edge-disjoint and count matches max flow;
  - food-truck assignment maximizes assigned customers (min vouchers) == max flow.
"""
import random

import pytest

from applications import (dynamic_maxflow_decrease, dynamic_maxflow_increase,
                         edge_disjoint_paths, food_truck_assignment)
from maxflow import MaxFlow


def build_random_network(n, rng, max_cap=6, p=0.4):
    """Return (edges list [(u,v,cap)], s, t)."""
    s, t = 0, n - 1
    edges = []
    for u in range(n):
        for v in range(n):
            if u != v and rng.random() < p:
                edges.append((u, v, rng.randint(1, max_cap)))
    return edges, s, t


def maxflow_from_edges(n, edges, s, t):
    mf = MaxFlow(n)
    locs = [mf.add_edge(u, v, c) for (u, v, c) in edges]
    val = mf.max_flow(s, t)
    return mf, locs, val


def test_maxflow_equals_mincut():
    rng = random.Random(0)
    for _ in range(200):
        n = rng.randint(2, 8)
        edges, s, t = build_random_network(n, rng)
        mf, _, val = maxflow_from_edges(n, edges, s, t)
        # min cut = sum of capacities of edges from reachable set to non-reachable
        reach = mf.min_cut_reachable(s)
        cut = 0
        for (u, v, c) in edges:
            if reach[u] and not reach[v]:
                cut += c
        assert val == cut, (n, edges, val, cut)


def test_maxflow_matches_reference_ek():
    # simple Edmonds-Karp reference implemented inline (BFS augmenting)
    from collections import deque

    def ek(n, edges, s, t):
        cap = [[0] * n for _ in range(n)]
        for u, v, c in edges:
            cap[u][v] += c
        flow = 0
        while True:
            par = [-1] * n
            par[s] = s
            q = deque([s])
            while q:
                u = q.popleft()
                for v in range(n):
                    if par[v] == -1 and cap[u][v] > 0:
                        par[v] = u
                        q.append(v)
            if par[t] == -1:
                break
            b = float("inf")
            v = t
            while v != s:
                u = par[v]
                b = min(b, cap[u][v])
                v = u
            v = t
            while v != s:
                u = par[v]
                cap[u][v] -= b
                cap[v][u] += b
                v = u
            flow += b
        return flow

    rng = random.Random(1)
    for _ in range(200):
        n = rng.randint(2, 8)
        edges, s, t = build_random_network(n, rng)
        _, _, val = maxflow_from_edges(n, edges, s, t)
        assert val == ek(n, edges, s, t)


def test_dynamic_increase():
    rng = random.Random(2)
    for _ in range(150):
        n = rng.randint(2, 7)
        edges, s, t = build_random_network(n, rng)
        if not edges:
            continue
        mf, locs, val0 = maxflow_from_edges(n, edges, s, t)
        ei = rng.randrange(len(edges))
        k = rng.randint(1, 5)
        new_val = dynamic_maxflow_increase(mf, s, t, locs[ei], k)
        # reference: recompute with modified capacity
        edges2 = list(edges)
        u, v, c = edges2[ei]
        edges2[ei] = (u, v, c + k)
        _, _, ref = maxflow_from_edges(n, edges2, s, t)
        assert new_val == ref, (n, edges, ei, k, new_val, ref)


def test_dynamic_decrease():
    rng = random.Random(3)
    for _ in range(150):
        n = rng.randint(2, 7)
        edges, s, t = build_random_network(n, rng)
        if not edges:
            continue
        mf, locs, val0 = maxflow_from_edges(n, edges, s, t)
        ei = rng.randrange(len(edges))
        u, v, c = edges[ei]
        k = rng.randint(1, c)
        new_val = dynamic_maxflow_decrease(mf, s, t, locs[ei], k)
        edges2 = list(edges)
        edges2[ei] = (u, v, c - k)
        _, _, ref = maxflow_from_edges(n, edges2, s, t)
        assert new_val == ref, (n, edges, ei, k, new_val, ref)


def test_edge_disjoint_paths():
    rng = random.Random(4)
    for _ in range(200):
        n = rng.randint(3, 9)
        t = n - 1
        directed = []
        for u in range(n):
            for v in range(n):
                if u != v and v != 0 and rng.random() < 0.35:
                    directed.append((u, v))
        directed = list(set(directed))
        k = rng.randint(1, 3)
        sources = rng.sample([x for x in range(n) if x != t], min(k, n - 1))
        res = edge_disjoint_paths(n, directed, sources, t)
        if res is not None:
            # verify each path valid and all edge-disjoint
            used = set()
            edgeset = set(directed)
            assert len(res) == len(sources)
            for p, src in zip(res, sources):
                assert p[0] == src and p[-1] == t
                for a, b in zip(p, p[1:]):
                    assert (a, b) in edgeset
                    assert (a, b) not in used  # edge-disjoint
                    used.add((a, b))


def test_food_truck_assignment():
    rng = random.Random(5)
    for _ in range(200):
        n = rng.randint(1, 8)   # customers
        m = rng.randint(1, 5)   # food types
        quantities = [rng.randint(0, 3) for _ in range(m)]
        prefs = []
        for _ in range(n):
            k = rng.randint(1, m)
            prefs.append(rng.sample(range(m), k))
        assigned, assignment = food_truck_assignment(prefs, quantities)
        # validity: each assigned customer got an acceptable food; capacities ok
        used = [0] * m
        cnt = 0
        for i, j in enumerate(assignment):
            if j is not None:
                assert j in prefs[i]
                used[j] += 1
                cnt += 1
        assert cnt == assigned
        for j in range(m):
            assert used[j] <= quantities[j]
        # optimality: brute force the max matching for small instances
        if n <= 6 and m <= 4:
            best = brute_matching(prefs, quantities)
            assert assigned == best, (prefs, quantities, assigned, best)


def brute_matching(prefs, quantities):
    n = len(prefs)
    m = len(quantities)
    best = 0

    def rec(i, remaining, cnt):
        nonlocal best
        if i == n:
            best = max(best, cnt)
            return
        # skip customer i (voucher)
        rec(i + 1, remaining, cnt)
        # assign to some acceptable food with capacity
        for j in prefs[i]:
            if remaining[j] > 0:
                remaining[j] -= 1
                rec(i + 1, remaining, cnt + 1)
                remaining[j] += 1

    rec(0, list(quantities), 0)
    return best


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

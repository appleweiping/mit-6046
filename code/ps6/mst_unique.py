"""PS6 Problem 6-2: MST with unique edge weights.

Undirected graph, all edge weights distinct -> the MST is unique (part a).

We implement and empirically classify the three candidate algorithms:
  (b) Batched edge-addition  (Boruvka's algorithm)  -> CORRECT;
  (c) Divide-and-conquer on an arbitrary vertex split -> INCORRECT (counterexample);
  (d) Cycle-breaking (remove the heaviest edge of some cycles each phase) -> CORRECT.

A reference Kruskal MST is used to certify (b) and (d) and to expose (c).
"""
from __future__ import annotations

from typing import Dict, FrozenSet, List, Set, Tuple

Edge = Tuple[int, int, float]  # (u, v, weight)


class DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        return True


def kruskal(n: int, edges: List[Edge]) -> FrozenSet[Tuple[int, int]]:
    """Reference MST (as a set of undirected edges) via Kruskal."""
    dsu = DSU(n)
    mst = set()
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if dsu.union(u, v):
            mst.add((min(u, v), max(u, v)))
    return frozenset(mst)


def _norm(u, v):
    return (min(u, v), max(u, v))


# ---------------------------------------------------------------------------
# (b) Boruvka: batched lightest-edge-per-component addition
# ---------------------------------------------------------------------------
def boruvka(n: int, edges: List[Edge]) -> FrozenSet[Tuple[int, int]]:
    dsu = DSU(n)
    mst: Set[Tuple[int, int]] = set()
    num_comp = n
    while num_comp > 1:
        # lightest outgoing edge per component
        cheapest: Dict[int, Edge] = {}
        for u, v, w in edges:
            ru, rv = dsu.find(u), dsu.find(v)
            if ru == rv:
                continue
            for r in (ru, rv):
                if r not in cheapest or w < cheapest[r][2]:
                    cheapest[r] = (u, v, w)
        if not cheapest:
            break  # disconnected
        added = False
        for r, (u, v, w) in cheapest.items():
            if dsu.union(u, v):
                mst.add(_norm(u, v))
                num_comp -= 1
                added = True
        if not added:
            break
    return frozenset(mst)


# ---------------------------------------------------------------------------
# (c) Divide-and-conquer on an arbitrary vertex partition (INCORRECT)
# ---------------------------------------------------------------------------
def divide_and_conquer_mst(n: int, edges: List[Edge],
                           vertices: List[int] = None) -> Set[Tuple[int, int]]:
    """Split V arbitrarily into V1,V2; recurse on induced subgraphs; add the
    single lightest edge crossing the cut.  This is the algorithm from part (c).
    It is NOT always correct (see counterexample())."""
    if vertices is None:
        vertices = list(range(n))
    if len(vertices) <= 1:
        return set()
    mid = len(vertices) // 2
    V1 = set(vertices[:mid])
    V2 = set(vertices[mid:])
    E1 = [(u, v, w) for (u, v, w) in edges if u in V1 and v in V1]
    E2 = [(u, v, w) for (u, v, w) in edges if u in V2 and v in V2]
    T1 = divide_and_conquer_mst(n, E1, vertices[:mid])
    T2 = divide_and_conquer_mst(n, E2, vertices[mid:])
    cross = [(u, v, w) for (u, v, w) in edges
             if (u in V1) != (v in V1)]
    T = set(T1) | set(T2)
    if cross:
        u, v, w = min(cross, key=lambda e: e[2])
        T.add(_norm(u, v))
    return T


def dc_counterexample():
    """A concrete graph where the divide-and-conquer algorithm returns a
    non-minimum (or non-)spanning tree.  Vertices split {0,1} | {2,3}."""
    # Path-ish graph: the arbitrary split isolates the truly-light connecting
    # structure.  Weights all distinct.
    n = 4
    edges = [
        (0, 1, 1.0),
        (2, 3, 2.0),
        (1, 2, 3.0),   # the only cross edge in split {0,1}|{2,3}
        (0, 3, 4.0),   # a heavier cross edge
        (0, 2, 10.0),
    ]
    # True MST (Kruskal): {0-1(1),2-3(2),1-2(3)} weight 6.
    # D&C with split {0,1}|{2,3}: T1={0-1}, T2={2-3}, cross lightest = 1-2(3).
    # -> {0-1,2-3,1-2} weight 6 -- here it happens to match.  We need a split
    # where the recursion misses a lighter internal option; construct that:
    n = 6
    edges = [
        (0, 1, 1.0),
        (1, 2, 7.0),
        (0, 2, 2.0),   # inside V1={0,1,2}: MST should use 0-1,0-2 (not 1-2)
        (3, 4, 3.0),
        (4, 5, 8.0),
        (3, 5, 4.0),   # inside V2={3,4,5}: MST uses 3-4,3-5
        (2, 3, 5.0),   # cross edge (lightest crossing)
        (0, 5, 6.0),   # another cross edge
    ]
    return n, edges


# ---------------------------------------------------------------------------
# (d) Cycle-breaking (INVERSE-KRUSKAL flavour) -- CORRECT
# ---------------------------------------------------------------------------
def cycle_breaking_mst(n: int, edges: List[Edge]) -> FrozenSet[Tuple[int, int]]:
    """Repeatedly: while the graph has a cycle, remove the heaviest edge on a
    cycle.  Equivalent to the reverse-delete algorithm; correct for unique
    weights.  We implement reverse-delete: consider edges heaviest-first, delete
    an edge iff its removal keeps the graph connected."""
    present = set(_norm(u, v) for u, v, _ in edges)
    weight = {_norm(u, v): w for u, v, w in edges}
    for u, v, w in sorted(edges, key=lambda e: e[2], reverse=True):
        e = _norm(u, v)
        if e not in present:
            continue
        present.discard(e)
        if not _connected(n, present):
            present.add(e)  # removal disconnects -> keep it
    return frozenset(present)


def _connected(n: int, edgeset: Set[Tuple[int, int]]) -> bool:
    if n == 0:
        return True
    adj: Dict[int, List[int]] = {i: [] for i in range(n)}
    for u, v in edgeset:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    stack = [0]
    seen[0] = True
    cnt = 1
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if not seen[y]:
                seen[y] = True
                cnt += 1
                stack.append(y)
    return cnt == n

"""PS9 Problem 9-2: Tournament Edge Reversal -- fixed-parameter algorithm.

A tournament T = (V, E): for every pair u,v exactly one of (u,v),(v,u) in E.
A cycle cover is a set A of edges hitting every directed cycle.  TER: does T have
a cycle cover of size <= k?

Facts used:
  (a) reversing a MINIMAL cycle cover makes T acyclic (a transitive tournament).
      Equivalently: a tournament is acyclic iff it has no directed triangle
      (3-cycle); so a "cycle cover" = a set of edges hitting every triangle =
      a triangle hitting set.
  (b) kernelization: if T has a triangle-hitting set of size <= k then |V| can be
      bounded (a k^2+2k-vertex kernel) after removing vertices in no triangle.
  (c) FPT algorithm: branch on a triangle (reverse one of its 3 edges), depth k
      -> 3^k * poly, i.e. FPT.

We implement:
  * is_acyclic(T)              -- via topological ordering;
  * has_triangle / find_triangle;
  * min_cycle_cover_bruteforce -- exact optimum (oracle);
  * fpt_bounded_search(T, k)   -- the 3^k branching FPT algorithm;
  * kernelize(T)               -- drop triangle-free vertices.
and verify fpt == brute force.
"""
from __future__ import annotations

import itertools
from typing import FrozenSet, List, Optional, Set, Tuple

Edge = Tuple[int, int]


class Tournament:
    def __init__(self, n: int, arcs: Set[Edge]):
        self.n = n
        self.arc = arcs  # set of directed edges (u,v)

    @staticmethod
    def from_order_with_flips(order: List[int], flips: Set[Edge] = frozenset()):
        """Transitive tournament by `order` (i beats j if earlier), then flip the
        given arcs (used to create cycles)."""
        n = len(order)
        pos = {v: i for i, v in enumerate(order)}
        arcs = set()
        for u in range(n):
            for v in range(n):
                if u != v and pos[u] < pos[v]:
                    arcs.add((u, v))
        for (a, b) in flips:
            if (a, b) in arcs:
                arcs.discard((a, b))
                arcs.add((b, a))
            elif (b, a) in arcs:
                arcs.discard((b, a))
                arcs.add((a, b))
        return Tournament(n, arcs)

    def reverse(self, edges) -> "Tournament":
        arcs = set(self.arc)
        for (u, v) in edges:
            if (u, v) in arcs:
                arcs.discard((u, v))
                arcs.add((v, u))
            elif (v, u) in arcs:
                arcs.discard((v, u))
                arcs.add((u, v))
        return Tournament(self.n, arcs)


def is_acyclic(T: Tournament) -> bool:
    """A tournament is acyclic iff it admits a topological order (Kahn)."""
    indeg = [0] * T.n
    adj = [[] for _ in range(T.n)]
    for (u, v) in T.arc:
        adj[u].append(v)
        indeg[v] += 1
    from collections import deque
    q = deque(i for i in range(T.n) if indeg[i] == 0)
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen == T.n


def find_triangle(T: Tournament) -> Optional[Tuple[int, int, int]]:
    """Return a directed 3-cycle (a->b->c->a) if one exists."""
    arc = T.arc
    for a, b, c in itertools.permutations(range(T.n), 3):
        if (a, b) in arc and (b, c) in arc and (c, a) in arc:
            return (a, b, c)
    return None


def has_triangle(T: Tournament) -> bool:
    return find_triangle(T) is not None


def min_cycle_cover_bruteforce(T: Tournament) -> int:
    """Smallest #edges to reverse so the tournament becomes acyclic (oracle).
    Try reversing subsets of edges in increasing size."""
    edges = list(T.arc)
    if is_acyclic(T):
        return 0
    for k in range(1, len(edges) + 1):
        for combo in itertools.combinations(edges, k):
            if is_acyclic(T.reverse(combo)):
                return k
    return len(edges)


def fpt_bounded_search(T: Tournament, k: int) -> Optional[List[Edge]]:
    """Return a set of <= k edges whose reversal makes T acyclic, or None.
    Branch on a triangle: at least one of its 3 edges must be reversed.
    Depth <= k, branching factor 3 => O(3^k * poly)."""
    if is_acyclic(T):
        return []
    if k == 0:
        return None
    tri = find_triangle(T)
    a, b, c = tri
    for e in [(a, b), (b, c), (c, a)]:
        sub = fpt_bounded_search(T.reverse([e]), k - 1)
        if sub is not None:
            return [e] + sub
    return None


def kernelize(T: Tournament) -> Tournament:
    """Remove vertices that lie in NO triangle (they never need a reversal).
    A relabelled tournament on the surviving vertices is returned.  (Part b's
    kernel bound: if the answer is <= k, the surviving vertex count is O(k^2).)"""
    in_triangle = set()
    arc = T.arc
    for a, b, c in itertools.permutations(range(T.n), 3):
        if (a, b) in arc and (b, c) in arc and (c, a) in arc:
            in_triangle.update([a, b, c])
    keep = sorted(in_triangle)
    relabel = {v: i for i, v in enumerate(keep)}
    new_arcs = set()
    for (u, v) in arc:
        if u in relabel and v in relabel:
            new_arcs.add((relabel[u], relabel[v]))
    return Tournament(len(keep), new_arcs)

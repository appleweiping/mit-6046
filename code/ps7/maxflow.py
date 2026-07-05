"""PS7: a real max-flow solver (Dinic + Edmonds-Karp) with the applications
needed by Problems 7-1..7-3.

Graph is stored as an adjacency list of directed residual edges; each edge has a
`cap`, current `flow`, and a pointer to its reverse edge.  Integer capacities.
"""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple


class Edge:
    __slots__ = ("to", "cap", "flow", "rev")

    def __init__(self, to: int, cap: int, rev: int):
        self.to = to
        self.cap = cap
        self.flow = 0
        self.rev = rev  # index of the reverse edge in graph[to]

    def residual(self) -> int:
        return self.cap - self.flow


class MaxFlow:
    def __init__(self, n: int):
        self.n = n
        self.graph: List[List[Edge]] = [[] for _ in range(n)]

    def add_edge(self, u: int, v: int, cap: int) -> Tuple[int, int]:
        """Add directed edge u->v with capacity cap (and a 0-cap reverse).
        Returns (u, index) so the edge can be located later (for dynamic updates)."""
        self.graph[u].append(Edge(v, cap, len(self.graph[v])))
        self.graph[v].append(Edge(u, 0, len(self.graph[u]) - 1))
        return (u, len(self.graph[u]) - 1)

    # ---------------- Dinic ----------------
    def _bfs_level(self, s: int, t: int) -> Optional[List[int]]:
        level = [-1] * self.n
        level[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for e in self.graph[u]:
                if e.residual() > 0 and level[e.to] < 0:
                    level[e.to] = level[u] + 1
                    q.append(e.to)
        return level if level[t] >= 0 else None

    def _dfs_blocking(self, u: int, t: int, pushed: int, level, it) -> int:
        if u == t:
            return pushed
        while it[u] < len(self.graph[u]):
            e = self.graph[u][it[u]]
            if e.residual() > 0 and level[e.to] == level[u] + 1:
                d = self._dfs_blocking(e.to, t, min(pushed, e.residual()), level, it)
                if d > 0:
                    e.flow += d
                    self.graph[e.to][e.rev].flow -= d
                    return d
            it[u] += 1
        return 0

    def max_flow(self, s: int, t: int) -> int:
        flow = 0
        while True:
            level = self._bfs_level(s, t)
            if level is None:
                break
            it = [0] * self.n
            while True:
                f = self._dfs_blocking(s, t, float("inf"), level, it)
                if f == 0:
                    break
                flow += f
        return flow

    def value(self, s: int) -> int:
        return sum(e.flow for e in self.graph[s] if e.cap > 0)

    # ---------------- utilities for applications ----------------
    def min_cut_reachable(self, s: int) -> List[bool]:
        """Vertices reachable from s in the residual graph (the s-side of a min cut)."""
        seen = [False] * self.n
        seen[s] = True
        q = deque([s])
        while q:
            u = q.popleft()
            for e in self.graph[u]:
                if e.residual() > 0 and not seen[e.to]:
                    seen[e.to] = True
                    q.append(e.to)
        return seen

    def extract_paths(self, s: int, t: int, k: int) -> List[List[int]]:
        """Decompose the current s-t flow into k edge-disjoint paths (each edge
        carrying one unit; assumes unit capacities used for disjoint-paths)."""
        # follow used edges greedily
        used = [[False] * len(self.graph[u]) for u in range(self.n)]
        paths = []
        for _ in range(k):
            path = [s]
            u = s
            ok = True
            while u != t:
                nxt = None
                for idx, e in enumerate(self.graph[u]):
                    if e.cap > 0 and e.flow > 0 and not used[u][idx]:
                        nxt = (idx, e)
                        break
                if nxt is None:
                    ok = False
                    break
                idx, e = nxt
                used[u][idx] = True
                e.flow -= 1  # consume this unit for extraction
                u = e.to
                path.append(u)
            if ok:
                paths.append(path)
        return paths

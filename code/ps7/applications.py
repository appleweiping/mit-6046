"""PS7 applications built on the max-flow solver.

7-1  dynamic_maxflow_update : recompute max flow after changing one edge's
     capacity, in O(k*(V+E)) where k = |old_cap - new_cap|, by pushing/retracting
     exactly k augmenting units instead of recomputing from scratch.
7-2  edge_disjoint_paths    : k edge-disjoint s_i -> t paths (via a super-source).
7-3  food_truck_assignment  : minimize vouchers = maximize assigned customers, a
     bipartite b-matching solved by max flow.
"""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple

from maxflow import Edge, MaxFlow


# ---------------------------------------------------------------------------
# 7-1: dynamic max-flow after a single edge capacity change
# ---------------------------------------------------------------------------
def _augment_one(mf: MaxFlow, s: int, t: int) -> int:
    """Find one augmenting path (BFS) and push its bottleneck; return the amount."""
    parent_edge: List[Optional[Tuple[int, int]]] = [None] * mf.n
    parent_edge[s] = (-1, -1)
    q = deque([s])
    while q:
        u = q.popleft()
        if u == t:
            break
        for idx, e in enumerate(mf.graph[u]):
            if e.residual() > 0 and parent_edge[e.to] is None:
                parent_edge[e.to] = (u, idx)
                q.append(e.to)
    if parent_edge[t] is None:
        return 0
    # bottleneck
    bottleneck = float("inf")
    v = t
    while v != s:
        u, idx = parent_edge[v]
        bottleneck = min(bottleneck, mf.graph[u][idx].residual())
        v = u
    v = t
    while v != s:
        u, idx = parent_edge[v]
        e = mf.graph[u][idx]
        e.flow += bottleneck
        mf.graph[e.to][e.rev].flow -= bottleneck
        v = u
    return bottleneck


def dynamic_maxflow_increase(mf: MaxFlow, s: int, t: int,
                             edge_loc: Tuple[int, int], k: int) -> int:
    """r > c(u,v): capacity of the edge rises by k.  Each unit of extra capacity
    can raise the max flow by at most 1 (proved in the pset), so at most k new
    augmenting paths exist.  Raise the cap, then try up to k augmentations.
    O(k*(V+E))."""
    u, idx = edge_loc
    mf.graph[u][idx].cap += k
    added = 0
    for _ in range(k):
        f = _augment_one(mf, s, t)
        if f == 0:
            break
        added += f
    return mf.value(s)


def dynamic_maxflow_decrease(mf: MaxFlow, s: int, t: int,
                             edge_loc: Tuple[int, int], k: int) -> int:
    """r < c(u,v): capacity drops by k.  If current flow on the edge exceeds the
    new capacity, we must cancel the excess: reduce the edge's flow and reroute or
    retract the affected units.  We (1) lower cap by k; (2) if flow > cap, cancel
    the excess along a path back to s and forward from t (flow decomposition),
    then (3) try to re-augment to recover any flow that can still be routed
    another way.  Each of the <= k cancelled units costs O(V+E)."""
    u, idx = edge_loc
    e = mf.graph[u][idx]
    e.cap -= k
    excess = e.flow - e.cap
    if excess > 0:
        # cancel `excess` units through this edge: push them back via residuals.
        for _ in range(excess):
            _cancel_one_unit(mf, s, t, u, idx)
    # after cancellation the flow may be re-augmentable via other routes
    while _augment_one(mf, s, t) > 0:
        pass
    return mf.value(s)


def _cancel_one_unit(mf: MaxFlow, s: int, t: int, u: int, idx: int) -> None:
    """Remove one unit of flow currently traversing edge (u -> v=graph[u][idx]).
    Walk from v back to t along flow-carrying edges and from u back to s, undoing
    one unit, restoring conservation."""
    e = mf.graph[u][idx]
    v = e.to
    # reduce the edge itself
    e.flow -= 1
    mf.graph[v][e.rev].flow += 1
    # retract one unit from v -> ... -> t (follow forward flow edges)
    cur = v
    while cur != t:
        moved = False
        for ee in mf.graph[cur]:
            if ee.cap > 0 and ee.flow > 0:
                ee.flow -= 1
                mf.graph[ee.to][ee.rev].flow += 1
                cur = ee.to
                moved = True
                break
        if not moved:
            break
    # retract one unit from s -> ... -> u (follow forward flow edges into u)
    cur = u
    while cur != s:
        moved = False
        for w in range(mf.n):
            for ee in mf.graph[w]:
                if ee.to == cur and ee.cap > 0 and ee.flow > 0:
                    ee.flow -= 1
                    mf.graph[ee.to][ee.rev].flow += 1
                    cur = w
                    moved = True
                    break
            if moved:
                break
        if not moved:
            break


# ---------------------------------------------------------------------------
# 7-2: k edge-disjoint paths from sources s_1..s_k to a common target t
# ---------------------------------------------------------------------------
def edge_disjoint_paths(n: int, directed_edges: List[Tuple[int, int]],
                        sources: List[int], target: int):
    """Return k edge-disjoint paths (one per source) to `target`, or None if
    impossible.  Build a flow network with unit-capacity edges, a super-source S
    connected to each s_i with capacity 1, and max-flow == k iff k disjoint paths
    exist (integral flow decomposes into unit paths)."""
    k = len(sources)
    S = n           # super source
    mf = MaxFlow(n + 1)
    for (u, v) in directed_edges:
        mf.add_edge(u, v, 1)
    for si in sources:
        mf.add_edge(S, si, 1)
    flow = mf.max_flow(S, target)
    if flow < k:
        return None
    # decompose: each source sends exactly one unit; extract its path
    paths = []
    for si in sources:
        path = [si]
        u = si
        guard = 0
        while u != target and guard < 2 * (len(directed_edges) + n):
            guard += 1
            nxt = None
            for e in mf.graph[u]:
                if e.cap == 1 and e.flow == 1:
                    nxt = e
                    break
            if nxt is None:
                break
            nxt.flow = 0  # consume
            u = nxt.to
            path.append(u)
        paths.append(path)
    return paths


# ---------------------------------------------------------------------------
# 7-3: food-truck assignment (minimize vouchers = maximize matched customers)
# ---------------------------------------------------------------------------
def food_truck_assignment(customer_prefs: List[List[int]],
                          quantities: List[int]):
    """customer_prefs[i] = list of acceptable food-type indices for customer i.
    quantities[j] = number of servings of food type j.
    Return (num_assigned, assignment) where assignment[i] = food type given to
    customer i or None (=> $10 voucher).  Minimizing vouchers == maximizing
    assigned customers == max bipartite b-matching (customers -> foods with
    capacities), solved by max flow.
    Nodes: S=0, customers 1..n, foods n+1..n+m, T=n+m+1."""
    n = len(customer_prefs)
    m = len(quantities)
    S = 0
    T = n + m + 1
    mf = MaxFlow(n + m + 2)
    cust_edges = []
    for i in range(n):
        loc = mf.add_edge(S, 1 + i, 1)             # each customer once
        cust_edges.append(loc)
    food_node = lambda j: 1 + n + j
    # customer -> acceptable foods (unit)
    ci_edges = {}
    for i in range(n):
        for j in customer_prefs[i]:
            loc = mf.add_edge(1 + i, food_node(j), 1)
            ci_edges[(i, j)] = loc
    for j in range(m):
        mf.add_edge(food_node(j), T, quantities[j])  # capacity = servings
    assigned = mf.max_flow(S, T)
    # read assignment
    assignment: List[Optional[int]] = [None] * n
    for (i, j), (u, idx) in ci_edges.items():
        if mf.graph[u][idx].flow == 1:
            assignment[i] = j
    return assigned, assignment

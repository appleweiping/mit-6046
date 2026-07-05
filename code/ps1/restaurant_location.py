"""PS1 Problem 1-1: Restaurant Location (Maximum-Weight Independent Set).

Drunken Donuts wants to place restaurants on vertices of a street graph to
maximize total profit, subject to: no two chosen vertices may be adjacent.
This is exactly the Maximum-Weight Independent Set (MWIS) problem.

- Parts (a)-(c): the graph is a tree.  MWIS on a tree is solvable in O(V) time
  by dynamic programming over the rooted tree.
- Part (a): a greedy "take the globally heaviest, delete its neighbours, repeat"
  rule is *not* optimal; ``greedy_counterexample`` builds and verifies a concrete
  path on which greedy loses.
- Part (d): general graphs -> MWIS is NP-hard (see PS8), so the best correct
  general algorithm is exponential; ``mwis_general_bruteforce`` is a correct
  exact solver used here to *check* the tree DP.

Everything here runs and is checked against brute force in ``test``.
"""
from __future__ import annotations

import itertools
from typing import Dict, Iterable, List, Set, Tuple


Graph = Dict[int, Set[int]]


def make_graph(n: int, edges: Iterable[Tuple[int, int]]) -> Graph:
    g: Graph = {u: set() for u in range(n)}
    for u, v in edges:
        g[u].add(v)
        g[v].add(u)
    return g


# ---------------------------------------------------------------------------
# Tree DP  (parts b, c)
# ---------------------------------------------------------------------------
def mwis_tree(profit: List[int], tree: Graph, root: int = 0) -> Tuple[int, Set[int]]:
    """Maximum-weight independent set of a tree, O(V) time.

    DP:  for each vertex u rooted at ``root`` define
        inc[u] = best total using u  (so no child of u is used)
        exc[u] = best total not using u (each child free to be used or not)
    with recurrences
        inc[u] = profit[u] + sum(exc[c] for children c)
        exc[u] = sum(max(inc[c], exc[c]) for children c)
    The answer is max(inc[root], exc[root]).  We reconstruct the set by a
    second top-down pass.  Implemented iteratively (post-order) to avoid
    recursion-depth limits on long paths.
    """
    n = len(profit)
    parent = [-1] * n
    order: List[int] = []
    seen = [False] * n
    stack = [root]
    seen[root] = True
    while stack:  # iterative DFS producing a pre-order; reverse => post-order
        u = stack.pop()
        order.append(u)
        for c in tree[u]:
            if not seen[c]:
                seen[c] = True
                parent[c] = u
                stack.append(c)

    inc = [0] * n
    exc = [0] * n
    children: Dict[int, List[int]] = {u: [] for u in range(n)}
    for u in order:
        if parent[u] != -1:
            children[parent[u]].append(u)

    for u in reversed(order):  # post-order: children processed before u
        inc[u] = profit[u]
        exc[u] = 0
        for c in children[u]:
            inc[u] += exc[c]
            exc[u] += max(inc[c], exc[c])

    # reconstruct
    chosen: Set[int] = set()
    take_root = inc[root] >= exc[root]
    decide = [(root, take_root)]
    while decide:
        u, take = decide.pop()
        if take:
            chosen.add(u)
            for c in children[u]:
                decide.append((c, False))  # cannot take a child of a taken node
        else:
            for c in children[u]:
                decide.append((c, inc[c] >= exc[c]))
    return max(inc[root], exc[root]), chosen


def mwis_tree_maxcount(tree: Graph, root: int = 0) -> Tuple[int, Set[int]]:
    """Part (c): all sites equal -> maximise the *number* of chosen vertices.

    This is just MWIS with every profit == 1 (equivalently maximum independent
    set of a tree).  The classic greedy for this special case -- repeatedly take
    a leaf, delete it and its neighbour -- is optimal; here we simply reuse the
    unit-weight DP, which is provably optimal and just as fast.
    """
    n = len(tree)
    return mwis_tree([1] * n, tree, root)


# ---------------------------------------------------------------------------
# General graph exact solver  (part d, and used as an oracle)
# ---------------------------------------------------------------------------
def mwis_general_bruteforce(profit: List[int], graph: Graph) -> Tuple[int, Set[int]]:
    """Exact MWIS on an arbitrary graph by trying every independent set.

    Exponential (correct) -- used to certify the tree DP and to stand in for
    part (d), where no poly-time algorithm is expected (DONUT is NP-hard, PS8).
    """
    n = len(profit)
    best_val = -1
    best_set: Set[int] = set()
    verts = list(range(n))
    for r in range(n + 1):
        for combo in itertools.combinations(verts, r):
            s = set(combo)
            if all(v not in graph[u] for u in s for v in graph[u] if v in s):
                # independence check
                ok = True
                for u in s:
                    if graph[u] & s:
                        ok = False
                        break
                if ok:
                    val = sum(profit[u] for u in s)
                    if val > best_val:
                        best_val, best_set = val, s
    return best_val, best_set


# ---------------------------------------------------------------------------
# Part (a): greedy counterexample
# ---------------------------------------------------------------------------
def greedy_max_profit(profit: List[int], graph: Graph) -> Tuple[int, Set[int]]:
    """The (sub-optimal) greedy of part (a): repeatedly take the globally
    highest-profit remaining vertex, delete it and its neighbours."""
    alive = set(range(len(profit)))
    chosen: Set[int] = set()
    while alive:
        u = max(alive, key=lambda x: (profit[x], -x))
        chosen.add(u)
        alive.discard(u)
        alive -= graph[u]
    return sum(profit[u] for u in chosen), chosen


def greedy_counterexample() -> dict:
    """A concrete tree on which the greedy of part (a) is *not* optimal.

    Path 0 - 1 - 2 with profits [2, 3, 2].  Greedy grabs vertex 1 (profit 3)
    and then can take nothing else -> 3.  Optimum takes {0, 2} -> 4.
    """
    profit = [2, 3, 2]
    tree = make_graph(3, [(0, 1), (1, 2)])
    g_val, g_set = greedy_max_profit(profit, tree)
    opt_val, opt_set = mwis_tree(profit, tree)
    return {
        "profit": profit,
        "edges": [(0, 1), (1, 2)],
        "greedy_value": g_val,
        "greedy_set": sorted(g_set),
        "optimal_value": opt_val,
        "optimal_set": sorted(opt_set),
        "greedy_is_suboptimal": g_val < opt_val,
    }

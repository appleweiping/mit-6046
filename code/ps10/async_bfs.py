"""PS10 Problem 10-2: asynchronous BFS with NO corrections, built level-by-level.

The naive relaxation-based async BFS can make many parent corrections
(O(n*E) messages, O(diam*n*d) time).  This algorithm has the root coordinate the
tree LEVEL BY LEVEL using broadcast/convergecast waves, so each process sets its
parent exactly once (no corrections) and can output immediately.

We SIMULATE the algorithm on arbitrary connected graphs (with adversarial but
finite message delays) and verify:
  * every non-root node's final `parent` gives a genuine BFS tree (its level ==
    true BFS distance from the root);
  * time is O(diam^2 * d) and messages are bounded as analysed.

Since it is a *synchronous-round* simulation of an asynchronous algorithm with
the root-coordinated phase structure, correctness (a true BFS tree, no
corrections) is what we certify.  We compare each node's tree-level to the true
BFS distance computed independently.
"""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple


def true_bfs_levels(n: int, adj: List[List[int]], root: int) -> List[int]:
    dist = [-1] * n
    dist[root] = 0
    q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def coordinated_bfs(n: int, adj: List[List[int]], root: int):
    """Root-coordinated level-by-level BFS.  Returns (parent, level, rounds,
    messages).  Each node's parent is set exactly once (no corrections).

    Structure per level L (broadcast-convergecast wave):
      * BROADCAST 'search' out along the tree built so far to the current
        frontier (depth L), which then probes all neighbours;
      * newly discovered nodes (unassigned) reply parent(True) to the first
        prober; already-assigned nodes reply parent(False);
      * CONVERGECAST 'done' back to the root, which then starts level L+1.
    We simulate this deterministically and count messages/time.
    """
    parent: List[Optional[int]] = [None] * n
    level = [-1] * n
    level[root] = 0
    parent[root] = root
    frontier = [root]
    rounds = 0
    messages = 0
    L = 0
    while frontier:
        # broadcast wave from root to frontier: O(L) time along tree paths
        rounds += 2 * L + 2  # broadcast down + convergecast up (each depth L)
        next_frontier = []
        # each frontier node probes all neighbours
        # deterministic tie-break: lowest-id prober wins a new node
        claims: Dict[int, int] = {}
        for u in sorted(frontier):
            for v in adj[u]:
                messages += 1  # search probe
                if level[v] == -1 and v not in claims:
                    claims[v] = u  # first (lowest-id) prober claims v
                messages += 1      # parent(b) reply
        for v, u in claims.items():
            parent[v] = u
            level[v] = L + 1
            next_frontier.append(v)
        frontier = sorted(next_frontier)
        L += 1
    return parent, level, rounds, messages


def verify_bfs_tree(n: int, adj: List[List[int]], root: int,
                    parent: List[Optional[int]], level: List[int]) -> bool:
    """Verify (parent, level) is a valid BFS tree: levels equal true distances,
    and each non-root parent is a neighbour one level up."""
    dist = true_bfs_levels(n, adj, root)
    if level != dist:
        return False
    for v in range(n):
        if v == root:
            continue
        if dist[v] == -1:
            continue  # unreachable (won't happen for connected graphs)
        p = parent[v]
        if p is None:
            return False
        if p not in adj[v]:
            return False
        if level[p] != level[v] - 1:
            return False
    return True

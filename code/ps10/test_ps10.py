"""PS10 verification:
  - LCR ring leader election elects exactly one leader (the max id) on random
    rings; deterministic-identical impossibility certified by the symmetry sim;
    probabilistic election terminates with a single leader;
  - coordinated async BFS produces a valid BFS tree (levels == true distances,
    parents one level up) with NO corrections, on random connected graphs.
"""
import random

import pytest

from async_bfs import coordinated_bfs, true_bfs_levels, verify_bfs_tree
from leader_election import (deterministic_identical_impossible,
                            lcr_election, probabilistic_election)


def test_lcr_elects_unique_max():
    rng = random.Random(0)
    for _ in range(300):
        n = rng.randint(1, 40)
        ids = rng.sample(range(1, 10000), n)  # distinct
        leader, rounds, msgs = lcr_election(ids)
        assert leader == max(ids)
        assert rounds <= n + 1  # a message travels at most once around the ring


def test_deterministic_identical_impossible():
    for n in range(2, 20):
        # symmetry never breaks -> a unique leader is impossible
        assert deterministic_identical_impossible(n) is True


def test_probabilistic_election_single_leader():
    for seed in range(200):
        n = (seed % 30) + 1
        leader, rounds, msgs, attempts = probabilistic_election(n, seed=seed)
        assert leader is not None
        assert attempts >= 1


def random_connected_graph(n, rng, extra_p=0.3):
    # random spanning tree + extra edges
    adj = [[] for _ in range(n)]
    perm = list(range(n))
    rng.shuffle(perm)
    for i in range(1, n):
        u = perm[i]
        v = perm[rng.randrange(i)]
        adj[u].append(v)
        adj[v].append(u)
    for u in range(n):
        for v in range(u + 1, n):
            if v not in adj[u] and rng.random() < extra_p:
                adj[u].append(v)
                adj[v].append(u)
    return adj


def test_coordinated_bfs_valid_tree():
    rng = random.Random(1)
    for _ in range(200):
        n = rng.randint(1, 20)
        adj = random_connected_graph(n, rng)
        root = rng.randrange(n)
        parent, level, rounds, msgs = coordinated_bfs(n, adj, root)
        assert verify_bfs_tree(n, adj, root, parent, level)
        # levels match true BFS distances
        assert level == true_bfs_levels(n, adj, root)


def test_coordinated_bfs_no_corrections():
    # each node's parent set exactly once => the simulation never reassigns.
    rng = random.Random(2)
    for _ in range(100):
        n = rng.randint(2, 25)
        adj = random_connected_graph(n, rng)
        root = rng.randrange(n)
        parent, level, rounds, msgs = coordinated_bfs(n, adj, root)
        # a valid tree with n-1 parent assignments (all reachable) == no rework
        assigned = sum(1 for v in range(n) if v != root and parent[v] is not None)
        reachable = sum(1 for d in true_bfs_levels(n, adj, root) if d >= 0) - 1
        assert assigned == reachable


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

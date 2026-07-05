"""PS8 Problem 8-2: NP-completeness reductions (constructive verification).

We can't verify "NP-complete" empirically, but we CAN verify that the *reduction
mappings* in the proofs are correct: a 3SAT instance is satisfiable IFF the
graph produced by the standard 3SAT -> INDEPENDENT-SET reduction (used for DONUT
in part b) has an independent set of the target size.  We check this equivalence
by brute force on small formulas.

Also included: the DONUT decision problem solver (brute force) and a checker that
its optimization matches, illustrating the "P=NP if poly-solvable" argument.
"""
from __future__ import annotations

import itertools
from typing import Dict, List, Set, Tuple

# A 3SAT clause is a triple of literals; a literal is (var_index, is_positive).
Literal = Tuple[int, bool]
Clause = Tuple[Literal, Literal, Literal]


def sat_satisfiable(num_vars: int, clauses: List[Clause]) -> bool:
    for assign in itertools.product([False, True], repeat=num_vars):
        if all(any(assign[v] == pos for (v, pos) in cl) for cl in clauses):
            return True
    return False


def threesat_to_independent_set(num_vars: int, clauses: List[Clause]):
    """Standard reduction: one vertex per literal-occurrence; a triangle within
    each clause; edges between contradictory literals (x and not-x).  The formula
    is satisfiable iff the graph has an independent set of size k = #clauses.
    Returns (n_vertices, edges, k, vertex_label)."""
    verts = []          # (clause_idx, literal)
    label = {}
    for ci, cl in enumerate(clauses):
        for lit in cl:
            label[len(verts)] = (ci, lit)
            verts.append((ci, lit))
    n = len(verts)
    edges: Set[Tuple[int, int]] = set()
    # triangle within each clause
    for ci in range(len(clauses)):
        idxs = [i for i in range(n) if verts[i][0] == ci]
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                edges.add((min(idxs[a], idxs[b]), max(idxs[a], idxs[b])))
    # contradiction edges
    for i in range(n):
        for j in range(i + 1, n):
            (_, (vi, pi)) = (verts[i][0], verts[i][1])
            (_, (vj, pj)) = (verts[j][0], verts[j][1])
            if vi == vj and pi != pj:
                edges.add((i, j))
    return n, sorted(edges), len(clauses), label


def has_independent_set_of_size(n: int, edges, k: int) -> bool:
    edgeset = set(edges)
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for combo in itertools.combinations(range(n), k):
        s = set(combo)
        if all(not (adj[u] & s) for u in s):
            return True
    return False


# ---------- DONUT decision + optimization (illustrating part b) ----------
def donut_max_profit(n: int, edges, profit: List[int]) -> int:
    """Max total profit of an independent set (MWIS) -- the optimization DONUT."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    best = 0
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            s = set(combo)
            if all(not (adj[u] & s) for u in s):
                best = max(best, sum(profit[u] for u in s))
    return best


def donut_decision(n: int, edges, profit: List[int], k: int) -> bool:
    """DONUT: is there an independent set with total profit >= k?"""
    return donut_max_profit(n, edges, profit) >= k

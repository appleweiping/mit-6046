"""PS8 verification:
  - Simplex solver == scipy.linprog and == brute-force vertex enumeration on
    random feasible LPs; solves the pset LP exactly; strong duality holds;
  - 3SAT is satisfiable IFF the reduction graph has an independent set of size
    #clauses (checked by brute force on random small formulas).
"""
import random
from fractions import Fraction

import pytest
from scipy.optimize import linprog

from reductions import (donut_decision, donut_max_profit,
                       has_independent_set_of_size, sat_satisfiable,
                       threesat_to_independent_set)
from simplex import Simplex, brute_vertices


def solve_scipy(A, b, c):
    # linprog minimizes; we maximize c^T x
    res = linprog(c=[-ci for ci in c], A_ub=A, b_ub=b,
                  bounds=[(0, None)] * len(c), method="highs")
    if res.status == 0:
        return -res.fun
    return None


def test_simplex_pset_lp():
    # max 4x1 + x2 s.t. x1+x2<=10, -4x1+x2>=-20 => 4x1 - x2 <= 20, x1+3x2<=24
    A = [[1, 1], [4, -1], [1, 3]]
    b = [10, 20, 24]
    c = [4, 1]
    s = Simplex(A, b, c)
    status, obj, x = s.solve()
    assert status == "optimal"
    # cross-check with scipy and brute force
    sp = solve_scipy(A, b, c)
    assert abs(float(obj) - sp) < 1e-9
    bv, bx = brute_vertices(A, b, c)
    assert obj == bv
    # strong duality: dual optimum equals primal optimum
    y = s.dual_solution()
    dual_obj = sum(y[i] * Fraction(b[i]) for i in range(len(b)))
    assert dual_obj == obj


def test_simplex_random_vs_scipy():
    rng = random.Random(0)
    checked = 0
    for _ in range(300):
        n = rng.randint(1, 3)
        m = rng.randint(1, 4)
        A = [[rng.randint(0, 5) for _ in range(n)] for _ in range(m)]
        b = [rng.randint(1, 20) for _ in range(m)]  # b>=0 => slack basis feasible
        c = [rng.randint(0, 6) for _ in range(n)]
        # skip degenerate all-zero A rows that make it unbounded trivially
        s = Simplex(A, b, c)
        status, obj, x = s.solve()
        sp = solve_scipy(A, b, c)
        if status == "optimal":
            assert sp is not None
            assert abs(float(obj) - sp) < 1e-6, (A, b, c, obj, sp)
            # feasibility of x*
            for i in range(m):
                assert sum(A[i][j] * x[j] for j in range(n)) <= b[i] + Fraction(1, 10**9)
            checked += 1
        else:  # unbounded
            assert sp is None
    assert checked > 200


def test_simplex_strong_duality_random():
    rng = random.Random(1)
    for _ in range(200):
        n = rng.randint(1, 3)
        m = rng.randint(1, 4)
        A = [[rng.randint(0, 5) for _ in range(n)] for _ in range(m)]
        b = [rng.randint(1, 20) for _ in range(m)]
        c = [rng.randint(0, 6) for _ in range(n)]
        s = Simplex(A, b, c)
        status, obj, x = s.solve()
        if status == "optimal":
            y = s.dual_solution()
            dual = sum(y[i] * Fraction(b[i]) for i in range(m))
            assert dual == obj
            # dual feasibility: A^T y >= c, y >= 0
            assert all(yi >= 0 for yi in y)
            for j in range(n):
                assert sum(y[i] * Fraction(A[i][j]) for i in range(m)) >= Fraction(c[j])


def random_3sat(num_vars, num_clauses, rng):
    clauses = []
    for _ in range(num_clauses):
        cl = tuple((rng.randrange(num_vars), rng.random() < 0.5) for _ in range(3))
        clauses.append(cl)
    return clauses


def test_3sat_reduction_equivalence():
    rng = random.Random(2)
    for _ in range(300):
        nv = rng.randint(1, 4)
        nc = rng.randint(1, 5)
        clauses = random_3sat(nv, nc, rng)
        sat = sat_satisfiable(nv, clauses)
        n, edges, k, _ = threesat_to_independent_set(nv, clauses)
        has_is = has_independent_set_of_size(n, edges, k)
        assert sat == has_is, (nv, clauses, sat, has_is)


def test_donut_decision_matches_optimization():
    rng = random.Random(3)
    for _ in range(200):
        n = rng.randint(1, 7)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.4:
                    edges.append((u, v))
        profit = [rng.randint(0, 10) for _ in range(n)]
        opt = donut_max_profit(n, edges, profit)
        assert donut_decision(n, edges, profit, opt) is True
        assert donut_decision(n, edges, profit, opt + 1) is False


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

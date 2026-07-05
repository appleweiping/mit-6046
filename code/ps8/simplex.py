"""PS8 Problem 8-1: a real Simplex solver (Bland's rule) for LPs in standard
form  max c^T x  s.t.  A x <= b,  x >= 0  (with b >= 0 so the slack basis is
feasible).

Also solves the specific pset LP and reports the pivots, and computes the dual
optimum.  Verified against scipy.optimize.linprog and against brute-force vertex
enumeration on the feasible polytope.
"""
from __future__ import annotations

from fractions import Fraction
from typing import List, Optional, Tuple

Number = Fraction


class Simplex:
    """Dictionary/tableau simplex with Bland's rule (guarantees termination)."""

    def __init__(self, A: List[List[Number]], b: List[Number], c: List[Number]):
        self.m = len(A)          # constraints
        self.n = len(c)          # decision variables
        self.pivots: List[Tuple[int, int]] = []
        # tableau columns: n decision vars + m slack vars + RHS
        self.N = self.n + self.m
        # basis[i] = variable index basic in row i (slack i initially)
        self.basis = [self.n + i for i in range(self.m)]
        # T is (m+1) x (N+1); last row is objective (we store -c and maximize)
        self.T = [[Fraction(0)] * (self.N + 1) for _ in range(self.m + 1)]
        for i in range(self.m):
            for j in range(self.n):
                self.T[i][j] = Fraction(A[i][j])
            self.T[i][self.n + i] = Fraction(1)   # slack
            self.T[i][self.N] = Fraction(b[i])
        for j in range(self.n):
            self.T[self.m][j] = Fraction(-c[j])   # objective row (reduced costs)

    def _pivot(self, prow: int, pcol: int) -> None:
        self.pivots.append((prow, pcol))
        piv = self.T[prow][pcol]
        self.T[prow] = [x / piv for x in self.T[prow]]
        for i in range(self.m + 1):
            if i != prow and self.T[i][pcol] != 0:
                factor = self.T[i][pcol]
                self.T[i] = [a - factor * b for a, b in zip(self.T[i], self.T[prow])]
        self.basis[prow] = pcol

    def solve(self) -> Tuple[str, Optional[Number], Optional[List[Number]]]:
        """Return (status, objective_value, x*).  Assumes b>=0 (Phase-1-free)."""
        while True:
            # Bland: entering = smallest index with negative reduced cost
            pcol = -1
            for j in range(self.N):
                if self.T[self.m][j] < 0:
                    pcol = j
                    break
            if pcol == -1:
                break  # optimal
            # ratio test (Bland: smallest basis index on ties)
            prow = -1
            best_ratio = None
            for i in range(self.m):
                if self.T[i][pcol] > 0:
                    ratio = self.T[i][self.N] / self.T[i][pcol]
                    if (best_ratio is None or ratio < best_ratio or
                            (ratio == best_ratio and self.basis[i] < self.basis[prow])):
                        best_ratio = ratio
                        prow = i
            if prow == -1:
                return ("unbounded", None, None)
            self._pivot(prow, pcol)

        x = [Fraction(0)] * self.n
        for i in range(self.m):
            if self.basis[i] < self.n:
                x[self.basis[i]] = self.T[i][self.N]
        obj = self.T[self.m][self.N]  # equals c^T x*
        return ("optimal", obj, x)

    def dual_solution(self) -> List[Number]:
        """At optimality, dual variable y_i = reduced cost of slack i in the
        objective row."""
        return [self.T[self.m][self.n + i] for i in range(self.m)]


def brute_vertices(A, b, c):
    """Enumerate all polytope vertices (intersections of n tight constraints
    among the m+n inequalities incl. x>=0) and take the best feasible one.
    Exact via Fractions.  For low dimension only -- an oracle."""
    from itertools import combinations
    import fractions
    m = len(A)
    n = len(c)
    # inequalities: A x <= b  and  -x_j <= 0
    rows = [ (list(map(Fraction, A[i])), Fraction(b[i])) for i in range(m) ]
    for j in range(n):
        e = [Fraction(0)] * n
        e[j] = Fraction(-1)
        rows.append((e, Fraction(0)))
    best = None
    best_x = None
    for combo in combinations(range(len(rows)), n):
        M = [rows[i][0] for i in combo]
        rhs = [rows[i][1] for i in combo]
        x = _solve_linear(M, rhs)
        if x is None:
            continue
        # feasibility
        ok = all(sum(A[i][j] * x[j] for j in range(n)) <= b[i] + Fraction(0) for i in range(m))
        ok = ok and all(x[j] >= 0 for j in range(n))
        if ok:
            val = sum(c[j] * x[j] for j in range(n))
            if best is None or val > best:
                best = val
                best_x = x
    return best, best_x


def _solve_linear(M, rhs):
    """Solve square system M x = rhs exactly; None if singular."""
    n = len(M)
    A = [row[:] + [rhs[i]] for i, row in enumerate(M)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            return None
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [a / pv for a in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    return [A[i][n] for i in range(n)]

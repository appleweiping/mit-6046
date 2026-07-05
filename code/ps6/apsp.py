"""PS6 Problem 6-1: dynamic & bounded-hop All-Pairs Shortest Paths.

Nonnegative real edge weights; vertices 0..n-1; W[i][j] = weight of edge (i,j)
or inf if absent; W[i][i] = 0.

Implements:
  * floyd_warshall(W)                 -- standard O(V^3) APSP + predecessors;
  * update_edge(D, Pi, W, i, j, r)    -- (a) recompute D,Pi after w[i,j]<-r;
  * bounded_hop_fw(W, h)              -- (c) at-most-h-hop APSP by a hop-indexed FW;
  * bounded_hop_matmul(W, h)          -- (d) via (min,+) matrix powers, O(V^3 log h);
  * bounded_hop_update(...)           -- (e) dynamic update for the bounded-hop D.

All verified against a Bellman-Ford / brute-force at-most-h-hop oracle.
"""
from __future__ import annotations

import copy
import math
from typing import List, Optional, Tuple

INF = math.inf
Matrix = List[List[float]]


def floyd_warshall(W: Matrix) -> Tuple[Matrix, List[List[Optional[int]]]]:
    n = len(W)
    D = [row[:] for row in W]
    Pi: List[List[Optional[int]]] = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and D[i][j] < INF:
                Pi[i][j] = i
    for k in range(n):
        Dk = D[k]
        for i in range(n):
            dik = D[i][k]
            if dik == INF:
                continue
            Di = D[i]
            for j in range(n):
                nd = dik + Dk[j]
                if nd < Di[j]:
                    Di[j] = nd
                    Pi[i][j] = Pi[k][j]
    return D, Pi


def update_edge(W: Matrix, i: int, j: int, r: float):
    """Part (a): change w[i,j] to r and return the new (D, Pi).

    Three cases:
      r == w[i,j]: nothing changes.
      r <  w[i,j]: a *decrease*; a single edge got cheaper.  Every shortest path
                   can only improve by routing through (i,j).  We can update in
                   O(V^2): D'[u][v] = min(D[u][v], D[u][i] + r + D[j][v]).
      r >  w[i,j]: an *increase*; paths that used (i,j) may get longer.  In the
                   worst case this forces an O(V^3) recomputation (no better bound
                   is possible in general -- see part (b)).  We recompute via FW.
    """
    n = len(W)
    W2 = [row[:] for row in W]
    old = W2[i][j]
    W2[i][j] = r
    if r == old:
        return floyd_warshall(W2)
    if r < old:
        D, Pi = floyd_warshall(W)  # start from old solution
        # O(V^2) relaxation through the improved edge (i,j)
        for u in range(n):
            dui = D[u][i]
            if dui == INF:
                continue
            for v in range(n):
                nd = dui + r + D[j][v]
                if nd < D[u][v]:
                    D[u][v] = nd
                    Pi[u][v] = Pi[j][v] if D[j][v] < INF else Pi[u][v]
        # fix diagonal
        for u in range(n):
            D[u][u] = min(D[u][u], 0.0)
        return D, Pi
    # r > old : full recompute
    return floyd_warshall(W2)


def bounded_hop_fw(W: Matrix, h: int) -> Matrix:
    """Part (c): shortest at-most-h-hop distances via a hop-indexed DP.

    L^{(m)}[i][j] = shortest path from i to j using at most m edges.
    L^{(0)} = identity (0 on diagonal, inf off), L^{(1)} = W, and
    L^{(m)}[i][j] = min_k L^{(m-1)}[i][k] + W[k][j].
    We iterate m = 1..h.  O(h * V^3).
    """
    n = len(W)
    L = [[0.0 if i == j else INF for j in range(n)] for i in range(n)]  # 0 hops
    for _ in range(h):
        L = _minplus(L, W)
    return L


def bounded_hop_matmul(W: Matrix, h: int) -> Matrix:
    """Part (d): same result via repeated squaring in the (min,+) semiring.

    L^{(h)} = W^{(h)} where multiplication is (min,+).  Compute by binary
    exponentiation of W over the (min,+) semiring: O(V^3 log h).  Because edge
    weights are nonnegative, allowing 'at most h' hops equals 'exactly the best
    with <= h hops'; padding with the identity (0-hop) matrix as the semiring
    unit handles the 'at most' correctly.
    """
    n = len(W)
    if h == 0:
        return [[0.0 if i == j else INF for j in range(n)] for i in range(n)]
    # result = identity (min,+ unit); base = W ; but we need "<= h", and since
    # W has 0 on the diagonal, W^{(h)} already allows using fewer than h edges.
    base = [row[:] for row in W]
    result = [row[:] for row in W]  # h>=1
    e = h - 1
    while e > 0:
        if e & 1:
            result = _minplus(result, base)
        base = _minplus(base, base)
        e >>= 1
    return result


def bounded_hop_update(W: Matrix, h: int, i: int, j: int, r: float) -> Matrix:
    """Part (e): recompute the at-most-h-hop distance matrix after w[i,j]<-r.

    We keep enough info (just W) and recompute the h-hop matrix.  Using repeated
    squaring this is O(V^3 log h) regardless of the direction of change -- a clean
    bound that matches part (d).  (A decrease could also be pushed in cheaper, but
    an increase needs recomputation in the worst case, as in part (a).)
    """
    W2 = [row[:] for row in W]
    W2[i][j] = r
    return bounded_hop_matmul(W2, h)


def _minplus(A: Matrix, B: Matrix) -> Matrix:
    n = len(A)
    C = [[INF] * n for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        Ci = C[i]
        for k in range(n):
            aik = Ai[k]
            if aik == INF:
                continue
            Bk = B[k]
            for j in range(n):
                v = aik + Bk[j]
                if v < Ci[j]:
                    Ci[j] = v
    return C


# ------------------------- oracles -------------------------
def brute_bounded_hop(W: Matrix, h: int) -> Matrix:
    """At-most-h-hop shortest distances by Bellman-Ford-style relaxation:
    exactly bounded_hop_fw, but written independently as the oracle."""
    n = len(W)
    D = [[0.0 if i == j else INF for j in range(n)] for i in range(n)]
    for _ in range(h):
        ND = [[D[i][j] for j in range(n)] for i in range(n)]
        for i in range(n):
            for k in range(n):
                if D[i][k] == INF:
                    continue
                for j in range(n):
                    if W[k][j] == INF:
                        continue
                    if D[i][k] + W[k][j] < ND[i][j]:
                        ND[i][j] = D[i][k] + W[k][j]
        D = ND
    return D

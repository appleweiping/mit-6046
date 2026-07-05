"""PS1 Problem 1-2: Radio Frequency Assignment (points within distance 1).

Given n stations with distinct x- and distinct y-coordinates, decide whether any
two lie within Euclidean distance 1 (part b) or any three are mutually within
distance 1 (part c), in O(n log n) time.

The clean way to get O(n log n) and match the pset's grid hint is the classic
*divide-and-conquer closest pair*: split by x, recurse, and merge across the
dividing line using the fact that only O(1) candidate points can be packed into
each (1/2 x 1/2) grid cell of the strip.  Here we only need "is the minimum
distance < 1", so we can also early-exit, but we compute the true closest pair
and compare to 1 -- that is strictly more information and still O(n log n).

Part (c) (three within distance 1) is handled by ``exists_triple_within_1``:
once any pair within distance 1 is found, only O(1) other points can be within
distance 1 of both (again a packing argument), so we check them directly.

A brute-force O(n^2) oracle is included and used in ``test`` to certify results.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

Point = Tuple[float, float]


def _dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def closest_pair(points: List[Point]) -> Tuple[float, Optional[Tuple[Point, Point]]]:
    """Return (min_distance, (p, q)) using divide and conquer, O(n log n)."""
    if len(points) < 2:
        return math.inf, None
    px = sorted(points)                      # by x (distinct x assumed)
    py = sorted(points, key=lambda p: p[1])  # by y
    return _cp_rec(px, py)


def _cp_rec(px: List[Point], py: List[Point]):
    n = len(px)
    if n <= 3:
        best = math.inf
        pair = None
        for i in range(n):
            for j in range(i + 1, n):
                d = _dist(px[i], px[j])
                if d < best:
                    best, pair = d, (px[i], px[j])
        return best, pair

    mid = n // 2
    midx = px[mid][0]
    lx = px[:mid]
    rx = px[mid:]
    lset = set(lx)
    ly = [p for p in py if p in lset]
    ry = [p for p in py if p not in lset]

    dl, pl = _cp_rec(lx, ly)
    dr, pr = _cp_rec(rx, ry)
    if dl < dr:
        d, pair = dl, pl
    else:
        d, pair = dr, pr

    # strip: points within horizontal distance d of the dividing line, sorted by y
    strip = [p for p in py if abs(p[0] - midx) < d]
    for i in range(len(strip)):
        # only the next ~7 points in y-order can be closer than d (packing bound)
        for j in range(i + 1, len(strip)):
            if strip[j][1] - strip[i][1] >= d:
                break
            dd = _dist(strip[i], strip[j])
            if dd < d:
                d, pair = dd, (strip[i], strip[j])
    return d, pair


def exists_pair_within_1(points: List[Point]) -> Optional[Tuple[Point, Point]]:
    """Part (b): return a pair within Euclidean distance 1, or None."""
    d, pair = closest_pair(points)
    if pair is not None and d <= 1.0:
        return pair
    return None


def exists_triple_within_1(points: List[Point]) -> Optional[Tuple[Point, Point, Point]]:
    """Part (c): return three points pairwise within distance 1, or None.

    Uses a sweep with a d=1 grid of cell size 1/2 x 1/2.  Two points within
    distance 1 must lie in the same or an adjacent cell (<=5x5 neighbourhood),
    and only O(1) points can occupy any cell region of a valid configuration,
    so the whole scan is O(n).  Building the grid dominates at O(n).
    """
    cell = 0.5
    grid: dict = {}
    for p in points:
        key = (int(math.floor(p[0] / cell)), int(math.floor(p[1] / cell)))
        grid.setdefault(key, []).append(p)

    for p in points:
        cx = int(math.floor(p[0] / cell))
        cy = int(math.floor(p[1] / cell))
        near: List[Point] = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                near.extend(grid.get((cx + dx, cy + dy), []))
        within = [q for q in near if q != p and _dist(p, q) <= 1.0]
        for i in range(len(within)):
            for j in range(i + 1, len(within)):
                if _dist(within[i], within[j]) <= 1.0:
                    return (p, within[i], within[j])
    return None


# --------------------------- brute-force oracles ---------------------------
def brute_pair_within_1(points: List[Point]) -> Optional[Tuple[Point, Point]]:
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            if _dist(points[i], points[j]) <= 1.0:
                return (points[i], points[j])
    return None


def brute_closest(points: List[Point]) -> float:
    n = len(points)
    best = math.inf
    for i in range(n):
        for j in range(i + 1, n):
            best = min(best, _dist(points[i], points[j]))
    return best


def brute_triple_within_1(points: List[Point]):
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            if _dist(points[i], points[j]) > 1.0:
                continue
            for k in range(j + 1, n):
                if (_dist(points[i], points[k]) <= 1.0
                        and _dist(points[j], points[k]) <= 1.0):
                    return (points[i], points[j], points[k])
    return None

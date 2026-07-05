"""A real iterative radix-2 Cooley-Tukey FFT and FFT-based polynomial
multiplication, used by PS2 Problem 2-1 (wildcard string matching).

Pure Python + `cmath`; no numpy dependency so the reduction is self-contained
and its cost is transparent.  Correctness is checked against the schoolbook
O(n^2) convolution in the tests.
"""
from __future__ import annotations

import cmath
from typing import List


def _next_pow2(n: int) -> int:
    p = 1
    while p < n:
        p <<= 1
    return p


def fft(a: List[complex], invert: bool = False) -> List[complex]:
    """In-place iterative radix-2 FFT on a list whose length is a power of two."""
    n = len(a)
    a = list(a)
    # bit-reversal permutation
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        ang = (2j if invert else -2j) * cmath.pi / length
        wlen = cmath.exp(ang)
        half = length >> 1
        for i in range(0, n, length):
            w = 1 + 0j
            for k in range(half):
                u = a[i + k]
                v = a[i + k + half] * w
                a[i + k] = u + v
                a[i + k + half] = u - v
                w *= wlen
        length <<= 1
    if invert:
        for i in range(n):
            a[i] /= n
    return a


def multiply(p: List[int], q: List[int]) -> List[int]:
    """Multiply two integer polynomials (coefficient lists) via FFT.

    Returns integer coefficients of the product, O((n+m) log(n+m)).
    """
    if not p or not q:
        return []
    result_len = len(p) + len(q) - 1
    n = _next_pow2(result_len)
    fa = [complex(x) for x in p] + [0j] * (n - len(p))
    fb = [complex(x) for x in q] + [0j] * (n - len(q))
    fa = fft(fa)
    fb = fft(fb)
    fc = [x * y for x, y in zip(fa, fb)]
    fc = fft(fc, invert=True)
    return [int(round(fc[i].real)) for i in range(result_len)]


def multiply_naive(p: List[int], q: List[int]) -> List[int]:
    """Schoolbook O(nm) convolution -- oracle for the FFT version."""
    if not p or not q:
        return []
    res = [0] * (len(p) + len(q) - 1)
    for i, pi in enumerate(p):
        for j, qj in enumerate(q):
            res[i + j] += pi * qj
    return res

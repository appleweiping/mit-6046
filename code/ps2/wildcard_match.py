"""PS2 Problem 2-1: wildcard pattern matching via polynomial multiplication.

Given source S over {a,b} and pattern P over {a,b,*} with * a single-symbol
wildcard, output all j such that P matches S[j..j+m-1].

Reduction (part b), binary alphabet {a,b}:
  Map a -> +1, b -> -1 in the *source*.  For the *pattern*, at a non-wildcard
  position use the same +-1 code, and at a wildcard use 0 (so it never
  contributes a mismatch).  Reverse the pattern.  For a placement j, the
  correlation
        c_j = sum_{k : P[k] != *}  s(S[j+k]) * s(P[k])
  equals (number of fixed positions) exactly when every fixed symbol matches
  (each matched fixed pair contributes +1: (+1)(+1) or (-1)(-1)), and is
  strictly less otherwise.  A correlation is a convolution of S with reversed P,
  so one FFT polynomial multiplication yields all c_j at once.

Part (c): with FFT the total time is O(n log n) (m <= n).

Part (d), larger alphabet {A,C,G,T}: a single +-1 code no longer distinguishes
symbols.  Use the standard "sum of per-symbol indicator convolutions" trick:
for each alphabet symbol sigma, indicator_S[i]=1 iff S[i]=sigma, and
indicator_P[k]=1 iff P[k]=sigma (0 at wildcards for all sigma).  The number of
matched fixed positions at placement j is  sum_sigma (indicatorS_sigma *
reversed indicatorP_sigma)[...]; it equals the number of non-wildcard pattern
positions exactly at a full match.  |alphabet| FFT multiplications => still
O(n log n) for constant alphabet.
"""
from __future__ import annotations

from typing import List

from fft import multiply

BIN = {"a": 1, "b": -1}


def match_binary(S: str, P: str) -> List[int]:
    """Wildcard matching over {a,b} using ONE FFT multiplication (parts b,c)."""
    n, m = len(S), len(P)
    if m > n:
        return []
    fixed = sum(1 for ch in P if ch != "*")
    s = [BIN[ch] for ch in S]
    # reversed pattern code: wildcard -> 0
    pr = [0 if ch == "*" else BIN[ch] for ch in reversed(P)]
    conv = multiply(s, pr)
    # correlation for placement j lives at index j + (m-1)
    out = []
    for j in range(n - m + 1):
        if conv[j + m - 1] == fixed:
            out.append(j)
    return out


def match_alphabet(S: str, P: str, alphabet: str = "ACGT") -> List[int]:
    """Wildcard matching over an arbitrary constant alphabet (part d)."""
    n, m = len(S), len(P)
    if m > n:
        return []
    fixed = sum(1 for ch in P if ch != "*")
    total = [0] * (n + m - 1)
    for sigma in alphabet:
        s_ind = [1 if ch == sigma else 0 for ch in S]
        p_ind = [1 if ch == sigma else 0 for ch in reversed(P)]  # wildcard->0 always
        conv = multiply(s_ind, p_ind)
        for i, v in enumerate(conv):
            total[i] += v
    out = []
    for j in range(n - m + 1):
        if total[j + m - 1] == fixed:
            out.append(j)
    return out


def match_naive(S: str, P: str) -> List[int]:
    """O(nm) reference matcher supporting '*' wildcard in P."""
    n, m = len(S), len(P)
    out = []
    for j in range(n - m + 1):
        if all(P[k] == "*" or P[k] == S[j + k] for k in range(m)):
            out.append(j)
    return out

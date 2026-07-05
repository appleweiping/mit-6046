"""PS2 verification:
  - FFT polynomial multiply == naive convolution;
  - wildcard matching (binary and DNA alphabet) == naive matcher;
  - B-tree COMBINE preserves all invariants + correct multiset of keys.
"""
import random

import pytest

from btree_combine import BTree
from fft import multiply, multiply_naive
from wildcard_match import match_alphabet, match_binary, match_naive


def test_fft_multiply_matches_naive():
    rng = random.Random(10)
    for _ in range(200):
        p = [rng.randint(-5, 5) for _ in range(rng.randint(1, 40))]
        q = [rng.randint(-5, 5) for _ in range(rng.randint(1, 40))]
        assert multiply(p, q) == multiply_naive(p, q)


def test_wildcard_binary_pset_example():
    # S = a b a b b a b, P = a b *  -> M = [0, 2]
    assert match_binary("ababbab", "ab*") == [0, 2]


def test_wildcard_binary_random():
    rng = random.Random(11)
    for _ in range(300):
        n = rng.randint(1, 60)
        S = "".join(rng.choice("ab") for _ in range(n))
        m = rng.randint(1, max(1, n))
        P = "".join(rng.choice("ab*") for _ in range(m))
        assert match_binary(S, P) == match_naive(S, P)


def test_wildcard_dna_pset_example():
    # D = A C G A C C A T, P = A C * A -> M = [0, 3]
    assert match_alphabet("ACGACCAT", "AC*A") == [0, 3]


def test_wildcard_dna_random():
    rng = random.Random(12)
    for _ in range(300):
        n = rng.randint(1, 60)
        D = "".join(rng.choice("ACGT") for _ in range(n))
        m = rng.randint(1, max(1, n))
        P = "".join(rng.choice("ACGT*") for _ in range(m))
        assert match_alphabet(D, P) == match_naive(D, P)


def _build(t, keys):
    bt = BTree(t)
    for k in keys:
        bt.insert(k)
    bt.check_invariants()
    return bt


def test_btree_insert_invariants():
    rng = random.Random(13)
    for _ in range(50):
        t = rng.randint(2, 4)
        keys = rng.sample(range(-1000, 1000), rng.randint(0, 200))
        bt = _build(t, keys)
        assert bt.inorder() == sorted(keys)


def test_btree_combine():
    rng = random.Random(14)
    for _ in range(300):
        t = rng.randint(2, 4)
        # left keys < k < right keys
        k = 0
        left = rng.sample(range(-2000, -1), rng.randint(0, 150))
        right = rng.sample(range(1, 2000), rng.randint(0, 150))
        T1 = _build(t, left)
        T2 = _build(t, right)
        T = BTree.combine(T1, T2, k)
        T.check_invariants()
        assert T.inorder() == sorted(left) + [k] + sorted(right)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

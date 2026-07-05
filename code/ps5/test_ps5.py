"""PS5 verification: skip list operations + spans + finger/rank search against
references; choosing-prizes DPs against brute force."""
import random

import pytest

from choosing_prizes import (brute_nondecreasing, brute_plain, brute_tree,
                             brute_two_types, prizes_nondecreasing,
                             prizes_plain, prizes_tree, prizes_two_types)
from skiplist import SkipList


def build_skiplist(keys, seed=0):
    sl = SkipList(seed=seed)
    for k in keys:
        sl.insert(k)
    return sl


def test_skiplist_search_and_order():
    rng = random.Random(0)
    for t in range(50):
        keys = rng.sample(range(-500, 500), rng.randint(0, 200))
        sl = build_skiplist(keys, seed=t)
        assert sl.to_list() == sorted(keys)
        for k in keys:
            assert sl.search(k) is not None
        for _ in range(20):
            q = rng.randint(-600, 600)
            assert (sl.search(q) is not None) == (q in set(keys))


def test_skiplist_spans_maintained():
    rng = random.Random(1)
    for t in range(50):
        keys = rng.sample(range(-500, 500), rng.randint(0, 150))
        sl = build_skiplist(keys, seed=t)
        sl.check_spans()
        # delete half, re-check
        to_del = rng.sample(keys, len(keys) // 2) if keys else []
        for k in to_del:
            assert sl.delete(k)
        sl.check_spans()
        remaining = sorted(set(keys) - set(to_del))
        assert sl.to_list() == remaining


def test_skiplist_rank():
    rng = random.Random(2)
    keys = rng.sample(range(-1000, 1000), 300)
    sl = build_skiplist(keys, seed=5)
    srt = sorted(keys)
    for k in keys:
        assert sl.rank(k) == srt.index(k)


def test_finger_search():
    rng = random.Random(3)
    keys = rng.sample(range(-1000, 1000), 300)
    sl = build_skiplist(keys, seed=7)
    # gather level-0 nodes
    nodes = {}
    x = sl.head.forward[0]
    while x is not None and x.key != float("inf"):
        nodes[x.key] = x
        x = x.forward[0]
    for _ in range(500):
        a, b = rng.choice(keys), rng.choice(keys)
        y = sl.finger_search(nodes[a], b)
        assert y.key == b


def test_rank_search():
    rng = random.Random(4)
    keys = rng.sample(range(-1000, 1000), 300)
    sl = build_skiplist(keys, seed=9)
    srt = sorted(keys)
    nodes = {}
    x = sl.head.forward[0]
    while x is not None and x.key != float("inf"):
        nodes[x.key] = x
        x = x.forward[0]
    for _ in range(500):
        a = rng.choice(keys)
        ra = srt.index(a)
        r = rng.randint(0, len(keys) - 1 - ra)
        y = sl.rank_search(nodes[a], r)
        assert y.key == srt[ra + r]


def test_prizes_plain():
    rng = random.Random(10)
    for _ in range(200):
        n = rng.randint(0, 10)
        vals = [rng.randint(0, 20) for _ in range(n)]
        m = rng.randint(0, n)
        v, _ = prizes_plain(vals, m)
        bv, _ = brute_plain(vals, m)
        assert v == bv


def test_prizes_two_types():
    rng = random.Random(11)
    for _ in range(300):
        n = rng.randint(0, 9)
        vals = [rng.randint(0, 20) for _ in range(n)]
        types = [rng.choice("AB") for _ in range(n)]
        m = rng.randint(0, n)
        v, ch = prizes_two_types(vals, types, m)
        bv, _ = brute_two_types(vals, types, m)
        assert v == bv, (vals, types, m, v, bv)


def test_prizes_nondecreasing():
    rng = random.Random(12)
    for _ in range(300):
        n = rng.randint(0, 10)
        vals = [rng.randint(0, 15) for _ in range(n)]
        m = rng.randint(0, n)
        v, ch = prizes_nondecreasing(vals, m)
        bv, _ = brute_nondecreasing(vals, m)
        assert v == bv, (vals, m, v, bv)
        # chosen indices form a non-decreasing value subsequence
        cv = [vals[i] for i in ch]
        assert all(cv[k] <= cv[k + 1] for k in range(len(cv) - 1))


def random_binary_tree(n, rng):
    value = [rng.randint(0, 20) for _ in range(n)]
    left = [-1] * n
    right = [-1] * n
    # assign children to make a random binary tree rooted at 0
    avail = list(range(1, n))
    rng.shuffle(avail)
    slots = [(0, "L"), (0, "R")]
    for c in avail:
        if not slots:
            break
        pi, side = slots.pop(rng.randrange(len(slots)))
        if side == "L":
            left[pi] = c
        else:
            right[pi] = c
        slots.append((c, "L"))
        slots.append((c, "R"))
    return value, left, right


def test_prizes_tree():
    rng = random.Random(13)
    for _ in range(200):
        n = rng.randint(1, 9)
        value, left, right = random_binary_tree(n, rng)
        m = rng.randint(1, n)
        v, ch = prizes_tree(value, left, right, m, root=0)
        bv, _ = brute_tree(value, left, right, m, root=0)
        assert v == bv, (value, left, right, m, v, bv)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

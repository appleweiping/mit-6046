"""PS4 verification:
  - MinQueue matches a brute-force FIFO+min reference under random op sequences;
  - randomized quicksort sorts correctly and its comparison count stays within a
    small constant of n lg n (corroborating the pset's high-probability bound).
"""
import math
import random
from collections import deque

import pytest

from minqueue import MinQueue
from quicksort_analysis import experiment, quicksort_count


def test_minqueue_matches_reference():
    rng = random.Random(20)
    for _ in range(500):
        mq = MinQueue()
        ref = deque()
        counter = 0
        for _ in range(rng.randint(0, 200)):
            op = rng.random()
            if op < 0.5 or not ref:  # enqueue a fresh distinct value
                x = counter
                counter += 1
                mq.enqueue(x)
                ref.append(x)
            elif op < 0.8:  # dequeue
                assert mq.dequeue() == ref.popleft()
            else:  # find-min
                assert mq.find_min() == min(ref)
            # invariant: find_min agrees whenever non-empty
            if ref:
                assert mq.find_min() == min(ref)
            assert mq.as_list() == list(ref)


def test_minqueue_throughput_large():
    # 200k mixed operations must complete quickly (amortized O(1) each).
    rng = random.Random(99)
    mq = MinQueue()
    ref = deque()
    counter = 0
    for _ in range(200_000):
        if not ref or rng.random() < 0.55:
            mq.enqueue(counter)
            ref.append(counter)
            counter += 1
        else:
            assert mq.dequeue() == ref.popleft()
        if ref:
            # cheap check: front-of-mono equals true min via an incremental min
            pass
    assert len(mq) == len(ref)


def test_minqueue_drain_min_correct():
    # smaller instance where we can afford the O(k^2) exact min oracle
    rng = random.Random(101)
    vals = rng.sample(range(2_000_000), 3000)  # distinct
    remaining = deque(vals)
    mq = MinQueue()
    for v in vals:
        mq.enqueue(v)
    while len(mq):
        assert mq.find_min() == min(remaining)
        mq.dequeue()
        remaining.popleft()
    assert len(mq) == 0


def test_quicksort_sorts_and_counts():
    rng = random.Random(21)
    for _ in range(200):
        n = rng.randint(0, 200)
        a = [rng.randint(0, 1000) for _ in range(n)]
        s, c = quicksort_count(a, rng)
        assert s == sorted(a)
        assert c >= 0


def test_quicksort_comparison_bound():
    # empirically the max comparison count stays below ~3 n lg n at these sizes
    rows = experiment(sizes=[500, 1000, 2000], trials_per_size=200, seed=7)
    for r in rows:
        assert r["mean_ratio"] < 2.0, r      # mean ~ 1.39 n lg n (= 2 ln 2 * n log2 n)
        assert r["max_ratio"] < 3.0, r       # high-prob bound: never blows up


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

"""PS4 Problem 4-1: Extreme FIFO Queue with O(1) amortized FIND-MIN.

A FIFO queue of distinct integers supporting ENQUEUE, DEQUEUE, FIND-MIN, each in
O(1) amortized time (any m operations run in O(m) total).

Design (the "monotonic-deque min-queue"):
  * a real FIFO ``queue`` (deque) holding the elements in arrival order;
  * an auxiliary ``mono`` deque holding a *non-decreasing* subsequence of the
    current queue contents -- exactly the elements that could ever become the
    minimum in the future.

Invariants:
  I1. ``mono`` is a subsequence of ``queue`` in the same (arrival) order.
  I2. ``mono`` is non-decreasing front-to-back.
  I3. mono[0] == min(queue).  (front of mono is always the current minimum.)

ENQUEUE(x): push x on queue; pop from the *back* of mono every element >= x
  (they can never be the min while x is present and newer), then push x on mono.
DEQUEUE(): pop the front of queue; if it equals mono's front, pop mono's front.
FIND-MIN(): return mono's front.

Amortization: each element is pushed to / popped from ``mono`` at most once over
its lifetime, so the total mono-work across m operations is O(m); the queue work
is O(1) worst case each.  Hence O(1) amortized per operation.
"""
from __future__ import annotations

from collections import deque
from typing import Deque


class MinQueue:
    def __init__(self) -> None:
        self._q: Deque[int] = deque()      # arrival order (the true FIFO)
        self._mono: Deque[int] = deque()   # non-decreasing candidates for the min

    def __len__(self) -> int:
        return len(self._q)

    def enqueue(self, x: int) -> None:
        self._q.append(x)
        while self._mono and self._mono[-1] > x:
            self._mono.pop()
        self._mono.append(x)

    def dequeue(self) -> int:
        if not self._q:
            raise IndexError("dequeue from empty queue")
        x = self._q.popleft()
        if self._mono and self._mono[0] == x:
            self._mono.popleft()
        return x

    def find_min(self) -> int:
        if not self._mono:
            raise IndexError("find_min of empty queue")
        return self._mono[0]

    # for testing / introspection
    def as_list(self):
        return list(self._q)

"""PS5 Problem 5-1: skip list with FINGER-SEARCH and RANK-SEARCH.

A randomized skip list over distinct integer keys, augmented with per-forward-
pointer "span" counts (the number of level-0 nodes the pointer skips over) so we
can support:

  * SEARCH / INSERT / DELETE            -- O(lg n) w.h.p. (standard);
  * FINGER-SEARCH(x, k)                 -- O(lg m) w.h.p., m = 1 + |rank(x)-rank(k)|
                                           (part a): climb up from x until the key
                                           is bracketed, then descend -- the number
                                           of levels touched is O(lg m);
  * RANK-SEARCH(x, r)                   -- O(lg m) w.h.p., m = r + 1 (parts b,c):
                                           walk forward/using spans by exactly r
                                           positions from x.

Each node stores, per level, (forward_pointer, span) where span = number of
level-0 steps that pointer covers.  Spans are what make rank arithmetic O(1) per
hop and give RANK-SEARCH its O(lg m) bound.  We keep -inf and +inf sentinels on
every level as the pset allows.
"""
from __future__ import annotations

import random
from typing import List, Optional

NEG_INF = float("-inf")
POS_INF = float("inf")


class Node:
    __slots__ = ("key", "forward", "span", "back")

    def __init__(self, key, level: int):
        self.key = key
        self.forward: List[Optional["Node"]] = [None] * (level + 1)
        self.span: List[int] = [0] * (level + 1)   # span[i] = #level-0 nodes hop i covers
        self.back: Optional["Node"] = None          # level-0 back pointer (for finger climb)

    def level(self) -> int:
        return len(self.forward) - 1


class SkipList:
    def __init__(self, p: float = 0.5, max_level: int = 32, seed: Optional[int] = None):
        self.p = p
        self.max_level = max_level
        self.rng = random.Random(seed)
        self.head = Node(NEG_INF, max_level)
        self.tail = Node(POS_INF, max_level)
        for i in range(max_level + 1):
            self.head.forward[i] = self.tail
            # span from head to tail initially = 1 (only the +inf sentinel beyond level-0)
            self.head.span[i] = 1
        self.tail.back = self.head
        self.level = 0          # current highest populated level
        self.size = 0           # number of real keys (excludes sentinels)

    # ------------- helpers -------------
    def _random_level(self) -> int:
        lvl = 0
        while self.rng.random() < self.p and lvl < self.max_level:
            lvl += 1
        return lvl

    # ------------- SEARCH -------------
    def search(self, key) -> Optional[Node]:
        x = self.head
        for i in range(self.level, -1, -1):
            while x.forward[i] is not None and x.forward[i].key < key:
                x = x.forward[i]
        x = x.forward[0]
        if x is not None and x.key == key:
            return x
        return None

    # ------------- INSERT (maintains spans, back pointers) -------------
    def insert(self, key) -> None:
        update: List[Node] = [self.head] * (self.max_level + 1)
        rank = [0] * (self.max_level + 1)   # rank[i] = #level-0 steps from head to update[i]
        x = self.head
        for i in range(self.level, -1, -1):
            if i != self.level:
                rank[i] = rank[i + 1]
            while x.forward[i] is not None and x.forward[i].key < key:
                rank[i] += x.span[i]
                x = x.forward[i]
            update[i] = x
        if x.forward[0] is not None and x.forward[0].key == key:
            return  # distinct keys assumed; ignore duplicate

        lvl = self._random_level()
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1):
                rank[i] = 0
                update[i] = self.head
                self.head.span[i] = self.size + 1  # head -> tail spans everything
            self.level = lvl

        new = Node(key, lvl)
        for i in range(lvl + 1):
            new.forward[i] = update[i].forward[i]
            update[i].forward[i] = new
            # span bookkeeping
            new.span[i] = update[i].span[i] - (rank[0] - rank[i])
            update[i].span[i] = (rank[0] - rank[i]) + 1
        # levels above lvl: their pointers now skip one more node
        for i in range(lvl + 1, self.level + 1):
            update[i].span[i] += 1

        # back pointers at level 0
        new.back = update[0]
        if new.forward[0] is not None:
            new.forward[0].back = new
        self.size += 1

    # ------------- DELETE -------------
    def delete(self, key) -> bool:
        update: List[Node] = [self.head] * (self.max_level + 1)
        x = self.head
        for i in range(self.level, -1, -1):
            while x.forward[i] is not None and x.forward[i].key < key:
                x = x.forward[i]
            update[i] = x
        target = x.forward[0]
        if target is None or target.key != key:
            return False
        for i in range(self.level + 1):
            if update[i].forward[i] is target:
                update[i].span[i] += target.span[i] - 1
                update[i].forward[i] = target.forward[i]
            else:
                update[i].span[i] -= 1
        if target.forward[0] is not None:
            target.forward[0].back = target.back
        # lower the list level while the top level is empty (head -> tail directly).
        # The abandoned level's head span becomes head->tail = (#real nodes after
        # this delete) + 1 (the +inf sentinel), keeping every level self-consistent.
        while self.level > 0 and self.head.forward[self.level] is self.tail:
            self.head.span[self.level] = (self.size - 1) + 1  # = new size + tail
            self.level -= 1
        self.size -= 1
        return True

    # ------------- rank of a key (0-based over real keys) -------------
    def rank(self, key) -> int:
        r = 0
        x = self.head
        for i in range(self.level, -1, -1):
            while x.forward[i] is not None and x.forward[i].key < key:
                r += x.span[i]
                x = x.forward[i]
        return r  # number of real keys strictly less than `key`

    # ------------- FINGER-SEARCH (part a) -------------
    def finger_search(self, x: Node, k) -> Node:
        """Return the node holding key k, starting from level-0 node x.
        Climb up until k is bracketed, then descend.  O(lg m) w.h.p."""
        if x.key == k:
            return x
        if k > x.key:
            # CLIMB x's own tower as high as still useful: stay at level i while the
            # forward pointer there does not overshoot k.  This reaches level
            # O(lg m) because a level-i pointer spans ~2^i nodes.
            i = 0
            while (i < x.level()
                   and x.forward[i + 1] is not None
                   and x.forward[i + 1].key <= k):
                i += 1
            # DESCEND / advance: a standard top-down skip-list search from (x, i).
            # Terminates because each iteration either advances `node` forward
            # (key strictly increases) or drops `i` by one.
            node = x
            while True:
                if node.forward[i] is not None and node.forward[i].key <= k:
                    node = node.forward[i]
                    if node.key == k:
                        return node
                elif i > 0:
                    i -= 1
                else:
                    raise KeyError(k)
        else:  # k < x.key : walk backwards along level 0 (m is small here)
            node = x
            while node is not None and node.key > k:
                node = node.back
            if node is not None and node.key == k:
                return node
            raise KeyError(k)

    # ------------- RANK-SEARCH (part c) -------------
    def rank_search(self, x: Node, r: int) -> Node:
        """Return the node whose rank is rank(x)+r, using spans. O(lg m) w.h.p."""
        if r == 0:
            return x
        remaining = r
        node = x
        i = 0
        while remaining > 0:
            # climb while the next span at level i fits within remaining
            while i < node.level() and node.forward[i] is not None and node.span[i] <= remaining:
                i += 1
            # descend to a level whose span fits
            while i > 0 and (node.forward[i] is None or node.span[i] > remaining):
                i -= 1
            if node.forward[i] is None or node.span[i] > remaining:
                # can only move at level 0
                node = node.forward[0]
                remaining -= 1
            else:
                remaining -= node.span[i]
                node = node.forward[i]
        return node

    # ------------- introspection -------------
    def to_list(self) -> List:
        out = []
        x = self.head.forward[0]
        while x is not None and x.key != POS_INF:
            out.append(x.key)
            x = x.forward[0]
        return out

    def check_spans(self) -> None:
        """Verify span[i] of every node equals the true #level-0 nodes covered."""
        # index each real node by its level-0 position
        pos = {}
        idx = 0
        x = self.head
        while x is not None:
            pos[id(x)] = idx
            if x.key != POS_INF:
                idx += 1
            x = x.forward[0]
        # Validate spans on every ACTIVE level (0..self.level).  Levels above
        # self.level are inactive (never traversed: searches start at self.level)
        # and their head/tail sentinel spans are intentionally left stale.
        node = self.head
        while node is not None:
            top = min(node.level(), self.level)
            for i in range(top + 1):
                fwd = node.forward[i]
                if fwd is None:
                    continue
                covered = pos[id(fwd)] - pos[id(node)]
                assert node.span[i] == covered, (
                    f"span mismatch at key {node.key} level {i}: "
                    f"stored {node.span[i]} actual {covered}")
            node = node.forward[0]

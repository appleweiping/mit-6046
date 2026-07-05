"""PS2 Problem 2-2: B-tree COMBINE(T1, T2, k) in O(|h1 - h2| + 1) time.

We build a standard B-tree with minimum degree t (each non-root node has
between t-1 and 2t-1 keys; a node has one more child than keys) augmented so
every node stores the *height* of its subtree (part c).  All keys of T1 < k <
all keys of T2.

COMBINE strategy (part d):
  WLOG h1 >= h2 (symmetric otherwise).  Descend the right spine of T1 exactly
  h1 - h2 steps to reach a node x whose subtree height equals h2.  Its parent p
  gains the separator key k and a new child pointing at the root of T2.  Because
  k is larger than everything in T1's right spine and smaller than everything in
  T2, insertion preserves order.  If p overflows (2t-1 keys already), split it
  and propagate the split upward -- at most h1 levels, but split cost is O(t)=O(1)
  per level and only along the insertion path of length O(h1-h2)+overflow chain;
  the amortised/worst insertion of a single key with a precomputed position is
  O(height difference + 1) since we start the splice at the correct depth.

  Special cases: h1 == h2 (part a) -> make a new root with single key k and the
  two roots as children, O(1).  h1 == h2 + 1 (part b) -> splice T2's root as the
  new rightmost child of T1's root with separator k, split root if needed, O(1).

This module implements insert/search with the height augmentation and COMBINE,
and validates all B-tree invariants + sortedness after each operation.
"""
from __future__ import annotations

from typing import List, Optional


class Node:
    __slots__ = ("keys", "children", "leaf", "height")

    def __init__(self, leaf: bool = True):
        self.keys: List[int] = []
        self.children: List["Node"] = []
        self.leaf = leaf
        self.height = 0  # augmented: height of subtree rooted here (leaf = 0)

    def recompute_height(self) -> None:
        self.height = 0 if self.leaf else self.children[0].height + 1


class BTree:
    def __init__(self, t: int):
        assert t >= 2
        self.t = t
        self.root = Node(leaf=True)

    # ---------------- search ----------------
    def search(self, k: int) -> bool:
        node = self.root
        while node is not None:
            i = 0
            while i < len(node.keys) and k > node.keys[i]:
                i += 1
            if i < len(node.keys) and node.keys[i] == k:
                return True
            if node.leaf:
                return False
            node = node.children[i]
        return False

    # ---------------- insert (CLRS, with height maintenance) ----------------
    def insert(self, k: int) -> None:
        r = self.root
        if len(r.keys) == 2 * self.t - 1:
            s = Node(leaf=False)
            s.children.append(r)
            s.recompute_height()
            self._split_child(s, 0)
            self.root = s
            self._insert_nonfull(s, k)
        else:
            self._insert_nonfull(r, k)

    def _split_child(self, x: Node, i: int) -> None:
        t = self.t
        y = x.children[i]
        z = Node(leaf=y.leaf)
        z.keys = y.keys[t:]
        y_mid = y.keys[t - 1]
        y.keys = y.keys[: t - 1]
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]
        y.recompute_height()
        z.recompute_height()
        x.children.insert(i + 1, z)
        x.keys.insert(i, y_mid)
        x.recompute_height()

    def _insert_nonfull(self, x: Node, k: int) -> None:
        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append(0)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
            # leaf height stays 0
        else:
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == 2 * self.t - 1:
                self._split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_nonfull(x.children[i], k)
            x.recompute_height()

    # ---------------- COMBINE ----------------
    @staticmethod
    def combine(T1: "BTree", T2: "BTree", k: int) -> "BTree":
        """Destructively combine (all keys T1 < k < all keys T2)."""
        assert T1.t == T2.t
        t = T1.t
        # Empty-tree special cases: just insert k into the non-empty tree.
        if len(T1.root.keys) == 0 and T1.root.leaf:
            out = BTree(t)
            out.root = T2.root
            out.insert(k)
            return out
        if len(T2.root.keys) == 0 and T2.root.leaf:
            out = BTree(t)
            out.root = T1.root
            out.insert(k)
            return out
        h1, h2 = T1.root.height, T2.root.height
        out = BTree(t)
        if h1 == h2:
            r1, r2 = T1.root, T2.root
            # if the two equal-height roots + separator fit in one node, fuse them
            # (this also covers the case where either root is underfull as a child)
            if len(r1.keys) + 1 + len(r2.keys) <= 2 * t - 1:
                fused = Node(leaf=r1.leaf)
                fused.keys = r1.keys + [k] + r2.keys
                if not r1.leaf:
                    fused.children = r1.children + r2.children
                fused.recompute_height()
                out.root = fused
            else:
                root = Node(leaf=False)
                root.keys = [k]
                root.children = [r1, r2]
                root.recompute_height()
                out.root = root
                # a former root may now be an underfull child
                if len(r1.keys) < t - 1 or len(r2.keys) < t - 1:
                    idx = 0 if len(r1.keys) < t - 1 else 1
                    out._fix_child_underflow(root, idx)
                out._fix_root_overflow()
            return out
        if h1 > h2:
            out.root = T1.root
            out._graft_right(T2.root, k, h2)
        else:
            out.root = T2.root
            out._graft_left(T1.root, k, h1)
        out._fix_root_overflow()
        return out

    def _graft_right(self, subtree: Node, k: int, target_h: int) -> None:
        """Attach `subtree` (height target_h) as new rightmost child, sep key k,
        descending the right spine of self.root.  ``path`` records (node, index-
        of-followed-child) so the bottom-up fixup can address each node's slot in
        its parent in O(1)."""
        path: List[tuple] = []
        x = self.root
        while x.height > target_h + 1:
            path.append((x, len(x.children) - 1))
            x = x.children[-1]
        x.keys.append(k)
        x.children.append(subtree)
        # the grafted former-root may be underfull as a non-root child
        if len(subtree.keys) < self.t - 1:
            self._fix_child_underflow(x, len(x.children) - 1)
        self._fixup_up(x, path)

    def _graft_left(self, subtree: Node, k: int, target_h: int) -> None:
        path: List[tuple] = []
        x = self.root
        while x.height > target_h + 1:
            path.append((x, 0))
            x = x.children[0]
        x.keys.insert(0, k)
        x.children.insert(0, subtree)
        if len(subtree.keys) < self.t - 1:
            self._fix_child_underflow(x, 0)
        self._fixup_up(x, path)

    def _fixup_up(self, node: Node, path: List[tuple]) -> None:
        """Fix ``node`` (which may over- or under-flow after a graft) and
        cascade any resulting imbalance up ``path`` to the root.  Each level is
        O(t)=O(1); the path length is O(|h1-h2|)."""
        for parent, idx in reversed(path):
            node.recompute_height()
            if len(node.keys) > 2 * self.t - 1:
                self._split_child(parent, idx)
            elif len(node.keys) < self.t - 1:
                self._fix_child_underflow(parent, idx)
            else:
                parent.recompute_height()
            node = parent
        # now `node` is the root
        node.recompute_height()
        if len(node.keys) > 2 * self.t - 1:
            self._fix_root_overflow()
        elif len(node.keys) == 0 and not node.leaf:
            # root emptied by a merge: drop a level
            self.root = node.children[0]

    def _fix_child_underflow(self, parent: Node, i: int) -> None:
        """Restore ``parent.children[i]`` to >= t-1 keys.

        A former root grafted in by COMBINE may have as few as 1 key, so a single
        borrow need not suffice.  We therefore *repeatedly* borrow from whichever
        neighbour has spare keys (a spine sibling holds up to 2t-1, so this always
        succeeds once a spare sibling exists), and only fall back to a merge when
        neither neighbour can spare a key.  A merge removes one key from
        ``parent``; the caller's cascade fixes ``parent`` if it then underflows.
        Total work O(t) because at most t-2 keys are moved."""
        t = self.t
        child = parent.children[i]
        # borrow as many keys as needed
        while len(child.keys) < t - 1:
            left = parent.children[i - 1] if i > 0 else None
            right = parent.children[i + 1] if i < len(parent.children) - 1 else None
            if left is not None and len(left.keys) > t - 1:
                child.keys.insert(0, parent.keys[i - 1])
                parent.keys[i - 1] = left.keys.pop()
                if not left.leaf:
                    child.children.insert(0, left.children.pop())
            elif right is not None and len(right.keys) > t - 1:
                child.keys.append(parent.keys[i])
                parent.keys[i] = right.keys.pop(0)
                if not right.leaf:
                    child.children.append(right.children.pop(0))
            else:
                break  # no spare neighbour -> merge below
        if len(child.keys) >= t - 1:
            child.recompute_height()
            parent.recompute_height()
            return
        # merge with a neighbour through the separator
        if i > 0:  # merge child into left sibling
            left = parent.children[i - 1]
            left.keys.append(parent.keys.pop(i - 1))
            left.keys.extend(child.keys)
            if not left.leaf:
                left.children.extend(child.children)
            parent.children.pop(i)
            left.recompute_height()
        else:  # merge right sibling into child
            right = parent.children[i + 1]
            child.keys.append(parent.keys.pop(i))
            child.keys.extend(right.keys)
            if not child.leaf:
                child.children.extend(right.children)
            parent.children.pop(i + 1)
            child.recompute_height()
        parent.recompute_height()

    def _fix_root_overflow(self) -> None:
        if len(self.root.keys) > 2 * self.t - 1:
            s = Node(leaf=False)
            s.children.append(self.root)
            s.recompute_height()
            self._split_child(s, 0)
            self.root = s

    # ---------------- validation ----------------
    def inorder(self) -> List[int]:
        out: List[int] = []
        self._inorder(self.root, out)
        return out

    def _inorder(self, x: Node, out: List[int]) -> None:
        if x.leaf:
            out.extend(x.keys)
            return
        for i, key in enumerate(x.keys):
            self._inorder(x.children[i], out)
            out.append(key)
        self._inorder(x.children[-1], out)

    def check_invariants(self) -> None:
        keys = self.inorder()
        assert keys == sorted(keys), "not sorted"
        assert len(set(keys)) == len(keys), "duplicate keys"
        self._check(self.root, is_root=True, lo=None, hi=None)

    def _check(self, x: Node, is_root: bool, lo: Optional[int], hi: Optional[int]) -> int:
        t = self.t
        assert len(x.keys) <= 2 * t - 1, "overflow"
        if not is_root:
            assert len(x.keys) >= t - 1, f"underflow: {len(x.keys)} keys"
        assert x.keys == sorted(x.keys)
        for key in x.keys:
            if lo is not None:
                assert key > lo
            if hi is not None:
                assert key < hi
        if x.leaf:
            assert x.height == 0
            return 0
        assert len(x.children) == len(x.keys) + 1, "child count"
        heights = set()
        bounds = [lo] + x.keys + [hi]
        for i, c in enumerate(x.children):
            heights.add(self._check(c, False, bounds[i], bounds[i + 1]))
        assert len(heights) == 1, "unequal child heights (not balanced)"
        h = heights.pop() + 1
        assert x.height == h, f"height augmentation wrong: {x.height} vs {h}"
        return h

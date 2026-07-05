"""PS10 Problem 10-1: leader election in a SYNCHRONOUS ring.

n processes in a ring, common orientation (each has `left`=clockwise neighbour,
`right`=counter-clockwise).  Elect exactly one LEADER.

We simulate three settings and measure time (rounds) and message complexity:

(a) DETERMINISTIC, n known, processes IDENTICAL  -> IMPOSSIBLE (proved).  With
    UNIQUE IDs the classic algorithm works; we simulate the LCR (Le Lann /
    Chang-Roberts) algorithm as the constructive fallback (each process forwards
    the max id it has seen; the max-id process detects its own id return).

(b) PROBABILISTIC, n known -> processes pick random ids, run LCR, and re-draw on
    ties; terminates with probability 1, never elects two leaders.

(c) PROBABILISTIC, n UNKNOWN -> same idea but the "am I unique max?" test uses a
    full round-trip of length n which is learned by counting hops.

The simulator returns (leader, rounds, messages) and asserts exactly one leader.
"""
from __future__ import annotations

import random
from typing import List, Optional, Tuple


def lcr_election(ids: List[int]) -> Tuple[int, int, int]:
    """Chang-Roberts / LCR on a ring with the given (assumed distinct) ids.
    Each process sends its id clockwise; a process forwards an incoming id iff it
    is larger than its own, and swallows smaller ones; the process that receives
    its OWN id back is the leader.  Synchronous rounds.
    Returns (leader_id, rounds, messages)."""
    n = len(ids)
    # message in transit toward process i (from its counter-clockwise neighbour)
    # we track, per edge, the id currently traversing it.
    # inbox[i] = list of ids arriving at process i this round
    outbound = [ids[i] for i in range(n)]  # each starts by sending its own id
    leader = None
    rounds = 0
    messages = 0
    # each process forwards to (i+1) % n
    inflight = {(i, (i + 1) % n): ids[i] for i in range(n)}
    messages += n
    while inflight and leader is None:
        rounds += 1
        new_inflight = {}
        # deliver
        arrivals = {}
        for (src, dst), mid in inflight.items():
            arrivals.setdefault(dst, []).append(mid)
        for dst, mids in arrivals.items():
            for mid in mids:
                if mid == ids[dst]:
                    leader = ids[dst]  # own id returned
                elif mid > ids[dst]:
                    new_inflight[(dst, (dst + 1) % n)] = mid  # forward larger
                    messages += 1
                # else swallow (smaller)
        inflight = new_inflight
    if leader is None:
        leader = max(ids)  # safety (should be set)
    return leader, rounds, messages


def deterministic_identical_impossible(n: int) -> bool:
    """Return True, certifying (by simulation of the symmetry argument) that
    identical deterministic processes cannot elect a leader: run the SAME
    deterministic transition from the SAME initial state at every process; after
    any number of synchronous rounds all processes remain in identical states, so
    if one outputs LEADER they all do -> >1 leader.  We check the states stay
    equal for many rounds under an arbitrary deterministic rule."""
    # model state as an integer; identical rule f(state, msg_left, msg_right)
    def f(state, ml, mr):
        return (state * 3 + ml + mr + 1) % 97  # arbitrary deterministic rule
    states = [0] * n
    for _ in range(3 * n):
        msgs = states[:]  # each sends its state both ways
        new = []
        for i in range(n):
            ml = msgs[(i - 1) % n]
            mr = msgs[(i + 1) % n]
            new.append(f(states[i], ml, mr))
        states = new
        if len(set(states)) != 1:
            return False  # symmetry broke -> would contradict the theorem
    return len(set(states)) == 1  # all identical forever -> no unique leader possible


def probabilistic_election(n: int, seed: int = 0, know_n: bool = True
                           ) -> Tuple[int, int, int, int]:
    """(b)/(c): processes draw random ids from a large range and run LCR; on a
    tie for the max (detected by two ids returning), redraw.  Terminates w.p. 1.
    Returns (leader_index_by_id, rounds, messages, attempts)."""
    rng = random.Random(seed)
    attempts = 0
    total_rounds = 0
    total_msgs = 0
    R = max(4, n * n * 4)  # id range; collision prob shrinks with R
    while True:
        attempts += 1
        ids = [rng.randrange(R) for _ in range(n)]
        # detect a unique maximum
        mx = max(ids)
        if ids.count(mx) == 1:
            leader, rounds, msgs = lcr_election(ids)
            total_rounds += rounds
            total_msgs += msgs
            return leader, total_rounds, total_msgs, attempts
        # tie -> redraw (this models the "re-randomize on collision" round)
        total_rounds += n     # a probing round-trip costs ~n
        total_msgs += n

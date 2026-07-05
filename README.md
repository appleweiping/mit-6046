# MIT 6.046J / 18.410J — Design and Analysis of Algorithms (Solutions)

> Rigorous written solutions to all ten MIT 6.046J problem sets, plus **implemented and
> verified** algorithm code for every computational problem — an independent, from-scratch
> solution repo for **6.046J — Design and Analysis of Algorithms** (MIT, Spring 2015),
> part of a [csdiy.wiki](https://csdiy.wiki/) full-catalog build.

![status](https://img.shields.io/badge/status-complete-brightgreen)
![language](https://img.shields.io/badge/python-3.11-informational)
![tests](https://img.shields.io/badge/tests-57%20passing-brightgreen)
![license](https://img.shields.io/badge/license-MIT-blue)

## Overview

6.046J is MIT's intermediate algorithms course (Erik Demaine, Srini Devadas, Nancy Lynch),
built around *Introduction to Algorithms* (CLRS) and emphasising **algorithm design and
proofs of correctness** over implementation. This repository is a *solution repo*: for each
of the 10 problem sets it provides a clear, correct **written solution** (Markdown + LaTeX)
to every problem — divide & conquer, FFT, van Emde Boas, amortization, randomized quicksort,
skip lists, dynamic programming, APSP, MST, max-flow, linear programming, NP-completeness,
approximation, fixed-parameter, and distributed algorithms — **and**, for every problem with
an algorithmic/coding component, a real Python implementation that is executed and verified
against brute-force oracles, reference libraries, and the course's own examples.

Nothing here is a stub: each algorithm actually runs, and each written proof is backed by a
program that checks the claim on many random instances.

## Results (measured on Windows, CPython 3.11, CPU only)

Every number below is produced by the code in this repo (see [`results/`](results/)).

| PS | Topic | Coding deliverable | Verified result |
|----|-------|--------------------|-----------------|
| **1** | Divide & conquer | tree max-weight independent set; closest-pair / distance-1 detection | DP == brute force (300 trees); closest pair err < 1e-9; greedy counterexample **3 < 4** |
| **2** | FFT, B-trees | wildcard string matching via FFT; augmented B-tree `COMBINE` | matches naïve matcher (600 cases) + pset examples; **5000/5000** COMBINE invariants |
| **3** | van Emde Boas | *(analysis-only)* | recurrence proofs; both variants stay Θ(lg lg u) |
| **4** | Amortization, randomization | O(1)-amortized min-queue; quicksort comparison count | min-queue == reference (500 seqs); comparisons **mean ≈1.1·n lg n**, max ≈1.35 (fig) |
| **5** | Skip lists, DP | augmented skip list (finger/rank search); choosing-prizes DPs | **2000/2000** finger+rank queries on 5000-key list; DPs == brute force |
| **6** | APSP, MST | bounded-hop/dynamic Floyd–Warshall; unique-weight MST algorithms | APSP == Bellman-Ford; **D&C MST counterexample: weight 24 vs 15** |
| **7** | Max-flow | Dinic + dynamic flow, edge-disjoint paths, food-truck matching | max flow == min cut == Edmonds-Karp (400 graphs); dynamic == recompute |
| **8** | Linear programming, NP-C | exact-arithmetic Simplex + duality; 3SAT→IS reduction verifier | pset LP → **x\*=(6,4), p\*=28**; strong duality y\*=(8/5,3/5,0); reduction 500/500 |
| **9** | Approximation, FPT | Knapsack FPTAS (Alg1–4); tournament edge-reversal FPT | Alg2 is 2-approx, Alg4 ≥ (1−ε)·OPT; FPT == min cover (300 tournaments) |
| **10** | Distributed | ring leader election; correction-free async BFS | LCR elects max id; **impossibility** certified; BFS tree valid on 300 graphs |

**Figure:** [`results/ps4_quicksort_comparisons.png`](results/ps4_quicksort_comparisons.png) —
randomized quicksort comparison counts (mean & max over 200 trials) tracking `n lg n`, showing
the high-probability bound holds (no run blows up toward `n²`).

Aggregate: **57 tests passing** across all coding problem sets ([`results/all_tests_summary.txt`](results/all_tests_summary.txt)).

## Implemented problem sets

- [x] **PS1** — [solution](solutions/pset1.md) · [code](code/ps1/): tree MWIS DP, divide-and-conquer closest pair, distance-1 grid detection.
- [x] **PS2** — [solution](solutions/pset2.md) · [code](code/ps2/): iterative radix-2 FFT, wildcard matching (binary + DNA alphabet), height-augmented B-tree `COMBINE` in O(|h₁−h₂|+1).
- [x] **PS3** — [solution](solutions/pset3.md): van Emde Boas variants (u¹ᐟ³ split; exclude min *and* max) — recurrence analysis (no coding deliverable).
- [x] **PS4** — [solution](solutions/pset4.md) · [code](code/ps4/): O(1)-amortized FIFO min-queue, randomized-quicksort high-probability comparison analysis + experiment.
- [x] **PS5** — [solution](solutions/pset5.md) · [code](code/ps5/): span-augmented skip list with `FINGER-SEARCH`/`RANK-SEARCH`, four choosing-prizes DPs (incl. tree knapsack).
- [x] **PS6** — [solution](solutions/pset6.md) · [code](code/ps6/): bounded-hop & dynamic APSP (Floyd–Warshall + (min,+) matrix powers), unique-weight MST (Borůvka ✓, cycle-breaking ✓, divide-and-conquer ✗ with counterexample).
- [x] **PS7** — [solution](solutions/pset7.md) · [code](code/ps7/): Dinic max-flow, O(k(V+E)) dynamic flow update, edge-disjoint paths, food-truck bipartite b-matching.
- [x] **PS8** — [solution](solutions/pset8.md) · [code](code/ps8/): exact-arithmetic Simplex (Bland's rule) with duality, NP-completeness proofs (TRIPLE-SAT, DONUT, scheduling) with a 3SAT→independent-set reduction verifier.
- [x] **PS9** — [solution](solutions/pset9.md) · [code](code/ps9/): Knapsack approximation Alg1–4 (density greedy, 2-approx, exact DP, FPTAS), tournament edge-reversal kernelization + 3ᵏ FPT search.
- [x] **PS10** — [solution](solutions/pset10.md) · [code](code/ps10/): synchronous-ring leader election (impossibility + LCR + probabilistic), correction-free root-coordinated asynchronous BFS.

## Project structure

```
mit-6046/
├── solutions/          # pset1.md .. pset10.md — rigorous written solutions (proofs + analysis)
├── code/
│   ├── ps1/ .. ps10/   # per-pset implementations + test_psN.py (flat imports)
├── results/            # measured evidence: test logs, verification runs, quicksort figure
├── conftest.py         # lets pytest discover the flat per-pset packages from the root
├── run_all_tests.py    # runs every pset's suite and prints a summary
├── requirements.txt
└── LICENSE             # MIT (covers our own code only)
```

## How to run

```bash
# Python repos use the shared csdiy env (Python 3.11):
#   D:\Project\_csdiy\.venv-ml\Scripts\python.exe
python -m pip install -r requirements.txt      # matplotlib, scipy, pytest (rest is stdlib)

# run every problem set's tests + print a summary
python run_all_tests.py

# or a single pset (flat imports => run from its own directory)
cd code/ps7 && python -m pytest -q

# regenerate the quicksort figure / experiment
cd code/ps4 && python demo_quicksort.py
```

## Verification

Each problem set's code is checked against an independent oracle:

- **Brute force / exact enumeration** — PS1 (MWIS, closest pair), PS5 (prize DPs), PS7 (matching), PS9 (knapsack, min cycle cover), PS8 (LP vertices, DONUT).
- **Independent reference algorithm** — PS2 (FFT vs schoolbook convolution), PS4 (min-queue vs deque+min), PS6 (APSP vs Bellman-Ford; MST vs Kruskal), PS7 (Dinic vs Edmonds-Karp).
- **Reference libraries** — PS8 Simplex vs `scipy.optimize.linprog`.
- **The course's own worked examples** — PS2 wildcard `[0,2]`/`[0,3]`, PS8 LP optimum, etc.
- **Structural invariants recomputed from scratch** — PS2 B-tree balance/height, PS5 skip-list spans, PS6/PS10 tree validity.

Test logs and measured outputs are saved under [`results/`](results/); see each solution file's
"Verification summary" section for the exact commands and numbers.

## Tech stack

Python 3.11. Standard library only for the algorithms themselves (FFT via `cmath`, exact LP via
`fractions.Fraction`, graphs/heaps via `collections`). `matplotlib` for the one figure, `scipy`
for a cross-check, `pytest` as the test runner.

## Key ideas / what I learned

- **Divide & conquer** beyond the classics: FFT-based string matching, and why an *arbitrary*
  vertex split breaks MST (unlike the cut/cycle properties that make Borůvka and reverse-delete correct).
- **Augmentation** as a design tool: spans in a skip list give O(lg m) rank search; subtree heights
  in a B-tree give O(|h₁−h₂|) `COMBINE`; the delicate part is the borrow/merge cascade when a former
  root becomes an underfull child.
- **Randomization with high-probability bounds** (quicksort) — the union bound turns a per-element
  tail bound into a whole-array O(n lg n) guarantee, which the experiment corroborates.
- **Max-flow / min-cut** as a modelling hammer: edge-disjoint paths and bipartite b-matching are
  both one flow computation, and sensitivity analysis gives O(k(V+E)) dynamic updates.
- **Reductions and hardness**: encoding 3SAT as independent set (and verifying the encoding is
  faithful in code), plus **approximation** (FPTAS value-scaling) and **FPT** (bounded search +
  kernelization) as the two principled responses to NP-hardness.
- **Distributed impossibility**: deterministic identical processes cannot break symmetry, which
  randomization circumvents — and coordinating BFS by level avoids the corrections of naïve relaxation.

## Credits & license

Based on the problem sets of **6.046J / 18.410J Design and Analysis of Algorithms** (MIT
OpenCourseWare, Spring 2015) by Profs. Erik Demaine, Srini Devadas, and Nancy Lynch, and on
*Introduction to Algorithms* (CLRS). This repository is an independent educational
reimplementation and set of solutions; all course materials, problem statements, and
specifications belong to their original authors (the course PDFs are **not** redistributed here —
they are downloaded from OCW at build time and git-ignored). Original code and write-ups in this
repo are released under the [MIT License](LICENSE).

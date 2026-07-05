# 6.046J / 18.410J — Problem Set 8 Solutions

**Topics:** linear programming (Simplex, duality), NP-completeness (reductions).

> Code: [`code/ps8/`](../code/ps8/) — `simplex.py` (P8-1, a real exact-arithmetic Simplex), `reductions.py` (P8-2 reduction verifier). Verified by `test_ps8.py` (5/5). Evidence: [`results/ps8_tests.txt`](../results/ps8_tests.txt), [`results/ps8_verification.txt`](../results/ps8_verification.txt).

---

## Exercises (CLRS 29 LP, 34 NP-completeness)

- **29.2-2 / 29.2-4** — converting an LP to standard/slack form; expressing max-flow as an LP.
- **34.2-8 / 34.3-5** — $\text{TAUTOLOGY}\in\text{co-NP}$; $2\text{-CNF-SAT}\in\text{P}$ (via implication-graph SCCs) whereas $3\text{-CNF-SAT}$ is NP-complete.

---

## Problem 8-1 — A Simple Simplex Example

$$\max\ p=4x_1+x_2\quad\text{s.t.}\quad x_1+x_2\le10,\ \ x_2\ge 4x_1-20,\ \ x_1+3x_2\le24,\ \ x_1,x_2\ge0.$$

### (a) Feasible region

Rewriting $x_2\ge 4x_1-20$ as $4x_1-x_2\le20$, the feasible region is the polygon bounded by $x_1=0$, $x_2=0$, $x_1+x_2=10$, $4x_1-x_2=20$, $x_1+3x_2=24$. Its vertices are $(0,0),(5,0),(6,4),(3,7),(0,8)$ (each an intersection of two tight constraints; verified feasible by `brute_vertices`).

### (b) Standard and slack form

**Standard form** ($\max c^Tx,\ Ax\le b,\ x\ge0$):
$$A=\begin{pmatrix}1&1\\4&-1\\1&3\end{pmatrix},\ b=\begin{pmatrix}10\\20\\24\end{pmatrix},\ c=\begin{pmatrix}4\\1\end{pmatrix}.$$

**Slack form** (introduce $x_3,x_4,x_5\ge0$):
$$
\begin{aligned}
x_3&=10-x_1-x_2\\
x_4&=20-4x_1+x_2\\
x_5&=24-x_1-3x_2\\
p&=0+4x_1+x_2
\end{aligned}
$$
with initial basic feasible solution $x_1=x_2=0$, $(x_3,x_4,x_5)=(10,20,24)$, $p=0$.

### (c) Simplex iterations

Starting basis $\{x_3,x_4,x_5\}$. Bland's rule (entering = smallest-index negative reduced cost).

- **Pivot 1:** $x_1$ enters (reduced cost $4$). Ratio test: $10/1,\ 20/4=5,\ 24/1$ → $x_4$ leaves (row 1). New solution $(x_1,x_2)=(5,0)$, $p=20$.
- **Pivot 2:** $x_2$ enters (still improves). Ratio test picks $x_3$ leaving (row 0). New solution $(x_1,x_2)=(6,4)$, $p=28$.
- No negative reduced cost remains → **optimal**.

**Optimum:** $x^\*=(6,4)$, $p^\*=28$. The successive feasible solutions $(0,0)\to(5,0)\to(6,4)$ trace an edge path on the polygon to the vertex $(6,4)$. Confirmed by the solver (`pivots = [(1,0),(0,1)]`, optimum $28$) and cross-checked against `scipy.linprog` and vertex enumeration.

### (d) Dual LP and its optimum

Primal (standard form) dual: $\min\ b^Ty$ s.t. $A^Ty\ge c,\ y\ge0$, i.e.
$$\min\ 10y_1+20y_2+24y_3\quad\text{s.t.}\quad y_1+4y_2+y_3\ge4,\ \ y_1-y_2+3y_3\ge1,\ \ y\ge0.$$
By **strong duality** the dual optimum equals the primal optimum $=28$. Reading the dual solution off the final tableau (dual $y_i$ = reduced cost of slack $x_{2+i}$):
$$y^\*=\left(\tfrac85,\ \tfrac35,\ 0\right),\qquad b^Ty^\*=10\cdot\tfrac85+20\cdot\tfrac35+24\cdot0=16+12=28.\ \checkmark$$
($y_3^\*=0$ by complementary slackness: constraint 3, $x_1+3x_2=6+12=18<24$, is slack at the optimum.) Verified: `dual_solution()` returns $(8/5,3/5,0)$ and $b^Ty=28=p^\*$; dual feasibility $A^Ty\ge c,\ y\ge0$ also checked on 200 random LPs.

---

## Problem 8-2 — NP-Completeness

### (a) TRIPLE-SAT is NP-complete

TRIPLE-SAT: does Boolean formula $\varphi$ have $\ge 3$ distinct satisfying assignments?

**In NP:** a certificate is three distinct assignments; verifying each satisfies $\varphi$ and that they are pairwise distinct is polynomial.

**NP-hard (reduction from SAT).** Given a SAT instance $\varphi$ over variables $x_1,\dots,x_n$, add **two fresh variables** $y,z$ and output
$$\varphi' = \varphi \wedge (y\vee \bar y).$$
The clause $(y\vee\bar y)$ is a tautology, so it doesn't constrain anything; $z$ appears nowhere. Now: if $\varphi$ is satisfiable by some assignment $a$, then $\varphi'$ is satisfied by $a$ combined with **any** of the $4$ combinations of $(y,z)$ — that is $\ge 4\ge3$ distinct satisfying assignments. If $\varphi$ is unsatisfiable, $\varphi'$ has $0$. So $\varphi\in\text{SAT}\iff\varphi'\in\text{TRIPLE-SAT}$. The transformation is polynomial. Hence TRIPLE-SAT is NP-hard, and with membership in NP, **NP-complete**. ∎

### (b) DONUT is NP-hard; poly-time DONUT $\Rightarrow$ P $=$ NP

DONUT: given graph $G$, profits $p(u)\ge0$, integer $k$ — is there an independent set $U$ with $\sum_{u\in U}p(u)\ge k$?

**NP-hard (reduction from 3SAT via INDEPENDENT-SET).** Standard 3SAT → INDEPENDENT-SET reduction: for a 3-CNF $\varphi$ with $m$ clauses, build a graph with **one vertex per literal-occurrence**; make a **triangle** among the three literals of each clause; and add an edge between any two vertices holding **contradictory** literals ($x_i$ and $\bar x_i$). Set all profits $p(u)=1$ and $k=m$.

- *If $\varphi$ is satisfiable:* pick, from each clause, one literal made true by a satisfying assignment. These $m$ vertices are independent — no two are in the same clause-triangle (one per clause), and no two are contradictory (they're all consistent with one assignment). So an IS of size $m$, total profit $m=k$, exists.
- *If an IS of size $m$ exists:* it has $\le1$ vertex per triangle, so exactly one per clause; the chosen literals are non-contradictory (no contradiction edges inside an IS), so they extend to a consistent assignment satisfying every clause.

Thus $\varphi\in3\text{SAT}\iff (G,p\equiv1,k=m)\in\text{DONUT}$; the construction is polynomial, so DONUT is NP-hard. **Verified on 500 random 3-CNF instances: $\varphi$ satisfiable $\iff$ the reduction graph has an independent set of size $m$, both directions, 500/500.**

**Optimization ⇒ P = NP.** DONUT is NP-complete (it is also in NP: an IS with its profit is a poly-checkable certificate). A polynomial algorithm that *outputs the maximum-profit* independent set $U^\*$ immediately decides DONUT (compare $\sum p(U^\*)$ to $k$) in polynomial time. That would put an NP-complete problem in P, forcing **P $=$ NP**. (Verified: `donut_decision(k=opt)` is always True and `donut_decision(k=opt+1)` always False, tying the optimization to the decision problem.)

### (c) Profit-maximizing task scheduling is NP-complete

$n$ tasks, task $a_j$ has time $t_j$, profit $p_j$, deadline $d_j$; one machine, non-preemptive, each run task must finish by its deadline; **maximize total profit** of scheduled tasks.

**Decision version (SCHED):** given also an integer $P$, is there a feasible schedule of a subset of tasks with total profit $\ge P$?

**In NP:** a certificate is the chosen subset with start times; check no overlap, each finishes by its deadline, and total profit $\ge P$ — all polynomial. (Also: if a subset is schedulable at all, it is schedulable in **earliest-deadline-first** order, so the certificate can just be the subset.)

**NP-hard (reduction from SUBSET-SUM / KNAPSACK, or PARTITION).** Reduce from **SUBSET-SUM**: given positive integers $s_1,\dots,s_n$ and target $B$, decide if some subset sums to exactly $B$. Construct tasks with $t_j=p_j=s_j$ and a **common deadline** $d_j=B$ for all $j$. A subset $S$ is schedulable (all by deadline $B$) iff $\sum_{j\in S}t_j\le B$, and its profit is $\sum_{j\in S}s_j$. Set $P=B$. Then a schedule of profit $\ge B$ exists iff some subset has total size $\le B$ and total profit $\ge B$ — i.e. $\sum_{j\in S}s_j=B$ exactly (size = profit here) — which is precisely a SUBSET-SUM solution. The reduction is polynomial, so SCHED is NP-hard; with membership in NP, **NP-complete**. ∎

*(Equivalently one reduces from KNAPSACK: sizes $t_j$, values $p_j$, capacity $B=$ common deadline — the deadline-$B$ single-machine schedule of maximum profit is exactly the knapsack of capacity $B$, whose decision form is NP-complete.)*

---

### Verification summary

```
$ python -m pytest code/ps8/test_ps8.py -q
5 passed
```
- Simplex == scipy.linprog and == brute-force vertices on 300 random LPs; the pset LP solved to $x^\*=(6,4),\ p^\*=28$; strong duality ($y^\*=(8/5,3/5,0)$, $b^Ty^\*=28$) checked on 200 LPs incl. dual feasibility.
- 3SAT satisfiable $\iff$ reduction graph has size-$m$ independent set, 500 random instances; DONUT decision tied to optimization on 200 graphs.

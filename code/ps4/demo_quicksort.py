"""Run the PS4-2 quicksort comparison-count experiment, print a table, and save a
figure showing empirical comparisons vs the n lg n reference and the mean/max
concentration -- the measured corroboration of the high-probability bound."""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from quicksort_analysis import experiment

RESULTS = os.path.join(os.path.dirname(__file__), "..", "..", "results")


def main():
    sizes = [100, 300, 1000, 3000, 10000]
    rows = experiment(sizes=sizes, trials_per_size=200, seed=2024)

    print(f"{'n':>7} {'trials':>7} {'mean_comps':>12} {'max_comps':>11} "
          f"{'n_lg_n':>12} {'mean/nlgn':>10} {'max/nlgn':>9}")
    for r in rows:
        print(f"{r['n']:>7} {r['trials']:>7} {r['mean_comps']:>12.1f} "
              f"{r['max_comps']:>11} {r['n_lg_n']:>12.1f} "
              f"{r['mean_ratio']:>10.3f} {r['max_ratio']:>9.3f}")

    # figure: mean & max comparisons vs n lg n
    ns = [r["n"] for r in rows]
    mean_c = [r["mean_comps"] for r in rows]
    max_c = [r["max_comps"] for r in rows]
    ref = [r["n_lg_n"] for r in rows]
    theory = [2 * math.log(2) * x for x in ref]  # 2 ln2 * n log2 n = expected

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(ns, mean_c, "o-", label="mean comparisons (200 trials)")
    ax.plot(ns, max_c, "^--", label="max comparisons (200 trials)")
    ax.plot(ns, theory, "k:", label=r"$2\ln 2\cdot n\log_2 n$ (expected)")
    ax.plot(ns, [3 * x for x in ref], "r:", label=r"$3\,n\log_2 n$ (h.p. upper env.)")
    ax.set_xlabel("n")
    ax.set_ylabel("comparisons")
    ax.set_title("Randomized Quicksort comparison count vs $n\\lg n$")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = os.path.abspath(os.path.join(RESULTS, "ps4_quicksort_comparisons.png"))
    fig.savefig(out, dpi=110)
    print(f"\nsaved figure -> {out}")


if __name__ == "__main__":
    main()

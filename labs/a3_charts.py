"""
A3 CHARTS: the two charts the assignment asks for, drawn from results/a3_results.csv.

    python labs/a3_charts.py                 reads results/a3_results.csv, writes two PNGs to results/

Chart A  FedAvg accuracy against number of hospitals, one line per skew (E = 5)
Chart B  worst-hospital accuracy against skew, one bar per E, one panel per consortium size
Needs: matplotlib (python -m pip install matplotlib)
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results" / "a3_results.csv"

SKEWS = ["none", "label", "quantity", "feature", "concept", "realistic"]
SKEW_COLOR = {"none": "#2a78d6", "label": "#eb6834", "quantity": "#1baf7a",
              "feature": "#eda100", "concept": "#e87ba4", "realistic": "#008300"}
SKEW_MARKER = {"none": "o", "label": "s", "quantity": "^", "feature": "D", "concept": "v", "realistic": "P"}
E_COLOR = {1: "#86b6ef", 5: "#2a78d6", 20: "#104281"}   # one hue, light to dark: E is ordered
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})


def load():
    with open(SRC) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["n_clients"], r["E"] = int(r["n_clients"]), int(r["E"])
        for k in ("fedavg_acc", "worst_hospital_acc", "centralized_acc"):
            r[k] = float(r[k])
    return rows


def spread(values, gap):
    """Nudge end labels apart so none overlap (keeps their order)."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = list(values)
    for a, b in zip(order, order[1:]):
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    return out


def chart_a(rows, E=5):
    sizes = sorted({r["n_clients"] for r in rows})
    fig, ax = plt.subplots(figsize=(6.6, 3.9), dpi=200)
    ends = []
    for s in SKEWS:
        ys = [next(r["fedavg_acc"] for r in rows if r["skew"] == s and r["n_clients"] == n and r["E"] == E) for n in sizes]
        ax.plot(sizes, ys, color=SKEW_COLOR[s], lw=2, marker=SKEW_MARKER[s], ms=6,
                markeredgecolor=SURFACE, markeredgewidth=1.2, label=s, zorder=3)
        ends.append((s, ys[-1]))
    pos = spread([y for _, y in ends], 0.0024)
    for (s, y), p in zip(ends, pos):
        ax.annotate(s, (sizes[-1], y), xytext=(sizes[-1] + 0.35, p), va="center", fontsize=8.5, color=INK,
                    arrowprops=dict(arrowstyle="-", color=GRID, lw=0.8) if abs(p - y) > 0.0006 else None)
    ax.set_xticks(sizes)
    ax.set_xlim(sizes[0] - 0.4, sizes[-1] + 2.2)
    ax.set_ylim(0.775, 0.825)
    ax.set_xlabel("Number of hospitals in the consortium")
    ax.set_ylabel("FedAvg accuracy on the neutral test set\n(proportion correct, 0 to 1)")
    ax.set_title(f"Chart A. FedAvg accuracy by consortium size, one line per skew (E = {E}, 20 rounds)",
                 loc="left", fontsize=9.5, color=INK, pad=10)
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.legend(title="skew", ncol=6, loc="upper center", bbox_to_anchor=(0.45, -0.2), frameon=False,
              fontsize=8, title_fontsize=8, handlelength=1.6, columnspacing=1.2)
    fig.tight_layout()
    out = ROOT / "results" / "chart_a_accuracy_vs_hospitals.png"
    fig.savefig(out, facecolor=SURFACE); plt.close(fig)
    return out


def chart_b(rows):
    sizes = sorted({r["n_clients"] for r in rows})
    Es = sorted({r["E"] for r in rows})
    fig, axes = plt.subplots(1, len(sizes), figsize=(7.2, 3.6), dpi=200, sharey=True)
    w = 0.26
    for ax, n in zip(axes, sizes):
        for j, E in enumerate(Es):
            xs = [i + (j - (len(Es) - 1) / 2) * w for i in range(len(SKEWS))]
            ys = [next(r["worst_hospital_acc"] for r in rows if r["skew"] == s and r["n_clients"] == n and r["E"] == E) for s in SKEWS]
            ax.bar(xs, ys, width=w * 0.9, color=E_COLOR[E], label=f"E = {E}", zorder=3)
        ax.axhline(0.70, color=INK2, lw=1, ls=(0, (4, 3)), zorder=4, label="charter floor 0.70")
        ax.set_xticks(range(len(SKEWS)))
        ax.set_xticklabels(SKEWS, rotation=40, ha="right", fontsize=8)
        ax.set_title(f"{n} hospitals", fontsize=9, color=INK)
        ax.set_ylim(0, 1.0)
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    axes[0].set_ylabel("Worst hospital's accuracy\n(proportion correct, 0 to 1)")
    fig.suptitle("Chart B. Worst-hospital accuracy by skew, one bar per E (local epochs per round)",
                 x=0.01, ha="left", fontsize=9.5, color=INK)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=len(Es) + 1, loc="lower center", frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, -0.01))
    fig.supxlabel("Kind of skew between hospitals", y=0.075, fontsize=9, color=INK)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    out = ROOT / "results" / "chart_b_worst_hospital_vs_skew.png"
    fig.savefig(out, facecolor=SURFACE); plt.close(fig)
    return out


if __name__ == "__main__":
    if not SRC.exists():
        sys.exit("results/a3_results.csv not found: run python labs/a3_harness.py first")
    data = load()
    for path in (chart_a(data), chart_b(data)):
        print(f"wrote {path.relative_to(ROOT)}")

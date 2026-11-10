"""
A3 ADD-ON: who pays, by name, at every consortium size.

    python labs/a3_who_pays.py                      all skews, 3 / 5 / 10 hospitals, E = 5
    python labs/a3_who_pays.py --skews label concept --clients 3 10

The harness reports only the WORST hospital's accuracy. This script uses the
same simulator and the same settings (20 rounds, local-only trained 100 epochs)
and writes one row per hospital, so the report can name who paid:

    local_only   the hospital's own model, on its slice of the neutral test set
    fedavg       the shared FedAvg model after 20 rounds, same slice
    finetuned    the FedAvg model plus 5 local epochs on the hospital's own data
    change       fedavg minus local_only (negative = the hospital paid to federate)

Output: results/a3_who_pays.csv
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fl import federation as F, model
from fl.world import make_world

ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--clients", type=int, nargs="+", default=[3, 5, 10])
    ap.add_argument("--skews", nargs="+", default=["none", "label", "quantity", "feature", "concept", "realistic"])
    ap.add_argument("--E", type=int, default=5)
    ap.add_argument("--rounds", type=int, default=20)
    ap.add_argument("--out", default="results/a3_who_pays.csv")
    a = ap.parse_args()

    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for n in a.clients:
        for skew in a.skews:
            world = make_world(n, skew)
            local = F.local_only(world, epochs=100)
            theta, _ = F.run(world, F.Config(rounds=a.rounds, E=a.E, verbose=False))
            for k, c in enumerate(world.clients):
                Xk, yk = world.test_for(k)
                tuned = model.local_train(theta, c.X_train, c.y_train, 5, 64, 0.1, rng=np.random.default_rng(1))
                lo, fa, ft = (model.accuracy(m, Xk, yk) for m in (local[c.name], theta, tuned))
                rows.append({"n_clients": n, "skew": skew, "E": a.E, "hospital": c.name, "patients": c.n,
                             "readmit_rate": round(float(c.y_train.mean()), 3), "local_only": round(lo, 4),
                             "fedavg": round(fa, 4), "finetuned": round(ft, 4), "change": round(fa - lo, 4)})
            paid = min((r for r in rows if r["n_clients"] == n and r["skew"] == skew), key=lambda r: r["change"])
            print(f"n={n:<3} skew={skew:<10} biggest loss from federating: {paid['hospital']:<15} "
                  f"local {paid['local_only']:.3f} -> FedAvg {paid['fedavg']:.3f} ({paid['change']:+.3f}), fine-tuned {paid['finetuned']:.3f}")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\nwrote {out.relative_to(ROOT)} with {len(rows)} rows")

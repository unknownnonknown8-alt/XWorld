"""Tiny synthetic recovery experiment, NOT a measured Roman selection function."""

import csv
from demonstration import ROOT
from demonstration.simulate import simulate_light_curve
from demonstration.core import prepare_light_curve, analyze_light_curve


def main():
    out = ROOT / "practice/outputs/05_recovery"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    # Step 1: repeat at three noise levels and three independent noise seeds.
    # Geometry is FIXED: this is only a sensitivity experiment for one system.
    for noise in (0.005, 0.03, 0.15):
        for kind in ("planet", "single", "artifact"):
            hits = 0
            for seed in (10, 11, 12):
                raw = simulate_light_curve(kind, seed=seed, noise=noise, cadence_minutes=30)
                time, flux, error, _ = prepare_light_curve(*raw[:4])
                result, _, _ = analyze_light_curve(time, flux, error)
                flagged = result["decision"] == "anomaly_candidate"
                hits += flagged
                rows.append({"kind": kind, "noise": noise, "seed": seed,
                             "flagged": flagged, "decision": result["decision"]})
            print(f"noise={noise:.3f}; {kind:8s}: {hits}/3 anomaly flags")
    # Step 2: inspect misses AND nonplanet triggers, not a single accuracy number.
    with (out / "recovery.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("Three trials per setting are far too few for calibrated efficiency estimates.")
    # TRY: more seeds, other q/s/alpha/rho, real noise and image-level injections.
    # Do not tune thresholds here and report these same data as independent tests.


if __name__ == "__main__":
    main()

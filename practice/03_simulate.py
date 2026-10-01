"""Practice saving a physical microlensing time series to CSV. Offline."""

import numpy as np
from demonstration import ROOT
from demonstration.simulate import simulate_light_curve
from demonstration.run import write_json


def main():
    out = ROOT / "practice/outputs/03_simulate"
    out.mkdir(parents=True, exist_ok=True)
    # Step 1: change planet to single, flat or artifact and compare the outputs.
    time, flux, error, quality, truth = simulate_light_curve("planet", seed=42)
    # Step 2: CSV contains observations only; keep hidden labels separately.
    np.savetxt(out / "light_curve.csv", np.column_stack((time, flux, error, quality)),
               delimiter=",", header="time_days,flux,flux_err,quality", comments="")
    write_json(out / "truth.json", truth)
    print("Saved observations and separate truth in", out)
    # TRY: noise=0.02 or cadence_minutes=60. What happens to a short anomaly?


if __name__ == "__main__":
    main()

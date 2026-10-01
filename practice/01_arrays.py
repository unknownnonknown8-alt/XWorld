"""Practice arrays, masks, weighted means and seeded randomness. Offline."""

import numpy as np


def main():
    # Step 1: each array entry is one measurement of the SAME source.
    flux = np.array([1.01, 0.99, np.nan, 1.03, 1.7])
    error = np.array([0.02, 0.02, 0.02, 0.03, 0.01])
    quality = np.array([0, 0, 0, 0, 1])
    # Step 2: reject invalid/known-bad data, not arbitrary large fluxes.
    usable = np.isfinite(flux) & (error > 0) & (quality == 0)
    good_flux, good_error = flux[usable], error[usable]
    # Step 3: precise observations get more weight.
    weights = 1 / good_error**2
    mean = np.sum(weights * good_flux) / np.sum(weights)
    mean_error = np.sqrt(1 / np.sum(weights))
    print("Mask:", usable)
    print(f"Weighted mean: {mean:.4f} +/- {mean_error:.4f}")
    # Step 4: a seed makes simulated noise reproducible.
    print("Repeatable Gaussian noise:", np.random.default_rng(42).normal(0, 0.02, 5))
    # TRY: set quality[-1]=0. Why does the result change so much?
    # Is a large flux always bad? No: it could be the event you are searching for.


if __name__ == "__main__":
    main()

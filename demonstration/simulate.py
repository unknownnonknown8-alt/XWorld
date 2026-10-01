"""Create physical lensing fluxes and idealized observations, separate from detection."""

import numpy as np
import MulensModel as mm

from .core import magnification


def simulate_light_curve(kind="planet", seed=42, noise=0.005, cadence_minutes=15.0):
    """Return time, measured_flux, error, quality and separate simulation truth.

    kind is used to GENERATE data. It is never supplied to the detector.
    noise is the 1-sigma error at unlensed total flux=1, not a Roman noise model.
    """
    if kind not in ("planet", "single", "flat", "artifact"):
        raise ValueError("kind must be planet, single, flat or artifact.")
    if not np.isfinite(noise) or noise <= 0:
        raise ValueError("noise must be finite and positive.")
    if not np.isfinite(cadence_minutes) or not 5 <= cadence_minutes <= 120:
        raise ValueError("Use a finite cadence between 5 and 120 minutes for this lab.")
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a nonnegative integer.")

    # Step 1: one idealized 72-day season; arbitrary relative days, NOT JD/UTC/TDB.
    time = np.arange(-36.0, 36.0, cadence_minutes / 1440)
    time = time[~((time > 10.0) & (time < 10.4))]  # a missing observing interval
    parameters = {"t_0": 0.0, "u_0": 0.15, "t_E": 12.0}
    if kind == "planet":
        # Step 2: a REAL binary-lens magnification calculation, not an added bump.
        parameters.update(s=1.2, q=0.001, alpha=60.0, rho=0.001)
        lens = mm.Model(parameters)
        lens.set_magnification_methods([-100.0, "VBBL", 100.0])
        amplification = lens.get_magnification(time)
    elif kind == "flat":
        amplification = np.ones_like(time)
    else:
        amplification = magnification(time, 0.0, 0.15, 12.0)

    # Step 3: blend source flux with a constant unresolved neighbour contribution.
    noiseless_flux = 0.8 * amplification + 0.2
    if kind == "artifact":
        # Intentional correlated instrumental-like bump, NOT a planetary model.
        noiseless_flux += 0.08 * np.exp(-0.5 * ((time - 3.0) / 0.08)**2)

    # Step 4: independent Gaussian noise with a simple photon-like flux scaling.
    error = noise * np.sqrt(noiseless_flux)
    rng = np.random.default_rng(seed)
    observed_flux = noiseless_flux + rng.normal(0.0, error)
    quality = np.zeros(len(time), dtype=int)
    quality[::997] = 1  # simulated unusable measurements, not Roman DQ bits
    observed_flux[quality != 0] += 0.4  # demonstrate why quality checks matter
    truth = {
        "kind": kind, "parameters": parameters if kind != "flat" else {},
        "source_flux": 0.8, "blend_flux": 0.2, "seed": seed,
        "noise_at_unit_flux": noise, "cadence_minutes": cadence_minutes,
        "time_convention": "arbitrary relative days; no physical epoch or time scale",
        "origin": "local MulensModel simulation; NOT official Roman simulation/data",
    }
    return time, observed_flux, error, quality, truth

"""Read this file one function at a time; each function is one pipeline step."""

from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

# Teaching thresholds, NOT calibrated discovery significance or a Roman standard.
MIN_EVENT_DELTA_CHI2 = 500.0
RESIDUAL_SIGMA = 3.0
MIN_RUN_POINTS = 5
GAP_FACTOR = 2.5


def magnification(time, t0, u0, tE):
    """Point-source, single-lens (PSPL) magnification: a smooth brightening."""
    u = np.sqrt(u0**2 + ((np.asarray(time) - t0) / tE)**2)
    return (u**2 + 2) / (u * np.sqrt(u**2 + 4))


def model_flux(time, parameters):
    """F = source_flux * magnification + unresolved_blended_flux."""
    t0, u0, tE, source_flux, blend_flux = parameters
    return source_flux * magnification(time, t0, u0, tE) + blend_flux


def prepare_light_curve(time, flux, error, quality):
    """Validate, select usable measurements, sort, and rescale flux and errors.

    No imputation, interpolation or sigma clipping: anomalies must survive.
    quality=0 means usable in OUR CSV convention, not in every mission product.
    """
    arrays = [np.asarray(a, dtype=float) for a in (time, flux, error, quality)]
    if any(a.ndim != 1 for a in arrays) or len({a.size for a in arrays}) != 1:
        raise ValueError("The four columns must be equal-length 1D arrays.")
    time, flux, error, quality = arrays
    finite = np.isfinite(time) & np.isfinite(flux) & np.isfinite(error)
    good = finite & (error > 0) & (quality == 0)
    report = {"input_rows": len(time), "removed_rows": int((~good).sum())}
    time, flux, error = time[good], flux[good], error[good]
    if len(time) < 30:
        raise ValueError("Need at least 30 finite, quality=0 points with positive errors.")
    order = np.argsort(time)
    time, flux, error = time[order], flux[order], error[order]
    if np.any(np.diff(time) <= 0):
        raise ValueError("Times must be unique; split filters or resolve duplicate epochs first.")
    scale = float(np.median(flux))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("This teaching fitter requires a positive median flux.")
    # Scaling both arrays preserves (data - model) / uncertainty.
    report.update(used_rows=len(time), flux_scale=scale)
    return time, flux / scale, error / scale, report


def read_light_curve(path):
    """Read a normalized one-source/one-band CSV, not an arbitrary mission file."""
    table = np.genfromtxt(Path(path), delimiter=",", names=True, dtype=float)
    names = ("time_days", "flux", "flux_err", "quality")
    if not set(names).issubset(table.dtype.names or ()):
        raise ValueError("CSV needs time_days,flux,flux_err,quality columns.")
    return prepare_light_curve(*(np.atleast_1d(table[name]) for name in names))


def fit_single_lens(time, flux, error):
    """Fit five parameters with weighted least squares from several guesses.

    We center times internally for numerical stability. Bounds are intentionally
    broad but finite; these are a beginner fitter's limits, not physical priors.
    A few starts are NOT a global search and do not resolve all degeneracies.
    """
    reference_time = float(np.median(time))
    centered_time = time - reference_time
    span = float(np.ptp(time))
    cadence = float(np.median(np.diff(time)))
    lower = [centered_time.min(), 0.001, cadence, 0.00001, 0.0]
    upper = [centered_time.max(), 2.0, 3 * span, 10.0, 10.0]

    def residual(parameters):
        return (flux - model_flux(centered_time, parameters)) / error

    peak_time = float(centered_time[np.argmax(flux)])
    fits = []
    # No injected/truth parameters are provided to the fitter.
    for t0_guess in (peak_time, 0.0):
        for u0_guess in (0.1, 0.4):
            guess = [t0_guess, u0_guess, span / 6, 0.8, 0.2]
            fit = least_squares(residual, guess, bounds=(lower, upper),
                                x_scale="jac", max_nfev=700)
            if fit.success and np.all(np.isfinite(fit.fun)):
                fits.append(fit)
    if not fits:
        raise RuntimeError("All single-lens fits failed; inspect data and starting guesses.")
    best = min(fits, key=lambda fit: float(np.sum(fit.fun**2)))
    prediction = model_flux(centered_time, best.x)
    parameters = best.x.copy()
    parameters[0] += reference_time
    # A blend_flux=0 boundary is allowed; geometric boundaries need review.
    geometry_boundary = bool(np.any(best.active_mask[:3] != 0))
    info = {
        "parameters": dict(zip(("t0_days", "u0", "tE_days", "source_flux", "blend_flux"),
                               map(float, parameters))),
        "geometry_boundary": geometry_boundary,
        "optimizer_message": str(best.message),
        "successful_starts": len(fits),
    }
    return prediction, info


def longest_residual_run(time, residual, sigma=RESIDUAL_SIGMA):
    """Find consecutive same-sign >sigma residuals; never bridge a long gap."""
    max_gap = GAP_FACTOR * float(np.median(np.diff(time)))
    longest = {"points": 0, "start_days": None, "end_days": None, "sign": 0}
    count, previous_sign, start = 0, 0, 0
    for i, value in enumerate(residual):
        sign = 1 if value > sigma else -1 if value < -sigma else 0
        gap = i > 0 and time[i] - time[i - 1] > max_gap
        if sign == 0:
            count = 0
        elif sign == previous_sign and not gap and count > 0:
            count += 1
        else:
            count, start = 1, i
        if count > longest["points"]:
            longest = {"points": count, "start_days": float(time[start]),
                       "end_days": float(time[i]), "sign": sign}
        previous_sign = sign
    return longest


def analyze_light_curve(time, flux, error):
    """Search observations ONLY: this function cannot see simulated class/truth."""
    prediction, fit_info = fit_single_lens(time, flux, error)
    constant = float(np.average(flux, weights=1 / error**2))
    chi2_constant = float(np.sum(((flux - constant) / error)**2))
    residual = (flux - prediction) / error
    chi2_single = float(np.sum(residual**2))
    delta = chi2_constant - chi2_single
    run = longest_residual_run(time, residual)
    event_like = delta >= MIN_EVENT_DELTA_CHI2
    anomalous = run["points"] >= MIN_RUN_POINTS
    if not event_like:
        decision = "no_event_candidate"
    elif fit_info["geometry_boundary"]:
        decision = "fit_needs_review"
    elif anomalous:
        decision = "anomaly_candidate"
    else:
        decision = "single_lens_like"
    result = {
        "decision": decision,
        "chi2_constant": chi2_constant,
        "chi2_single_lens": chi2_single,
        "delta_chi2_constant_to_single": delta,
        "reduced_chi2_single_lens": chi2_single / (len(time) - 5),
        "longest_residual_run": run,
        "fit": fit_info,
        "thresholds": {"event_delta_chi2": MIN_EVENT_DELTA_CHI2,
                       "residual_sigma": RESIDUAL_SIGMA,
                       "min_run_points": MIN_RUN_POINTS, "gap_factor": GAP_FACTOR},
        "warning": "Heuristic candidate screening, NOT planet confirmation or a p-value.",
    }
    return result, prediction, residual

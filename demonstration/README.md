# Demonstration: physical microlensing simulation → anomaly candidates

## Run

From the repository root, with the environment activated:

```bash
python -m demonstration.run
python -m demonstration.run --help
```

No downloads or accounts are needed after installing requirements. Files are saved
under `demonstration/outputs/latest/`, not opened in a GUI. Use another `--output`
path containing `outputs/` inside the repository to preserve an experiment.

## Read the code in this order

1. `core.py`: `magnification` and `model_flux` — the simple physical baseline.
2. `simulate.py`: observations from physical models plus noise, with truth separate.
3. `core.py`: `prepare_light_curve` — validation without erasing possible signals.
4. `core.py`: `fit_single_lens` — fitting data, not using the injected answer.
5. `core.py`: `longest_residual_run` and `analyze_light_curve` — screening rules.
6. `run.py`: the plain sequential pipeline, outputs, plots and provenance.

Each function has a docstring and the important steps have comments. The practice
folder lets you run the pieces independently; you do not need classes, a database,
a workflow framework, or machine learning to understand this version.

## Exactly what each step does

### 1. Simulate observations

Create four one-source light curves:

| ID | What was injected (for evaluation AFTER detection) |
|---|---|
| event_001 | A finite-source star–planet binary lens |
| event_002 | A point-source single lens, no planet |
| event_003 | Constant flux, no event |
| event_004 | Single lens plus an instrumental-like correlated bump, no planet |

The generator knows these labels. The detector receives only time, flux and error.
The physical planet signal is computed by MulensModel's finite-source binary-lens
`VBBL` method, not a Gaussian perturbation. A Gaussian bump is used **only** as an
explicitly nonplanetary artifact control.

### 2. Validate and prepare

Read `time_days,flux,flux_err,quality`. Keep finite measurements with positive
uncertainties and `quality=0`. Report excluded counts. Sort times and reject duplicate
epochs. Require at least 30 usable points. Scale flux and uncertainties by the same
positive median so optimizer bounds work on order-one numbers.

This is numerical rescaling, not a fitted baseline or astrophysical detrending.
No gap filling or sigma clipping is done. The CSV quality convention is our own;
real mission DQ flags need a product-specific mapping before import.

### 3. Fit a point-source, single-lens model

```text
u(t) = sqrt(u0**2 + ((t - t0) / tE)**2)
A(t) = (u(t)**2 + 2) / (u(t) * sqrt(u(t)**2 + 4))
F(t) = source_flux * A(t) + blend_flux
```

SciPy least squares minimizes `sum(((data-model)/error)**2)` for five parameters:
`t0`, `u0`, `tE`, source flux and blend flux. Four starting guesses reduce, but do
not eliminate, local-minimum risk. No simulation truth is passed in. Times are
centered internally and returned in the original input coordinate.

Bounds: `t0` within the observations, `0.001 <= u0 <= 2`, median cadence <= `tE`
<= three data spans, and positive source/nonnegative blend flux capped at 10 in
rescaled units. They simplify the exercise and exclude some real scenarios,
including negative fitted blending. Geometry-bound fits require manual review.
The code does not estimate parameter posteriors or claim these are global fits.

### 4. Screen for anomalies

First compare the single lens against weighted constant flux. An improvement of
at least 500 in chi-squared marks an event-like light curve in this toy setup.
**This is NOT a single-lens versus planetary-model comparison.**

Compute `(observed_flux - fitted_flux) / flux_error`. Flag an anomaly if at least
five consecutive measurements exceed +3 or fall below -3 with the same sign.
A time gap larger than 2.5 times the median sampling interval breaks the run.

| Output | Interpretation |
|---|---|
| `no_event_candidate` | Did not pass this simple constant-versus-lens event gate |
| `single_lens_like` | Event gate passed, no qualifying residual run |
| `anomaly_candidate` | Event gate passed and a coherent residual run needs follow-up |
| `fit_needs_review` | Event-like but a geometry parameter hit its optimizer bound |

These names are screening outcomes, not ground-truth classifications. Thresholds
are deliberately illustrative; no false-alarm probability or calibrated survey
completeness is attached to them. Finite-source single lenses, stellar binaries,
variable stars, systematics and bad fits can all produce anomalies.

### 5. Save diagnostics

- `event_*.csv`: observed inputs; no injected labels as columns.
- `event_*_fit.csv`: usable rescaled data, fitted baseline and standardized residuals.
- `event_*_result.json`: statistics, parameters, thresholds, fit status, removal counts.
- `event_*.png`: full light curve, residuals, and a zoom near the largest residual.
- `summary.csv`: one row per analyzed source.
- `simulation_truth.json`: generator parameters, labels and provenance, separate from fitting.
- `manifest.json`: run status, settings, package versions, Git revision, code hashes,
  input hashes and paths. Check `status == "complete"` before trusting outputs.

If you change modes/output settings, choose a new directory; the runner overwrites
its own named products but does not delete unrelated or old products in the folder.
It intentionally stops on errors rather than silently skipping sources.

### 6. Evaluate, not confirm

For the default easy signal/noise settings, expect the planet and artifact to be
anomaly candidates, the single lens to be single-lens-like, and the flat control
to fail the event gate. **The artifact false positive is intentional.** Compare the
output to the separate truth only after the search. This is not a representative
population, and four examples do not measure a detector's reliability.

## Simulation assumptions

- One 72-day relative-time window, 15-minute nominal sampling and a 0.4-day gap.
- Instantaneous samples (no exposure integration), one unspecified band, one source.
- `t0=0 days`, `u0=0.15`, `tE=12 days`; for planet `q=0.001`, `s=1.2`,
  `alpha=60 degrees`, `rho=0.001`; uniform finite source, no limb darkening.
- Source flux 0.8 plus constant blend flux 0.2; no calibrated magnitude or electrons.
- Independent Gaussian errors `sigma = noise * sqrt(noiseless_flux)`, with
  `noise=0.005` at unit total flux. This is not a Roman WFI detector/noise model.
- A few explicitly flagged unusable points; a deliberately unflagged artifact control.
- No orbital motion, parallax, detector image simulation, realistic crowding,
  photometric extraction, six-season mission schedule or official survey forecast.
- Relative days are not JD/MJD, UTC/TDB or barycentrically corrected flight times.

These assumptions were selected for a readable, fast, offline lesson. They are
**Roman-like local physical simulations, not official Roman simulation products**.
Use Nexus/current mission documentation for actual product examples and forecasts.

## Try another CSV

```bash
python -m demonstration.run \
  --input practice/outputs/03_simulate/light_curve.csv \
  --output demonstration/outputs/imported
```

Run exercise 03 first to create that example. The input must be outside the output
directory so original observations are protected. For an external official dataset,
follow the explicit conversion/provenance checklist in [`lerning/pipelines.md`](../lerning/pipelines.md).
Do not feed magnitudes, mixed filters, an arbitrary FITS table or undocumented times
straight into this flux-only interface.

## What to add in your own version

First reproduce known events. Then add binary-lens fitting with broad parameter
searches, competing models, realistic systematics, multiple starts/modes, posterior
uncertainties and model comparison. Validate with independently generated datasets,
multiple geometries and image-level injection–recovery where relevant. Real planet
confirmation requires much more than detecting a deviation from a single lens.

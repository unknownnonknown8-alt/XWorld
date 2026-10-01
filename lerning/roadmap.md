# From your Python notebook to Roman exoplanet research

This saves and organizes the advice from the conversation. Learn in this order:

**Python → scientific computing → astronomical data and statistics → light curves
and photometry → microlensing → reproducible pipelines → optional ML.**

## 1. Choose a science route

| Route | Signal | Essential skills |
|---|---|---|
| Microlensing | A background source brightens; a planet perturbs the lensing signal | Crowded-field photometry, physical models, inference |
| Transits | A star periodically dims | Detrending, period searches, transit fitting, false positives |
| Coronagraph imaging | Faint planets next to bright stars | Optical PSFs, speckles, high-contrast imaging, astrometry |

Make **microlensing** the primary Roman specialization, and use a known TESS or
Kepler transit as a more accessible introduction. Roman's Galactic Bulge
Time-Domain Survey supports microlensing and transit science, but the two require
different searches. The coronagraph is a separate instrument/analysis route;
`romancal` WFI processing is not a coronagraph reduction workflow.

Do not wait for flight data. Roman Research Nexus early access has simulations,
software, tutorials, and cloud resources. Plan around learning milestones rather
than assuming a launch date or a fixed calibration waiting period. Mission plans
and product schedules can change; consult current official documentation.

## 2. Review of `PythonToAi.ipynb.json.txt`

Verified structure: **989 cells, 670 code and 319 Markdown**. Cell numbers below
count all cells from 1, not execution numbers. This is a curriculum/code review,
not a claim that every example was run or that the notebook is error-free.

| Section / cells | Recommendation | Reason |
|---|---|---|
| Types, lists, tuples, dictionaries, sets / 13–170 | Keep | Parameters, metadata, dataset organization |
| String methods / 25–81 | Skim repetition | Learn format, split, strip, join, filenames; do not memorize everything |
| Conditionals, loops, comprehensions / 171–210 | Keep | Filtering and batch processing |
| Functions and exceptions / 211–241 | Keep and expand | Reusable, reliable pipelines |
| NumPy / 242–284 | Highest priority; expand | Images and light curves are arrays |
| pandas, load/clean/merge / 285–438 | Keep | Catalogs and tables |
| Visualization / 439–479 | Keep | Add uncertainties, residuals, image displays, log scales |
| Aggregation/grouping / 480–501 | Keep | Group by star, detector, exposure, season |
| Preprocessing/feature selection / 502–580 | Use cautiously | Generic cleaning can erase real astronomical signals |
| Regression/classification / 581–646 | Concepts now, details later | Useful baselines, not replacements for physical models |
| Clustering/customer segmentation / 647–677 | Optional later | Anomaly-detection ideas can help; marketing exercise not needed |
| Neural networks, Iris, MNIST / 678–761 | Postpone | Not planet-search prerequisites |
| NLP/spam / 762–822 | Skip for this goal | Tokenization/stemming do not teach photometry |
| Movie recommendations / 823–881 | Skip | Collaborative filtering is not a priority |
| CIFAR-10 CNNs / 882–921 | Postpone | May later help reject image artifacts |
| Sentiment/chatbot / 922–989 | Skip | Not directly relevant |

A good point to switch to astronomy projects is **around cell 501**.

### Corrections and habits to avoid

- Cell 132 calls dictionaries unordered. Modern Python preserves insertion order.
- Cells 703–705 fit a scaler before the train/test split: information leakage.
  Split first; fit on training only; use `sklearn.pipeline.Pipeline` within CV.
- `fillna(0)`, mean imputation, and forward-fill are demonstrations, not safe
  defaults for missing light-curve measurements. Do not invent observations.
- Low feature variance does not mean low scientific importance. Small planetary
  signals can be exactly what you want.
- Do not suppress all warnings while learning. Investigate invalid calculations
  and deprecated APIs instead.
- Some notebook APIs are dated, including `plot_confusion_matrix` and
  `fillna(method="ffill")`. Use `ConfusionMatrixDisplay` and, where scientifically
  appropriate for the data type, `.ffill()` rather than reproducing obsolete APIs.
- An "outlier" may be a real short planetary microlensing anomaly. Never apply
  blind sigma clipping before understanding the signal and the quality flags.

## 3. Scientific Python

Deepen NumPy: Boolean masks and bitwise operations; broadcasting; vectorization;
axes/shapes/dtypes; views versus copies; NaN/Inf and masked arrays; precision;
seeded random generators; memory use and chunked processing.

Learn SciPy: weighted least squares, optimization, bounds, interpolation,
numerical integration, probability distributions, and signal processing.

Learn practical engineering: `pathlib`, file I/O, context managers, modules,
imports, basic classes/dataclasses, logging, config files, CLI arguments,
virtual environments, Git, and `pytest`. Move reusable functions out of notebooks.

**Deliverable:** read a light curve, validate its columns, plot error bars, fit a
model, and save both results and a diagnostic residual plot.

## 4. Mathematics and statistics

Study alongside projects, not as a wall of prerequisites:

1. Algebra, logarithms, basic calculus, and linear algebra.
2. Gaussian/Poisson probability distributions.
3. Uncertainties, propagation, weighted means, covariance.
4. Likelihoods, weighted fitting, numerical optimization.
5. Priors, posteriors, credible intervals, Bayesian inference.
6. MCMC convergence, effective sample size, multimodal posteriors.
7. Model comparison: extra parameters usually improve a fit even without a planet.
8. Detection efficiency, completeness, false positives, selection/population bias.

A starting statistic is

```text
chi_squared = sum(((observed_flux - model_flux) / flux_uncertainty)**2)
```

It assumes an appropriate model and (in its simplest interpretation) independent
Gaussian errors with trustworthy uncertainties. Correlated noise and underestimated
errors invalidate naive significance claims. A search over many trials also needs
a false-alarm calibration; a residual threshold is not a p-value.

## 5. Astronomy foundations

Learn flux/magnitude/zero points and SNR; RA/Dec and Galactic coordinates; pixels
versus sky positions; variability and eclipsing binaries; blending; stellar/orbital
physics. JD/MJD are **formats**, UTC/TDB are **scales**; barycentric corrections
and mission-specific offsets matter. A column called `time` is not self-describing.
Changing UTC to TDB alone is NOT the barycentric light-travel-time correction.

## 6. Photometry and image analysis

Roman's bulge fields are crowded. Extracting a trustworthy flux can be harder
than fitting the resulting light curve.

1. Inspect images, metadata, uncertainty arrays, quality bitmasks.
2. Estimate backgrounds.
3. Learn aperture photometry as a teaching exercise.
4. Understand the point-spread function (PSF).
5. Fit overlapping PSFs and understand blending.
6. Align images; learn astrometric calibration and WCS.
7. Learn difference imaging: align epochs and account for PSF differences.
8. Understand nonlinearity, saturation, persistence, cosmic rays, flat fields,
   detector reads, and ramp fitting.

Aperture photometry alone is not a solution for Roman's crowded-field science.
Image-level artificial-star/signal injection is required to evaluate extraction,
not just the downstream light-curve detector.

## 7. Microlensing specialization

Start with a point-source point-lens (PSPL) event:

- `t_0`: closest-approach time.
- `u_0`: minimum separation in Einstein-radius units.
- `t_E`: Einstein crossing time, not an orbital period.
- Source flux `F_s` and unresolved blended flux `F_b`.

Then learn binary lenses, planetary perturbations, mass ratio `q`, projected
separation `s` (Einstein-radius units), trajectory angle, finite-source size `rho`,
limb darkening, parallax, orbital motion, close/wide degeneracies, binary-source
alternatives, and joint fitting across telescopes/filters.

**A planetary fit often estimates mass ratio and projected separation, not Earth
masses or semimajor axis.** Further measurements/Galactic-model assumptions may be
needed. A short event alone does not establish an isolated planetary-mass lens.

Start with **MulensModel or pyLIMA**, not both. You do not need to implement a
binary-lens solver yourself. The demonstration uses MulensModel to generate a
physical planetary light curve, but deliberately stops at candidate detection.

## 8. Library priorities

| When | Tools | Purpose |
|---|---|---|
| Now | NumPy, SciPy, Matplotlib | Arrays, fitting, diagnostics |
| Now | pandas | Catalogs, metadata, candidate tables |
| Next | Astropy | Units, coordinates, time, tables, FITS, WCS, statistics |
| Next | astroquery | MAST and other astronomical services |
| Next | photutils | Backgrounds, detection, aperture/PSF photometry |
| Transit intro | lightkurve | Kepler/TESS light curves and pixels |
| Transit depth | Astropy BoxLeastSquares, batman | Transit searches and physical models |
| Microlensing | MulensModel OR pyLIMA | Physical light curves and modelling workflows |
| Inference | emcee, corner | Posterior sampling and correlations |
| Roman formats | asdf, roman_datamodels, gwcs | Data models and generalized coordinates |
| WFI calibration | romancal, CRDS | Calibration and reference files |
| Reproducibility | Git, pytest, then Snakemake | Versions, tests, workflows |
| Later | scikit-learn, dask, fsspec/s3fs, pyvo | ML, scaling, cloud access, VO queries |

Focus Astropy study on `units`, `coordinates`, `time`, `table`, `io.fits`, `wcs`,
`stats`. Install tools when a project needs them, not all at once.

## 9. Suggested 9–12 months at 8–10 hours/week

| Phase | Work | Deliverable |
|---|---|---|
| Month 1 | Relevant Python sections, environments, Git | Reproducible read/filter/plot script |
| Months 2–3 | NumPy/SciPy, Astropy, stats, MAST | Retrieve data; fit with uncertainties |
| Month 4 | Known Kepler/TESS transit | Recover signal and examine false-positive indicators |
| Months 5–6 | Microlensing physics/models | Reproduce single-lens fit; study a planetary event |
| Months 7–8 | Photometry, ASDF, Nexus | Inspect simulated Roman image; test source fluxes |
| Months 9–10 | Batch pipelines and validation | Small tested workflow with provenance |
| Months 11–12 | Research specialization | Focused study with injection–recovery and limitations |

Adjust to your mathematics/physics background and available hours. Choose a small
weekly deliverable; dates are not a promise of research readiness.

### Three substantial projects

**Known TESS planet:** use lightkurve and published parameters. Inspect quality
flags; search and fit transits; check odd/even events, secondary eclipses,
contamination, and pixel/centroid information. A periodogram peak is not enough.

**Published microlensing event:** use publicly released OGLE/KMTNet event data,
published supplemental files, or appropriate simulation material. Reproduce the
single-lens result, then examine planetary versus alternative models. Respect
release conditions/citations; not every survey event has a public full light curve.

**Injection–recovery:** insert signals into realistic data, measure recovery and
miss rates and nonplanet triggers versus brightness, cadence, blending, and event
parameters. Light-curve injections test only the stages after photometry. The tiny
practice experiment is not a survey selection-function measurement.

## 10. Where AI belongs

AI can help rank candidates, reject artifacts, classify events, initialize fits,
or approximate expensive calculations. Establish a physical-model baseline first.
Use independent stars/events for validation rather than random points from the
same light curve. Test simulated-versus-real differences and avoid preprocessing
leakage. An AI score is not planet confirmation; "99% accuracy" may hide terrible
performance on rare planets. No expensive GPU is required to start.

**Spend more time learning how measurements go wrong than collecting AI models.**
Timing errors, blending, detector artifacts, correlated noise, degeneracies, and
selection effects matter enormously. Reproduce one published analysis, including
uncertainties and alternatives, in a workflow another person can rerun.

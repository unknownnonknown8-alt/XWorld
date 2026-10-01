# What MAST + Roman + your pipeline actually means

There are three distinct layers. Do not confuse them.

## Layer 1: discover and access products

For existing MAST missions a common `astroquery.mast.Observations` pattern is:

```text
query_criteria / query_object → inspect metadata → get_product_list
→ filter_products → inspect sizes/rights → download_products
```

The runnable [MAST exercise](../practice/06_mast.py) uses **Kepler**, not fictional
Roman flight products. It first lists metadata and products; downloading a single
small light-curve product requires `--download`. Network/archive availability is
external to this repository. Never assume that changing `Kepler` to `Roman` in a
script implements Roman's current service, query schemas, or product access.

Learn target-coordinate queries, catalogs, crossmatching, data rights, units,
filters, instruments, product levels, sizes, observation/product IDs, pagination,
rate limits, interrupted downloads, and manifest files. Keep downloaded originals
unchanged. For remote/cloud data, compute near the data where possible rather than
downloading entire surveys. Later learn SQL/ADQL and pyVO for suitable services.

## Layer 2: observatory calibration

Roman WFI uses **ASDF, Roman data models, and generalized WCS**, not just FITS.
Understand metadata, quality bitmasks (not merely Boolean good/bad), uncertainty
arrays, calibration contexts and reference-file versions, detector effects, and
`romancal`. The code for WFI calibration is **not a planet-finding pipeline**.

STScI WFI processing and IPAC's high-level microlensing processing serve different
roles. IPAC plans PSF and difference photometry, light curves, quality metrics,
variability/event analyses. Daily, end-of-season, and end-of-survey products differ;
not every high-level result is immediate. Consult current handbooks for schedules.

Start with supplied calibrated products/time-series photometry when available.
You do not need to reproduce the observatory's entire calibration system.

## Layer 3: your scientific analysis

```text
Find relevant observations or supplied light curves
  → record product IDs, versions, checksums and provenance
  → inspect time format/scale/zero point, units, uncertainties and quality flags
  → extract photometry IF needed (PSF/difference methods in crowded fields)
  → model baseline/variability and detect candidate events
  → compare single-lens, binary-lens, binary-source and systematic explanations
  → search multiple parameter solutions, inspect residuals, infer uncertainties
  → injection–recovery and false-positive validation
  → candidate catalog, plots, reproducible report
```

**The demonstration implements only a small part of layer 3**, using synthetic
fluxes instead of images. It does not calibrate a detector, extract photometry,
fit a planetary model, establish a mass, or validate a candidate.

### Transition from this demo to an official simulated light curve

1. Obtain a released dataset using the current provider's instructions. Save its
   citation, dataset identifier, URL, version, license/usage conditions and checksum.
2. Read its documented column meanings. Do not guess that column 2 is flux or that
   every file is a one-filter time series.
3. Split by source and compatible bandpass. Resolve time systems before combining.
4. If converting magnitude `m` with zero point `zp`, use
   `F=10**(-0.4*(m-zp))` and, for small magnitude errors,
   `sigma_F=(ln(10)/2.5)*F*sigma_m`. Large errors require more careful likelihoods.
5. Map mission-specific DQ bits deliberately. The demo accepts only your converted
   `quality=0` for usable points. It is NOT a Roman bitmask interpreter.
6. Write a CSV with `time_days,flux,flux_err,quality`; include an external metadata
   document for the original time scale/zero point, bandpass, units and conversions.
7. Run `python -m demonstration.run --input path/to/curve.csv --output demonstration/outputs/imported`.
8. Inspect fits and boundaries; the narrow beginner model and threshold rules may
   not suit that dataset. Recalibrate them using independent validation data.

For a simulated **image**, use the Nexus examples for its product type, inspect
`roman_datamodels` and GWCS, then build/test appropriate photometry before feeding
this detector. The optional `practice/07_roman_asdf.py` is just an inspection tool.

## What makes a pipeline reliable?

- No dependence on notebook cell execution history.
- Small functions, explicit inputs, clear errors, tests and a known-answer case.
- Immutable downloaded originals; separate derived and scratch outputs.
- Saved software versions, settings, seeds, product hashes, fit status and failures.
- CRDS context and reference provenance when calibration is involved.
- Retries with limits/backoff; no silently skipped targets or fake fallback data.
- Explicit resume/cache policy; recompute when inputs, code or settings change.
- Logs/reports explaining unsuccessful fits, boundary hits, and invalid rows.
- A small reproducible command before a workflow manager.

This starter is intentionally **not production orchestration**: it reruns its
small dataset, overwrites the selected output location, and stops on an error.
It saves manifests, hashes and diagnostics but has no distributed scheduler or
resume system. Add those after understanding the individual steps.

## Validation before a scientific claim

1. Reproduce published events and competing solutions.
2. Test a wide ensemble of lens/source/systematic models, including nonplanets.
3. Calibrate false alarms across all searched times/targets/settings.
4. Perform light-curve and, where relevant, image-level injection–recovery.
5. Test correlated noise, error miscalibration, gaps and blending.
6. Model selection effects before inferring a planet population.
7. Review candidates with experienced microlensing researchers.

A single beautiful plot and a large improvement over constant flux do not establish
a planet. Here, that improvement is **constant versus single lens**, not evidence
in favor of a binary planetary lens over a single lens.

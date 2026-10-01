# Small, runnable practice exercises

Activate the root environment and run commands **from the repository root**.
Scripts are deliberately ordinary Python, with numbered steps and `TRY` comments.
You can copy one function into your own notebook or modify one exercise at a time.

| Exercise | Command | What to learn |
|---|---|---|
| 01 | `python -m practice.01_arrays` | Masks, weighted means, uncertainties, random seeds |
| 02 | `python -m practice.02_astropy` | Units, coordinates, times, ECSV, tiny synthetic FITS image |
| 03 | `python -m practice.03_simulate` | Physical microlensing simulations, CSV, separate truth |
| 04 | `python -m practice.04_fit_detect` | Single-lens fit, residuals, anomaly flag and plot |
| 05 | `python -m practice.05_injection_recovery` | Noise sensitivity, repeated trials, nonplanet triggers |
| 06 | `python -m practice.06_mast` | Online Kepler MAST metadata/product queries; no default data download |
| 07 | `python -m practice.07_roman_asdf your_image.asdf` | Optional schema-aware Roman image inspection |

**01–05 are independent and offline** after package installation. They do not need
files created by previous exercises. Generated files go in `practice/outputs/`,
which Git ignores. Exercise 05 may take longer because it repeats fitting 27 times.

## Practice questions (answer before looking at the outputs)

1. Why does `1/error**2` give a precise point more weight? What if the error is wrong?
2. Why are MJD and TDB not alternative labels for the same concept? What additional
   information is needed for barycentric light-travel-time corrections?
3. Which planetary signals disappear when cadence becomes coarse? Is lowering
   `q` guaranteed to make every light curve look like a scaled-down copy?
4. Why does a single lens fit most of a planetary event yet leave large residuals?
5. Why does the artifact trigger? What independent checks could reject it?
6. What is the difference between an observation row and a downloadable product?
7. Where are uncertainties, DQ bits and the WCS stored for your specific Roman
   product? Why should you not hardcode another mission's schema?

## MAST: opt-in download

```bash
python -m practice.06_mast
python -m practice.06_mast --download
```

The second command requests at most **one public Kepler long-cadence FITS light
curve <=5 MB**, then saves its hash and download status. This teaches real archive
access, but it is **not a Roman data access API or Roman microlensing analysis**.
Network/rate-limit/service errors exit clearly; no fake replacement data is used.
The metadata tables and query manifest are saved for inspection. The online call
is not part of offline CI tests; the file-selection logic is tested with a fixture.

## Optional Roman ASDF practice

Obtain a calibrated 2D simulated image through current Nexus/handbook instructions,
using an environment compatible with its schema. If working locally, install the
optional dependency separately:

```bash
python -m pip install roman_datamodels
python -m practice.07_roman_asdf path/to/calibrated_image.asdf
```

`roman_datamodels` is intentionally not in the core environment: Roman software and
schemas evolve, and Nexus provides matched environments. The script reports metadata,
shape, and available errors/DQ. It does not download, calibrate or alter the file.
No official Roman ASDF file is bundled, and compatibility with your product must be
checked. Exercise 02's FITS image is an artificial array, NOT a substitute Roman file.

## A simple weekly habit

- Read the script and predict the output.
- Run it unchanged once.
- Change just one setting; save a different output folder if needed.
- Explain the difference in your own words.
- Add a small test for something you learned.
- Commit and push your code; keep generated bulk data out of Git.

The next milestone is a published event reproduction, not just tuning the demo
until it labels its four handcrafted cases correctly.

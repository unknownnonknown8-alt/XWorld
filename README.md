# Roman exoplanet learning lab

A beginner-friendly path from Python to **microlensing candidate detection**.
This repository contains the learning advice requested in the conversation,
a runnable physical simulation, and small exercises you can edit independently.

**This is not a validated planet discovery pipeline.** The demonstration flags
anomalies that need follow-up. A detector artifact can trigger the same flag.
There are no Roman flight observations here and no claim of planet confirmation.

## Start here

The work is on the `genspark_ai_developer` branch in
[PR #1](https://github.com/unknownnonknown8-alt/XWorld/pull/1). To get it before merging:

```bash
git clone --branch genspark_ai_developer https://github.com/unknownnonknown8-alt/XWorld.git
cd XWorld
```

Use **Python 3.13** (the tested version). From this repository's root:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m demonstration.run
python -m pytest -q
```

The first run needs internet to install packages. The main demonstration and
exercises 01–05 then run **offline**, without NASA credentials or a GPU.
An installation with binary wheels is recommended; MulensModel's binary-lens
solver may otherwise need a C/C++ build toolchain.

Open `demonstration/outputs/latest/summary.csv` and the PNGs there. The terminal
prints each step. Re-running with the same seed reproduces observations to numerical precision
and overwrites that output folder. Change `--output` to keep another experiment:

```bash
python -m demonstration.run --seed 7 --output demonstration/outputs/seed7
python -m demonstration.run --noise 0.02 --cadence-minutes 30 \
  --output demonstration/outputs/noisier
```

## Three folders

| Folder | What is inside | Start with |
|---|---|---|
| [`demonstration`](demonstration/README.md) | Physical simulated light curves, basic fitting, anomaly detection, plots, provenance | `python -m demonstration.run` |
| [`lerning`](lerning/README.md) | Full Python-to-Roman roadmap, notebook review, resource links, pipeline design | [`roadmap.md`](lerning/roadmap.md) |
| [`practice`](practice/README.md) | Independently runnable exercises with explanations and experiments | `python -m practice.01_arrays` |

The spelling **`lerning`** is intentional, matching the request. Reusable science
functions live in `demonstration/core.py`; there is no web app or background job.

## Where do the simulations come from?

We generate them locally using **MulensModel's finite-source binary-lens model**:
a host star plus a low-mass companion, not a made-up Gaussian "planet bump".
A 72-day window, 15-minute sampling, a small gap, flux blending, and an idealized
noise law make a Roman-like *teaching* time series. These are chosen assumptions,
**not an official Roman simulator, mission specification, or sensitivity forecast**.

See the [simulation assumptions](demonstration/README.md#simulation-assumptions).
Official Roman simulation/data resources are linked in
[`lerning/resources.md`](lerning/resources.md). Older WFIRST workshop and challenge
products are distinct from today's Roman products. Some historical data download
links were unavailable when checked; this repository does not silently replace
missing official datasets with fabricated downloads.

## Next reading

1. [Review of your Python notebook and complete roadmap](lerning/roadmap.md).
2. [Exactly what the demonstration does](demonstration/README.md).
3. [Practice exercises, in order](practice/README.md).
4. [MAST, Roman formats, and reproducible pipelines](lerning/pipelines.md).
5. [Curated resources](lerning/resources.md).

The uploaded notebook was inspected (989 cells: 670 code, 319 Markdown), not fully
executed. It is not duplicated here; the review and its cell references are saved.
Large generated data, environments, downloads, and caches are excluded from Git.
Small code/document changes should be committed and pushed on a feature branch:

```bash
git add demonstration lerning practice tests README.md requirements.txt
git commit -m "feat: describe your learning experiment"
git push origin genspark_ai_developer
```

Pushing future work is a deliberate action, not an always-running automation.
This repository does not contain credentials or automatically publish your data.


## Automated checks

Run `python -m pytest -q`. Tests include known simulation cases, invalid input,
quality masks, time/flux rescaling, gaps, separate truth, CSV import, CLI outputs,
and bounded exact-target MAST product selection. Online service calls are not unit
tests. Tiny solver roundoff differences are tested with numerical tolerance rather
than bit-for-bit equality.

The connected GitHub App cannot create workflow files. A ready-to-use configuration
is saved at `tests/github_actions_example.yml`, **not active CI**. To enable it,
copy it to `.github/workflows/tests.yml` using credentials authorized to edit
workflows, then commit and push that change. No automatic GitHub test run is claimed.

# Curated resources

Prefer official documentation. Links and priorities assembled 2026-10-01; versions,
mission schedules, archive interfaces, access rules, and URLs can change. This is
not a claim that every linked page or example was executed.

## 1. Python and numerical foundations

- [Python tutorial](https://docs.python.org/3/tutorial/): functions, collections, exceptions, modules.
- [NumPy beginner guide](https://numpy.org/doc/stable/user/absolute_beginners.html): arrays and masks.
- [SciPy tutorials](https://docs.scipy.org/doc/scipy/tutorial/): especially optimize and stats.
- [Matplotlib tutorials](https://matplotlib.org/stable/tutorials/index.html): errors, subplots, images.
- [pandas user guide](https://pandas.pydata.org/docs/user_guide/index.html): tables and joins.
- [Software Carpentry lessons](https://software-carpentry.org/lessons/): shell, Git, reproducible programming.
- [Scientific Python lectures](https://lectures.scientific-python.org/): a broader scientific-computing course.

## 2. Astropy and photometry

- [Astropy learning](https://learn.astropy.org/): project-driven astronomy tutorials.
- [Astropy documentation](https://docs.astropy.org/en/stable/): units, coordinates, times, tables, FITS, WCS, stats.
- [Astropy time](https://docs.astropy.org/en/stable/time/): understand formats/scales before combining data.
- [Photutils](https://photutils.readthedocs.io/en/stable/): background estimation, aperture and PSF photometry.
- [GWCS](https://gwcs.readthedocs.io/en/latest/): generalized world-coordinate transformations used with Roman.

## 3. MAST and introductory exoplanet data

- [MAST portal](https://mast.stsci.edu/): discover data interactively first.
- [MAST documentation](https://mast.stsci.edu/api/v0/): service reference.
- [astroquery MAST observations](https://astroquery.readthedocs.io/en/latest/mast/mast_obsquery.html): metadata → products → filtering → download.
- [Lightkurve tutorials](https://lightkurve.github.io/lightkurve/tutorials/index.html): Kepler/TESS projects, not a Roman microlensing loader.
- [Astropy BoxLeastSquares](https://docs.astropy.org/en/stable/timeseries/bls.html): transit searches, NOT microlensing detection.
- [batman](https://lkreidberg.github.io/batman/docs/html/index.html): physical transit models.
- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/): published systems and comparison values.
- [Gaia archive](https://gea.esac.esa.int/archive/): astrometry/catalog crossmatching.
- [pyVO](https://pyvo.readthedocs.io/en/latest/): later, TAP/VO interfaces and ADQL.

## 4. Roman: current authoritative starting points

- [NASA Roman](https://science.nasa.gov/mission/roman-space-telescope/): mission scope and updates.
- [Galactic Bulge Time-Domain Survey](https://science.nasa.gov/mission/roman-space-telescope/galactic-bulge-time-domain-survey/): the science context for this project.
- [Roman Research Nexus](https://roman.science.stsci.edu/): simulated datasets, software, notebooks, cloud compute. Early access uses a MyST account; quotas/support policies apply.
- [Nexus guide](https://roman-docs.stsci.edu/data-handbook/roman-research-nexus): access and workflow details.
- [STScI Roman Data Handbook](https://roman-docs.stsci.edu/data-handbook): WFI data, formats, calibration, archive context.
- [IPAC Roman Data Handbook](https://roman-docs.ipac.caltech.edu/data-handbook): SSC products and science processing.
- [Galactic bulge pipelines](https://roman-docs.ipac.caltech.edu/data-handbook/roman-wfi-data-pipelines/galactic-bulge-survey-pipelines): PSF/difference photometry, light curves, events, delivery modes.
- [Roman data models](https://roman-datamodels.readthedocs.io/en/latest/): schema-aware access rather than assuming FITS HDUs.
- [ASDF](https://asdf.readthedocs.io/en/latest/): structured data and metadata.
- [romancal](https://roman-pipeline.readthedocs.io/en/latest/): WFI calibration; not planet finding.
- [CRDS](https://hst-crds.stsci.edu/static/users_guide/index.html): calibration reference files and contexts.
- [STPSF](https://stpsf.readthedocs.io/en/latest/): telescope PSFs; only when you reach image-level projects.

### Historical WFIRST material: useful, but distinguish its provenance

- [IPAC exoplanet data challenges](https://roman.ipac.caltech.edu/page/exoplanet-data-challenges-html): archived challenges (closed), including a 293-light-curve microlensing challenge with mixed source classes. Old survey/filter assumptions are not current specifications.
- [IPAC microlensing notebook page](https://roman.ipac.caltech.edu/page/microlensing-python-notebook-tutorial): explains a **2017 Sagan workshop** sample; it explicitly says the example is **not** the official challenge dataset. Its notebook originally targeted Python 2.7.
- The old `https://roman.ipac.caltech.edu/sims/WFIRST_1827.dat` download returned **404** when checked here. The linked `microlensing-source.org/data-challenge/` page was also unavailable. Do not build a new pipeline around these unverified legacy download paths. Follow the maintained IPAC/Nexus entry points or ask their support for archival material.

The runnable demonstration in this repository is independently generated physical
simulation, not any of these archival products. No official completeness/sensitivity
claim can be inferred from its simple cadence and noise assumptions.

## 5. Microlensing and inference

- [MulensModel documentation](https://rpoleski.github.io/MulensModel/): start with Model, MulensData, and Event.
- [MulensModel source/examples](https://github.com/rpoleski/MulensModel): worked examples and solver methods; cite the package and algorithms as requested by its authors in research.
- [IPAC MulensModel introduction](https://roman.ipac.caltech.edu/page/mulensmodel-sim-html): mission-oriented modelling introduction.
- [pyLIMA](https://github.com/ebachelet/pyLIMA): alternative microlensing framework; choose one initially.
- [2017 Sagan workshop](https://nexsci.caltech.edu/workshop/2017/): microlensing lectures and hands-on context, with historical caveats.
- [OGLE](https://ogle.astrouw.edu.pl/): public releases/event pages where available.
- [KMTNet](https://kmtnet.kasi.re.kr/): survey context and public materials where released.
- [emcee](https://emcee.readthedocs.io/en/stable/): posterior sampling, not automatic global optimization.
- [corner](https://corner.readthedocs.io/en/latest/): parameter correlations; plots alone do not prove convergence.

## 6. Reproducible engineering and later scaling

- [pytest](https://docs.pytest.org/en/stable/): known-answer tests and regression checks.
- [Git book](https://git-scm.com/book/en/v2): branches, commits, reproducible collaboration.
- [Snakemake tutorial](https://snakemake.readthedocs.io/en/stable/tutorial/tutorial.html): add once plain scripts are clear.
- [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): leakage, preprocessing, randomness.
- [Dask](https://docs.dask.org/en/stable/): only when memory/workload justifies it.
- [fsspec](https://filesystem-spec.readthedocs.io/en/latest/): filesystem-style remote access.

No need for Kubernetes, an LLM, or a GPU cluster to complete the first projects.

"""Offline known-answer, validation and no-truth-leakage tests."""

import importlib
import inspect
import json
import subprocess
import sys

import numpy as np
import pytest
from astropy.table import Table

from demonstration import ROOT
from demonstration.core import (analyze_light_curve, magnification,
                                longest_residual_run, prepare_light_curve, read_light_curve)
from demonstration.run import output_directory
from demonstration.simulate import simulate_light_curve


@pytest.mark.parametrize("seed", [42, 7])
@pytest.mark.parametrize("kind,decision", [("planet", "anomaly_candidate"),
                                          ("single", "single_lens_like"),
                                          ("flat", "no_event_candidate"),
                                          ("artifact", "anomaly_candidate")])
def test_known_cases(seed, kind, decision):
    raw = simulate_light_curve(kind, seed, cadence_minutes=30)
    time, flux, error, _ = prepare_light_curve(*raw[:4])
    result, prediction, residual = analyze_light_curve(time, flux, error)
    assert result["decision"] == decision
    assert np.all(np.isfinite(prediction))
    np.testing.assert_allclose(residual, (flux - prediction) / error)


def test_magnification_symmetry_and_baseline():
    np.testing.assert_allclose(magnification(np.array([-2, 2]), 0, 0.1, 10),
                               magnification(np.array([2, -2]), 0, 0.1, 10))
    assert magnification(1e6, 0, 0.1, 10) == pytest.approx(1)


def test_seed_reproducible():
    first, second = simulate_light_curve(), simulate_light_curve()
    for a, b in zip(first[:4], second[:4]):
        # The binary-lens solver can differ at machine roundoff (~1e-16).
        np.testing.assert_allclose(a, b, rtol=1e-12, atol=1e-12)


def test_detector_accepts_no_labels():
    assert list(inspect.signature(analyze_light_curve).parameters) == ["time", "flux", "error"]


def test_quality_masks_without_clipping_anomaly():
    t = np.arange(40.0)
    f, e, q = np.ones(40), np.full(40, 0.1), np.zeros(40)
    f[2], e[3], q[4], f[5] = np.nan, 0, 1, 100
    time, flux, error, report = prepare_light_curve(t[::-1], f[::-1], e[::-1], q[::-1])
    assert report["removed_rows"] == 3
    assert np.max(flux) == 100  # a large unflagged anomaly must survive
    assert np.all(np.diff(time) > 0)
    assert np.all(error > 0)


def test_duplicates_and_bad_shapes():
    with pytest.raises(ValueError, match="unique"):
        prepare_light_curve(np.zeros(40), np.ones(40), np.ones(40), np.zeros(40))
    with pytest.raises(ValueError, match="equal-length"):
        prepare_light_curve(np.arange(40), np.ones(39), np.ones(40), np.zeros(40))
    with pytest.raises(ValueError, match="at least 30"):
        prepare_light_curve(np.arange(40), np.ones(40), np.ones(40), np.ones(40))


def test_gaps_and_sign_changes_break_runs():
    time = np.array([0, 1, 2, 10, 11, 12, 13, 14], dtype=float)
    run = longest_residual_run(time, np.array([4, 4, 4, 4, 4, 4, -4, -4]))
    assert run["points"] == 3
    assert run["start_days"] == 0
    assert longest_residual_run(time, np.zeros(8))["points"] == 0


@pytest.mark.parametrize("kwargs", [{"noise": 0}, {"noise": float("nan")},
                                    {"cadence_minutes": 0}, {"seed": -1}, {"kind": "unknown"}])
def test_invalid_simulation_settings(kwargs):
    with pytest.raises(ValueError):
        simulate_light_curve(**kwargs)


def test_csv_contract(tmp_path):
    path = tmp_path / "wrong.csv"
    path.write_text("time,brightness\n1,2\n")
    with pytest.raises(ValueError, match="CSV needs"):
        read_light_curve(path)


def test_output_protection():
    with pytest.raises(ValueError, match="outputs"):
        output_directory(ROOT / "demonstration")
    with pytest.raises(ValueError, match="outputs"):
        output_directory(ROOT.parent / "outputs")


def test_mast_selection_is_bounded_and_public():
    select = importlib.import_module("practice.06_mast").choose_small_light_curves
    table = Table({"productFilename": ["a_llc.fits", "b_llc.fits", "c_llc.fits", "pixel.fits"],
                   "size": [100, 6_000_000, 100, 100],
                   "dataRights": ["PUBLIC", "PUBLIC", "EXCLUSIVE_ACCESS", "PUBLIC"]})
    chosen = select(table)
    assert list(chosen["productFilename"]) == ["a_llc.fits"]


def test_cli_end_to_end(tmp_path):
    # pytest's configured basetemp is inside this repository.
    out = tmp_path / "outputs"
    subprocess.run([sys.executable, "-m", "demonstration.run", "--cadence-minutes", "30",
                    "--output", str(out)], check=True, cwd=ROOT, capture_output=True, text=True)
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["status"] == "complete"
    assert len(manifest["inputs"]) == 4
    assert len(list(out.glob("*.png"))) == 4
    truth = json.loads((out / "simulation_truth.json").read_text())
    assert truth["event_001"]["kind"] == "planet"
    result = json.loads((out / "event_001_result.json").read_text())
    assert result["decision"] == "anomaly_candidate"
    # Import must not depend on labels or the simulation_truth file.
    (out / "simulation_truth.json").unlink()
    imported = tmp_path / "outputs/imported"
    subprocess.run([sys.executable, "-m", "demonstration.run", "--input", str(out / "event_001.csv"),
                    "--output", str(imported)], check=True, cwd=ROOT, capture_output=True, text=True)
    assert json.loads((imported / "event_001_result.json").read_text())["decision"] == "anomaly_candidate"


@pytest.mark.parametrize("option,value", [("--noise", "nan"), ("--noise", "0"),
                                         ("--cadence-minutes", "inf"), ("--seed", "-1")])
def test_cli_bad_settings_fail_cleanly(tmp_path, option, value):
    completed = subprocess.run([sys.executable, "-m", "demonstration.run", option, value,
                                "--output", str(tmp_path / "outputs")],
                               cwd=ROOT, capture_output=True, text=True)
    assert completed.returncode != 0
    assert "Traceback" not in completed.stderr


def test_missing_input_records_failure(tmp_path):
    out = tmp_path / "outputs"
    completed = subprocess.run([sys.executable, "-m", "demonstration.run",
                                "--input", str(tmp_path / "missing.csv"), "--output", str(out)],
                               cwd=ROOT, capture_output=True, text=True)
    assert completed.returncode != 0
    assert json.loads((out / "manifest.json").read_text())["status"] == "failed"


def test_mast_cone_search_excludes_neighboring_targets():
    select = importlib.import_module("practice.06_mast").select_kepler10
    observations = Table({"obs_collection": ["Kepler", "Kepler", "TESS"],
                          "target_name": ["kplr011904151", "kplr011904148", "kplr011904151"]})
    assert len(select(observations)) == 1
    assert select(observations)[0]["target_name"] == "kplr011904151"


def test_flux_and_time_reference_invariance():
    raw = simulate_light_curve("single", seed=42, cadence_minutes=30)
    time, flux, error, _ = prepare_light_curve(*raw[:4])
    result, prediction, _ = analyze_light_curve(time, flux, error)
    t2, f2, e2, _ = prepare_light_curve(raw[0] + 2460000, raw[1] * 1000,
                                       raw[2] * 1000, raw[3])
    shifted, prediction2, _ = analyze_light_curve(t2, f2, e2)
    assert shifted["decision"] == result["decision"]
    np.testing.assert_allclose(prediction, prediction2, rtol=1e-6, atol=1e-6)
    fit = result["fit"]["parameters"]
    assert abs(fit["t0_days"]) < 0.03
    assert fit["u0"] == pytest.approx(0.15, rel=0.1)
    assert fit["tE_days"] == pytest.approx(12.0, rel=0.1)

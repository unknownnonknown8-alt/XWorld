"""Run the whole small pipeline: python -m demonstration.run --help."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")  # Save PNGs without needing a window or desktop.
import matplotlib.pyplot as plt
import numpy as np

from . import ROOT
from .core import analyze_light_curve, read_light_curve
from .simulate import simulate_light_curve


def write_json(path, content):
    Path(path).write_text(json.dumps(content, indent=2, allow_nan=False) + "\n")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def output_directory(path):
    """Keep generated data inside the project and out of tracked source folders."""
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT) or "outputs" not in path.relative_to(ROOT).parts:
        raise ValueError("Output must be inside this repository in an outputs/ directory.")
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_plot(path, time, flux, error, prediction, residual, result):
    """Observations above; standardized residuals below, with an anomaly zoom."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), constrained_layout=True)
    axes[0].errorbar(time, flux, yerr=error, fmt=".", ms=1.5, alpha=0.35,
                     color="slateblue", label="Observed flux with uncertainties")
    axes[0].plot(time, prediction, color="darkorange", lw=1.5, label="Best single-lens fit")
    axes[0].set(ylabel="Rescaled flux", title=f"{path.stem}: {result['decision']}")
    axes[0].legend()
    run = result["longest_residual_run"]
    for ax in axes[1:]:
        ax.plot(time, residual, ".", ms=2, color="slateblue")
        ax.axhline(0, color="black", lw=0.7)
        for level in (-3, 3):
            ax.axhline(level, color="darkorange", ls="--", lw=0.8)
        ax.set(xlabel="Input time (days; see input metadata)", ylabel="Residual / uncertainty")
        if run["points"] >= 5:
            ax.axvspan(run["start_days"], run["end_days"], color="orange", alpha=0.2)
    center = float(time[np.argmax(np.abs(residual))])
    axes[2].set_xlim(center - 0.75, center + 0.75)
    axes[2].set_title("Zoom near the largest residual (not a planetary fit)")
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="One-source, one-band CSV; otherwise simulate four cases.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--noise", type=float, default=0.005)
    parser.add_argument("--cadence-minutes", type=float, default=15.0)
    parser.add_argument("--output", type=Path, default=ROOT / "demonstration/outputs/latest")
    args = parser.parse_args()
    # Validate before serializing settings: JSON must never contain NaN/Infinity.
    if not np.isfinite(args.noise) or args.noise <= 0:
        parser.error("--noise must be finite and positive.")
    if not np.isfinite(args.cadence_minutes) or not 5 <= args.cadence_minutes <= 120:
        parser.error("--cadence-minutes must be finite and between 5 and 120.")
    if args.seed < 0:
        parser.error("--seed must be nonnegative.")
    try:
        # Step 1: create inputs OR accept an existing CSV. Never use truth to fit.
        out = output_directory(args.output)
        if args.input and args.input.resolve().is_relative_to(out):
            raise ValueError("Input must be outside this output directory to protect originals.")
        manifest_path = out / "manifest.json"
        # Mark in-progress first so an interrupted rerun cannot look completed.
        manifest = {"status": "running", "started_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "mode": "import" if args.input else "simulation",
                    "settings": {"seed": args.seed, "noise": args.noise,
                                 "cadence_minutes": args.cadence_minutes},
                    "packages": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
                    "source_sha256": {p.name: sha256(p) for p in Path(__file__).parent.glob("*.py")}}
        try:
            revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
            manifest["git_commit"] = revision.stdout.strip() or "unavailable"
        except FileNotFoundError:
            manifest["git_commit"] = "unavailable (Git not installed)"
        write_json(manifest_path, manifest)
        if args.input:
            print("Step 1: using your CSV; no simulation or hidden truth.")
            paths = [args.input.resolve()]
        else:
            print("Step 1: generating four Roman-like teaching light curves (not official products).")
            paths, truth = [], {}
            for i, kind in enumerate(("planet", "single", "flat", "artifact"), start=1):
                time, flux, error, quality, known = simulate_light_curve(
                    kind, args.seed + i - 1, args.noise, args.cadence_minutes)
                path = out / f"event_{i:03d}.csv"
                np.savetxt(path, np.column_stack((time, flux, error, quality)), delimiter=",",
                           header="time_days,flux,flux_err,quality", comments="",
                           fmt=["%.10f", "%.12g", "%.12g", "%d"])
                paths.append(path)
                truth[path.stem] = known
            write_json(out / "simulation_truth.json", truth)

        # Steps 2–5: work only with observable columns, regardless of their source.
        rows, inputs = [], []
        for path in paths:
            print(f"Step 2: read, validate, quality-mask and sort {path.name}.")
            time, flux, error, quality_report = read_light_curve(path)
            print(f"        {quality_report['used_rows']} usable; {quality_report['removed_rows']} removed.")
            print("Step 3: fit a single lens, then compare against constant flux.")
            result, prediction, residual = analyze_light_curve(time, flux, error)
            result["quality_report"] = quality_report
            print("Step 4: look for same-sign residual runs; gaps break a run.")
            print(f"        {result['decision']} (not planet confirmation)")
            print("Step 5: save diagnostics and machine-readable fit results.")
            name = path.stem
            write_json(out / f"{name}_result.json", result)
            save_plot(out / f"{name}.png", time, flux, error, prediction, residual, result)
            np.savetxt(out / f"{name}_fit.csv", np.column_stack((time, flux, error, prediction, residual)),
                       delimiter=",", header="time_days,scaled_flux,scaled_error,single_lens_flux,residual_sigma",
                       comments="")
            rows.append({"event_id": name, "decision": result["decision"],
                         "delta_chi2_constant_to_single": result["delta_chi2_constant_to_single"],
                         "reduced_chi2_single": result["reduced_chi2_single_lens"],
                         "longest_run_points": result["longest_residual_run"]["points"]})
            inputs.append({"path": str(path), "sha256": sha256(path)})
        with (out / "summary.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        manifest.update(status="complete", inputs=inputs)
        write_json(manifest_path, manifest)
        print(f"Step 6: complete. Open {out / 'summary.csv'} and the PNG plots.")
        if not args.input:
            print("Now inspect simulation_truth.json: the artifact can also trigger. No planets confirmed.")
    except (ValueError, OSError, RuntimeError) as exc:
        # No fabricated fallback results when input, optimization or writing fails.
        if "manifest_path" in locals() and "manifest" in locals():
            manifest.update(status="failed", error=str(exc))
            try:
                write_json(manifest_path, manifest)
            except OSError:
                pass  # Report the original error even if the output is not writable.
        parser.exit(1, f"Pipeline failed: {exc}\n")


if __name__ == "__main__":
    main()

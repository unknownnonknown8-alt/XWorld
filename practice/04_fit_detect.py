"""Practice fitting and residual screening. Offline; no earlier exercise needed."""

from demonstration import ROOT
from demonstration.simulate import simulate_light_curve
from demonstration.core import prepare_light_curve, analyze_light_curve
from demonstration.run import save_plot, write_json


def main():
    out = ROOT / "practice/outputs/04_fit_detect"
    out.mkdir(parents=True, exist_ok=True)
    # Step 1: generate independent inputs, then deliberately discard truth.
    time, flux, error, quality, _ = simulate_light_curve("planet", seed=42)
    time, flux, error, report = prepare_light_curve(time, flux, error, quality)
    # Step 2: the same public functions are used by the complete demonstration.
    result, prediction, residual = analyze_light_curve(time, flux, error)
    # Step 3: judge the residuals, not just how nice the overall fit looks.
    save_plot(out / "fit.png", time, flux, error, prediction, residual, result)
    write_json(out / "result.json", result)
    print(report)
    print("Decision:", result["decision"])
    print("Longest run:", result["longest_residual_run"])
    print("Plot:", out / "fit.png")
    # TRY: change planet to artifact. Why can both be anomaly candidates?


if __name__ == "__main__":
    main()

"""Optional: inspect YOUR calibrated 2D Roman ASDF image, without modifying it."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="Locally downloaded, schema-compatible Roman ASDF image.")
    args = parser.parse_args()
    if not args.file.is_file():
        parser.error("Supply an existing file obtained using current Roman/Nexus instructions.")
    try:
        import roman_datamodels as rdm
    except ImportError:
        parser.exit(1, "Optional dependency missing: python -m pip install roman_datamodels\n"
                       "Prefer the Nexus environment matching your dataset/schema version.\n")
    # Step 1: use the Roman model, not FITS assumptions or hardcoded ASDF tree paths.
    with rdm.open(args.file) as model:
        print("Model class:", type(model).__name__)
        print("Metadata:", model.meta)
        # Step 2: this exercise accepts calibrated images, not arbitrary raw products.
        if not hasattr(model, "data") or model.data.ndim != 2:
            parser.error("Expected a calibrated 2D image; consult this product's data model.")
        print("Image shape:", model.data.shape, "dtype:", model.data.dtype)
        # Step 3: inspect available errors/DQ; do not assign meanings to bits here.
        for name in ("err", "dq"):
            if hasattr(model, name):
                print(name, "shape:", getattr(model, name).shape)
    print("Read only: no calibration, photometry, download, or planet detection performed.")


if __name__ == "__main__":
    main()

"""Online MAST practice using Kepler, not Roman. Downloads are opt-in and bounded."""

import argparse
from pathlib import Path

from demonstration import ROOT
from demonstration.run import sha256, write_json
from astropy import units as u
from astroquery.mast import Observations
import numpy as np


def select_kepler10(observations):
    """A cone search also returns neighbors: require Kepler-10 = KIC 11904151."""
    mask = ((observations["obs_collection"] == "Kepler") &
            (observations["target_name"] == "kplr011904151"))
    return observations[mask]


def choose_small_light_curves(products):
    """Select public Kepler long-cadence light curves below 5 MB each."""
    names = np.asarray(products["productFilename"], dtype=str)
    sizes = np.asarray(products["size"], dtype=float)
    public = np.asarray(products["dataRights"], dtype=str) == "PUBLIC"
    mask = np.char.endswith(names, "_llc.fits") & (sizes > 0) & (sizes <= 5_000_000) & public
    return products[mask][:1]  # At most ONE file, no accidental bulk download.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download at most one public file, <=5 MB.")
    args = parser.parse_args()
    out = ROOT / "practice/outputs/06_mast"
    out.mkdir(parents=True, exist_ok=True)
    Observations.TIMEOUT = 45
    try:
        # Step 1: discover observations near a known planet host.
        print("Querying MAST around Kepler-10; internet is required.")
        observations = Observations.query_object("Kepler-10", radius=0.02 * u.deg)
        kepler = select_kepler10(observations)
        kepler.write(out / "observations.ecsv", overwrite=True)
        if len(kepler) == 0:
            raise RuntimeError("No Kepler observations returned. Inspect MAST interactively.")
        print(kepler[["obsid", "target_name", "obs_collection"]][:5])
        # Step 2: list products for at most five observations, not the whole archive.
        products = Observations.get_product_list(kepler[:5])
        products.write(out / "products.ecsv", overwrite=True)
        chosen = choose_small_light_curves(products)
        if len(chosen) == 0:
            raise RuntimeError("No suitable public <=5 MB long-cadence file in these observations.")
        print(chosen[["productFilename", "size", "dataURI"]])
        record = {"mission": "Kepler (not Roman)", "target_query": "Kepler-10",
                  "radius_deg": 0.02, "catalog_id": "KIC 11904151", "download_requested": args.download,
                  "product": {key: str(chosen[0][key]) for key in
                              ("obsID", "productFilename", "dataURI", "size")}}
        # Step 3: an explicit flag authorizes one bounded download.
        if args.download:
            manifest = Observations.download_products(chosen, download_dir=str(out), mrp_only=False)
            manifest.write(out / "download_manifest.ecsv", overwrite=True)
            if any(str(status) != "COMPLETE" for status in manifest["Status"]):
                raise RuntimeError(f"Download did not complete: {manifest}")
            path = Path(str(manifest["Local Path"][0]))
            record["download"] = {"path": str(path), "sha256": sha256(path)}
            print("Downloaded:", path)
        else:
            print("Metadata only. Add --download to fetch the selected file.")
        write_json(out / "query_manifest.json", record)
    except Exception as exc:
        # External APIs may fail/change. Fail clearly instead of pretending to succeed.
        parser.exit(1, f"MAST exercise failed: {exc}\nNo simulated fallback was substituted.\n")


if __name__ == "__main__":
    main()

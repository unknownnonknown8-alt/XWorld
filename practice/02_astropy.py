"""Practice units, coordinates, time, tables and FITS. Offline synthetic data."""

from demonstration import ROOT  # Set local cache directories before Astropy imports.
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.table import Table
from astropy.io import fits
import numpy as np


def main():
    out = ROOT / "practice/outputs/02_astropy"
    out.mkdir(parents=True, exist_ok=True)
    # Step 1: attach units; a 15-minute cadence is a fraction of a day.
    cadence = 15 * u.minute
    print("Cadence in days:", cadence.to(u.day))
    # Step 2: coordinate frames are not interchangeable numbers.
    position = SkyCoord(ra=270 * u.deg, dec=-30 * u.deg, frame="icrs")
    print("Galactic coordinates:", position.galactic)
    # Step 3: MJD is a format and UTC is a scale; label both explicitly.
    times = Time([60000, 60000.01], format="mjd", scale="utc")
    print("UTC ISO:", times.iso)
    print("TDB JD:", times.tdb.jd)
    print("This scale conversion is NOT a barycentric light-travel-time correction.")
    # Step 4: ECSV preserves units and metadata that bare CSV does not.
    table = Table({"time_mjd": times.mjd * u.day, "flux": [1.0, 1.01] * u.Jy})
    table.meta["time_scale"] = "utc"
    table.write(out / "table.ecsv", overwrite=True)
    print(Table.read(out / "table.ecsv"))
    # Step 5: a tiny artificial image teaches FITS I/O. It is NOT a Roman image.
    image = np.random.default_rng(42).normal(100, 5, (32, 32))
    hdu = fits.PrimaryHDU(image)
    hdu.header["BUNIT"] = "adu"
    hdu.header["ORIGIN"] = "Synthetic teaching example, not Roman data"
    hdu.writeto(out / "toy_image.fits", overwrite=True)
    with fits.open(out / "toy_image.fits") as hdus:
        print("Image shape:", hdus[0].data.shape, "unit:", hdus[0].header["BUNIT"])
    # TRY: convert cadence to seconds; change the sky position; inspect the header.


if __name__ == "__main__":
    main()

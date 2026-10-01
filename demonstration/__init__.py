"""Beginner microlensing lab: physical simulation, not planet confirmation."""

import os
from pathlib import Path

# Keep caches local. This also works on machines without a graphical desktop.
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))

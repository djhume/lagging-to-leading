"""repro.py — shared plumbing for the reactive-power replication notebooks.

This module holds ONLY the boring, repeated machinery — file paths, the house
plotting style, the lines-company name lookups, and a couple of tiny formatting
helpers. Everything that is part of the *analysis* (how a trend is measured, how
the organic share is estimated, how the physics is computed) lives visibly inside
the notebooks, so a reader can audit it without opening this file.

Design rule (so the notebooks stay honest and portable):
  - No analytical decisions are hidden here.
  - Sign convention, used everywhere:  Q < 0  =  leading / capacitive.
  - Data paths resolve to a local stage if one exists (the production data lives on
    a network mount that is slow for batch reads), else the bundled project data.

The notebooks import this with `import repro`.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# replication/repro.py  ->  parents[1] == the power-factor project root.
PROJECT = Path(__file__).resolve().parents[1]
REPLICATION = PROJECT / "replication"
CACHE = REPLICATION / "cache"          # analysis-ready intermediates built by notebook 00
FIGURES = REPLICATION / "figures"      # publication figures saved by the notebooks
CACHE.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

# A local stage is used when the network mount is slow/flaky for batch reads.
_STAGE = Path(os.environ.get("PF_STAGE", "/tmp/pf_stage"))


def processed_dir() -> Path:
    """Where the cleaned per-year EMI GXP parquet files live (1997-2025).

    Prefers the local stage if it has the files (fast, mount-independent); falls
    back to the bundled project data. Override with PF_PROCESSED_DIR.
    """
    override = os.environ.get("PF_PROCESSED_DIR")
    if override:
        return Path(override)
    staged = _STAGE / "processed"
    if staged.exists() and any(staged.glob("*_power_factor_gxps.parquet")):
        return staged
    return PROJECT / "data" / "processed"


def comcom_parquet() -> Path:
    """The Commerce Commission information-disclosure parquet (tidy long form)."""
    override = os.environ.get("PF_COMCOM_PARQUET")
    if override:
        return Path(override)
    staged = _STAGE / "comcom.parquet"
    if staged.exists():
        return staged
    return PROJECT / "data" / "metadata" / "comcom_edb_disclosure_2025.parquet"


# Make the project's edb_mapping importable (the canonical EMI-code -> EDB lookup).
sys.path.insert(0, str(PROJECT / "data" / "metadata"))
from edb_mapping import EDB_CODES, NON_EDB_CODES  # noqa: E402

# Commerce-Commission display name -> EMI 4-char network code. Explicit (not fuzzy)
# so the join can never silently mis-map a lines company. Mirrors the project scripts.
COMCOM_TO_EMI = {
    "The Power Company": "TPCO", "OtagoNet": "OTPO", "Centralines": "CHBP",
    "The Lines Company": "LINE", "Buller Electricity": "BUEL", "Scanpower": "SCAN",
    "Network Waitaki": "WATA", "Firstlight Network": "EAST", "Westpower": "WPOW",
    "Northpower": "NPOW", "Alpine Energy": "ALPE", "Marlborough Lines": "MARL",
    "MainPower NZ": "MPOW", "Top Energy": "TOPE", "Horizon Networks": "HEDL",
    "Waipa Networks": "WAIP", "EA Networks": "EASH", "Powerco": "POCO",
    "Network Tasman": "TASM", "Electra": "ELEC", "Counties Energy": "COUP",
    "Aurora Energy": "DUNE", "Unison Networks": "HAWK", "WEL Networks": "WAIK",
    "Orion NZ": "ORON", "Vector Lines": "VECT", "Wellington Electricity": "CKHK",
    "Nelson Electricity": "NELS", "Electricity Invercargill": "ELIN",
}


def edb_name(code: str) -> str:
    """Human-readable lines-company name from an EMI network code."""
    return EDB_CODES.get(code, {}).get("name", code)


# ---------------------------------------------------------------------------
# House plotting style (EA palette) — cosmetic only
# ---------------------------------------------------------------------------
EA_BLUE = "#003366"
GREEN = "#2ca02c"     # clean / organic
RED = "#d62728"       # cable / network
ORANGE = "#ff7f0e"    # mixed / transitional
PURPLE = "#9467bd"    # DER
BROWN = "#8c2d04"     # deep-leading


def set_style():
    """Apply the house matplotlib style. Call once near the top of a notebook."""
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 400,
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.titlecolor": EA_BLUE,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "figure.facecolor": "white",
    })


# ---------------------------------------------------------------------------
# Tiny formatting helpers (presentation only)
# ---------------------------------------------------------------------------
def lead_lag(q: float) -> str:
    """Word for the sign of a reactive value (our convention: Q<0 = leading)."""
    if q < 0:
        return "leading (capacitive)"
    if q > 0:
        return "lagging (inductive)"
    return "balanced"


def signed(x: float, unit: str = "", dp: int = 0) -> str:
    """'+673 MVAr' style string with an explicit sign."""
    return f"{x:+,.{dp}f}{(' ' + unit) if unit else ''}"

#!/usr/bin/env python3
"""ICP-count regression - decisive check #1 of the proxy decomposition (6 Aug 2026).

SUPERSEDED same evening by icp_regression.ipynb (canonical, now a 91-assertion battery,
adds the 8 Aug panel rebase, the 10 Aug cluster inference, leave-one-out and the figure).
This script is kept only as provenance of the FIRST run.

  *** IT DOES NOT OWN ANY SHIPPED ARTEFACT. ***  (clarified 24 Aug 2026, Pass E)

  icp_regression_results_20260806.json and icp_per_poc_20260806.csv are written by the
  NOTEBOOK, which is the canonical generator: it emits 18 top-level keys where this script
  emits 9, and the two sets are not nested either way. The notebook's extra keys include
  cluster_inference_20260810, which ../../replication/src/07_anzsic_class_split.py reads to
  draw Fig. 6's pooled row, and the corrected `consistency` string. To avoid any chance of
  this script standing in for the notebook, its outputs are now written under
  *_legacy_firstrun names and it no longer writes to either shipped filename.

  Three dead paths were also repaired here (all three made the script un-runnable, which is
  why the collision had never actually fired): the ICP input defaulted to a /tmp session
  scratchpad belonging to a different project, ROOT was HERE.parents[5] (= $HOME) where the
  notebook correctly uses parents[4], and screen_by_gxp_year.csv was read from this directory
  where it has never lived. Inputs now resolve exactly as the notebook resolves them; the
  archived data_raw/icp_by_rootnsp_20260806.csv.gz was verified frame-equal to the scratchpad
  CSV this script originally consumed.

Tests: does the 2013-25 rise in overnight net leading vars scale with the number
of connections behind each GXP? Device-fleet story predicts a slope of roughly
100-200 VAr per household (band widened to 50-400 VAr/ICP for net-vs-gross and
the commercial ICP mix). A GXP-level metering artefact predicts NO scaling with
connection count (the mean-only null M0).

PRE-REGISTERED decision rule (set before results were computed):
  SUPPORTED    - beta > 0, 95% bootstrap CI excludes 0, beta in [50, 400] VAr/ICP,
                 and M1 R-squared > 0.15.
  ARTEFACT-FAVOURED - CI includes 0 / R-squared ~ 0.
  Otherwise inconclusive.

Data:
  ICP counts: EMI Retail/Datasets/MarketStructure/20260630_MarketShareTrendsByRootNSP.csv
              (downloaded 6 Aug 2026; monthly ICP count by root NSP x retailer,
              Dec 2003 - Jun 2026; root NSP = POC+network+suffix, ICPs summed per POC).
  Screen:     screen_by_gxp_year.csv (clients/ea/harmonics/consultation-2026/analysis/
              resonance-screen/; night-median net leading MVAr).
  Flags:      power-factor replication cache contamination_flag.csv (clean cohort).

Outputs (this directory, legacy names - NOT the shipped artefacts):
  icp_per_poc_20260806_legacy_firstrun.csv, icp_regression_results_20260806_legacy_firstrun.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]  # gridlytics repo root (parents[5] was $HOME - fixed 24 Aug 2026)
ICP_SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    HERE / "data_raw" / "icp_by_rootnsp_20260806.csv.gz")   # the archived copy of the
    # session-scratchpad CSV the 6 Aug run consumed (verified frame-equal, 24 Aug 2026)

rng = np.random.default_rng(20260806)

# ---- build per-POC ICP counts for calendar 2013 and 2025 ----
icp = pd.read_csv(ICP_SRC)
icp = icp[icp["Region"].astype(str).str.len() == 13].copy()  # drop 226 malformed/aggregate rows
icp["poc"] = icp["Region"].str[:7]
icp["month"] = pd.to_datetime(icp["Month ended"])
icp["year"] = icp["month"].dt.year
per_poc_month = icp.groupby(["poc", "month"], as_index=False)["ICP count"].sum()
per_poc_month["year"] = per_poc_month["month"].dt.year
yr = (per_poc_month[per_poc_month.year.isin([2013, 2025])]
      .groupby(["poc", "year"])["ICP count"].mean().unstack())
yr.columns = ["N2013", "N2025"]
yr["dN"] = yr.N2025 - yr.N2013
yr["Nbar"] = (yr.N2013 + yr.N2025) / 2
yr.round(0).to_csv(HERE / "icp_per_poc_20260806_legacy_firstrun.csv")

# ---- screen panel: clean cohort, balanced 2013 & 2025, night-median rise ----
SCREEN = ROOT / "clients/ea/harmonics/consultation-2026/analysis/resonance-screen"
scr = pd.read_csv(SCREEN / "screen_by_gxp_year.csv")   # where it actually lives
fl = pd.read_csv(ROOT / "clients/ea/power-factor/replication/cache/contamination_flag.csv")
piv = scr.pivot_table(index="gxp_code", columns="year", values="qc_night_med")
bal = piv.dropna(subset=[2013, 2025]).copy()
bal["dQ"] = bal[2025] - bal[2013]
clean_codes = set(fl.loc[fl.contaminated == 0, "gxp"])
d = bal.join(yr, how="inner")
d_all = d.copy()
d = d[d.index.isin(clean_codes)].dropna(subset=["dQ", "Nbar", "dN"])

X = d["Nbar"].to_numpy()
XdN = d["dN"].to_numpy()
Y = d["dQ"].to_numpy()
n = len(d)


def ols(y, cols):
    A = np.column_stack([np.ones(len(y))] + cols)
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    sse = float(resid @ resid)
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - sse / sst if sst > 0 else np.nan
    aic = len(y) * np.log(sse / len(y)) + 2 * A.shape[1]
    return beta, r2, aic, resid


# M0 mean-only (the bus-level-artefact null)
sse0 = float(((Y - Y.mean()) ** 2).sum())
aic0 = n * np.log(sse0 / n) + 2

# M1: dQ = a + b*Nbar
b1, r2_1, aic1, resid1 = ols(Y, [X])
# pair bootstrap CI on slope
boots = []
for _ in range(4000):
    i = rng.integers(0, n, n)
    bb, *_ = ols(Y[i], [X[i]])
    boots.append(bb[1])
ci = np.percentile(boots, [2.5, 97.5])

# Theil-Sen (robust) on M1
ii, jj = np.triu_indices(n, 1)
slopes = (Y[jj] - Y[ii]) / (X[jj] - X[ii])
ts_slope = float(np.median(slopes[np.isfinite(slopes)]))

# through-origin sensitivity
b_origin = float((X @ Y) / (X @ X))

# M2: dQ = a + b*Nbar + c*dN
corr_n_dn = float(np.corrcoef(X, XdN)[0, 1])
b2, r2_2, aic2, _ = ols(Y, [X, XdN])

# top residuals from M1
d = d.assign(resid=resid1)
worst = d.reindex(d.resid.abs().sort_values(ascending=False).index)[
    ["dQ", "Nbar", "dN", "resid"]].head(6)

to_var = 1e6  # MVAr per ICP -> VAr per ICP
res = {
    "n_clean_joined": n,
    "n_all_joined": int(len(d_all)),
    "M0_null": {"aic": round(aic0, 1)},
    "M1": {"slope_var_per_icp": round(b1[1] * to_var, 1),
           "ci95_var_per_icp": [round(c * to_var, 1) for c in ci],
           "intercept_mvar": round(b1[0], 2), "r2": round(r2_1, 3),
           "aic": round(aic1, 1)},
    "M1_theilsen_var_per_icp": round(ts_slope * to_var, 1),
    "M1_through_origin_var_per_icp": round(b_origin * to_var, 1),
    "M2": {"a_var_per_icp": round(b2[1] * to_var, 1),
           "b_var_per_new_icp": round(b2[2] * to_var, 1),
           "r2": round(r2_2, 3), "aic": round(aic2, 1),
           "corr_Nbar_dN": round(corr_n_dn, 2)},
    "prediction_band_var_per_icp": [50, 400],
    "central_prediction_var_per_household": [100, 200],
}
(HERE / "icp_regression_results_20260806_legacy_firstrun.json").write_text(
    json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
print("\nlargest |residuals| (M1):")
print(worst.round(2).to_string())
print(f"\nleverage: max Nbar = {X.max():.0f} ({d.index[np.argmax(X)]}), "
      f"median Nbar = {np.median(X):.0f}")

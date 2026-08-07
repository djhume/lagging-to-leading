#!/usr/bin/env python3
"""ICP-count regression - decisive check #1 of the proxy decomposition (6 Aug 2026).

SUPERSEDED same evening by icp_regression.ipynb (canonical, 20-assertion battery,
adds leave-one-out + figure). This script kept for provenance of the first run.

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
  Screen:     screen_by_gxp_year.csv (this directory; night-median net leading MVAr).
  Flags:      power-factor replication cache contamination_flag.csv (clean cohort).

Outputs (this directory): icp_per_poc_20260806.csv, icp_regression_results_20260806.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]  # gridlytics repo root
ICP_SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/tmp/claude-1000/-home-dave-gridlytics-clients-ea-harmonics/"
    "e9186570-b413-443f-b74f-891aeae915a1/scratchpad/icp_by_rootnsp.csv")

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
yr.round(0).to_csv(HERE / "icp_per_poc_20260806.csv")

# ---- screen panel: clean cohort, balanced 2013 & 2025, night-median rise ----
scr = pd.read_csv(HERE / "screen_by_gxp_year.csv")
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
(HERE / "icp_regression_results_20260806.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
print("\nlargest |residuals| (M1):")
print(worst.round(2).to_string())
print(f"\nleverage: max Nbar = {X.max():.0f} ({d.index[np.argmax(X)]}), "
      f"median Nbar = {np.median(X):.0f}")

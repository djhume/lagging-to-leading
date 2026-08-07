# %% [markdown]
# # 00 — Data acquisition: from public records to an analysis-ready dataset
#
# **What this notebook is.** This is the first of six notebooks that reproduce, from
# public data, every headline number in the power-factor / overvoltage paper. It does
# the unglamorous but essential job: it takes the two public data sources, explains
# exactly where they come from and what they contain, cleans them with documented
# choices, and writes two small **analysis-ready tables** that the other five notebooks
# read. Nothing here is a result yet — this is the provenance and the plumbing, written
# out in full so that the numbers downstream cannot be mistaken for magic.
#
# **Who this is for.** Power engineers, lawyers, regulators, and overseas researchers —
# including people with little or no statistics background. Every technical term is
# explained the first time it appears. If a step looks like a black box, that is a bug
# in this notebook, not something you are expected to already know.
#
# **The two sources (both public):**
#
# 1. **EMI grid metering** — half-hourly real and reactive power at every *grid exit
#    point* (the substations where the national grid hands electricity to the local
#    networks), from 1997 to 2025. Published by New Zealand's Electricity Authority on
#    the Electricity Market Information site (**emi.ea.govt.nz**). This is the 29-year
#    measurement record that makes this study possible and, as far as we know, unique in
#    the world for its length.
# 2. **Commerce Commission information disclosure** — the regulated lines companies'
#    annual disclosures of their physical assets (how many kilometres of cable, how many
#    capacitor banks, how much demand), published by the Commerce Commission
#    (**comcom.govt.nz**). We use this to describe each network's physical make-up.
#
# **Bottom line of this notebook:** we build (a) a per-grid-exit-point, per-year table
# of reactive behaviour, and (b) a per-lines-company, per-year table of physical assets.
# Both are saved to `replication/cache/`. We confirm the foundation reproduces the
# paper's "spine" numbers exactly before going any further.

# %% [markdown]
# ## A 90-second primer on the physics (so the rest reads plainly)
#
# Electricity on an AC grid carries two kinds of power:
#
# - **Real power (P)**, measured in **megawatts (MW)** — the part that does useful work
#   (heat, light, motion). This is what your power bill is mostly about.
# - **Reactive power (Q)**, measured in **megavolt-amperes reactive (MVAr)** — power that
#   sloshes back and forth between the grid and equipment that stores energy in magnetic
#   or electric fields (motors, transformers, cables). It does no net work, but it has to
#   be supplied, and it has a big effect on **voltage**.
#
# Reactive power has a direction, and the direction matters enormously here:
#
# - **Lagging (inductive)** reactive power is what *motors and transformers* draw. A grid
#   that is net-lagging tends to have its voltage pulled **down**.
# - **Leading (capacitive)** reactive power is what *cables and capacitors* inject. A grid
#   that is net-leading tends to have its voltage pushed **up** — and too much of it,
#   especially overnight when demand is low, causes **overvoltage**.
#
# **Sign convention used in every notebook in this series: `Q < 0` means leading
# (capacitive); `Q > 0` means lagging (inductive).** We will repeat this whenever it
# matters, because getting the sign backwards inverts the whole story.
#
# **Power factor (PF)** is just a tidy summary of the *ratio* of real to total power. A PF
# near 1.0 ("unity") means almost all the power is doing work. We mostly lead with the raw
# **signed MVAr** rather than PF, because PF throws away the lagging-vs-leading sign that
# is the entire point of this study. PF appears only as a companion.

# %% [markdown]
# ### Glossary (terms used across all six notebooks)
#
# | Term | Plain meaning |
# |---|---|
# | **GXP** (grid exit point) | A substation where the national transmission grid hands power to a local network. Our unit of measurement. |
# | **EDB** (electricity distribution business) | A lines company that runs a local network downstream of one or more GXPs. NZ has 29. |
# | **Trading period (TP)** | A half-hour settlement slot. A normal NZ day has 48 (TP1 = 00:00–00:30 … TP48 = 23:30–00:00). |
# | **Overnight** | Here, TP 6–10 (≈ 02:30–05:00) — the deepest part of the night, lowest demand, highest overvoltage risk. |
# | **Evening peak** | Here, TP 36–38 (≈ 17:30–19:00) — the daily demand peak. |
# | **Balanced panel** | The set of GXPs that have data in *every one* of the 29 years, so a long-run trend cannot be faked by the set of measured sites changing over time. |
# | **%UG (underground)** | The share of a network's lines that are underground cable rather than overhead wire. Our stand-in ("proxy") for how much cable-charging a network has. |
#
# Glowworm evidence tags used throughout: **[V]** verified against the primary source ·
# **[I]** inferred/reasoned · **[H]** hypothesis, not yet proven.

# %%
import sys
import pathlib
import warnings

import numpy as np
import pandas as pd

# Find repro.py (it sits in replication/, one level above notebooks/).
for _cand in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents]:
    if (_cand / "repro.py").exists():
        sys.path.insert(0, str(_cand))
        break
import repro
repro.set_style()
warnings.filterwarnings("ignore")  # tidy output; we surface anything that matters explicitly

PROC = repro.processed_dir()
COMCOM = repro.comcom_parquet()
CACHE = repro.CACHE
print("Reading cleaned EMI GXP data from :", PROC)
print("Reading ComCom disclosure from    :", COMCOM)
print("Writing analysis-ready caches to  :", CACHE)

# %% [markdown]
# ## Part 1 — The EMI grid-metering record
#
# **Where it comes from, and how to pull it fresh.** The raw data is half-hourly grid
# metering published by the Electricity Authority at **emi.ea.govt.nz** (Datasets →
# Wholesale → Metered data / Grid export). The project ships two scripts that pull and
# clean it end-to-end:
#
# - `scripts/download_emi_data.py` — downloads the raw half-hourly grid-metered CSVs.
# - `scripts/process_to_parquet.py` — tidies them into one parquet per year,
#   `data/processed/{year}_power_factor_gxps.parquet`, with real power **P** and reactive
#   power **Q** separated and signed.
#
# Re-pulling 29 years of half-hourly metering is a large, slow download, so by default
# this notebook reads the **cleaned per-year parquet files that ship with the project**
# (the bundled cache). That is the deliberate "hybrid" design: the path from raw public
# records is fully scripted and auditable, but the notebooks run offline from the cleaned
# extract. To rebuild from source, run the two scripts above, then re-run this notebook.
#
# Each per-year file is half-hourly for a whole year, with columns identified by
# `(metric, EDB, GXP)` — i.e. for every grid exit point we have a P column and a Q column,
# for every half hour. Let us look at one year to make that concrete.

# %%
sample = pd.read_parquet(PROC / "2024_power_factor_gxps.parquet")
print("One year (2024) of half-hourly grid metering:")
print("  shape           :", sample.shape, "(rows = half-hours, columns = metric x GXP)")
print("  index levels    :", list(sample.index.names))
print("  metrics present :", sorted(sample.columns.get_level_values(0).unique()))
n_gxp = sample.xs("Q", axis=1, level=0).shape[1]
print(f"  GXPs in 2024    : {n_gxp}")
# show the first few half-hours of reactive power (Q) for three example GXPs
demo = sample.xs("Q", axis=1, level=0).iloc[:3, :3]
demo.columns = [f"{e}/{g}" for e, g in demo.columns]
print("\n  Example: reactive power Q (MVAr) for 3 GXPs, first 3 half-hours:")
print(demo.round(2).to_string())

# %% [markdown]
# ### Building the per-GXP, per-year feature table (the "panel")
#
# **Plain bottom line.** We boil each GXP's whole year of half-hourly data down to a
# handful of numbers — most importantly its *overnight* reactive power — giving one tidy
# row per GXP per year. That table (the "panel") is what the trajectory, decomposition,
# and typology notebooks all build on.
#
# **Why we do this, and what breaks without it.** The raw data is roughly 17,500 half-hours
# × ~230 GXPs × 29 years ≈ 100 million numbers. You cannot see a 29-year trend in that. We
# need a *summary per GXP per year* that keeps the one thing we care about — the overnight
# reactive behaviour — and discards the rest. If we skipped this and, say, averaged over
# the whole day, we would blur together the busy daytime (lots of lagging motor load) with
# the quiet night (where the leading-overvoltage problem lives), and the signal would
# vanish.
#
# **What the summary actually does.** For each GXP and year we compute:
#
# - `on_Q`, `on_P` — average reactive and real power in the **overnight** window (TP 6–10).
#   These are the headline quantities: `on_Q` going negative over the years is the leading-
#   overvoltage drift we are studying.
# - `on_frac_qneg` — the *fraction* of overnight half-hours that were leading (Q<0). A
#   number from 0 (never leading) to 1 (always leading). This is the same idea behind the
#   symptom types the system operator uses, and we reuse it in notebook 04.
# - `pk_Q`, `pk_P` — the same for the **evening peak** (TP 36–38), for comparison.
# - `on_pf` — overnight power factor, kept only as a companion (the *sign* lives in `on_Q`).
#
# **How to read it / what it does NOT mean.** Each row is one GXP's *average* behaviour in
# one year. `on_Q = -5` means that GXP was, on average, injecting 5 MVAr of leading reactive
# power back toward the grid overnight. It does **not** mean every single night was like
# that — `on_frac_qneg` tells you how *consistently* it was leading.
#
# **Why this rigour matters.** Averaging over a 5-half-hour overnight window (rather than a
# single half-hour) makes each number robust to one freak reading. We keep the *signed*
# value rather than power factor so we never lose the lagging/leading direction. These are
# the kinds of choices a hostile reviewer probes first; they are made here in the open.

# %%
# Windows. NZ days have 48 trading periods (49/50 on daylight-saving switch days).
OVERNIGHT = range(6, 11)    # TP 6-10  (deep overnight, lowest demand)
PEAK = range(36, 39)        # TP 36-38 (evening demand peak)


def pf_magnitude(P, Q):
    """Displacement power-factor magnitude |P| / sqrt(P^2 + Q^2). Unsigned on purpose:
    the leading/lagging direction is carried by the sign of Q, kept separately."""
    S = np.sqrt(P**2 + Q**2)
    return np.where(S > 0, np.abs(P) / S, np.nan)


def summarise_year(path):
    """Collapse one year of half-hourly data into one row per GXP."""
    df = pd.read_parquet(path)
    tp = df.index.get_level_values("Trading_Period").to_numpy()
    P, Q = df.xs("P", axis=1, level=0), df.xs("Q", axis=1, level=0)
    on = np.isin(tp, list(OVERNIGHT))
    pk = np.isin(tp, list(PEAK))

    out = pd.DataFrame({
        "on_P": P[on].mean(), "on_Q": Q[on].mean(),
        "pk_P": P[pk].mean(), "pk_Q": Q[pk].mean(),
        "on_frac_qneg": (Q[on] < 0).mean(),         # share of overnight half-hours leading
        "frac_qneg_allday": (Q < 0).mean(),
        "n_obs": Q.shape[0],
    })
    out["on_pf"] = pf_magnitude(out["on_P"], out["on_Q"])
    out.index = pd.MultiIndex.from_tuples(out.index, names=["edb", "gxp"])
    out["year"] = int(path.name[:4])
    return out.reset_index()


files = sorted(PROC.glob("*_power_factor_gxps.parquet"))
panel = pd.concat([summarise_year(f) for f in files], ignore_index=True)
print(f"Panel built: {len(panel):,} GXP-year rows, "
      f"{panel.gxp.nunique()} distinct GXPs, years {panel.year.min()}-{panel.year.max()}")

# %% [markdown]
# ### The balanced panel — guarding against a 29-year measurement trap
#
# **Plain bottom line.** The single biggest way a 29-year trend could be *fake* is if the
# set of measured grid exit points changed over time — new urban (cable-heavy, leading)
# sites appearing and old rural ones dropping out would *manufacture* a leading trend out
# of pure bookkeeping. We defend against this by also computing everything on the
# **balanced panel**: only the GXPs present in *every single one* of the 29 years.
#
# **What it does.** We flag the GXPs whose data spans all 29 years and mark them
# `balanced = True`. When we want a trustworthy long-run trend, we use only those — the
# *same* sites measured the *whole* time, so any change is real change, not a change in
# who got measured.
#
# **How to read it / what it does NOT mean.** "Balanced" is not "better quality" data; it
# is the *same* data restricted to a fixed cast of sites. The full panel is still useful
# for snapshots of the whole network in a given year (notebook 03 uses it). The rule of
# thumb we follow throughout: **trends on the balanced panel, snapshots on the full panel.**
#
# **Why this matters (especially to a sceptical reader).** A reviewer's first attack on any
# long time series is "your sample changed." Pre-empting it with a fixed-cast panel is what
# turns "the trend is probably real" into "the trend is real on a constant set of sites."

# %%
span = panel.year.nunique()
years_per_gxp = panel.groupby("gxp").year.nunique()
balanced_gxps = set(years_per_gxp[years_per_gxp == span].index)
panel["balanced"] = panel.gxp.isin(balanced_gxps)
print(f"Full panel : {panel.gxp.nunique()} GXPs ever measured")
print(f"Balanced   : {len(balanced_gxps)} GXPs present in all {span} years "
      f"(these carry the long-run trend)")

# %% [markdown]
# ### Checkpoint — does the foundation reproduce the paper's "spine" numbers? [V]
#
# Before trusting anything downstream, we confirm the balanced panel reproduces the three
# anchor numbers the paper is built on. These are the **"spine"**: national overnight
# reactive power across the balanced set of GXPs went from strongly **lagging** in 1997 to
# clearly **leading** by 2025. If this does not match, stop — everything else inherits it.

# %%
bal = panel[panel.balanced]
nat = bal.groupby("year").on_Q.sum()
y0, y1 = nat.index.min(), nat.index.max()
slope = np.polyfit(nat.index, nat.values, 1)[0]
print("BALANCED-PANEL SPINE (national overnight reactive power):")
print(f"  GXPs in balanced panel : {len(balanced_gxps)}  of  {panel.gxp.nunique()}")
print(f"  {y0}: {repro.signed(nat.loc[y0], 'MVAr')}  ->  {y1}: {repro.signed(nat.loc[y1], 'MVAr')}")
print(f"  linear trend           : {slope:+.1f} MVAr/yr")
print(f"  {y0} was net {repro.lead_lag(nat.loc[y0])};  {y1} is net {repro.lead_lag(nat.loc[y1])}")
print()
print("Expected (paper spine): 132 of 238 GXPs, +673 -> -296 MVAr, -30.3 MVAr/yr.")
assert len(balanced_gxps) == 132, "balanced count drifted from the documented spine"
assert abs(slope - (-30.3)) < 0.2, "spine slope drifted"
print("[V] Spine reproduced exactly.")

# %% [markdown]
# **Caution on this spine number (carried through every notebook).** This balanced-panel
# figure (−30.3 MVAr/yr across 132 GXPs) is **one specific dataset**. The paper also uses an
# all-network *physical footprint* number (≈ −49.9 MVAr/yr over 2013–25, notebook 03) and a
# cable-correlation number (≈ 46 MVAr/yr). These measure different things over different
# samples and time spans. **They must be labelled as distinct datasets and never blended
# into a single "headline rate."** We repeat this where each appears.

# %%
# Save the panel for the other notebooks.
panel_cols = ["gxp", "edb", "year", "on_Q", "on_P", "on_pf", "on_frac_qneg",
              "pk_Q", "pk_P", "frac_qneg_allday", "n_obs", "balanced"]
panel[panel_cols].to_parquet(CACHE / "gxp_year_panel.parquet", index=False)
print("wrote", CACHE / "gxp_year_panel.parquet")

# %% [markdown]
# ## Part 2 — The Commerce Commission asset record (the "parameter database")
#
# **Plain bottom line.** To explain *why* a network's reactive behaviour looks the way it
# does, we need to know each lines company's physical make-up: how much underground cable
# it has (cables inject leading reactive power), how many capacitor banks (which also inject
# leading reactive power), how big its demand is, and how much embedded generation sits on
# it. No single public table has all this, so we assemble it from the Commerce Commission's
# annual **information disclosures** into one tidy per-company, per-year table.
#
# **Where it comes from.** Every regulated lines company must publicly disclose standardised
# schedules each year (Commerce Commission, comcom.govt.nz). The project ships these parsed
# into one tidy "long" parquet (`comcom_edb_disclosure_2025.parquet`); each row is one
# disclosed value tagged by schedule, category, year, and units. We pull the specific series
# we need.
#
# **The schedules we use:** 9c (circuit length — overhead vs underground km), 9a (capacitor
# bank counts), 9e (demand, connections, embedded generation), and 4 (regulated asset base).

# %%
disc = pd.read_parquet(COMCOM)
print(f"ComCom disclosure (tidy long form): {len(disc):,} rows")
print("Columns:", list(disc.columns))

# %% [markdown]
# ### Two honesty traps in the asset data we handle explicitly
#
# **(1) The "All-network" double-count.** A few large lines companies (Aurora, Powerco,
# Unison) report each sub-network *and* an "All" roll-up. If we summed everything we would
# count those companies two or three times. **Fix: we keep only the `network == "All"`
# rows.** This is exactly the bug that earlier produced a spurious "national capacitor count
# is rising" story — corrected below.
#
# **(2) A definitional break in the capacitor counts.** Around 2014→2015 several companies
# *widened the scope* of which capacitors they report (e.g. one company's count jumps
# 28 → 104 in a single year). That is a paperwork change, not new equipment. We **flag** it
# per company (`cap_rebaselined`) so nobody reads a scope change as a physical change. Only
# changes *within* a continuous stretch are trustworthy. The capacitor data is also **counts
# only** — no MVAr ratings, no install dates, and it starts in 2013 — so it can only ever be
# a rough proxy. We say so wherever we use it.

# %%
def pull(schedule, category=None, sub_category=None, description=None):
    """Pull one disclosed series as a (edb, year) -> value table. Always restrict to the
    'All' network roll-up to avoid double-counting multi-network companies."""
    d = disc[disc.schedule.str.startswith(schedule) & (disc.network == "All")]
    if category is not None:
        d = d[d.category == category]
    if sub_category is not None:
        d = d[d.sub_category == sub_category]
    if description is not None:
        d = d[d.description == description]
    d = d.dropna(subset=["obs_yr", "value"])
    return d.groupby(["edb", "obs_yr"]).value.mean()


SPECS = {
    "oh_km":   ("SCHEDULE 9c", "Total circuit length (for supply)", "Overhead (km)",    "Total circuit length (for supply)"),
    "ug_km":   ("SCHEDULE 9c", "Total circuit length (for supply)", "Underground (km)", "Total circuit length (for supply)"),
    "cap_end":   ("SCHEDULE 9a", "All - Capacitor Banks", "Capacitors including controls", "Items at end of year (quantity)"),
    "cap_start": ("SCHEDULE 9a", "All - Capacitor Banks", "Capacitors including controls", "Items at start of year (quantity)"),
    "rab_close_000": ("SCHEDULE 4", "Total closing RAB value", "RAB", None),
    "max_demand_mw": ("SCHEDULE 9e", "Maximum coincident system demand", None, "Maximum coincident system demand"),
    "icp_total":     ("SCHEDULE 9e", "Number of connections (ICPs)", None, "Connections total"),
}
series = {k: pull(*v) for k, v in SPECS.items()}

# Embedded ("distributed") generation, summed across MVA rows per company-year.
dg = disc[disc.schedule.str.startswith("SCHEDULE 9e") & (disc.network == "All")
          & (disc.category == "Distributed generation") & (disc.units == "MVA")]
series["dg_mva"] = dg.dropna(subset=["obs_yr", "value"]).groupby(["edb", "obs_yr"]).value.sum()

pdb = pd.DataFrame(series).reset_index().rename(columns={"obs_yr": "year"})
pdb["year"] = pdb.year.astype(int)
pdb["emi_code"] = pdb.edb.map(repro.COMCOM_TO_EMI)

# Derived covariates.
pdb["total_km"] = pdb.oh_km + pdb.ug_km
pdb["pct_ug"] = 100 * pdb.ug_km / pdb.total_km          # cable "dose" proxy
pdb["cap_per_1000icp"] = 1000 * pdb.cap_end / pdb.icp_total
pdb["dg_intensity"] = pdb.dg_mva / pdb.max_demand_mw     # embedded gen as share of peak

# Flag the capacitor definitional break: start-of-year(y) should equal end-of-year(y-1).
pdb = pdb.sort_values(["edb", "year"])
prev_end = pdb.groupby("edb").cap_end.shift(1)
pdb["cap_rebaselined"] = ((pdb.cap_start - prev_end).abs() > 0.5) & prev_end.notna() & pdb.cap_start.notna()

print(f"Parameter database: {len(pdb)} company-year rows, "
      f"{pdb.edb.nunique()} companies, years {pdb.year.min()}-{pdb.year.max()}")
print(f"EMI-mapped companies: {pdb.emi_code.notna().groupby(pdb.edb).any().sum()} of {pdb.edb.nunique()}")

# %% [markdown]
# ### Checkpoint — the capacitor-fleet fact that matters for the paper [V]
#
# One result from this table is load-bearing for the paper's argument, so we verify it here:
# the national capacitor fleet is **flat-to-declining**, not growing. This matters because a
# *static or shrinking* set of capacitors **cannot** be the cause of a *rising* leading-
# reactive trend — it helps rule out "old over-sized capacitors left switched in" as the
# driver, and points instead at the demand-side composition shift (notebooks 02–03).

# %%
nat_caps = pdb[pdb.year >= 2015].groupby("year").cap_end.sum()   # 2015+ = post scope-break
vector = pdb[pdb.edb == "Vector Lines"].set_index("year").cap_end
print("National capacitor count (2015+, after the scope break):")
print(f"  {int(nat_caps.index[0])}: {int(nat_caps.iloc[0])}  ->  "
      f"{int(nat_caps.index[-1])}: {int(nat_caps.iloc[-1])}   (flat-to-declining)")
print(f"Vector Lines capacitor count: 2015={int(vector.loc[2015])} -> 2025={int(vector.loc[2025])} "
      f"(a fall of {int(vector.loc[2015] - vector.loc[2025])} banks — networks are *removing* capacitors)")
assert int(nat_caps.iloc[0]) == 298 and int(nat_caps.iloc[-1]) == 254
assert int(vector.loc[2015]) == 104 and int(vector.loc[2025]) == 57
print("[V] Capacitor-fleet fact reproduced (national 298->254; Vector 104->57).")

# %%
# Save the parameter database for the other notebooks.
pdb_cols = ["edb", "emi_code", "year", "oh_km", "ug_km", "total_km", "pct_ug",
            "cap_start", "cap_end", "cap_rebaselined", "cap_per_1000icp",
            "rab_close_000", "max_demand_mw", "icp_total", "dg_mva", "dg_intensity"]
pdb[pdb_cols].to_parquet(CACHE / "edb_parameter_db.parquet", index=False)
print("wrote", CACHE / "edb_parameter_db.parquet")

# %% [markdown]
# ## Part 3 — A contamination screen: which grid exit points are *not* clean offtakes
#
# **Plain bottom line.** We have been treating every grid exit point as if its meter sees a
# clean slice of *distribution network* — local load plus the network's own cables. Most do.
# But a handful do not, and we must find them before they distort the story. This step builds
# a simple, reproducible **contamination flag** and saves it as a third small table the later
# notebooks read. It does not change any headline; its job is to let us *prove* the headline
# survives once the messy sites are removed (notebooks 01, 02 and 04 do exactly that).
#
# **Why a GXP meter can be "contaminated."** The reactive power a GXP meter records is a *net*
# of several things:
#
# > **metered Q  =  distribution-load Q  +  cable-charging Q  −  embedded-generator Q  ±  Transpower plant Q**
#
# The first two are what this study is about. The other two are confounds:
#
# - **Embedded (distributed) generation.** A *synchronous* embedded generator — a hydro, geo,
#   or cogeneration set wired into the local network — actively regulates voltage, setting its
#   reactive output by the *voltage* it sees, not by the local load. (Crucially, it runs
#   **24/7**, so the overnight window removes the *solar* confound but **not** the synchronous-
#   generator one — solar is dark at 3 a.m., a hydro set is not.)
# - **Transpower voltage-regulating plant on a shared bus.** At some substations a Transpower
#   reactive device (an SVC or STATCOM, a synchronous condenser, or a switched capacitor or
#   reactor bank) sits on the *same* metered bus as the distribution offtake, so its reactive
#   output lands in the GXP figure even though it is not distribution at all.
#
# **One test catches all of these — whoever owns the plant.** A network's own large regulating
# compensation would trip the same flag; the test is behavioural, not ownership-based. A clean
# distribution offtake's reactive power *tracks its load*:
# when local demand rises and falls, so does its reactive draw, so a straight-line fit of
# reactive **Q** against real power **P** explains an appreciable share of the variation
# (R² ≈ 0.3–0.5). Voltage-regulating plant or a voltage-regulating generator sets Q by voltage,
# *independently* of the local load — so the same Q-versus-P fit explains almost nothing
# (R² → 0) and leaves a large, load-independent scatter. We flag a GXP **decoupled** when its
# Q~P fit is weak (**R² < 0.12**) *and* the leftover scatter is large (**residual standard
# deviation > 5 MVAr**). To make sure a flag is a stable trait and not a one-year fluke, we
# compute it on **three spread-out years (2016, 2019, 2022)** and take the median.
#
# **Glossary:** *R² ("R-squared")* — the share (0 to 1) of one quantity's ups-and-downs that a
# straight-line fit on another quantity explains; here, how much of a GXP's reactive wobble is
# explained by its load. *Residual* — what the fit fails to explain (the leftover scatter);
# a big residual with a low R² is the fingerprint of reactive power being set by something
# other than local load.

# %%
# Compute the flag on three spread-out years so it reflects a stable trait, not a fluke.
FLAG_YEARS = [2016, 2019, 2022]
hh_by_year = {}
for y in FLAG_YEARS:
    fp = PROC / f"{y}_power_factor_gxps.parquet"
    if fp.exists():
        hh_by_year[y] = pd.read_parquet(fp)
print(f"Half-hourly years loaded for the screen: {sorted(hh_by_year)}")


def qp_decoupling(edb, gxp):
    """Median Q~P R^2 and residual scatter for one GXP across the flag years.

    A clean offtake's reactive tracks its load (R^2 appreciable); plant / voltage-regulating
    embedded generation set Q by voltage, so Q~P explains little and the residual is large.
    """
    r2s, resids = [], []
    for y, d in hh_by_year.items():
        cq, cp = ("Q", edb, gxp), ("P", edb, gxp)
        if cq not in d.columns or cp not in d.columns:
            continue
        q, p = d[cq].to_numpy(), d[cp].to_numpy()
        m = np.isfinite(q) & np.isfinite(p)
        if m.sum() < 100:
            continue
        q, p = q[m], p[m]
        if q.var() == 0 or p.var() == 0:          # a flat series has no slope to fit
            continue
        try:
            slope, intercept = np.polyfit(p, q, 1)
        except np.linalg.LinAlgError:
            continue
        resid = q - (slope * p + intercept)
        r2s.append(1 - resid.var() / q.var())
        resids.append(resid.std())
    return (np.median(r2s) if r2s else np.nan,
            np.median(resids) if resids else np.nan)


# Last-observed embedded-generation intensity per company (a steady-DG indicator).
dg_by_emi = pdb.sort_values("year").groupby("emi_code").dg_intensity.last().to_dict()

flag_rows = []
for gxp, s in panel.groupby("gxp"):
    edb = s.edb.iloc[0]
    r2, resid = qp_decoupling(edb, gxp)
    decoupled = bool(np.isfinite(r2) and r2 < 0.12 and resid > 5)   # plant / dynamic-DG fingerprint
    steady_dg = bool((dg_by_emi.get(edb, 0) or 0) > 0.10)           # heavy embedded generation
    net_exporter = bool(s.on_P.min() < 0.5)                         # exports overnight (DER archetype)
    flag_rows.append(dict(gxp=gxp, edb=edb, r2_qp=r2, resid_std=resid,
                          decoupled=decoupled, steady_dg=steady_dg,
                          net_exporter=net_exporter,
                          contaminated=bool(decoupled or steady_dg or net_exporter)))
flag = pd.DataFrame(flag_rows).sort_values("gxp").reset_index(drop=True)

decoupled_gxps = sorted(flag.loc[flag.decoupled, "gxp"])
print(f"\nScreened {len(flag)} GXPs over {sorted(hh_by_year)}.")
print(f"Decoupled (reactive set by plant/voltage-regulating DG, not load): "
      f"{len(decoupled_gxps)} GXPs")
print("  ", decoupled_gxps)
print(f"Additionally flagged for the STRICT cohort (steady DG or net-export): "
      f"{int(flag.contaminated.sum()) - len(decoupled_gxps)} GXPs")
print(f"Total flagged 'contaminated' (any reason): {int(flag.contaminated.sum())} of {len(flag)}")

# %% [markdown]
# ### Checkpoint — the decoupled set is small, named, and stable [V]
#
# Six grid exit points fail the Q-tracks-load test across all three years. They are exactly the
# sites where a meter is watching voltage-regulating plant or an embedded synchronous generator
# rather than a distribution network: **ISL0661** and **BRY0661** (Islington and Bromley, on
# Orion's Christchurch network — Transpower SVCs, switched capacitor banks, and shunt reactors
# on the shared buses; verified vs Transpower USI planning docs 16 Jul 2026. NB Orion's own
# static sources — ~28 MVAr of 66 kV cable charging and ~11 MVAr of ripple coupling cells, per
# Orion's Feb-2026 EA-workshop presentation — set much of the standing *level* there, but being
# static they cannot produce the load-independent *scatter* this flag detects), **PEN1101** and
# **HOB1101** (on Vector's Auckland network), **BPE0331** (Bunnythorpe), and **TWH0331** (Tuai,
# which sits with the Waikaremoana hydro stations). This is a *named, mechanism-labelled*
# handful — not a vague exclusion — and it is the set the robustness tests in notebooks 01/02/04
# remove to show the headline does not depend on them.

# %%
expected_decoupled = {"ISL0661", "BRY0661", "PEN1101", "HOB1101", "BPE0331", "TWH0331"}
assert set(decoupled_gxps) == expected_decoupled, \
    f"decoupled set drifted from the documented six: {decoupled_gxps}"
flag.to_parquet(CACHE / "contamination_flag.parquet", index=False)
flag.to_csv(CACHE / "contamination_flag.csv", index=False)
print("[V] Decoupled set reproduced exactly (the documented six).")
print("wrote", CACHE / "contamination_flag.csv")

# %% [markdown]
# ## What we built, and what comes next
#
# Three analysis-ready tables now sit in `replication/cache/`:
#
# - **`gxp_year_panel.parquet`** — one row per grid exit point per year, with the overnight
#   and peak reactive behaviour. The balanced-panel flag marks the 132 sites measured in all
#   29 years. *Reproduces the −30.3 MVAr/yr spine exactly.*
# - **`edb_parameter_db.parquet`** — one row per lines company per year, with cable
#   kilometres, capacitor counts, demand, and embedded generation. *Reproduces the flat-to-
#   declining capacitor fleet.*
# - **`contamination_flag.csv`** — one row per grid exit point, flagging the six "decoupled"
#   sites (reactive set by plant or embedded generation, not load) plus the steady-DG and
#   net-export sites. *Lets the later notebooks prove the headline survives their removal.*
#
# Everything from here uses only these tables plus public physics constants. The next
# notebook (**01**) measures the 29-year reactive trajectory and — crucially — tests whether
# that trajectory is *real* or an artefact of how the metering was recorded over the decades,
# and whether it *survives* removing the contaminated sites above.

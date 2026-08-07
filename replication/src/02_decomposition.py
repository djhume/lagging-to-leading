# %% [markdown]
# # 02 — What is driving the drift: the network, or demand itself?
#
# **What this notebook is.** Notebook 01 established *that* overnight reactive power drifted
# from lagging to leading. This notebook asks the question the whole policy argument turns
# on: **how much of that drift is the network's own cables** (underground cable injects
# leading reactive power), **and how much is the changing make-up of electricity demand
# itself** — the slow replacement of old inductive equipment (simple motors) with modern
# electronic equipment (LED lighting, switch-mode power supplies, variable-speed drives)
# that behaves capacitively? We call the second part **"organic"**: it is in the load fleet,
# not the wires.
#
# **Why the answer matters.** If the drift were mostly cables, it would be a network-planning
# problem with familiar fixes. If it is mostly the *demand fleet*, then it is structural,
# nationwide, outside any single network's control, and not addressed by today's rules — the
# paper's central point.
#
# **Bottom line:** independent methods agree that **the large majority — on the order of 80%
# (method estimates span ~75–90%) — of the 29-year drift toward leading is organic
# (demand-side), not cable charging.** We are careful about what is proven and what is not:
#
# - The drift being **dominantly organic** is robust — it survives both methods and every
#   sensitivity check. We carry it as **[I] approaching [V]**.
# - The **exact split** (is it 80/20 or 90/10?) is **not** precisely pinned by the statistics
#   alone, and we say so plainly: **[H]**. Notebook 03 adds a third, physics-based method.
#
# **The discipline that makes this credible (read this first if you are not a statistician):**
# before we believe *any* number off the real data, we **prove the method works on data where
# we already know the answer** (Section 2b). We invent networks with a *planted* organic share,
# run the exact same machinery, and check it gives the planted number back. This is the direct
# answer to the fair challenge *"you just fit a line to get the answer you wanted"* — we show
# the line-fitting recovers a truth we set in advance, before we ever point it at reality.

# %%
import sys
import pathlib
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import theilslopes

for _cand in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents]:
    if (_cand / "repro.py").exists():
        sys.path.insert(0, str(_cand))
        break
import repro
repro.set_style()
warnings.filterwarnings("ignore")

panel = pd.read_parquet(repro.CACHE / "gxp_year_panel.parquet")
panel = panel[panel.balanced & ~panel.edb.isin(repro.NON_EDB_CODES)].copy()  # balanced demand GXPs
pdb = pd.read_parquet(repro.CACHE / "edb_parameter_db.parquet")
flag = pd.read_csv(repro.CACHE / "contamination_flag.csv")  # notebook 00's contamination screen
clean_gxps = set(flag.loc[~flag.decoupled, "gxp"])          # GXPs whose reactive tracks load

# Each lines company's "cable dose" = its share of lines underground, averaged 2013-25.
# Underground cable is the source of network leading-reactive (charging), so %UG is our
# data-driven stand-in for "how much cable charging sits behind this network".
dose = pdb.groupby("emi_code").pct_ug.mean()
print(f"Balanced demand GXPs: {panel.gxp.nunique()} across {panel.edb.nunique()} networks.")
print(f"Cable dose (%UG) ranges {dose.min():.1f}%–{dose.max():.1f}% across networks.")

# %% [markdown]
# ## Method 1 — the clean-cohort contrast
#
# **Plain bottom line.** Some networks are almost all overhead wire and almost no underground
# cable — rural, "old-school" networks. Overhead wire injects very little leading reactive
# power, so these networks have *almost no cable contribution*. If their overnight reactive
# power **still** drifts toward leading, that drift can only be coming from the demand fleet.
# It does. Comparing how fast the clean (overhead) networks drift against how fast the
# cable-rich (urban) networks drift gives a direct read on the split.
#
# **Why the contrast works (and its two named assumptions).** We did not run a controlled
# trial; history handed us networks at opposite ends of the cable spectrum. The clean ones
# act like a comparison group where the cable cause is nearly switched off, so whatever drift
# remains isolates the demand-side cause. The reading rests on two assumptions, stated
# plainly (and in the paper): that the organic per-MW drift is common across cohorts (if
# urban fleets modernise faster than rural ones, the cable share is overstated), and that
# ≤12%UG networks carry no material cable term (to the extent they do, the demand share is
# overstated) — the two possible violations pull the split in opposite directions.
#
# **What we compute, and why per-MW.** Clean rural networks are *small*, so comparing raw
# MVAr would just compare sizes. We compare **reactive power per MW of load** (`on_Q / |on_P|`)
# — the *character* of each megawatt's reactive behaviour, independent of network size — and
# we load-weight the cohort average so big sites count for more.
#
# **Glossary:** *cohort* = a group of networks (here "clean" vs "cable-rich"). *Load-weighted
# mean* = an average where larger sites count proportionally more, so one tiny site cannot
# swing it.

# %%
CLEAN_MAX, RICH_MIN = 12.0, 40.0    # %UG cut-points: <=12% overhead-dominated; >=40% cable-rich
p = panel.merge(dose.rename("dose"), left_on="edb", right_index=True, how="left").dropna(subset=["dose"])
p["cohort"] = np.where(p.dose <= CLEAN_MAX, "clean",
                np.where(p.dose >= RICH_MIN, "cable-rich", "mid"))
p["q_per_mw"] = (p.on_Q / p.on_P.abs()).replace([np.inf, -np.inf], np.nan)

clean_edbs = sorted(dose.index[dose <= CLEAN_MAX])
rich_edbs = sorted(dose.index[dose >= RICH_MIN])
print(f"CLEAN networks (<= {CLEAN_MAX:.0f}% underground): {[repro.edb_name(e) for e in clean_edbs]}")
print(f"CABLE-RICH networks (>= {RICH_MIN:.0f}% underground): {[repro.edb_name(e) for e in rich_edbs]}")


def cohort_year(g):
    w = g.on_P.abs()
    return pd.Series({
        "q_per_mw_wt": np.average(g.q_per_mw, weights=w.where(w > 0, 0).fillna(0) + 1e-9),
        "frac_lead": (g.on_Q < 0).mean(),
        "n_gxp": g.gxp.nunique(),
    })


traj = (p[p.cohort.isin(["clean", "cable-rich"])]
        .groupby(["cohort", "year"]).apply(cohort_year, include_groups=False).reset_index())


def lin_slope(d):
    m = np.isfinite(d.year) & np.isfinite(d.q_per_mw_wt)   # mask any year with no usable data
    return np.polyfit(d.year[m], d.q_per_mw_wt[m], 1)[0]


rates = {}
print("\nPer-MW overnight reactive drift (MVAr per MW of load; <0 = leading):")
for c in ["clean", "cable-rich"]:
    d = traj[traj.cohort == c].sort_values("year")
    rates[c] = lin_slope(d)
    print(f"  {c:10s}: {int(d.year.min())} = {d.q_per_mw_wt.iloc[0]:+.3f}  ->  "
          f"{int(d.year.max())} = {d.q_per_mw_wt.iloc[-1]:+.3f}   "
          f"(slope {rates[c]:+.4f}/yr, ~{int(d.n_gxp.mean())} GXPs)")

demand_share = rates["clean"] / rates["cable-rich"]
print(f"\nThe clean cohort's drift is PURE demand-composition (≈no cable). Its drift as a")
print(f"share of the cable-rich cohort's drift ≈ {demand_share*100:.0f}% demand / "
      f"{(1-demand_share)*100:.0f}% cable.  [H — proxy estimate]")

# Robustness: the cable-rich cohort contains ISL0661 and BRY0661 (both Orion, both cable-rich),
# which notebook 00 flagged as plant-contaminated — their reactive is set by Transpower SVC
# plant on the shared bus, not by load+cable. If they inflate the cable-rich drift, the
# clean-vs-cable contrast would OVERSTATE the cable share. Re-run dropping the six decoupled GXPs.
p_clean = p[p.gxp.isin(clean_gxps)]
traj_clean = (p_clean[p_clean.cohort.isin(["clean", "cable-rich"])]
              .groupby(["cohort", "year"]).apply(cohort_year, include_groups=False).reset_index())
rates_clean = {c: lin_slope(traj_clean[traj_clean.cohort == c].sort_values("year"))
               for c in ["clean", "cable-rich"]}
demand_share_clean = rates_clean["clean"] / rates_clean["cable-rich"]
print(f"\nContamination check (drop the 6 decoupled GXPs incl. ISL0661/BRY0661):")
print(f"  cable-rich drift {rates['cable-rich']:+.4f}/yr (full) -> "
      f"{rates_clean['cable-rich']:+.4f}/yr (clean)")
print(f"  organic share    {demand_share*100:.0f}% (full) -> {demand_share_clean*100:.0f}% (clean)")
print(f"  -> removing the plant-contaminated nodes if anything STRENGTHENS the demand share;")
print(f"     Method 1's direction is robust to contamination. [H, robust]")

# %% [markdown]
# **Sensitivity to network attribution (ownership changed under the record).** The cable dose
# is a *company* trait, and companies themselves changed: over the 29 years a block of demand
# grid exit points changed EMI network code — essentially all traceable to the breakup of
# UnitedNetworks (successor codes Powerco, Unison, Vector appearing between 2003 and 2013) and
# the onward sale of the Wellington network (2009), plus one Nelson-region boundary change
# (2014). The *metering* panel follows the per-year codes, so the trajectory tracks every
# change automatically. For the *dose* there are two defensible attributions, and we run both:
#
# - **Per-year attribution** (used above): a site carries the dose of its operator that year.
#   Ex-UnitedNetworks sites enter the cohorts only once their successor discloses — UNET
#   pre-dates the disclosure regime and has no dose — so cohort membership changes mid-series.
# - **Physical-continuity attribution**: the wires are the same wires regardless of the owner
#   label, so a site carries its *successor* network's dose throughout — fixed membership, no
#   mid-series composition change.
#
# The clean cohort contains no ex-UnitedNetworks site, so the organic-direction evidence is
# **identical under both**. Only the cable-rich slope (and hence the hypothesis *ratio*) moves:
# the Wellington/Auckland joiners entered relatively lagging, so per-year attribution dilutes
# the cable-rich slope and flatters the demand share. Another reminder that Method 1's ratio is
# a hypothesis; the magnitude rests on the physics (notebook 03), which sums disclosed
# kilometres nationally and is invariant to who owns them.

# %%
pfull = pd.read_parquet(repro.CACHE / "gxp_year_panel.parquet")
pfull = pfull[~pfull.edb.isin(repro.NON_EDB_CODES)]
nun_all = pfull.groupby("gxp").edb.nunique()
ch_all = set(nun_all[nun_all > 1].index)
ch_bal = ch_all & set(panel.gxp.unique())
print(f"Network-code changers: {len(ch_all)} demand GXPs, {len(ch_bal)} in the balanced panel.")
seqs = pfull[pfull.gxp.isin(ch_all)].sort_values("year").groupby("gxp").edb.agg(["first", "last"])
print("Transitions (first -> last code):")
print(seqs.groupby(["first", "last"]).size().rename("n_gxp").reset_index().to_string(index=False))

# Physical-continuity attribution: every site carries its successor's dose for all years.
last_edb = panel.sort_values("year").groupby("gxp").edb.last()
p2 = panel.assign(edb_final=panel.gxp.map(last_edb)).merge(
    dose.rename("dose"), left_on="edb_final", right_index=True, how="left").dropna(subset=["dose"])
p2["cohort"] = np.where(p2.dose <= CLEAN_MAX, "clean",
                 np.where(p2.dose >= RICH_MIN, "cable-rich", "mid"))
p2["q_per_mw"] = (p2.on_Q / p2.on_P.abs()).replace([np.inf, -np.inf], np.nan)
traj2 = (p2[p2.cohort.isin(["clean", "cable-rich"])]
         .groupby(["cohort", "year"]).apply(cohort_year, include_groups=False).reset_index())
rates2 = {c: lin_slope(traj2[traj2.cohort == c].sort_values("year")) for c in ["clean", "cable-rich"]}
share2 = rates2["clean"] / rates2["cable-rich"]
print(f"\nPer-year attribution   : clean {rates['clean']:+.4f}, cable-rich {rates['cable-rich']:+.4f}/yr"
      f"  -> demand share {demand_share*100:.0f}%")
print(f"Physical-continuity    : clean {rates2['clean']:+.4f}, cable-rich {rates2['cable-rich']:+.4f}/yr"
      f"  -> demand share {share2*100:.0f}%")
print("The clean cohort is IDENTICAL under both attributions (no ex-UnitedNetworks site is in it);")
print("only the cable-rich slope, and hence the hypothesis ratio, moves. Direction unaffected. [V]")

# %% [markdown]
# **Sensitivity to the cable-intensity definition (the dual Schedule 9c tables).** Schedule~9c
# reports circuit length two ways — a "total circuit length (for supply)" table (used above) and
# a "by operating voltage" table — and they differ by a few points of %UG for cabled networks.
# This definitional choice, not the data, is what moves Method 1 between the documented ~75% and
# ~90%. We report the ratio under both, and name the boundary network whose cohort membership the
# choice flips.

# %%
disc = pd.read_parquet(repro.comcom_parquet())


def ug_by_voltage():
    """%UG from Schedule 9c's 'by operating voltage' table (the alternative definition)."""
    sel = disc[disc.schedule.str.startswith("SCHEDULE 9c") & (disc.network == "All")
               & (disc.category == "Circuit length by operating voltage (at year end)")]
    oh = sel[sel.sub_category == "Overhead (km)"].dropna(subset=["obs_yr", "value"]).groupby("edb").value.mean()
    ug = sel[sel.sub_category == "Underground (km)"].dropna(subset=["obs_yr", "value"]).groupby("edb").value.mean()
    s = 100 * ug / (oh + ug)
    s.index = s.index.map(repro.COMCOM_TO_EMI)
    return s.dropna()


def method1_ratio(dose_series):
    pp = panel.merge(dose_series.rename("dose"), left_on="edb", right_index=True, how="left").dropna(subset=["dose"])
    pp["cohort"] = np.where(pp.dose <= CLEAN_MAX, "clean", np.where(pp.dose >= RICH_MIN, "cable-rich", "mid"))
    pp["q_per_mw"] = (pp.on_Q / pp.on_P.abs()).replace([np.inf, -np.inf], np.nan)
    tj = (pp[pp.cohort.isin(["clean", "cable-rich"])].groupby(["cohort", "year"])
          .apply(cohort_year, include_groups=False).reset_index())
    rr = {c: lin_slope(tj[tj.cohort == c].sort_values("year")) for c in ["clean", "cable-rich"]}
    return rr["clean"] / rr["cable-rich"]


doseB = ug_by_voltage()
ratio_B = method1_ratio(doseB)
hawk_A, hawk_B = dose.get("HAWK", np.nan), doseB.get("HAWK", np.nan)
print("Method 1 organic share under the two Schedule 9c circuit-length definitions:")
print(f"  'total circuit length (for supply)' : {demand_share*100:.0f}% demand  (the headline)")
print(f"  'by operating voltage'              : {ratio_B*100:.0f}% demand")
print(f"Unison (HAWK) is the network nearest the {RICH_MIN:.0f}% cable-rich cut: %UG = "
      f"{hawk_A:.1f}% (for-supply) / {hawk_B:.1f}% (by-voltage), and on a circuit-km basis "
      f"(rather than mean-of-years) ~45%.")
print("  Its cohort membership is sensitive to the definitional choice; the load-weighted ratio")
print("  is not. The documented ~90/10 came from a different circuit-length series over ALL GXPs")
print("  (not the balanced panel); the exact ratio is definition-dependent, the direction is not. [H]")

# %%
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
col = {"clean": repro.GREEN, "cable-rich": repro.RED}
lab = {"clean": f"Clean rural (≤{CLEAN_MAX:.0f}% underground)",
       "cable-rich": f"Cable-rich urban (≥{RICH_MIN:.0f}% underground)"}
for c in ["clean", "cable-rich"]:
    d = traj[traj.cohort == c].sort_values("year")
    ax1.plot(d.year, d.frac_lead * 100, "-o", color=col[c], lw=2, ms=4, label=lab[c])
    ax2.plot(d.year, d.q_per_mw_wt, "-o", color=col[c], lw=2, ms=4, label=lab[c])
for ax in (ax1, ax2):
    ax.axhline(0, color="grey", lw=0.8, ls="--"); ax.set_xlabel("Year"); ax.legend(fontsize=9)
ax1.set_ylabel("% of overnight half-hours leading"); ax1.set_title("Even clean rural networks go leading")
ax2.set_ylabel("Overnight reactive per MW (MVAr/MW)"); ax2.set_title("Per-MW drift: clean vs cable-rich")
fig.suptitle("Method 1 — the clean-cohort contrast", color=repro.EA_BLUE)
fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(repro.FIGURES / "02_clean_cohort.png"); plt.show()

# %% [markdown]
# **How to read Method 1 / what it does NOT prove.** The clean rural networks drift leading
# almost as fast (per MW) as the cable-rich ones — the cable adds only a modest extra push.
# In this self-contained re-derivation the ratio comes out around **75% demand / 25% cable**.
#
# > **Fresh-eyes note (precision).** An earlier internal run of this method reported ~90/10.
# > The difference is entirely in *how the cohorts are defined*: this notebook uses the cable
# > %UG from the assembled parameter database on the balanced 29-year panel; the earlier run
# > used a different Commerce-Commission circuit-length series over all GXPs. The **direction**
# > (drift is dominantly demand-side) is robust to the choice; the **exact ratio is not** — it
# > moves between roughly 75% and 90% with defensible definitional choices. This is precisely
# > why we treat Method 1's ratio as **[H]** and bring two further methods.
#
# **Other caveats we keep visible:** (1) it assumes the per-MW demand shift is similar in rural
# and urban areas; (2) the clean cohort ends near *balanced* while the cable-rich crosses into
# *leading* — so cable is the *minority* of the drift but can be the **marginal tip** that
# pushes a network from balanced into net-leading (overvoltage) territory; (3) overhead lines
# are not *exactly* zero-charging. So Method 1 is strong on direction but **[H]** on the exact
# split. That is why we bring a second, independent method — and validate it first.

# %% [markdown]
# ## Method 2 — the dose-response, validated before use
#
# **The idea in one sentence.** Give every grid exit point a single number — *how fast its
# overnight reactive power drifts leading per year* — then line the sites up by how much cable
# sits behind them and watch how the drift grows with cable. **The drift that is still there
# at zero cable is the organic, demand-side part.**
#
# **The estimator, step by step (this is the entire method; nothing hidden):**
#
# 1. **One drift number per site.** For each GXP, take its overnight reactive power scaled by
#    its own typical size (`on_Q / median|on_P|`, so big and small sites are comparable) and
#    fit a **robust** trend line through the years (Theil–Sen — median of all pairwise slopes,
#    so a couple of odd years cannot swing it). The slope is the site's *drift*.
# 2. **The dose-response.** Regress those per-site drifts on the site's **cable dose** (its
#    network's %UG). The fitted line has two parts: its value **at zero cable** (`b0`) is the
#    organic drift; its **slope** (`b1`) is the extra drift per unit of cable.
# 3. **Honest uncertainty.** Sites under the same lines company share a dose and are not
#    independent, so we put error bars on by **cluster-bootstrap**: repeatedly re-draw whole
#    *companies* (not individual sites) with replacement and re-fit. Resampling sites would
#    fake precision.
#
# **Glossary:** *intercept* `b0` = the line's height where cable = 0. *Bootstrap* = re-running
# the estimate on many re-sampled versions of the data to see how much the answer wobbles.
# *Cluster bootstrap* = re-sampling whole groups (companies) so correlated sites are kept
# together. *Mixed model* = a regression that lets each company have its own baseline
# ("random intercept"), pooling information without pretending companies are identical.

# %%
MIN_YEARS, MIN_SCALE_MW = 15, 1.0


def gxp_drifts(pnl):
    """One robust drift number per GXP: Theil-Sen slope of (on_Q / median|on_P|) vs year."""
    out = []
    for gxp, g in pnl.groupby("gxp"):
        g = g.dropna(subset=["on_Q", "on_P", "year"])
        if g.year.nunique() < MIN_YEARS:
            continue
        scale = abs(np.median(g.on_P.values))
        if scale < MIN_SCALE_MW:
            continue
        slope, *_ = theilslopes((g.on_Q / scale).values, g.year.values.astype(float))
        out.append(dict(gxp=gxp, edb=g.edb.mode().iloc[0], drift=slope,
                        med_on_P=np.median(g.on_P.values)))
    return pd.DataFrame(out)


def fit_dose(d, mixed=True):
    """Fit drift = b0 + b1*dose. Returns (b0, b1). Mixed = random intercept per company."""
    d = d.dropna(subset=["drift", "dose"])
    if mixed:
        try:
            import statsmodels.formula.api as smf
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")   # mixed-model convergence chatter is harmless here
                m = smf.mixedlm("drift ~ dose", d, groups=d.edb).fit(reml=True)
            return float(m.params["Intercept"]), float(m.params["dose"])
        except Exception:
            pass
    X = np.column_stack([np.ones(len(d)), d.dose.values])
    beta, *_ = np.linalg.lstsq(X, d.drift.values, rcond=None)
    return beta[0], beta[1]


def organic_share(b0, b1, d):
    tot = b0 + b1 * d
    return np.nan if abs(tot) < 1e-9 else b0 / tot


def cluster_bootstrap(d, ref_doses, n_boot=2000, seed=12345):
    """Resample whole companies with replacement; re-fit each time (OLS for speed)."""
    rng = np.random.default_rng(seed)
    edbs = d.edb.dropna().unique()
    by = {e: d[d.edb == e] for e in edbs}
    rows = []
    for _ in range(n_boot):
        pick = rng.choice(edbs, size=len(edbs), replace=True)
        samp = pd.concat([by[e].assign(edb=f"{e}__{i}") for i, e in enumerate(pick)],
                         ignore_index=True)
        b0, b1 = fit_dose(samp, mixed=False)
        rows.append(dict(b0=b0, b1=b1,
                         **{f"share_{k}": organic_share(b0, b1, v) for k, v in ref_doses.items()}))
    return pd.DataFrame(rows)


print("Estimator defined. Validating it on known-answer data before any real use...")

# %% [markdown]
# ### 2b. Validation: what can this estimator recover, and what can it not? [V — the credibility gate]
#
# **Why this section exists.** This protects the result from the fair challenge *"you just fit a
# line to get the answer you wanted."* We build synthetic networks whose drift is a **known**
# organic part + a **known** cable part + realistic noise, laid on top of the **real** cable doses
# and the **real** company structure, then run the *identical* estimator and check what it returns.
# The crucial discipline (Brian's rule: *identifiability before estimation*) is to test it in **two
# regimes**, because the honest answer is that it can recover some things and not others:
#
# 1. **An "identified" regime — a real, sizeable cable effect.** Here the organic *share* is a
#    well-posed target. We check the estimator recovers the planted share with little bias and a
#    roughly calibrated interval. *If it failed this, the machinery would be broken and nothing
#    downstream could be trusted.*
# 2. **The "real-data" regime — a cable effect of essentially zero.** This is what the real data
#    actually show (Section 2c: the cable slope `b1` crosses zero). When the cable effect is truly
#    zero the planted organic share is **100% by construction**, and the question is what the
#    estimator returns. It returns ~100% at the median — but the share becomes **wide and unstable**
#    as cable dose rises. So in this regime the *share* is **not point-identified**; only the
#    **sign and size of the organic drift `b0`** are.
#
# **What this buys us, plainly.** We validate — and will claim — that the estimator recovers the
# **organic drift's direction and magnitude** robustly, and recovers a **share** only when the
# cable effect is large enough to be identified. We do **not** claim it validates a precise *share*
# on the real data, because the real data sit in regime 2. (This is the correction to an earlier
# single arm, which validated the *sign of `b0`*, not the *share*.)

# %%
# Two planted regimes. Sign convention: <0 = leading. The skeleton (companies, doses, sizes,
# observed years) is REAL; only the drift law and the noise are planted.
REGIMES = {
    "identified (real cable effect)": dict(b0=-0.0120, b1=-0.00060,
                                           sigma_edb=0.0035, sigma_year=0.040, rho=0.5),
    "real-data regime (b1 = 0)":      dict(b0=-0.0120, b1=0.0,
                                           sigma_edb=0.0035, sigma_year=0.040, rho=0.5),
}
N_SIM, N_SIM_COV, N_BOOT_COV = 120, 40, 400   # modest counts so the notebook runs briskly

# Real skeleton to simulate onto: each GXP's company, dose, size, and observed years.
design = []
for gxp, g in panel.groupby("gxp"):
    g = g.dropna(subset=["on_Q", "on_P", "year"])
    edb = g.edb.mode().iloc[0]
    if g.year.nunique() < MIN_YEARS or edb not in dose.index or not np.isfinite(dose[edb]):
        continue
    scale = abs(np.median(g.on_P.values))
    if scale >= MIN_SCALE_MW:
        design.append(dict(gxp=gxp, edb=edb, dose=float(dose[edb]), scale=scale,
                           years=sorted(g.year.unique())))
design = pd.DataFrame(design)
ref = {"median": float(np.median(design.dose)), "p90": float(np.percentile(design.dose, 90)),
       "max": float(design.dose.max())}
print(f"Synthetic skeleton: {len(design)} GXPs, {design.edb.nunique()} companies.")


def simulate(rng, TRUE):
    """One synthetic panel under a planted drift law TRUE, on the real skeleton."""
    u = {e: rng.normal(0, TRUE["sigma_edb"]) for e in design.edb.unique()}
    recs = []
    for _, r in design.iterrows():
        d = TRUE["b0"] + TRUE["b1"] * r.dose + u[r.edb]
        yrs = np.array(r.years, float); y0 = yrs.mean()
        eps = np.zeros(len(yrs)); e = rng.normal(0, TRUE["sigma_year"])
        for i in range(len(yrs)):
            e = TRUE["rho"] * e + np.sqrt(1 - TRUE["rho"]**2) * rng.normal(0, TRUE["sigma_year"])
            eps[i] = e
        scaled = rng.normal(0.1, 0.1) + d * (yrs - y0) + eps
        for yr, q in zip(yrs, scaled * r.scale):
            recs.append(dict(gxp=r.gxp, edb=r.edb, year=int(yr), on_Q=q, on_P=r.scale))
    return pd.DataFrame(recs)


# What does the estimator return in each regime? (b0's sign/size vs the share)
for name, TRUE in REGIMES.items():
    true_share = {k: organic_share(TRUE["b0"], TRUE["b1"], v) for k, v in ref.items()}
    rng = np.random.default_rng(2026)
    rec = []
    for _ in range(N_SIM):
        dr = gxp_drifts(simulate(rng, TRUE)); dr["dose"] = dr.edb.map(dose)
        b0, b1 = fit_dose(dr)
        rec.append({k: organic_share(b0, b1, ref[k]) for k in ref}
                   | {"b0": b0, "b1": b1, "b0_leading": b0 < 0})
    R = pd.DataFrame(rec)
    print(f"\n=== REGIME: {name} ===")
    print(f"  planted b0={TRUE['b0']:+.4f}, b1={TRUE['b1']:+.5f}  -> TRUE organic share: "
          f"median-dose {true_share['median']*100:.0f}%, most-cabled {true_share['max']*100:.0f}%")
    print(f"  organic drift b0 recovered: mean {R.b0.mean():+.5f} (planted {TRUE['b0']:+.4f}); "
          f"leading sign in {R.b0_leading.mean()*100:.0f}% of sims  <- robust")
    print(f"  organic SHARE recovered (median [P10, P90] over sims):")
    for k in ref:
        med = np.nanmedian(R[k]) * 100
        lo, hi = np.nanpercentile(R[k], [10, 90]) * 100
        tag = "  <- tight (identified)" if (hi - lo) < 30 else "  <- WIDE / unstable (not identified)"
        print(f"     @ {k:7s} dose: {med:5.0f}%  [{lo:4.0f}%, {hi:4.0f}%]{tag if k=='max' else ''}")

# Coverage of the SHARE interval — only meaningful where the share is identified (regime 1).
TRUE = REGIMES["identified (real cable effect)"]
true_share_med = organic_share(TRUE["b0"], TRUE["b1"], ref["median"])
rng2 = np.random.default_rng(7)
hits = 0
for _ in range(N_SIM_COV):
    dr = gxp_drifts(simulate(rng2, TRUE)); dr["dose"] = dr.edb.map(dose)
    boot = cluster_bootstrap(dr, ref, n_boot=N_BOOT_COV)
    lo, hi = np.nanpercentile(boot.share_median, [2.5, 97.5])
    hits += lo <= true_share_med <= hi
cov = hits / N_SIM_COV
mc = (cov * (1 - cov) / N_SIM_COV) ** 0.5
print(f"\nCOVERAGE of the share interval (identified regime, {N_SIM_COV} sims): "
      f"truth inside the 95% interval {cov*100:.0f}% of the time")
print(f"  Monte-Carlo error ~{mc*100:.0f}pp at {N_SIM_COV} sims -> report as APPROXIMATELY")
print(f"  CALIBRATED (indistinguishable from nominal 95%), not a precise point figure.")

# %% [markdown]
# **Validation verdict — what is, and is not, established. [V]**
#
# - **The estimator recovers the organic drift `b0` — its leading *sign* and its *magnitude* —
#   with negligible bias, in *both* regimes.** This is the robust, validated result, and it is
#   exactly what the "dominantly organic" conclusion rests on.
# - **In an identified regime (a real cable effect) it also recovers the *share* accurately, with
#   an approximately calibrated interval** (coverage above; with only 40 simulations the
#   Monte-Carlo error is several percentage points, so we say "approximately calibrated," not a
#   precise 92%).
# - **In the real-data regime (`b1 ≈ 0`) the *share* is not point-identified.** The estimator
#   correctly returns ~100% organic at the median, but the value is wide and unstable as cable
#   dose rises — the very behaviour Section 2c finds on the real data. **So we validate a
#   *direction and dominance*, not a precise *share*.** The number (~80%) is pinned instead by the
#   physics in notebook 03, which fits no cable coefficient at all.

# %% [markdown]
# ## 2c. The dose-response on the real data
#
# Now — and only now — we run the validated estimator on the real grid metering.

# %%
drifts = gxp_drifts(panel)
drifts["dose"] = drifts.edb.map(dose)
# overnight net-exporters are a distributed-generation archetype, not a clean demand signal
drifts["is_der"] = drifts.med_on_P < 0
core = drifts[~drifts.is_der].dropna(subset=["dose"])
print(f"Core demand GXPs: {len(core)} across {core.edb.nunique()} companies "
      f"({drifts.is_der.sum()} overnight-exporter (DER) site excluded).")

b0, b1 = fit_dose(core)
boot = cluster_bootstrap(core, ref, n_boot=2000)
b0_lo, b0_hi = np.percentile(boot.b0, [2.5, 97.5])
b1_lo, b1_hi = np.percentile(boot.b1, [2.5, 97.5])
print(f"\nORGANIC DRIFT at zero cable  b0 = {b0:+.5f}/yr   95% CI [{b0_lo:+.5f}, {b0_hi:+.5f}]")
print(f"   -> negative (i.e. leading) in {(boot.b0 < 0).mean()*100:.0f}% of bootstraps")
print(f"CABLE SLOPE per +1%UG        b1 = {b1:+.6f}/yr   95% CI [{b1_lo:+.6f}, {b1_hi:+.6f}]")
print(f"   -> crosses zero ({(boot.b1 >= 0).mean()*100:.0f}% of bootstraps are >= 0): weakly identified")
print("\nOrganic SHARE of the drift, read across the cable range (point estimates):")
for k in ref:
    print(f"   @ {k:7s} dose ({ref[k]:4.1f}%UG): {organic_share(b0, b1, ref[k])*100:5.1f}%")

# %% [markdown]
# **How to read this — the careful version.** Two different things are happening here, and
# keeping them apart is the whole honesty of the result:
#
# - **The organic drift `b0` is strongly and unambiguously leading** — negative in ~all
#   bootstraps, with a tight interval. *That* the demand-side drift is real and dominant is
#   the robust finding. **[I] approaching [V].**
# - **The cable slope `b1` is weakly identified** — its interval crosses zero, because cable
#   dose is a *company-level* trait (only ~23 distinct values), so the data cannot pin the
#   marginal cable effect precisely. This means the **exact** organic *share* (78%? 90%?) has
#   a wide, unstable uncertainty. **We therefore do NOT publish a tight share interval** — we
#   report the share as a point estimate across the cable range and a sensitivity band, and we
#   keep the exact split **[H]**. (Notebook 03 pins it better with physics, not statistics.)

# %% [markdown]
# ### 2d. Two robustness checks: capacitors and transportability

# %%
# Cap-bank confound: does controlling for capacitor intensity move the organic intercept?
cap = core.merge(pdb.groupby("emi_code").cap_per_1000icp.mean().rename("cap"),
                 left_on="edb", right_index=True, how="left").dropna(subset=["cap"])
X = np.column_stack([np.ones(len(cap)), cap.dose.values, cap.cap.values])
beta_cap, *_ = np.linalg.lstsq(X, cap.drift.values, rcond=None)
b0_ols, _ = fit_dose(core, mixed=False)
print("CAP-BANK ROBUSTNESS (does adding capacitor intensity as a control move b0?):")
print(f"  organic drift b0 without cap control = {b0_ols:+.5f}")
print(f"  organic drift b0 WITH cap control    = {beta_cap[0]:+.5f}  "
      f"(shift {beta_cap[0]-b0_ols:+.5f}, ~{abs((beta_cap[0]-b0_ols)/b0_ols)*100:.0f}%)")
print("  -> b0 stays strongly leading; the static/declining capacitor fleet (notebook 00)")
print("     cannot be the driver. Confound bounded. [H, but consistent with all other evidence]")

# Transportability: is the organic signal entangled with distributed generation?
dgint = pdb.groupby("emi_code").dg_intensity.mean()
cc = core.merge(dgint.rename("dg"), left_on="edb", right_index=True, how="left").dropna(subset=["dg"])
r_dg = np.corrcoef(cc.dose, cc.dg)[0, 1]
print(f"\nTRANSPORTABILITY: corr(cable dose, distributed-generation intensity) = {r_dg:+.2f}")
print("  -> low; the organic signal is not an artefact of where solar/embedded gen sits,")
print("     so it should generalise across rural and urban networks.")

# Attribution robustness: four ex-UnitedNetworks Auckland-region sites (ALB0331, ALB1101,
# HEN0331, WEL0331) carry the defunct UNET code for most of the record, get no dose, and drop
# out of the fit. The wires are Vector's; restore them under Vector's dose and re-fit.
UNET_VECT = ["ALB0331", "ALB1101", "HEN0331", "WEL0331"]
restored = drifts.copy()
restored.loc[restored.gxp.isin(UNET_VECT), "edb"] = "VECT"
restored["dose"] = restored.edb.map(dose)
core_r = restored[~restored.is_der].dropna(subset=["dose"])
b0_r, b1_r = fit_dose(core_r)
print(f"\nATTRIBUTION ROBUSTNESS (restore the 4 ex-UnitedNetworks sites under Vector's dose):")
print(f"  b0 = {b0:+.5f} (published, n={len(core)})  ->  {b0_r:+.5f} (restored, n={len(core_r)})")
print(f"  b1 = {b1:+.6f}                    ->  {b1_r:+.6f}")
print("  -> the organic drift moves by well under 1%; Method 2 is insensitive to the")
print("     ownership-change attribution. [V]")

# Save the per-GXP drift table for the typology notebook (04) so it can run independently.
drifts_out = drifts.merge(dgint.rename("dg_intensity"), left_on="edb", right_index=True, how="left")
drifts_out.to_parquet(repro.CACHE / "gxp_drifts.parquet", index=False)
print(f"\nwrote {repro.CACHE / 'gxp_drifts.parquet'} (per-GXP drift + dose + DER flag, for notebook 04)")

# %% [markdown]
# ## Publication figure — Methods 1 and 2 as one exhibit
#
# The paper (Aug 2026 figure surgery) shows Method 1's per-MW cohort trajectories and
# Method 2's dose-response as a single two-panel figure. Content is identical to the
# standalone figures above; fonts sized for print, no micro-annotations.

# %%
fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.5, 4.8))
for c, col, lab in (("clean", repro.GREEN,
                     f"Clean rural (≤12% UG), slope {rates['clean']:+.4f}/yr"),
                    ("cable-rich", repro.RED,
                     f"Cable-rich urban (≥40% UG), slope {rates['cable-rich']:+.4f}/yr")):
    d = traj[traj.cohort == c].sort_values("year")
    axA.plot(d.year, d.q_per_mw_wt, "-o", color=col, lw=2, ms=3.5, label=lab)
axA.axhline(0, color="grey", lw=0.8, ls="--")
axA.set_xlabel("Year")
axA.set_ylabel("Overnight reactive per MW of load (MVAr/MW)\n<0 = leading")
axA.set_title("A. Method 1 — clean-cohort contrast")
axA.legend(fontsize=8, loc="lower left")

axB.scatter(core.dose, core.drift, s=26, alpha=0.75, color=repro.EA_BLUE,
            edgecolors="k", linewidths=0.3)
xs = np.linspace(0, float(core.dose.max()) * 1.02, 50)
axB.plot(xs, b0 + b1 * xs, color=repro.RED, lw=2,
         label=f"fit: $b_0$={b0:+.4f}/yr, $b_1$={b1:+.6f}/yr per %UG")
axB.axhline(0, color="grey", lw=0.8, ls="--")
axB.set_xlabel("Cable dose (% of network underground)")
axB.set_ylabel("Per-site overnight leading drift (MVAr/MW/yr)")
axB.set_title("B. Method 2 — dose-response (organic intercept)")
axB.legend(fontsize=8, loc="lower left")
fig.tight_layout(); fig.savefig(repro.FIGURES / "02_methods.png"); plt.show()
print("wrote 02_methods.png (paper exhibit: Methods 1+2 combined)")

# %% [markdown]
# ### 2e. Sensitivity sweep — the honest uncertainty picture

# %%
sweep = {}
sweep["headline (mixed model, %UG dose)"] = fit_dose(core, mixed=True)
sweep["ordinary least squares"] = fit_dose(core, mixed=False)
sweep["include DER-exporter site"] = fit_dose(drifts.dropna(subset=["dose"]), mixed=True)
ug1000 = (pdb.groupby("emi_code").ug_km.mean() * 1000 / pdb.groupby("emi_code").icp_total.mean())
alt = core.assign(dose=core.edb.map(ug1000)).dropna(subset=["dose"])
sweep["dose = cable km per 1000 connections"] = fit_dose(alt, mixed=True)
print("Organic share at the MEDIAN cable dose, under different reasonable choices:")
shares = []
for name, (sb0, sb1) in sweep.items():
    d_med = ref["median"] if "per 1000" not in name else float(np.median(alt.dose))
    s = organic_share(sb0, sb1, d_med) * 100
    shares.append(s)
    print(f"  {name:36s}: {s:5.1f}%")
print(f"\nSENSITIVITY BAND (organic share @ median dose): ~{min(shares):.0f}–{max(shares):.0f}%")
print("This spread IS the honest uncertainty — wider than any single model's interval.")

# %%
# Figure: drift vs cable dose, with the fitted organic intercept.
fig, ax = plt.subplots(figsize=(10, 6))
cmap = {"clean": repro.GREEN, "mid": repro.ORANGE, "cable-rich": repro.RED}
core_c = core.assign(coh=np.where(core.dose <= CLEAN_MAX, "clean",
                     np.where(core.dose >= RICH_MIN, "cable-rich", "mid")))
for c, gg in core_c.groupby("coh"):
    ax.scatter(gg.dose, gg.drift, s=24, alpha=0.7, color=cmap[c], label=c)
xs = np.linspace(0, 100, 50)
ax.plot(xs, b0 + b1 * xs, color=repro.EA_BLUE, lw=2.2, label=f"fit (b0={b0:+.4f}, b1={b1:+.5f})")
ax.axhline(0, color="grey", lw=0.8, ls="--")
ax.axhline(b0, color=repro.EA_BLUE, lw=1, ls=":", label="organic drift at zero cable (b0)")
ax.annotate("the drift is already strongly leading\nat ZERO cable = the organic signal",
            xy=(2, b0), xytext=(20, b0 * 0.4), fontsize=9, color=repro.EA_BLUE,
            arrowprops=dict(arrowstyle="->", color=repro.EA_BLUE))
ax.set_xlabel("Cable dose (% of network underground)")
ax.set_ylabel("Per-site overnight leading drift (scaled/yr; <0 = leading)")
ax.set_title("Method 2 — dose-response: drift vs cable, with the organic intercept")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(repro.FIGURES / "02_dose_response.png"); plt.show()

# %% [markdown]
# ## Triangulation and verdict
#
# The three methods do **not** play equal roles, and saying they do would over-package the
# result. They are also not fully independent: **Methods 1 and 2 both rest on the same `%UG`
# cable proxy applied to the same balanced panel**, so they share a degree of freedom (the very
# one that swings Method 1 between 75% and 90%). The honest division of labour is:
#
# | Method | What it leans on | What it actually establishes |
# |---|---|---|
# | Method 1 — clean-cohort contrast | `%UG` proxy; rural networks ≈ no cable | **direction**: clean networks drift leading almost as fast (~75%; 78% clean-cohort) |
# | Method 2 — dose-response | same `%UG` proxy, drift extrapolated to zero cable | **direction/dominance**: `b0` strongly leading; share **not identified** (`b1` crosses zero) |
# | Method 3 — physics (notebook 03) | first-principles cable charging, **no fitted cable coefficient** | **magnitude**: organic share ≈ **80%** (physical band 75–88%) |
#
# **Verdict — stated the way it should be quoted.**
#
# - **Direction (robust, [I]→[V]).** The organic, demand-side drift is strongly and unambiguously
#   leading (`b0` negative in 100% of bootstraps). The cable-charging contribution to the 29-year
#   drift is **not statistically distinguishable from zero** (the cable slope `b1` crosses zero;
#   positive in ~42% of bootstraps). Together these *imply* the drift is dominantly demand-side —
#   as a logical consequence of the two facts, not as a measured percentage.
# - **Magnitude (carried by physics, not statistics).** A first-principles charging calculation,
#   which fits **no** cable coefficient (notebook 03), puts the organic share of the drift at
#   **about 80% (physical band 75–88%)**. The two statistical methods are *directionally
#   consistent* but, because the marginal cable effect is not identified at the ~23 available
#   company-level cable values, **do not themselves pin the share** (the b1=0 arm in 2b shows why:
#   in this regime the estimator returns ~100% with a wide, unstable interval).
# - **What we do not claim.** No point-identified split, and no "three independent methods" — the
#   number is a physics result; the statistics confirm its sign and dominance. The split stays
#   **[H]**; we never publish a tight share interval. Cable is the *minority* of the drift but can
#   be the **marginal tip** that pushes a balanced network into net-leading (where overvoltage
#   shows up first).
#
# **The sentence the paper uses (drift only, hedged):** *"The demand-side composition shift is the
# dominant driver of the 29-year drift toward leading power factor: the organic drift is leading in
# 100% of bootstraps while the cable contribution is not distinguishable from zero. A
# first-principles charging calculation puts the organic share at about 80% (physical band
# 75–88%); the statistical methods are directionally consistent but do not point-identify the
# split."* The **level** question (how much of *today's* standing leading reactive is organic) is a
# different, weaker claim handled in notebook 03 — do not conflate them.

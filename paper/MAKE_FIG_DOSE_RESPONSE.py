"""Paper-styled (single-column) Method 2 dose-response figure.

WHY THIS EXISTS. The extended tier illustrates Method 2 as panel (B) of the
double-column `02_methods.png`. That figure was cut from the journal tier in the
TPWRS page reduction, leaving Method 2 as prose only -- and Dave's read (18 Aug)
was that the method is hard to follow without it. This regenerates JUST the
dose-response panel at IEEE single-column size, with the notebook title dropped
(the caption carries it) and the intercept made the visual subject.

REPRODUCIBILITY. All numbers come from the replication suite by re-executing
`src/02_decomposition.py`; nothing is re-fitted or hand-entered here. It writes
to the paper's own figures/ dir and does NOT touch the deposited
`02_dose_response.png`.

    run from replication/:   python ../ieee-pf-trajectory-paper/MAKE_FIG_DOSE_RESPONSE.py

TODO for task #121 (publish chain): fold this generator into the replication
suite before the next deposit refresh, so the journal figure is reproducible from
the archive alone rather than from a paper-directory script.
"""
from __future__ import annotations
import os, pathlib, runpy
os.environ.setdefault("MPLBACKEND", "Agg")
import numpy as np
import matplotlib.pyplot as plt

g2 = runpy.run_path("src/02_decomposition.py")
core, b0, b1 = g2["core"], g2["b0"], g2["b1"]
b0_lo, b0_hi = g2["b0_lo"], g2["b0_hi"]        # the suite's own cluster bootstrap
CLEAN_MAX, RICH_MIN, repro = g2["CLEAN_MAX"], g2["RICH_MIN"], g2["repro"]

OUT = pathlib.Path(__file__).resolve().parent / "figures" / "02_dose_response_journal.png"

plt.rcParams.update({
    "font.size": 7, "axes.labelsize": 7, "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5, "legend.fontsize": 6,
})
# House weights shared across MAKE_FIG_TRAJECTORY / _DOSE_RESPONSE /
# _LEVEL_DECOMPOSITION (Dave, 23 Aug: same formatting across Figs 1-3;
# middle ground between Fig 2's ~1.0 and Fig 3's 1.5).
fig, ax = plt.subplots(figsize=(3.45, 2.45))

# --- the cloud: faint, because the LEVEL is the message, not any single point ---
cmap = {"clean": repro.GREEN, "mid": repro.ORANGE, "cable-rich": repro.RED}
lab  = {"clean": "clean (\u226412% UG)", "mid": "mid",
        "cable-rich": "cable-rich (\u226540% UG)"}
cc = core.assign(coh=np.where(core.dose <= CLEAN_MAX, "clean",
                 np.where(core.dose >= RICH_MIN, "cable-rich", "mid")))
for c in ["clean", "mid", "cable-rich"]:
    gg = cc[cc.coh == c]
    ax.scatter(gg.dose, gg.drift, s=6.5, alpha=0.5, color=cmap[c],
               linewidths=0, label=lab[c], zorder=2)

ax.axhline(0, color="0.4", lw=0.8, ls="--", zorder=1)
ax.annotate("balanced", xy=(103, 0), xytext=(103, 0.0028), fontsize=5.8,
            color="0.35", ha="right")

# --- the organic LEVEL, held across every dose: this is the result ---
ax.axhline(b0, color=repro.EA_BLUE, lw=0.8, ls=":", zorder=3)

# --- the fitted slope, DEMOTED: flat, and that flatness is itself the finding ---
xs = np.linspace(0, 100, 50)
ax.plot(xs, b0 + b1 * xs, color=repro.EA_BLUE, lw=1.3, alpha=0.55, ls="--",
        zorder=4, label="fitted slope (flat)")

# --- the intercept and its uncertainty: the SUBJECT of the picture ---
ax.errorbar([0], [b0], yerr=[[b0 - b0_lo], [b0_hi - b0]], fmt="o", ms=3.0,
            color=repro.EA_BLUE, ecolor=repro.EA_BLUE, elinewidth=1.6,
            capsize=2.6, capthick=1.2, zorder=7, markeredgecolor="white",
            markeredgewidth=0.7, label="$b_0$ at zero cable (95% CI)")

ax.annotate("still leading\nwith NO cable",
            xy=(1.5, b0_lo), xytext=(15, b0 * 2.7), fontsize=6.4,
            color=repro.EA_BLUE, linespacing=1.25,
            arrowprops=dict(arrowstyle="->", color=repro.EA_BLUE, lw=0.8))

ax.set_xlim(-6, 106)
ax.set_xlabel("Cable dose (% of network underground)")
ax.set_ylabel("Overnight drift (scaled/yr)\n$<0$ = going leading")
ax.legend(loc="lower right", frameon=True, framealpha=0.9, borderpad=0.35,
          handletextpad=0.4, labelspacing=0.25)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout(pad=0.25)
fig.savefig(OUT, dpi=400)
print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.0f} kB)")
print(f"  b0 = {b0:+.4f}/yr  CI [{b0_lo:+.4f}, {b0_hi:+.4f}]   b1 = {b1:+.5f}/yr   n = {len(core)}")

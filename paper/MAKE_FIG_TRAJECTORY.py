"""Paper-styled (single-column) 29-year reactive trajectory -- Fig. 1 of the journal tier.

WHY THIS EXISTS. Dave, 23 Aug: "Fig 1, 2 and 3 need to be the same in terms of
formatting -- Figure 3 has more bold lines, Figure 1 not so much -- perhaps take a
middle ground and apply the style for consistency throughout?"

The cause was not line weight. Figs 2 and 3 already had journal variants built at
IEEE column width (3.45 in), but Fig 1 was still the REPLICATION figure -- generated
at 11.0 x 6.0 in and then squeezed into \\columnwidth by LaTeX, a 3.19x reduction.
That scaling divides every stroke and every glyph:

    Fig 1   11.00 in -> 3.45 in   /3.19   lw 2.4 -> ~0.75 pt   font 11 -> ~3.4 pt
    Fig 2    3.45 in -> 3.45 in   x1.01   lw 1.0 -> ~1.0 pt
    Fig 3    3.45 in -> 3.45 in   x1.01   lw 1.5 -> ~1.5 pt

So Fig 1 rendered faintest and with ~3.4 pt axis text (a print legibility problem,
not just an inconsistency), and Fig 3 boldest -- exactly the ordering Dave read off
the page. The fix is a column-width variant, not an lw tweak.

HOUSE WEIGHTS, applied identically here and in the other two MAKE_FIG_* scripts --
the middle ground between Fig 2's ~1.0 and Fig 3's 1.5:

    data series      lw 1.3    markers ms 3.0
    zero / reference lw 0.8    annotation arrows lw 0.8
    fonts            7 axis / 6.5 ticks / 6 legend+annotation

The title is dropped, as in the other journal variants: under Dave's caption rule
the caption names the figure and the chart carries the data and its key. The
LAGGING / LEADING labels stay -- they are the sign convention, which is key, not
argument.

Data comes from src/01_reactive_trajectory.py via runpy, so this plots exactly the
series the replication package computes. Nothing is recomputed here.

    run from replication/:  python ../ieee-pf-trajectory-paper/MAKE_FIG_TRAJECTORY.py
"""
from __future__ import annotations
import os, pathlib, runpy
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt

g1 = runpy.run_path("src/01_reactive_trajectory.py")
repro = g1["repro"]
nat_on, nat_pk, bal = g1["nat_on"], g1["nat_pk"], g1["bal"]
cross_yr, cross_yr_pk = g1["cross_yr"], g1["cross_yr_pk"]

OUT = pathlib.Path(__file__).resolve().parent / "figures" / "01_trajectory_journal.png"

# ---- house weights (shared with MAKE_FIG_DOSE_RESPONSE / _LEVEL_DECOMPOSITION) ----
LW_DATA, MS_DATA, LW_REF = 1.3, 3.0, 0.8

plt.rcParams.update({"font.size": 7, "axes.labelsize": 7, "xtick.labelsize": 6.5,
                     "ytick.labelsize": 6.5, "legend.fontsize": 6})
fig, ax = plt.subplots(figsize=(3.45, 2.20))

ax.axhline(0, color="0.4", lw=LW_REF, ls="--")
ax.plot(nat_on.index, nat_on.values, "-o", color=repro.EA_BLUE, lw=LW_DATA, ms=MS_DATA,
        label="Overnight (TP 6-10)", zorder=5)
ax.plot(nat_pk.index, nat_pk.values, "-s", color=repro.ORANGE, lw=LW_DATA, ms=MS_DATA,
        label="Evening peak (TP 36-38)", zorder=4)

if cross_yr:
    ax.axvline(cross_yr, color=repro.EA_BLUE, ls=":", lw=LW_REF, alpha=0.8, zorder=1)
    ax.annotate(f"overnight goes\nnet leading {cross_yr}", xy=(cross_yr, 0),
                xytext=(cross_yr - 12.5, -235), fontsize=6, color=repro.EA_BLUE,
                arrowprops=dict(arrowstyle="->", color=repro.EA_BLUE, lw=LW_REF))
if cross_yr_pk:
    ax.axvline(cross_yr_pk, color=repro.ORANGE, ls=":", lw=LW_REF, alpha=0.8, zorder=1)
    ax.annotate(f"evening peak\nfollows {cross_yr_pk}", xy=(cross_yr_pk, 0),
                xytext=(cross_yr_pk + 0.6, 330), fontsize=6, color=repro.ORANGE,
                arrowprops=dict(arrowstyle="->", color=repro.ORANGE, lw=LW_REF))

# the sign convention is the chart's key -- it stays in the chart, not the caption
ax.text(1997.5, 545, "LAGGING", fontsize=6, color="grey", weight="bold")
ax.text(1997.5, -300, "LEADING\n(voltage-raising)", fontsize=6, color=repro.RED, weight="bold")

ax.set_xlabel("Year")
# Short label deliberately: at 2.20 in the two-line version clipped ("Q<0 = leadir"),
# and the caption already carries the panel size and the sign convention, which the
# LAGGING / LEADING blocks also show positionally.
ax.set_ylabel("National reactive power (MVAr)")
ax.legend(loc="upper right")
fig.tight_layout(pad=0.3)
OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, dpi=400)
print(f"wrote {OUT}  (3.45 x 2.20 in, house weights lw={LW_DATA})")

"""Paper-styled (single-column) LEVEL decomposition -- the drift/level boundary figure.

WHY THIS EXISTS. Dave, 18 Aug, having just read the ~80% headline: "we all assume
it's the cables and this tells us it's not the cables." Half right, and the wrong
half is load-bearing -- ~80% is the share of the DRIFT. Of the leading MVAr
STANDING on the network, cables are the majority (~84%, and a majority across the
whole +/-35% band). If the author can make that slip, every reader can.

This is panel (A) of the extended tier's `03_physical_charging.png`, extracted at
IEEE single-column size for the journal, which carries no Method 3 figure at all.
Its job is not to report Method 3's result -- that is a number -- but to draw the
boundary between the drift claim the paper makes and the level claim it refuses.
Hence Section IV-D, beside Table I ("Three Decompositions of the DRIFT").

Keep the uncertainty bands: the organic band is huge and straddles zero for much
of the record, which is the visual proof of "we quote no precise share".

    run from replication/:  python ../ieee-pf-trajectory-paper/MAKE_FIG_LEVEL_DECOMPOSITION.py
"""
from __future__ import annotations
import os, pathlib, runpy
os.environ.setdefault("MPLBACKEND", "Agg")
import numpy as np
import matplotlib.pyplot as plt

g3 = runpy.run_path("src/03_physical_charging.py")
nat, repro = g3["nat"], g3["repro"]

OUT = pathlib.Path(__file__).resolve().parent / "figures" / "03_level_journal.png"
plt.rcParams.update({"font.size": 7, "axes.labelsize": 7, "xtick.labelsize": 6.5,
                     "ytick.labelsize": 6.5, "legend.fontsize": 6})
# House weights shared across MAKE_FIG_TRAJECTORY / _DOSE_RESPONSE /
# _LEVEL_DECOMPOSITION (Dave, 23 Aug: same formatting across Figs 1-3;
# middle ground between Fig 2's ~1.0 and Fig 3's 1.5).
fig, ax = plt.subplots(figsize=(3.45, 2.55))
yr = nat.year.values

ax.fill_between(yr, -nat.charge_lo, -nat.charge_hi, color=repro.RED, alpha=0.13, lw=0)
ax.fill_between(yr, nat.organic_lo, nat.organic_hi, color=repro.GREEN, alpha=0.15, lw=0)
ax.axhline(0, color="0.4", lw=0.8, ls="--")

ax.plot(yr, nat.measured, "-o", color="0.15", lw=1.3, ms=3.0, label="measured", zorder=5)
ax.plot(yr, -nat.charge_c, "-s", color=repro.RED, lw=1.3, ms=3.0,
        label="cable + line charging", zorder=4)
ax.plot(yr, nat.organic_c, "-^", color=repro.GREEN, lw=1.3, ms=3.0,
        label="organic (demand)", zorder=4)

# the crossing: where demand stops masking and starts adding.
# No year is printed and no rule is drawn -- the +-35% band plotted here leaves
# the crossing year unresolved from ~2021 to past the end of the record, and
# facing text (journal SIV-D) carries the crossing qualitatively by decision.
# Cold read 25 Aug 2026, F5.
cross = nat[nat.organic_c < 0].year.min()
ax.annotate("demand crosses\ninto leading", xy=(cross - 0.18, 490),
            fontsize=6.2, color=repro.GREEN, linespacing=1.2, va="top", ha="right")
ax.annotate("charging: near-flat\nthe whole time", xy=(2016.2, -250), fontsize=6.2,
            color=repro.RED, ha="left", va="top", linespacing=1.2)
ax.set_xlim(2012.5, 2025.6)

ax.set_xlabel("Year")
ax.set_ylabel("National overnight reactive (MVAr)\n$<0$ = leading")
ax.legend(loc="lower left", frameon=True, framealpha=0.9, borderpad=0.35,
          handletextpad=0.4, labelspacing=0.25)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout(pad=0.25)
fig.savefig(OUT, dpi=400)
print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.0f} kB)")
print(f"  measured {nat.measured.iloc[0]:+.0f} -> {nat.measured.iloc[-1]:+.0f} MVAr")
print(f"  charging {-nat.charge_c.iloc[0]:+.0f} -> {-nat.charge_c.iloc[-1]:+.0f} MVAr (near-flat)")
print(f"  organic  {nat.organic_c.iloc[0]:+.0f} -> {nat.organic_c.iloc[-1]:+.0f} MVAr, crosses {int(cross)}")

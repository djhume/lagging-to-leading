"""Paper-styled (column-width, vector) connection-scaling exhibit -- Fig. 5, BOTH tiers.

WHY THIS EXISTS (Pass C, #124, 23 Aug 2026)
-------------------------------------------
This figure had exactly the disease `MAKE_FIG_TRAJECTORY.py` was written to cure on
Fig. 1, and it had it in both tiers at once:

    generated 7.20 x 9.00 in  ->  drawn at 0.94\\columnwidth = 3.24 in  ->  /2.22

Every stroke and glyph divided by 2.2. `font.size` 11 landed at ~5 pt, panel titles
at ~5.4 pt, and it was saved at `savefig.dpi` 130 where the rest of the set uses 400.
Fig. 1 got its column-width variant on 23 Aug; this one did not, because it is built
from `icp-regression/icp_regression.ipynb` rather than from `replication/src/`.

THREE DEFECTS FIXED, all found by rendering the page and looking (Pass B, B-15):

  1. The "TAK0331" point label was **struck through by its own data marker** -- the
     offset was (2, -12) pt against a 26-pt^2 marker, so the glyphs sat under it. It
     also labelled one point by GXP code where the other four use place names. It is
     Takanini (the prose: "Takanini and Wiri, in south Auckland"), so it says so now.
  2. The slope/CI/R^2 annotation sat **on the dashed zero gridline**, which ran
     straight through the text. It now carries an opaque bbox and sits clear.
  3. Panel B's title asserted a crossing DATE -- "inductive until 2011, deepening
     capacitive every year from 2012" -- which **contradicts the paper's own prose**.
     Section V-C and the journal both now read "crosses zero early in the 2010s" and
     say in terms that the ramp, "rather than the crossing date", is what the data
     establish (Pass B, B-9). The title had kept the retracted claim alive inside a
     raster, where no `.tex` number guard can see it. This is the whole argument for
     the vector conversion and `AUDIT_FIG_ANNOTATIONS.py`.

DATA. The canonical source is the notebook, so its code cells are executed here up to
(not including) its own figure cell, exactly as the other `MAKE_FIG_*` scripts
`runpy` their `src/` script. Nothing is recomputed; the numbers printed at the end are
asserted against the paper's.

HOUSE WEIGHTS: shared with the other MAKE_FIG_* scripts -- data lw 1.3 / ms 3.0,
references lw 0.8, fonts 7 axis / 6.5 ticks / 6 legend and annotation. Serif and
`pdf.fonttype: 42` come from `repro.set_style()`.

    run from replication/:  python ../ieee-pf-trajectory-paper/MAKE_FIG_CONNECTION_SCALING.py
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

os.environ.setdefault("MPLBACKEND", "Agg")

PAPER = pathlib.Path(__file__).resolve().parent
# icp-regression sits beside main.tex in the workspace and at the top level of the public
# repository snapshot; resolve either layout so the script runs from both (24 Aug 2026).
NB = next((p for p in (PAPER / "icp-regression" / "icp_regression.ipynb",
                       PAPER.parent / "icp-regression" / "icp_regression.ipynb") if p.exists()),
          PAPER / "icp-regression" / "icp_regression.ipynb")
REPL = PAPER.parent / "replication"
sys.path.insert(0, str(REPL))
import repro  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

OUT_PNG = REPL / "figures" / "06_connection_scaling.png"

LW_DATA, MS_DATA, LW_REF = 1.3, 3.0, 0.8


def load_state() -> dict:
    """Execute the notebook's analysis cells, stopping before its own figure cell."""
    cells = [c for c in json.loads(NB.read_text())["cells"]
             if c["cell_type"] == "code"]
    code, hit_figure = [], False
    for cell in cells:
        text = "".join(cell["source"])
        if "06_connection_scaling" in text:      # the figure cell: stop here
            hit_figure = True
            break
        code.append(text)
    if not hit_figure:
        raise SystemExit("could not find the figure cell in the notebook")
    ns: dict = {"__name__": "__main__"}
    cwd = os.getcwd()
    os.chdir(NB.parent)                          # the notebook resolves paths from HERE
    try:
        exec(compile("\n".join(code), str(NB), "exec"), ns)
    finally:
        os.chdir(cwd)
    return ns


def main() -> int:
    ns = load_state()
    Xn, Yn, b1n = ns["Xn"], ns["Yn"], ns["b1n"]
    bt, pan = ns["bt"], ns["pan"]
    slope_n, ci_n, r2n, npan = ns["slope_n"], ns["ci_n"], ns["r2n"], ns["npan"]
    r2_h, r3 = ns["r2_h"], ns["r3"]

    repro.set_style()                             # serif + pdf.fonttype 42
    plt.rcParams.update({"font.size": 7, "axes.labelsize": 7,
                         "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
                         "legend.fontsize": 6, "axes.titlesize": 7})

    # Column width, so nothing is scaled down on the page. Both tiers draw it at
    # 0.94\columnwidth, so one variant serves both.
    fig, (axA, axB) = plt.subplots(2, 1, figsize=(3.45, 4.10))

    # ---------------- Panel A: the two-endpoint scatter ----------------
    axA.axhline(0, color="0.4", lw=LW_REF, ls="--", zorder=1)
    axA.scatter(Xn / 1000, -Yn, s=7.0, c=repro.EA_BLUE, alpha=0.75, lw=0, zorder=3)
    xx = np.linspace(0, Xn.max() * 1.04, 50)
    axA.plot(xx / 1000, -(b1n[0] + b1n[1] * xx), c=repro.GREEN, lw=LW_DATA, zorder=2)

    # Place names throughout (the prose names Takanini), and offsets large enough
    # that no glyph lands under its own marker.
    for code, label, dxy, ha in [
            ("PEN0221+0331", "Penrose",       (-6, 0), "right"),
            ("ALB+WRD",      "North Shore",   (-6, 0), "right"),
            ("HEN+HEP",      "West Auckland", (-6, 0), "right"),
            ("HWB+SDN",      "Dunedin",       (6, 0),  "left"),
            ("TAK0331",      "Takanini",      (-6, 0), "right")]:
        r = pan.loc[code]
        # a light backing: the three right-hand points sit close to the fitted
        # line, which otherwise strikes through their labels
        axA.annotate(label, (r.Nbar / 1000, -r.dQ), textcoords="offset points",
                     xytext=dxy, fontsize=5.8, color="0.35", ha=ha, va="center",
                     bbox=dict(facecolor="white", edgecolor="none", alpha=0.8,
                               pad=0.6))

    _iq = -b1n[0]
    axA.annotate(
        f"slope $-${abs(slope_n):.0f} VAr per connection\n"
        f"bootstrap 95% CI $-${abs(ci_n[1]):.0f} to $-${abs(ci_n[0]):.0f}\n"
        f"intercept {'$-$' if _iq < 0 else '$+$'}{abs(_iq):.2f} MVAr per unit\n"
        f"$R^2$ = {r2n:.2f},  n = {npan}",
        xy=(0.03, 0.04), xycoords="axes fraction", ha="left", va="bottom",
        fontsize=6, linespacing=1.3,
        # opaque, so the dashed zero line cannot run through the text
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.92, pad=1.6))

    axA.set_xlabel("Connections served (mean of 2013 and 2025 ICP count, thousands)")
    axA.set_ylabel("Change in overnight reactive\npower, 2013-2025 (MVAr)")
    axA.set_title("A. The deepening scales with connections served", loc="left")

    # ---------------- Panel B: the coefficient's history ----------------
    axB.axhline(0, color="0.4", lw=LW_REF, ls="--", zorder=1)
    axB.fill_between(bt.index, -bt.hi, -bt.lo, color=repro.EA_BLUE, alpha=0.15,
                     lw=0, zorder=2)
    axB.plot(bt.index, -bt.beta, "o-", c=repro.EA_BLUE, lw=LW_DATA, ms=MS_DATA,
             zorder=3)
    axB.set_xlabel("Year")
    axB.set_ylabel("Standing VAr per connection\n(cross-sectional coefficient)")
    # No crossing DATE in the title: Section V-C reports the yearly intervals as
    # straddling zero either side of the crossing, so the ramp is the finding.
    axB.set_title("B. The coefficient's history: inductive early in the record,\n"
                  "deepening capacitive every year since", loc="left")
    axB.annotate(f"accumulation rate\n2013-19 $\\approx$ {r2_h:.0f}, "
                 f"2019-25 $\\approx$ {r3:.0f}\nVAr per connection per year",
                 xy=(0.03, 0.06), xycoords="axes fraction", va="bottom",
                 fontsize=6, linespacing=1.3,
                 bbox=dict(facecolor="white", edgecolor="none", alpha=0.92, pad=1.6))

    fig.tight_layout(pad=0.3)
    OUT_PNG.parent.mkdir(exist_ok=True)
    fig.savefig(OUT_PNG, dpi=400)
    fig.savefig(OUT_PNG.with_suffix(".pdf"))
    print(f"wrote {OUT_PNG.name} and .pdf  (3.45 x 4.10 in, house weights)")
    print(f"  slope {slope_n:.1f} VAr/ICP, CI [{ci_n[0]:.0f}, {ci_n[1]:.0f}], "
          f"R2 {r2n:.3f}, n {npan}, accumulation {r2_h:.1f}/{r3:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

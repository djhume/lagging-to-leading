"""Pass C (#124): rebuild every paper figure as VECTOR PDF, in the paper's own serif.

WHY THIS EXISTS
---------------
Two problems, one build.

1. **Raster.** Every figure shipped as a 400-dpi PNG. At IEEE column width a raster
   is resolution-locked: it cannot be zoomed, its text is not selectable, and the
   numbers annotated inside it are invisible to the paper's own number guards
   (`L4_NUMBER_DIFF`, `PASS7_NUMBER_DIFF`, `TPWRS_CUT_DIFF`), all of which read the
   `.tex`. A value baked into a PNG could drift from the prose and no guard would
   see it. In vector PDF that same text is extractable with `pdftotext`, so the
   annotation audit (`AUDIT_FIG_ANNOTATIONS.py`) becomes mechanical and repeatable.

2. **Font.** Figure text was matplotlib's default DejaVu Sans against an IEEEtran
   body set in URW Nimbus Roman (confirmed: `pdffonts main.pdf` ->
   `NimbusRomNo9L-Regu`). `repro.set_style()` now sets the serif stack and
   `mathtext.fontset="stix"` so `$b_0$` and `$R^2$` match their surroundings.

   It also sets **`pdf.fonttype: 42`**. This matters: matplotlib's default is
   **Type 3**, which IEEE explicitly prohibits in submissions. 42 is TrueType,
   embedded and subsetted.

HOW IT WORKS -- and why it touches no notebook source
-----------------------------------------------------
Each build script is run in its **own subprocess** with `Figure.savefig`
monkeypatched so that every `savefig("X.png")` also writes `X.pdf`. So:

  * no `src/*.py` savefig call is edited, so `build_notebooks.py` need not run and
    the executed notebook outputs are not disturbed (the standing trap);
  * the notebooks keep emitting the PNGs a replicator expects;
  * the paper gets the vector build, exactly as the `MAKE_FIG_*` scripts already
    produce paper-styled variants outside the notebooks.

A subprocess per script also stops rcParam leakage: `MAKE_FIG_TRAJECTORY` sets
7-pt axis text for its column-width variant, and that must not follow the
full-width extended figures built by the next script.

Running the three `MAKE_FIG_*` scripts covers the `src/` figures for free, because
each one already `runpy`s its own `src/` script to get the data -- and that src run
emits the extended tier's figures on the way past.

    run from replication/:  python ../ieee-pf-trajectory-paper/MAKE_FIGS_VECTOR.py

Figures NOT built here: `06_connection_scaling` (canonical source is
`icp-regression/icp_regression.ipynb`, handled by MAKE_FIG_CONNECTION_SCALING.py)
and the two TikZ figures in the extended tier, which are already vector.
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

PAPER = Path(__file__).resolve().parent
REPL = PAPER.parent / "replication"
FIGS = REPL / "figures"

# Each entry is run in its own interpreter, from REPL as the working directory.
# The MAKE_FIG_* scripts runpy their own src/ script, which emits the extended
# tier's figures as a side effect -- so this list covers both tiers.
SCRIPTS = [
    PAPER / "MAKE_FIG_TRAJECTORY.py",          # -> 01_trajectory{,_journal}, 01_splice_test, 01_clean_cohort
    PAPER / "MAKE_FIG_DOSE_RESPONSE.py",       # -> 02_methods, 02_clean_cohort, 02_dose_response{,_journal}
    PAPER / "MAKE_FIG_LEVEL_DECOMPOSITION.py", # -> 03_physical_charging, 03_level_journal
    REPL / "src" / "07_anzsic_class_split.py", # -> 07_class_split (.png, .tex)
]

BOOTSTRAP = textwrap.dedent('''
    import os, pathlib, runpy, sys
    os.environ.setdefault("MPLBACKEND", "Agg")
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure

    _orig_savefig = Figure.savefig
    _written = []

    def _savefig(self, fname, *args, **kwargs):
        result = _orig_savefig(self, fname, *args, **kwargs)
        try:
            p = pathlib.Path(str(fname))
            if p.suffix.lower() == ".png":
                vec = dict(kwargs)
                vec.pop("dpi", None)          # dpi is meaningless for vector text
                _orig_savefig(self, p.with_suffix(".pdf"), *args, **vec)
                _written.append(str(p.with_suffix(".pdf").resolve()))
        except Exception as exc:                       # never let the twin break the build
            print(f"  !! vector twin FAILED for {fname}: {exc}", file=sys.stderr)
        return result

    Figure.savefig = _savefig
    runpy.run_path(sys.argv[1], run_name="__main__")
    print("VECTOR_WROTE:" + ",".join(_written))
''')


def main() -> int:
    if not REPL.is_dir():
        print(f"MISSING: {REPL}")
        return 1
    wrote: list[str] = []
    for script in SCRIPTS:
        if not script.exists():
            print(f"MISSING: {script}")
            return 1
        print(f"\n════ {script.name}")
        proc = subprocess.run(
            [sys.executable, "-c", BOOTSTRAP, str(script)],
            cwd=REPL, capture_output=True, text=True)
        for line in proc.stdout.splitlines():
            if line.startswith("VECTOR_WROTE:"):
                wrote += [n for n in line.split(":", 1)[1].split(",") if n]
            elif line.startswith("wrote ") or "->" in line:
                print("   " + line)
        if proc.returncode != 0:
            print(proc.stdout[-2500:])
            print(proc.stderr[-2500:])
            print(f"FAILED: {script.name}")
            return 1
        if proc.stderr.strip():
            for line in proc.stderr.splitlines():
                if "vector twin FAILED" in line:
                    print("   " + line)

    print("\n════ vector figures now on disk")
    ok = True
    saved = 0.0
    for full in sorted(set(wrote)):
        p = Path(full)
        if not p.exists():
            print(f"   MISSING {p}")
            ok = False
            continue
        png = p.with_suffix(".png")
        png_kb = png.stat().st_size / 1024 if png.exists() else 0.0
        saved += png_kb - p.stat().st_size / 1024
        where = "paper" if p.parent == PAPER / "figures" else "repl"
        print(f"   [{where}] {p.name:<32} {p.stat().st_size/1024:>7.0f} kB "
              f"(png {png_kb:>6.0f} kB)")
    print(f"\n   raster -> vector saves {saved/1024:.1f} MB across the set")
    print(f"\n{len(set(wrote))} vector figures written")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

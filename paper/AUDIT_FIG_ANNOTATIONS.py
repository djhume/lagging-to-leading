"""Pass C (#124): audit the numbers baked INTO the figures against the paper's prose.

THE BLIND SPOT THIS CLOSES
--------------------------
Every number guard this project runs -- `L4_NUMBER_DIFF`, `PASS7_NUMBER_DIFF`,
`TPWRS_CUT_DIFF` -- reads the `.tex`. A value annotated inside a figure was invisible
to all of them. It could contradict the prose indefinitely and no check would fire.

It had. Fig. 5 panel B carried the title

    "B. The coefficient's history: inductive until 2011,
     deepening capacitive every year from 2012"

while Section V-C and the journal both read "crosses zero early in the 2010s" and say
in terms that the ramp, "rather than the crossing date", is what the data establish.
The prose had been hedged (Pass B, B-9); the raster kept asserting the retracted date
in both tiers. Nothing could see it, because a PNG has no text.

Once the figures are vector (`MAKE_FIGS_VECTOR.py`), their annotation text is
extractable, and that check becomes mechanical. This is the check.

WHAT IT DOES
------------
For every figure either tier includes:

  1. `pdftotext` the figure, and split it into lines.
  2. Classify each line. A line carrying any word of three or more letters is
     **prose** -- a title, a legend entry, an annotation, a claim. A line of bare
     numbers is **axis furniture** (tick labels), which asserts nothing and is not
     audited.
  3. Extract numeric tokens from the prose lines with the project's own extractor
     (`PASS7_NUMBER_DIFF_20260813.norm_token`), so a figure's "0.80" and the paper's
     "0.80" normalise identically.
  4. Report each such number as PRESENT if it appears in the tier that includes that
     figure, or UNMATCHED if it does not.

UNMATCHED IS NOT AUTOMATICALLY WRONG -- a figure may legitimately annotate a value
the prose never repeats. It means *a human has to look*, which is exactly what was
missing. Adjudicated exceptions go in `ALLOWED` below, each with its reason, and the
guard prints them so an exception can never quietly become a habit.

    run from anywhere:  python AUDIT_FIG_ANNOTATIONS.py
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPL = HERE.parent / "replication"

spec = importlib.util.spec_from_file_location(
    "pass7", HERE / "PASS7_NUMBER_DIFF_20260813.py")
pass7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pass7)
norm_token = pass7.norm_token

TIERS = {
    "journal": HERE / "main.tex",
    "extended": HERE / "main_extended_20260808.tex",
}

# Numbers a figure may carry that the prose does not repeat, with the reason.
# Keyed by (figure stem, normalised token).
ALLOWED = {
    ("06_connection_scaling", "2013"):
        "axis/annotation window label; the window itself is prose throughout",
    ("06_connection_scaling", "2019"):
        "accumulation-rate sub-window, reported in the caption not the body",
    ("06_connection_scaling", "2025"):
        "axis/annotation window label; the window itself is prose throughout",
    ("01_trajectory", "6"): "trading-period range in the legend (TP 6-10)",
    ("01_trajectory", "10"): "trading-period range in the legend (TP 6-10)",
    ("01_trajectory", "36"): "trading-period range in the legend (TP 36-38)",
    ("01_trajectory", "38"): "trading-period range in the legend (TP 36-38)",
    ("01_trajectory_journal", "6"): "trading-period range in the legend (TP 6-10)",
    ("01_trajectory_journal", "10"): "trading-period range in the legend (TP 6-10)",
    ("01_trajectory_journal", "36"): "trading-period range in the legend (TP 36-38)",
    ("01_trajectory_journal", "38"): "trading-period range in the legend (TP 36-38)",

    # --- adjudicated 23 Aug 2026, Pass C. Each was checked against the source. ---

    # Fig. 5 is ONE figure shared by both tiers, and the journal's condensed V-C
    # drops the numeric CI and intercept ("indistinguishable from zero under every
    # inference scheme") while the extended prose keeps them. The values are right;
    # the journal simply does not repeat them in words.
    # ⚠ Consequence worth knowing: these three ARE printed on the journal's page,
    # inside the figure, so the journal's printed number set is larger than
    # L4_NUMBER_DIFF / TPWRS_CUT_DIFF can see. Not a defect -- a limit of guards
    # that read the .tex.
    ("06_connection_scaling", "-272"):
        "bootstrap CI, in the shared figure; extended prose carries it, journal's does not",
    ("06_connection_scaling", "-199"):
        "bootstrap CI, in the shared figure; extended prose carries it, journal's does not",
    ("06_connection_scaling", "-0.29"):
        "intercept, in the shared figure; journal's prose states it qualitatively only",

    # "CLEAN (-6 decoupled)" -- the prose spells the count ("the six decoupled grid
    # exit points"), so the numeral matches nothing. Same fact.
    ("01_clean_cohort", "-6"):
        "count spelled as a word in the prose ('six decoupled'); same fact",

    # The figure prints six decimal places, the prose five: -0.000050 vs -0.00005.
    # Identical value, trailing zero only.
    ("02_methods", "-0.000050"):
        "same value as the prose's -0.00005; figure carries one more trailing zero",
}

WORD = re.compile(r"[A-Za-z]{3,}")
# A number, optionally signed (incl. the unicode minus matplotlib emits), with
# thousands separators or a decimal part. The lookbehind stops a hyphenated RANGE
# being read as a negative: "TP 36-38" is two trading periods, not -38, and
# "2013-2025" is a window, not -2025.
NUM = re.compile(r"(?<![\w.,])[-−+]?\d[\d,]*(?:\.\d+)?")


def figures_for(tex: Path) -> list[str]:
    """Figure stems a tier actually includes."""
    body = tex.read_text(encoding="utf-8")
    stems = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body)
    return [Path(s).stem for s in stems]


def find_figure(stem: str) -> Path | None:
    for d in (HERE / "figures", REPL / "figures"):
        p = d / f"{stem}.pdf"
        if p.exists():
            return p
    return None


def prose_numbers(pdf: Path) -> list[tuple[str, str]]:
    """(normalised token, the line it came from) for every number on a prose line."""
    # NOT -layout: it reconstructs columns, gluing the y-axis tick labels onto
    # whatever annotation shares their line and inventing numbers that are not
    # in any annotation. Stream order keeps each matplotlib text run on its own line.
    txt = subprocess.run(["pdftotext", str(pdf), "-"],
                         capture_output=True, text=True).stdout
    out: list[tuple[str, str]] = []
    for raw in txt.splitlines():
        line = raw.strip()
        # Furniture is a line with NO word in it at all -- a bare tick label.
        # Anything carrying a word is a title, legend entry or annotation, i.e. a
        # claim. (A two-word threshold was tried and was too strict: it skipped
        # "bootstrap 95% CI -272 to -199", which has one word of three letters.)
        if not line or not WORD.search(line):
            continue
        for m in NUM.finditer(line):
            tok = m.group(0).replace("−", "-")
            out.append((norm_token(tok).lstrip("+"), line))
    return out


def main() -> int:
    tex_text = {name: p.read_text(encoding="utf-8") for name, p in TIERS.items()}
    tex_nums = {}
    for name, path in TIERS.items():
        tex_nums[name] = {norm_token(t).lstrip("+") for t, _ in pass7.extract(path)}

    unmatched, allowed_hits, audited = [], [], 0
    for tier, tex in TIERS.items():
        for stem in dict.fromkeys(figures_for(tex)):
            pdf = find_figure(stem)
            if pdf is None:
                print(f"⚠ {tier}: no vector figure for {stem} "
                      f"(raster figures cannot be audited)")
                continue
            for tok, line in prose_numbers(pdf):
                audited += 1
                if tok in tex_nums[tier]:
                    continue
                if (stem, tok) in ALLOWED:
                    allowed_hits.append((stem, tok, ALLOWED[(stem, tok)]))
                    continue
                unmatched.append((tier, stem, tok, line))

    print(f"audited {audited} numeric tokens on prose lines across "
          f"{len({s for t in TIERS.values() for s in figures_for(t)})} figures\n")

    if allowed_hits:
        print(f"=== ADJUDICATED EXCEPTIONS: {len(set(allowed_hits))} ===")
        for stem, tok, why in sorted(set(allowed_hits)):
            print(f"   {stem:<26} {tok:>10}   {why}")
        print()

    print(f"=== UNMATCHED (in a figure, not in that tier's prose): {len(unmatched)} ===")
    for tier, stem, tok, line in unmatched:
        print(f"  ⚠ [{tier}] {stem}: {tok}")
        print(f"      line: {line[:120]}")

    rec = HERE / "fig_annotation_audit.json"
    rec.write_text(json.dumps({
        "audited_tokens": audited,
        "allowed": [{"figure": s, "token": t, "reason": w}
                    for s, t, w in sorted(set(allowed_hits))],
        "unmatched": [{"tier": a, "figure": b, "token": c, "line": d}
                      for a, b, c, d in unmatched],
    }, indent=1))
    print(f"\nrecord: {rec}")
    green = not unmatched
    print("VERDICT:", "GREEN — every number annotated in a figure is in its tier's prose"
          if green else "⚠ REVIEW — see UNMATCHED above")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())

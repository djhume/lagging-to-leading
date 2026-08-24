"""TPWRS venue-cut number diff (18 Aug 2026) — acceptance check #3.

Three-way diff on the PASS7 extraction machinery (imported, not duplicated),
with A taken from the snapshot the kickoff nominates rather than from L4's
18-pp git baseline:

  A = tpwrs-cut-baseline-A/main.tex   (14 pp, pre-cut journal tier)
  B = main.tex                        (10 pp, cut journal tier)
  C = main_extended_20260808.tex      (23 pp, the complete record, NOT cut)

Checks:
  1. SURVIVING (value in A and B): every raw print form in B must have appeared
     in A — no value drift, no precision change.
  2. REMOVED (in A, gone from B): the value must be present in C. Nothing may
     leave the record entirely.
  3. ADDED (count(B) > count(A)): listed for adjudication; expected ~none, since
     the venue cut only removes.

Writes tpwrs_cut_diff_record.json next to itself. Read-only on the tree.
Usage: python TPWRS_CUT_DIFF.py
"""
from __future__ import annotations

import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

spec = importlib.util.spec_from_file_location(
    "pass7", HERE / "PASS7_NUMBER_DIFF_20260813.py")
pass7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pass7)

extract, norm_token = pass7.extract, pass7.norm_token


def tokens(path):
    counts, raws, ctxs = Counter(), defaultdict(Counter), defaultdict(list)
    for tok, ctx in extract(path):
        v = norm_token(tok).lstrip("+")
        counts[v] += 1
        raws[v][tok] += 1
        ctxs[v].append(ctx.strip())
    return counts, raws, ctxs


def main() -> int:
    pA = HERE / "tpwrs-cut-baseline-A" / "main.tex"
    pB = HERE / "main.tex"
    pC = HERE / "main_extended_20260808.tex"
    for p in (pA, pB, pC):
        if not p.exists():
            print(f"MISSING: {p}")
            return 1

    tA, rA, cA = tokens(pA)
    tB, rB, cB = tokens(pB)
    tC, rC, cC = tokens(pC)

    print(f"tokens: A(14pp)={sum(tA.values())} distinct {len(tA)} | "
          f"B(10pp)={sum(tB.values())} distinct {len(tB)} | "
          f"C(ext)={sum(tC.values())} distinct {len(tC)}")

    # --- 1. surviving byte-identity ---------------------------------------
    drift = [(v, sorted(rA[v]), sorted(set(rB[v]) - set(rA[v])))
             for v in sorted(set(tA) & set(tB))
             if set(rB[v]) - set(rA[v])]
    print(f"\n=== 1. SURVIVING: {len(set(tA) & set(tB))} values; "
          f"raw-form drift: {len(drift)} ===")
    for v, a, new in drift:
        print(f"  ⚠ value {v}: A forms {a} -> B adds {new}")

    # --- 2. removed values must live in the extended ----------------------
    gone, ok, partial = [], [], []
    for v in sorted(tA, key=lambda x: (len(x), x)):
        if tA[v] <= tB.get(v, 0):
            continue
        entry = (v, tA[v], tB.get(v, 0), tC.get(v, 0))
        if tB.get(v, 0) == 0:
            (ok if tC.get(v, 0) else gone).append(entry)
        else:
            partial.append(entry)
    print(f"\n=== 2. REMOVED entirely: {len(ok) + len(gone)} "
          f"(in extended: {len(ok)}; NOT in extended: {len(gone)}); "
          f"count-reduced: {len(partial)} ===")
    for v, a, b, c in gone:
        print(f"  ⚠ NOT IN EXTENDED {v} (A x{a}) ctx: ...{cA[v][0][:150]}...")
    orphan_partial = [p for p in partial if p[3] == 0]
    for v, a, b, c in orphan_partial:
        print(f"  ⚠ count-reduced value absent from extended: {v}")

    # --- 3. added values ---------------------------------------------------
    added = [(v, tA.get(v, 0), tB[v], tC.get(v, 0))
             for v in sorted(tB, key=lambda x: (len(x), x))
             if tB[v] > tA.get(v, 0)]
    print(f"\n=== 3. ADDED in B vs A: {len(added)} ===")
    for v, a, b, c in added:
        print(f"  {v:>12} A x{a} -> B x{b} (ext x{c}) "
              f"ctx: ...{cB[v][-1][:130]}...")

    out = HERE / "tpwrs_cut_diff_record.json"
    out.write_text(json.dumps({
        "pass": "TPWRS venue cut, 18 Aug 2026",
        "A": "tpwrs-cut-baseline-A/main.tex (14 pp)",
        "B": "main.tex (10 pp)",
        "C": "main_extended_20260808.tex (23 pp)",
        "surviving_values": len(set(tA) & set(tB)),
        "raw_form_drift": [
            {"value": v, "formsA": a, "newFormsB": n} for v, a, n in drift],
        "removed_fully_in_extended": [
            {"value": v, "countA": a, "countExt": c, "contextA": cA[v][:2]}
            for v, a, b, c in ok],
        "removed_fully_NOT_in_extended": [
            {"value": v, "countA": a, "contextA": cA[v]}
            for v, a, b, c in gone],
        "count_reduced": [
            {"value": v, "countA": a, "countB": b, "countExt": c}
            for v, a, b, c in partial],
        "added": [
            {"value": v, "countA": a, "countB": b, "countExt": c,
             "contextsB": cB[v][:3]}
            for v, a, b, c in added],
    }, indent=1))
    print(f"\nrecord: {out}")

    green = not gone and not drift and not orphan_partial
    print("VERDICT:", "GREEN — no value drifted; nothing left the record"
          if green else "⚠ RED — adjudication required (see above)")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())

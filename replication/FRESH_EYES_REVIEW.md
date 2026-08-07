# Fresh-eyes review — building the replication notebooks

> **Update (21 June 2026):** Two findings supersede parts of this 18 June log. (1) The
> expert panel (`../ieee-pf-trajectory-paper/PANEL_REVIEW_FINDINGS_20260620.md`) corrected the
> "three independent methods that share no assumptions" framing below: Methods 1 and 2 share the
> %UG cable proxy and are **not** independent, and the ~80% figure is carried by Method 3
> (physics), with Methods 1–2 establishing **direction**, not the share. Notebook 02's validation
> now runs a two-regime test (a planted `b1=0` arm) showing the *share* is identified only when the
> cable effect is, while `b0`'s sign/size is robust. (2) A contamination screen (notebook 00,
> `contamination_flag.csv`) and clean-cohort re-runs (notebooks 01/02/04) show the headline is
> robust to removing the six decoupled GXPs: per-MW drift and %-leading are unchanged, only the
> absolute level is contamination-sensitive. The notebooks and the paper reflect the reframe; this
> log is kept as the original record.

**Date:** 18 June 2026. **Method:** every headline number in the power-factor / overvoltage
work was **re-derived cold** in clean, public-data notebooks (this `replication/` package),
in a fresh session, without inheriting the build session's answers. The rule: what reproduces
from source earns `[V]`; what doesn't is a finding caught *before* drafting. The notebooks are
the single source of truth the LaTeX paper should pull figures and numbers from.

**Verdict: the reactive-power core is publication-grade.** All three decomposition methods
reproduce and agree; the trajectory is confirmed real (not a metering artefact); the asset-
response evidence holds. Four precision findings (below) need to flow into the draft wording —
none weakens the thesis; two actually strengthen the honesty of it.

---

## What reproduced exactly  [V]

| Claim | Re-derived | Documented | Notebook |
|---|---|---|---|
| Balanced-panel spine (all GXPs) | 132 GXPs, +673 → −296 MVAr, −30.3/yr | same | 00, 01 |
| Diurnal signature | overnight goes leading ~2019–20; peak does not | same | 01 |
| Overnight leading fraction | 1% (1997) → 74% (2025) | — | 01 |
| Capacitor fleet | national 298→254; Vector 104→57 (removing) | same | 00, 05 |
| Dose-response organic drift `b0` | −0.01643/yr, 95% CI [−0.0213, −0.0100], **100%** of boots negative | −0.0164, [−0.0215, −0.0101], 100% | 02 |
| Cable slope `b1` | weakly identified, crosses zero (42% ≥0) | sign flips 43% | 02 |
| Organic share (dose-response) | 78% (most-cabled) → 93% (typical); sweep 85–99% | 78–93%; 85–99% | 02 |
| Estimator validation | synthetic-recovery **PASS**: bias ≤0.9%, coverage 92% | PASS, ≤0.9%, 92% | 02 |
| Cap-bank confound | adding cap control moves `b0` ~10%, stays strongly leading | ~10% | 02 |
| Transportability | corr(cable, DER) = −0.22 (low) | −0.22 | 02 |
| Physical decomposition — **drift** | 82% organic (band 75–88%); charging ~−9/yr (near-static) | 82%, 75–88% | 03 |
| Physical decomposition — **level** | 2025: −541 net leading, ~−454 charging, ~16% organic (band −13–45%) | 16%, [−13,45] | 03 |
| Archetypes | k=4, silhouette 0.43; centroids — deep-leading 31.5%UG/−0.033/96%, cable-urban 56%/−0.0145, clean-rural 14.7%/−0.012, DER 0.64 | same | 04 |
| Vong cross-tab | "T2 leading" symptom splits across all 4 mechanisms; most-leading ≠ most-cabled | same | 04 |

**Three independent methods agree the 29-year drift toward leading is dominantly demand-side
("organic").** Clean natural experiment, validated dose-response, and first-principles physics
share no assumptions and all land in the same place. This is the robust, paper-grade claim.

---

## Findings — precision issues to carry into the draft

### F1. The "spine" includes non-demand connection points — label which panel each number uses
The documented spine (132 GXPs, +673 → −296 MVAr, −30.3/yr) is computed over **all** balanced
grid exit points, **including a handful of generator / industrial / rail connection points**.
Restricted to **demand networks** (the paper's actual subject) it is **123 GXPs, +466 → −451
MVAr, −31.1/yr**. The drift rate is essentially identical and the leading endpoint is *stronger*
(lagging industrial load removed). **Action:** in the paper, state which panel each number is on;
never let the two variants be read as the same figure. (Notebook 01 now shows both, labelled.)

### F2. Method 1 (clean cohort) re-derives to ~75/25, not ~90/10 — the exact split is `[H]`
The clean-vs-cable-rich slope ratio came out **~75% demand / 25% cable** in this self-contained
re-derivation, against an earlier internal ~90/10. The whole difference is the cable-intensity
*definition*: this notebook uses parameter-DB %UG on the balanced panel; the earlier run used a
different Commerce-Commission circuit-length series over all GXPs. **Direction is robust; the
exact ratio is not** — it moves ~75–90% with defensible choices. **Action:** the paper should
report the organic share of the drift as **"the large majority, on the order of 80% (method
estimates span ~75–90%)"**, drift only, with the exact split explicitly *not* identified. Do not
headline "~90%". (This strengthens, not weakens, the honesty of the claim.)

### F3. WP1 archetype counts swapped on borderline sites — immaterial
Cluster *counts* differ from the earlier run: clean-rural n29 / deep-leading n16 here vs n16 /
n29 documented. Centroids, labels, silhouette (0.43), and **every conclusion are identical**;
~13 borderline sites move between the two non-DER clusters (clustering sensitivity / BLAS
threading). **Action:** none for the thesis; the notebook prints counts live so it is internally
consistent. If the paper quotes counts, quote this run's.

### F4. Splice test: candidate steps at 2002 & 2022 are curve-bends, not re-bases — confirmed
The synchronous-step detector marks ~2002 and ~2022 (matching the original WP2 over-segmentation
result). The decisive check is **coherence**: at those years it is 67% / 69% vs a typical-year
62% — **not** the near-total spike a genuine metering re-base leaves. So they are trend curvature,
not splices; the trend is splice-robust, and it survives dropping the pre-2002 splice-suspect era
(−31.1 → −33.0/yr). **Action:** §III can pre-empt the "your metering changed" objection in print.

---

## Honesty-rail check (all held)

- **Signed MVAr led throughout; PF only as a companion; the V/f-confounded `k_qf` never used.**
- **Drift vs level kept strictly separate** — drift is the strong claim (`[I]→[V]`), level is the
  weaker narrative point (`[H]`, never quoted as a precise share).
- **Numbers-spine discipline applied** — the three rate numbers (−30.3 / ≈−50 / ≈46 MVAr/yr) are
  labelled as distinct datasets in 00, 01 and 03; never blended.
- **"~80% organic" carried correctly** — `[I]→[V]` for "dominantly organic", `[H]` for the exact
  split; the estimator was validated on known-answer data first (the "you just fit a line"
  defence is in notebook 02, for the lawyer audience).
- **EA hat = descriptive, not advocacy;** the Code is framed as the **missing defence layer**, not
  a "fixable Code" (no cause-removal implied).
- **The Silverdale near-miss is stated accurately** — a Restricted-Earth-Fault maloperation, **not**
  an overvoltage trip; cited only as a *regime* indicator (notebook 05).
- **Public EMI + Commerce Commission data only;** capacitance constants are the only non-public
  inputs and carry an explicit ±35% physical band (notebook 03).

## Pending external-source hardening (notebook 05, §VI) — not blockers for the draft
- Verbatim **Reg 28** wording + the 2025 amendment SR number (via Vicky KB / legislation.govt.nz).
- Exact reactor **MVAr + commissioning dates** from the Transpower SSF / Commerce Commission PDFs
  (web summaries are consistent but quote the primary source).
- Optional: SIPS / South Island additions to `nips_sips.db`.

## Recommendation
Proceed to draft **§§III–VI** (the verified core) pulling all figures and numbers from these
notebooks, then build §§I/II/VII/VIII around them. Fold F1 and F2 into the wording. The
notebooks are the single source of truth; if a number changes, change it here first and re-run.

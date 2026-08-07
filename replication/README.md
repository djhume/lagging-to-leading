# Replication notebooks — the NZ standing-capacitance / reactive-power paper

Companion notebooks that reproduce, from public data, every headline number in

> **"From Lagging to Leading: The Measured Emergence of Standing Capacitance
> Behind Consumer Connections, 1997–2025"** (D. Hume, 2026)

The paper ships in **two tiers with identical section numbering (I–IX)**:

- **Journal version** (`../ieee-pf-trajectory-paper/main.tex`, 14 pp) — condensed
  for the IEEE Open Access Journal of Power and Energy; carries every claim,
  headline number, and hedge.
- **Extended version** (`../ieee-pf-trajectory-paper/main_extended_20260808.pdf`,
  16 pp, frozen 8 Aug 2026) — adds Appendix A (the complete measurement-error
  analysis and the system-wide re-base/"splice" exhibit), Appendix B (the mains
  input filter at 50 Hz), and the supporting cohort/method exhibits (its
  Figs. 2, 3, and 6).

The notebooks are written for a mixed audience — power engineers,
lawyers, regulators, and overseas researchers — and **every statistical step is explained in
plain English**: what it does, why it is needed, how to read the output, and what it does
*not* mean. Technical terms are glossed on first use.

These notebooks doubled as the paper's **fresh-eyes review**: each headline number was
re-derived cold from source. What reproduced is tagged `[V]`; what did not is recorded as a
finding (see `FRESH_EYES_REVIEW.md`).

## What's here

| Notebook | Reproduces | Maps to paper (both versions) |
|---|---|---|
| `00_data_acquisition` | EMI grid metering + Commerce Commission disclosures → two analysis-ready tables | §II Data & method |
| `01_reactive_trajectory` | the 29-year lagging→leading drift **and** the splice/re-base robustness test | §III (results); the splice exhibit itself is extended-only (App. A, its Fig. 6) |
| `02_decomposition` | organic vs cable split — clean-cohort + **validated** dose-response | §IV-A/B (method exhibits extended-only, its Fig. 3) |
| `03_physical_charging` | the same split from first-principles physics (third method) | §IV-C/D |
| `04_archetypes` | the mechanism typology (4 archetypes) vs the Vong symptom types | **supporting analysis only** — not in either paper version (cut at the v3 restructure) |
| `05_overvoltage_evidence` | leading-Q → overvoltage: physics, asset response, foreign blackouts, the Code gap | §VI |

### Indexed evidence notebooks outside this suite (added 7 Aug 2026)

Two claims in the paper's §V (the demand-side term identified: §V-A
load-independence; §V-B the candidate device layer and national sums; §V-C the
connection-scaling test — §IV-E/§IV-F before the v5 renumbering) are computed in
asserted, executed-in-place notebooks that live outside this directory. They are
indexed here so the paper's full claim set stays notebook-backed:

| Notebook (battery) | Backs |
|---|---|
| `../ieee-pf-trajectory-paper/icp-regression/icp_regression.ipynb` (47/47) | The **connection-scaling test** (§V-C): −253 VAr per ICP, bootstrap 95% CI [−291, −192], intercept ≈ 0, R² = 0.77, leave-one-out [−270, −239], ΔAIC ≈ 120 vs the mean-only null; the **coefficient history** (§V-C, cell a3: near zero through 2012, −274 VAr/connection by 2025, rates ≈13/17/24 VAr/connection/yr); **and** the §V-B national sums + bottom-up device estimate (native 114-site cohort: +188 → −182 MVAr night-median in the paper's Q-signed convention, deepening 369, p99 variant 314, 157–214 VAr per household; the n = 90 screen-table sums remain as the regression-panel derivation; device estimate ~150–600 MVAr / 100–200 VAr per household central). Reads this suite's `cache/contamination_flag.csv`, the harmonics resonance-screen panel, and public EMI market-structure ICP counts (raw extract archived alongside it). Saves `figures/06_connection_scaling.png` (journal Fig. 4 / extended Fig. 5, paper sign convention). |
| `../../harmonics/consultation-2026/analysis/resonance-screen/resonance_screen_workings.ipynb` (58/58) | Cross-validation reference for the **parallel-shift / load-independence test** (§V-A): median per-site 2013–25 change −2.25 MVAr overnight (TP 1–12) vs −2.42 MVAr at evening peak (TP 35–39), median per-site ratio 1.06, median peak-load change +3.4%, on 114 clean GXPs with both endpoints (its `results.json`, `unmasking` block; that notebook works leading-positive — signs flipped here to this suite's convention). |

**Release-blocker resolved 7 Aug 2026 eve:** the parallel-shift test and the paper's
§V-B national sums are now computed **natively in the ICP notebook** (cell a2, archive
direct: n = 114; −188 → +182 MVAr night-median, deepening +369; p99 variant +314;
157–214 VAr/household; parallel-shift +2.25/+2.42/1.06/+3.4% reproduced exactly). The
harmonics workings notebook remains indexed as an independent cross-validation only —
no longer required for release. The ICP notebook is release-clean and ships with its
raw EMI extract; it now reads the pf half-hourly archive (`data/analysis/`), the same
source the suite's notebook 00 documents.

## The numbers spine (do not blend these)

Four distinct rate numbers measure different things over different samples. Always say which:

| Number | Sample | Span | Where |
|---|---|---|---|
| **−31.1 MVAr/yr** | 123 balanced demand GXPs | 1997–2025 | the paper's headline panel (00, 01) |
| **−30.3 MVAr/yr** | 132 balanced GXPs (incl. non-distribution points) | 1997–2025 | companion balanced panel (00, 01) |
| **≈ −50 MVAr/yr** | all demand networks | 2013–2025 | physical footprint (03) |
| **≈ 46 MVAr/yr** | cable-Q correlation | — | earlier cable study |

### Panel taxonomy (one place; never blend)

| n | Panel | Used for |
|---|---|---|
| **123** | balanced demand panel (present all 29 years, demand networks only) | the headline trajectory |
| **132** | balanced panel incl. generator/industrial/rail points | companion trend |
| **114** | clean endpoint cohort (2013 & 2025 both metered, clean-strict screen) | §V-B national sums; §V-A parallel-shift test |
| **83** | 114 ∩ usable ICP connection-count series | §V-C scaling regression |
| **81** | cohort present throughout 2009–2025 | §V-C coefficient history β(t) |
| **90** | legacy screen-table clean panel | regression-panel derivation + harmonics documents (superseded for paper quotes by the 114) |

### Sign conventions (three, deliberate; never compare without flipping)

- **This suite and the paper: `Q < 0` = leading** (capacitive, voltage-raising).
- The ICP notebook's screen cells and the harmonics workings notebook compute
  **leading-positive** (leading = +); the ICP notebook's paper-facing cells and
  figure flip to the paper's Q-signed convention and say so in place.

Glowworm evidence tags: `[V]` verified vs primary source · `[I]` inferred · `[H]` hypothesis.

## Figure map (filename ↔ paper figure number)

| File | Journal (14 pp) | Extended (16 pp) |
|---|---|---|
| `01_trajectory.png` | Fig. 1 | Fig. 1 |
| `01_clean_cohort.png` | — (results in §III-B text) | Fig. 2 |
| `02_methods.png` | — (results in §IV text + Table I) | Fig. 3 |
| `03_physical_charging.png` | Fig. 2 | Fig. 4 |
| `06_connection_scaling.png` | Fig. 4 | Fig. 5 |
| `01_splice_test.png` | — (results in §III-B text) | Fig. 6 |
| (in-TeX TikZ mains-filter schematic) | Fig. 3 | Fig. 7 |

Other files in `figures/` (`02_clean_cohort`, `02_dose_response`, `04_archetypes`,
`05_capacitors_out`) are notebook exhibits not placed in either paper version.

## Citing

- **Journal version** (under submission, 2026): D. Hume, ``From Lagging to Leading:
  The Measured Emergence of Standing Capacitance Behind Consumer Connections,
  1997--2025,'' IEEE Open Access Journal of Power and Energy.
- **Extended version + this package:** D. Hume, extended version and
  reproducibility package, GitHub repository with Zenodo snapshot, 2026.
  *(DOI minted at repository publication; insert here and in the journal
  version's reference [33] before submission.)*

## How to run

```bash
source ~/gridlytics/.venv/bin/activate        # pandas, numpy, scipy, scikit-learn,
                                              # statsmodels, ruptures, matplotlib, nbformat
cd replication
python build_notebooks.py                     # src/*.py  ->  notebooks/*.ipynb
cd notebooks
# run 00 first (it builds the cache the others read), then the rest in any order:
for nb in 0*.ipynb; do jupyter nbconvert --to notebook --execute --inplace "$nb"; done
```

### Data access (hybrid design)

- **Default (offline, recommended):** the notebooks read the cleaned per-year EMI parquet
  files and the Commerce Commission disclosure parquet that ship with the project, and
  `00_data_acquisition` builds the two analysis-ready caches (`cache/`). Everything else runs
  from those plus public physics constants.
- **Rebuild from source:** the path from raw public records is fully scripted —
  `scripts/download_emi_data.py` + `scripts/process_to_parquet.py` (EMI half-hourly grid
  metering, emi.ea.govt.nz) and the Commerce Commission information-disclosure data
  (comcom.govt.nz). Run those, then re-run notebook 00.
- The production data lives on a network mount that is slow for batch reads. If a local stage
  exists at `/tmp/pf_stage` (set `PF_STAGE` to override) the notebooks use it automatically;
  otherwise they fall back to the bundled project data. `PF_PROCESSED_DIR` and
  `PF_COMCOM_PARQUET` override individual sources.

## Files

```
replication/
├── README.md              this file
├── FRESH_EYES_REVIEW.md   what reproduced, what didn't, and the precision findings
├── repro.py               shared plumbing ONLY (paths, plot style, name maps) — no analysis
├── build_notebooks.py     percent-.py  ->  .ipynb converter (a tiny jupytext stand-in)
├── src/                   the readable percent-format notebook sources (edit these)
├── notebooks/             the executed .ipynb (build artifacts; regenerated from src/)
├── cache/                 analysis-ready tables built by notebook 00
└── figures/              publication figures saved by the notebooks
```

Edit the `src/*.py` files (clean diffs, easy review), then `python build_notebooks.py` to
regenerate the notebooks. The `repro.py` module deliberately holds *no analytical decisions* —
all analysis is visible inside the notebooks so it can be audited without opening a library.

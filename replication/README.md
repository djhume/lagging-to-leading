# Replication notebooks — the NZ standing-capacitance / reactive-power paper

Companion notebooks that reproduce, from public data, every headline number in

> **"From Lagging to Leading: The Measured Emergence of Standing Capacitance
> Behind Consumer Connections, 1997–2025"** (D. Hume, 2026)

[Read the paper in the browser](https://djhume.github.io/lagging-to-leading/).

The paper ships in **two tiers with identical section numbering (I–IX)**:

- **Journal version** (`../ieee-pf-trajectory-paper/main.tex`, 18 pp, build of
  13 Aug 2026) — condensed for journal submission; carries every claim,
  headline number, and hedge.
- **Extended version** (`../ieee-pf-trajectory-paper/main_extended_20260808.pdf`,
  22 pp, build of 13 Aug 2026) — adds Appendix A (the complete measurement-error
  analysis and the system-wide re-base/"splice" exhibit), Appendix B (the mains
  input filter at 50 Hz), the two-loop cascade taxonomy figure, and the
  supporting cohort/method exhibits (its Figs. 2, 3, and 7).

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
| `../ieee-pf-trajectory-paper/icp-regression/icp_regression.ipynb` (91/91) | The **connection-scaling test** (§V-C, rebased 8 Aug 2026 onto the 96-unit correspondence-audited panel; re-run 13 Aug 2026 on the corrected `data/analysis` archive after the duplicate dual-network rows in the 13-Mar vintage were found double-counting group-member Q): −230 VAr per ICP, bootstrap 95% CI [−272, −199], intercept −0.29 MVAr (**spans zero under every inference scheme**, wild-cluster p = 0.29 — the device story's zero-intercept prediction met on both limbs), R² = 0.80, leave-one-out [−242, −220], ΔAIC ≈ 155 vs the mean-only null, Theil–Sen −259 / through-origin −237 bracketing the OLS; the **original pre-registered 83-site run kept verbatim** as the labelled consistency result (−253, CI [−291, −192], R² = 0.77 — its screen-table inputs were never exposed to the duplicate-row defect, and the two panels now agree within ~10%); the **correspondence audit** itself (8 industrial identities, 2 registry re-registrations, 1 unresolvable, 7 aggregation groups incl. the registry-churn clusters, all evidence-asserted); the **coefficient history** (§V-C, cell a3, 92 units: +41 VAr/connection *inductive* in 2009, crossing zero early in the 2010s, −262 by 2025, CI clear of zero from 2016, in-window rates ≈15/20 VAr/connection/yr, endpoint diff −212 agreeing with the two-endpoint slope within 10%); **and** the §V-B national sums + bottom-up device estimate (native 114-site cohort: +188 → −182 MVAr night-median in the paper's Q-signed convention, deepening 369, p99 variant 314, 157–214 VAr per household — unchanged by the rebase and vintage-stable under the rebuild; the n = 90 screen-table sums remain as the legacy-panel derivation; device estimate ~150–600 MVAr / 100–200 VAr per household central). Reads this suite's `cache/contamination_flag.csv`, the pf half-hourly archive, the harmonics resonance-screen panel (legacy run + cross-check), the POC→network mappings, and public EMI market-structure ICP counts (raw extract archived alongside it). Does **not** save the paper's figure: journal Fig. 5 / extended Fig. 5 is built by `../ieee-pf-trajectory-paper/MAKE_FIG_CONNECTION_SCALING.py`, which re-executes this notebook's analysis cells and draws the exhibit at column width (see *Generated files* below). The notebook's own working copy is `06_connection_scaling_notebook.png`, beside it. |
| `../../harmonics/consultation-2026/analysis/resonance-screen/resonance_screen_workings.ipynb` (58/58) | Cross-validation reference for the **parallel-shift / load-independence test** (§V-A): median per-site 2013–25 change −2.25 MVAr overnight (TP 1–12) vs −2.42 MVAr at evening peak (TP 35–39), median per-site ratio 1.06, on 114 clean GXPs with both endpoints (its `results.json`, `unmasking` block; that notebook works leading-positive — signs flipped here to this suite's convention). Its median peak-load change reads +3.4% because its screen table is frozen on the pre-14-Mar-2026 processed vintage; the ICP notebook's native run on the corrected archive reads **+2.9%**, which is the paper's print — the Q-side per-site medians agree between vintages to < 0.01 MVAr (they are median-immune to the duplicate rows). |

**Release-blocker resolved 7 Aug 2026 eve:** the parallel-shift test and the paper's
§V-B national sums are now computed **natively in the ICP notebook** (cell a2, archive
direct: n = 114; −188 → +182 MVAr night-median, deepening +369; p99 variant +314;
157–214 VAr/household; parallel-shift +2.25/+2.42/1.06 with peak-load change +2.9% on
the corrected 13-Aug-2026 archive — the harmonics cross-check's +3.4% is the same
quantity on the superseded vintage). The harmonics workings notebook remains indexed
as an independent cross-validation only — no longer required for release. The ICP
notebook is release-clean and ships with its raw EMI extract; it now reads the pf
half-hourly archive (`data/analysis/`, rebuilt 13 Aug 2026 by the corrected
`calculate_power_factors.py`), the same source the suite's notebook 00 documents.

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
| **96** | the 114 resolved into attribution units by the 8-Aug correspondence audit (8 industrial + 2 no-endpoint + 1 unresolvable excluded; 14 members aggregated into 7 station/churn groups; 103 members represented) | §V-C scaling regression (headline) |
| **92** | panel units with metering *and* registry present throughout 2009–2025 | §V-C coefficient history β(t) |
| **83** | legacy: screen-table 90 ∩ per-code ICP join | §V-C original pre-registered run (labelled consistency result; report both, never blend) |
| **81** | legacy: the 83 present throughout 2009–2025 | superseded β(t) run (in-notebook history note only) |
| **90** | legacy screen-table clean panel | legacy-panel derivation + harmonics documents (superseded for paper quotes by the 114) |

### Sign conventions (three, deliberate; never compare without flipping)

- **This suite and the paper: `Q < 0` = leading** (capacitive, voltage-raising).
- The ICP notebook's screen cells and the harmonics workings notebook compute
  **leading-positive** (leading = +); the ICP notebook's paper-facing cells and
  figure flip to the paper's Q-signed convention and say so in place.

Glowworm evidence tags: `[V]` verified vs primary source · `[I]` inferred · `[H]` hypothesis.

## Figure map (filename ↔ paper figure number)

Both tiers embed **vector PDFs** (23 Aug 2026 conversion: serif, no Type-3 fonts, which
IEEE does not accept). The journal tier draws Figs. 1–3 from column-width variants that
live in `../ieee-pf-trajectory-paper/figures/`, because the shared exhibits were being
scaled down by more than a factor of two on a single-column page.

| File | Journal (10 pp) | Extended (28 pp) |
|---|---|---|
| `01_trajectory_journal.pdf` *(paper/figures)* | Fig. 1 | — |
| `02_dose_response_journal.pdf` *(paper/figures)* | Fig. 2 | — |
| `03_level_journal.pdf` *(paper/figures)* | Fig. 3 | — |
| (in-TeX TikZ mains-filter schematic) | Fig. 4 | Fig. 9 |
| `06_connection_scaling.pdf` | Fig. 5 | Fig. 5 |
| `07_class_split.tex` (TikZ) / `07_class_split.pdf` | Fig. 6 *(TikZ `\input`)* | Fig. 6 *(PDF)* |
| `01_trajectory.pdf` | — | Fig. 1 |
| `01_clean_cohort.pdf` | — | Fig. 2 |
| `02_methods.pdf` | — | Fig. 3 |
| `03_physical_charging.pdf` | — | Fig. 4 |
| (in-TeX TikZ two-loop cascade taxonomy) | — | Fig. 7 |
| `01_splice_test.pdf` | — | Fig. 8 |

Other files in `figures/` (`02_clean_cohort`, `02_dose_response`, `04_archetypes`,
`05_capacitors_out`) are notebook exhibits not placed in either paper version.

### Generated files, and which generator owns each

Several artefacts carry a "GENERATED — do not edit by hand" contract. A hand-fix to one of
them comes back on the next run; this has bitten the project three times, so the ownership
is written down here.

| Artefact | Its one generator | Note |
|---|---|---|
| `figures/07_class_split.tex` and `.png` | `src/07_anzsic_class_split.py` | Reproduces byte-for-byte. |
| `cache/anzsic_class_split.json` | `src/07_anzsic_class_split.py` | The §V-C canonical values. |
| `figures/06_connection_scaling.pdf` and `.png` | `../ieee-pf-trajectory-paper/MAKE_FIG_CONNECTION_SCALING.py` | Re-executes the ICP notebook's analysis cells, stops before its figure cell, redraws at column width. |
| `../ieee-pf-trajectory-paper/icp-regression/icp_regression_results_20260806.json` | `icp_regression.ipynb` — **not** `icp_regression_20260806.py` | The notebook writes all 18 keys; the 6 Aug script is the superseded first run and writes 9 different ones. It now writes only `*_legacy_firstrun` names so it cannot stand in for the notebook. |
| `../ieee-pf-trajectory-paper/refs_journal.bib` | `../ieee-pf-trajectory-paper/make_journal_bib.py` | Derived from `refs.bib`; regenerates byte-for-byte. |
| `notebooks/*.ipynb` | `build_notebooks.py` (from `src/*.py`) | Takes selective arguments — `python build_notebooks.py 07` rebuilds only notebook 07. A rebuild **wipes executed outputs**, so re-execute afterwards. |

## Citing

- **Journal version** (in preparation for submission, 2026): D. Hume, ``From
  Lagging to Leading: The Measured Emergence of Standing Capacitance Behind
  Consumer Connections, 1997--2025.''
- **Extended version + this package:** D. Hume, extended version and
  reproducibility package, GitHub repository with Zenodo snapshot, 2026.
  DOI: [10.5281/zenodo.21927098](https://doi.org/10.5281/zenodo.21927098)
  (reserved 14 Aug 2026; resolves once the record is published). The journal
  version's reference `hume_extended` carries the same DOI.

## How to run

```bash
# environment: Python 3.12.3 + the pinned package set in requirements-pass7.txt
# (the versions that produced every shipped execution, figure, and results JSON)
pip install -r requirements-pass7.txt

cd replication
python build_notebooks.py                     # src/*.py  ->  notebooks/*.ipynb
cd notebooks
# run 00 first (it builds the cache the others read), then the rest in any order:
for nb in 0*.ipynb; do jupyter nbconvert --to notebook --execute --inplace "$nb"; done

# then the connection-scaling notebook (§V) — reads the pf half-hourly archive
# plus this suite's contamination flag, and carries its own 91-assertion battery:
cd ../../icp-regression 2>/dev/null || cd ../../ieee-pf-trajectory-paper/icp-regression
jupyter nbconvert --to notebook --execute --inplace icp_regression.ipynb

# guard scripts (pure arithmetic checks of the paper's §V-B dose figures):
python ../replication/src/mains_dose_check.py
```

### Data access (hybrid design)

- **Default (offline, recommended):** the notebooks read the cleaned per-year EMI parquet
  files and the Commerce Commission disclosure parquet that ship with the project, and
  `00_data_acquisition` builds the two analysis-ready caches (`cache/`). Everything else runs
  from those plus public physics constants. One judgment table is a hard input:
  `data/metadata/edb_mapping.py` (the EMI-code → lines-company lookup, imported by
  `repro.py` at load) — it ships with the data set alongside the ComCom parquet.
- **Rebuild from source:** the path from raw public records is fully scripted —
  `scripts/download_emi_data.py` + `scripts/process_to_parquet.py` (EMI half-hourly grid
  metering, emi.ea.govt.nz) build the per-year processed parquets, and
  `scripts/calculate_power_factors.py` (corrected 13 Aug 2026 for the 3-level schema)
  builds the per-year `pf_by_gxp` / `pf_by_group` archive the connection-scaling notebook
  reads; the Commerce Commission information-disclosure parquet has its own downloader
  (comcom.govt.nz). All of these ship in the data archive's `code/builders/`. Run those,
  then re-run notebook 00.
- The production data lives on a network mount that is slow for batch reads. If a local stage
  exists at `/tmp/pf_stage` (set `PF_STAGE` to override) the notebooks use it automatically;
  otherwise they fall back to the bundled project data. `PF_PROCESSED_DIR` and
  `PF_COMCOM_PARQUET` override individual sources.

## Files

```
replication/
├── README.md                  this file
├── FRESH_EYES_REVIEW.md       what reproduced, what didn't, and the precision findings
├── requirements-pass7.txt     the pinned environment (Python 3.12.3)
├── repro.py                   shared plumbing ONLY (paths, plot style, name maps) — no analysis
├── build_notebooks.py         percent-.py  ->  .ipynb converter (a tiny jupytext stand-in)
├── src/                       the readable percent-format notebook sources (edit these;
│                              includes mains_dose_check.py, the §V-B dose guard)
├── notebooks/                 the executed .ipynb (build artifacts; regenerated from src/)
├── cache/                     analysis-ready tables built by notebook 00
└── figures/                   publication figures saved by the notebooks
```

Edit the `src/*.py` files (clean diffs, easy review), then `python build_notebooks.py` to
regenerate the notebooks. The `repro.py` module deliberately holds *no analytical decisions* —
all analysis is visible inside the notebooks so it can be audited without opening a library.

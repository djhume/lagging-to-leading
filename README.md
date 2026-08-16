# From Lagging to Leading

**The measured emergence of standing capacitance behind consumer connections —
New Zealand, 1997–2025.**

Using 29 years of regulatory half-hourly metering at New Zealand grid exit
points, this work measures a national power system's reactive character
crossing from lagging to leading overnight (2016), attributes the drift
dominantly to the demand side (about 80%, physical band 75–88%, by a
first-principles charging calculation with no fitted cable coefficient), and
identifies what the demand side is physically doing: accumulating **standing
distributed capacitance** — about 220 VAr per connection added over 2013–2025,
with no detectable connection-independent residual, from a per-connection term
that sat on the inductive side of zero in 2009, crossed zero about 2012, and
accumulated faster over the second half of that window than the first. The
mandated electromagnetic-compatibility filter in every switched-mode device is
advanced as the candidate device layer (a labelled hypothesis), with the
decisive low-voltage measurement identified. Both inputs to the scaling test —
settlement metering and connection counts — are records any system operator
already holds, so the measurement is portable to any system.

## The two versions

| Version | File | What it is |
|---|---|---|
| **Extended version** (23 pp) | [`paper/extended-version.pdf`](paper/extended-version.pdf) | The complete record: adds Appendix A (the full measurement-error analysis and the system-wide re-base/"splice" test), Appendix B (the mains input filter at 50 Hz), the two-loop cascade taxonomy, a Future Work section, and the supporting cohort/method exhibits |
| **Journal version — draft** (15 pp) | [`paper/journal-version-draft.pdf`](paper/journal-version-draft.pdf) | Reduced for journal submission (sections I–VIII): every claim, its supporting evidence, and every hedge stay in-paper; robustness depth, derivations, censuses, and worked exhibits are cited out to the extended version. **Draft of 16 Aug 2026, not yet submitted.** |

Both are builds of 16 Aug 2026. The journal tier is the reduced form: it
was cut from 18 pp to 15 pp on 14–15 Aug 2026 by moving depth to
extended-version pointers, with no claim, printed number, or hedge changed (a
numeric-token diff against the 18-pp build verifies every surviving number
byte-identical and every removed number present in the extended version).
On 16 Aug 2026 a bounded wording correction was applied to both versions
(the confound-screen passage no longer asserts that Transpower
voltage-regulating plant registers inside the revenue-metering boundary —
the screen itself and every number are unchanged), and a one-sentence note
of a companion circuit-model study in preparation was added; the
numeric-token diff was re-run and remains clean.

The LaTeX sources are alongside the PDFs: `paper/main.tex` builds
`journal-version-draft.pdf` and `paper/main_extended_20260808.tex` builds
`extended-version.pdf`, sharing `paper/refs.bib` (IEEEtran class files
included, so `pdflatex` + `bibtex` reproduce both from a clone).

The connection-scaling test runs on the
96-unit correspondence-audited panel (8 Aug rebase), with the original
pre-registered 83-site run retained as a labelled consistency result; on
13 Aug 2026 the underlying per-year archive was rebuilt after duplicate
dual-network rows in the March vintage were found double-counting Q at three
aggregation-group panel points, and the headline family was corrected (slope
about 220–230 VAr per connection; the intercept now spans zero under every
inference scheme). The paper's pass-7 reproducibility record documents the
defect, the correction, and the re-verification.

## What's in this repository

- [`replication/`](replication/) — six companion notebooks that reproduce every
  headline number from public data, written in plain English for a mixed
  audience, plus the pinned environment (`requirements-pass7.txt`) and the
  §V-B dose guard (`src/mains_dose_check.py`). Start at
  [`replication/README.md`](replication/README.md), which carries the
  notebook→section map, the panel taxonomy, the sign-convention rules, and the
  figure map.
- [`icp-regression/`](icp-regression/) — the connection-scaling test, the
  registry↔metering correspondence audit, and the coefficient history (paper
  §V), executed in place with a 91-assertion battery, shipping with its raw
  public-data extract.
- [`data/metadata/`](data/metadata/) — `edb_mapping.py`, the EMI-code →
  lines-company judgment table the suite imports (the remaining data inputs
  are distributed in the accompanying data archive; see below).
- [`paper/`](paper/) — the paper itself.

## Data

Everything is computed from **public data**: Electricity Authority grid
metering (EMI, emi.ea.govt.nz) and Commerce Commission information
disclosures (comcom.govt.nz), both published under Creative Commons
Attribution 4.0 licences. Small extracts and analysis-ready caches ship in
this repository; the full inputs — the raw EMI monthly extracts as consumed,
the derived per-year parquet archives, the judgment tables with provenance
notes, and the builder scripts — ship together in the accompanying **data
archive** (Zenodo record,
DOI [10.5281/zenodo.21927098](https://doi.org/10.5281/zenodo.21927098)),
whose SHA-256 manifest is OpenTimestamps-anchored.

## Reproducing

```bash
pip install -r replication/requirements-pass7.txt   # Python 3.12.3 pin
cd replication
python build_notebooks.py
cd notebooks
# run 00 first (builds the caches), then the rest in any order
for nb in 0*.ipynb; do jupyter nbconvert --to notebook --execute --inplace "$nb"; done
# then the connection-scaling notebook (91-assertion battery):
cd ../../icp-regression
jupyter nbconvert --to notebook --execute --inplace icp_regression.ipynb
```

The suite expects the per-year data archives at `data/processed/` and
`data/analysis/` (unpack them there from the data archive, or point
`PF_PROCESSED_DIR` at them); `replication/README.md` documents the layout.

## Citing

Until the journal version is published, cite the extended version and this
repository:

> D. Hume, *From Lagging to Leading: The Measured Emergence of Standing
> Capacitance Behind Consumer Connections, 1997–2025* (extended version and
> reproducibility package), 2026. GitHub: djhume/lagging-to-leading.
> DOI: [10.5281/zenodo.21927098](https://doi.org/10.5281/zenodo.21927098).

A `CITATION.cff` is included (GitHub's "Cite this repository" button uses it).

## Status and licence

- **Status:** private pre-release. The journal version is being prepared for
  submission.
- **Licence:** to be finalised before public release (intended: open licence
  for code and notebooks; data redistributed under the custodians' CC BY 4.0
  terms with attribution to the Electricity Authority and the Commerce
  Commission; the paper PDF © the author).
- The views expressed are the author's. The analysis is descriptive: it
  informs, but does not advocate on, a live reactive-power pricing policy
  question.

## Author

David Hume — ORCID [0009-0006-6920-0598](https://orcid.org/0009-0006-6920-0598).

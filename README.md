# From Lagging to Leading

**The measured emergence of standing capacitance behind consumer connections —
New Zealand, 1997–2025.**

Using 29 years of regulatory half-hourly metering at New Zealand grid exit
points, this work measures a national power system's reactive character
crossing from lagging to leading overnight (2016), attributes the drift
dominantly to the demand side (about 80%, physical band 75–88%, by a
first-principles charging calculation with no fitted cable coefficient), and
identifies what the demand side is physically doing: accumulating **standing
distributed capacitance** — about 250 VAr per connection added over 2013–2025,
with nothing left at zero connections, from a per-connection term that was
indistinguishable from zero until about 2012 and is accelerating. The mandated
electromagnetic-compatibility filter in every switched-mode device is advanced
as the candidate device layer (a labelled hypothesis), with the decisive
low-voltage measurement identified. Both inputs to the scaling test —
settlement metering and connection counts — are records any system operator
already holds, so the measurement is portable to any system.

## The two versions

| Version | File | What it is |
|---|---|---|
| **Extended version** (16 pp) | [`paper/extended-version.pdf`](paper/extended-version.pdf) | The complete record: adds Appendix A (the full measurement-error analysis and the system-wide re-base/"splice" test), Appendix B (the mains input filter at 50 Hz), and the supporting cohort/method exhibits |
| **Journal version** (14 pp) | *added at submission* | Condensed for the IEEE Open Access Journal of Power and Energy; identical section numbering (I–IX); every claim, headline number, and hedge |

## What's in this repository

- [`replication/`](replication/) — six companion notebooks that reproduce every
  headline number from public data, written in plain English for a mixed
  audience. Start at [`replication/README.md`](replication/README.md), which
  carries the notebook→section map, the panel taxonomy, the sign-convention
  rules, and the figure map.
- [`icp-regression/`](icp-regression/) — the connection-scaling test and
  coefficient history (paper §V), executed in place with a 47/47 assertion
  battery, shipping with its raw public-data extract.
- [`paper/`](paper/) — the paper itself.

## Data

Everything is computed from **public data**: Electricity Authority grid
metering (EMI, emi.ea.govt.nz) and Commerce Commission information
disclosures (comcom.govt.nz). Small extracts and analysis-ready caches ship
in this repository; the full half-hourly archive (~1.2 GB) is not included —
the scripted path from the raw public records is documented in
[`replication/README.md`](replication/README.md) (data-access section).
Release of any underlying extract is subject to the data custodians' terms.

## Reproducing

```bash
pip install pandas numpy scipy scikit-learn statsmodels ruptures matplotlib nbformat jupyter
cd replication
python build_notebooks.py
cd notebooks
# run 00 first (builds the caches), then the rest in any order
for nb in 0*.ipynb; do jupyter nbconvert --to notebook --execute --inplace "$nb"; done
```

## Citing

Until the journal version is published, cite the extended version and this
repository:

> D. Hume, *From Lagging to Leading: The Measured Emergence of Standing
> Capacitance Behind Consumer Connections, 1997–2025* (extended version and
> reproducibility package), 2026. GitHub: djhume/lagging-to-leading.
> DOI: *to be minted via Zenodo at public release.*

A `CITATION.cff` is included (GitHub's "Cite this repository" button uses it).

## Status and licence

- **Status:** private pre-release. The journal version is being prepared for
  submission to the IEEE Open Access Journal of Power and Energy.
- **Licence:** to be finalised before public release (intended: open licence
  for code and notebooks; data extracts remain under their custodians' terms;
  the paper PDF © the author).
- The views expressed are the author's. The analysis is descriptive: it
  informs, but does not advocate on, a live reactive-power pricing policy
  question.

## Author

David Hume — ORCID [0009-0006-6920-0598](https://orcid.org/0009-0006-6920-0598).

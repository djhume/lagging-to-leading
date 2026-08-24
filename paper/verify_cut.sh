#!/usr/bin/env bash
# verify_cut.sh — the deterministic gate for the reader-review cut passes (17 Aug 2026).
#
# Every workflow agent calls THIS rather than assembling its own checks, so verification
# never depends on an agent remembering to do it. Exit 0 = GREEN, exit 1 = RED.
#
#   usage:  bash verify_cut.sh [label]
#
# HARD checks (any failure = RED, halt the chain):
#   1. journal tier builds
#   2. 0 overfull boxes
#   3. 0 undefined references/citations
#   4. bibliography still BIB_BASELINE entries  <- the single-use-citation trap: a cut
#      that drops the only \cite of a reference renumbers every later one and destroys
#      the L4 proof. RE-BASELINE DELIBERATELY, never by silencing a failure, and record
#      the move here:
#        41 -> 42 -> 44   17 Aug, cold-read / re-registration session
#        40 -> 39         18 Aug, Pass-5b repair sitting: powerco_pricing_fy26
#                         dropped with the VI-D compression that PAID for the
#                         F1/F3/F7 + gloss restorations (Dave's "less NZ data"
#                         steer). Verified still cited in the extended tier.
#        44 -> 40         18 Aug, TPWRS venue cut, tranche 1 + prime candidates:
#                         aemo_tcpf (I-B AEMO para), egr_partf_r11 + ec_cds2004
#                         (II-B provenance para), eu_emc1989 (V-B mandate-history
#                         para, cut B2). All four verified still cited in the
#                         extended tier -- nothing left the record.
#        39 -> 28         22 Aug, 10-pp submission cut, reference tranches 1a+1b.
#                         Standards carried in running text instead of as entries
#                         (iec61000_3_2, iec62053_22, iec62053_23, ieee1459,
#                         cispr32, iec60384_14, ieee1547); source chains delegated
#                         to the extended (ehinz_heating, ross_meier2000,
#                         edlington2006); and psarros2022, the redundant second
#                         cite on "well documented" beside vournas2021. All eleven
#                         verified still cited in the extended tier -- nothing left
#                         the record. Adjudicated one by one; the novelty-positioning
#                         set (vournas2026review, entsoe_iberia, entsoe_nm,
#                         kaloudas2014/2017, bosisio2022, javed2024,
#                         baghbannovin2020) was held INTACT.
#        28 -> 27         22 Aug, same session: heep_sr155, dropped with the HEEP
#                         nine-house witness sentence when Dave's steer compressed
#                         V-C ("way too over the top in detail -- summarise at a
#                         higher level"). Verified still cited in the extended.
#        27 -> 25         23 Aug, external review (ENTSO-E panel simulation),
#                         DISPLACEMENT. Dave's call on the review's own nomination:
#                         Section VI-D ("Coverage of existing reactive-power
#                         provisions") reduced to its point to pay for the review's
#                         accepted remedies at 10 pp. That uncites eipc_sch126 and
#                         eipc_part8 -- the EIPC Code navigation paths -- which leave
#                         the JOURNAL tier only. Both verified still cited in the
#                         extended tier, which carries VI-D in full, so nothing left
#                         the record. ** Flagged to Dave: those two were on the
#                         finishing kickoff's protected list. ** Reverse this first at
#                         R&R, where papers may exceed 10 pp. Bibliography hygiene in
#                         the same pass, from the review's section 4: the six standards
#                         got their INSTITUTION back as an acronym (the 22 Aug drop of
#                         author+institution together printed them as bare "Tech. Rep."
#                         with no issuing body, which a blind referee read as a defect),
#                         paid for by dropping the institution on eleven entries whose
#                         AUTHOR already names the same organisation, and by a short
#                         title for eu_lighting2020 (the full EU citation form ran four
#                         lines and IEEEtran title-cased it to "1 october 2019").
#        21 -> 27         23 Aug, Pass D (#123), R1's acceptance condition 6 --
#                         REVERSES the 22 Aug 'standards in running text' call, on a
#                         blind referee's measured objection: CISPR 32, IEC 61000-3-2,
#                         IEC 62053-22, IEC 62053-23, IEEE Std 1459 and IEEE Std 1547
#                         were each named in the text AS EVIDENCE with no entry. R1:
#                         "The CISPR 32 omission is the material one. That standard is
#                         the entire load-bearing premise of Section V-B." The entries
#                         already existed in refs.bib -- this was a missing \cite, not a
#                         missing reference. Paid for inside the bibliography, not from
#                         prose: make_journal_bib.py now also drops author, institution
#                         and address on the six standards (the publisher is named three
#                         times in a designation that already carries it) and the city on
#                         seven institutional tech reports. Still 10 pp, 0 overfull.
#                         ** 28 does NOT fit. ** A 28th entry (a primary standby-survey
#                         cite, R1's 1.7) spills one line onto page 11 and no prose trim
#                         moved the break. Deferred to R&R, where papers may exceed 10 pp.
#        27 -> 21         22 Aug, same session: Dave restored the EMC-filter figure
#                         ("not so happy about losing the EMC filter... not too
#                         fussed on the previous work/research"), and the I-A
#                         prior-work catalogue PAID for it -- kaloudas2014 (CIRED;
#                         the kaloudas2017 TPWRS paper is kept as the closest
#                         measured series), rte_bilan, powerlink_seq, hannagan2023,
#                         javed2024, baghbannovin2020. No claim was left unsourced:
#                         the jurisdiction catalogue and the boundary-study list now
#                         point at hume_extended, which carries all six. bosisio2022
#                         (closest decomposition), vournas2026review and entsoe x2
#                         remain INTACT.
#        20 -> 21         23 Aug, Pass A follow-on: wecc_cmpldw ADDED (not a cut).
#                         Dave asked for the VII composite-load-model sentence --
#                         the WECC spec says the feeder reactive compensation is a
#                         residual back-solved from the power-flow Q and is then
#                         'tripped in proportion to the MW of each component
#                         tripped'. That is a primary-source structural finding and
#                         it must be citable, so the entry is load-bearing. Text
#                         extracted and swept 23 Aug; agrees with the Apr 2021
#                         edition read for literature_review.md C11a.
#        21 -> 20         23 Aug, Pass A: esr_reg28 dropped with the ESR reg 28
#                         band-widening paragraph, cut from VI-D on Dave's call
#                         ("a very NZ inc. one... a few weeks at the end of a
#                         29 year series is zero; it can stay in the extended
#                         but is not required in the main.pdf"). The paragraph
#                         and its fuller quantified treatment (omega C V^2: ~2%
#                         more reactive power per 1% of sustained voltage
#                         elevation, ~8% at the new ceiling) are RETAINED IN THE
#                         EXTENDED, which carries the DOI -- verified still
#                         cited there. Nothing left the record.
#   5. every named load-bearing hedge still present at least once (whitespace-normalised,
#      because the tex line-wraps mid-sentence — a plain grep gives false negatives)
#   6. L4 numeric-token diff GREEN (no value drift; nothing left the record entirely)
#
# REPORTED, not gated: page count, per-hedge counts, L4 added-values list.

set -uo pipefail
cd "$(dirname "$0")" || exit 1
LABEL="${1:-unlabelled}"
RED=0

echo "════════ verify_cut.sh · ${LABEL} ════════"

# ---- 1. build ------------------------------------------------------------
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1
bibtex main >/dev/null 2>&1
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1
if [[ ! -f main.pdf ]]; then echo "RED  build: main.pdf not produced"; exit 1; fi

PAGES=$(pdfinfo main.pdf | awk '/^Pages:/{print $2}')
OVERFULL=$(grep -c 'Overfull' main.log || true)
UNDEF=$(grep -c 'Warning.*undefined' main.log || true)
BIB=$(grep -c '\\bibitem' main.bbl || true)

# TPWRS hard cap is 10 pages INCLUDING references (venue re-pointed 17 Aug 2026,
# OAJPE -> TPWRS; see TPWRS_CUT_KICKOFF_20260817.md). Reported loudly but NOT a
# hard fail: the tier is legitimately over during the cut pass itself. The <=10pp
# assertion is acceptance check #2 at the end of that pass, not a per-build gate.
TPWRS_CAP=10
if [[ "$PAGES" -gt "$TPWRS_CAP" ]]; then
  printf 'pages      %s   >>> OVER the TPWRS cap of %s by %s pp <<<\n' \
         "$PAGES" "$TPWRS_CAP" "$((PAGES - TPWRS_CAP))"
else
  printf 'pages      %s   (within the TPWRS cap of %s)\n' "$PAGES" "$TPWRS_CAP"
fi

# ---- 2/3. box + reference hygiene ---------------------------------------
if [[ "$OVERFULL" -ne 0 ]]; then echo "RED  overfull boxes: $OVERFULL (must be 0)"; RED=1
else echo "ok   overfull 0"; fi
if [[ "$UNDEF" -ne 0 ]];    then echo "RED  undefined refs/cites: $UNDEF (must be 0)"; RED=1
else echo "ok   undefined 0"; fi

# ---- 4. bibliography count ----------------------------------------------
BIB_BASELINE=25   # see the header ledger before changing this (27 -> 25, 23 Aug)
if [[ "$BIB" -ne "$BIB_BASELINE" ]]; then
  echo "RED  bibliography $BIB entries (baseline $BIB_BASELINE) — a cut dropped a unique \\cite;"
  echo "     every later reference has renumbered and the L4 proof is void."
  RED=1
else echo "ok   bibliography $BIB"; fi

# ---- 5. named hedges (whitespace-normalised) ----------------------------
HEDGE_OUT=$(python3 - <<'PY'
import sys
flat = ' '.join(open('main.tex').read().split())
hedges = {
    "no-tight-interval":      "deliberately publish no tight interval on the share",
    # "pre-commencement" RETIRED from the journal check 23 Aug (Pass A). It was
    # the only site of the hedge and it left with the ESR reg 28 paragraph, cut
    # from VI-D as NZ-specific for an international venue (Dave's call). The
    # hedge and the full disclosure REMAIN IN THE EXTENDED -- checked there, not
    # here. This is a deliberate re-baseline, not a silenced failure: if the
    # journal ever re-acquires the endpoint/commencement discussion, restore it.
    "labelled-hypothesis":    "labelled hypothesis",
    "physical-band":          "physical band 75",
    "to-our-knowledge":       "to our knowledge",
}
bad = 0
for name, s in hedges.items():
    n = flat.count(s)
    print(f"{'ok  ' if n else 'RED '} hedge {name}: {n}")
    if not n:
        bad = 1
sys.exit(bad)
PY
)
echo "$HEDGE_OUT"
if echo "$HEDGE_OUT" | grep -q '^RED'; then
  echo "     a load-bearing hedge was removed entirely — settled decision 3 violated."
  RED=1
fi

# ---- 6. L4 numeric-token diff -------------------------------------------
L4=$(python L4_NUMBER_DIFF_20260815.py 2>&1)
if echo "$L4" | grep -q 'VERDICT: GREEN'; then
  echo "ok   L4 numeric diff GREEN"
  echo "$L4" | grep -E '^ +[0-9]' | sed 's/^/     added: /' || true
else
  echo "RED  L4 numeric diff NOT green:"
  echo "$L4" | tail -6 | sed 's/^/     /'
  RED=1
fi

echo "────────"
if [[ "$RED" -eq 0 ]]; then echo "VERDICT: GREEN (${LABEL}, ${PAGES} pp)"; exit 0
else echo "VERDICT: RED (${LABEL}) — HALT, do not proceed to the next cut"; exit 1; fi

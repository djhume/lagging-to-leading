"""make_journal_bib.py -- generate refs_journal.bib for the TPWRS journal tier.

The 10-page TPWRS cap makes the bibliography 17% of the whole page budget, and
refs.bib carries long `note = {...}` fields (edition histories, CELEX numbers,
consolidation dates) that are the project's citation-verification record but are
NOT IEEE Transactions house style. This script strips those notes for the
JOURNAL tier only.

refs.bib itself is never modified, so the extended tier -- the complete record --
keeps every annotation. Run this whenever refs.bib changes; main.tex builds
against the generated file.

KEPT deliberately: notes on the New Zealand regulatory instruments (eipc_*,
esr_reg28). Those carry the full Code navigation path (Part / Schedule / clause),
and per the project's EIPC citation standard a bare Connection Code cite is
unfindable. Their notes are load-bearing, not bibliographic decoration.

Usage:  python make_journal_bib.py     (writes refs_journal.bib, reports saving)
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "refs.bib"
DST = HERE / "refs_journal.bib"

# Entries whose note carries a Code navigation path. These are NOT stripped --
# a bare Connection Code cite is unfindable, so the Part / Schedule / clause path
# must survive into the journal tier. They ARE shortened: the path and clause are
# kept verbatim, the prose gloss dropped, because the body text already states
# what each provision does. refs.bib keeps the full note for the extended tier.
# Entries whose `url` is dropped from the JOURNAL tier only. Long URLs cost far
# more column space than their word count -- they do not hyphenate, so each one
# forces several short lines. These four are the longest (100-163 chars), and each
# document is unambiguously identifiable from publisher + title; refs.bib keeps
# every URL for the extended tier, and the Wayback captures made in the R2 pass
# are the durable record. Short, high-value URLs (ENTSO-E landing page, the Code
# parts, the legislation, the EMI dataset) are all retained.
DROP_URL = (
    "powerlink_seq",          # 163 chars
    "transpower_ssf2024n1",   # 137
    "entsoe_nm",              # 136, a fragile CDN blob link
    "transpower_tpr2023",     # 100
    "transpower_ssf2022",     # 91; all four Transpower docs treated alike
    # Extended 22 Aug 2026 (10-pp submission cut). Same reasoning, applied once
    # more under a harder cap: each of these is unambiguously identifiable from
    # publisher + title + (for the instruments) the clause path in the note, and
    # every one has an R2-pass Wayback capture. refs.bib keeps them all.
    "rte_bilan",              # 82
    "esr_reg28",              # 82, a DLM deep link
    "entsoe_iberia",          # 75
    "eipc_part10",            # 75
    # Added 23 Aug 2026 with the VII composite-load-model sentence.
    "wecc_cmpldw",            # 118, a percent-encoded meeting-folder path that
                              # does not hyphenate and forces four short lines.
                              # The document is unambiguously identifiable from
                              # publisher + title, and refs.bib keeps both the URL
                              # and the verbatim Bfdr / MW-trip quotations for the
                              # extended tier.
    # emi_icp's URL is RETAINED: it is the dataset a reader needs to reproduce
    # the connection-scaling test, not a locator for a named document.
)

# Long titles trimmed for the JOURNAL tier only (10-pp cap). The instrument is
# still fully named; only parenthetical glosses and the SR number go, both of
# which the clause path in the retained note already implies. refs.bib is intact.
SHORT_TITLES = {
    # The full citation form of an EU regulation ("... of 1 October 2019 laying down
    # ecodesign requirements for ...") runs four lines in a two-column bibliography and
    # IEEEtran title-cases it into "1 october 2019". The number IS the identifier.
    "eu_lighting2020": "Commission Regulation ({EU}) 2019/2020: ecodesign requirements "
                       "for light sources and separate control gears",

    "esr_reg28": "Electricity (Safety) Regulations 2010, regulation 28 "
                 "(voltage supply to installations), as amended by {SL} 2025/225",

    # --- The six device/metering standards, cited in the journal tier from 23 Aug
    # 2026 (Pass D, R1's acceptance condition 6: each was named in the text as
    # evidence and none was in the reference list). refs.bib keeps the full
    # consolidated-edition designations -- "CISPR 32:2015+AMD1:2019 CSV",
    # "IEC 61000-3-2:2018+AMD1:2020+AMD2:2024 CSV" -- which are the project's
    # verification record, not IEEE house style. The journal tier keeps the
    # designation and the substantive title and drops the amendment string.
    "cispr32":      "{CISPR}~32: Electromagnetic compatibility of multimedia "
                    "equipment---emission requirements",
    "iec61000_3_2": "{IEC}~61000-3-2: Limits for harmonic current emissions "
                    "(equipment input current {$\\leq$}16~{A} per phase)",
    "iec62053_22":  "{IEC}~62053-22: Static meters for {AC} active energy "
                    "(classes {0,1S}, {0,2S} and {0,5S})",
    "iec62053_23":  "{IEC}~62053-23: Static meters for reactive energy "
                    "(classes 2 and 3)",
    "ieee1459":     "{IEEE} {Std} 1459-2010: Definitions for the measurement of "
                    "electric power quantities",
    # 24 Aug citation pass: "and interoperability" restored. Dropping it made the
    # short form read as IEEE Std 1547-2003's scope, i.e. it named a DIFFERENT
    # standard; the 2018 revision's identity is the interoperability half. Costs
    # 21 characters and was build-verified at 10 pp. The full official title --
    # "...of Distributed Energy Resources with Associated Electric Power Systems
    # Interfaces" -- does NOT fit: with ieee1459's full title it measures 11 pp.
    "ieee1547":     "{IEEE} {Std} 1547-2018: Interconnection and interoperability "
                    "of distributed energy resources",
}

# Standards carry the publisher in the designation itself, so IEEE house style
# does not repeat a city -- or the organisation as author -- for them. As printed
# before this trim, [27] read "Institute of Electrical and Electronics Engineers,
# 'IEEE std 1547-2018: ...,' IEEE, Tech. Rep., 2018" -- the publisher three times
# in one entry. Journal tier only; refs.bib keeps author, institution and address.
DROP_ADDRESS = ("cispr32", "iec61000_3_2", "iec62053_22", "iec62053_23",
                "ieee1459", "ieee1547")
DROP_AUTHOR = DROP_ADDRESS
# The institution is NOT dropped, and the earlier decision to drop it is reversed.
# Rationale for the reversal (external review, 23 Aug 2026, section 4): with author
# AND institution stripped, IEEEtran prints these six as a bare `"<title>," Tech.
# Rep., <year>.` and a blind reviewer read them as "formatted as bare technical
# reports with no issuing body". The designation does name the publisher, but the
# publisher slot reading "Tech. Rep." with nothing in front of it is what the page
# shows. Keeping the institution -- as an acronym, so it is named exactly once
# outside the designation -- costs a few characters and fixes the printed form.
# Entries whose AUTHOR field already names the issuing organisation, so the
# institution slot prints the same body a second time in the same entry:
# "Transpower New Zealand (System Operator), '...', Transpower New Zealand
# Limited, Tech. Rep." This is the same redundancy rule the standards block above
# applies from the other side (there the designation names the body and the author
# is dropped; here the author names it and the institution is dropped). Every one
# of these still prints an issuing body -- the review's complaint was entries that
# print NONE. Journal tier only; refs.bib keeps every field.
DROP_INSTITUTION = ("transpower_ssf2022", "transpower_ssf2024n1", "transpower_tpr2023",
                    "wecc_cmpldw", "entsoe_iberia", "entsoe_nm", "epri_loadmodel",
                    "eipc_part10", "eipc_sch126", "eipc_part8", "cigre_tb719")
# Journal-tier institution, shortened to the acronym so the two-column bibliography
# does not carry "International Electrotechnical Commission" beside a title that
# already opens "IEC ...". refs.bib keeps the full names.
SHORT_INSTITUTIONS = {
    "cispr32":      "IEC",
    "iec61000_3_2": "IEC",
    "iec62053_22":  "IEC",
    "iec62053_23":  "IEC",
    "ieee1459":     "IEEE",
    "ieee1547":     "IEEE",
}

# City names on institutional technical reports. IEEE tolerates their omission and
# each costs a line-fragment in a two-column bibliography; publisher + title
# identifies every one of these unambiguously. refs.bib keeps them all.
DROP_ADDRESS_EXTRA = ("transpower_ssf2022", "transpower_ssf2024n1",
                      "transpower_tpr2023", "eipc_sch126", "eipc_part8",
                      "eipc_part10", "wecc_cmpldw", "ross_meier2000")

SHORT_NOTES = {
    "eipc_sch126": "Part~12, Schedule~12.6, Schedule~8 (Connection Code), "
                   "cl~4.4; consolidation as at 1~July 2026",
    "eipc_part8":  "cl~8.67(4)(a); consolidation as at 1~July 2026",
    "eipc_part10": "cl~10.37(2)(a) and Schedule~10.1, Tables~1, 5, 6; "
                   "consolidation as at 1~April 2025",
    # esr_reg28's note was dropped 22 Aug (10-pp cut): unlike the eipc_* notes it
    # carried a commencement pin, not a Code navigation path, and the body text
    # already states the 13 November 2025 date. refs.bib keeps it.
}

HEADER = """%% refs_journal.bib -- GENERATED, DO NOT EDIT BY HAND.
%% Produced by make_journal_bib.py from refs.bib for the TPWRS journal tier:
%% bibliographic `note` fields removed to fit the 10-page cap. The extended
%% tier builds against refs.bib and keeps every note. Notes on the NZ
%% regulatory instruments (eipc_*, esr_*) are retained -- they carry the Code
%% navigation path, without which the cite is unfindable.
"""


def find_matching_brace(text: str, open_idx: int) -> int:
    """Index just past the '}' matching the '{' at open_idx."""
    depth = 0
    i = open_idx
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced braces in refs.bib")


def rewrite_note(entry: str, replacement: str | None) -> tuple[str, int]:
    """Drop the note field, or replace it with `replacement`.

    Returns (entry, net_words_removed).
    """
    m = re.search(r",\s*\n\s*note\s*=\s*\{", entry)
    if not m:
        return entry, 0
    brace = entry.index("{", m.end() - 1)
    end = find_matching_brace(entry, brace)
    old = entry[brace + 1 : end - 1]
    if replacement is None:
        # Drop from the preceding comma through the note's closing brace.
        return entry[: m.start()] + entry[end:], len(old.split())
    new = entry[: brace + 1] + replacement + entry[end - 1 :]
    return new, len(old.split()) - len(replacement.split())


def main() -> int:
    src = SRC.read_text()
    out, saved, stripped, kept, dropped_urls = [], 0, 0, 0, 0
    shortened_inst = 0
    shortened_titles = 0
    dropped_addr = 0
    dropped_auth = 0
    dropped_inst = 0
    pos = 0
    for m in re.finditer(r"@\w+\s*\{", src):
        if m.start() < pos:
            continue
        out.append(src[pos : m.start()])
        end = find_matching_brace(src, m.end() - 1)
        entry = src[m.start() : end]
        key = re.match(r"@\w+\s*\{\s*([^,]+),", entry).group(1).strip()
        if key in DROP_URL:
            um = re.search(r",\s*\n\s*url\s*=\s*\{", entry)
            if um:
                ub = entry.index("{", um.end() - 1)
                entry = entry[: um.start()] + entry[find_matching_brace(entry, ub):]
                dropped_urls += 1
        if key in DROP_AUTHOR:
            aum = re.search(r"\n\s*author\s*=\s*\{", entry)
            if aum:
                aub = entry.index("{", aum.end() - 1)
                nxt = find_matching_brace(entry, aub)
                tail = entry[nxt:]
                tail = tail[1:] if tail.startswith(",") else tail
                entry = entry[: aum.start()] + tail
                dropped_auth += 1
        if key in DROP_INSTITUTION:
            im = re.search(r",\s*\n\s*institution\s*=\s*\{", entry)
            if im:
                ib = entry.index("{", im.end() - 1)
                entry = entry[: im.start()] + entry[find_matching_brace(entry, ib):]
                dropped_inst += 1
        if key in SHORT_INSTITUTIONS:
            im = re.search(r"\n\s*institution\s*=\s*\{", entry)
            assert im, f"{key}: no institution field to shorten"
            ib = entry.index("{", im.end() - 1)
            entry = (entry[: ib + 1] + SHORT_INSTITUTIONS[key]
                     + entry[find_matching_brace(entry, ib) - 1:])
            shortened_inst += 1
        if key in DROP_ADDRESS or key in DROP_ADDRESS_EXTRA:
            am = re.search(r",\s*\n\s*address\s*=\s*\{", entry)
            if am:
                ab = entry.index("{", am.end() - 1)
                entry = entry[: am.start()] + entry[find_matching_brace(entry, ab):]
                dropped_addr += 1
        if key in SHORT_TITLES:
            tm = re.search(r"\n\s*title\s*=\s*\{", entry)
            if tm:
                tb = entry.index("{", tm.end() - 1)
                entry = (entry[: tb + 1] + SHORT_TITLES[key]
                         + entry[find_matching_brace(entry, tb) - 1:])
                shortened_titles += 1
        if key in SHORT_NOTES:
            entry, w = rewrite_note(entry, SHORT_NOTES[key])
            kept += 1
            saved += w
        else:
            entry, w = rewrite_note(entry, None)
            if w:
                stripped += 1
                saved += w
        out.append(entry)
        pos = end
    out.append(src[pos:])

    DST.write_text(HEADER + "".join(out).lstrip("%").lstrip())
    print(f"wrote {DST.name}")
    print(f"  notes dropped   : {stripped} entries")
    print(f"  notes shortened : {kept} entries (Code path kept, gloss dropped)")
    print(f"  URLs dropped    : {dropped_urls} entries (longest only)")
    print(f"  titles trimmed  : {shortened_titles} entries")
    print(f"  addresses dropped: {dropped_addr} standards")
    print(f"  authors dropped : {dropped_auth} standards (org named in the designation)")
    print(f"  institutions    : {dropped_inst} dropped, {shortened_inst} shortened to acronym")
    print(f"  total words saved: {saved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

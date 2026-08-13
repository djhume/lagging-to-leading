"""
NZ Electricity Distribution Business (EDB) mapping.

Maps EMI 4-character network codes (nwk_code) to:
- Current EDB name (as of 2025)
- Historical names and mergers
- Whether the code is an EDB or non-EDB (generator, industrial, rail etc.)

There are 29 current EDBs in New Zealand:
  - 16 non-exempt (price-quality regulated by Commerce Commission)
  - 13 consumer-owned (exempt from price-quality regulation)
  All 29 have EMI nwk_codes. Centralines (CHBP) has one GXP: WPW0331 (Waipawa).
  Its network is managed by Unison Networks (HAWK) but it has a separate code.

Approach: use the 2025 POC→nwk_code mapping as canonical grouping applied
backwards through all years. This means a GXP is always attributed to its
CURRENT owner, even if it had a different nwk_code historically (e.g. UNET
POCs are attributed to VECT, CKHK, or HAWK as appropriate).

Data sources:
  - EMI POC-to-nwk_code mappings 1997-2025
  - EA Distribution Pricing Scorecards
  - Commerce Commission DPP determinations
  - EA regulatory framework documentation (Jan 2026)
"""

# ─────────────────────────────────────────────────────────────────────────────
# EDB network codes → current company name
#
# Some EDBs have had multiple codes over time due to mergers, demergers,
# and name changes. The 'successor' field links historical codes to their
# current EDB.
# ─────────────────────────────────────────────────────────────────────────────

EDB_CODES = {
    # ── Non-exempt (price-quality regulated by Commerce Commission) ───────
    'ALPE': {'name': 'Alpine Energy',       'region': 'South Canterbury',               'regulated': True},
    'CKHK': {'name': 'Wellington Electricity', 'region': 'Wellington',                   'regulated': True,
             'notes': 'Owned by CK Infrastructure (Hong Kong). CKHK = Cheung Kong HK. '
                      'POCs were under UNET pre-2009. 12 GXPs in Wellington region. '
                      'Privately owned but price-quality regulated.'},
    'DUNE': {'name': 'Aurora Energy',        'region': 'Dunedin, Central Otago, Queenstown', 'regulated': True,
             'notes': 'Formerly Dunedin Electricity'},
    'EASH': {'name': 'EA Networks',          'region': 'Mid-Canterbury',                 'regulated': True,
             'notes': 'Formerly Electricity Ashburton'},
    'EAST': {'name': 'Firstlight Network',   'region': 'Gisborne, East Coast',           'regulated': True,
             'notes': 'Formerly Eastland Network'},
    'ELIN': {'name': 'Electricity Invercargill', 'region': 'Invercargill',              'regulated': True,
             'notes': 'Part of PowerNet group. Powernet operates both ELIN and TPCO networks.'},
    'HAWK': {'name': 'Unison Networks',      'region': "Hawke's Bay, Rotorua, Taupo",    'regulated': True,
             'notes': 'Formerly Hawkes Bay Network (merged with Rotorua/Taupo from UNET)'},
    'HEDL': {'name': 'Horizon Networks',     'region': "Hawke's Bay (Napier/Hastings)",   'regulated': True,
             'notes': 'Formerly Hawkes Bay Power / HB Electric Distribution'},
    'NELS': {'name': 'Nelson Electricity',   'region': 'Nelson City',                    'regulated': True,
             'notes': 'Appeared as separate code from 2014; previously part of TASM'},
    'NPOW': {'name': 'Northpower',           'region': 'Whangarei, Kaipara',             'regulated': True},
    'ORON': {'name': 'Orion',                'region': 'Canterbury',                     'regulated': True,
             'notes': 'Formerly Orion New Zealand / Southpower'},
    'POCO': {'name': 'Powerco',              'region': 'Waikato, Taranaki, Manawatu, Wairarapa', 'regulated': True,
             'notes': 'Largest by geography.'},
    'TPCO': {'name': 'The Power Company',    'region': 'Southland (excl. Invercargill)', 'regulated': True,
             'notes': 'Part of PowerNet group.'},
    'TOPE': {'name': 'Top Energy',           'region': 'Far North',                      'regulated': True},
    'VECT': {'name': 'Vector',               'region': 'Auckland',                       'regulated': True,
             'notes': 'Absorbed UNET (United Networks) POCs progressively to 2013'},
    'WAIK': {'name': 'WEL Networks',         'region': 'Hamilton, Waikato',              'regulated': True,
             'notes': 'Also known as Waikato Electricity / W.E.L. Energy'},

    # ── Consumer-owned (exempt from price-quality regulation) ─────────────
    'BUEL': {'name': 'Buller Electricity',   'region': 'West Coast (Buller)',             'regulated': False},
    'CHBP': {'name': 'Centralines',          'region': 'Central Hawke\'s Bay',            'regulated': False,
             'notes': 'WPW0331 (Waipawa) GXP. Network managed by Unison Networks (HAWK). '
                      'Owned by Central Hawke\'s Bay Electric Power Trust.'},
    'COUP': {'name': 'Counties Energy',      'region': 'Franklin, South Auckland',        'regulated': False,
             'notes': 'Formerly Counties Power'},
    'ELEC': {'name': 'Electra',              'region': 'Kapiti, Horowhenua',              'regulated': False},
    'LINE': {'name': 'The Lines Company',    'region': 'King Country, Ruapehu',            'regulated': False},
    'MARL': {'name': 'Marlborough Lines',    'region': 'Marlborough',                     'regulated': False},
    'MPOW': {'name': 'Mainpower',            'region': 'North Canterbury',                'regulated': False},
    'OTPO': {'name': 'OtagoNet',             'region': 'Otago (Balclutha, South Otago)',   'regulated': False,
             'notes': 'OtagoNet Joint Venture'},
    'SCAN': {'name': 'Scanpower',            'region': 'Tararua',                         'regulated': False},
    'TASM': {'name': 'Network Tasman',       'region': 'Nelson, Tasman',                  'regulated': False},
    'WAIP': {'name': 'Waipa Networks',       'region': 'Waipa district',                   'regulated': False},
    'WATA': {'name': 'Network Waitaki',      'region': 'North Otago',                     'regulated': False},
    'WPOW': {'name': 'Westpower',            'region': 'West Coast (Grey, Westland)',      'regulated': False},
}

# ─────────────────────────────────────────────────────────────────────────────
# Historical / predecessor codes that should be mapped to current EDBs
# ─────────────────────────────────────────────────────────────────────────────

HISTORICAL_EDB_CODES = {
    'UNET': {'name': 'United Networks',
             'years': (1997, 2012),
             'notes': 'Large network that progressively fragmented. '
                      'POCs moved to HAWK (pre-2008), CKHK/Wellington Electricity (2009), '
                      'and VECT (2013). Use 2025 POC mapping to attribute UNET POCs '
                      'to their current owners retrospectively.'},
    'BOPE': {'name': 'Bay of Plenty Electricity',
             'years': (1997, 2007),
             'successor': 'BOPD',
             'notes': 'Renamed to Horizon Energy Distribution (BOPD) in 2008. '
                      'Not one of the 29 EDBs - actually an embedded network.'},
    'TAPP': {'name': 'TappEnergy / Taranaki Power',
             'years': (1997, 2004),
             'notes': 'KAW0112 went to CHHE, KAW0113 went to SKOG then disappeared. '
                      'Industrial cogeneration, not a standard EDB.'},
    'TRUS': {'name': 'TrustPower',
             'years': (1997, 1997),
             'notes': 'ATI0111 POC. TrustPower was a gentailer, not an EDB.'},
    'WROA': {'name': 'Wairoa (Road Board?)',
             'years': (1997, 2000),
             'notes': 'WRA0501 POC. Small historical network, merged/disappeared.'},
}

# ─────────────────────────────────────────────────────────────────────────────
# Non-EDB codes (generators, industrials, rail, transmission)
# These should be EXCLUDED from distribution company scatter plots
# ─────────────────────────────────────────────────────────────────────────────

NON_EDB_CODES = {
    # Generators
    'CTCT': {'name': 'Contact Energy',          'type': 'generator'},
    'GENE': {'name': 'Genesis Energy',          'type': 'generator'},
    'MERI': {'name': 'Meridian Energy',         'type': 'generator'},
    'MRPL': {'name': 'Mercury NZ (Mighty River Power)', 'type': 'generator'},
    'TRPG': {'name': 'Trustpower Generation',   'type': 'generator'},
    'KUPE': {'name': 'Kupe (OMV/Origin)',        'type': 'generator',
             'notes': 'Kupe gas field cogeneration'},
    'KAPE': {'name': 'Kapuni Energy',            'type': 'generator',
             'notes': 'Kapuni gas field'},
    'TUAR': {'name': 'Tuaropaki Power',          'type': 'generator',
             'notes': 'Geothermal generation at Mokai'},

    # Large industrials
    'NZAS': {'name': 'NZ Aluminium Smelters',    'type': 'industrial',
             'notes': 'Tiwai Point aluminium smelter'},
    'NZST': {'name': 'NZ Steel (BHP)',           'type': 'industrial',
             'notes': 'Glenbrook steel mill'},
    'METH': {'name': 'Methanex',                 'type': 'industrial',
             'notes': 'Methanol plant at Motunui'},
    'PANP': {'name': 'Pan Pac Forest Products',  'type': 'industrial',
             'notes': 'Forestry/pulp at Whirinaki'},
    'CHHE': {'name': 'Carter Holt Harvey',       'type': 'industrial',
             'notes': 'Kinleith pulp mill cogeneration'},
    'SKOG': {'name': 'Norske Skog (Tasman)',     'type': 'industrial',
             'notes': 'Kawerau pulp/paper. Code appeared 2005-2023.'},

    # Rail
    'NZRN': {'name': 'KiwiRail (NZ Rail Network)', 'type': 'rail',
             'notes': 'Electric traction (Wellington, Auckland)'},

    # Other / small
    'RAYN': {'name': 'Raynbird Holdings',        'type': 'other',
             'notes': 'BDE0111 POC. Small embedded network.'},
    'WNST': {'name': 'Wainuiomata (Wellington Suburban)', 'type': 'other',
             'notes': 'TNG0111 POC. Small network.'},
    'SHPK': {'name': 'South Park / Southpark',   'type': 'other',
             'notes': 'PEN0331 POC. Small / embedded.'},
    'MPAS': {'name': 'Mainpower Auxiliary Services', 'type': 'other',
             'notes': 'ASY0111 POC. Appeared 2015.'},
    'BOPD': {'name': 'Horizon Energy Distribution', 'type': 'other',
             'notes': 'MAT1101 POC only. Bay of Plenty embedded network. '
                      'Formerly BOPE. Not one of the 29 standard EDBs.'},
    'PTNP': {'name': 'Petroleum NP',             'type': 'other',
             'notes': 'NPL0331 POC. 2020 only.'},
}


# ─────────────────────────────────────────────────────────────────────────────
# POC → current EDB mapping (2025 baseline, applied backwards through time)
#
# Strategy: use the 2025 POC-to-nwk_code mapping as the canonical grouping.
# For any POC that existed historically but not in 2025, fall back to the
# most recent year's mapping. This ensures consistent company groupings
# across the full 1997-2025 time series.
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# Convenience lookups
# ─────────────────────────────────────────────────────────────────────────────

def is_edb(nwk_code: str) -> bool:
    """Check if a network code is a current EDB (distribution company)."""
    return nwk_code in EDB_CODES

def is_historical_edb(nwk_code: str) -> bool:
    """Check if a network code was a historical EDB."""
    return nwk_code in HISTORICAL_EDB_CODES

def get_edb_name(nwk_code: str) -> str:
    """Get display name for an EDB code."""
    if nwk_code in EDB_CODES:
        return EDB_CODES[nwk_code]['name']
    if nwk_code in HISTORICAL_EDB_CODES:
        return HISTORICAL_EDB_CODES[nwk_code]['name']
    if nwk_code in NON_EDB_CODES:
        return NON_EDB_CODES[nwk_code]['name']
    return nwk_code

def get_all_edb_codes() -> list:
    """Get all current EDB codes sorted by name."""
    return sorted(EDB_CODES.keys(), key=lambda c: EDB_CODES[c]['name'])

def get_edb_display_name(nwk_code: str) -> str:
    """Get display name suitable for chart titles."""
    if nwk_code in EDB_CODES:
        info = EDB_CODES[nwk_code]
        return f"{info['name']} ({info['region']})"
    return get_edb_name(nwk_code)


def get_network_names() -> dict:
    """Get mapping from all known nwk_codes to display names.

    Drop-in replacement for the ad-hoc get_network_names() dicts that
    existed in analyze_worst_gxps.py, create_gxp_excel_summary.py, etc.
    Those used registry/reconciliation codes (WELT, ECDN, CNET, etc.)
    which don't match EMI data. This uses the correct EMI nwk_codes.
    """
    names = {}
    for code, info in EDB_CODES.items():
        names[code] = info['name']
    for code, info in HISTORICAL_EDB_CODES.items():
        names[code] = info['name']
    for code, info in NON_EDB_CODES.items():
        names[code] = info['name']
    return names


# ─────────────────────────────────────────────────────────────────────────────
# POC owner corrections (added 10 Aug 2026)
#
# Where a POC hosts a generator or a small embedded network ALONGSIDE the local
# distributor's connections, the EMI POC→nwk_code mapping names the non-distributor
# party. Taken at face value that drops the distributor's load from every per-EDB
# analysis: 6 POCs and ~99,600 ICPs (4.2% of the national total) were being excluded,
# 82k of them at Penrose alone.
#
# The correction uses the ICP registry's own root-NSP field — the same source the ICP
# counts come from — which is single-valued and unambiguous for each POC below.
# Evidence is the 2025-06 registry: root NSP and ICP count.
#
# Found while building the company-cluster bootstrap for the IEEE trajectory paper,
# where PEN0331 (the panel's highest-leverage unit) would otherwise have been
# clustered on its own. See ieee-pf-trajectory-paper/PEER_REVIEW_FINDINGS_20260809.md.
# ─────────────────────────────────────────────────────────────────────────────

POC_OWNER_CORRECTIONS = {
    'PEN0331': {'edb': 'VECT', 'mapped_as': 'SHPK', 'icps_2025': 82396,
                'notes': 'Penrose. Mapping names Southpark, a code that appears in ZERO '
                         'rows of the ICP registry in any month. Registry root NSP is VECT '
                         'for all 82,396 connections. Mapping flipped VECT→SHPK in 2001.'},
    'CYD0331': {'edb': 'DUNE', 'mapped_as': 'CTCT', 'icps_2025': 7930,
                'notes': 'Clyde. Mapping names Contact Energy (the Clyde station); the '
                         'retail connections at the POC are Aurora\'s. Registry root NSP '
                         'DUNE. This POC was previously an explicit exclusion in '
                         'build_poc_to_edb_mapping, made from the mapping not the registry.'},
    'TKU0331': {'edb': 'LINE', 'mapped_as': 'GENE', 'icps_2025': 5035,
                'notes': 'Tokaanu. Mapping names Genesis (the Tokaanu station); the retail '
                         'connections are The Lines Company\'s. Registry root NSP LINE. '
                         'Mapping flipped LINE→GENE in 2003.'},
    'ASY0111': {'edb': 'MPOW', 'mapped_as': 'MPAS', 'icps_2025': 4241,
                'notes': 'Ashley. MPAS (MainPower Auxiliary Services) is a MainPower entity '
                         'but not one of the 29 EDB codes. Registry root NSP MPOW. Note the '
                         'registry series is absent 2005-2015 (re-registration), so this POC '
                         'still lacks endpoints for some balanced-panel analyses.'},
}

# Deliberately NOT corrected — genuine embedded networks with negligible retail load,
# correctly excluded from per-EDB analysis:
#   WKM2201 (TUAR, Tuaropaki, 11 ICPs) and ATI2201 (MRPL, 1 ICP).


def build_poc_to_edb_mapping(include_metadata=False):
    """
    Build a POC -> current EDB code mapping using 2025 as baseline.

    Args:
        include_metadata: If True, return dict of dicts with additional info:
            {poc: {'edb': code, 'first_year': int, 'last_year': int, 'current': bool}}
            If False (default), return simple dict {poc: edb_code}.

    Returns dict mapping POC codes to their current EDB nwk_code.
    POCs belonging to non-EDB codes are excluded.
    """
    import pandas as pd
    from pathlib import Path

    meta_dir = Path(__file__).parent
    df_2025 = pd.read_csv(meta_dir / '2025_poc_nwk_mapping.csv')

    # Build set of POCs that are non-EDB in 2025 (exclude these entirely).
    # POCs in POC_OWNER_CORRECTIONS are NOT excluded: the mapping names a generator or
    # embedded network at a POC that also carries the local distributor's connections.
    non_edb_pocs_2025 = set()
    for _, row in df_2025.iterrows():
        if row['nwk_code'] not in EDB_CODES and row['poc'] not in POC_OWNER_CORRECTIONS:
            non_edb_pocs_2025.add(row['poc'])

    # Track which POCs exist in 2025 for the 'current' flag
    pocs_in_2025 = set(df_2025['poc'])

    # Start with 2025 mapping, filtered to EDB codes only
    poc_map = {}
    for _, row in df_2025.iterrows():
        if row['nwk_code'] in EDB_CODES:
            poc_map[row['poc']] = row['nwk_code']

    # Apply the registry-evidenced owner corrections (see POC_OWNER_CORRECTIONS above)
    for poc, fix in POC_OWNER_CORRECTIONS.items():
        if poc in pocs_in_2025:
            poc_map[poc] = fix['edb']

    # Track first/last year each POC appears (across all years, EDB or not)
    poc_years = {}  # {poc: (first_year, last_year)}

    # Walk all years to build year ranges and pick up historical EDB POCs
    for year in range(1997, 2026):
        f = meta_dir / f'{year}_poc_nwk_mapping.csv'
        if not f.exists():
            continue
        df = pd.read_csv(f)
        for _, row in df.iterrows():
            poc = row['poc']
            code = row['nwk_code']

            # Track year range for all POCs
            if poc in poc_years:
                first, last = poc_years[poc]
                poc_years[poc] = (min(first, year), max(last, year))
            else:
                poc_years[poc] = (year, year)

            # For historical POCs not in 2025, find their last EDB code
            # Skip any POC that is non-EDB in 2025 (e.g. CYD0331 = CTCT)
            if poc not in poc_map and poc not in non_edb_pocs_2025 and code in EDB_CODES:
                poc_map[poc] = code

    if not include_metadata:
        return poc_map

    # Build enriched mapping with metadata
    enriched = {}
    for poc, edb_code in poc_map.items():
        first_year, last_year = poc_years.get(poc, (None, None))
        enriched[poc] = {
            'edb': edb_code,
            'first_year': first_year,
            'last_year': last_year,
            'current': poc in pocs_in_2025,
        }
    return enriched


# ─────────────────────────────────────────────────────────────────────────────
# Print summary when run directly
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 70)
    print("NZ Electricity Distribution Businesses (EDBs)")
    print("=" * 70)

    print(f"\nCurrent EDB codes: {len(EDB_CODES)} (all 29 NZ EDBs)")
    regulated = [c for c, v in EDB_CODES.items() if v['regulated']]
    exempt = [c for c, v in EDB_CODES.items() if not v['regulated']]
    print(f"  Non-exempt (regulated): {len(regulated)}")
    print(f"  Consumer-owned (exempt): {len(exempt)}")

    print("\n── Regulated EDBs ──")
    for code in sorted(regulated, key=lambda c: EDB_CODES[c]['name']):
        info = EDB_CODES[code]
        print(f"  {code:6s} {info['name']:28s} {info['region']}")

    print("\n── Consumer-owned (exempt) EDBs ──")
    for code in sorted(exempt, key=lambda c: EDB_CODES[c]['name']):
        info = EDB_CODES[code]
        print(f"  {code:6s} {info['name']:28s} {info['region']}")

    print(f"\nHistorical EDB codes: {len(HISTORICAL_EDB_CODES)}")
    for code, info in sorted(HISTORICAL_EDB_CODES.items()):
        print(f"  {code:6s} {info['name']:28s} {info['years'][0]}-{info['years'][1]}")

    print(f"\nNon-EDB codes: {len(NON_EDB_CODES)}")
    for code, info in sorted(NON_EDB_CODES.items()):
        print(f"  {code:6s} {info['name']:28s} ({info['type']})")

    all_known = set(EDB_CODES) | set(HISTORICAL_EDB_CODES) | set(NON_EDB_CODES)
    print(f"\nTotal codes mapped: {len(all_known)}")

    # Build and summarise POC mapping
    print("\n" + "=" * 70)
    print("POC → EDB MAPPING")
    print("=" * 70)

    poc_map = build_poc_to_edb_mapping(include_metadata=True)
    print(f"\nTotal EDB POCs mapped: {len(poc_map)}")

    current = sum(1 for v in poc_map.values() if v['current'])
    historical = sum(1 for v in poc_map.values() if not v['current'])
    print(f"  Current (in 2025): {current}")
    print(f"  Historical only:   {historical}")

    # POCs per EDB
    from collections import Counter
    edb_counts = Counter(v['edb'] for v in poc_map.values())
    print(f"\nPOCs per EDB:")
    for code in sorted(edb_counts, key=lambda c: EDB_CODES[c]['name']):
        info = EDB_CODES[code]
        print(f"  {code:6s} {info['name']:28s} {edb_counts[code]:3d} POCs")

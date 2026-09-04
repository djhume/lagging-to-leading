"""Guard: the designed HTML page must carry the short version's words, unchanged.

The page at `clients/ea/power-factor/ieee-pf-trajectory-paper/` (wave 2) renders the SAME
text as `main.tex`, natively rather than as a PDF. Placement moves — hedges go to the
margin — but wording does not. Nothing downstream reads the .tex, so without this guard
the page can drift from the paper silently, the same failure mode `AUDIT_FIG_ANNOTATIONS.py`
covers for figures and `VERIFY_FIGURE_DATA.py` for series.

WHAT IT CHECKS. A token-level diff, both directions, over every section the page carries:
no word in the paper is missing from the page, and no word on the page is absent from the
paper.

Paper text is identified by a WHITELIST, not by deleting chrome. Deleting chrome was the
first attempt and it is wrong: `<div class="figtop">` and `<div class="ctl">` contain nested
divs, a regex cannot match balanced tags, and the over-match silently swallowed a whole
paragraph and a caption — the guard then reported drift that did not exist. The whitelist
elements (`.blk > p`, `.note`, `figcaption`) hold only inline tags, so matching them is safe.

OUT OF SCOPE, deliberately: figure NUMBERS, which differ between the two media as the
page grows, and headings, on both sides. The page carries §III's title in a
<header> that also holds a deck written for the page, so headings cannot be compared without
false positives. They are short and visible; this guard covers running prose.

MAINTENANCE. As sections are added to the page, add them to CARRIES below. That list is
the contract: it says which parts of main.tex the page currently claims to reproduce.

    run from the paper directory:  python VERIFY_PAGE_TEXT.py [path/to/page.html]
"""
from __future__ import annotations

import collections
import html as htmllib
import pathlib
import re
import sys

PAPER = pathlib.Path(__file__).resolve().parent
DEFAULT_PAGE = PAPER / "lagging-to-leading.html"

# Which parts of main.tex the page currently carries. (start marker, end marker).
CARRIES = [
    ("Abstract",
     "Both ENTSO-E Final Reports on the 2025 Iberian",
     r"\end{abstract}"),
    ("I  Introduction",
     r"\section{Introduction}", r"\section{Data and Method}"),
    ("II  Data and Method",
     r"\section{Data and Method}", r"\section{The 29-Year Reactive Trajectory}"),
    ("III  The 29-Year Reactive Trajectory",
     r"\section{The 29-Year Reactive Trajectory}", r"\section{Decomposition: Demand vs Network}"),
    ("IV  Decomposition: Demand vs Network — intro, Method 1, Method 2",
     r"\section{Decomposition: Demand vs Network}", r"\subsection{Method 3: first-principles charging physics}"),
    ("IV-C  Method 3: first-principles charging physics",
     r"\subsection{Method 3: first-principles charging physics}", r"\subsection{Triangulation}"),
    ("IV-D  Triangulation, entire (with Table 2)",
     r"\subsection{Triangulation}",
     r"\section{The Demand-Side Term Identified: A Standing Shunt Term Behind"),
    ("V  The Demand-Side Term Identified — head and V-A",
     r"\section{The Demand-Side Term Identified: A Standing Shunt Term Behind",
     r"\subsection{A physical candidate: the mandated EMC filter}"),
    ("V-B  A physical candidate: the mandated EMC filter, entire",
     r"\subsection{A physical candidate: the mandated EMC filter}",
     r"\subsection{A connection-scaling test}"),
    ("V-C  A connection-scaling test, entire",
     r"\subsection{A connection-scaling test}",
     r"\section{From Leading Reactive Power to Overvoltage}"),
    ("VI  From Leading Reactive Power to Overvoltage",
     r"\section{From Leading Reactive Power to Overvoltage}",
     r"\section{Implications for Power-System Analysis}"),
    ("VII  Implications for Power-System Analysis",
     r"\section{Implications for Power-System Analysis}", r"\section{Conclusion}"),
    ("VIII  Conclusion, Reproducibility and Acknowledgment",
     r"\section{Conclusion}", r"% Final-page column balance"),
]

# The whitelist: elements that hold paper prose and nothing else.
PAPER_TEXT = [
    r'<p class="lead">(.*?)</p>',      # a block's opening paragraph
    r"<p>(.*?)</p>",                   # a block's body paragraph (class-less by convention)
    r'<aside class="note">(.*?)</aside>',
    r"<figcaption>(.*?)</figcaption>",
    r"<caption>(.*?)</caption>",          # the paper's own table captions
]


def clean_tex(s: str) -> str:
    # a real comment, NOT an escaped \% — getting this wrong silently eats half a line
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\(sub)?section\*?\{[^}]*\}", " ", s)   # headings are out of scope
    # keep caption text (the page carries captions); drop the rest of the float
    caps = re.findall(r"\\caption\{(.*?)\}\s*\n?\s*\\label", s, flags=re.S)
    s = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", " ", s, flags=re.S)
    s = re.sub(r"\\begin\{table\}.*?\\end\{table\}", " ", s, flags=re.S)
    s = re.sub(r"\\begin\{equation\*?\}.*?\\end\{equation\*?\}", " ", s, flags=re.S)
    s += " " + " ".join(caps)
    s = re.sub(r"\\cite\{[^}]*\}", " ", s)
    s = re.sub(r"Fig\.~?\\ref\{[^}]*\}", " figref ", s)
    s = re.sub(r"Table~?\\ref\{[^}]*\}", " tableref ", s)
    s = re.sub(r"\\ref\{[^}]*\}", " ", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\IEEEPARstart\{(\w)\}\{(\w+)\}", r"\1\2", s)
    # both arrows are read aloud as "to" and render as one on the page
    s = s.replace(r"\rightarrow", " to ")
    s = re.sub(r"\\to(?![A-Za-z])", " to ", s)
    # notation macros render as glyphs the tokeniser already drops as punctuation,
    # so they must not survive as words on the TeX side
    for mac in (r"\\approx", r"\\circ", r"\\leq", r"\\geq", r"\\times",
                r"\\cdot", r"\\pm"):
        s = re.sub(mac, " ", s)
    # symbol and dash normalisations, so TeX source and rendered glyph tokenise alike
    s = (s.replace(r"\sim", " ")
          .replace(r"\ell", "l").replace(r"\omega", "omega").replace("^", " "))
    s = s.replace("---", " ").replace("--", "-")
    s = s.replace("$", " ").replace("~", " ").replace(r"\%", "%").replace(r"\,", " ")
    return s.replace("\\", " ")


def clean_page(s: str) -> str:
    s = s[s.index('<div class="wrap">'):]
    if '<div class="foot">' in s:          # the footer holds bare <p>s that are page chrome
        s = s[:s.index('<div class="foot">')]
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    parts = []
    for pat in PAPER_TEXT:
        parts.extend(re.findall(pat, s, flags=re.S))
    out = " ".join(parts)
    # reference markers and the extended-record marker are navigation, not words
    out = re.sub(r'<span class="key">[a-z]</span>|<sup class="ref">[a-z]</sup>'
                 r'|<span class="src">[A-Z]</span>|<span class="tlabel">[^<]*</span>'
                 r'|<sup class="cn">.*?</sup>', " ", out)
    out = htmllib.unescape(re.sub(r"<[^>]+>", " ", out))
    out = re.sub(r"Plate\s*\d+", " ", out)      # page-only exhibits
    out = re.sub(r"Fig\.\s*\d+", " figref ", out)
    return re.sub(r"Table\s*\d+", " tableref ", out)


def toks(s: str) -> collections.Counter:
    # Rendered glyphs are folded to the same form clean_tex() produces from the source,
    # so an en-dash and "--", or "→" and \rightarrow, are the same token.
    s = (s.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", " ")
          .replace("---", " ").replace("\u2192", " to ").replace("\u00a0", " ")
          .replace("\u2019", "'").replace("\u03c9", "omega").replace("\u2113", "l")
          .replace("\u03bc", "mu ").replace("\u00b5", "mu ")
          .replace("\u03b2", "beta ").replace("\u0394", "Delta ")
          .replace("\u03a3", "Sigma ").replace("\u221a", "sqrt ")
          .replace("\u00b1", " "))
    s = s.replace("/", " ")   # "$-0.00005$/yr" vs "-0.00005/yr" must agree
    s = re.sub(r"[^A-Za-z0-9%.']+", " ", s)
    return collections.Counter(t.strip("-.'") for t in s.lower().split() if t.strip("-.'"))


def main() -> int:
    page_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PAGE
    if not page_path.exists():
        print(f"page not found: {page_path}", file=sys.stderr)
        return 2
    tex = (PAPER / "main.tex").read_text()

    carried = []
    print(f"page: {page_path.name}")
    print("sections the page claims to carry:")
    for name, start, end in CARRIES:
        if start not in tex:
            print(f"  [FAIL] {name}: start marker not in main.tex")
            return 1
        i = tex.index(start)
        j = tex.index(end, i) if end in tex[i:] else len(tex)
        carried.append(tex[i:j])
        print(f"  · {name}")

    T = toks(clean_tex("\n".join(carried)))
    P = toks(clean_page(page_path.read_text()))
    dropped, added = T - P, P - T

    print()
    print(f"tokens in the paper's carried sections: {sum(T.values())}")
    print(f"tokens on the page (paper text only)  : {sum(P.values())}")
    print()
    ok = True
    if dropped:
        ok = False
        print("[FAIL] IN THE PAPER, NOT ON THE PAGE — words dropped:")
        for t, n in sorted(dropped.items()):
            print(f"        {t!r} x{n}")
    else:
        print("[ok  ] no word of the carried sections is missing from the page")
    if added:
        ok = False
        print("[FAIL] ON THE PAGE, NOT IN THE PAPER — words added:")
        for t, n in sorted(added.items()):
            print(f"        {t!r} x{n}")
    else:
        print("[ok  ] no word on the page is absent from the paper")

    print()
    if not ok:
        print("DRIFT — the page no longer carries the paper's words verbatim.")
        return 1
    print("ALL GREEN — the page carries the paper's words verbatim; only placement differs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

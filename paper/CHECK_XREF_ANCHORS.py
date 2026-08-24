"""Dangling concept-reference check (21 Aug 2026).

The defect class Dave found twice in one afternoon, and that NO existing guard
can see: the paper says "the <concept> of Section~X", a later compression pass
deletes <concept> from Section X, and the reference silently stops landing.

  - "we lead with this intensity ... " relied on §III-B's "contamination-sensitive
    companion", deleted by an earlier cut.
  - "In the comparator of Section~II-A" relied on §II-A's "familiar comparator",
    deleted by the 21-Aug compression.

Numeric diffs check values. Hedge guards check named strings. Neither checks
whether a *named concept* still exists in the section it is attributed to.

Usage:  python CHECK_XREF_ANCHORS.py [file.tex ...]   (defaults to both tiers)
Exit 0 = all anchors land.
"""
from __future__ import annotations
import re, sys

ROMAN = ["I","II","III","IV","V","VI","VII","VIII","IX","X"]
STOP = {"the","a","an","of","in","and","this","that","its","their","same","full",
        "our","above","below","own","one","two","three","first","second","third"}

def sections(tex: str):
    """Map section label -> its text. A PARENT section inherits its subsections'
    text, since "the X of Section~III" is satisfied by X appearing in III-B."""
    body = tex[tex.index(r"\begin{document}"):]
    marks, si, sub = [], -1, 0
    for m in re.finditer(r"\\(section|subsection)\*?\{([^}]*)\}", body):
        if m.group(1) == "section":
            if m.group(2).startswith(("Reproducib", "Acknowl", "Appendix")):
                lab = None
            else:
                si += 1; sub = 0
                lab = ROMAN[si] if 0 <= si < len(ROMAN) else None
        else:
            lab = None
            if 0 <= si < len(ROMAN):
                sub += 1
                lab = f"{ROMAN[si]}-{chr(64+sub)}" if sub <= 26 else None
        marks.append((m.start(), lab))
    out = {}
    for i, (pos, lab) in enumerate(marks):
        if not lab:
            continue
        end = marks[i+1][0] if i + 1 < len(marks) else len(body)
        chunk = " " + " ".join(body[pos:end].split())
        out[lab] = out.get(lab, "") + chunk
        parent = lab.split("-")[0]
        if parent != lab:                      # roll subsection text up to parent
            out[parent] = out.get(parent, "") + chunk
    return out

def check(path: str) -> int:
    tex = open(path).read()
    secs = sections(tex)
    flat = " ".join(tex.split())
    # "the <words> of/in Section~X-Y"
    pat = re.compile(r"\b(?:the|its)\s+([a-z][a-z\-]*(?:\s+[a-z][a-z\-]*){0,3})\s+"
                     r"(?:of|in|from)\s+Section~([IVX]+(?:-[A-Z])?)")
    bad = 0
    print(f"── {path}")
    for m in pat.finditer(flat):
        phrase, tgt = m.group(1), m.group(2)
        if tgt not in secs:
            print(f"   ⚠ Section~{tgt} does not exist  ({m.group(0)})"); bad += 1; continue
        # split hyphenated compounds: "cable-dose" is satisfied by "cable dose",
        # and "measurement-error analysis" by a section that discusses errors.
        words = [w for part in phrase.split() for w in part.split("-")
                 if w not in STOP and len(w) > 3]
        if not words:
            continue
        target = secs[tgt].lower().replace("-", " ")
        missing = [w for w in words if w.rstrip("s") not in target]
        if len(missing) == len(words):          # none of the content words appear
            print(f"   ⚠ DANGLING: \"{m.group(0)}\" — none of {words} occurs in §{tgt}")
            bad += 1
    print("   ok — every concept-reference lands" if not bad
          else f"   {bad} dangling reference(s)")
    return bad

if __name__ == "__main__":
    files = sys.argv[1:] or ["main.tex", "main_extended_20260808.tex"]
    raise SystemExit(1 if sum(check(f) for f in files) else 0)

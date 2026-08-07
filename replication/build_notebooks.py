#!/usr/bin/env python3
"""Build the .ipynb notebooks from their readable percent-format `.py` sources.

We author each notebook as a plain `src/NN_name.py` file using the Jupyter
"percent" cell convention:

    # %% [markdown]
    # markdown text, each line prefixed with '# '
    # %%
    code goes here

This script converts those sources to executable notebooks in `notebooks/`. It is
a 40-line stand-in for `jupytext` (which is not installed in this environment) so
the build has no extra dependency beyond `nbformat`.

Usage:
    python build_notebooks.py            # build all src/*.py -> notebooks/*.ipynb
    python build_notebooks.py 00 02      # build only the matching sources
"""
from pathlib import Path
import sys

import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
OUT = HERE / "notebooks"


def parse_percent(text: str):
    """Yield (kind, source) cells from percent-format text."""
    lines = text.splitlines()
    cells = []
    kind, buf = None, []

    def flush():
        if kind is None:
            return
        src = "\n".join(buf).strip("\n")
        if src.strip() == "" and kind == "code":
            return
        cells.append((kind, src))

    for ln in lines:
        stripped = ln.strip()
        if stripped.startswith("# %% [markdown]"):
            flush()
            kind, buf = "markdown", []
        elif stripped.startswith("# %%"):
            flush()
            kind, buf = "code", []
        else:
            if kind == "markdown":
                # strip the leading "# " (or a bare "#") comment marker
                if ln.startswith("# "):
                    buf.append(ln[2:])
                elif ln.rstrip() == "#":
                    buf.append("")
                else:
                    buf.append(ln)
            elif kind == "code":
                buf.append(ln)
            # text before the first cell marker is ignored (module docstring etc.)
    flush()
    return cells


def build(src_path: Path) -> Path:
    cells = parse_percent(src_path.read_text())
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(s) if k == "markdown" else new_code_cell(s)
        for k, s in cells
    ]
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3", "language": "python", "name": "python3",
    }
    out_path = OUT / (src_path.stem + ".ipynb")
    OUT.mkdir(exist_ok=True)
    nbformat.write(nb, out_path)
    return out_path


def main(argv):
    OUT.mkdir(exist_ok=True)
    srcs = sorted(SRC.glob("*.py"))
    if argv:
        srcs = [s for s in srcs if any(s.name.startswith(a) for a in argv)]
    for s in srcs:
        out = build(s)
        n = len(parse_percent(s.read_text()))
        print(f"built {out.relative_to(HERE)}  ({n} cells)")


if __name__ == "__main__":
    main(sys.argv[1:])

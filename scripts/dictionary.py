"""Where the dictionary is, and what it is, for the scripts in this folder.

The scripts work on the dictionary repository they are run in: the
current folder, or the nearest folder above it, that has a src/ folder
with the dictionary files (dict-sme, dict-sma, ...). XXE runs them from
the root of the repository of the document being edited.

The name and language of the dictionary are read from the root element
of its files: <r id="dict-sme" xml:lang="sme">.
"""

import re
import sys
from pathlib import Path


def find_root():
    here = Path.cwd().resolve()
    for d in [here, *here.parents]:
        if any((d / "src").glob("*.xml")):
            return d
    sys.exit(f"! no dictionary here: no src/*.xml in {here} or above it")


ROOT = find_root()
SRC = ROOT / "src"
BATCHES = ROOT / "batches" / "batches.xml"
# the lists made for XXE by make_refs.py and batch_goto.py; not in git
LISTS = ROOT / ".xxe"
# PDFs of batches; not in git
EXPORTS = ROOT / "pdf"


def _root_element():
    for f in sorted(SRC.glob("*.xml")):
        with open(f, encoding="utf-8") as fh:
            m = re.search(r"<r\s[^>]*>", fh.read(4096))
        if m:
            return m.group(0)
    return ""


_r = _root_element()
NAME = (re.search(r'\bid="([^"]*)"', _r) or [None, ROOT.name])[1]
LANG = (re.search(r'\bxml:lang="([^"]*)"', _r) or [None, ""])[1]

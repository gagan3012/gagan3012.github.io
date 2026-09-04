#!/usr/bin/env python3
"""Fill in the `bibtex` field for any paper in data/papers.yaml that lacks one.

Sources, in order of preference:
  - ACL Anthology  (.bib for the paper id in the link)
  - arXiv          (arxiv.org/bibtex/<id>)
  - Semantic Scholar (citationStyles.bibtex, matched by title)

Existing bibtex entries are never overwritten, so hand-edits are preserved.
Usage: python scripts/fetch_bibtex.py
"""

import os
import re
import sys
import time
import yaml
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_PATH = os.path.join(ROOT, "data", "papers.yaml")
UA = {"User-Agent": "gagan3012.github.io bibtex fetcher"}

HEADER = (
    "# Publications.\n"
    '# venue: short label shown next to the paper — "arXiv" for preprints,\n'
    '#        otherwise the conference/journal (e.g. "EMNLP 2025").\n'
    "# Papers are grouped by year automatically; order within a year follows this file.\n"
    "# bibtex: filled in by scripts/fetch_bibtex.py; hand-edits are preserved.\n"
)


def tidy(bib):
    bib = bib.strip()
    # Collapse the ragged indentation the anthology uses.
    bib = re.sub(r"\n[ \t]+", "\n    ", bib)
    return bib


def from_acl(link):
    m = re.search(r"aclanthology\.org/([^/]+?)(?:\.pdf)?/?$", link or "")
    if not m:
        return None
    r = requests.get(f"https://aclanthology.org/{m.group(1)}.bib", headers=UA, timeout=30)
    return tidy(r.text) if r.ok and r.text.lstrip().startswith("@") else None


def from_arxiv(link):
    m = re.search(r"arxiv\.org/abs/([0-9.]+)", link or "")
    if not m:
        return None
    r = requests.get(f"https://arxiv.org/bibtex/{m.group(1)}", headers=UA, timeout=30)
    return tidy(r.text) if r.ok and r.text.lstrip().startswith("@") else None


def from_s2(title):
    r = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query": title, "fields": "title,citationStyles", "limit": 1},
        headers=UA,
        timeout=30,
    )
    if not r.ok:
        return None
    data = (r.json() or {}).get("data") or []
    if not data:
        return None
    bib = ((data[0].get("citationStyles") or {}).get("bibtex") or "").strip()
    return tidy(bib) if bib.startswith("@") else None


def main():
    with open(PAPERS_PATH, encoding="utf-8") as f:
        papers = yaml.safe_load(f) or []

    filled, missing = 0, []
    for p in papers:
        if p.get("bibtex"):
            continue
        title, link = p.get("title", ""), p.get("link", "")
        bib = None
        for source in (lambda: from_acl(link), lambda: from_arxiv(link), lambda: from_s2(title)):
            try:
                bib = source()
            except requests.RequestException:
                bib = None
            if bib:
                break
            time.sleep(1)
        if bib:
            p["bibtex"] = bib
            filled += 1
            print(f"  + {title[:70]}")
        else:
            missing.append(title)

    if filled:
        with open(PAPERS_PATH, "w", encoding="utf-8") as f:
            f.write(HEADER)
            yaml.safe_dump(papers, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)

    print(f"\nFilled {filled} bibtex entr{'y' if filled == 1 else 'ies'}.")
    if missing:
        print("No bibtex found for (add by hand in data/papers.yaml):")
        for t in missing:
            print(f"  - {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Sync data/papers.yaml with new papers from Semantic Scholar.

Fetches the author's paper list from the Semantic Scholar Graph API and
appends any paper not already present (matched by normalized title) to
data/papers.yaml. Existing entries are never modified or removed, so any
manual edits (status, job_market_paper, abstract, ...) are preserved.

Usage: python scripts/sync_papers.py
Optional env var S2_API_KEY raises the Semantic Scholar rate limit.
"""

import os
import re
import time
import yaml
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_PATH = os.path.join(ROOT, "data", "papers.yaml")

S2_AUTHOR_ID = "2148712875"  # Gagan Bhatia
S2_API_BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,year,venue,authors,externalIds,publicationTypes,openAccessPdf"


def normalize(title):
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def load_existing():
    if not os.path.exists(PAPERS_PATH):
        return []
    with open(PAPERS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def fetch_s2_papers():
    url = f"{S2_API_BASE}/author/{S2_AUTHOR_ID}/papers"
    api_key = os.environ.get("S2_API_KEY")

    if api_key:
        resp = requests.get(url, params={"fields": FIELDS}, headers={"x-api-key": api_key}, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("data", [])
        print(f"Keyed request failed ({resp.status_code}), retrying without API key")

    resp = requests.get(url, params={"fields": FIELDS}, timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", [])


def best_link(paper):
    ext = paper.get("externalIds") or {}
    if ext.get("ACL"):
        return f"https://aclanthology.org/{ext['ACL']}.pdf"
    if ext.get("ArXiv"):
        return f"https://arxiv.org/abs/{ext['ArXiv']}"
    oa = paper.get("openAccessPdf") or {}
    if oa.get("url"):
        return oa["url"]
    return f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}"


def venue_label(paper):
    """Short label shown on the site: "arXiv" for preprints, otherwise the venue."""
    ext = paper.get("externalIds") or {}
    venue = (paper.get("venue") or "").strip()
    if not venue or venue.lower() in ("arxiv.org", "arxiv"):
        return "arXiv" if ext.get("ArXiv") else (venue or "Preprint")
    return venue


def to_entry(paper):
    authors = [a.get("name", "").strip() for a in (paper.get("authors") or []) if a.get("name")]
    return {
        "title": paper.get("title", "").strip(),
        "authors": authors,
        "year": paper.get("year"),
        "venue": venue_label(paper),
        "link": best_link(paper),
    }


def known_coauthors(existing):
    """Normalized names of everyone who has coauthored a paper already on the
    site (excluding Gagan Bhatia himself). Used to guard against a same-name
    author collision on Semantic Scholar pulling in someone else's papers."""
    names = set()
    for p in existing:
        for a in p.get("authors") or []:
            n = normalize(a)
            if n and "gagan bhatia" not in n:
                names.add(n)
    return names


def main():
    existing = load_existing()
    known_titles = {normalize(p["title"]) for p in existing if p.get("title")}
    coauthors = known_coauthors(existing)

    try:
        s2_papers = fetch_s2_papers()
    except requests.RequestException as e:
        print(f"Semantic Scholar fetch failed, skipping sync: {e}")
        return

    new_entries = []
    needs_review = []
    for paper in s2_papers:
        title = (paper.get("title") or "").strip()
        if not title:
            continue
        key = normalize(title)
        if key in known_titles:
            continue

        authors = [a.get("name", "") for a in (paper.get("authors") or [])]
        overlap = any(normalize(a) in coauthors for a in authors)
        # A same-name collision on Semantic Scholar can pull in an unrelated
        # researcher's papers. Only auto-add when a known collaborator is on
        # the paper too, or it's solo-authored; otherwise flag for review.
        if not overlap and len(authors) > 1:
            needs_review.append(title)
            known_titles.add(key)
            continue

        new_entries.append(to_entry(paper))
        known_titles.add(key)
        time.sleep(0.2)

    if needs_review:
        print("Skipped (no known coauthor overlap, needs manual review):")
        for t in needs_review:
            print(f"  - {t}")

    if not new_entries:
        print("No new papers found.")
        return

    updated = existing + new_entries
    with open(PAPERS_PATH, "w", encoding="utf-8") as f:
        f.write("# Publications.\n")
        f.write('# venue: short label shown next to the paper — "arXiv" for preprints,\n')
        f.write('#        otherwise the conference/journal (e.g. "EMNLP 2025").\n')
        f.write("# Papers are grouped by year automatically; order within a year follows this file.\n")
        yaml.safe_dump(updated, f, sort_keys=False, default_flow_style=False, allow_unicode=True)

    print(f"Added {len(new_entries)} new paper(s):")
    for e in new_entries:
        print(f"  - {e['title']} ({e['year']})")


if __name__ == "__main__":
    main()

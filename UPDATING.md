# Updating this site

This site is built with [Hugo](https://gohugo.io) and deploys automatically
to GitHub Pages whenever you push to `main`. Most changes can be made
directly in the GitHub web editor — no local setup needed.

## Add a new paper

Edit [`data/papers.yaml`](data/papers.yaml) and add a new entry:

```yaml
- title: "Paper Title Here"
  authors: ["Gagan Bhatia", "Coauthor Name"]
  year: 2026
  venue: "arXiv" # or the conference/journal, e.g. "EMNLP 2025"
  link: "https://arxiv.org/abs/xxxx.xxxxx"
```

Papers are grouped by year automatically, newest first; within a year they
appear in the order they're listed in the file. The `venue` label is shown as
a small tag next to each paper — write `arXiv` (or `TechRxiv`) for preprints,
which renders as a plain outlined tag, and a real venue name for anything
peer-reviewed, which renders in the accent colour.

This repo also has a scheduled workflow (`.github/workflows/papers-sync.yml`)
that checks Semantic Scholar weekly and appends any new paper it finds — it
never edits or removes entries you've already added, so feel free to hand-edit
`venue` or `link` afterward. Auto-added venue labels come straight from
Semantic Scholar and are often long, so it's worth shortening them by hand.

## Update your bio

Edit the body of [`content/_index.md`](content/_index.md).

## Update your CV

The CV is compiled automatically every day from the LaTeX source in
[gagan3012/resume-v2](https://github.com/gagan3012/resume-v2) by
`.github/workflows/cv-sync.yml`, and copied to `static/files/cv.pdf`. Just
push changes to `resume-v2` — no action needed here. To trigger an update
immediately, run the "Sync CV from resume-v2" workflow manually from the
Actions tab.

## Change your photo

Replace `static/images/photo.jpg` with a new image (keep the same filename,
roughly square, at least 400x400px).

## Add a teaching entry

Create `data/teaching.yaml` (if it doesn't exist yet) with entries like:

```yaml
- course: "Course Name"
  role: "Teaching Assistant"
  institution: "University of Technology Nuremberg"
  term: "Winter 2026"
```

## Add an award or fellowship

Create `data/awards.yaml`:

```yaml
- name: "Award Name"
  year: 2026
```

## Add a software project

Create `data/projects.yaml`:

```yaml
- name: "ProjectName"
  description: "One-sentence description of what it does."
  url: "https://github.com/gagan3012/project"
```

## Add a blog post

Create `content/blog/your-post-slug/index.md`:

```yaml
---
title: "Post Title"
date: 2026-09-04
description: "One-sentence summary."
---
Post content in Markdown.
```

## A preprint got accepted

Change its `venue` in `data/papers.yaml` from `"arXiv"` to the venue name
(e.g. `"EMNLP 2026"`). The tag then renders in the accent colour instead of
the dimmed preprint style. Keep the arXiv `link` until the paper appears on
the ACL Anthology.

Once it *is* on the Anthology: update `link` to the anthology URL, **delete
the paper's `bibtex:` block**, and run `python scripts/fetch_bibtex.py` (or
wait for the weekly sync). The script only fills in missing entries, so
deleting the block is what lets it pull the official citation with pages,
DOI, and editors.

All changes auto-deploy within about two minutes of pushing to `main`.

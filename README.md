# gagan3012.github.io

Personal academic website for Gagan Bhatia, built with [Hugo](https://gohugo.io)
and deployed to GitHub Pages via GitHub Actions.

- Content is edited via `data/papers.yaml`, `content/_index.md`, and the
  files under `static/` — see [UPDATING.md](UPDATING.md).
- The CV (`static/files/cv.pdf`) is compiled daily from
  [gagan3012/resume-v2](https://github.com/gagan3012/resume-v2) by
  `.github/workflows/cv-sync.yml`.
- New papers are pulled weekly from Semantic Scholar by
  `.github/workflows/papers-sync.yml` (`scripts/sync_papers.py`).

## Local development

```bash
hugo server -D
```

Requires [Hugo Extended](https://gohugo.io/installation/).

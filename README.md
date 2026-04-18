# research-hub

Static GitHub Pages site + SQLite-backed research repository for audience research, market insights, landing page recommendations, and product strategy.

## Structure
- `data/research.db` — SQLite database
- `data/exports/*.json` — exported site data
- `content/raw/` — raw notes and manually captured research
- `content/generated/` — generated summaries
- `schema/schema.sql` — database schema
- `scripts/` — ingest, export, and static site build scripts
- `src/` — static site source files
- `.github/workflows/` — Pages deploy and daily refresh workflows

## Workflow
1. Add or update research in SQLite via scripts.
2. Export JSON for the site.
3. Build static pages.
4. Push to GitHub.
5. GitHub Actions deploys to Pages.

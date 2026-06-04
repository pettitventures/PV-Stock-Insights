# Static-Only Architecture

This project is intentionally static for now.

## Current Deployment Model

- Public hosting: Cloudflare Pages
- Build command: `python3 build_share_site.py`
- Output directory: `share`
- Public contents: HTML pages and SVG charts only

The generated website is designed for business colleagues. It is a research
site, not a live trading app.

## Data Policy

Raw market data stays local.

- `.env`, `.env.local`, and other secret files are ignored.
- `data/*.csv` is ignored.
- Raw 1-minute bars are not committed.
- Raw 1-minute bars are not uploaded to Supabase or any hosted database.

The repo can include derived artifacts such as markdown reports, candidate-rule
CSVs, SVG charts, and the generated static site.

## Verification

Before pushing a report update:

```bash
python3 build_share_site.py
python3 verify_static_site.py
git status -sb --ignored
```

Expected result:

- all public pages exist under `share/`
- all local page and chart links resolve
- no `.env`, database, parquet, or raw CSV files exist in `share/`
- Cloudflare Pages output remains `share`

## Database Decision

Do not add Supabase yet.

Add a database later only if the project needs:

- paper-trade tracking
- collaborator notes or annotations
- login/auth
- saved research runs
- searchable pattern records
- dashboards that update without rebuilding the static site

If that time comes, use Supabase for metadata and paper-tracking records, not raw
minute-bar storage.

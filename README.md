# Airyanem Atlas website

Static bilingual (English / Farsi) site for [@airyanematlas](https://x.com/airyanematlas), live at https://airyanematlas.github.io

- `_src/build.py` generates the site (Python standard library only). It publishes only items dated today or earlier (Pacific time), so scheduled pieces appear on their date automatically.
- `.github/workflows/site.yml` rebuilds and deploys every day at about 7 am Pacific and on every push.
- Content lives in `_src/data/` (`pieces.json`, `evening.json`, `config.json`) and `_src/img/<piece-id>/` (web images and the high-resolution JPG downloads).
- `_src/ingest.py` converts an infographic folder (EN/ and FA/ with X-ready JPGs and Posts_*.md) into web images and a `pieces.json` entry.

Add a piece: run `ingest.py`, commit, push. Add an evening post: append to `_src/data/evening.json`.

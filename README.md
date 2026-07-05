# Two Listeners, One Question — demo dashboards

Two interactive D3.js dashboards comparing the Spotify/Apple Music listening
histories of **Or** and **Roman**. Full project write-up: `DATA/README.md`.
Design source of truth: `DATA/CLAUDE.md`.

## Run the dashboard

The prepared JSON in `data/` is committed, so no Python is needed just to view it:

```bash
# from the repo root — any static server works
python3 -m http.server 8137
# then open http://127.0.0.1:8137/index.html
```

Opening `index.html` via `file://` will NOT work — the page fetches `data/*.json`,
which browsers block from the local filesystem.

## Regenerate the data (only after changing prep or the CSVs)

Requires the raw exports in `DATA/` (gitignored, ~110 MB — copy them over manually)
and pandas:

```bash
python3 -m venv .venv
.venv/bin/pip install pandas
.venv/bin/python prepare_data.py   # rewrites data/*.json, prints ground truths
```

Check the printed ground truths against the table at the end of `DATA/CLAUDE.md`
before trusting the output.

## Layout

| path | what |
|---|---|
| `index.html` | the whole site (both dashboards, inline CSS/JS) |
| `lib/d3.v7.min.js` | vendored D3, so the demo works offline |
| `data/*.json` | small per-chart aggregates (committed) |
| `prepare_data.py` | CSV → JSON prep, prints verification numbers |
| `DATA/` | raw CSV exports (gitignored) + project docs (committed) |

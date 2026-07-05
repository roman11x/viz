# CLAUDE.md — repo root (session context)

Read this first. The **locked dashboard design, data dictionary, honesty constraints,
and ground truths** live in `DATA/CLAUDE.md` — treat that file as the source of truth
for anything design- or data-related. `DATA/README.md` is the project write-up.
`message.txt` (untracked) was the original build brief.

## Current state (2026-07-05)

The demo is **built, verified, and committed**. Both dashboards work:

- `prepare_data.py` — Python/pandas prep; reads `DATA/*.csv`, writes `data/*.json`
  (~130 KB total), prints the CLAUDE.md ground truths at the end.
- `index.html` — the whole site: one static page, D3 v7 (vendored at
  `lib/d3.v7.min.js`), inline CSS/JS, no build step. Dashboard 1 (intensity river,
  linked routine heatmaps, day-length distribution) + Dashboard 2 (three charts:
  a LINKED discovery-per-year line + artist-stickiness stacked bars — clicking a
  year in the line filters the bars to that cohort — plus the artist-takeover
  stacked bars; headline numbers annotated on the charts), one global period
  selector (All / COVID / Pre-uni / University) that re-renders every panel,
  tooltips everywhere.
- `data/*.json` — committed, so the site runs **without** the raw CSVs.

## Running it

See `README.md`. Short version: serve the repo root with any static server and open
`index.html` (it fetches `data/*.json`, so `file://` will not work).

## Raw data

`DATA/*.csv` (~110 MB) is **gitignored** — copy it manually to a new machine only if
you need to re-run `prepare_data.py`. Never commit the CSVs. The browser must never
load `fact_plays*.csv`.

## Environment notes

- `.venv/` (gitignored) holds pandas + playwright. Recreate with:
  `python3 -m venv .venv && .venv/bin/pip install pandas playwright && .venv/bin/playwright install firefox`
- Playwright's headless Firefox was used to verify rendering, filtering, tooltips,
  and the linked heatmap highlight (no console errors). System `firefox --headless
  --screenshot` also works but needs `--no-remote --profile <tmpdir>` if Firefox is
  already running.
- No Node.js was available on the original machine.

## Implementation decisions already made (do not re-litigate silently)

- **Data window and periods** are named constants in `prepare_data.py`: `DATA_START`
  = 2020-01 (everything earlier is dropped from every output) and `PERIODS`:
  COVID = 2020-01 … 2021-12, Pre-uni = 2022-01 … 2023-12, University = 2024-01 … end.
  Whole-year buckets today; a mid-year cutoff is a one-line boundary edit. They ship
  to the browser in `data/meta.json`; change them only there and re-run the prep.
- **Heatmap aggregates come from `fact_plays.csv`** (prep-only), not
  `hour_weekday_year.csv`, so period boundaries are exact even if a cutoff ever
  moves mid-year.
- **Period-filtered artist stats (including the "All" period) come from
  `plays_daily.csv`** — it is the only artist-level table that can be trimmed to the
  `DATA_START` window (`artist_totals.csv` is all-time from 2018-09). Known caveat,
  commented in `prepare_data.py`: plays_daily lacks ~4k plays whose artist or date
  is missing in the raw export.
- **Exception — the discovery/stickiness pair uses `artist_totals.csv` all-time on
  purpose** (`data/artists.json`): "discovered" means first play ever and "stuck"
  means total plays ever, so trimming would fake both. The window only sets the
  discovery-line x-axis start (2020); caveats (left-censored early years, partial
  last year, all-time play counts) are annotated in the UI.
- **River honesty**: each person's area starts at their own first month inside the
  window (Or 2020-01, Roman 2020-04); only interior gap months (Roman has one,
  2020-10) are zero-filled.
- **Skips** = `short_plays / plays` (the comparable under-30s measure). Never native
  skip counters.
- **Palette is locked**: Or `#E69F00`, Roman `#0072B2` (Wong pair). Text never wears
  the raw series color — darkened ink variants `#8a5f00` / `#005a8e` are used for
  text. Heatmaps use a single-hue ramp of each person's color (HCL-interpolated,
  square-root scale, neutral grey for zero cells, legend under each grid); no second
  categorical palette inside one person's chart — within-person categories (e.g. the
  takeover bar's rank groups) use lightness steps of that person's hue.
- **Music motifs are decoration-only** (added 2026-07, maintainer-requested):
  Side A / Side B chips on the dashboard headers, small grey panel icons, a "▶"
  prefix on the active period control, and the "Liner notes" footer. They must
  never encode data, introduce colors beyond the locked palette, or replace
  labels. Do not add louder decoration. (A header waveform strip was tried and
  reverted — the maintainer found it read as a squished chart.)
- **Out of scope** (decided): shared-vs-unique artists chart, Lorenz curve, top-artist
  leaderboard hero, discovery scatter hero, map, genre as a primary panel, backend,
  build tooling.

## Ground truths — verify after any prep change

`prepare_data.py` prints these (2020-01+ window totals); the dashboard must display
the same:

- Or #1 artist = Imagine Dragons, 14.6% of minutes; Roman #1 = Sleep Token, 25.6%.
- under_30s overall: Or 38.2%, Roman 29.4%.
- Unique artists: Or 1,241; Roman 3,854.
- Robust check regardless of where the cutoff sits: Sleep Token ≈ 25% of Roman's
  minutes (Roman barely predates 2020).

If a number stops matching, stop and tell the maintainer — never adjust data to fit.

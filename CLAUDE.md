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
  linked routine heatmaps, day-length distribution) + Dashboard 2 (three headline
  cards), one global period selector (All / Army / COVID / University) that
  re-renders every panel, tooltips everywhere.
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

- **Periods** are named constants in `prepare_data.py` (`PERIODS`): Army = start …
  2021-06, COVID = 2021-07 … 2023-09, University = 2023-10 … end. They ship to the
  browser in `data/meta.json`; change them only there and re-run the prep.
- **Heatmap aggregates come from `fact_plays.csv`** (prep-only), not
  `hour_weekday_year.csv`, because the period boundaries cut mid-year and the year
  file cannot represent them exactly.
- **All-time artist stats come from `artist_totals.csv`**, not `plays_daily.csv`:
  `plays_daily` is missing ~4k of Or's plays (rows with no artist/date in the raw
  export), which would shift his top-artist share from 14.3% to 14.4% and undercount
  unique artists. The three sub-periods use `plays_daily.csv` (the only
  period-filterable artist source). Commented in `prepare_data.py`.
- **River honesty**: each person's area starts at their own first month (Roman
  2019-09); only interior gap months (Roman has 5 in 2019–2020) are zero-filled.
- **Skips** = `short_plays / plays` (the comparable under-30s measure). Never native
  skip counters.
- **Palette is locked**: Or `#E69F00`, Roman `#0072B2` (Wong pair). Text never wears
  the raw series color — darkened ink variants `#8a5f00` / `#005a8e` are used for
  text. Heatmaps use a single-hue ramp of each person's color; no second categorical
  palette inside one person's chart.
- **Out of scope** (decided): shared-vs-unique artists chart, Lorenz curve, top-artist
  leaderboard hero, discovery scatter hero, map, genre as a primary panel, backend,
  build tooling.

## Ground truths — verify after any prep change

`prepare_data.py` prints these; the dashboard must display the same:

- Or #1 artist = Imagine Dragons, 14.3% of minutes; Roman #1 = Sleep Token, 25.4%.
- under_30s overall: Or 41.5%, Roman 30.0%.
- Unique artists: Or 1,436; Roman 4,036.

If a number stops matching, stop and tell the maintainer — never adjust data to fit.

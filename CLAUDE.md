# CLAUDE.md — "Two Listeners" music visualization

Persistent guidance for this repo. Read before every task.

## What this project is
A static D3.js website for a University of Haifa Data Visualization course. It compares two people's
complete personal listening histories: **אור (Or)** — Apple Music — and **רומן (Roman)** — Spotify.
Central question: is similarity between two listeners only about taste, or also about routine and intensity?

Two dashboards:
1. **Listening DNA** — musical identity: genres, artists, concentration, overlap.
2. **Before Uni vs Uni: Music as Routine** — how routine and intensity changed when university began.

## Stack and hosting
- pandas for data prep; D3.js for every chart (required). No build step. Static files on GitHub Pages.
- Ship only compact aggregates, embedded as a single `EMBEDDED_DATA` object in `data.js`.
  Do NOT ship the ~180k-row event table to the browser.

## Locked constants
- Data window: **2021-01 onward** (earlier data dropped; pre-2021 is thin/uneven for Roman).
- Periods: `pre_uni` = 2021-01..2023-12; `university` = 2024-01 onward. Define as documented constants
  in both `prep.py` and the JS.

## Hard rules
- English for all code, comments, UI chart titles, and file/column names. UI display names are Hebrew: אור / רומן.
- Use ONLY the provided CSVs. Never invent artists, figures, or data points. If a needed field is missing,
  say so and propose the closest available alternative.
- Genre is an EXTERNAL add-on and is partial; the long tail is bucketed as "Other". Mark genre as
  external/provisional wherever it appears, and never hide "Other".
- Skips use the comparable `under_30s` measure (or `short_plays / plays`). Never use native skip counters —
  Apple and Spotify count skips differently, so `skipped_native` is not comparable across people.
- No map: city-level location exists only for Or.
- The absolute-vs-normalized toggle is first-class, not decoration: Roman has higher total volume, so
  normalized share is what makes taste/routine comparisons fair.
- Keep it minimal. No over-engineering, no speculative abstractions, no extra files. Remove any temporary
  scratch scripts at the end.
- Show evidence (printed numbers, verification checks); do not just assert success.

## Colors and state
- Fixed, colorblind-safe owner colors, strong on a dark background: אור = bright blue (~`#4EA1FF`),
  רומן = bright orange/amber (~`#FF9F1C`). Same colors in every chart and the legend.
- In a single-person chart with categories (that person's genres/artists), use only LIGHTNESS steps of that
  person's single hue — never a second categorical palette.
- Global state object every chart reads from and writes to:
  `{ dashboard, period, metricMode, selectedGenre, selectedArtist, selectedWindow }`.

## Data files (English names)
- `fact_plays_with_genre.csv` — event-level (~180,003 rows). Prep only; never shipped to the browser.
- `fact_plays_SAMPLE.csv` — a 300-row schema sample. NOT the real data; do not compute from it.
- Aggregates (full-history, re-cut to 2021+ in prep): `owner_summary`, `artist_totals(_with_genre)`,
  `monthly_totals`, `daily_totals`, `hour_weekday(_year)`, `hourly_profile`, `genre_monthly`,
  `plays_daily(_with_genre)`.
- `under_30s` lives in the fact table; `short_plays`/`plays` in `plays_daily` is its aggregate proxy.

## Sanity anchors (FULL history — recompute on 2021+, do NOT hardcode)
Expect the 2021+ numbers to differ; these are only rough checks.
- Or ≈ 2,802 h / 97,000 plays / 1,436 artists / top artist Imagine Dragons.
- Roman ≈ 3,491 h / 83,003 plays / 4,036 artists / top artist Sleep Token.
- 192 shared artists. Minutes-weighted shared share ≈ 57.5% (Or) vs ≈ 2.1% (Roman) — overlap is ASYMMETRIC.
- Genre "Other" ≈ 28% (Or) / ≈ 36% (Roman).

## Gotchas
- The SAMPLE trap: for any event-level work use the full `fact_plays_with_genre.csv`, not the 300-row sample.
- Overlap must be weighted by minutes, not artist count. A count-based Venn misleads: 192 shared artists
  looks large, but it is 57% of Or's listening time versus 2% of Roman's.
- Periods differ in length, so compare rates/averages (e.g. average monthly hours), not raw period totals.
- Difference/divergence views apply only to scalar metrics (hours, under_30s%, concentration). An
  artist-level difference view is meaningless here — near-zero taste overlap makes it two disjoint lists.
- Genre coverage differs per person; do not overclaim genre precision.

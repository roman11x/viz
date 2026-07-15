# CLAUDE.md — "Two Listeners" music visualization

Persistent guidance for this repo. Read before every task.

## What this project is
A static D3.js website for a University of Haifa Data Visualization course. It compares two people's
complete personal listening histories: **Orr** — Apple Music — and **Roman** — Spotify.
Central question: is similarity between two listeners only about taste, or also about routine and intensity?

One scrolling page (no tabs), two stacked dashboards (hero → panel grid; the KPI strips were removed —
their numbers live in the written report, the page keeps only visualizations), in ONE personal,
story-driven voice ("Wrapped for two people") — measures serve the story:
1. **Listening DNA** — genre families, obsessions (top artists), minutes-weighted overlap.
2. **Before Uni vs Uni: Music as Routine** — whole-span waveform timeline, daily-rhythm heatmap,
   cumulative artist-discovery curve, slopegraph.
Seven panels, seven DISTINCT chart shapes: paired family bars / lollipop dot-plot / 100% strip /
mirrored-area waveform / heatmap / cumulative discovery curve / slopegraph small-multiples
(Pre-uni → University change). Panel titles are human questions. No takeaway lines (considered and
explicitly declined by the owner). EVERY panel responds to the global period filter; whole-span charts
(river, discovery curve) and the slopegraph respond by EMPHASIZING the selected period's region/side,
not by re-cutting. The daily-minutes histogram was replaced by the discovery curve (redundant with the
slopegraph's median-day and hours/month slopes).

## Stack and hosting
- pandas for data prep; D3.js for every chart (required). No build step. Static files on GitHub Pages.
- Ship only compact aggregates, embedded as a single `EMBEDDED_DATA` object in `data.js`.
  Do NOT ship the ~180k-row event table to the browser.

## Locked constants
- Data window: **2021-01 onward** (earlier data dropped; pre-2021 is thin/uneven for Roman).
- Periods: `pre_uni` = 2021-01..2023-12; `university` = 2024-01 onward. Define as documented constants
  in both `prep.py` and the JS.

## Hard rules
- English for all code, comments, UI chart titles, and file/column names. UI display names are English: Orr / Roman (changed from the earlier Hebrew אור / רומן — do not revert).
- Use ONLY the provided CSVs. Never invent artists, figures, or data points. If a needed field is missing,
  say so and propose the closest available alternative.
- Genre is an EXTERNAL add-on, partial, collapsed into ~6 broad FAMILIES (Pop, Rock, Israeli, Metal,
  Electronic/Dance, Hip-Hop/R&B + "Other"). A curated map in `prep.py` extends it for top unclassified
  artists — only confident assignments; the uncertain rest stays "Other", always visible. Mark genre as
  external/provisional wherever it appears.
- "Shared" artists require REAL listening on both sides (≥1 over-30s play each), not name-only matches.
  Overlap is weighted by minutes, never artist count (79 shared artists, but 39% of Or's minutes vs ~1% of Roman's).
- Skip behavior appears in the UI only as the comparable `under_30s` measure (shown as "plays kept past
  30 s" = 100 − under30_pct, in kpis and the slopegraph) — never native skip counters (Apple and Spotify
  count skips differently).
- Heatmaps use a PER-LISTENER color scale (own max across periods): the panel compares routine shape,
  and one absolute scale would let Roman's volume wash out Orr's pattern.
- Absolute, natural units by default; percentages ONLY in the overlap strip (where Roman's higher volume
  would mislead). No global absolute/normalized toggle.
- No map: city-level location exists only for Or.
- Keep it minimal. No over-engineering, no speculative abstractions, no extra files. Remove any temporary
  scratch scripts at the end.
- Show evidence (printed numbers, verification checks); do not just assert success.

## Colors and state
- Fixed, colorblind-safe owner colors, strong on a dark background: Orr = bright blue (~`#4EA1FF`),
  Roman = bright orange/amber (~`#FF9F1C`). Same colors in every chart and the legend.
- In a single-person chart with categories, use only LIGHTNESS steps of that person's single hue —
  never a second categorical palette. Muted gray for inactive marks.
- Heatmap cells ramp from a visible floor (`#242634`), not the page background, with a subtle grid so
  empty cells read as empty rather than invisible.
- State is kept PER DASHBOARD (independent stacked sections), each with its own period filter, reset,
  and removable filter chips:
  `{ d1: {period, selectedFamily, selectedArtist}, d2: {period, selectedWindow} }`.
- Whole-span charts (Dashboard 2 timeline, discovery curve) always draw the full span; the period
  filter dims the non-selected period band and outlines the selected one (emphasis, not re-cutting).

## Data files (English names)
- `fact_plays_with_genre.csv` — event-level (~180,003 rows). Prep only; never shipped to the browser.
- `fact_plays_SAMPLE.csv` — a 300-row schema sample. NOT the real data; do not compute from it.
- Aggregates (full-history, re-cut to 2021+ in prep): `owner_summary`, `artist_totals(_with_genre)`,
  `monthly_totals`, `daily_totals`, `hour_weekday(_year)`, `hourly_profile`, `genre_monthly`,
  `plays_daily(_with_genre)`.

## Sanity anchors (FULL history — recompute on 2021+, do NOT hardcode)
Expect the 2021+ numbers to differ; these are only rough checks.
- Or ≈ 2,802 h / 97,000 plays / 1,436 artists / top artist Imagine Dragons.
- Roman ≈ 3,491 h / 83,003 plays / 4,036 artists / top artist Sleep Token.
- 2021+ computed: Or 1,962.9 h / 1,108 artists; Roman 3,393.8 h / 3,756 artists; 79 truly-shared artists;
  shared minutes 38.8% (Or) vs 1.1% (Roman); family "Other" ≈ 15% (Or) / 23% (Roman) after curation.

## Gotchas
- The SAMPLE trap: for any event-level work use the full `fact_plays_with_genre.csv`, not the 300-row sample.
- Periods differ in length (36 vs 29 months; 1,095 vs 873 days in `meta.period_days`) — compare rates/averages.
- Hebrew names next to signed/parenthesized numbers get bidi-scrambled; put an LRM (`&lrm;` / `‎`)
  after the Hebrew run.
- Genre coverage differs per person; do not overclaim genre precision.

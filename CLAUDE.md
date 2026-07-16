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
- "Shared" artists require REAL listening on both sides (≥1 over-30s play each AND 3+ minutes each),
  not name-only matches. Overlap is weighted by minutes, never artist count (40 shared artists, but
  35.4% of Or's minutes vs 0.5% of Roman's).
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
- 2021+ computed: Or 1,962.9 h / 1,108 artists; Roman 3,393.8 h / 3,756 artists; 40 truly-shared artists
  (130 name-only matches); shared minutes 35.4% (Or) vs 0.5% (Roman); family "Other" 8.0% (Or) /
  14.2% (Roman) after curation.

## Verified single-month facts (do not restate differently)
Recomputed from the fact CSV. Narrative text (report, tooltips, annotations) must quote these exactly.
- Roman record month: 105.7 h (2024-05). Roman quietest month: 1.7 h (2021-03). Ratio ~61x.
  Never describe the record as "12x his quietest" — that figure came from dividing by Or's quietest
  month (8.8 h) by mistake.
- Or quietest month: 8.8 h (2026-03). It is NOT the last month of the window; 2026-04 and 2026-05
  rebounded (29.1 h, 34.4 h). Do not describe Or's listening as still fading based on 2026-03 alone.
- October 2023 timing nuance (window-level, verified): Roman's volume level-shift (33-month
  pre-Oct-2023 average 31.5 h/month -> 73.6 h/month from Oct 2023 on) and his move into night
  listening (22:00–05:59 share of minutes 17–20% in Jul–Sep 2023 -> 39–53% in Oct–Dec 2023) both
  begin in October 2023, three months before the calendar period boundary. Or played 0 minutes on
  2023-10-07 and discovered zero new artists in both 2023-10 and 2023-11 (the only consecutive
  zero-discovery months in the window). The dashboards keep the locked two-period split; this note
  exists so narrative text never attributes these specific shifts to the university calendar alone.

## Gotchas
- The SAMPLE trap: for any event-level work use the full `fact_plays_with_genre.csv`, not the 300-row sample.
- Periods differ in length (36 vs 29 months; 1,095 vs 873 days in `meta.period_days`) — compare rates/averages.
- Hebrew names next to signed/parenthesized numbers get bidi-scrambled; put an LRM (`&lrm;` / `‎`)
  after the Hebrew run.
- Genre coverage differs per person; do not overclaim genre precision.

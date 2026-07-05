# CLAUDE.md — Music Listening Comparison Dashboards

Persistent project context. Read this first, every session. Keep answers grounded in
the actual files — read a file before making claims about it.

## What this project is
An interactive data-visualization project comparing the Spotify listening histories of
two people, **Or** and **Roman**, whose musical taste barely overlaps. Built for a
university Information Visualization course. Deliverable: two interactive dashboards
(D3.js), hosted on GitHub Pages.

## Research question
How do two people with almost non-overlapping musical taste use music similarly or
differently as part of their lives, routine, and life periods? Put differently: does
similarity between listeners have to live in *taste*, or can it be found in *listening
patterns, routine, and intensity of connection to music*?

## The story the dashboards must convey
- Taste barely overlaps (~0.6% time-weighted; 0 shared artists in either person's
  top 100). Do **not** build a "shared vs unique artists" chart — it is not interesting.
- Similarity and difference live in **behavior**: Or = *consistency* (listens on more
  days; morning listener). Roman = *intensity* (fewer but much heavier days and
  sessions; evening/night listener; Sleep Token alone is ~25% of his hours).
- The comparison **changes by life period** — that shift is the point.

## People and color
- Exactly two subjects: `Or` and `Roman`. Give each ONE fixed, colorblind-safe color,
  reused in every chart.
- Rule: in a chart that compares the two people, color encodes the person (two colors,
  nothing else). In a chart showing categories *within* one person (e.g. genres), do not
  add a second categorical palette — use position/length, or the lightness of that
  person's single hue (sequential single-hue).

## Data window and life periods (adjustable constants in the prep script)
The whole project is trimmed to a global data window starting **2020-01**
(`DATA_START` in `prepare_data.py`); everything earlier is dropped from every output.
Three whole-year windows, chosen via ONE global control that filters every panel on
both dashboards:
- `COVID`: 2020-01 … 2021-12
- `Pre-uni`: 2022-01 … 2023-12
- `University`: 2024-01 … end   ← key fair-comparison window (both started university
  the same semester)
These boundaries are defaults — keep them as named constants so a mid-year cutoff, if
ever needed, is a one-line change. Roman's data is sparse before 2021, so the early
`COVID` months are Or-heavier; show that honestly, do not hide it.

## Data — use ONLY these files; never invent artists, dates, or figures
CSVs in the repo root. The prep step reads them. The browser must NOT load the big
`fact_plays*` tables (~50 MB each) — prep distills small JSON for D3.

| file | key columns | use for |
| --- | --- | --- |
| `owner_summary.csv` | owner, play_events, listens_over_30s, hours, unique_artists, first_play, last_play, top_artist | headline totals, coverage |
| `monthly_totals.csv` | owner, ym, plays, minutes | Intensity river (hours/month) |
| `daily_totals.csv` | owner, date, plays, minutes | Day-length distribution (minutes per active day) |
| `hour_weekday.csv` | owner, weekday, hour_local, plays, pct_of_owner | Routine heatmap (all-time) |
| `hour_weekday_year.csv` | owner, year, weekday, hour_local, plays, pct_of_owner_year | Routine heatmap per period |
| `artist_totals.csv` | owner, artist, plays, minutes, first_played, last_played, rank_in_owner | concentration, #1-artist share |
| `plays_daily.csv` | owner, date, artist, track, plays, short_plays, minutes | per-period artist/skip aggregates |
| `artist_genres.csv`, `*_with_genre.csv`, `genre_monthly.csv` | + genre | genre panels (external add-on only) |
| `fact_plays.csv` | play_id, played_at_local, hour_local, weekday, under_30s, … | prep-only source of truth (timestamps, sessions) |

Honesty constraints, flag them on-screen where relevant:
- Skips: services' native skip counters are not comparable. Use the comparable measure
  **`under_30s`**, realized in the aggregates as `short_plays / plays`.
- Genre is an **external add-on** and partial (Other/blank ≈ 30% for Or, 44% for Roman).
  Mark any genre element "external / provisional". Prefer non-genre charts.
- Location: city-level exists only for Or → no map panel.
- Date coverage differs (Or from 2018-09; Roman effectively active from 2021). The
  analysis window is trimmed to 2020-01 onward — say so on-screen; Or's 2018–2019
  history exists in the CSVs but is excluded by design.

## Dashboards (locked design)
Two dashboards share one global period control and tooltips everywhere (details on
demand). Use raw numbers when magnitude is the finding; normalized % when comparing
structure.

### Dashboard 1 — "Two rhythms" (routine and intensity)
1. **Intensity river (hero).** Q: how does each person's monthly volume rise and fall
   across periods, and when do they converge or diverge? Mirrored area — Or above the
   axis, Roman below — hours per month, on a flat stable baseline (NOT a wiggly
   streamgraph). A timeline strip below the river is the period selector. Hover = a guide
   line plus both people's hours for that month. Source: `monthly_totals.csv`.
2. **Routine heatmap.** Q: when in the day and week does each person listen (Or mornings,
   Roman nights)? An hour × weekday heatmap, one per person, shared scale, color =
   `pct_of_owner` (single hue per person, HCL-interpolated on a square-root scale so
   mid/low values stay distinguishable; zero cells neutral grey; small legend under each
   grid). Hover = pct + raw plays. Linked highlight: hovering a weekday lights the same
   row in the other heatmap. Source: `hour_weekday(_year).csv`.
3. **Day-length distribution.** Q: on active days, how heavy is a typical day, and who
   has the much heavier ones? Grouped column chart: x = active-day-length buckets
   (≤30m, 30–60, 1–2h, 2–3h, 3–5h, 5h+), y = % of that person's active days, two bars per
   bucket. No numbers printed on bars — raw day counts live in the hover tooltip; ONE
   annotation calls out the 5h+ gap, where magnitude is the finding. Source:
   `daily_totals.csv`.

### Dashboard 2 — "Depth of connection" (audience: curious streaming users, "Wrapped-plus")
Three real charts, one question each, each with its headline annotated ON the chart
plus one plain sentence; all period-filterable, all obeying the two-color = two-people
rule (within-person categories use lightness of that person's hue). Charts 1+2 are a
LINKED pair (discovering artists vs. those artists sticking), built from one shared
table (`data/artists.json`: owner × first-played year × play-count tier, from
`artist_totals.csv` — first plays and play counts are all-time, deliberately not
trimmed to the window).
1. **"Do you keep discovering, or stay in a known world?"** — a line chart of newly
   discovered artists per year (x = year from 2020, y = artists first played that
   year, line per person). Period years emphasized, others dimmed. Clicking a year
   filters chart 2 to that cohort. Honesty, annotated on-chart: earliest years are
   left-censored (histories start 2018-09 / 2019-09, returning favorites count as
   "new"); the last year is partial.
2. **"Of all the artists you tried, how many stuck?"** — a 100% stacked horizontal bar
   per person, split by all-time play-count tier (1 play / 2–9 / 10–49 / 50+); darker
   = more plays = stuck. Headline = the 50+ share. Cohort = the clicked year, else the
   period's discovery years, else the full list ("All" includes pre-2020 discoveries);
   a label + reset control names the active cohort. Caveat: play counts are all-time,
   recent cohorts have had less time to stick.
3. **"How much did one artist take over?"** — a 100% stacked horizontal bar per person,
   split by artist rank (#1 / #2–5 / #6–10 / rest) as share of that person's hours;
   darker = closer to #1. Headline = the #1 artist's share.

Retired (replaced 2026-07 by the linked pair above; do not resurrect silently): the
monthly `under_30s` skip line and the cumulative half-your-hours curve.

Do NOT build (already decided against): shared-vs-unique artists; a Lorenz curve; a
treemap; a Sankey; a plain top-artist leaderboard or a discovery *scatter* as a hero
(the Dashboard-2 discovery *line* + stickiness pair above is maintainer-sanctioned).

## Tech and workflow
- Prep: Python + pandas. Reads the CSVs, writes small per-chart JSON into `data/`. The
  full `fact_plays.csv` may be used here for hour-of-day and session logic, but is never
  shipped to the browser.
- Visualization: **D3.js (required)**, static HTML/CSS/JS, GitHub Pages (serve from
  `/docs` or repo root). No build step.
- All code, comments, UI text, and file/column names in English.
- Every visualization documents — in code comments and a short on-page note — the
  question it answers, its data mappings (what each axis/color/size encodes), and its
  interactions (filter / highlight / tooltip).
- Prioritize insight over decoration: no chart junk, no truncated axes, label any log
  scale. Clean, restrained styling; motion only for meaningful transitions.
- When explaining code to the maintainers, explain it line by line, in plain calm
  language.

## Verify before claiming done (CSV ground-truths, 2020-01+ window)
Compute these in the prep script, print them, and confirm the dashboards show matching
numbers. All are window totals from `plays_daily.csv` trimmed to `DATA_START`
(`artist_totals.csv` is all-time-only and cannot be trimmed, so it is no longer the
artist source):
- Roman's #1 = Sleep Token, 25.6% of minutes; Or's #1 = Imagine Dragons, 14.6%.
- `under_30s` (short_plays / plays) overall: Or 38.2%, Roman 29.4%.
- Unique artists: Or 1,241; Roman 3,854.
- Robust check that should hold wherever the cutoff sits (Roman barely predates 2020):
  Sleep Token ≈ 25% of Roman's minutes.

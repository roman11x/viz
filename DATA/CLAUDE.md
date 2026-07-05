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

## Life periods (adjustable constants in the prep script)
Three windows, chosen via ONE global control that filters every panel on both dashboards:
- `Army`: start … 2021-06
- `COVID`: 2021-07 … 2023-09
- `University`: 2023-10 … end   ← key fair-comparison window (both started university
  the same semester)
These boundaries are defaults — keep them as named constants so they are easy to change.
Roman's data is sparse before 2021, so the `Army` window is Or-dominant; show that
honestly, do not hide it.

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
- Date coverage differs; overlap is 2019–2026 (Or from 2018-09; Roman effectively active
  from 2021).

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
   `pct_of_owner` (single hue). Hover = pct + raw plays. Linked highlight: hovering a
   weekday lights the same row in the other heatmap. Source: `hour_weekday(_year).csv`.
3. **Day-length distribution.** Q: on active days, how heavy is a typical day, and who
   has the much heavier ones? Grouped column chart: x = active-day-length buckets
   (≤30m, 30–60, 1–2h, 2–3h, 3–5h, 5h+), y = % of that person's active days, two bars per
   bucket. Raw count label on the heavy buckets (where magnitude is the finding). Hover =
   exact day count. Source: `daily_totals.csv`.

### Dashboard 2 — "Depth of connection" (audience: curious streaming users, "Wrapped-plus")
Each chart = one big headline number per person + one plain sentence + a small detail;
all period-filterable.
1. **"How much did one artist take over?"** — the #1 artist's share of that person's hours.
2. **"When you hit play, did you stay or skip?"** — the `under_30s` rate.
3. **"How many artists make up half your hours?"** — count of artists needed to reach 50%
   of cumulative hours.

Do NOT build (already decided against): shared-vs-unique artists; a Lorenz curve; a plain
top-artist leaderboard or a discovery scatter as a hero (too "Wrapped-descriptive"; does
not answer the behavior question).

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

## Verify before claiming done (CSV ground-truths, all-time)
Compute these in the prep script, print them, and confirm the dashboards show matching
numbers:
- Sleep Token = 25.4% of Roman's minutes; Roman's #1 = Sleep Token; Or's #1 = Imagine
  Dragons (14.3%).
- `under_30s` (short_plays / plays) overall: Or 41.5%, Roman 30.0%.
- Unique artists: Or 1,436; Roman 4,036.

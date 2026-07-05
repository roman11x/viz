# Two Listeners, One Question — a music-listening visualization project

An interactive, data-driven set of D3.js dashboards comparing the listening
histories of **Or** (Apple Music) and **Roman** (Spotify), built **only** from the
provided CSV export files. No values are invented. Where a service does not record a
field, the cell is left empty.

## Research question

> How do two people with almost non-overlapping musical taste use music in
> similar or different ways as part of their lives, routine, and life periods?

Alternative phrasing: *Does similarity between listeners have to live in musical
taste, or can it be found in listening patterns, routine, and the intensity of the
bond to music?*

The taste barely overlaps (about **0.6%** time-weighted, **0** shared artists in
either person's top 100). So the project is not "who likes what." It asks whether two
very different listeners still resemble each other in **behavior, routine, and
depth of connection** — and where they diverge.

## Audience

Music-streaming users who are curious about what their listening history says about
their life, beyond a yearly Wrapped/Replay. Every panel leads with one plain-language
question and one headline number, then offers detail on demand.

---

## The two dashboards

Each visualization answers a question, reveals a pattern, and documents its data
mappings and interactions. We prioritize insight over decoration and pick the clearest
chart the course taught for each question.

### Dashboard 1 — Two rhythms (routine & intensity)

1. **Intensity river** — *How does each person's listening volume rise and fall across
   life periods, and when do they converge or diverge?*
   Mirrored area: Or above a flat baseline, Roman below, hours per month. Keeps the
   "river" look but each side sits on a fixed baseline (no streamgraph wiggle), so
   heights are readable. Color = person. Interaction: a period timeline strip below the
   chart is the global filter; hover shows both people's hours for that month.

2. **Routine heatmap** — *When during the day and week does each person listen (Or in
   the morning, Roman at night)?*
   Hour × weekday heatmap, one per person, shared scale. Color = `pct_of_owner`
   (normalized, so the two are comparable despite different volumes), single-hue
   sequential ramp. Interaction: filtered by the period control; hover shows the exact
   percentage and raw play count; hovering a weekday row highlights the same row in the
   other person's heatmap.

3. **Day-length distribution** — *On days someone actually listens, how heavy is a
   typical day, and who has much heavier days?*
   Grouped column chart (a frequency distribution): x = active-day length in fixed
   buckets (≤30m, 30–60m, 1–2h, 2–3h, 3–5h, 5h+), two columns per bucket (Or, Roman),
   y = share of that person's active days. Raw counts labelled on the heavy buckets,
   where the size itself is the finding. A small per-period skip-rate figure
   (`under_30s`) sits alongside. This is the "consistency vs. intensity" contrast.

### Dashboard 2 — Depth of connection (a Wrapped-plus view)

Each panel = one big headline number per person + one sentence + detail.

1. **How much did one artist take over?** — top-1 artist's share of hours per person
   (Roman's Sleep Token ~25%, up to ~33% in the university period; Or's ~14%).
2. **When you hit play, did you stay?** — the comparable `under_30s` skip rate per
   person and period (Or ~41%, Roman ~30%).
3. **How many artists make up half your hours?** — one number per person and period,
   next to each person's total unique artists (Or concentrated; Roman a huge center of
   gravity *and* a long tail of 4,036 artists).

Genre is available but stays an optional, clearly-labelled *provisional* panel (see
limits). We do **not** ship a "shared vs. unique artists" chart: the overlap (~0.6%) is
too small to be worth a panel.

### Shared interaction model

- **Global period control** (COVID / Pre-uni / University) filters every panel at once
  (linked filtering). Default: both people always shown together, compared by period —
  not a manual toggle between Or and Roman.
- **Tooltips** everywhere (details on demand).
- **Brushing / linked highlight** between panels where it adds value.
- **Raw numbers when size is the finding; normalized percentages when comparing shape.**

### Color

Two-color categorical, colorblind-safe and distinct in grayscale (Wong palette):
Or = orange `#E69F00`, Roman = blue `#0072B2`. Color encodes **person** only in
cross-person charts. Inside a single person's chart (e.g. top artists), categories are
separated by position/length or by lightness of that person's single hue — never by a
second color scale.

---

## Data files

Built to local time (Asia/Jerusalem) so the two histories line up. Artist names are
normalized (duplicates merged); `artist_raw` keeps the original spelling.

| file | grain | who | use |
|---|---|---|---|
| `fact_plays.csv` / `fact_plays_with_genre.csv` | one row per play event (has timestamps) | both | source for the Python prep only — **not shipped to the browser** |
| `plays_daily.csv` / `plays_daily_with_genre.csv` | owner × day × artist × track | both | per-period genre, skip rate, artist rankings |
| `daily_totals.csv` | owner × day (plays, minutes) | both | active days, day-length distribution |
| `monthly_totals.csv` | owner × month | both | intensity river |
| `hourly_profile.csv` | owner × hour (0–23) | both | overall daily rhythm |
| `hour_weekday.csv` | owner × weekday × hour | both | routine heatmap |
| `hour_weekday_year.csv` | owner × year × weekday × hour | both | per-period heatmap |
| `artist_totals.csv` / `artist_totals_with_genre.csv` | owner × artist | both | concentration, top artists |
| `genre_monthly.csv` | owner × month × genre | both | optional genre panel |
| `artist_genres.csv` | artist → genre map | — | the external genre add-on |
| `owner_summary.csv` | one row per person | both | headline totals |

The comparable skip measure is `under_30s` (a play under 30 seconds), computed
identically for both services from `ms_played`. Its aggregate form is `short_plays` in
`plays_daily`. Do **not** compare each service's native skip counter — Apple and Spotify
count skips differently.

---

## Honest limits (state these in the UI where relevant)

- **Different date ranges.** Or's history starts 2018-09; Roman's 2019-09. The strict
  head-to-head overlap is **2019–2026**, and Roman is **sparse before 2021** — so the
  earliest period is Or-dominant and is labelled as low-data for Roman rather than
  compared as if equal.
- **Genre is an external add-on.** It is not in either export; it was attached per
  artist afterward. Coverage is partial (~67% of Or's plays, ~56% of Roman's carry a
  genre; the rest are `Other`). Any genre panel is marked *provisional / external*.
- **City-level location exists only for Or** (Apple's IP-derived city; Spotify does not
  provide it), so there is no map panel.

---

## Architecture & hosting

Static site on **GitHub Pages**. Python (pandas) does all data prep; D3.js does all
visualization.

1. `prep/build_data.py` reads the CSVs (including the large `fact_plays.csv` for
   timestamp-level work such as hours-by-hour and sessions) and writes small,
   pre-aggregated **JSON** files into `docs/data/`.
2. The browser loads only those small JSON files — never the ~50 MB `fact_plays.csv`.
3. `docs/` is the published site (`index.html`, `js/`, `css/`, `data/`).

Run:

```bash
python prep/build_data.py      # regenerate docs/data/*.json from the CSVs
# then open docs/index.html, or serve docs/ locally, or push docs/ to GitHub Pages
```

All code, comments, UI text, and file/column names are in English.

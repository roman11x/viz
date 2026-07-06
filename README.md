# Two Listeners, One Question

An interactive D3.js page comparing two friends' complete personal listening histories —
**אור (Or)**, an Apple Music listener, and **רומן (Roman)**, a Spotify listener. Built for a
University of Haifa Data Visualization course.

The guiding question: *do two friends need the same songs to share music — or is it enough to
share the rhythm: listening patterns, routine, and intensity?*

## The pivot behind the design

Taste overlap between the two is tiny and, more interestingly, **asymmetric**: a large share of Or's
listening time is on artists Roman also really plays, while almost none of Roman's time flows back
(Roman's wide exploration brushes past Or's mainstream pop, but Roman's metal core is absent from
Or's world). So the project does not try to find common taste. Instead:

- **Dashboard 1** treats taste as a *contrast* — two different musical worlds — and shows the asymmetric overlap honestly.
- **Dashboard 2** looks for the deeper kind of similarity: routine and intensity, and how both changed when university began.

The page is one continuous scroll; each dashboard is laid out classically — a KPI strip on top,
then a grid of coordinated panels with the hero view first — and every panel is titled with the
question it answers, in one consistent personal voice.

## The six panels — six distinct chart shapes

### Dashboard 1 — "Listening DNA"
- **What two musical worlds do we live in?** — paired horizontal bars of broad genre *families*
  (fine external tags collapsed into ~6 families; the residual "Other" stays visible). Click a
  family to filter the artist panel; tooltip shows minutes, share, and the family's top artist.
- **Who are our obsessions?** — a dot-plot / lollipop of each person's top-10 artists. A ring in
  the other person's color marks artists both really play. Hover to spotlight an artist everywhere;
  click for a detail card (minutes, plays, first/last played, family, shared or unique).
- **How much music do we actually share?** — a minutes-weighted 100% proportion strip per person
  (shared vs "mine alone"), plus the top shared artists by name. Deliberately not a Venn: counting
  names would look symmetric, but listening *time* is not. This is the one place the page uses
  percentages — Roman simply plays more hours, and raw minutes would mislead.

### Dashboard 2 — "Before Uni vs Uni: Music as Routine"
- **How has our listening ebbed and flowed since 2021?** — a mirrored area over the whole span
  (Or above the baseline, Roman below) styled as a listening waveform: one vertical grain line per
  real month, each encoding that month's hours. The 2024-01 university line is marked. This hero
  panel deliberately ignores the period filter — it is the overview.
- **When in the day do we listen?** — an hour × weekday heatmap per person for the selected
  period; the period filter is the before/after mechanism. Cells have a visible color floor and a
  subtle grid so an empty cell reads as empty, not invisible. Click a cell for that hour's top
  artists and families; hover a weekday to follow its column.
- **What do our listening days look like?** — a per-person histogram of daily listening minutes
  (30-minute bins, shared scales). Or's days cluster as steady moderate listening; Roman has many
  light days and a long binge tail.

Each dashboard has its own period filter (Pre-uni / University), a working reset, and removable
filter chips, so the two sections never interfere.

## Data and pipeline

Both histories are built only from the official export files: Or's Apple Music privacy export and
Roman's Spotify *Extended Streaming History*. Timestamps are converted to local time
(Asia/Jerusalem) so the two line up, and artist names are normalized (duplicates merged). The core
event table `fact_plays` has 180,003 rows — one per play — which is the true apples-to-apples layer.

**Genre is an external add-on**: it is not in either export, so it was added by classifying artists
externally, then collapsed into ~6 broad families. The biggest still-unclassified artists were
assigned a family only where identification was confident; everything uncertain stays in an honest
"Other" (about 15% of Or's minutes and 23% of Roman's after curation, down from ~30/36%).

**"Shared" requires real listening on both sides** — at least one over-30-seconds play by each
person, not just a name appearing in both exports. That drops name-only matches (130 → 79 artists
in the 2021+ window).

`prep.py` filters everything to 2021+, assigns the two periods (pre-uni = 2021-01..2023-12,
university = 2024-01+), and rebuilds all aggregates into a single embedded `data.js`. The ~180k-row
event table is used only during prep and is never shipped to the browser.

## Running it

```
python prep.py        # writes data.js from the CSVs
```

Then open `index.html` in a browser, or push the folder to GitHub Pages. There is no build step.

Files: `prep.py`, `index.html`, `data.js`, and the source CSVs.

## Design decisions (grounded in course material)

- Six panels, six different chart shapes — no two views share a silhouette, so each shape signals
  its own kind of question (ranking, concentration, part-to-whole, time, rhythm, distribution).
- Small multiples with consistent scales for fair side-by-side comparison.
- A mirrored area (not a streamgraph) so monthly values remain readable.
- One color scheme for the page; two fixed, colorblind-safe owner colors (blue for Or, orange for
  Roman) that carry meaning; single-hue lightness steps inside a single-person chart; muted gray
  for inactive marks.
- Absolute, natural units by default ("1,202 hours", "37,643 plays"); percentages only where volume
  would mislead (the overlap strip).
- Importance-driven layout (hero top-left, KPI anchors on top), instructions next to every
  interactive area, and a five-second readability test for each panel.
- Dark "music-history" theme; three deliberate type roles (display / body / monospace numbers);
  motion limited to a gentle scroll reveal that respects `prefers-reduced-motion`.

## Honest limits (also in the page's "About the data" note)

- **Different date ranges.** Apple data starts 2018-09, Spotify 2019-09. The page uses **2021+**
  because pre-2021 months are thin and uneven for Roman, which would make the baseline unfair.
- **Partial genre.** Families come from external tags and a conservative manual extension; the
  residual "Other" is shown, never hidden.
- **Skips are not compared.** Apple and Spotify count skips differently; if skip behavior is ever
  added, it must use the comparable `under_30s` measure, never the native counters.
- **Location.** City-level location exists only for Or, so no map is shown.

## Headline finding (recomputed in-app on 2021+)

Taste barely overlaps, and only in one direction: a third or more of Or's minutes fall on artists
Roman also plays, but roughly 1–2% of Roman's flow back. Then university happened — Roman's months
roughly doubled (≈36 → ≈72 hours of music per month) and his day shifted later (peak hour 16:00 →
22:00), while Or eased down. The interesting similarity is not *what* they listen to, but *how*
music sits inside each of their days — which is exactly what Dashboard 2 shows.

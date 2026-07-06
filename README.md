# Two Listeners, One Question

An interactive D3.js visualization comparing two people's complete personal listening histories —
**אור (Or)**, an Apple Music listener, and **רומן (Roman)**, a Spotify listener. Built for a
University of Haifa Data Visualization course.

The guiding question: *does similarity between two listeners have to live in musical taste, or can it
live in listening patterns, routine, and intensity instead?*

## The pivot behind the design

Taste overlap between the two is tiny and, more interestingly, **asymmetric**: a large share of Or's
listening time is on artists Roman has also touched, while almost none of Roman's time is on shared
artists (Roman explores a very wide tail that brushes past Or's mainstream pop, but Roman's metal core
is absent from Or's world). So the project does not try to find common taste. Instead:

- **Dashboard 1** treats taste as a *contrast* — two different musical worlds — and shows the asymmetric overlap honestly.
- **Dashboard 2** looks for the deeper kind of similarity: routine and intensity, and how both changed when university began.

## The two dashboards

Each visualization answers a question, reveals a pattern, and documents its data mappings and interactions.

### Dashboard 1 — "Listening DNA"
*What defines each listener musically, and how concentrated is that identity?*

- **Genre composition** — two side-by-side horizontal bar charts (small multiples). Axes: x = % of that
  owner's minutes, y = genre; color = the owner's single hue in lightness steps. Reveals that the two
  worlds barely touch. Interaction: click a genre to highlight it in both charts and filter the artist
  chart to that genre; tooltip for minutes and the top artist in the genre.
- **Top-artist dominance + concentration** — top-10 artists per owner as horizontal bars, plus a small
  "top-10 cover X%" figure. Reveals Roman's single dominant artist over a huge tail versus Or's flatter
  spread. Interaction: click an artist to see its detail and highlight it across charts; hover dims the rest.
- **Shared vs unique (minutes-weighted)** — two bars showing "% of my listening on shared artists" per
  owner, plus the top shared artists by name. Deliberately not a Venn (a count-based Venn would mislead).
  Interaction: click a shared artist to highlight it for both people.

### Dashboard 2 — "Before Uni vs Uni: Music as Routine"
*What changed when university began, and did both listeners change the same way?*

- **Monthly listening intensity** — a mirrored area chart (Or above a baseline, Roman below), hours per
  month, with a marker at 2024-01. Not a streamgraph, so values stay readable.
- **Routine heatmap (hour × weekday)** — small multiples: two maps per owner (pre-uni / university).
  Axes: x = weekday, y = hour, color = intensity in the owner's hue. Interaction: click a cell to see who
  listens more in that window and its top genres/artists; hover a weekday to highlight its column; toggle
  absolute vs normalized.
- **Change in a key metric** — a slope chart of average monthly hours (and under_30s%) from pre-uni to
  university per owner, with an optional centered-zero divergence view for these scalar metrics.

Two global controls apply across both dashboards: a **period** selector (Pre-uni / University / Difference)
and a **metric** toggle (absolute hours vs normalized share). Absolute answers "who listened more";
normalized answers "what role this artist/genre/time-window plays inside each person's own listening" —
which matters because Roman has higher total volume.

## Data and pipeline

Both histories are built only from the official export files: Or's Apple Music privacy export and Roman's
Spotify *Extended Streaming History*. Timestamps are converted to local time (Asia/Jerusalem) so the two
line up, and artist names are normalized (duplicates merged). The core event table `fact_plays` has
180,003 rows — one per play, including short plays and skips — which is the true apples-to-apples layer.
**Genre is an external add-on**: it is not in either export, so it was added by classifying each artist
externally and is partial (the long tail is bucketed as "Other").

`prep.py` filters everything to 2021+, assigns the two periods, and rebuilds the aggregates the dashboards
need into a single embedded `data.js`. The ~180k-row event table is used only during prep and is never
shipped to the browser.

## Running it

```
python prep.py        # writes data.js from the CSVs
```

Then open `index.html` in a browser, or push the folder to GitHub Pages. There is no build step.

Files: `prep.py`, `index.html`, `data.js`, and the source CSVs.

## Design decisions (grounded in course material)

- Bars over pie charts for rankings (clearer part-to-whole and comparison).
- Small multiples with consistent scales for fair side-by-side comparison.
- A mirrored area chart (not a streamgraph) so monthly values remain readable.
- One color scheme per dashboard; two fixed, colorblind-safe owner colors (blue for Or, orange for Roman);
  single-hue lightness steps inside a single-person chart.
- Raw numbers when magnitude is the point; normalized percentages when comparing structure.
- A dark "music-history" theme with strong, clear colors and a five-second readability test for each panel.

## Honest limits

- **Different date ranges.** Apple data starts 2018-09, Spotify 2019-09. The visualization uses **2021+**
  because the pre-2021 months are thin and uneven for Roman, which would make the pre-uni baseline unfair.
- **Partial genre.** Genre is external and provisional; the long tail is shown as "Other"
  (roughly a quarter to a third of each person's minutes) rather than hidden.
- **Skips.** Compared only via `under_30s` (identical for both services), never the native skip counters.
- **Location.** City-level location exists only for Or, so no map is shown.
- **Volume gap.** Roman has higher total listening volume, so absolute comparisons can exaggerate the gap —
  the normalized mode is always available.

## Headline finding (framing, recomputed in-app on 2021+)

Taste barely overlaps and does so asymmetrically: a majority of Or's minutes fall on artists Roman has
also played, but only a small fraction of Roman's minutes do. Roman is an intense, evening/night listener
anchored by one dominant artist over a very wide tail; Or is a steadier, more spread-out listener. The
interesting comparison is therefore not *what* they listen to, but *how* music sits in each of their days —
which is what Dashboard 2 examines around the start of university.

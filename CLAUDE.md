# CLAUDE.md — "Two Listeners" music visualization

Persistent guidance for this repo. Read before every task.

## What this project is
A static D3.js website for a University of Haifa Data Visualization course. It compares two people's
complete personal listening histories: **Orr** — Apple Music — and **Roman** — Spotify.
Central question: is similarity between two listeners only about taste, or also about routine and intensity?

One scrolling page (no tabs), two stacked dashboards (hero → panel grid; the KPI strips were removed —
their numbers live in the written report, the page keeps only visualizations), in ONE personal,
story-driven voice ("Wrapped for two people") — measures serve the story. On-page the two dashboards are
labeled **Side A / Side B** (a vinyl-record framing, not "Dashboard 1/2" — that read as generic BI-tool
naming and was flagged as making the whole page feel "web-ie"), with a "flip the record" divider between
them, and every panel carries a small catalog-style track number (A1–A3, B1–B4) instead of just a title.
Keep this — don't revert to "Dashboard 1: ..." headings.
1. **Listening DNA** — genre families, obsessions (top artists), minutes-weighted overlap.
2. **Routine, Disrupted — Before Uni vs. University** — whole-span waveform timeline (equalizer-bar
   style), daily-rhythm heatmap, cumulative artist-discovery curve, slopegraph.
Seven panels, seven DISTINCT chart shapes: mirrored BUTTERFLY family bars (one shared axis, Orr left /
Roman right — replaced the old side-by-side paired bars 2026-07-16; the mirror echoes B1's waveform and
is the page's signature motif) / lollipop dot-plot / 100% strip + LOG-SCALE DUMBBELL of shared artists
(one line per artist from Orr's minutes to Roman's minutes — replaced the old top-10 shared TABLE; the
285h-vs-15min asymmetry is the project's headline and deserves a chart, not a table row) / mirrored
equalizer-bar waveform / heatmap / cumulative discovery curve / slopegraph small-multiples
(Pre-uni → University change). Panel titles are human questions. No takeaway lines (considered and
explicitly declined by the owner) — but date-anchored EVENT ANNOTATIONS on the charts are IN
(owner-approved 2026-07-16, distinct from takeaways: marks on data points, not conclusion sentences):
B1 carries the Oct-2023 routine-break line (neutral-factual wording — "both routines break, 3 months
before uni"; the owner chose NOT to name the war explicitly), Roman's record month (value computed,
but the ~61× ratio is quoted from the locked facts, NOT recomputed — the shipped 0.1-rounded monthlies
inflate it to 62×), and Or's quietest month with its rebound; B3 marks Or's only 2+-month zero-discovery
run (derived from the data, not hardcoded dates). A1 shows GHOST TICKS (bullet-chart idiom) when one
period is selected: a thin mark at the other period's share per bar, so taste drift is visible without
toggling back and forth. Rationale: the audit found the page showed patterns but hid its discoveries —
the verified findings existed only in narrative text.

**Side-A filters (owner-driven 2026-07-16 upgrade — the old single-click filter was judged "low
level"):** the genre-family filter is a MULTI-SELECT union (click families to accumulate, one removable
chip each; A2 shows the merged top-10 across selected families). A3 carries the "what counts as
shared?" SLIDER (1–60 min, default = SHARED_MIN_MINUTES): it recomputes the shared set CLIENT-SIDE from
`shared.overlap_artists` (every name-matched artist with both-side minutes + real-play flags, per cut)
and drives the strips, the shared count, the dumbbell, and A2's shared rings together. At the default
threshold the client formula MUST reproduce prep's count/pct exactly — verify_dashboard.py asserts
this per cut; don't change either side's rule without the other. A non-default threshold shows a
removable "Shared rule" chip. The locked 35.4%-vs-0.5% narrative numbers always refer to the DEFAULT
threshold. EVERY panel responds to the global period filter; whole-span charts
(river, discovery curve) and the slopegraph respond by EMPHASIZING the selected period's region/side,
not by re-cutting.

**Why D2 is framed as "routine, disrupted" and not just "routine":** the discovery curve (artist
novelty over time) doesn't visually read as "routine" or "intensity" on its own — it reads as a taste/
exploration measure, and got flagged twice as feeling out of place under a bare "routine" label. The fix
was to make the whole dashboard explicit about WHY discovery belongs there: Kim et al. (PNAS 2024,
"Disrupted routines anticipate musical exploration") found that breaking a personal routine is
systematically associated with MORE musical exploration, not nostalgic retreat. D2's four panels now
explicitly frame the Pre-uni → University line as a routine-disruption event and ask whether each
listener's exploration rate visibly shifted around it — that's what gives the discovery curve a
legitimate home instead of a forced one. Do not revert to a generic "routine and intensity" label
without re-solving this fit problem.

**The Dashboard-2 range brush (drag-to-select under the waveform) is a deliberate, narrow exception to
"whole-span charts never re-cut":** dragging it genuinely recomputes the weekday/hour heatmap and a
four-metric readout (the same four metrics the slopegraph shows — see below) for the EXACT dragged month
range, via the `monthly_detail` aggregate (see Data files below) — not just an emphasis overlay. It sits
ALONGSIDE the fixed All/Pre-uni/University toggle, not in place of it (the toggle still drives
everything else, and still matters for the locked two-period comparison the slopegraph depends on). The
waveform and discovery curve themselves still only get emphasized/echoed by the brush, never re-cut —
only the heatmap and the brush's own readout genuinely recompute. This distinction (which panels re-cut
vs. which only emphasize) is intentional, not inconsistent — don't "fix" it by making everything re-cut
or everything emphasize without re-checking this note.

**The slopegraph is four metrics, not six:** hours/month, median listening day, days-with-music%, and
plays-kept-past-30s. "Top-10 artist share" and "different artists" USED to be there too but were cut —
both are taste/breadth measures, not routine or intensity, and both duplicated content shown elsewhere
(top-10 share is the headline of Dashboard 1's Top Artist Concentration panel; "different artists"
duplicates this dashboard's own discovery curve, just as a single before/after snapshot instead of a
trajectory). Don't re-add them without re-solving that duplication.

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
- **Terminal identity (2026-07-16 pass, owner-driven):** the page's design system is a blue-tinted
  night terminal, modeled on the owner's own `~/Downloads/dashboard(1).html`. Chrome palette: bg
  `#0f1117`, panel `#151926`, border `#232a3a`, ink `#c8d0e0`. IBM Plex Mono is the BODY typeface
  (13px), Space Grotesk only for the hero h1/question and side h2s. Panels are FLAT (1px border, 8px
  radius, no gradients/shadows — an earlier gradient-card look was tried and rejected as "web-ie").
  Panel titles are one-line small-caps mono rows: `▍` accent + colored track number + name, with a
  terse right-aligned functional sub-label INSTEAD of hint paragraphs (hints only survive where a
  correctness explanation genuinely needs a sentence, e.g. the per-listener heatmap scale). A mono
  prompt line (`orr@apple-music × roman@spotify ~/two-listeners · jan 2021 → may 2026`) sits above the
  hero title. A `method` footer (mono, muted) closes the page: provenance, genre-external caveat,
  shared rule, 30-second skip rule, tooling — it carries the required genre disclosure, don't remove it.
- The legend is a CONTROL: clicking a listener chip solos him (state.solo; the other listener's marks
  drop to 0.15 opacity in every panel via soloOp(), chip gets `.off`); clicking again un-solos.
- In a single-person chart with categories, use only LIGHTNESS steps of that person's single hue —
  never a second categorical palette. Muted gray for inactive marks.
- Heatmap cells ramp from a visible floor (`--floor: #232b3d`), not the page background, with a subtle
  grid so empty cells read as empty rather than invisible.
- State is kept PER DASHBOARD (independent stacked sections) plus the global period and solo:
  `{ period, solo, d1: {selectedFamilies[], selectedArtist, selectedArtistSource, sharedMin},
  d2: {selectedWindow} }` — every active filter surfaces as a removable chip.
- Whole-span charts (Dashboard 2 timeline, discovery curve) always draw the full span; the period
  filter dims the non-selected period band and outlines the selected one (emphasis, not re-cutting).

## Data files (English names)
- `fact_plays_with_genre.csv` — event-level (~180,003 rows). Prep only; never shipped to the browser.
- `fact_plays_SAMPLE.csv` — a 300-row schema sample. NOT the real data; do not compute from it.
- Aggregates (full-history, re-cut to 2021+ in prep): `owner_summary`, `artist_totals(_with_genre)`,
  `monthly_totals`, `daily_totals`, `hour_weekday(_year)`, `hourly_profile`, `genre_monthly`,
  `plays_daily(_with_genre)`.
- `EMBEDDED_DATA.monthly_detail` (in `data.js`, built by `prep.py`'s `monthly_detail()`) — per-owner,
  per-month breakdown (hours/plays/under-30-plays/active-days, sparse weekday×hour play counts, and a
  dated active-day series). Still a compact aggregate, NOT the event table — bounded by (weekday, hour,
  month) triples that actually occurred. Exists solely to let the Dashboard-2 range brush recompute the
  heatmap and the four slopegraph-equivalent metrics for an arbitrary custom month range client-side.
  Deliberately has NO per-artist breakdown — that would only feed top-10-share/unique-artist recomputes,
  and those metrics were cut from the slopegraph as taste/breadth duplicates (see above), so there was
  nothing left to justify shipping it. Replaced the old unused `daily` field (bare per-cut value arrays
  with no date labels, never referenced in `index.html` — dead code, not a data loss).

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

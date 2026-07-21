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
1. **Taste Profile and Shared Listening** — genre families, obsessions (top artists), minutes-weighted
   overlap. (This title supersedes the earlier "Listening DNA" 2026-07-20 — the shipped h2 was kept and
   the spec updated to match; do not rename the Side A heading back.)
2. **Routine, Disrupted — Before Uni vs. University** — whole-span waveform timeline (equalizer-bar
   style), daily-rhythm heatmap, cumulative artist-discovery curve, slopegraph.
Seven panels, seven DISTINCT chart shapes: mirrored BUTTERFLY family bars (one shared axis, Orr left /
Roman right — replaced the old side-by-side paired bars 2026-07-16; the mirror echoes B1's waveform and
is the page's signature motif) / lollipop dot-plot / 100% strip + LOG-SCALE DUMBBELL of shared artists
(one line per artist from Orr's minutes to Roman's minutes — replaced the old top-10 shared TABLE; the
285h-vs-15min asymmetry is the project's headline and deserves a chart, not a table row) / mirrored
equalizer-bar waveform / heatmap / cumulative discovery curve / slopegraph small-multiples
(Pre-uni → University change). Panel titles are human questions. No takeaway lines (considered and
explicitly declined by the owner). **NO TEXT ON CHARTS beyond axes/values/owner labels:** labeled
event annotations were built and then REMOVED the same day (2026-07-16) — the course lecturer treats
on-chart narration as chart junk; his philosophy is "the viz displays the data, the reader concludes."
Do not re-add annotation labels. What survived, and why it's allowed:
- B1's 2023-10 dotted guide (`BREAK_YM`) was REMOVED 2026-07-20 on the owner's instruction — only the
  university guide remains drawn. `BREAK_YM` itself survives in the JS because the 2023-10 hover
  tooltip still keys off it: the verified October facts (Roman 31.5→73.6 h/month; night share
  17–20%→39–53%; Orr 0 min on Oct 7, zero discoveries Oct–Nov) surface ONLY in that tooltip
  (`BREAK_FACTS` — wording quotes the locked facts exactly; the ~61× record ratio must never be
  recomputed from the shipped 0.1-rounded monthlies, which inflate it to 62×). Do not redraw the line.
- A1's GHOST TICKS (thin on-bar marks at the other period's share, with a "▏= …" key) were REMOVED
  2026-07-20 on the owner's instruction ("we don't like them"). The cross-period drift values still
  surface in the family hover tooltip ("(Pre-uni: X%)" per listener) — that is now the only place the
  other period's share appears. Do not redraw the marks or the key.
Findings are made discoverable through interaction (brush, hover, slider), never through
on-chart sentences.

**Side-A filters (owner-driven 2026-07-16 upgrade — the old single-click filter was judged "low
level"):** the genre-family filter is a MULTI-SELECT union (click families to accumulate, one removable
chip each; A2 shows the merged top-10 across selected families). A3 carries the "what counts as
shared?" SLIDER (1–60 min, default = SHARED_MIN_MINUTES): it recomputes the shared set CLIENT-SIDE from
`shared.overlap_artists` (every name-matched artist with both-side minutes + real-play flags, per cut)
and drives the strips, the shared count, the dumbbell, and A2's shared rings together. At the default
threshold the client formula MUST reproduce prep's count/pct exactly — verify_dashboard.py asserts
this per cut; don't change either side's rule without the other. A non-default threshold shows a
removable "Shared rule" chip. The locked 35.2%-vs-0.5% narrative numbers always refer to the DEFAULT
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

**The Dashboard-2 range brush (drag-to-select ON the B1 waveform itself) is a deliberate, narrow
exception to "whole-span charts never re-cut":** since 2026-07-20 the brush surface IS the river — the
separate strip that used to sit under the waveform was removed on the owner's instruction. Dragging
horizontally across the river (either direction) selects that month range; a bare click selects a
single month; the selection shows as a dashed outline on the river with the unselected months dimmed.
Hover and drag coexist: the synced month tooltip shows only while no drag is in progress, and goes
quiet from mousedown to release. Dragging genuinely recomputes the weekday/hour heatmap and a
four-metric readout (the same four metrics the slopegraph shows — see below) for the EXACT dragged month
range, via the `monthly_detail` aggregate (see Data files below) — not just an emphasis overlay. It sits
ALONGSIDE the fixed All/Pre-uni/University toggle, not in place of it (the toggle still drives
everything else, and still matters for the locked two-period comparison the slopegraph depends on).
Changing the period CLEARS an active range (and its chip) — changed 2026-07-20; a range used to survive
the toggle, but that masked the period toggle's effect on the heatmap, which made the toggle look
broken on that panel. The waveform and discovery curve themselves still only get emphasized/echoed by
the brush, never re-cut — only the heatmap and the brush's own readout genuinely recompute. This
distinction (which panels re-cut vs. which only emphasize) is intentional, not inconsistent — don't
"fix" it by making everything re-cut or everything emphasize without re-checking this note.

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
- Data window: **2021-01 .. 2026-04** (earlier data dropped; pre-2021 is thin/uneven for Roman.
  2026-05 was dropped WHOLE 2026-07-20 on the owner's instruction — it is a partial month, the
  exports stop 2026-05-22 for Or and 2026-05-10 for Roman — so the last plotted month is never an
  artificially quiet one; `WINDOW_END_EXCL = "2026-05-01"` in both `prep.py` and
  `verify_dashboard.py`).
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
  not name-only matches. Overlap is weighted by minutes, never artist count (39 shared artists, but
  35.2% of Or's minutes vs 0.5% of Roman's — updated when 2026-05 was dropped from the window).
- Skip behavior appears in the UI only as the comparable `under_30s` measure (shown as "plays kept past
  30 s" = 100 − under30_pct, in the B1 range-brush readout and the slopegraph) — never native skip counters (Apple and Spotify
  count skips differently).
- Heatmaps use a PER-LISTENER color scale (own max across periods): the panel compares routine shape,
  and one absolute scale would let Roman's volume wash out Orr's pattern.
- Absolute, natural units by default; percentages only where Roman's higher volume would mislead: the
  overlap strips, A1's family shares, and the two rate metrics in the slopegraph and
  brush readout. No global absolute/normalized toggle.
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
  terse right-aligned functional sub-label INSTEAD of hint paragraphs (hints survive where a
  correctness explanation genuinely needs a sentence AND for interaction instructions or reading
  guidance — rule widened 2026-07-20 to sanction what ships. Exactly four hints ship and must not be
  deleted, trimmed, or relocated: A3's slider rule-note ("drag to test how sensitive…"), B1's
  range-scrub drag hint, B2's per-listener heatmap-scale explanation, and B3's how-to-read-the-bend
  guidance). A mono
  prompt line (`orr@apple-music × roman@spotify ~/two-listeners · jan 2021 → apr 2026`) sits above the
  hero title. A `method` footer (mono, muted) closes the page: provenance, genre-external caveat,
  shared rule, 30-second skip rule, tooling — it carries the required genre disclosure, don't remove it.
- The legend is a CONTROL: clicking a listener chip solos him (state.solo; the other listener's marks
  drop to 0.15 opacity in every panel via soloOp(), chip gets `.off`); clicking again un-solos.
- In a single-person chart with categories, use only LIGHTNESS steps of that person's single hue —
  never a second categorical palette. Muted gray for inactive marks.
- Heatmap cells ramp from a visible floor (`--floor: #242634`), not the page background, with a subtle
  grid so empty cells read as empty rather than invisible.
- State is kept PER DASHBOARD (independent stacked sections) plus the global period and solo:
  `{ period, solo, d1: {selectedFamilies[], selectedArtist, selectedArtistSource, sharedMin},
  d2: {selectedWindow} }` — every active filter surfaces as a removable chip.
- Whole-span charts (Dashboard 2 timeline, discovery curve) always draw the full span; the period
  filter dims the non-selected period band and outlines the selected one (emphasis, not re-cutting).

## Data files (English names)
- `fact_plays_with_genre.csv` — event-level (~180,003 rows). Prep only; never shipped to the browser.
- Aggregates in `EMBEDDED_DATA` (all built by `prep.py` on the 2021+ window, all read by the browser):
  `meta`, `kpis`, `families`, `top_artists`, `family_artists`, `shared`, `monthly`, `heatmap`,
  `monthly_detail`, `discovery`, `routine_window`, `change`.
- `EMBEDDED_DATA.monthly_detail` (in `data.js`, built by `prep.py`'s `monthly_detail()`) — per-owner,
  per-month breakdown (hours/plays/under-30-plays/active-days, sparse weekday×hour play counts, and a
  dated active-day series). Still a compact aggregate, NOT the event table — bounded by (weekday, hour,
  month) triples that actually occurred. Exists solely to let the Dashboard-2 range brush recompute the
  heatmap and the four slopegraph-equivalent metrics for an arbitrary custom month range client-side.
  Currently has NO per-artist breakdown — originally left out because it would only have fed
  top-10-share/unique-artist recomputes, which were cut from the slopegraph as taste/breadth duplicates
  (see above). Replaced the old unused `daily` field (bare per-cut value arrays with no date labels,
  never referenced in `index.html` — dead code, not a data loss).

## PENDING TASK (owner decision 2026-07-21 — do this next)
The B2 cell drill-down is plays-only when a custom B1 range is selected (it shows a caveat sentence
instead of artist/family lists), because `monthly_detail` ships no per-artist data. The owner wants
real "what plays here" details for custom ranges. Plan, sized against the shipped data (8,341
occupied (weekday, hour, month) cells across both owners, ~16 plays each — full per-artist fidelity
would be a disguised event table and stays banned):
1. Extend `prep.py`'s `monthly_detail()` with, per occupied (weekday, hour, month) cell: top ~3
   artists by minutes (name-indexed against a shared string table) + COMPLETE per-family minutes
   (families are only ~7, so family breakdowns stay exact for any range). Expected data.js growth
   ~+0.3–0.5 MB.
2. Update the range branch of `renderWindowPanel()` in `index.html` to render those lists (rank
   merged artists by summed minutes across the range's months; label the artist list "top artists
   of each month" — truncated months make artist minutes a lower bound, so never present the artist
   list as complete; the family list IS complete and can show exact minutes). Remove the
   "breakdowns exist only for the fixed cuts" caveat sentence.
3. Update `verify_dashboard.py` to assert the new field against the CSV, re-run prep + the full
   suite, and re-commit the regenerated `data.js` (Part A byte-identity must pass again).
BLOCKED ON: `DATA/fact_plays_with_genre.csv` (~110 MB, gitignored) — it lives on the owner's LINUX
partition; this task must run from there (or after copying DATA/ back into the repo root).
Until then, do NOT ship JS that reads the new field — data.js does not have it yet.

## Sanity anchors (FULL history — recompute on 2021+, do NOT hardcode)
Expect the 2021+ numbers to differ; these are only rough checks.
- Or ≈ 2,802 h / 97,000 plays / 1,436 artists / top artist Imagine Dragons.
- Roman ≈ 3,491 h / 83,003 plays / 4,036 artists / top artist Sleep Token.
- Window (2021-01..2026-04) computed: Or 1,928.5 h / 1,107 artists; Roman 3,367.2 h / 3,703 artists;
  39 truly-shared artists (129 name-only matches); shared minutes 35.2% (Or) vs 0.5% (Roman); family
  "Other" 8.0% (Or) / 14.1% (Roman) after curation.

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
- Periods differ in length (36 vs 28 months; 1,095 vs 851 days in `meta.period_days`, after the
  2026-05 drop) — compare rates/averages.
- Hebrew names next to signed/parenthesized numbers get bidi-scrambled; put an LRM (`&lrm;` / `‎`)
  after the Hebrew run.
- Genre coverage differs per person; do not overclaim genre precision.

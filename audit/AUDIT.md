# Pre-submission audit — "Two Listeners" (2026-07-19)

Read-only audit of the repo at commit `17af0ed` (working tree has uncommitted CLAUDE.md
edits only). Every number below was independently recomputed from
`DATA/fact_plays_with_genre.csv` with fresh pandas code, and every interaction was
exercised live in a browser against `index.html` served over HTTP, with DOM assertions.

## A. Summary

**The data and the page are solid; the written documents are not.** All 71 independent
recomputations of CLAUDE.md's anchor numbers, the data.js aggregates, and the cross-sums
(per-period vs. all-span, monthly vs. KPIs, heatmap vs. plays, discovery vs. unique
artists) reproduce exactly from the source CSV. Every documented interaction — global
period toggle, multi-select family filter, shared-threshold slider, range brush, legend
solo, chips, tooltips, all reset paths, the empty-result case, and the deliberate
re-cut-vs-emphasize distinction — fires correctly and leaves no broken state. The page
loads with zero console errors or warnings. The client-side shared-artist formula
reproduces prep's counts and percentages exactly in all three cuts, and the brush
readout for an arbitrary 9-month range matched a from-scratch CSV recompute to the digit.

What is broken is the paperwork: **README.md describes a previous iteration of the site**
(six panels including a histogram that no longer exists, wrong shared-artist and genre
numbers), and **REPORT.md, while numerically current, still describes the pre-rebuild
chart shapes** — most damningly, it claims a free date-range brush was *considered and
rejected*, while the shipped site has exactly that brush as a headline feature. The three
previously reported code-side issues (Side A title, `--floor` variable, surviving hint
paragraphs) are all still present.

## B. Findings

| ID | Severity | Area | Evidence | What is wrong | Why it matters |
|----|----------|------|----------|---------------|----------------|
| F1 | Minor | docs (previously reported) | index.html:785 vs CLAUDE.md:17 | Side A h2 reads "Taste Profile and Shared Listening"; the locked spec title is "Listening DNA". README.md:26 uses the correct name; REPORT.md:40 uses the wrong one. | The most visible string on the page contradicts the locked spec. |
| F2 | Nitpick | encoding (previously reported) | index.html:32 (`--floor: #232b3d`), index.html:2281 (`d3.interpolateLab("#242634", …)`); `--floor` referenced nowhere else (grep) | The documented heatmap ramp floor variable is dead; the ramp hardcodes a slightly different color. | Doc/code drift; the intended single source of truth for the floor color does nothing. |
| F3 | Minor | docs (previously reported) | index.html:815 (A3 rule-note), :854–857 (B1 scrub hint), :877–880 (B3 hint) | Three hint paragraphs survive beyond CLAUDE.md's rule that hints exist only for genuine correctness explanations (the sanctioned one is B2's per-listener-scale hint at :866–869). B3's is interpretive narration; A3's and B1's are usage instructions. | Violates the owner's own locked style rule and the lecturer's no-narration stance that got on-chart labels removed. |
| F4 | Major | docs | README.md:21 (KPI strip), :24 ("six panels"), :27 (paired bars), :39 (mirrored area), :41–42 (hero "ignores the period filter"), :47–49 (daily-minutes histogram panel — no longer exists), :51 (per-dashboard period filters — there is one global), :64 (Other residual "15%/23%" — actual 8.0%/14.2%), :67–68 ("130 → 79 artists" — actual 130 → 40), :113 ("1–2% of Roman's" — actual 0.5%) | README describes a design at least two iterations old, with several flatly wrong numbers. | Anyone grading or reading the repo top-down is told the site contains panels it doesn't have and numbers the data contradicts. |
| F5 | Major | docs | REPORT.md:99 (free date-range brush "rejected" — the site ships one), :121 (shape list: "paired bar charts … mirrored-area timeline"; no butterfly, no dumbbell, no equalizer waveform), :176 ("paired bar charts"), :206 (A3 top-10 shared **table** — replaced by the dumbbell per CLAUDE.md:22–24, and no threshold slider mentioned), :212 ("mirrored-area timeline") | The report's numbers are current (35.4%/0.5%, 40/130, per-cut values all check out) but its structural description predates the 2026-07-16 Side A rebuild and brush addition. The brush passage actively denies a shipped feature. | The submitted report contradicts the submitted artifact — the course requires documented mappings and interactions, and the report documents the wrong ones. |
| F6 | Minor | docs | index.html:851 sub "hours per month · Orr above the line…" documents B1's mapping but not its hover crosshair/tooltip; B3 sub (:876) documents no interaction (it has the synced hover); B4 sub (:886) documents no interaction (it has hover tooltips with deltas) | Course rule: every visualization documents its interactions. Click interactions are documented everywhere; hover/tooltip is undocumented on B1/B3/B4 (A1's hover is likewise undocumented but its sub already documents click-to-filter). | A grader checking the "documents its interactions" rule panel-by-panel finds three gaps. |
| F7 | Minor | docs | Page footer (index.html:892–901) states the jan-2021 cut but not why (Roman's sparse pre-2021 data — REPORT.md:79 has it); unequal period lengths (36 vs 29 months) are stated only in REPORT.md:80/:324, nowhere on the page. Mitigation exists: every cross-period metric on the page is a rate (hours/month, days-with-music %, medians). | Two of the four required honesty disclosures live only in the report, not on the page. Genre-external and shared-rule disclosures are properly on the page (A1 sub, slider label, window panel "(external tags)", footer). | The page is where the charts are; the audit brief requires limitations stated where they affect a chart. |
| F8 | Minor | encoding | index.html:1264–1269: in a period cut, the A1 tooltip appends ` (University: X%)` directly after the family's top artist; `families.university.Roman.Israeli.top_artist` is Hebrew (`סטילה`). Same pattern: B2 drill-down lists 239 Hebrew artist entries followed by bold minute values (index.html:2397). No LRM (`&lrm;`) anywhere in index.html (grep). | CLAUDE.md:184's bidi gotcha (Hebrew run + parenthesized/adjacent number scrambles) is unhandled at the exact spots it predicts. | Hebrew-named artists render with visually scrambled numbers for RTL-adjacent text. |
| F9 | Nitpick | data | data.js fields never read by index.html: `kpis.*.{plays, unique_artists, top_artist, top_artist_share, peak_hour}`, `shared.{count, count_by_cut, pct_minutes, top_shared}`, `meta.{owners, months_per_period}`, the baked `shared` booleans on `top_artists`/`family_artists` rows (the A2 ring recomputes live from the slider). All except `shared.top_shared` are consumed by verify_dashboard.py's assertions; `top_shared` (3×≤15 rows) is read by nothing. | Shipped-but-unused payload; the baked `shared` flags could silently diverge from the live-threshold rings if ever used. | Dead weight is small; the trap is future misuse of the stale flags. |
| F10 | Nitpick | data | index.html:915 hardcodes `OWNERS = ["Or", "Roman"]` duplicating `meta.owners`; footer hardcodes "138,894 plays" (verified correct against the CSV; also asserted by verify_dashboard.py:68); heatmap ramp floor hardcoded (see F2). `BREAK_YM`/`BREAK_FACTS` hardcodes are sanctioned by CLAUDE.md:31–35 and their wording matches the locked facts exactly, including avoiding the forbidden 62× recompute. | Duplicated constants instead of reading from data. | Drift risk only; all current values verified correct. |
| F11 | Nitpick | encoding | index.html:1219: A1 bar fill `ownerShade(o, fams.indexOf(d), fams.length)` — lightness darkens with row rank | Lightness varies down the butterfly's rows but encodes nothing (rank is already position). CLAUDE.md reserves lightness steps for categories in single-listener charts. | A careful reader may hunt for a meaning that isn't there; hue-per-listener is still correct, so it's cosmetic. |
| F12 | Nitpick | encoding | index.html:800 A2 sub says "hours in range"; values under 60 min render as "N min" (fmin, index.html:936–937). Brush readout renders 62.3 min as "1 h" (fm1t trims 1.0) | Mixed h/min display under an "hours" label; sub-hour precision loss at the h boundary. | Marginal; the adaptive unit rule is itself documented in REPORT.md:109. |
| F13 | Nitpick | data | `shared.name_matches` = 130 but `overlap_artists.all` ships 129 rows; the missing artist is Jonas Blue (Or 3.24 min, Roman 0.0 min — excluded by the `>0` both-sides rule, prep.py:325). Code comment index.html:1420 says "~130". The on-page "130 name-only matches" line is correct per its own definition, and Jonas Blue can never clear any threshold ≥ 1 min, so no slider position is affected. | One name-matched artist can't appear in the A3 client-side set. | Zero user-visible effect; documented here so nobody "fixes" the 130 later. |
| F14 | Nitpick | performance | data.js = 535 KB decoded (547 KB on disk; `monthly_detail` + `routine_window` dominate); d3 = 273 KB; DOMContentLoaded 479 ms, load 496 ms, zero failed requests, zero console messages. Fonts load from fonts.googleapis.com (external). | data.js exceeds the "few hundred KB" comfort line uncompressed; GitHub Pages serves it gzipped (JSON of this shape compresses ~5–8×), so wire size is fine. Fonts require network. | Informational; no action strictly needed. |

Course-rule compliance check (for completeness): two dashboards ✓; every panel has a
question title ✓; mappings documented per panel ✓ (subs + in-chart keys; gaps only on
interactions, F6); the two colorblind-safe owner colors are the only categorical hues in
every comparison chart ✓ (`#4EA1FF`/`#FF9F1C` via one `COLOR` map); single-listener
charts use only lightness of that hue ✓ (heatmap ramp, A2 — the other-owner ring is the
owner encoding, not a second palette); skip behavior appears only as the under-30s
"plays kept past 30 s" measure ✓ (grep: no native skip counter anywhere).

Interaction evidence (all driven live, DOM-asserted): period toggle re-cuts A1/A2/A3/B2
and emphasizes B1/B3/B4 exactly as documented (ghost ticks + "▏= University share" key
appear only in a period cut); family multi-select unions correctly with one removable
chip each ("their Pop + Israeli corner"); Metal-only filter produces Orr's empty-state
message; slider at 30 min → 4 shared artists, chip appears, A2 rings drop 5→2, chip
removal restores 3 min/40 artists; artist click ↔ detail card toggles (Imagine Dragons
285 h vs 15 min — the locked headline); solo dims the other listener to opacity 0.15
everywhere and un-solos; heatmap cell click ↔ drill-down + chip; brush: live readout
during drag, range chip, B2 re-cut to "2023-04 → 2023-12", drill-down locked out with an
explanatory notice, cell clicks ignored while active, range survives a period toggle
(documented priority), both reset paths (inline clear ×, chip) work, single-month click
and right-to-left drag work; readout metrics for 2023-04→2023-12 match a fresh CSV
recompute exactly (34.8/54.0 h/mo, 62.3/100.3 min medians, 95/89 %, 66.8/68.4 %).

## C. Unverified

- **Visual rendering.** Browser-pane screenshots timed out in this session (environment
  issue; the page itself was fully responsive to scripted interaction and logged no
  errors). Pixel-level checks — bidi scrambling in the two F8 spots, label overlaps,
  the reveal animation — need one manual eyeball pass or a working screenshot run.
- **verify_dashboard.py end-to-end.** Not run, deliberately: its Part A executes
  prep.py, which rewrites data.js in place — not read-only. My independent recompute
  covers the same ground (and more anchors), but the byte-identity guarantee
  (committed data.js == fresh prep run under this pandas version) is unverified today.
  Run it once before submitting, after any fix that touches prep.py or data.js.
- **GitHub Pages deployment.** Audited against a local HTTP serve only; Pages-specific
  behavior (gzip ratios, font loading in production) not checked.
- **Two_Listeners_Report.docx.** Not opened; if it was exported from REPORT.md before
  the F5 fixes, it inherits the same staleness.

## D. Proposed action plan (in order — awaiting approval; nothing has been changed)

Nothing on screen displays a wrong number, so document fixes that correct false claims
come first, then spec-compliance fixes, then hygiene.

1. **Rewrite README.md to describe the shipped site** — fixes F4. Files: README.md.
   Correct the panel inventory (7 panels: butterfly, lollipop, strips+dumbbell+slider,
   equalizer waveform+brush, heatmaps, discovery curve, slopegraph), the single global
   period filter, no KPI strips, and the numbers (40 shared, 8.0%/14.2% Other, 0.5%).
   Risk: none to code; keep the accurate "Honest limits" section.
2. **Update REPORT.md's structural sections** — fixes F5. Files: REPORT.md (§4
   rejected-alternatives brush passage → explain what changed and why the brush was
   ultimately added alongside the fixed toggle; §5.2.1/5.2.3/5.2.4 shape names and the
   :121 shape list; add the slider, dumbbell, ghost ticks). Risk: keep every verified
   number untouched; re-export the .docx afterwards if it derives from this file.
3. **Rename Side A to "Listening DNA"** — fixes F1. Files: index.html:785 (and the
   REPORT.md:40 mention, folded into fix 2). Risk: pure text; CLAUDE.md says the code,
   not the spec, is wrong.
4. **Trim the three off-spec hints** — fixes F3. Files: index.html:815, :854–857,
   :877–880. Fold the A3 rule-note and B1 scrub instruction into the panels' sub-labels
   (where instructions belong per CLAUDE.md:126–128); delete or relocate B3's
   interpretive paragraph into the report. Risk: owner may prefer keeping B1's
   drag affordance visible — decide per hint; B2's scale hint stays.
5. **Add LRM handling after Hebrew runs** — fixes F8. Files: index.html (A1 tooltip
   top-artist line, B2 window-panel artist list; a small `bidiSafe(name)` helper
   appending `‎` when the string contains Hebrew). Risk: cosmetic-only; test with
   the University cut → Israeli row tooltip (`סטילה`).
6. **Document the missing hover interactions in panel subs** — fixes F6, helps F7.
   Files: index.html:851, :876, :886 (append e.g. "· hover for month detail"). Optionally
   add one footer clause for the 36-vs-29-month rate rule and the sparse-pre-2021
   rationale — closes F7 on-page. Risk: sub-labels must stay terse per the design rule.
7. **Hygiene (optional, lowest value-to-risk):** point the heatmap ramp at
   `--floor` or delete the variable and fix CLAUDE.md's mention (F2); read `OWNERS`
   from `meta.owners` (F10); either drop `shared.top_shared` from prep.py or leave all
   dead fields as verify-suite surface and just note it (F9 — recommend leaving; several
   are asserted by verify_dashboard.py, and pruning risks breaking those asserts).
   F11/F12/F13/F14: recommend no action. Risk: any prep.py change requires re-running
   prep + verify_dashboard.py and re-committing data.js.

After any code fix: `py verify_dashboard.py` must pass (61+ checks), and re-run the
interaction battery on the changed panels.

---
*Method note: all evidence gathered read-only — schema dump of EMBEDDED_DATA via node;
71-check pandas recompute of every CLAUDE.md anchor and cross-sum against
DATA/fact_plays_with_genre.csv; live DOM-asserted interaction battery in a served
browser session; grep-verified lineage of every shipped field. Throwaway audit scripts
were deleted after this report was written, per the repo's no-scratch-files rule.*

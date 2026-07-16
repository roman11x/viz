# Two Listeners: Orr vs Roman

## Final Project Report, Data Visualization

**Live site:** https://roman11x.github.io/viz/
**Repository:** https://github.com/roman11x/viz

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [The Data](#2-the-data)
3. [Ideas and Planning](#3-ideas-and-planning)
4. [Solution and Design Decisions](#4-solution-and-design-decisions)
5. [Implementation](#5-implementation)
   1. [Data preprocessing](#51-data-preprocessing)
   2. [The visualizations](#52-the-visualizations)
   3. [Code, tools and libraries](#53-code-tools-and-libraries)
6. [Findings](#6-findings)
7. [Limitations](#7-limitations)
8. [Conclusion](#8-conclusion)

---

## 1. Introduction

Every year, Spotify and Apple Music send their users a "Wrapped" or "Replay" summary. It is fun, but it only tells you what you already know: which artists you love. We wanted to ask a deeper question about what a listening history says about a person.

The two of us are friends with completely different musical taste. Orr listens to pop and Israeli music on Apple Music. Roman listens to metal on Spotify. Out of more than one hundred shared artist names, almost none of them get real listening time from both of us. This made us curious, and it became our research question:

> **How do two people with almost non-overlapping musical taste use music in a similar or different way as part of their lives, routines and life periods?**
>
> In other words: does the similarity between listeners have to be in musical taste, or can it be found in listening patterns, routines and the intensity of the connection to music?

The dataset is our own complete listening histories, which we requested from our streaming providers. This gave us a rich event-level dataset (about 180,000 play events, 138,894 of them inside the analysis window) that covers more than five years of daily life, including a real life change that happened to both of us at the same time: we both started university in 2024. This natural "before and after" split is what makes the question answerable.

The project is one scrolling page with two dashboards:

1. **Taste Profile and Shared Listening**, which establishes the premise (our tastes barely overlap).
2. **Routine and Listening Intensity**, which gives the answer (where we are similar and where we are not).

The intended audience is music streaming users who are curious what their history says about their life beyond a yearly Wrapped, and of course the course staff.

*Viewing note: the site is best viewed in Chrome on a desktop screen at 100% zoom.*

---

## 2. The Data

### 2.1 Source

The data is our own. Each of us requested a full export of his listening history from his audio provider:

- **Roman** requested his "Extended Streaming History" from **Spotify** (a set of JSON files with one record per play).
- **Orr** requested his "Play Activity" data from **Apple Music** through Apple's Data and Privacy portal (a large CSV file).

The two exports describe the same kind of event (one play of one track) but in completely different formats, with different field names, different units and different conventions. Section 5.1 describes how we merged them into one table.

### 2.2 The unified fact table

After merging, the whole project is built from one event-level file, `fact_plays_with_genre.csv`, with about 180,000 rows (one row per play). The main fields:

| Field | Meaning |
|---|---|
| `owner` | Who the play belongs to (Or / Roman) |
| `source` | Which service it came from (apple / spotify) |
| `played_at_utc`, `played_at_local` | Timestamp of the play in UTC and in Israel local time |
| `date`, `weekday`, `hour_local` | Derived calendar fields used by the charts |
| `artist`, `artist_raw` | Normalized artist name, and the original spelling from the export |
| `track`, `album` | Track and album names |
| `ms_played`, `minutes_played` | How long the track actually played |
| `under_30s` | True if the play lasted under 30 seconds (computed identically for both services) |
| `skipped_native` | The service's own skip flag (kept but never used for comparison, see 5.1) |
| `genre` | External genre label added per artist (partial coverage) |

### 2.3 Analysis window and periods

- **Window: January 2021 to May 2026.** Orr's history starts in September 2018 and Roman's in September 2019, but Roman's data is sparse before 2021, so a comparison there would be unfair. We locked the window at 2021 onward (138,894 plays).
- **Two life periods:** `pre_uni` (January 2021 to December 2023, 36 months) and `university` (January 2024 onward, 29 months). We both started university in 2024, so this split is the heart of the research question. Since the periods have different lengths (1,095 vs 873 days), we always compare rates and averages, not raw totals.

### 2.4 What we added to the data

- **Genre.** Neither export contains genre. We attached a genre label per artist from an external source, and then collapsed the fine genres into about 6 broad families (Pop, Rock, Israeli, Metal, Electronic/Dance, Hip-Hop/R&B, plus "Other"). Coverage is partial, so everywhere genre appears in the site we mark it as external. After the collapse and a curated fix-up for top artists, the honest "Other" residual is 8.0% of Orr's minutes and 14.2% of Roman's (before the fix-up it was 30.2% and 35.5%).
- **A comparable skip measure.** Apple and Spotify count "skips" differently, so comparing their native skip flags would be wrong. Instead we computed `under_30s` (the play lasted less than 30 seconds) identically for both services from `ms_played`, and use only that.

---

## 3. Ideas and Planning

We did not arrive at the final page in one step. This section describes what we tried, what we changed and what we rejected, with the reasons.

### 3.1 Ideas we rejected before building

- **A Venn diagram or chord diagram of shared artists.** The time-weighted overlap between us is around half a percent of Roman's listening. A Venn diagram of that is an empty picture. Instead we chose a 100% strip that shows the overlap in minutes, which is the only honest unit for it.
- **A map.** Apple's export contains a city field but Spotify's does not, so location exists for only one of us. A one-sided map cannot compare anything.
- **A connected scatterplot** (Orr's monthly hours on one axis, Roman's on the other, one dot per month). It shows convergence and divergence as a shape, but it is famously hard for readers to decode. A mirrored timeline says the same thing and everyone can read it.
- **A radar / spider chart of behavior metrics.** Radar charts make magnitude comparison hard. We used a slopegraph instead (section 5.2.7).
- **A free date-range brush** on the timeline (select any period you want). Technically attractive, but our whole question is about two specific life periods. Fixed period buttons keep the story focused, and they also let us pre-compute everything (section 5.1).
- **An absolute/normalized toggle.** We decided on a rule: absolute, natural units everywhere, with one deliberate exception (the overlap strip uses percentages, because Roman listens to almost twice as many hours and raw minutes would mislead there). A global toggle would break that rule.

### 3.2 Things we built and then changed

- **KPI cards.** Both dashboards originally opened with a strip of "KPI cards" (hours, plays, artists, top artist and so on). We removed them: they are numbers to read, not patterns to see, and everything they said is now shown better by a chart. The full KPI table moved into this report (section 6.1), and the page keeps only visualizations.
- **The active-day histogram.** Dashboard 2 originally had a histogram of how many minutes each active day contained. After we added the slopegraph, the histogram stopped adding anything (its two insights, "Roman's days are heavier" and "especially at university", are both slopes in the slopegraph). We replaced it with the cumulative artist discovery curve, which shows a genuinely new axis of the data: exploration versus loyalty.
- **The shared-artist definition.** At first "shared" meant a name that appears in both histories. There are 130 such names, but most of them are accidental (one of us played the artist once for a few seconds). We tightened the definition: an artist is shared in a period only if **each of us** played it for at least 3 minutes **and** each of us has at least one real play of it (over 30 seconds). That leaves 40 truly shared artists over the whole window.
- **The heatmap color scale.** At first both routine heatmaps shared one absolute color scale. Because Roman's volume is much larger, Orr's heatmap looked washed out and his pattern was invisible, even though the panel's whole point is comparing the shape of the routines. We switched to one color scale per person (each person's own maximum), and the tooltip still shows the raw play counts.
- **The slopegraph axes.** Our first version zoomed each mini chart into the range of its data. It looked dramatic, but small differences looked huge, which is exactly the kind of lie a visualization course teaches you to avoid. We rebuilt it with zero-based axes, and percentage metrics get a full 0 to 100 scale.
- **Units.** Values used to switch between minutes and hours inconsistently. We fixed one rule for the whole site: anything over 60 minutes is shown in hours (with one decimal under 10 hours), anything under stays in minutes.

### 3.3 What we kept from the start

The two-dashboard structure (taste first as the premise, behavior second as the answer), the fixed person colors, the dark theme, and the single global period filter survived from the first sketch to the final page.

---

## 4. Solution and Design Decisions

### 4.1 Structure

One scrolling page, two stacked dashboards, seven panels, and deliberately **seven distinct chart shapes**: paired bar charts, a lollipop dot-plot, a 100% strip, a mirrored-area timeline, heatmaps, a cumulative curve and a slopegraph. Each panel answers one question and no two panels answer the same one.

### 4.2 Color

- **Color encodes person, and only person, in every cross-person chart:** Orr is bright blue (`#4EA1FF`) and Roman is bright orange (`#FF9F1C`). The pair is colorblind-safe and stays distinct in grayscale. The same two colors appear in the legend, the charts, the tooltips and the detail cards.
- **Inside a single person's chart** (for example, his genre bars), categories are separated only by lightness steps of that person's single hue, never by a second color palette. Inactive or filtered-out marks turn gray.
- The page uses a dark theme, so the two person colors were chosen to be strong against the dark background, and heatmap cells ramp from a visible dark floor rather than from the page background, so an empty cell reads as "empty" and not as "invisible".

### 4.3 Units

Absolute, natural units by default (hours, minutes, plays, artists). Percentages appear only where an absolute comparison would mislead: the overlap strip (Roman's much larger volume would hide the point) and per-person normalized scales in the heatmaps. Durations over 60 minutes are displayed as hours.

### 4.4 Interaction model

- **One global period filter** (All / Pre-uni / University) in a sticky bar that also carries the legend, so the two things you always need (which period, who is which color) are always on screen.
- **Every panel responds to the period filter.** Panels that show a single period recompute. Panels that show the whole span by design (the monthly timeline, the discovery curve, the slopegraph) do not hide data, they **emphasize** the selected period and dim the rest, so the overview never disappears.
- **Details on demand.** Tooltips everywhere. Clicking a genre family filters the artist lists and dims non-matching artists in the shared table. Clicking an artist opens a detail card and highlights that artist across panels (linked highlighting). Clicking a heatmap cell opens a drill-down of that specific hour of the week. Active filters appear as removable chips.

---

## 5. Implementation

### 5.1 Data preprocessing

Preprocessing happened in two stages: **merging the two exports into one fact table**, and then **aggregating that table for the site**.

#### Stage 1: merging two different export formats into one table

We each requested our listening history from our audio provider (Spotify for Roman, Apple Music for Orr). The two exports do not share a schema, so we merged them with the help of Claude (Anthropic's AI assistant), which we used to map, convert and normalize the fields into one common format. The main conversions:

- **Field name mapping.** The same fact has a different name in each export. For example, Spotify stores the artist as `master_metadata_album_artist_name` while Apple stores a song and container description in different fields. Every field was mapped into one shared schema (`owner`, `played_at_utc`, `artist`, `track`, `album`, `ms_played` and so on).
- **Timestamps and timezone.** Spotify gives play timestamps in UTC. Apple gives its own timestamp format. Both were parsed and converted to **Israel local time** (`played_at_local`), because the research question is about daily routine, and "9:00 in the morning" must mean the same thing for both of us. Calendar fields (`date`, `weekday`, `hour_local`) were derived from the local time.
- **Durations.** Both services record how long the track actually played in milliseconds (`ms_played`), but in different fields with different quirks. These were unified, and `seconds_played` / `minutes_played` were derived from them.
- **Artist name normalization.** The same artist can be spelled differently across services and even across years of the same service (featuring credits, "&" vs "and", trailing whitespace). Names were normalized so duplicates merge, and the original spelling is kept in `artist_raw` so nothing is lost.
- **A comparable skip measure.** Each service has a native skip flag (`skipped_native`) but they are counted differently, so they must never be compared. We computed `under_30s` identically for both sides from `ms_played` and use only it.
- **Fields without a twin.** Some fields exist for only one service (for example, Apple has a `city` column and Spotify has `shuffle`/`incognito` flags). These were kept in the fact table for honesty but were not used for any cross-person comparison.
- **Genre.** Added afterwards per artist from an external source, as described in 2.4.

The result is `fact_plays_with_genre.csv`, around 180,000 rows and 50 MB.

#### Stage 2: aggregating for the browser (`prep.py`)

The site never loads the 180,000-row table. A Python script (`prep.py`, using **pandas**) reads the fact table and produces one compact JavaScript object (`data.js`, about 310 KB) with exactly the aggregates the charts need:

1. Cut the data to the 2021+ window and tag each play with its period (`pre_uni` / `university`).
2. Collapse fine genres into broad families, then rescue top "Other" artists with a small curated artist-to-family map (only confident assignments, everything uncertain stays "Other").
3. Compute per period and per person: KPIs (hours, plays, unique artists, active days, median listening day, peak hour, top artist share, top-10 share, under-30-seconds rate), family compositions, top artist tables, per-family artist lists, the shared-artist set and its minutes-weighted shares, monthly totals, weekday-by-hour heatmap counts, per-cell drill-down lists, and the cumulative discovery series (how many distinct artists each person has heard by each month).
4. Print verification output: totals per period must sum to the totals of the whole window, and the final value of the discovery curve must equal the unique-artist count computed independently. The script fails loudly if they do not match.

As a final check we also wrote an independent verification script that recomputed every number from the raw CSV with fresh pandas code and compared it to `data.js`. All 74 checks matched.

### 5.2 The visualizations

*(One subsection per panel. Screenshots of each panel appear alongside the explanations.)*

#### 5.2.1 Genre Family Distribution (paired bar charts)

**Question: what does each person's taste actually look like?**

[SCREENSHOT: Genre Family Distribution panel]

Two aligned horizontal bar charts, one per person, sharing one x scale (percent of that person's minutes). Bar length encodes the share, and the bars inside each chart use lightness steps of the owner's hue. Hovering a family shows its minutes, share and most played artist. Clicking a family filters the artist panel below and dims non-matching artists in the shared table.

Why this chart: distribution across a handful of categories is exactly what bars with a common scale do best, and putting the two people side by side with one scale makes the taste gap immediate: Orr is 48.3% Pop and 29.5% Israeli, Roman is 72.9% Metal. There is no category where both are large.

Weakness: genre data is external and partial, so the "Other" bars (8.0% / 14.2%) must stay visible, and we label genre as provisional.

#### 5.2.2 Top Artist Concentration (lollipop dot-plot)

**Question: who are the obsessions, and how big are they?**

[SCREENSHOT: Top Artist Concentration panel]

A lollipop chart per person: the top 10 artists ranked by minutes, position encodes minutes, and a ring around a dot marks an artist that is in the shared set. Hovering highlights the artist everywhere, clicking opens a detail card (minutes, plays, share, first and last played date for both people when both have the artist).

Why this chart: lollipops keep the ranking readable with less ink than bars, and the ring adds the shared-set membership without a second color. The panel also states each person's top-10 concentration in its header (48.0% for Orr, 51.4% for Roman over the whole window), which becomes important later in the slopegraph.

Weakness: only the top of the distribution is visible. The long tail (especially Roman's 3,756 artists) is handled by the discovery curve instead.

#### 5.2.3 Minutes-Weighted Shared Listening (100% strips + table)

**Question: how much of our listening do we actually share?**

[SCREENSHOT: Minutes-Weighted Shared Listening panel]

One 100% strip per person, split into "shared artists" and "everything else", plus a table of the top 10 shared artists with each person's minutes. This is the one panel that uses percentages, because Roman's total volume is almost double and raw minutes would hide the asymmetry. Clicking a table row opens the artist's detail card. When a genre family is selected above, non-matching table rows dim, and a note explains that the strips always show the total.

Why this chart: the finding here is an asymmetry of proportions. 35.4% of Orr's minutes go to the 40 shared artists, but only 0.5% of Roman's. The same fact in one number per person, per period.

Weakness: a 100% strip hides absolute volume by design. The tooltips give the absolute hours back.

#### 5.2.4 Monthly Listening Volume (mirrored-area timeline)

**Question: how did each person's volume move across the whole span, and when did we split apart?**

[SCREENSHOT: Monthly Listening Volume panel]

A mirrored area chart of monthly hours: Orr drawn upward from a shared baseline, Roman drawn downward, with a dashed line marking the start of university. The chart always shows the full span. Selecting a period does not crop it, it dims the other period and outlines the selected one, so the "before and after" context never disappears. A hover crosshair reads both people's hours and plays for any month.

Why this chart: the mirror makes the two volumes comparable at every point in time without the lines crossing each other, and the timing of the divergence (gradual for Orr, an eruption for Roman after 2024) is a finding that only a full timeline can show.

Weakness: mirrored areas make exact value comparison between the two people harder than overlaid lines. The crosshair tooltip compensates.

#### 5.2.5 Listening Activity by Weekday and Hour (heatmaps + drill-down)

**Question: when in the week does each person live with music?**

[SCREENSHOT: Weekday-by-hour heatmaps]

One weekday-by-hour heatmap per person. Cell color encodes play counts on a per-person scale (each person relative to his own maximum), because the panel compares the shape of the routines, not the volumes. Hovering a weekday highlights the same weekday in both heatmaps. Clicking a cell opens a drill-down with that hour's totals and top artists and families for both people.

Why this chart: a routine is a two-dimensional pattern (day x hour), and a heatmap is the only compact way to show all 168 hours of the week at once. The two shapes are the finding: Orr is a morning listener (peak 9:00, busiest cell Friday at noon), Roman owns the night (peak 16:00 overall, moving to 22:00 at university, busiest cell Wednesday 16:00).

Weakness: normalized color means the two heatmaps cannot be compared by absolute intensity. That comparison belongs to the timeline and the slopegraph, and the tooltips still show raw counts.

#### 5.2.6 Cumulative Artist Discovery (cumulative curves)

**Question: is the connection to music about exploring or about returning?**

[SCREENSHOT: Cumulative Artist Discovery panel]

One cumulative line per person: how many distinct artists he has heard by each month. The university start is marked, and the period filter dims the non-selected period. The tooltip shows, for any month, the cumulative count and how many artists were heard for the first time that month.

Why this chart: the biggest number in the dataset (Roman's 3,756 artists against Orr's 1,108) is not really about taste, it is about behavior. The curve turns it into a shape: Roman's line keeps climbing at full speed through university (1,206 new artists) while Orr's flattens early and stays flat (328). For Orr, connection to music means returning to the same well. For Roman, the search itself is the connection.

Weakness: a cumulative curve can only rise, so slowing down is visible only as flattening. The tooltip's "new this month" number makes the rate explicit.

#### 5.2.7 Before Uni vs University: Same Direction or Opposite? (slopegraph)

**Question: when life changed, did we change the same way?**

[SCREENSHOT: Slopegraph panel]

Six mini slopegraphs, one per metric (hours per month, median listening day, share of days with music, top-10 artist share, number of different artists, plays kept past 30 seconds). Each connects the pre-uni value to the university value with one line per person. All axes start at zero, and percentage metrics span the full 0 to 100, so the steepness of a slope reflects the real size of the change. Selecting a period highlights that side of every slope. Hovering a line gives both values and the percent change.

Why this chart: the research question is literally "same direction or opposite", and a slopegraph is the one chart whose whole vocabulary is direction. Parallel lines mean we changed the same way (both concentration slopes rise in parallel), crossing lines mean we swapped (days with music). It is the synthesis panel of the project.

Weakness: it compresses each metric to two points, hiding everything in between. That is deliberate, the timeline above it carries the in-between.

### 5.3 Code, tools and libraries

| Tool / library | Used for |
|---|---|
| **Claude (Anthropic)** | Merging and normalizing the two export formats into one fact table, and assisting the development of the site |
| **Python 3 + pandas** | All data preprocessing and aggregation (`prep.py`), and the independent verification script |
| **D3.js v7** | Every chart on the page (no chart library on top of it) |
| **HTML/CSS/JavaScript** | One static page, no build step and no framework |
| **Prettier** | Code formatting |
| **Git + GitHub Pages** | Version control and free static hosting |

The repository contains: `index.html` (all markup, styles and chart code), `data.js` (the generated aggregates, about 310 KB), `prep.py` (the aggregation script), `lib/d3.v7.min.js`, and `DATA/` (the fact table, which is used only by `prep.py` and never shipped to the browser).

---

## 6. Findings

### 6.1 The numbers (all periods, both listeners)

| Metric | Orr, All | Roman, All | Orr, Pre-uni | Roman, Pre-uni | Orr, University | Roman, University |
|---|---|---|---|---|---|---|
| Hours of music | 1,963 | 3,394 | 1,202 | 1,291 | 761 | 2,103 |
| Average hours per month | 30.2 | 52.2 | 33.4 | 35.9 | 26.2 | 72.5 |
| Plays | 60,199 | 78,695 | 37,643 | 39,560 | 22,556 | 39,135 |
| Unique artists | 1,108 | 3,756 | 780 | 2,550 | 631 | 1,752 |
| Top artist | Imagine Dragons | Sleep Token | Imagine Dragons | Sleep Token | Imagine Dragons | Sleep Token |
| Top artist share of minutes | 14.5% | 26.2% | 12.6% | 15.3% | 17.7% | 32.9% |
| Top-10 artists share of minutes | 48.0% | 51.4% | 45.7% | 46.4% | 54.3% | 60.1% |
| Days with music | 1,623 (82.5%) | 1,626 (82.6%) | 987 (90.1%) | 805 (73.5%) | 636 (72.9%) | 821 (94.0%) |
| Median listening day | 61 min | 104 min | 59 min | 64 min | 65 min | 143 min |
| Peak listening hour | 9:00 | 16:00 | 9:00 | 16:00 | 11:00 | 22:00 |
| Plays kept past 30 seconds | 64.1% | 71.3% | 63.0% | 59.9% | 65.8% | 82.8% |

Shared listening: 40 truly shared artists over the whole window (out of 130 name-only matches). They take **35.4% of Orr's minutes but only 0.5% of Roman's** (pre-uni: 20.4% vs 0.2% over 12 artists, university: 42.1% vs 0.4% over 23 artists).

### 6.2 The findings in words

1. **The taste gap is real and extremely asymmetric.** Only 40 artists get real listening from both of us. For Orr they are a third of his musical life (35.4% of his minutes, led by Imagine Dragons and Taylor Swift). For Roman the same artists are background noise (0.5%). Shared taste is not just small, it means completely different things to each side. Interestingly, the overlap grew at university (from 12 shared artists to 23, and from 20.4% to 42.1% of Orr's minutes) but entirely from Orr's side: as Orr concentrated on globally popular artists, more of his listening landed on names Roman had touched, while Roman's share of shared music stayed flat near zero.

2. **Before university we were behavioral twins.** With essentially zero shared music, our relationship with music was almost identical: 33.4 vs 35.9 hours per month, a median listening day of 59 vs 64 minutes, a top-10 concentration of 45.7% vs 46.4%, and even similar patience (63.0% vs 59.9% of plays kept past 30 seconds). This is the strongest possible answer to the research question: the similarity lived entirely in behavior, not in taste.

3. **University broke the symmetry in opposite directions.** Orr's listening dropped 22% (33.4 to 26.2 hours per month) while Roman's doubled, up 102% (35.9 to 72.5). Roman's median day went from 64 minutes to 143 minutes, Orr's barely moved (59 to 65). One honest nuance the timeline shows: Roman's ramp does not start at the calendar boundary but in October 2023, the month the October 7 war began (74, 79 and 99 hours in October to December, against a 31.5-hour monthly average over the 33 months before). The shift was immediate and permanent: from October 2023 onward Roman averages 73.6 hours per month, and no month since has dropped back below his old average. The first days are the sharpest version of the whole finding. On October 7 itself Orr played no music at all, and stayed nearly silent for two weeks (2.5 hours in the first week of the war, against 7.1 the week before); Roman played 155 minutes that day, 340 the next, 405 the day after. The same event pushed one of us into silence and the other into immersion.

4. **Orr changes by drift, Roman by eruption.** Orr's yearly averages move gently (28, 35, 37, 30, 24, 23 hours per month from 2021 to 2026), while Roman swings hard (43, 22, 43, 76, 69, 72). Roman had a quiet year in 2022 that his pre-uni average hides, and his record month (105.7 hours in May 2024) is over sixty times his quietest (1.7 hours in March 2021). Orr's whole range is narrower, and his quietest month ever is a recent one (8.8 hours in March 2026), though the two months after it recovered (29.1 and 34.4 hours), so his slow fade is not a one-way slide. Stability versus volatility turned out to be a personality difference of its own.

5. **We swapped who is the everyday listener.** Pre-uni, Orr had music on 90.1% of days and Roman on 73.5%. At university it flipped: Orr 72.9%, Roman 94.0%. And over the whole five and a half years the totals land almost on the same value, 82.5% vs 82.6% of days, a coincidence that summarizes the whole project: same amount of life with music, completely different distribution of it.

6. **Under pressure, we both narrowed the same way.** Even though our volumes moved in opposite directions, our taste structure changed in the same direction: top-10 share rose for both (45.7 to 54.3 and 46.4 to 60.1), the number of different artists fell for both (780 to 631 and 2,550 to 1,752), and each of us leaned harder into his core genre (Orr's Pop 43.4% to 56.2%, Roman's Metal 54.1% to 84.4%). Opposite volume, same coping pattern.

7. **Exploration versus loyalty is a personality trait, not a taste.** During university Roman still met 1,206 new artists while Orr met 328. Roman's discovery curve never flattens, Orr's does early. And Roman's discovery comes in eruptions rather than a steady stream: 261 new artists in September 2021, 185 in March 2022, and 240 in January 2026, meaning a fresh exploration burst is happening in the newest data we have. Orr has no comparable burst anywhere in the window (his biggest genuine month is 71). Orr's opposite extreme has a date too: October and November 2023, the first two months of the war, are the only two consecutive months in the whole window in which he discovered zero new artists — for two months he played only music he already knew. Roman's connection to music includes the constant search itself, Orr's is about returning to known ground.

8. **Attention diverged too.** Pre-uni our "stay rates" were similar (63.0% vs 59.9% of plays kept past 30 seconds). At university Roman's jumped to 82.8% (he presses play and stays) while Orr stayed around 65.8%.

9. **The clock and the week are where we were never similar.** Orr is a morning listener (peak 9:00, drifting to 11:00 at university), Roman owns the afternoon and night (16:00, drifting to 22:00). Friday is Orr's biggest day of the week (19.1% of his plays, busiest single cell Friday at noon) while for Roman Friday is nearly his quietest day (11.5%, ahead of only Saturday). Same country, same weekend, opposite rhythm. Two small agreements hide inside the difference though: university pushed both of our peak hours later (Orr by two hours, Roman by six), and Saturday is the quietest day of the week for both of us (8.5% and 7.7% of plays). Roman's move into the night also predates the calendar boundary: the 22:00–05:00 share of his minutes jumped from 17–20% in July–September 2023 to 39–52% in October–December, so the night listener of the university period was born in October 2023.

10. **One artist can mean very different things.** Roman's top artist (Sleep Token) grew from 15.3% to 32.9% of everything he plays, a level of devotion Orr never reaches with anyone (Imagine Dragons peaked at 17.7%).

---

## 7. Limitations

- **Genre is external and partial.** Neither export includes genre. Our external labels cover most minutes but not all, and the honest residual stays visible as "Other" (8.0% of Orr's minutes, 14.2% of Roman's). Genre findings are therefore indicative, not exact.
- **2,587 of Orr's plays (about 85 hours) have no artist name** in the Apple export. They are counted in his totals (they are real listening) but cannot appear in any artist ranking. Roman's export has no such rows.
- **Two different services log differently.** We neutralized the known differences (timezone, duration fields, skip counting) but cannot rule out subtler logging differences between Apple Music and Spotify.
- **The periods have different lengths** (36 vs 29 months), so all comparisons use rates and averages rather than totals. The split is also calendar-based (January 2024), while Roman's volume ramp visibly starts about three months earlier, so the period averages slightly understate how early his change began.
- **The period boundary does not separate the war from university.** The October 7 war began three months before the calendar split, and it also delayed the opening of the academic year. Roman's volume shift, his move into night listening and his rise in average play length (2.3 to 3.1 minutes) all begin in October 2023, and Orr's two-month discovery freeze happens then as well, so part of what the "university" period measures may be the war's effect rather than student life. The data shows the timing, not the cause.
- **The discovery curve counts "first heard inside the window"**, so the first month or two of 2021 absorb artists we already knew from before. We therefore never treat the very first months as genuine discovery bursts.
- **This is a study of two people.** The findings are insights about us, not statistics about listeners in general. The value is in the depth of the comparison, not in generalization.

---

## 8. Conclusion

Our research question asked whether similarity between listeners has to live in musical taste, or whether it can be found in listening patterns, routines and the intensity of the connection to music.

The answer from the data is clear. With almost no shared music (40 artists, worth half a percent of Roman's time), we were nearly identical listeners before university: the same monthly volume, the same length of a typical day, the same concentration of taste, similar patience with songs. The similarity lived entirely in behavior. Then the same life event pushed us in opposite directions in **how much** we listen (Orr down 22%, Roman up 102%, and we swapped who listens every day), while pushing us in the **same** direction in how we listen (both of us narrowed toward fewer artists and our core genre). And underneath both periods, some things never converged at all: morning versus night, Friday versus weekdays, returning versus exploring.

So no, similarity between listeners does not have to be in taste. Two people can share almost no music and still be the same kind of listener, until life happens, and then the same event can split their intensity while bending their habits in exactly the same way. None of that is visible in a playlist. All of it is visible in the data.

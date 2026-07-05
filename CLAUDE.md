# CLAUDE.md — Music Listening Visualization

Final Data Visualization project: an interactive D3.js site comparing two friends'
listening histories. Two people: **Or** (Apple Music) and **Roman** (Spotify).
Static site for GitHub Pages, no build step. Talk to me in Hebrew; keep all code,
comments, UI text, file names, and the report in English.

## Data (CSV in repo; charts are built ONLY from these aggregates, never raw events)
- artist_totals_with_genre.csv — owner, artist, plays, minutes, first_played, last_played, rank_in_owner, shared_by_both, genre
- monthly_totals.csv — owner, ym ("YYYY-MM"), plays, minutes
- genre_monthly.csv — owner, ym, genre, plays, minutes
- hour_weekday.csv — owner, weekday, hour_local, plays, pct_of_owner (SPARSE: missing day-hour combos = real zeros)
- hour_weekday_year.csv — owner, year, weekday, hour_local, plays, pct_of_owner_year
- daily_totals.csv, hourly_profile.csv, owner_summary.csv, or_playlists.csv, or_preferences.csv
Full schema, sources, and pre-processing already done are in README.md.

## Conventions
- D3.js (v7) loaded from CDN. Vanilla JS/CSS, no bundler. Load CSVs with d3.csv.
- Separate files: index.html, css/, js/ (one JS module per dashboard + shared helpers).

## Critical rules
- <important>Use ONLY the data in these files. Never invent numbers, artists, or findings. If a value is genuinely unavailable, write [check].</important>
- <important>ONE color scheme per dashboard: color = person. Or = blue, Roman = orange. Colorblind-safe, readable in black and white. Genre is a category/axis or tooltip field, never a second color scheme.</important>
- <important>In the heatmap, build the full weekday×hour grid in code; render missing cells as zero (lightest shade), not as gaps.</important>
- Bar charts: Y axis starts at 0. Horizontal bars for long names. Prefer bars over pie.
- State data limits where relevant: different date ranges (overlap 2019–2026), partial genre coverage (Other = 29% of Or, 44% of Roman), city-level location for Or only.

## Report voice
Student voice, not AI. No em dashes. Avoid: delve, tapestry, moreover, furthermore, leverage,
utilize, robust, seamless, intricate, underscore, comprehensive, "It's worth noting", "Overall",
"In conclusion". Prefer everyday words, varied sentence length, first person plural ("we chose",
"we noticed"), concrete specifics from the real data.
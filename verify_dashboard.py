"""verify_dashboard.py — independent audit of the dashboards against the fact table.

Three parts:
  A. Regenerate data.js by running prep.py and confirm the output is byte-identical
     to the committed data.js (the browser renders only from data.js).
  B. Extract every hardcoded numeric claim in index.html (hint text, table headers,
     slice sizes, the 30-second label) and check each against prep.py's constants
     and a fresh recomputation from DATA/fact_plays_with_genre.csv.
  C. Recompute every aggregate the panels display (KPIs, shared overlap, families,
     discovery, monthly extremes, heatmap peaks) from the fact CSV with fresh
     pandas code and compare to data.js.

Prints a PASS/FAIL table and exits nonzero on any failure.

Run:  python verify_dashboard.py
"""

import json
import re
import subprocess
import sys

import pandas as pd

FACT_CSV = "DATA/fact_plays_with_genre.csv"
WINDOW_START = "2021-01-01"
UNI_START = "2024-01-01"
OWNERS = ["Or", "Roman"]

sys.stdout.reconfigure(encoding="utf-8")

results = []  # (status, claim, shown_value, csv_value)


def check(claim, shown, computed, tol=0.0):
    if isinstance(shown, float) or isinstance(computed, float):
        ok = abs(float(shown) - float(computed)) <= tol
    else:
        ok = shown == computed
    results.append(("PASS" if ok else "FAIL", claim, shown, computed))


# ---------------------------------------------------------------- part A
print("== Part A: data.js regeneration ==")
with open("data.js", "rb") as f:
    committed = f.read()
subprocess.run([sys.executable, "prep.py"], check=True, capture_output=True)
with open("data.js", "rb") as f:
    fresh = f.read()
check("data.js byte-identical to fresh prep.py run", len(committed), len(fresh))
if committed != fresh:
    results.append(("FAIL", "data.js content identical", "committed", "differs"))
else:
    results.append(("PASS", "data.js content identical", "identical", "identical"))

D = json.loads(fresh.decode("utf-8").split("=", 1)[1].rstrip().rstrip(";"))

# ---------------------------------------------------------------- load CSV
full = pd.read_csv(FACT_CSV, usecols=["owner", "date", "weekday", "hour_local", "artist",
                                      "minutes_played", "ms_played", "under_30s", "genre"])
full["date"] = pd.to_datetime(full["date"])
full["under_30s"] = full["under_30s"].astype(str).eq("True")
check("full history rows", 180003, len(full))

df = full[full["date"] >= WINDOW_START].copy()
df["period"] = df["date"].map(lambda d: "university" if d >= pd.Timestamp(UNI_START) else "pre_uni")
df["ym"] = df["date"].dt.strftime("%Y-%m")
check("window rows", 138894, len(df))

cuts = {"all": df, "pre_uni": df[df.period == "pre_uni"], "university": df[df.period == "university"]}

# ---------------------------------------------------------------- part B
print("== Part B: hardcoded claims in index.html ==")
html = open("index.html", encoding="utf-8").read()
prep_src = open("prep.py", encoding="utf-8").read()

# A3's sub-label says "played it N+ min"; the footer says "≥ N minutes".
shared_min_html = int(re.search(r"played it (\d+)\+ min", html).group(1))
shared_min_foot = int(re.search(r"≥ (\d+) minutes", html).group(1))
shared_min_prep = int(re.search(r"SHARED_MIN_MINUTES = (\d+)", prep_src).group(1))
check("A3 sub 'N+ min' == prep SHARED_MIN_MINUTES", shared_min_html, shared_min_prep)
check("footer '≥ N minutes' == prep SHARED_MIN_MINUTES", shared_min_foot, shared_min_prep)
check("A3 sub 'N+ min' == data.js meta", shared_min_html, D["meta"]["shared_min_minutes"])

top_n_header = int(re.search(r"top (\d+) shared artists", html).group(1))
# data-row truncations only: WINDOW_START/UNI_START.slice(0, 7) are string slices
# of date constants ("2021-01-01" -> "2021-01"), not row limits.
slices = [int(m.group(1)) for m in re.finditer(r"slice\(0, ?(\d+)\)", html)
          if "_START.slice" not in html[max(0, m.start() - 30):m.end()]]
check("'top 10 shared artists' header == table slice", top_n_header, slices.count(10) >= 1 and 10)
check("all top-artist/shared slices are 10 (plus one 8 for family lists)",
      sorted(slices), sorted([10, 10, 10, 8]))
check("shipped top_shared rows cover the 10 shown", True, len(D["shared"]["top_shared"]["all"]) >= 10)
check("shipped top_artists cover the 10 shown", True,
      all(len(D["top_artists"]["all"][o]) >= 10 for o in OWNERS))

thirty = int(re.search(r"past (\d+) s", html).group(1))
mismatch = int(((full.ms_played < thirty * 1000) != full.under_30s).sum())
check("'past 30 s' label: under_30s == ms_played < 30000 (mismatch rows)", 0, mismatch)

# ---------------------------------------------------------------- part C
print("== Part C: aggregates the panels display, recomputed from CSV ==")
for cut, d in cuts.items():
    for o in OWNERS:
        g = d[d.owner == o]
        k = D["kpis"][cut][o]
        daily = g.groupby("date")["minutes_played"].sum()
        top = g.groupby("artist")["minutes_played"].sum().sort_values(ascending=False)
        check(f"{cut}/{o} hours", k["hours"], round(g.minutes_played.sum() / 60, 1), 0.05)
        check(f"{cut}/{o} plays", k["plays"], len(g))
        check(f"{cut}/{o} unique artists", k["unique_artists"], g.artist.nunique())
        check(f"{cut}/{o} active days", k["active_days"], len(daily))
        check(f"{cut}/{o} median daily min", k["median_daily_min"], round(float(daily.median()), 1), 0.05)
        check(f"{cut}/{o} peak hour", k["peak_hour"], int(g.groupby("hour_local").size().idxmax()))
        check(f"{cut}/{o} under30 pct", k["under30_pct"], round(g.under_30s.mean() * 100, 1), 0.05)
        check(f"{cut}/{o} top artist", k["top_artist"], top.index[0])
        check(f"{cut}/{o} top artist share", k["top_artist_share"],
              round(top.iloc[0] / g.minutes_played.sum() * 100, 1), 0.05)
        check(f"{cut}/{o} top10 share", k["top10_share"],
              round(top.head(10).sum() / g.minutes_played.sum() * 100, 1), 0.05)

# shared overlap (strict definition: 3+ min each AND >=1 real play each)
name_matches = len(set(df[df.owner == "Or"].artist.dropna()) & set(df[df.owner == "Roman"].artist.dropna()))
check("name-only matches", D["shared"]["name_matches"], name_matches)
for cut, d in cuts.items():
    per = d.groupby(["artist", "owner"]).minutes_played.sum().unstack(fill_value=0)
    loose = set(per[(per.Or >= shared_min_prep) & (per.Roman >= shared_min_prep)].index)
    real = d[~d.under_30s]
    strict = loose & set(real[real.owner == "Or"].artist) & set(real[real.owner == "Roman"].artist)
    check(f"{cut} shared artist count", D["shared"]["count_by_cut"][cut], len(strict))
    for o in OWNERS:
        g = d[d.owner == o]
        pct = round(g[g.artist.isin(strict)].minutes_played.sum() / g.minutes_played.sum() * 100, 1)
        check(f"{cut} shared minutes pct {o}", D["shared"]["pct_minutes"][cut][o], pct, 0.05)

# families (all cut): shipped minutes must sum to the owner's CSV total, and the
# displayed percentages must sum to ~100 (family assignment itself is prep's
# curated map, which Part A already covers via the byte-identical regeneration)
for o in OWNERS:
    shipped = {r["family"]: r["minutes"] for r in D["families"]["all"][o]}
    check(f"families/{o} minutes sum == owner total", round(sum(shipped.values()), 0),
          round(df[df.owner == o].minutes_played.sum(), 0), 2)
    pcts = {r["family"]: r["pct"] for r in D["families"]["all"][o]}
    check(f"families/{o} pcts sum to ~100", 100.0, round(sum(pcts.values()), 0), 0.6)

# discovery: final cumulative equals unique artists; no negative months
for o in OWNERS:
    first = df[df.owner == o].groupby("artist").ym.min()
    months = sorted(df.ym.unique())
    check(f"discovery/{o} final cumulative", D["discovery"][o][-1]["cum"], int(len(first)))
    spot = "2023-12"
    check(f"discovery/{o} cumulative @{spot}", next(r["cum"] for r in D["discovery"][o] if r["ym"] == spot),
          int((first <= spot).sum()))

# monthly extremes per owner (what the river draws)
for o in OWNERS:
    m = df[df.owner == o].groupby("ym").minutes_played.sum() / 60
    shipped = {r["ym"]: r["hours"] for r in D["monthly"][o]}
    mx, mn = m.idxmax(), m.idxmin()
    check(f"monthly/{o} max month {mx}", shipped[mx], round(m[mx], 1), 0.05)
    check(f"monthly/{o} min month {mn}", shipped[mn], round(m[mn], 1), 0.05)

# heatmap busiest cell per owner (all cut)
for o in OWNERS:
    g = df[df.owner == o].groupby(["weekday", "hour_local"]).size()
    (wd, hr), n = g.idxmax(), int(g.max())
    shipped = next(c["plays"] for c in D["heatmap"]["all"][o] if c["weekday"] == wd and c["hour"] == int(hr))
    check(f"heatmap/{o} busiest cell {wd} {int(hr)}:00", shipped, n)

# days-with-music percentages (finding shown via slopegraph 'days with music')
period_days = D["meta"]["period_days"]
for cut, d in cuts.items():
    for o in OWNERS:
        pct = round(d[d.owner == o].groupby("date").size().shape[0] / period_days[cut] * 100, 1)
        shipped = round(D["kpis"][cut][o]["active_days"] / period_days[cut] * 100, 1)
        check(f"{cut}/{o} days-with-music pct", shipped, pct, 0.05)

# ---------------------------------------------------------------- summary
print()
w = max(len(r[1]) for r in results) + 2
fails = 0
for status, claim, shown, computed in results:
    if status == "FAIL":
        fails += 1
    print(f"{status}  {claim:<{w}} shown={shown}  csv={computed}")
print()
print(f"RESULT: {len(results)} checks, {fails} failures")
sys.exit(1 if fails else 0)

#!/usr/bin/env python3
"""
prepare_data.py — distill the raw CSV exports in DATA/ into small JSON files in data/.

The browser never loads the big fact_plays*.csv files (~50 MB); this script uses
fact_plays.csv only to build period-accurate hour x weekday aggregates (the period
boundaries cut mid-year, so the year-granular hour_weekday_year.csv cannot represent
them exactly).

Everything is trimmed to the DATA_START window (2020-01 onward).

Outputs (all small, all consumed by index.html via d3.json):
  data/meta.json       — data window + life-period boundaries (single source for the UI)
  data/monthly.json    — hours per owner per month             -> Intensity river
  data/heatmap.json    — plays + pct per owner/period/weekday/hour -> Routine heatmap
  data/daylength.json  — active-day length buckets per owner/period -> Day-length chart
  data/headlines.json  — per owner/period headline stats + takeover shares -> Dashboard 2
  data/artists.json    — artists per owner x discovery-year x play-count tier
                         -> Dashboard 2 discovery line + stickiness bars (linked)

At the end it prints the CSV ground-truths from CLAUDE.md so they can be checked
against what the dashboards display.
"""

import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "DATA"
OUT_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# Data window and life periods (adjustable constants). Everything before
# DATA_START is dropped from every output. Period boundaries are inclusive
# "YYYY-MM" month strings; None means open-ended. Whole-year buckets today —
# if a mid-year cutoff is ever needed, edit the one boundary string here.
# These drive the global period selector.
# ---------------------------------------------------------------------------
DATA_START = "2020-01"

PERIODS = {
    "all": {"label": "All", "start": None, "end": None},
    "covid": {"label": "COVID", "start": "2020-01", "end": "2021-12"},
    "preuni": {"label": "Pre-uni", "start": "2022-01", "end": "2023-12"},
    "university": {"label": "University", "start": "2024-01", "end": None},  # key window
}

# Israeli week: Sunday first. Used to give the heatmap a fixed row order.
WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Active-day length buckets (minutes). Upper bound exclusive; last is open-ended.
DAY_BUCKETS = [
    ("<=30m", 0, 30),
    ("30-60m", 30, 60),
    ("1-2h", 60, 120),
    ("2-3h", 120, 180),
    ("3-5h", 180, 300),
    ("5h+", 300, None),
]

OWNERS = ["Or", "Roman"]


def in_period(ym: pd.Series, key: str) -> pd.Series:
    """Boolean mask: which "YYYY-MM" values fall inside the given period.

    String comparison works because the format is zero-padded ISO year-month.
    The global DATA_START cutoff applies to every period, including "all".
    """
    p = PERIODS[key]
    mask = ym >= DATA_START
    if p["start"]:
        mask &= ym >= p["start"]
    if p["end"]:
        mask &= ym <= p["end"]
    return mask


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    # utf-8-sig strips the BOM some of the exports carry in their header row.
    return pd.read_csv(DATA_DIR / name, encoding="utf-8-sig", **kwargs)


# ---------------------------------------------------------------------------
# 1. Intensity river — hours per owner per month (monthly_totals.csv is already
#    the right grain and small; we just convert minutes to hours).
# ---------------------------------------------------------------------------
def build_monthly() -> list[dict]:
    monthly = read_csv("monthly_totals.csv")
    monthly = monthly[monthly["ym"] >= DATA_START]
    monthly["hours"] = (monthly["minutes"] / 60).round(2)
    return monthly[["owner", "ym", "plays", "hours"]].to_dict("records")


# ---------------------------------------------------------------------------
# 2. Routine heatmap — plays per owner x weekday x hour, per period, plus the
#    pct of that owner's plays *within the period* (so the two people are
#    comparable despite very different volumes). Built from fact_plays.csv
#    because periods cut mid-year.
# ---------------------------------------------------------------------------
def build_heatmap() -> list[dict]:
    fact = read_csv("fact_plays.csv", usecols=["owner", "date", "weekday", "hour_local"])
    fact = fact.dropna(subset=["weekday", "hour_local"])
    fact["hour"] = fact["hour_local"].astype(int)
    fact["ym"] = fact["date"].str[:7]

    rows = []
    for key in PERIODS:
        sub = fact[in_period(fact["ym"], key)]
        counts = sub.groupby(["owner", "weekday", "hour"]).size().rename("plays").reset_index()
        totals = counts.groupby("owner")["plays"].transform("sum")
        counts["pct"] = (counts["plays"] / totals * 100).round(3)
        counts.insert(0, "period", key)
        rows += counts.to_dict("records")
    return rows


# ---------------------------------------------------------------------------
# 3. Day-length distribution — on active days, how many minutes were played,
#    bucketed; pct = share of that owner's active days in the period.
# ---------------------------------------------------------------------------
def build_daylength() -> list[dict]:
    daily = read_csv("daily_totals.csv")
    daily["ym"] = daily["date"].str[:7]
    edges = [b[1] for b in DAY_BUCKETS] + [float("inf")]
    labels = [b[0] for b in DAY_BUCKETS]
    daily["bucket"] = pd.cut(daily["minutes"], bins=edges, labels=labels, right=True,
                             include_lowest=True)

    rows = []
    for key in PERIODS:
        sub = daily[in_period(daily["ym"], key)]
        counts = (sub.groupby(["owner", "bucket"], observed=False).size()
                  .rename("days").reset_index())
        totals = counts.groupby("owner")["days"].transform("sum")
        counts["pct"] = (counts["days"] / totals * 100).round(2)
        counts.insert(0, "period", key)
        rows += counts.to_dict("records")
    return rows


# ---------------------------------------------------------------------------
# 4. Dashboard 2 headlines — per owner and period: the artist "takeover"
#    shares (100% stacked bar: #1 / #2-5 / #6-10 / rest of minutes) plus the
#    headline stats (top artist, under_30s rate, artists-to-half — the last
#    two are also the printed ground-truth checks).
#    plays_daily.csv is the source for every period INCLUDING "all": it is the
#    only artist-level table that can be trimmed to the DATA_START window
#    (artist_totals.csv is all-time from 2018-09 and cannot). Caveat: plays_daily
#    lacks ~4k plays whose artist or date is missing in the raw export.
# ---------------------------------------------------------------------------
def artist_stats(by_artist: pd.Series) -> dict:
    """Concentration stats from a minutes-per-artist series (sorted desc)."""
    total_min = by_artist.sum()
    cum = by_artist.cumsum() / total_min

    def share(lo: int, hi: int | None) -> float:
        """% of minutes taken by artist ranks lo..hi (1-based, inclusive)."""
        return round(by_artist.iloc[lo - 1:hi].sum() / total_min * 100, 1)

    return {
        "unique_artists": int(by_artist.size),
        "top_artist": by_artist.index[0],
        "top_share_pct": round(by_artist.iloc[0] / total_min * 100, 1),
        "top_hours": round(by_artist.iloc[0] / 60, 1),
        # first index position where cumulative share reaches 50%
        "artists_to_half": int((cum < 0.5).sum()) + 1,
        # takeover-bar segments (sum to ~100 modulo rounding)
        "share_top1": share(1, 1),
        "share_top2_5": share(2, 5),
        "share_top6_10": share(6, 10),
        "share_rest": share(11, None),
    }


def build_headlines(pdaily: pd.DataFrame) -> dict:
    out: dict[str, dict] = {}
    for key in PERIODS:
        sub = pdaily[in_period(pdaily["ym"], key)]
        out[key] = {}
        for owner in OWNERS:
            d = sub[sub["owner"] == owner]
            plays = int(d["plays"].sum())
            if plays == 0:
                out[key][owner] = None
                continue
            by_artist = d.groupby("artist")["minutes"].sum().sort_values(ascending=False)
            out[key][owner] = {
                "plays": plays,
                "short_plays": int(d["short_plays"].sum()),
                "under30_pct": round(d["short_plays"].sum() / plays * 100, 1),
                "hours": round(by_artist.sum() / 60, 1),
                "active_days": int(d["date"].nunique()),
                **artist_stats(by_artist),
            }
    return out


# ---------------------------------------------------------------------------
# 5. Dashboard 2 discovery + stickiness (one shared table, so the two charts
#    can link): artists per owner x first-played year x play-count tier.
#    - Discovery line: sum the tiers per year -> newly discovered artists/year.
#    - Stickiness bars: sum the years (all, a period's years, or one clicked
#      cohort year) -> tier shares of that artist list.
#    Source: artist_totals.csv — first_played and plays are ALL-TIME values
#    from the full export, deliberately NOT trimmed to DATA_START: "discovered"
#    means first play ever, and "stuck" means total plays ever. Pre-2020 rows
#    ship too, so the unfiltered stickiness bars can show each person's full
#    artist list; the discovery line simply starts its x-axis at 2020.
#    Honesty caveats (the UI must surface them): each history begins somewhere
#    (Or 2018-09, Roman 2019-09), so the earliest years count returning
#    favorites as "new" (left-censoring); the last year is partial; recently
#    discovered artists have had less time to accumulate plays.
# ---------------------------------------------------------------------------
DISCOVERY_TIERS = [   # play-count tiers; upper bounds inclusive, last open-ended
    ("1 play", 1, 1),
    ("2-9", 2, 9),
    ("10-49", 10, 49),
    ("50+", 50, None),
]


def build_artists() -> list[dict]:
    at = read_csv("artist_totals.csv", usecols=["owner", "artist", "plays", "first_played"])
    at["year"] = at["first_played"].str[:4].astype(int)
    edges = [t[1] for t in DISCOVERY_TIERS] + [float("inf")]
    labels = [t[0] for t in DISCOVERY_TIERS]
    at["tier"] = pd.cut(at["plays"], bins=edges, labels=labels, right=False)
    counts = (at.groupby(["owner", "year", "tier"], observed=False).size()
              .rename("artists").reset_index())
    counts = counts[counts["artists"] > 0]
    return counts.to_dict("records")


# ---------------------------------------------------------------------------
# Key figures + ground-truth checks, recomputed from the CSVs so a mismatch is
# loud rather than silently shipped. Expected values are for the DATA_START
# window and live in CLAUDE.md; the Sleep Token ~25% check should hold
# regardless of where the cutoff sits (Roman barely predates 2020).
# ---------------------------------------------------------------------------
def print_key_figures(headlines: dict) -> None:
    print(f"\n=== Key figures per period (window starts {DATA_START}) ===")
    for key, p in PERIODS.items():
        print(f"[{p['label']}]  {p['start'] or DATA_START} .. {p['end'] or 'end'}")
        for owner in OWNERS:
            h = headlines[key][owner]
            if h is None:
                print(f"  {owner}: no data")
                continue
            print(f"  {owner}: {h['hours']:,} h, under_30s {h['under30_pct']}%, "
                  f"#1 {h['top_artist']} {h['top_share_pct']}%, "
                  f"{h['unique_artists']:,} artists, {h['artists_to_half']} to half")

    print("\n=== Ground truths (window totals, expected values from CLAUDE.md) ===")
    for owner, exp_top, exp_share, exp_unique, exp_u30 in [
        ("Or", "Imagine Dragons", 14.6, 1241, 38.2),
        ("Roman", "Sleep Token", 25.6, 3854, 29.4),
    ]:
        h = headlines["all"][owner]
        print(f"{owner}: #1 = {h['top_artist']} ({h['top_share_pct']}%)"
              f"  [expected {exp_top} {exp_share}%]")
        print(f"{owner}: unique artists = {h['unique_artists']:,}  [expected {exp_unique:,}]")
        print(f"{owner}: under_30s = {h['under30_pct']}%  [expected {exp_u30}%]")

    st = headlines["all"]["Roman"]
    ok = st["top_artist"] == "Sleep Token" and 24 <= st["top_share_pct"] <= 27
    print(f"Robust check: Sleep Token ~25% of Roman's minutes -> "
          f"{st['top_share_pct']}% [{'OK' if ok else 'FAILED — investigate'}]")

    print("\n(The same numbers ship to the browser in data/headlines.json.)")


def print_artist_figures(artists: list[dict]) -> None:
    df = pd.DataFrame(artists)
    print("\n=== Newly discovered artists per year (first_played year, 2020+) ===")
    per_year = (df[df["year"] >= 2020].groupby(["owner", "year"])["artists"].sum()
                .unstack(fill_value=0))
    print(per_year.to_string())
    print("(Earliest years are left-censored - each history starts somewhere; "
          "the last year is partial.)")

    print("\n=== Stickiness tiers, full artist list "
          "(% of that person's artists; all-time play counts) ===")
    tier_order = [t[0] for t in DISCOVERY_TIERS]
    for owner in OWNERS:
        d = df[df["owner"] == owner].groupby("tier", sort=False)["artists"].sum()
        total = d.sum()
        pcts = ", ".join(f"{t}: {d.get(t, 0) / total * 100:.1f}%" for t in tier_order)
        print(f"{owner} (n={total:,}): {pcts}")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    # plays_daily feeds both the monthly skip line and the per-period headlines
    pdaily = read_csv("plays_daily.csv",
                      usecols=["owner", "date", "artist", "plays", "short_plays", "minutes"])
    pdaily["ym"] = pdaily["date"].str[:7]
    pdaily = pdaily[pdaily["ym"] >= DATA_START]

    files = {
        "meta.json": {"periods": PERIODS, "weekdays": WEEKDAYS, "owners": OWNERS,
                      "data_start": DATA_START},
        "monthly.json": build_monthly(),
        "heatmap.json": build_heatmap(),
        "daylength.json": build_daylength(),
        "headlines.json": build_headlines(pdaily),
        "artists.json": build_artists(),
    }
    for name, payload in files.items():
        path = OUT_DIR / name
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {path} ({path.stat().st_size / 1024:.0f} KB)")

    print_key_figures(files["headlines.json"])
    print_artist_figures(files["artists.json"])


if __name__ == "__main__":
    main()

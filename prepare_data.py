#!/usr/bin/env python3
"""
prepare_data.py — distill the raw CSV exports in DATA/ into small JSON files in data/.

The browser never loads the big fact_plays*.csv files (~50 MB); this script uses
fact_plays.csv only to build period-accurate hour x weekday aggregates (the period
boundaries cut mid-year, so the year-granular hour_weekday_year.csv cannot represent
them exactly).

Outputs (all small, all consumed by index.html via d3.json):
  data/meta.json       — life-period boundaries and labels (single source for the UI)
  data/monthly.json    — hours per owner per month           -> Intensity river
  data/heatmap.json    — plays + pct per owner/period/weekday/hour -> Routine heatmap
  data/daylength.json  — active-day length buckets per owner/period -> Day-length chart
  data/headlines.json  — per owner/period headline numbers   -> Dashboard 2

At the end it prints the CSV ground-truths from CLAUDE.md so they can be checked
against what the dashboards display.
"""

import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "DATA"
OUT_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# Life periods (adjustable constants). Boundaries are inclusive "YYYY-MM" month
# strings; None means open-ended. These drive the global period selector.
# ---------------------------------------------------------------------------
PERIODS = {
    "all": {"label": "All", "start": None, "end": None},
    "army": {"label": "Army", "start": None, "end": "2021-06"},
    "covid": {"label": "COVID", "start": "2021-07", "end": "2023-09"},
    "university": {"label": "University", "start": "2023-10", "end": None},
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
    """
    p = PERIODS[key]
    mask = pd.Series(True, index=ym.index)
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
# 4. Dashboard 2 headlines — per owner and period:
#    top-1 artist share of minutes, under_30s rate (short_plays / plays, the
#    only skip measure comparable across Apple and Spotify), and how many
#    artists cover 50% of listening minutes. plays_daily.csv has the
#    owner x date x artist grain needed to filter all three by period.
#
#    Exception: for the "all" period the artist-level stats are recomputed from
#    artist_totals.csv, the designated source for concentration. plays_daily
#    lacks ~4k plays whose artist or date is missing in the raw export, which
#    shifts Or's top share from 14.3% to 14.4% and undercounts unique artists.
# ---------------------------------------------------------------------------
def artist_stats(by_artist: pd.Series) -> dict:
    """Concentration stats from a minutes-per-artist series (sorted desc)."""
    total_min = by_artist.sum()
    cum = by_artist.cumsum() / total_min
    return {
        "unique_artists": int(by_artist.size),
        "top_artist": by_artist.index[0],
        "top_share_pct": round(by_artist.iloc[0] / total_min * 100, 1),
        "top_hours": round(by_artist.iloc[0] / 60, 1),
        # first index position where cumulative share reaches 50%
        "artists_to_half": int((cum < 0.5).sum()) + 1,
    }


def build_headlines() -> dict:
    pdaily = read_csv("plays_daily.csv",
                      usecols=["owner", "date", "artist", "plays", "short_plays", "minutes"])
    pdaily["ym"] = pdaily["date"].str[:7]

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

    # All-time artist stats from the complete artist-level table (see note above).
    at = read_csv("artist_totals.csv")
    for owner in OWNERS:
        by_artist = (at[at["owner"] == owner].set_index("artist")["minutes"]
                     .sort_values(ascending=False))
        out["all"][owner].update(artist_stats(by_artist))
        out["all"][owner]["hours"] = round(by_artist.sum() / 60, 1)
    return out


# ---------------------------------------------------------------------------
# Ground-truth checks (all-time numbers from CLAUDE.md, recomputed from the
# CSVs so a mismatch is loud rather than silently shipped).
# ---------------------------------------------------------------------------
def print_ground_truths(headlines: dict) -> None:
    at = read_csv("artist_totals.csv")
    print("\n=== Ground truths (all-time, expected values from CLAUDE.md) ===")
    for owner, exp_top, exp_share, exp_unique in [
        ("Or", "Imagine Dragons", 14.3, 1436),
        ("Roman", "Sleep Token", 25.4, 4036),
    ]:
        d = at[at["owner"] == owner]
        top = d.sort_values("minutes", ascending=False).iloc[0]
        share = round(top["minutes"] / d["minutes"].sum() * 100, 1)
        print(f"{owner}: #1 artist = {top['artist']} ({share}% of minutes)"
              f"  [expected {exp_top} {exp_share}%]")
        print(f"{owner}: unique artists = {d['artist'].nunique()}  [expected {exp_unique}]")

    for owner, exp in [("Or", 41.5), ("Roman", 30.0)]:
        h = headlines["all"][owner]
        print(f"{owner}: under_30s = {h['under30_pct']}%  [expected {exp}%]")

    print("\n(The same numbers ship to the browser in data/headlines.json['all'].)")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    files = {
        "meta.json": {"periods": PERIODS, "weekdays": WEEKDAYS, "owners": OWNERS},
        "monthly.json": build_monthly(),
        "heatmap.json": build_heatmap(),
        "daylength.json": build_daylength(),
        "headlines.json": build_headlines(),
    }
    for name, payload in files.items():
        path = OUT_DIR / name
        path.write_text(json.dumps(payload, ensure_ascii=False))
        print(f"wrote {path} ({path.stat().st_size / 1024:.0f} KB)")

    print_ground_truths(files["headlines.json"])


if __name__ == "__main__":
    main()

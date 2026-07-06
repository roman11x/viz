"""prep.py — build compact aggregates for the "Two Listeners" site.

Reads DATA/fact_plays_with_genre.csv (event-level, ~180k rows), cuts it to the
2021+ window, splits it into the two periods, and emits every aggregate the
dashboards need as a single embedded object in data.js.

Run:  python prep.py
"""

import json

import pandas as pd

# ---------------------------------------------------------------- constants
# Locked data window and period split (must match the constants in index.html).
WINDOW_START = "2021-01-01"   # drop everything before 2021 (Roman sparse earlier)
UNI_START = "2024-01-01"      # pre_uni = 2021-01..2023-12, university = 2024-01+
PERIODS = ["pre_uni", "university"]
OWNERS = ["Or", "Roman"]

FACT_CSV = "DATA/fact_plays_with_genre.csv"
OUT_JS = "data.js"

TOP_ARTISTS_N = 15        # top artists per owner+period cut
GENRE_ARTISTS_N = 8       # artists listed under each genre (backs genre->artist filter)
SHARED_LIST_N = 15        # top shared artists shown by name
WINDOW_TOP_ARTISTS = 5    # per heatmap cell
WINDOW_TOP_GENRES = 3     # per heatmap cell


# ---------------------------------------------------------------- load + cut
def load_fact():
    df = pd.read_csv(
        FACT_CSV,
        usecols=["owner", "date", "weekday", "hour_local", "artist",
                 "minutes_played", "under_30s", "genre"],
    )
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= WINDOW_START].copy()
    df["period"] = df["date"].map(
        lambda d: "university" if d >= pd.Timestamp(UNI_START) else "pre_uni")
    df["ym"] = df["date"].dt.strftime("%Y-%m")
    df["hour_local"] = df["hour_local"].astype(int)
    df["under_30s"] = df["under_30s"].astype(str).eq("True")
    df["genre"] = df["genre"].fillna("Other")
    return df


def cuts(df):
    """The three analysis cuts: whole 2021+ window plus the two periods."""
    yield "all", df
    for p in PERIODS:
        yield p, df[df["period"] == p]


# ---------------------------------------------------------------- aggregates
def owner_kpis(df):
    out = {}
    for cut, d in cuts(df):
        out[cut] = {}
        for owner in OWNERS:
            g = d[d["owner"] == owner]
            minutes = g["minutes_played"].sum()
            by_artist = g.groupby("artist")["minutes_played"].sum().sort_values(ascending=False)
            out[cut][owner] = {
                "hours": round(minutes / 60, 1),
                "plays": int(len(g)),
                "unique_artists": int(g["artist"].nunique()),
                "top_artist": by_artist.index[0],
                "top_artist_share": round(by_artist.iloc[0] / minutes * 100, 1),
                "top5_share": round(by_artist.head(5).sum() / minutes * 100, 1),
                "top10_share": round(by_artist.head(10).sum() / minutes * 100, 1),
                "under_30s_pct": round(g["under_30s"].mean() * 100, 1),
            }
    return out


def genre_composition(df):
    out = {}
    for cut, d in cuts(df):
        out[cut] = {}
        for owner in OWNERS:
            g = d[d["owner"] == owner]
            total = g["minutes_played"].sum()
            rows = []
            for genre, gg in g.groupby("genre"):
                minutes = gg["minutes_played"].sum()
                top = gg.groupby("artist")["minutes_played"].sum().idxmax()
                rows.append({"genre": genre, "minutes": round(minutes, 1),
                             "pct": round(minutes / total * 100, 1), "top_artist": top})
            rows.sort(key=lambda r: -r["minutes"])
            out[cut][owner] = rows
    return out


def artist_tables(df, shared_set):
    """Top artists per owner+cut, and top artists per genre (for genre filtering)."""
    top, by_genre = {}, {}
    for cut, d in cuts(df):
        top[cut], by_genre[cut] = {}, {}
        for owner in OWNERS:
            g = d[d["owner"] == owner]
            total = g["minutes_played"].sum()
            agg = (g.groupby("artist")
                    .agg(minutes=("minutes_played", "sum"), plays=("artist", "size"),
                         genre=("genre", "first"),
                         first_played=("date", "min"), last_played=("date", "max"))
                    .sort_values("minutes", ascending=False))
            top[cut][owner] = [{
                "artist": a, "minutes": round(r.minutes, 1), "plays": int(r.plays),
                "share": round(r.minutes / total * 100, 1), "genre": r.genre,
                "shared": a in shared_set,
                "first_played": str(r.first_played.date()),
                "last_played": str(r.last_played.date()),
            } for a, r in agg.head(TOP_ARTISTS_N).iterrows()]
            by_genre[cut][owner] = {
                genre: [{"artist": a, "minutes": round(m, 1),
                         "share": round(m / total * 100, 1), "shared": a in shared_set}
                        for a, m in gg["minutes"].head(GENRE_ARTISTS_N).items()]
                for genre, gg in agg.groupby("genre", sort=False)}
    return top, by_genre


def shared_overlap(df):
    """Minutes-weighted overlap. 'Shared' = artist name present in BOTH owners'
    2021+ histories (even one play) — which is exactly why we weight by minutes."""
    sets = {o: set(df[df["owner"] == o]["artist"].unique()) for o in OWNERS}
    shared_set = sets["Or"] & sets["Roman"]

    pct = {}
    for cut, d in cuts(df):
        pct[cut] = {}
        for owner in OWNERS:
            g = d[d["owner"] == owner]
            total = g["minutes_played"].sum()
            on_shared = g[g["artist"].isin(shared_set)]["minutes_played"].sum()
            pct[cut][owner] = round(on_shared / total * 100, 1)

    per_owner = (df[df["artist"].isin(shared_set)]
                 .groupby(["artist", "owner"])["minutes_played"].sum().unstack(fill_value=0))
    per_owner["total"] = per_owner.sum(axis=1)
    top_shared = [{"artist": a, "or_minutes": round(r["Or"], 1),
                   "roman_minutes": round(r["Roman"], 1)}
                  for a, r in per_owner.sort_values("total", ascending=False)
                                       .head(SHARED_LIST_N).iterrows()]
    return {"count": len(shared_set), "pct_minutes": pct, "top_shared": top_shared}, shared_set


def monthly_hours(df):
    agg = df.groupby(["owner", "ym"]).agg(
        minutes=("minutes_played", "sum"), plays=("owner", "size"))
    return {owner: [{"ym": ym, "hours": round(r.minutes / 60, 1), "plays": int(r.plays)}
                    for (o, ym), r in agg.iterrows() if o == owner]
            for owner in OWNERS}


def heatmaps(df):
    """weekday x hour plays per owner+period; pct normalized within owner+period."""
    out = {}
    for p in PERIODS:
        out[p] = {}
        for owner in OWNERS:
            g = df[(df["period"] == p) & (df["owner"] == owner)]
            total = len(g)
            cells = g.groupby(["weekday", "hour_local"]).size()
            out[p][owner] = [{"weekday": wd, "hour": int(h), "plays": int(n),
                              "pct": round(n / total * 100, 2)}
                             for (wd, h), n in cells.items()]
    return out


def routine_windows(df):
    """Per (period, owner, weekday, hour): totals + top artists/genres for the
    heatmap-cell drilldown. Keyed 'period|owner|weekday|hour' for O(1) lookup."""
    out = {}
    for (p, owner, wd, h), g in df.groupby(["period", "owner", "weekday", "hour_local"]):
        top_a = g.groupby("artist")["minutes_played"].sum().nlargest(WINDOW_TOP_ARTISTS)
        top_g = g.groupby("genre")["minutes_played"].sum().nlargest(WINDOW_TOP_GENRES)
        out[f"{p}|{owner}|{wd}|{int(h)}"] = {
            "plays": int(len(g)), "minutes": round(g["minutes_played"].sum(), 1),
            "top_artists": [[a, round(m, 1)] for a, m in top_a.items()],
            "top_genres": [[ge, round(m, 1)] for ge, m in top_g.items()],
        }
    return out


def change_metrics(df, kpis):
    """Averages/rates for the slope chart — periods differ in length, so divide
    by the number of calendar months each period actually covers in the data."""
    months = {p: int(df[df["period"] == p]["ym"].nunique()) for p in PERIODS}
    out = {}
    for owner in OWNERS:
        out[owner] = {p: {
            "avg_monthly_hours": round(kpis[p][owner]["hours"] / months[p], 1),
            "under_30s_pct": kpis[p][owner]["under_30s_pct"],
        } for p in PERIODS}
    return out, months


# ---------------------------------------------------------------- main
def main():
    df = load_fact()

    shared, shared_set = shared_overlap(df)
    kpis = owner_kpis(df)
    genres = genre_composition(df)
    top_artists, genre_artists = artist_tables(df, shared_set)
    data = {
        "meta": {
            "window_start": WINDOW_START, "uni_start": UNI_START,
            "periods": PERIODS, "owners": OWNERS,
            "last_month": df["ym"].max(),
        },
        "kpis": kpis,
        "genres": genres,
        "top_artists": top_artists,
        "genre_artists": genre_artists,
        "shared": shared,
        "monthly": monthly_hours(df),
        "heatmap": heatmaps(df),
        "routine_window": routine_windows(df),
    }
    data["change"], months = change_metrics(df, kpis)
    data["meta"]["months_per_period"] = months

    js = "const EMBEDDED_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write(js)

    # ------------------------------------------------------------ verification
    print(f"window: {WINDOW_START}+  |  university starts {UNI_START}")
    print(f"rows in window: {len(df):,}  |  months per period: {months}")
    print(f"wrote {OUT_JS}: {len(js)/1024:.0f} KB\n")

    for cut in ["all", *PERIODS]:
        print(f"-- {cut}")
        for o in OWNERS:
            k = kpis[cut][o]
            print(f"  {o:6} {k['hours']:8,.1f} h  {k['plays']:7,} plays  "
                  f"{k['unique_artists']:5,} artists  top={k['top_artist']} "
                  f"({k['top_artist_share']}%)  top10={k['top10_share']}%  "
                  f"under30s={k['under_30s_pct']}%")

    print("\n-- consistency: pre_uni + university == all")
    for o in OWNERS:
        for m in ["hours", "plays"]:
            parts = kpis["pre_uni"][o][m] + kpis["university"][o][m]
            whole = kpis["all"][o][m]
            ok = abs(parts - whole) < (0.2 if m == "hours" else 1)
            print(f"  {o:6} {m:6} {parts:,.1f} vs {whole:,.1f}  {'OK' if ok else 'MISMATCH'}")

    print("\n-- genre composition (all, % of owner minutes; genre is EXTERNAL/partial)")
    for o in OWNERS:
        row = ", ".join(f"{g['genre']} {g['pct']}%" for g in genres["all"][o][:6])
        other = next((g["pct"] for g in genres["all"][o] if g["genre"] == "Other"), 0)
        print(f"  {o:6} {row}  |  Other={other}%")

    print(f"\n-- shared artists (2021+ window): {shared['count']}")
    for cut in ["all", *PERIODS]:
        p = shared["pct_minutes"][cut]
        print(f"  {cut:10} minutes-weighted shared share: Or {p['Or']}%  Roman {p['Roman']}%")
    print("  top shared:", ", ".join(a["artist"] for a in shared["top_shared"][:8]))

    print("\n-- change metrics (avg monthly hours / under_30s%)")
    for o in OWNERS:
        c = data["change"][o]
        print(f"  {o:6} hours {c['pre_uni']['avg_monthly_hours']} -> "
              f"{c['university']['avg_monthly_hours']}   "
              f"under30s {c['pre_uni']['under_30s_pct']}% -> {c['university']['under_30s_pct']}%")


if __name__ == "__main__":
    main()

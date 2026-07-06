"""prep.py — build compact aggregates for the "Two Listeners" dashboards.

Reads DATA/fact_plays_with_genre.csv (event-level, ~180k rows), cuts it to the
2021+ window, splits it into the two periods, collapses external genres into
broad FAMILIES, and emits everything the page needs as one EMBEDDED_DATA
object in data.js.

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

TOP_ARTISTS_N = 15        # top artists per owner+cut (dot-plot shows 10)
FAMILY_ARTISTS_N = 8      # artists listed per family (backs the genre->artist filter)
SHARED_LIST_N = 15        # top shared artists shown by name
WINDOW_TOP_ARTISTS = 5    # per heatmap cell
WINDOW_TOP_FAMILIES = 3   # per heatmap cell

# ---------------------------------------------------------------- genre families
# The external fine genres collapse into ~6 broad families for display.
# Genre remains external/provisional; "Other" stays as the honest residual.
FAMILY_OF_GENRE = {
    "Pop": "Pop", "Pop Rock": "Pop", "Indie/Alt Pop": "Pop", "K/J-Pop": "Pop",
    "Singer-Songwriter": "Pop",
    "Rock": "Rock", "Alternative Rock": "Rock", "Hard Rock": "Rock", "Post-Grunge": "Rock",
    "Israeli Pop": "Israeli", "Israeli Rock": "Israeli", "World/Israeli": "Israeli",
    "Mizrahi": "Israeli",
    "Metal": "Metal", "Metalcore": "Metal", "Nu Metal": "Metal",
    "Electronic/Dance": "Electronic/Dance",
    "Hip-Hop": "Hip-Hop/R&B", "R&B/Soul": "Hip-Hop/R&B",
    "Latin": "Other", "Soundtrack": "Other", "Other": "Other",
}

# Curated extension for the TOP artists that the external map left as "Other".
# Only artists identified confidently are listed; everything uncertain stays
# "Other" (e.g. UPIKO, Parallyx, Black Spikes, LoFi Tokyo, Poppy).
ARTIST_FAMILY = {
    # Roman's unclassified tail — overwhelmingly metal/metalcore/deathcore acts
    "Gojira": "Metal", "Humanity's Last Breath": "Metal", "Currents": "Metal",
    "Ice Nine Kills": "Metal", "Jinjer": "Metal", "TesseracT": "Metal",
    "Bury Tomorrow": "Metal", "The Plot In You": "Metal", "Silent Planet": "Metal",
    "Lorna Shore": "Metal", "Kingdom Of Giants": "Metal", "Atreyu": "Metal",
    "As Everything Unfolds": "Metal", "Distant": "Metal", "Ankor": "Metal",
    "Will Ramos": "Metal", "Darko US": "Metal", "Elwood Stray": "Metal",
    "Samurai Pizza Cats": "Metal", "Rain Paris": "Metal", "Crossfaith": "Metal",
    "Invent Animate": "Metal", "Ghost": "Metal", "Tetrarch": "Metal",
    "Make Them Suffer": "Metal", "Kanonenfieber": "Metal", "Papa Roach": "Metal",
    "Wage War": "Metal", "Skindred": "Metal", "TOOL": "Metal",
    "Fit For An Autopsy": "Metal", "In Flames": "Metal", "We Came As Romans": "Metal",
    "Slipknot": "Metal", "Bad Omens": "Metal", "Avenged Sevenfold": "Metal",
    "Eluveitie": "Metal", "After The Burial": "Metal", "The Devil Wears Prada": "Metal",
    "Wind Rose": "Metal", "Miss May I": "Metal", "Hacktivist": "Metal",
    "Morphide": "Metal", "花冷え。": "Metal", "Shrine of Malice": "Metal",
    "Future Palace": "Metal", "ERRA": "Metal", "Unprocessed": "Metal",
    "My Chemical Romance": "Rock", "Thousand Foot Krutch": "Rock",
    "Dead By Sunrise": "Rock", "Seether": "Rock", "Trapt": "Rock",
    "Nine Lashes": "Rock", "All Time Low": "Rock", "Chevelle": "Rock",
    "Mike Shinoda": "Rock",
    "Twenty One Pilots": "Pop", "Maggie Lindemann": "Pop",
    "IRyS": "Pop", "Kobo Kanaeru": "Pop", "ファントムシータ": "Pop",
    "X-Ecutioners": "Hip-Hop/R&B",
    # Or's unclassified tail — mainstream pop / rock / dance and Israeli acts
    "Michael Jackson": "Pop", "Sam Smith & Labrinth": "Pop", "Sam Smith & Normani": "Pop",
    "Katy Perry": "Pop", "Miley Cyrus": "Pop", "George Ezra": "Pop",
    "Jonas Brothers": "Pop", "Mark Ronson": "Pop", "Dean Lewis": "Pop",
    "Olivia Rodrigo": "Pop", "Kodaline": "Pop", "Johnny Balik": "Pop",
    "Michael Jackson & Justin Timberlake": "Pop",
    "Rihanna and Kanye West and Paul McCartney": "Pop",
    "Imagine Dragons & JID": "Pop",
    "The Beatles": "Rock", "Paul Simon": "Rock", "KALEO": "Rock", "The Band": "Rock",
    "Nicki Minaj": "Hip-Hop/R&B", "Rihanna": "Hip-Hop/R&B",
    "Macklemore & Tones And I": "Hip-Hop/R&B",
    "Joel Corry": "Electronic/Dance", "Calvin Harris, Sam Smith": "Electronic/Dance",
    "The Chainsmokers & Coldplay": "Electronic/Dance",
    "Eden Alene": "Israeli", "Raviv Kaner": "Israeli", "Asaf Avidan & The Mojos": "Israeli",
    "Static & Ben El": "Israeli",
}


def has_hebrew(s):
    """Hebrew script in the artist name is a reliable 'Israeli' signal."""
    return any("֐" <= ch <= "׿" for ch in str(s))


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

    # genre -> family: collapse fine genres, then rescue top "Other" artists via
    # the curated map and the Hebrew-script rule; the uncertain rest stays Other
    fam = df["genre"].fillna("Other").map(FAMILY_OF_GENRE).fillna("Other")
    curated = df["artist"].map(ARTIST_FAMILY)
    hebrew = df["artist"].map(has_hebrew)
    df["family"] = fam.where(fam != "Other", curated.fillna("Other"))
    df.loc[(df["family"] == "Other") & hebrew, "family"] = "Israeli"
    df["raw_other"] = fam.eq("Other") & df["genre"].fillna("Other").eq("Other")
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
            daily = g.groupby("date")["minutes_played"].sum()
            out[cut][owner] = {
                "hours": round(minutes / 60, 1),
                "plays": int(len(g)),
                "unique_artists": int(g["artist"].nunique()),
                "top_artist": by_artist.index[0],
                "top_artist_share": round(by_artist.iloc[0] / minutes * 100, 1),
                "top10_share": round(by_artist.head(10).sum() / minutes * 100, 1),
                "active_days": int(len(daily)),
                "median_daily_min": round(float(daily.median()), 1),
                "peak_hour": int(g.groupby("hour_local").size().idxmax()),
            }
    return out


def family_composition(df):
    out = {}
    for cut, d in cuts(df):
        out[cut] = {}
        for owner in OWNERS:
            g = d[d["owner"] == owner]
            total = g["minutes_played"].sum()
            rows = []
            for family, gg in g.groupby("family"):
                minutes = gg["minutes_played"].sum()
                top = gg.groupby("artist")["minutes_played"].sum().idxmax()
                rows.append({"family": family, "minutes": round(minutes, 1),
                             "pct": round(minutes / total * 100, 1), "top_artist": top})
            rows.sort(key=lambda r: -r["minutes"])
            out[cut][owner] = rows
    return out


def artist_tables(df, shared_set):
    """Top artists per owner+cut, and top artists per family (for the genre filter)."""
    top, by_family = {}, {}
    for cut, d in cuts(df):
        top[cut], by_family[cut] = {}, {}
        for owner in OWNERS:
            g = d[d["owner"] == owner]
            total = g["minutes_played"].sum()
            agg = (g.groupby("artist")
                    .agg(minutes=("minutes_played", "sum"), plays=("artist", "size"),
                         family=("family", "first"),
                         first_played=("date", "min"), last_played=("date", "max"))
                    .sort_values("minutes", ascending=False))
            top[cut][owner] = [{
                "artist": a, "minutes": round(r.minutes, 1), "plays": int(r.plays),
                "share": round(r.minutes / total * 100, 1), "family": r.family,
                "shared": a in shared_set,
                "first_played": str(r.first_played.date()),
                "last_played": str(r.last_played.date()),
            } for a, r in agg.head(TOP_ARTISTS_N).iterrows()]
            by_family[cut][owner] = {
                family: [{"artist": a, "minutes": round(m, 1),
                          "share": round(m / total * 100, 1), "shared": a in shared_set}
                         for a, m in gg["minutes"].head(FAMILY_ARTISTS_N).items()]
                for family, gg in agg.groupby("family", sort=False)}
    return top, by_family


def shared_overlap(df):
    """Minutes-weighted overlap. 'Shared' now requires REAL listening on both
    sides: at least one over-30-seconds play by each person (this drops
    name-only matches where one side has 0 meaningful minutes)."""
    real = df[~df["under_30s"]]
    real_sets = {o: set(real[real["owner"] == o]["artist"].unique()) for o in OWNERS}
    name_sets = {o: set(df[df["owner"] == o]["artist"].unique()) for o in OWNERS}
    shared_set = real_sets["Or"] & real_sets["Roman"]
    name_only = len(name_sets["Or"] & name_sets["Roman"])

    pct = {}
    for cut, d in cuts(df):
        pct[cut] = {}
        for owner in OWNERS:
            g = d[d["owner"] == owner]
            total = g["minutes_played"].sum()
            on_shared = g[g["artist"].isin(shared_set)]["minutes_played"].sum()
            pct[cut][owner] = round(on_shared / total * 100, 1)

    top_shared = {}
    for c, d in cuts(df):
        per_owner = (d[d["artist"].isin(shared_set)]
                     .groupby(["artist", "owner"])["minutes_played"].sum().unstack(fill_value=0)
                     .reindex(columns=OWNERS, fill_value=0))
        per_owner["total"] = per_owner.sum(axis=1)
        top_shared[c] = [{"artist": a, "or_minutes": round(r["Or"], 1),
                          "roman_minutes": round(r["Roman"], 1)}
                         for a, r in per_owner.sort_values("total", ascending=False)
                                              .head(SHARED_LIST_N).iterrows()]
    return {"count": len(shared_set), "name_matches": name_only,
            "pct_minutes": pct, "top_shared": top_shared}, shared_set


def monthly_hours(df):
    agg = df.groupby(["owner", "ym"]).agg(
        minutes=("minutes_played", "sum"), plays=("owner", "size"))
    return {owner: [{"ym": ym, "hours": round(r.minutes / 60, 1), "plays": int(r.plays)}
                    for (o, ym), r in agg.iterrows() if o == owner]
            for owner in OWNERS}


def heatmaps(df):
    """weekday x hour plays per owner+period (absolute plays only)."""
    out = {}
    for p in PERIODS:
        out[p] = {}
        for owner in OWNERS:
            g = df[(df["period"] == p) & (df["owner"] == owner)]
            cells = g.groupby(["weekday", "hour_local"]).size()
            out[p][owner] = [{"weekday": wd, "hour": int(h), "plays": int(n)}
                             for (wd, h), n in cells.items()]
    return out


def daily_minutes(df):
    """Minutes listened per ACTIVE day, per owner+period — backs the histogram."""
    out = {}
    for p in PERIODS:
        out[p] = {}
        for owner in OWNERS:
            g = df[(df["period"] == p) & (df["owner"] == owner)]
            daily = g.groupby("date")["minutes_played"].sum()
            out[p][owner] = [int(round(v)) for v in daily.values if v > 0]
    return out


def routine_windows(df):
    """Per (period, owner, weekday, hour): totals + top artists/families for the
    heatmap-cell drilldown. Keyed 'period|owner|weekday|hour' for O(1) lookup."""
    out = {}
    for (p, owner, wd, h), g in df.groupby(["period", "owner", "weekday", "hour_local"]):
        top_a = g.groupby("artist")["minutes_played"].sum().nlargest(WINDOW_TOP_ARTISTS)
        top_f = g.groupby("family")["minutes_played"].sum().nlargest(WINDOW_TOP_FAMILIES)
        out[f"{p}|{owner}|{wd}|{int(h)}"] = {
            "plays": int(len(g)), "minutes": round(g["minutes_played"].sum(), 1),
            "top_artists": [[a, round(m, 1)] for a, m in top_a.items()],
            "top_families": [[f, round(m, 1)] for f, m in top_f.items()],
        }
    return out


# ---------------------------------------------------------------- main
def main():
    df = load_fact()

    shared, shared_set = shared_overlap(df)
    kpis = owner_kpis(df)
    families = family_composition(df)
    top_artists, family_artists = artist_tables(df, shared_set)
    months = {p: int(df[df["period"] == p]["ym"].nunique()) for p in PERIODS}
    change = {o: {p: {"avg_monthly_hours": round(kpis[p][o]["hours"] / months[p], 1)}
                  for p in PERIODS} for o in OWNERS}

    data = {
        "meta": {
            "window_start": WINDOW_START, "uni_start": UNI_START,
            "periods": PERIODS, "owners": OWNERS,
            "last_month": df["ym"].max(), "months_per_period": months,
            # calendar days per period (university runs to the last observed date)
            "period_days": {
                "pre_uni": (pd.Timestamp(UNI_START) - pd.Timestamp(WINDOW_START)).days,
                "university": (df["date"].max() - pd.Timestamp(UNI_START)).days + 1,
            },
        },
        "kpis": kpis,
        "families": families,
        "top_artists": top_artists,
        "family_artists": family_artists,
        "shared": shared,
        "monthly": monthly_hours(df),
        "heatmap": heatmaps(df),
        "daily": daily_minutes(df),
        "routine_window": routine_windows(df),
        "change": change,
    }

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
                  f"({k['top_artist_share']}%)  active_days={k['active_days']:,}  "
                  f"median_day={k['median_daily_min']} min  peak_hour={k['peak_hour']}:00")

    print("\n-- consistency: pre_uni + university == all")
    for o in OWNERS:
        for m in ["hours", "plays"]:
            parts = kpis["pre_uni"][o][m] + kpis["university"][o][m]
            whole = kpis["all"][o][m]
            ok = abs(parts - whole) < (0.2 if m == "hours" else 1)
            print(f"  {o:6} {m:6} {parts:,.1f} vs {whole:,.1f}  {'OK' if ok else 'MISMATCH'}")

    print("\n-- genre FAMILY composition (all, % of owner minutes; external/provisional)")
    raw_other = {o: round(df[(df.owner == o) & df.raw_other]["minutes_played"].sum()
                          / df[df.owner == o]["minutes_played"].sum() * 100, 1) for o in OWNERS}
    for o in OWNERS:
        row = ", ".join(f"{g['family']} {g['pct']}%" for g in families["all"][o])
        fam_other = next((g["pct"] for g in families["all"][o] if g["family"] == "Other"), 0)
        print(f"  {o:6} {row}")
        print(f"         'Other' residual: {fam_other}%  (was {raw_other[o]}% before family collapse + curation)")

    print(f"\n-- shared artists: {shared['count']} with real listening on both sides "
          f"(name-only matches in window: {shared['name_matches']})")
    for cut in ["all", *PERIODS]:
        p = shared["pct_minutes"][cut]
        print(f"  {cut:10} minutes-weighted shared share: Or {p['Or']}%  Roman {p['Roman']}%")
    print("  top shared:", ", ".join(a["artist"] for a in shared["top_shared"]["all"][:8]))

    print("\n-- avg monthly hours (for the bridge sentence)")
    for o in OWNERS:
        print(f"  {o:6} {change[o]['pre_uni']['avg_monthly_hours']} -> "
              f"{change[o]['university']['avg_monthly_hours']} h/mo")


if __name__ == "__main__":
    main()

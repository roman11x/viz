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
# 2026-05 is a PARTIAL month (exports stop 2026-05-22 for Or, 2026-05-10 for
# Roman) — dropped whole on the owner's instruction 2026-07-20 so the last
# plotted month is never an artificially quiet one.
WINDOW_END_EXCL = "2026-05-01"
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
CELL_TOP_ARTISTS = 3      # per (weekday, hour, month) cell in monthly_detail
SHARED_MIN_MINUTES = 3    # per listener, per cut

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
# "Other" (e.g. UPIKO, LoFi Tokyo, Killabite Media).
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
    "Black Sabbath": "Metal", "Asking Alexandria": "Metal", "Apocalyptica": "Metal",
    "Bodysnatcher": "Metal", "Utsu-P": "Metal", "Conquer Divide": "Metal",
    "Cursed Earth": "Metal", "Windrunner": "Metal", "Her Last Sight": "Metal",
    "Vended": "Metal", "Bloodywood": "Metal", "Dayseeker": "Metal",
    "Monuments": "Metal", "Paleface Swiss": "Metal", "Norma Jean": "Metal",
    "NOVELISTS": "Metal", "Solence": "Metal", "Dropout Kings": "Metal",
    "Poppy": "Metal", "PassCode": "Metal", "Our Demise": "Metal", "VEXED": "Metal",
    "Alpha Wolf": "Metal", "156/Silence": "Metal", "Oceans Ate Alaska": "Metal",
    "Thornhill": "Metal", "Trivium": "Metal", "Nik Nocturnal": "Metal",
    "The Narrator": "Metal", "Korn": "Metal", "Within Temptation": "Metal",
    "Architects": "Metal", "The Browning": "Metal", "Cane Hill": "Metal",
    "Imminence": "Metal", "Sentinels": "Metal", "August Burns Red": "Metal",
    "Future Static": "Metal", "Bleed From Within": "Metal", "Orbit Culture": "Metal",
    "Aviana": "Metal", "Shadow of Intent": "Metal", "All That Remains": "Metal",
    "Like Moths To Flames": "Metal", "Fit For A King": "Metal", "Parkway Drive": "Metal",
    "Lacuna Coil": "Metal", "Allt": "Metal", "The John Candy": "Metal",
    "Disembodied Tyrant": "Metal", "Memphis May Fire": "Metal", "System Of A Down": "Metal",
    "Terminal Sleep": "Metal", "Bullet For My Valentine": "Metal", "Downswing": "Metal",
    "Parallyx": "Metal", "Black Spikes": "Metal", "Mirar": "Metal", "Cenobia": "Metal",
    "Gore.": "Metal", "Dal Av": "Metal", "SFINX": "Metal", "IAMONE": "Metal",
    "Maphra": "Metal", "Daedric": "Metal",
    "My Chemical Romance": "Rock", "Thousand Foot Krutch": "Rock",
    "Dead By Sunrise": "Rock", "Seether": "Rock", "Trapt": "Rock",
    "Nine Lashes": "Rock", "All Time Low": "Rock", "Chevelle": "Rock",
    "Mike Shinoda": "Rock", "Fame on Fire": "Rock", "Billy Talent": "Rock",
    "My Darkest Days": "Rock", "BAND-MAID": "Rock", "Sum 41": "Rock",
    "Pierce The Veil": "Rock", "Escape the Fate": "Rock", "Green Day": "Rock",
    "NOTHING MORE": "Rock", "Egypt Central": "Rock", "10 Years": "Rock",
    "Red Hot Chili Peppers": "Rock", "Discrepancies": "Rock", "EarlyRise": "Rock",
    "Shinedown": "Rock", "The All-American Rejects": "Rock", "Finger Eleven": "Rock",
    "Volbeat": "Rock", "The Pretty Reckless": "Rock", "Fireflight": "Rock",
    "Thirty Seconds To Mars": "Rock", "Staind": "Rock",
    "Twenty One Pilots": "Pop", "Maggie Lindemann": "Pop",
    "IRyS": "Pop", "Kobo Kanaeru": "Pop", "ファントムシータ": "Pop", "BLACKPINK": "Pop",
    "Shakira": "Pop", "KAROL G": "Pop", "Abor & Tynna": "Pop",
    "X-Ecutioners": "Hip-Hop/R&B",
    # Or's unclassified tail — mainstream pop / rock / dance and Israeli acts
    "Michael Jackson": "Pop", "Sam Smith & Labrinth": "Pop", "Sam Smith & Normani": "Pop",
    "Katy Perry": "Pop", "Miley Cyrus": "Pop", "George Ezra": "Pop",
    "Jonas Brothers": "Pop", "Mark Ronson": "Pop", "Dean Lewis": "Pop",
    "Olivia Rodrigo": "Pop", "Kodaline": "Pop", "Johnny Balik": "Pop",
    "Michael Jackson & Justin Timberlake": "Pop",
    "Rihanna and Kanye West and Paul McCartney": "Pop",
    "Imagine Dragons & JID": "Pop",
    "Justin Bieber": "Pop", "Ed Sheeran & Justin Bieber": "Pop", "GAYLE": "Pop",
    "The Vamps": "Pop", "Lady Gaga": "Pop", "TeenAngels": "Pop",
    "Cyndi Lauper": "Pop", "SHAED": "Pop", "MKTO": "Pop",
    "Lady Gaga & Ariana Grande": "Pop", "Coldplay & Rihanna": "Pop",
    "James Smith": "Pop", "Sonny & Cher": "Pop",
    "Troy & Gabriella": "Pop", "The Cast of High School Musical": "Pop",
    "The Cast of High School Musical, Vanessa Hudgens, Lucas Grabeel, Zac Efron & Olesya Rulin": "Pop",
    "Demi Lovato": "Pop", "Frank Sinatra": "Pop", "Johnny Nash": "Pop",
    "The Four Seasons": "Pop", "One Direction": "Pop", "Lady Gaga & Bruno Mars": "Pop",
    "Matt Simons": "Pop", "The 5th Dimension": "Pop", "Elton John": "Pop",
    "Lola Marsh": "Pop", "The Monkees": "Pop", "James Arthur": "Pop",
    "Dion": "Pop", "Natalie Taylor": "Pop", "Gracie Abrams": "Pop",
    "Lesley Gore": "Pop", "Frankie Valli": "Pop", "Surfaces": "Pop",
    "Lola Young": "Pop", "LunchMoney Lewis": "Pop", "Dusty Springfield": "Pop",
    "Sam Smith & Kim Petras": "Pop",
    "The Beatles": "Rock", "Paul Simon": "Rock", "KALEO": "Rock", "The Band": "Rock",
    "YUNGBLUD": "Rock", "Roy Orbison": "Rock", "Family of the Year": "Rock",
    "Of Monsters and Men": "Rock", "The Mamas & The Papas": "Rock",
    "The Beach Boys": "Rock", "The Rolling Stones": "Rock", "Procol Harum": "Rock",
    "Elvis Presley": "Rock", "The Byrds": "Rock", "Bruce Springsteen": "Rock",
    "The Hollies": "Rock", "Manfred Mann": "Rock", "The Everly Brothers": "Rock",
    "Tommy James & The Shondells": "Rock", "Electric Light Orchestra": "Rock",
    "Nicki Minaj": "Hip-Hop/R&B", "Rihanna": "Hip-Hop/R&B",
    "Macklemore & Tones And I": "Hip-Hop/R&B", "Jacob Banks": "Hip-Hop/R&B",
    "SZA & Justin Timberlake": "Hip-Hop/R&B", "Ike & Tina Turner": "Hip-Hop/R&B",
    "Nina Simone": "Hip-Hop/R&B", "Bill Withers": "Hip-Hop/R&B", "Four Tops": "Hip-Hop/R&B",
    "Wild Cherry": "Hip-Hop/R&B", "Aretha Franklin": "Hip-Hop/R&B",
    "James Brown & The Famous Flames": "Hip-Hop/R&B", "Lil Wayne, Wiz Khalifa & Imagine Dragons": "Hip-Hop/R&B",
    "Stevie Wonder": "Hip-Hop/R&B", "The Supremes": "Hip-Hop/R&B",
    "Doja Cat": "Hip-Hop/R&B", "Childish Gambino": "Hip-Hop/R&B", "Marvin Gaye": "Hip-Hop/R&B",
    "The Temptations": "Hip-Hop/R&B", "Alicia Keys": "Hip-Hop/R&B",
    "Sly & The Family Stone": "Hip-Hop/R&B", "Cardi B & Bruno Mars": "Hip-Hop/R&B",
    "GIVĒON": "Hip-Hop/R&B", "Otis Redding": "Hip-Hop/R&B", "Dionne Warwick": "Hip-Hop/R&B",
    "Jackson 5": "Hip-Hop/R&B", "JAY-Z": "Hip-Hop/R&B",
    "Joel Corry": "Electronic/Dance", "Calvin Harris, Sam Smith": "Electronic/Dance",
    "The Chainsmokers & Coldplay": "Electronic/Dance",
    "Major Lazer": "Electronic/Dance", "Zedd, Maren Morris & Grey": "Electronic/Dance",
    "Kygo & Imagine Dragons": "Electronic/Dance", "Rudimental": "Electronic/Dance",
    "David Guetta": "Electronic/Dance", "Marshmello & Bastille": "Electronic/Dance",
    "Marshmello & Anne-Marie": "Electronic/Dance", "Disclosure": "Electronic/Dance",
    "Sam Feldt & Tones And I": "Electronic/Dance", "MEDUZA & Goodboys": "Electronic/Dance",
    "David Guetta & Sia": "Electronic/Dance", "Felix Jaehn, Hight & Alex Aiono": "Electronic/Dance",
    "ILLENIUM": "Electronic/Dance", "Jesus Jackson": "Electronic/Dance",
    "Eden Alene": "Israeli", "Raviv Kaner": "Israeli", "Asaf Avidan & The Mojos": "Israeli",
    "Static & Ben El": "Israeli", "Noga Erez": "Israeli", "Kobi Marimi": "Israeli",
    "Asaf Avidan": "Israeli", "Balkan Beat Box": "Israeli", "Eliana Tidhar & Tuval Shafir": "Israeli",
    "Idan Shneor": "Israeli", "Lama Lo": "Israeli", "DJ Malka": "Israeli",
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
    df = df[(df["date"] >= WINDOW_START) & (df["date"] < WINDOW_END_EXCL)].copy()
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
                # comparable across services (computed identically from ms_played);
                # never use the native skip counters
                "under30_pct": round(g["under_30s"].mean() * 100, 1),
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
    """Minutes-weighted overlap. 'Shared' requires real listening and enough minutes."""
    name_sets = {o: set(df[df["owner"] == o]["artist"].unique()) for o in OWNERS}
    name_only = len(name_sets["Or"] & name_sets["Roman"])

    def shared_for(d):
        real = d[~d["under_30s"]]
        real_sets = {o: set(real[real["owner"] == o]["artist"].unique()) for o in OWNERS}
        per_owner = (d.groupby(["artist", "owner"])["minutes_played"].sum()
                     .unstack(fill_value=0).reindex(columns=OWNERS, fill_value=0))
        over_threshold = set(per_owner[(per_owner["Or"] >= SHARED_MIN_MINUTES)
                                       & (per_owner["Roman"] >= SHARED_MIN_MINUTES)].index)
        return over_threshold & real_sets["Or"] & real_sets["Roman"]

    shared_by_cut = {cut: shared_for(d) for cut, d in cuts(df)}
    shared_set = shared_by_cut["all"]

    pct = {}
    for cut, d in cuts(df):
        pct[cut] = {}
        cut_shared = shared_by_cut[cut]
        for owner in OWNERS:
            g = d[d["owner"] == owner]
            total = g["minutes_played"].sum()
            on_shared = g[g["artist"].isin(cut_shared)]["minutes_played"].sum()
            pct[cut][owner] = round(on_shared / total * 100, 1)

    top_shared = {}
    for c, d in cuts(df):
        cut_shared = shared_by_cut[c]
        if not cut_shared:
            top_shared[c] = []
            continue
        per_owner = (d[d["artist"].isin(cut_shared)]
                     .groupby(["artist", "owner"])["minutes_played"].sum().unstack(fill_value=0)
                     .reindex(columns=OWNERS, fill_value=0))
        per_owner["total"] = per_owner.sum(axis=1)
        top_shared[c] = [{"artist": a, "or_minutes": round(r["Or"], 1),
                          "roman_minutes": round(r["Roman"], 1)}
                         for a, r in per_owner.sort_values("total", ascending=False)
                                              .head(SHARED_LIST_N).iterrows()]
    # Every name-matched artist with both-side minutes and the "real listening"
    # flags, per cut — lets the page recompute the shared set CLIENT-SIDE for an
    # arbitrary minutes threshold (the A3 sensitivity slider). At the default
    # threshold the client formula must reproduce count_by_cut/pct_minutes
    # exactly; verify_dashboard.py asserts that.
    overlap_artists = {}
    for cut, d in cuts(df):
        real = d[~d["under_30s"]]
        real_sets = {o: set(real[real["owner"] == o]["artist"].unique()) for o in OWNERS}
        per_owner = (d.groupby(["artist", "owner"])["minutes_played"].sum()
                     .unstack(fill_value=0).reindex(columns=OWNERS, fill_value=0))
        both = per_owner[(per_owner["Or"] > 0) & (per_owner["Roman"] > 0)]
        overlap_artists[cut] = [{
            "artist": a,
            "or_minutes": round(r["Or"], 2), "roman_minutes": round(r["Roman"], 2),
            "or_real": a in real_sets["Or"], "roman_real": a in real_sets["Roman"],
        } for a, r in both.sort_values("Or", ascending=False).iterrows()]

    return {"count": len(shared_set),
            "count_by_cut": {cut: len(s) for cut, s in shared_by_cut.items()},
            "name_matches": name_only,
            "pct_minutes": pct, "top_shared": top_shared,
            "overlap_artists": overlap_artists}, shared_set


def monthly_hours(df):
    agg = df.groupby(["owner", "ym"]).agg(
        minutes=("minutes_played", "sum"), plays=("owner", "size"))
    return {owner: [{"ym": ym, "hours": round(r.minutes / 60, 1), "plays": int(r.plays)}
                    for (o, ym), r in agg.iterrows() if o == owner]
            for owner in OWNERS}


def heatmaps(df):
    """weekday x hour plays per owner+cut (absolute plays only)."""
    out = {}
    for cut, d in cuts(df):
        out[cut] = {}
        for owner in OWNERS:
            g = d[d["owner"] == owner]
            cells = g.groupby(["weekday", "hour_local"]).size()
            out[cut][owner] = [{"weekday": wd, "hour": int(h), "plays": int(n)}
                               for (wd, h), n in cells.items()]
    return out


def monthly_detail(df):
    """Per-owner, per-month breakdown rich enough to recompute the slopegraph's
    routine/intensity metrics, the heatmap, AND the heatmap-cell drill-down for
    an ARBITRARY custom month range client-side — this is what lets the
    Dashboard-2 range brush genuinely re-filter instead of being limited to the
    three locked cuts (all/pre_uni/university). Still a compact aggregate, not
    the event table: bounded by (weekday, hour, month) triples that actually
    have activity, not raw plays. Each occupied cell carries its per-month
    top-3 artists by minutes (indices into the shared `artists` string table —
    a LOWER BOUND when summed across months, since a month's 4th artist is
    dropped) and its COMPLETE per-family minutes (indices into `families`;
    only ~7 families, so family breakdowns stay exact for any range and their
    sum is the cell's exact total minutes).
    """
    artist_ids = {}

    def aid(a):
        if a not in artist_ids:
            artist_ids[a] = len(artist_ids)
        return artist_ids[a]

    families_list = sorted(df["family"].unique())
    fam_id = {f: i for i, f in enumerate(families_list)}

    out = {}
    for owner in OWNERS:
        g_all = df[df["owner"] == owner]
        by_month = {}
        for ym, gm in g_all.groupby("ym"):
            minutes = gm["minutes_played"].sum()
            daily = gm.groupby("date")["minutes_played"].sum()
            cells = []
            for (wd, h), gc in gm.groupby(["weekday", "hour_local"]):
                # deterministic top-3: minutes desc, then name — so a fresh
                # verify run reproduces the same pick under exact-minute ties
                top = (gc.groupby("artist")["minutes_played"].sum()
                         .reset_index()
                         .sort_values(["minutes_played", "artist"],
                                      ascending=[False, True])
                         .head(CELL_TOP_ARTISTS))
                fams = (gc.groupby("family")["minutes_played"].sum()
                          .sort_values(ascending=False))
                cells.append([
                    wd, int(h), int(len(gc)),
                    [[aid(a), round(m, 1)]
                     for a, m in zip(top["artist"], top["minutes_played"])],
                    [[fam_id[f], round(m, 1)] for f, m in fams.items()],
                ])
            by_month[ym] = {
                "hours": round(minutes / 60, 1),
                "plays": int(len(gm)),
                "under30_plays": int(gm["under_30s"].sum()),
                "active_days": int(len(daily)),
                "heatmap": cells,
            }

        daily_all = g_all.groupby("date")["minutes_played"].sum()
        out[owner] = {
            "by_month": by_month,
            "daily": [[str(d.date()), round(v, 1)] for d, v in daily_all.items()],
        }
    out["artists"] = list(artist_ids)
    out["families"] = families_list
    return out


def discovery(df):
    """Cumulative distinct artists heard by the end of each month, per owner —
    backs the discovery curve. 'new' = artists first heard that month (in-window)."""
    out = {}
    all_months = sorted(df["ym"].unique())
    for owner in OWNERS:
        g = df[df["owner"] == owner]
        first_ym = g.groupby("artist")["ym"].min()
        new_per_month = first_ym.value_counts().reindex(all_months, fill_value=0).sort_index()
        cum = new_per_month.cumsum()
        out[owner] = [{"ym": ym, "new": int(new_per_month[ym]), "cum": int(cum[ym])}
                      for ym in all_months]
    return out


def routine_windows(df):
    """Per (cut, owner, weekday, hour): totals + top artists/families for the
    heatmap-cell drilldown. Keyed 'cut|owner|weekday|hour' for O(1) lookup."""
    out = {}
    for cut, d in cuts(df):
        for (owner, wd, h), g in d.groupby(["owner", "weekday", "hour_local"]):
            top_a = g.groupby("artist")["minutes_played"].sum().nlargest(WINDOW_TOP_ARTISTS)
            top_f = g.groupby("family")["minutes_played"].sum().nlargest(WINDOW_TOP_FAMILIES)
            out[f"{cut}|{owner}|{wd}|{int(h)}"] = {
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
            "shared_min_minutes": SHARED_MIN_MINUTES,
            # calendar days per period (university runs to the last observed date)
            "period_days": {
                "all": (df["date"].max() - pd.Timestamp(WINDOW_START)).days + 1,
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
        "monthly_detail": monthly_detail(df),
        "discovery": discovery(df),
        "routine_window": routine_windows(df),
        "change": change,
    }

    js = "const EMBEDDED_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write(js)

    # ------------------------------------------------------------ verification
    print(f"window: {WINDOW_START} .. <{WINDOW_END_EXCL}  |  university starts {UNI_START}")
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

    print(f"\n-- shared artists: {shared['count']} with {SHARED_MIN_MINUTES}+ min on both sides "
          f"(name-only matches in window: {shared['name_matches']})")
    for cut in ["all", *PERIODS]:
        p = shared["pct_minutes"][cut]
        print(f"  {cut:10} minutes-weighted shared share: Or {p['Or']}%  Roman {p['Roman']}%  "
              f"({shared['count_by_cut'][cut]} artists)")
    print("  top shared:", ", ".join(a["artist"] for a in shared["top_shared"]["all"][:8]))

    print("\n-- avg monthly hours")
    for o in OWNERS:
        print(f"  {o:6} {change[o]['pre_uni']['avg_monthly_hours']} -> "
              f"{change[o]['university']['avg_monthly_hours']} h/mo")

    print("\n-- discovery: final cumulative == unique_artists (all)")
    for o in OWNERS:
        final = data["discovery"][o][-1]["cum"]
        whole = kpis["all"][o]["unique_artists"]
        uni_new = sum(r["new"] for r in data["discovery"][o] if r["ym"] >= UNI_START[:7])
        print(f"  {o:6} {final:,} vs {whole:,}  {'OK' if final == whole else 'MISMATCH'}"
              f"  (new at university: {uni_new:,})")


if __name__ == "__main__":
    main()

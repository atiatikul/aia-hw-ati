"""Earnings spillover event study for the top-50 US universe.

Reporters = top-50 companies that report inside the calendar window (upcoming)
plus those that already reported in the past month (reported). For each, look
back at its last 8 earnings releases (SEC EDGAR 8-K Item 2.02) and measure how
each same-sector top-50 peer moved on the reaction day, after removing the
market move (SPY).

Inputs (local, not committed):  work/edgar/<TICKER>.json (+ <TICKER>_older.json, XOM_OLD.json)
                                work/ohlcv/<EXCH>_<TICKER>.json  TradingView daily bars
                                output/data/universe.csv
Outputs: output/data/spillover.csv            one row per reporter-peer pair
         output/data/spillover_events.csv     one row per reporter-quarter-stock (derived returns only)
         output/data/spillover_reporters.csv  one row per reporter

Usage: python scripts/spillover.py
"""
import csv, datetime as dt, json, os, statistics as st

QUARTERS = 8
MIN_GAP_DAYS = 50  # two 8-K 2.02 filings closer than this = one quarter; keep the later one (the full results release)
ASOF = dt.date(2026, 11, 4)
RECENT_DAYS = 31   # "already reported in the past month"
# upcoming reporters from the TradingView earnings calendar; DELL date corrected from its IR page
UPCOMING = {"NVDA": "2026-11-17", "AVGO": "2026-12-10", "BRK.B": "2026-11-04", "WMT": "2026-11-19", "MU": "2026-12-23",
            "COST": "2026-12-10", "CSCO": "2026-11-18", "ORCL": "2026-12-14", "HD": "2026-11-17", "AMAT": "2026-11-12",
            "PANW": "2026-11-12", "DELL": "2026-11-24", "CRWD": "2026-12-01"}
SATURDAY_RELEASERS = {"BRK.B"}  # Berkshire publishes results on Saturday morning (berkshirehathaway.com news list)
EXTRA_HISTORY = {"XOM": ["XOM_OLD"]}  # ExxonMobil moved to a new holding-company CIK in 2026; older 8-Ks sit under CIK 34088


def load_bars(symbol):
    path = f"work/ohlcv/{symbol.replace(':', '_', 1)}.json"
    if not os.path.exists(path):
        return None
    bars = json.load(open(path, encoding="utf-8"))["bars"]
    return {dt.datetime.utcfromtimestamp(b["t"]).date(): b["c"] for b in bars}


def utc_to_et(t):
    """EDGAR acceptanceDateTime is UTC. US DST: 2nd Sunday of March to 1st Sunday of November."""
    y = t.year
    march = dt.datetime(y, 3, 8) + dt.timedelta(days=(6 - dt.datetime(y, 3, 8).weekday()) % 7)
    nov = dt.datetime(y, 11, 1) + dt.timedelta(days=(6 - dt.datetime(y, 11, 1).weekday()) % 7)
    dst = march + dt.timedelta(hours=7) <= t < nov + dt.timedelta(hours=6)
    return t - dt.timedelta(hours=4 if dst else 5)


def filings(name):
    """Filing table from one submissions file; '_older' pages store the table at top level."""
    path = f"work/edgar/{name}.json"
    if not os.path.exists(path):
        return None, None
    d = json.load(open(path, encoding="utf-8"))
    if "filings" in d:
        return d["filings"]["recent"], int(d["cik"])
    return d, None


def earnings_releases(ticker):
    rows = []
    for name in [ticker, ticker + "_older"] + EXTRA_HISTORY.get(ticker, []):
        r, cik = filings(name)
        if r is None:
            continue
        if cik is None:
            cik = int(json.load(open(f"work/edgar/{ticker}.json", encoding="utf-8"))["cik"])
        for i, form in enumerate(r["form"]):
            if form == "8-K" and "2.02" in r["items"][i]:
                acc = r["accessionNumber"][i]
                rows.append({
                    "accepted_utc": dt.datetime.fromisoformat(r["acceptanceDateTime"][i].rstrip("Z").split(".")[0]),
                    "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{r['primaryDocument'][i]}",
                })
    rows = sorted({r["url"]: r for r in rows}.values(), key=lambda x: x["accepted_utc"], reverse=True)
    kept = []
    for row in rows:  # newest first; an earlier filing within the gap (pre-announcement, update) is dropped
        if kept and (kept[-1]["accepted_utc"] - row["accepted_utc"]).days < MIN_GAP_DAYS:
            continue
        kept.append(row)
    return kept[:QUARTERS][::-1]


def reaction_day(et, calendar):
    """After 16:00 ET -> next trading day. Before the open or intraday -> that day (or next trading day)."""
    day = et.date()
    timing = "AMC" if et.hour >= 16 else ("BMO" if (et.hour, et.minute) < (9, 30) else "Intraday")
    later = [d for d in calendar if (d > day if timing == "AMC" else d >= day)]
    return timing, (later[0] if later else None)


def day_return(closes, day, calendar):
    i = calendar.index(day)
    prev, cur = closes.get(calendar[i - 1]), closes.get(day)
    if prev is None or cur is None:
        return None
    return cur / prev - 1


def ols_slope(x, y):
    mx, my = st.mean(x), st.mean(y)
    var = sum((a - mx) ** 2 for a in x)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / var if var else None


def link_label(hit, slope, corr):
    """With 8 quarters, 5/8 same-direction (62%) is close to a coin flip, so a link needs >= 6/8
    plus a positive correlation. Strong also needs the peer to move >= 0.3% per 1% reporter move."""
    if hit is None or slope is None or corr is None:
        return "n/a"
    if hit >= 0.75 and corr >= 0.5 and slope >= 0.3:
        return "Strong"
    if hit >= 0.75 and corr >= 0.4:
        return "Moderate"
    if corr <= -0.5:
        return "Inverse"
    return "Weak"


def r2(x):
    return round(x * 100, 2) if x is not None else ""


def main():
    uni = {r["ticker"]: r for r in csv.DictReader(open("output/data/universe.csv", encoding="utf-8"))}
    spy = load_bars("AMEX:SPY")
    calendar = sorted(spy)
    bars = {t: load_bars(u["symbol"]) for t, u in uni.items()}

    # who counts as a reporter
    reporters = []
    for t in uni:
        rel = earnings_releases(t) if os.path.exists(f"work/edgar/{t}.json") else []
        last = utc_to_et(rel[-1]["accepted_utc"]).date() if rel else None
        if t in UPCOMING:
            reporters.append((t, "upcoming", UPCOMING[t], rel))
        elif last and (ASOF - last).days <= RECENT_DAYS:
            reporters.append((t, "reported", last.isoformat(), rel))

    pair_rows, event_rows, rep_rows = [], [], []
    for rep, status, key_date, releases in reporters:
        peers = [t for t, u in uni.items() if u["sector"] == uni[rep]["sector"] and t != rep]
        quarters, pending = [], ""
        for rel in releases:
            et = utc_to_et(rel["accepted_utc"])
            timing, day = reaction_day(et, calendar)
            if rep in SATURDAY_RELEASERS:
                # results come out on Saturday; the 8-K is filed on a later weekday
                sat = et.date() - dt.timedelta(days=(et.date().weekday() - 5) % 7)
                et = dt.datetime.combine(sat, dt.time(8, 0))
                timing, day = "Saturday", next((d for d in calendar if d > sat), None)
            if day is None:
                pending = f"latest release {et:%Y-%m-%d %H:%M} ET reacts on a day with no closing price yet"
                continue
            if bars.get(rep) is None:
                continue
            m = day_return(spy, day, calendar)
            r_rep = day_return(bars[rep], day, calendar)
            if r_rep is None:
                continue
            q = {"day": day, "rep_ex": r_rep - m, "peer_ex": {}}
            event_rows.append([rep, rep, et.strftime("%Y-%m-%d %H:%M ET"), timing, day, r2(r_rep), r2(m), r2(r_rep - m), rel["url"]])
            for p in peers:
                if bars.get(p) is None:
                    continue
                r_p = day_return(bars[p], day, calendar)
                if r_p is None:
                    continue
                q["peer_ex"][p] = r_p - m
                event_rows.append([rep, p, et.strftime("%Y-%m-%d %H:%M ET"), timing, day, r2(r_p), r2(m), r2(r_p - m), rel["url"]])
            quarters.append(q)

        latest = quarters[-1] if quarters else None
        rep_rows.append([rep, status, key_date, len(quarters), latest["day"] if latest else "",
                         r2(latest["rep_ex"]) if latest else "", len(peers),
                         round(st.mean(abs(q["rep_ex"]) for q in quarters) * 100, 2) if quarters else "", pending])

        for p in peers:
            pts = [(q["rep_ex"], q["peer_ex"][p]) for q in quarters if p in q["peer_ex"]]
            lat = latest["peer_ex"].get(p) if latest else None
            lat_same = "" if lat is None else (lat > 0) == (latest["rep_ex"] > 0)
            base = [rep, p, uni[p]["industry"], uni[p]["industry"] == uni[rep]["industry"], len(pts)]
            if len(pts) < 4:
                pair_rows.append(base + ["", "", "", "", "", "n/a", r2(lat), lat_same, "fewer than 4 quarters with prices"])
                continue
            xs, ys = zip(*pts)
            hit = sum(1 for a, b in pts if (a > 0) == (b > 0)) / len(pts)
            slope = ols_slope(xs, ys)
            corr = st.correlation(xs, ys) if len(set(xs)) > 1 and len(set(ys)) > 1 else None
            note = "GEV closes taken from the last hourly bar of each day" if p == "GEV" or rep == "GEV" else ""
            pair_rows.append(base + [round(st.mean(ys) * 100, 2), round(st.mean(abs(y) for y in ys) * 100, 2),
                                     round(hit * 100), round(slope, 2), round(corr, 2) if corr is not None else "",
                                     link_label(hit, slope, corr), r2(lat), lat_same, note])

    with open("output/data/spillover.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["reporter", "peer", "peer_industry", "same_industry", "n_quarters", "avg_peer_excess_pct",
                    "avg_abs_peer_excess_pct", "same_direction_hit_pct", "sensitivity_slope", "correlation",
                    "link", "latest_peer_excess_pct", "latest_same_direction", "note"])
        w.writerows(pair_rows)
    with open("output/data/spillover_events.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["reporter", "stock", "release_time_et", "timing", "reaction_day", "stock_return_pct",
                    "spy_return_pct", "excess_return_pct", "edgar_8k_url"])
        w.writerows(event_rows)
    with open("output/data/spillover_reporters.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["reporter", "status", "date", "n_quarters", "latest_reaction_day", "latest_excess_pct",
                    "n_peers", "avg_abs_excess_pct", "note"])
        w.writerows(rep_rows)
    print(len(rep_rows), "reporters,", len(pair_rows), "pairs,", len(event_rows), "event rows")


if __name__ == "__main__":
    main()

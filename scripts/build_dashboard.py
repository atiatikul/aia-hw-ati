"""Inject the CSV outputs into the dashboard template -> output/dashboard.html (self-contained).

Usage: python scripts/build_dashboard.py
"""
import csv, json, os
from collections import defaultdict

ASOF = "2026-11-04"


def read(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def num(x):
    return float(x) if x not in ("", None) else None


def main():
    uni = read("output/data/universe.csv")
    events = read("output/data/events.csv")
    pairs = read("output/data/spillover.csv")
    ev_rows = read("output/data/spillover_events.csv")
    reps = read("output/data/spillover_reporters.csv")
    results = json.load(open("output/data/earnings_results.json", encoding="utf-8"))["results"]
    for item in json.load(open("work/results_todo.json")):  # latest 8-K per reporter
        if item["t"] in results:
            results[item["t"]].update(url=item["url"], released=item["accepted_et"])

    quarters = defaultdict(dict)
    for r in ev_rows:
        q = quarters[r["reporter"]].setdefault(r["reaction_day"], {
            "day": r["reaction_day"], "release": r["release_time_et"], "timing": r["timing"],
            "url": r["edgar_8k_url"], "spy": num(r["spy_return_pct"]), "rep": None, "peers": {}})
        if r["stock"] == r["reporter"]:
            q["rep"] = num(r["excess_return_pct"])
        else:
            q["peers"][r["stock"]] = num(r["excess_return_pct"])

    data = {
        "asof": ASOF,
        "window": ["2026-11-04", "2027-01-04"],
        "universe": [{"t": u["ticker"], "rank": int(u["rank"]), "company": u["company"], "sector": u["sector"],
                      "industry": u["industry"], "cap": num(u["market_cap_usd_bn"])} for u in uni],
        "events": events,
        "pairs": [{"rep": p["reporter"], "peer": p["peer"], "industry": p["peer_industry"],
                   "same": p["same_industry"] == "True", "n": int(p["n_quarters"]),
                   "avg": num(p["avg_peer_excess_pct"]), "abs": num(p["avg_abs_peer_excess_pct"]),
                   "hit": num(p["same_direction_hit_pct"]), "slope": num(p["sensitivity_slope"]),
                   "corr": num(p["correlation"]), "link": p["link"], "latest": num(p["latest_peer_excess_pct"]),
                   "note": p["note"]} for p in pairs],
        "reporters": [{"t": r["reporter"], "status": r["status"], "date": r["date"], "n": int(r["n_quarters"]),
                       "latestDay": r["latest_reaction_day"], "latest": num(r["latest_excess_pct"]),
                       "peers": int(r["n_peers"]), "avgAbs": num(r["avg_abs_excess_pct"]), "note": r["note"]} for r in reps],
        "results": results,
        "quarters": {k: sorted(v.values(), key=lambda q: q["day"]) for k, v in quarters.items()},
    }
    tpl = open("scripts/dashboard_template.html", encoding="utf-8").read()
    html = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    # the claude.ai artifact adds its own document skeleton; the repo copy needs one to open locally
    os.makedirs("work/artifact", exist_ok=True)
    open("work/artifact/mega-cap-event-radar.html", "w", encoding="utf-8").write(html)
    full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n'
            + html + '\n</body>\n</html>\n')
    open("output/dashboard.html", "w", encoding="utf-8").write(full)
    print("output/dashboard.html", round(len(full) / 1024), "KB")


if __name__ == "__main__":
    main()

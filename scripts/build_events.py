"""Build the event calendar (earnings + US macro) for 2026-11-04 .. 2027-01-04.

Earnings: TradingView earnings calendar (work/earnings_calendar_2026-11-04.json),
          overridden where the company IR page states a different date/time.
Macro:    TradingView economic calendar (US, high importance) up to 2026-12-04, the
          limit of its forward window; after that the official Fed / BLS / BEA schedules.
Usage: python scripts/build_events.py
"""
import csv, json

ACCESSED = "2026-11-04"
TV_EARN = "TradingView MCP mcp-tv-get-earnings-calendar"
TV_ECON = "TradingView MCP mcp-tv-get-economic-calendar (US, min_importance=1)"
TIMING = {1: "AMC", -1: "BMO", 0: "time not set"}

# IR page checks (2026-11-04). Value None = page did not state a date or could not be read.
IR = {
    "WMT": ("2026-11-19", "BMO", "https://corporate.walmart.com/investors/events", "confirmed on IR page: 7:00 a.m. CT"),
    "HD": ("2026-11-17", "BMO", "https://ir.homedepot.com/news-releases/2026/11-03-2026-130236805", "confirmed: call 9 a.m. ET; BMO inferred"),
    "DELL": ("2026-11-24", "AMC", "https://investors.delltechnologies.com/", "IR page date differs from TradingView (2026-12-01); IR date used; 3:30 pm CT, AMC inferred"),
    "MU": (None, None, "http://investors.micron.com/events-and-presentations/default.aspx", "IR page shows no date yet"),
    "CSCO": (None, None, "https://investor.cisco.com/events-and-presentations/default.aspx", "IR page shows no date yet"),
    "ORCL": (None, None, "https://investor.oracle.com/events-and-presentations/default.aspx", "IR page shows no date yet"),
    "AVGO": (None, None, "https://investors.broadcom.com", "IR page blocked (HTTP 403)"),
    "PANW": (None, None, "https://investors.paloaltonetworks.com", "IR page blocked (HTTP 403)"),
    "CRWD": (None, None, "https://ir.crowdstrike.com", "IR page blocked (HTTP 403)"),
    "BRK.B": (None, None, "https://berkshirehathaway.com/news/2026news.html", "no Q3 2026 release listed yet; Berkshire usually publishes on a Saturday"),
}

FOMC = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
BLS_CPI = "https://www.bls.gov/schedule/news_release/cpi.htm"
BLS_PPI = "https://www.bls.gov/schedule/news_release/ppi.htm"
BLS_EMP = "https://www.bls.gov/schedule/news_release/empsit.htm"
BLS_JOLTS = "https://www.bls.gov/schedule/news_release/jolts.htm"
BEA = "https://www.bea.gov/news/schedule"

# (date, time ET, event, period, forecast/previous text, source, url, topic)
MACRO = [
    ("2026-11-04", "10:00", "ISM Services PMI", "Oct 2026", "fcst 54.8 · prev 54.9", TV_ECON, "https://www.ismworld.org", "growth"),
    ("2026-11-06", "08:30", "Jobs report: Non-farm payrolls & unemployment rate", "Oct 2026", "NFP fcst 65K · prev 29K; UR fcst 4.2% · prev 4.2%", TV_ECON, BLS_EMP, "labor"),
    ("2026-11-06", "10:00", "U. Michigan consumer sentiment (prelim)", "Nov 2026", "fcst 48 · prev 46.3", TV_ECON, "http://www.sca.isr.umich.edu/", "consumer"),
    ("2026-11-10", "08:30", "CPI inflation (headline & core)", "Oct 2026", "core m/m fcst 0.2% · prev 0.3%; headline y/y prev 3.7%", TV_ECON, BLS_CPI, "inflation"),
    ("2026-11-12", "10:00", "Existing home sales", "Oct 2026", "fcst 3.98M · prev 3.99M", TV_ECON, "https://www.nar.realtor", "housing"),
    ("2026-11-13", "08:30", "PPI final demand", "Oct 2026", "m/m fcst 0.4% · prev 1.3%", TV_ECON, BLS_PPI, "inflation"),
    ("2026-11-17", "08:30", "Retail sales", "Oct 2026", "m/m prev 0.8%", TV_ECON, "https://www.census.gov/", "consumer"),
    ("2026-11-18", "08:30", "Housing starts & building permits", "Oct 2026", "starts prev 1.221M; permits prev 1.40M", TV_ECON, "https://www.census.gov/", "housing"),
    ("2026-11-25", "08:30", "GDP Q3 (2nd estimate)", "Q3 2026", "prev 1.5% q/q", TV_ECON, BEA, "growth"),
    ("2026-11-25", "08:30", "PCE inflation, personal income & spending", "Oct 2026", "core PCE m/m prev 0.3%; spending prev 0.5%", TV_ECON, BEA, "inflation"),
    ("2026-11-25", "08:30", "Durable goods orders", "Oct 2026", "m/m prev 1.8%", TV_ECON, "https://www.census.gov/", "growth"),
    ("2026-12-01", "10:00", "ISM Manufacturing PMI", "Nov 2026", "prev 55.5", TV_ECON, "https://www.ismworld.org", "growth"),
    ("2026-12-01", "10:00", "JOLTS job openings", "Oct 2026", "prev 7.523M", TV_ECON, BLS_JOLTS, "labor"),
    ("2026-12-03", "10:00", "ISM Services PMI", "Nov 2026", "", TV_ECON, "https://www.ismworld.org", "growth"),
    ("2026-12-04", "08:30", "Jobs report: Non-farm payrolls & unemployment rate", "Nov 2026", "", TV_ECON + "; date matches BLS schedule", BLS_EMP, "labor"),
    ("2026-12-04", "10:00", "U. Michigan consumer sentiment (prelim)", "Dec 2026", "", TV_ECON, "http://www.sca.isr.umich.edu/", "consumer"),
    ("2026-12-09", "not stated", "FOMC rate decision (meeting Dec 8-9, with Summary of Economic Projections)", "Dec 2026", "", "Federal Reserve FOMC calendar (decision time not stated on page)", FOMC, "rates"),
    ("2026-12-10", "08:30", "CPI inflation (headline & core)", "Nov 2026", "", "BLS release schedule", BLS_CPI, "inflation"),
    ("2026-12-15", "08:30", "PPI final demand", "Nov 2026", "", "BLS release schedule", BLS_PPI, "inflation"),
    ("2026-12-23", "08:30", "GDP Q3 (3rd estimate) & corporate profits", "Q3 2026", "", "BEA release schedule", BEA, "growth"),
    ("2026-12-23", "08:30", "PCE inflation, personal income & spending", "Nov 2026", "", "BEA release schedule", BEA, "inflation"),
]

# Which top-50 groups usually react most. Reasoning, not sourced data - shown on the dashboard as such.
TOPIC_NOTE = {
    "rates": "All 50; long-duration growth (tech) and banks most rate-sensitive",
    "inflation": "All 50 via rate expectations; retailers via consumer prices",
    "labor": "All 50 via rate expectations",
    "growth": "Industrials (CAT, GE, RTX, GEV) and semis for PMIs; all for GDP",
    "consumer": "Retailers (WMT, COST, HD, AMZN) and payments (V, MA)",
    "housing": "HD most directly; banks (mortgage demand)",
}


def main():
    uni = {r["ticker"]: r for r in csv.DictReader(open("output/data/universe.csv", encoding="utf-8"))}
    cal = json.load(open("work/earnings_calendar_2026-11-04.json", encoding="utf-8"))["earnings"]
    rows = []
    for e in cal:
        t = e["t"]
        date, timing, status = e["date"], TIMING[e["flag"]], "confirmed (TradingView)" if e["confirmed"] else "estimated (TradingView) [ยังไม่ยืนยัน]"
        src, url, note = TV_EARN, "", ""
        ir = IR.get(t)
        if ir:
            note = ir[3]
            if ir[0]:
                date, timing, status, src, url = ir[0], ir[1], "confirmed (company IR)", "Company IR page", ir[2]
            else:
                url = ir[2]
        rows.append({
            "date": date, "time_et": timing, "type": "Earnings", "event": f"{t} quarterly results (FQ ending {e['fpe']})",
            "tickers": t, "sector": uni[t]["sector"], "status": status,
            "detail": f"Consensus EPS {e['eps']:.2f} · revenue {e['rev'] / 1e9:.1f}B USD (TradingView)",
            "impact_note": "Same-sector peers: see Spillover tab", "source": src, "source_url": url,
            "note": note, "accessed": ACCESSED,
        })
    for d, tm, ev, per, det, src, url, topic in MACRO:
        rows.append({
            "date": d, "time_et": tm, "type": "Macro", "event": f"{ev} ({per})", "tickers": "ALL", "sector": "All",
            "status": "scheduled (official)" if "BLS" in src or "BEA" in src or "Federal Reserve" in src else "scheduled (TradingView)",
            "detail": det, "impact_note": TOPIC_NOTE[topic], "source": src, "source_url": url, "note": topic, "accessed": ACCESSED,
        })
    rows.sort(key=lambda r: (r["date"], r["type"]))
    with open("output/data/events.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "events")


if __name__ == "__main__":
    main()

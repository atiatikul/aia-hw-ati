"""Build the top-50 US universe from a saved TradingView screener JSON.

Rules: NYSE/NASDAQ listing, country = United States, common stock only
(no preferred / depositary shares), one share class per company.
Usage: python scripts/build_universe.py work/screener_YYYY-MM-DD.json output/data/universe.csv
"""
import csv, json, sys

SKIP_CLASSES = {"NASDAQ:GOOG", "NYSE:BRK.A"}  # keep GOOGL and BRK.B

src, dst = sys.argv[1], sys.argv[2]
snapshot = src.rsplit("_", 1)[-1].removesuffix(".json")
rows = json.load(open(src, encoding="utf-8"))["data"]["rows"]

out, seen = [], set()
for r in rows:
    desc = r.get("description") or ""
    if r["exchange"] not in ("NYSE", "NASDAQ") or r["country"] != "United States":
        continue
    if "/" in r["name"] or "Depositary" in desc or "Preferred" in desc:
        continue
    if r["symbol"] in SKIP_CLASSES or desc in seen:
        continue
    seen.add(desc)
    out.append(r)
    if len(out) == 50:
        break

with open(dst, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rank", "symbol", "ticker", "company", "market_cap_usd_bn", "sector", "industry",
                "next_earnings_date", "snapshot_date", "source"])
    for i, r in enumerate(out, 1):
        w.writerow([i, r["symbol"], r["name"], r["description"], round(r["market_cap_basic"] / 1e9, 1),
                    r["sector"], r["industry"], r["earnings_release_next_date"], snapshot,
                    "TradingView screener (MCP mcp-tv-run-screener, market=america, sort=market_cap_basic)"])
print(len(out), "companies; #50 =", out[-1]["name"], round(out[-1]["market_cap_basic"] / 1e9))

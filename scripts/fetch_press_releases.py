"""Download the earnings press release (8-K exhibit 99.1) behind each reporter's latest 8-K Item 2.02.

Reads work/results_todo.json (ticker, filing url), writes plain text to work/pr/<TICKER>.txt.
Usage: python scripts/fetch_press_releases.py
"""
import html, json, os, re, time, urllib.request

UA = {"User-Agent": "aia-hw-ati research contact@example.com", "Accept-Encoding": "identity"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r:
        return r.read().decode("utf-8", errors="replace")


def to_text(doc):
    doc = re.sub(r"(?is)<(script|style).*?</\1>", " ", doc)
    doc = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d)>", "\n", doc)
    doc = re.sub(r"(?i)</t[dh]>", " | ", doc)
    doc = html.unescape(re.sub(r"<[^>]+>", " ", doc))
    doc = re.sub(r"[ \t\xa0]+", " ", doc)
    return re.sub(r"\n\s*\n+", "\n", doc).strip()


def main():
    os.makedirs("work/pr", exist_ok=True)
    for item in json.load(open("work/results_todo.json")):
        out = f"work/pr/{item['t']}.txt"
        if os.path.exists(out):
            continue
        folder = item["url"].rsplit("/", 1)[0]
        acc = folder.rsplit("/", 1)[1]
        full = get(f"{folder}/{acc[:10]}-{acc[10:12]}-{acc[12:]}.txt")
        docs = re.findall(r"(?s)<DOCUMENT>(.*?)</DOCUMENT>", full)
        ex = [d for d in docs if re.search(r"<TYPE>EX-99\.?1?\b", d)] or [d for d in docs if "<TYPE>EX-99" in d]
        text = to_text(ex[0]) if ex else ""
        open(out, "w", encoding="utf-8").write(f"SOURCE: {item['url']}\nACCEPTED_ET: {item['accepted_et']}\n\n{text}")
        print(item["t"], len(text))
        time.sleep(0.3)


if __name__ == "__main__":
    main()

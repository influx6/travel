"""Fetch one freely-licensed photo per place, from Wikimedia Commons then Openverse."""
import json, os, re, subprocess, urllib.parse, time

SPECS = {
    "pingan": [("commons", "Ping An Finance Centre"), ("commons", "Ping An Finance Center Shenzhen")],
    "moca": [("commons", "Museum of Contemporary Art and Planning Exhibition Shenzhen")],
    "upperhills": [("commons", "Lianhuashan Park Shenzhen"), ("openverse", "Lianhuashan Park Shenzhen skyline")],
    "culture": [("openverse", "Shenzhen Civic Center"), ("commons", "Shenzhen Civic Center")],
    "grand": [("commons", "Shenzhen Grand Theatre")],
    "mixc_crossing": [("commons", "Shenzhen MIXC")],
    "dingplaza": [("commons", "Dongmen night market Shenzhen")],
    "dmd": [("commons", "Dongmen food Shenzhen")],
    "dongmen": [("commons", "Dongmen Pedestrian Street Shenzhen")],
    "mixc_tiandi": [("commons", "MIXC WORLD Shenzhen")],
    "talent": [("openverse", "Shenzhen Talent Park"), ("commons", "Shenzhen Talent Park")],
    "poly": [("openverse", "Houhai Shenzhen skyline"), ("commons", "Shenzhen Bay skyline")],
    "nantou": [("commons", "Nantou Ancient City")],
    "happy": [("openverse", "Shenzhen Bay ferris wheel"), ("openverse", "Baoan Shenzhen waterfront"),
              ("commons", "Shenzhen ferris wheel")],
}
UA = "trip-planner/1.0 (personal trip planning)"


def curl_json(url):
    r = subprocess.run(["curl", "-s", "--compressed", "-A", UA, url], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def commons(query, limit=12):
    url = ("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": "1200"}))
    d = curl_json(url)
    out = []
    for p in (d.get("query") or {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii.get("thumburl") or ii.get("width", 0) < 900:
            continue
        meta = ii.get("extmetadata") or {}
        out.append({
            "title": p.get("title", ""), "url": ii["thumburl"], "page": ii.get("descriptionurl", ""),
            "artist": re.sub(r"<[^>]+>", "", (meta.get("Artist", {}) or {}).get("value", "")).strip(),
            "license": (meta.get("LicenseShortName", {}) or {}).get("value", ""),
            "w": ii.get("width", 0), "h": ii.get("height", 0), "index": p.get("index", 99),
            "src": "commons",
        })
    out.sort(key=lambda x: x["index"])
    return out


def openverse(query, limit=12):
    url = ("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({
        "q": query, "page_size": str(limit), "license_type": "all-cc"}))
    d = curl_json(url)
    out = []
    for r in d.get("results", []):
        if not r.get("url") or (r.get("width") or 0) < 1000:
            continue
        out.append({
            "title": r.get("title") or "", "url": r["url"], "page": r.get("foreign_landing_url", ""),
            "artist": r.get("creator") or "", "license": (r.get("license") or "").upper(),
            "w": r.get("width"), "h": r.get("height"), "src": "openverse",
        })
    return out


def main():
    os.makedirs("../images", exist_ok=True)
    credits = {}
    for key, attempts in SPECS.items():
        picked = None
        for src, q in attempts:
            hits = commons(q) if src == "commons" else openverse(q)
            # prefer landscape photos
            hits.sort(key=lambda h: 0 if h["w"] >= h["h"] else 1)
            if hits:
                picked = hits[0]
                picked["query"] = q
                break
            time.sleep(0.5)
        if not picked:
            print("MISS", key)
            continue
        dest = f"../images/{key}.jpg"
        subprocess.run(["curl", "-sL", "-A", UA, "-o", dest, picked["url"]])
        ok = subprocess.run(["file", dest], capture_output=True, text=True).stdout
        size = os.path.getsize(dest) if os.path.exists(dest) else 0
        if "image" not in ok or size < 5000:
            print("BAD", key, ok.strip()[:60])
            os.path.exists(dest) and os.remove(dest)
            continue
        credits[key] = {"file": f"images/{key}.jpg", "title": picked["title"], "page": picked["page"],
                        "artist": picked["artist"], "license": picked["license"], "source": picked["src"],
                        "query": picked["query"]}
        print(f"{key:14s} {size:>8d} {picked['src']:9s} {picked['title'][:60]}")
        time.sleep(0.5)
    json.dump(credits, open("out/image_credits.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

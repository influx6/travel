"""Render README.md from the generated dataset + editorial notes."""
import csv, json, urllib.parse

HOTEL_ZH = "加来酒店(深圳福田口岸店)"
HOTEL_ADDR_ZH = "福田区福民路皇岗公园街8号 (皇岗公园东大门)"

EDIT = {
    "pingan": dict(
        img="pingan", cap="Ping An International Finance Centre (平安金融中心), Futian CBD",
        sweet="116F, the west/southwest corner windows about 30 min before sunset — you look straight "
              "down 益田路 and across to 莲花山公园. Do daylight → sunset → lights on one ¥180 ticket.",
        expect="Airport-style security (bag scan), a 55-second lift, then an open 360° deck. "
               "45–60 min inside. Buy online (¥180) instead of ¥200 at the counter.",
        watch="Last entry 19:15, 20:15 on Fri/Sat. Haze after a humid day ruins the view — check the "
              "visibility before paying. No tripods. **Fanny's note:** the tower's base is just a "
              "commercial block next to COCO Park — the observation deck is the only reason to go; "
              "skip the building itself.",
        img2=None),
    "moca": dict(
        img="moca", cap="Museum of Contemporary Art & Planning Exhibition (当代艺术与城市规划馆)",
        sweet="The ground-floor atrium and the giant city-model hall (north wing, floors 3–5). "
              "The brushed-aluminium skin looks best in mid-afternoon light.",
        expect="Free, no booking, Tue–Sun 10:00–18:00. Security x-ray at the door, 1–1.5 h inside. "
               "English captions are patchy; the model is the highlight.",
        watch="Closed Mondays. Some touring exhibitions charge separately. No food or drink inside; "
              "free lockers at the entrance.",
        img2=None),
    "upperhills": dict(
        img="upperhills", cap="MUJI Diner at Upper Hills (深业上城)",
        sweet="The loft lanes and coffee terraces, then the footbridge into 莲花山公园 — a 15–20 min "
              "climb to the Deng Xiaoping statue for the classic CBD skyline at sunset, free.",
        expect="An open-air mall (MUJI Hotel/Diner, duty-free, design shops) plus a big park. "
               "2–3 h if you do both. This is the best free sunset in the city.",
        watch="The bridge and park climb are unshaded — go after 16:00. Few toilets near the summit. "
              "The mall is quiet on weekday mornings.",
        img2="lianhuashan", img2cap="莲花山公园 (Lianhuashan Park) — the park at the end of the bridge"),
    "culture": dict(
        img=None, cap="",
        sweet="Whatever is on that week — it's a working arts centre, not a sight.",
        expect="A neighbourhood venue in 景田; small exhibitions and performances.",
        watch="Check the programme first; parts close on Mondays. Easy to skip on a 3-day trip.",
        img2=None),
    "grand": dict(
        img="grand", cap="Shenzhen Grand Theatre (深圳大剧院)",
        sweet="The glass lobby lit up before a performance.",
        expect="A ticketed concert/ theatre house; without a ticket it's a 5-minute look.",
        watch="Don't build a day around it unless you've booked a show — check 大麦/Damai for that week.",
        img2=None),
    "mixc_crossing": dict(
        img="mixc_crossing", cap="The MixC (深圳万象城), Luohu",
        sweet="The luxury atrium and the basement food hall — the reliable rain plan.",
        expect="1–2 h of shopping; clean, English-friendly, air-conditioned.",
        watch="It's a mall, not a landmark. Prices are Hong Kong-level.",
        img2=None),
    "dingplaza": dict(
        img="dingplaza", cap="Food hall inside Dongmen (东门町广场)",
        sweet="Nothing of its own — it's the covered shortcut into the food city.",
        expect="A generic mall attached to DMD Food City.",
        watch="Skip unless it's raining or you need AC.",
        img2=None),
    "dmd": dict(
        img="dmd", cap="东门町美食城 (DMD Food City), Dongmen",
        sweet="The back stall rows: 潮汕 beef balls, 生煎 buns, 糖水 desserts. Order by pointing; "
              "most stalls take WeChat/Alipay only.",
        expect="Loud, bright, crowded. ¥15–40 a dish, shared tables, 45–90 min. "
               "The cheapest good eating on this list.",
        watch="Peak 18:00–20:00 — go 17:00 or 20:30. Some stalls shut early on weekdays. "
              "Cash is often refused.",
        img2=None),
    "dongmen": dict(
        img="dongmen", cap="Dongmen Pedestrian Street (东门步行街) at night",
        sweet="The neon at dusk, then the side lanes off 解放路 for snacks.",
        expect="Shenzhen's original bargain street: clothes, phone cases, skewers, huge crowds. 1–2 h.",
        watch="Ignore anyone inviting you to a \"tea ceremony\" or \"art show\" — classic scam. "
              "Keep your phone zipped; it's shoulder-to-shoulder on weekends.",
        img2=None),
    "mixc_tiandi": dict(
        img="mixc_tiandi", cap="MIXC WORLD / 万象天地, Nanshan",
        sweet="The outdoor 里巷 lanes and sunken plaza — best coffee-and-dessert stop in the city.",
        expect="Design-led mall, 1–2 h, English menus common.",
        watch="Popular restaurants queue 45 min+ at weekends — reserve on 大众点评 (Dianping) first.",
        img2=None),
    "talent": dict(
        img="talent", cap="Shenzhen Talent Park (深圳人才公园) and the Houhai skyline",
        sweet="The wooden boardwalk on the west side, looking back at 春笋 and the Houhai towers. "
              "17:00–18:30 is the light you want.",
        expect="Free, flat ~2.5 km loop, 45–60 min. Locals run and fish here; it's calm on weekdays.",
        watch="Little shade; mosquitoes after dusk. The metro exit is a 10-min walk from the water.",
        img2=None),
    "poly": dict(
        img="poly", cap="Houhai skyline — Poly Cultural Plaza (保利文化广场) sits at its foot",
        sweet="Only if a show is on at the theatre.",
        expect="A local mall and theatre next to Talent Park.",
        watch="Skip as a destination; use it for AC or dinner after the park.",
        img2=None),
    "nantou": dict(
        img="nantou", cap="South gate of Nantou Ancient City (南头古城)",
        sweet="The south gate and main lane, plus coffee in the restored courtyard houses.",
        expect="1.5–2 h. **Fanny's verdict:** *\"not very interesting — they turned it into a "
               "pedestrian street, small shops on both sides, and the street isn't long.\"*",
        watch="Weekends are packed and the shops repeat. Go for coffee, not sightseeing.",
        img2=None),
    "happy": dict(
        img="happy", cap="Happy Harbour (欢乐港湾) and the Bay Glory wheel, Bao'an",
        sweet="The waterfront steps facing the wheel at sunset, then the light show after dark.",
        expect="Wheel ride ~20 min, ¥150 (¥180 public holidays). Promenade free. 2–3 h total.",
        watch="Tuesdays open 14:00 (maintenance day). Ticket sales stop 30 min before close. "
              "High wind closes the wheel — check the weather.",
        img2=None),
}


def main():
    rows = list(csv.DictReader(open('../places.csv', encoding='utf-8-sig')))
    plan = json.load(open('out/plan.json'))
    links = plan['links']
    by_key = {}
    for r in rows:
        for k, e in EDIT.items():
            if e['img'] == k:
                pass
    # map rows to editorial keys via image name guess = first token of name
    key_for = {
        "Ping'an International Financial Center": "pingan",
        "Museum of Contemporary Art & Planning Exhibition": "moca",
        "Upper Hills (深业上城)": "upperhills",
        "Shenzhen Cultural Center (Jingtian)": "culture",
        "Shenzhen Grand Theatre": "grand",
        "The Mixc of Shenzhen City Crossing": "mixc_crossing",
        "Dong Men Ding Plaza": "dingplaza",
        "DMD Food City (东门町美食城)": "dmd",
        "Dongmen Pedestrian Street": "dongmen",
        "MixC World 万象天地 (Nanshan)": "mixc_tiandi",
        "Shenzhen Talent Park": "talent",
        "Shenzhen Poly Cultural Plaza": "poly",
        "Nantou Ancient City": "nantou",
        "Happy Harbour": "happy",
    }

    out = []
    A = out.append

    A("# Shenzhen trip plan\n")
    A("**Hotel:** 加来酒店 (Calais Hotel) — 深圳福田口岸店  ")
    A(f"**Address:** {HOTEL_ADDR_ZH}  ")
    A("**Phone:** [+86-755-88257999](tel:+8675588257999) · Booking [removed]\n")
    A("**Nearest metro:** 皇岗村 (Huanggangcun), Line 7, Exit A — 430 m / 7 min walk  ")
    A("**Also close:** Futian Checkpoint (福田口岸), Lines 4 & 10 — ~1.1 km / 15 min walk\n")
    A("14 places, sorted closest → furthest. Photos are freely licensed (credits at the bottom).\n")
    A("---\n")

    A("## 1. The short version\n")
    A("- **Arrive:** high-speed rail from West Kowloon to **福田 (Futian)** — 14 min, ¥68 — then a 3 km DiDi.")
    A("- **Best of the list:** Ping An Free Sky at sunset · Talent Park at sunset · Happy Harbour wheel · "
      "DMD Food City · Upper Hills + 莲花山公园.")
    A("- **Skip unless passing:** 文化馆, 保利文化广场, 东门町广场.")
    A("- **Money:** Alipay or WeChat Pay with a foreign card; metro gates also take contactless Visa/Mastercard.")
    A("- **Bring:** passport everywhere — trains, hotel, museums.\n")

    A("---\n")
    A("## 2. Getting from Tung Chung to the hotel\n")
    A("| Option | Route | Time | Cost | Verdict |")
    A("|---|---|---|---|---|")
    A("| **A. High-speed rail** | Tung Chung → Kowloon → walk to West Kowloon → HSR to 福田 → DiDi | 1 h 50 – 2 h 15 | ≈ HK$19 + ¥68 + ¥15 ≈ **HK$110** | Fastest, one immigration, easiest with bags |")
    A("| **B. East Rail** | Tung Chung → Nam Cheong (南昌) → Hung Hom (红磡) → East Rail → Lok Ma Chau (落马洲) → Futian Port (福田口岸) → ~1.1 km walk | 2 h 10 – 2 h 40 | **HK$57.5** | Cheapest; the port is next to the hotel |")
    A("| **C. Coach** | S1 bus to HKIA → cross-border coach → 福田/皇岗 | 2 h 30 + | ~HK$120–180 | Only if you're already at the airport |")
    A("")

    A("### A — High-speed rail, step by step (recommended)\n")
    A("| Step | What | Time | Cost |")
    A("|---|---|---|---|")
    A("| 1 | 东涌 (Tung Chung) → 九龙 (Kowloon), Tung Chung Line | 28 min | HK$18.7 |")
    A("| 2 | Walk Kowloon → 西九龙 (West Kowloon) through Elements | 10 min | — |")
    A("| 3 | HK exit + mainland entry + security **at West Kowloon** | 30–45 min | — |")
    A("| 4 | 西九龙 → 福田, G-train | 14–18 min | ¥68 (2nd class) |")
    A("| 5 | 福田站 → hotel, DiDi | 10–15 min | ¥15–20 |")
    A("")
    A("**Faster first leg:** Tung Chung → 南昌 (Nam Cheong, 10 min) → Tuen Ma Line one stop to 柯士甸 "
      "(Austin, 5 min) → 5 min covered walk to West Kowloon. Saves ~10 min over the Kowloon walk.\n")
    A("**Booking the train.** Use the **12306** app (English UI) or Trip.com, or buy at the West Kowloon "
      "counters. You need your **passport number**; the ticket is tied to it. ~40 trains a day to 福田, "
      "roughly **07:00–23:00**, every 5–20 min. Book a day ahead on weekends and holidays.\n")
    A("**What to expect at West Kowloon.** It's a co-located border: you clear Hong Kong exit and "
      "mainland entry *before* boarding, then walk straight out at 福田 with no further checks. "
      "Arrive **45 min before departure** (60 min at peak). Security is airport-style — liquids are fine, "
      "but no lighters and no power banks over 100 Wh. There are currency exchanges and SIM counters "
      "airside.\n")
    A("**At 福田站.** You arrive underground beneath 益田路. Follow signs to 地铁 (Metro): Lines 2, 3 and 11. "
      "For a DiDi, use the designated pickup level — the station is huge, so match the car's PIN and "
      "meet at the signed pick-up zone rather than the taxi rank.\n")

    A("### The HSR journey, minute by minute\n")
    A("| When | What happens |")
    A("|---|---|")
    A("| Before | Book on **12306** (English UI) or Trip.com with your passport number. There is no paper "
      "ticket — your passport *is* the ticket. |")
    A("| T-45 | Enter West Kowloon at B1. **Security first**: bag scan, no lighters, power banks must be "
      "under 100 Wh and in your hand luggage. |")
    A("| T-35 | **Hong Kong immigration** (e-channel or counter). |")
    A("| T-25 | **Mainland immigration** — this queue is the variable; it's where the 30–45 min goes. |")
    A("| T-10 | Walk to your gate (numbered 1–15). **Gates close 5 min before departure.** |")
    A("| T-0 | 14–18 min to 福田. The stop is short — stand up early. |")
    A("| Arrive | You're already inside China; walk straight out. Follow **地铁 (Metro)** for Lines 2/3/11 "
      "or **网约车** for the DiDi pickup level. |")
    A("")
    A("**Luggage:** overhead racks plus racks at carriage ends; no weight check on this route. "
      "**Seats:** second class is 3+2 and fine for 15 min; first class (¥109) is 2+2 if you want quiet.\n")

    A("### B — East Rail via 落马洲 / 福田口岸 (cheapest)\n")
    A("1. Tung Chung (东涌) → Nam Cheong (南昌) (Tung Chung Line, 10 min) → Hung Hom (红磡) "
      "(Tuen Ma Line, ~12 min) → Lok Ma Chau (落马洲) (East Rail, ~40 min). Total ~75–85 min, **HK$57.5** on Octopus.")
    A("2. Cross at **福田口岸 (Futian Port)**: open **06:30–22:30**, 15–30 min. Two checks, one walkway.")
    A("3. The hotel is **~1.1 km** from the port — 15 min on foot, or ¥10 by DiDi.")
    A("")
    A("East Rail last trains to Lok Ma Chau (落马洲) leave Hung Hom (红磡) around 21:35 and Admiralty (金钟) around 21:29 — **don't use this "
      "route if you land late**. For late arrivals use the HSR (runs to ~23:00) or 皇岗口岸 "
      "(Huanggang Port, 24 h, 1.4 km from the hotel).\n")

    A("### C — Coach from the airport\n")
    A("S1 bus from Tung Chung (东涌) → HKIA (~10 min, HK$3.5), then a cross-border coach to Futian (福田) or "
      "Huanggang (皇岗) (~HK$120–180, "
      "60–90 min plus the border). Slower than the train and you still queue — only worth it if you're "
      "already at HKIA with a lot of luggage.\n")

    A("---\n")
    A("## 3. Trains and metro — the details\n")
    A("**Shenzhen Metro, in practice**")
    A("- 17 lines, 400+ stations, announcements in Mandarin/Cantonese/English, signage in English.")
    A("- **Pay:** tap a contactless **Visa / Mastercard / Amex / JCB** on the gate (works across the "
      "network since 2026), or use **Alipay → Transport → 深圳地铁** QR. Use the *same* method in and out — "
      "mixing them creates an incomplete trip and a red gate.")
    A("- **Fares:** ¥2–8. Gates close ~23:00–23:30 depending on the line.")
    A("- **Exits matter:** station exits can be 500 m apart. Check the exit letter in this guide before "
      "you go up.")
    A("- **Rush hour:** 08:00–09:30 and 17:30–19:30. Avoid Line 4 and Line 1 with luggage.\n")
    A("**DiDi, in practice**")
    A("- The DiDi app has an English mode and takes foreign cards. Set your pickup pin carefully — "
      "drivers call to confirm; the in-app chat auto-translates.")
    A("- Typical fares from the hotel are listed on each place below (DiDi Express, no surge).")
    A("- At stations and malls use the signed **网约车 (ride-hailing) pickup point**, not the taxi rank.\n")
    A("**About direct DiDi links:** DiDi has no public link format that pre-fills an origin and "
      "destination. The supported way is DiDi's own API (the DiDi MCP, `taxi_generate_ride_app_link`, "
      "free key at mcp.didichuxing.com), which returns a `v.didi.cn` link that opens the app with both "
      "ends filled in. If you want those 14 links generated, get a key and I'll wire them in. "
      "Until then, each place below gives you a **copy-paste Chinese block** for the DiDi destination "
      "field, plus an Amap route link.\n")

    A("---\n")
    A("## 4. Places, closest → furthest\n")
    A("`km` straight line from the hotel · `DiDi` road distance/time · `Metro` door-to-door · `Fun` 1–10\n")
    A("| # | Place | 中文 | Area | km | DiDi | Metro | Fun |")
    A("|---|---|---|---|---|---|---|---|")
    for r in rows:
        A(f"| {r['rank']} | {r['name']} | {r['chinese_name']} | {r['area']} | {r['distance_km_straight']} | "
          f"{r['didi_min']} min / {r['didi_km']} km | {r['metro_plan']} · {r['metro_min']} min | "
          f"**{r['fun_factor_1_10']}** |")
    A("")

    for r in rows:
        key = key_for.get(r['name'])
        e = EDIT.get(key) if key else None
        if not e:
            continue
        head = r['name'] if r['chinese_name'] in r['name'] else f"{r['name']} — {r['chinese_name']}"
        A(f"### {head}\n")
        if e.get('img'):
            A(f"![{e['cap']}](images/{e['img']}.jpg)")
            A(f"*{e['cap']}*")
        if e.get('img2'):
            A(f"![{e['img2cap']}](images/{e['img2']}.jpg)")
            A(f"*{e['img2cap']}*\n")
        A(f"**Fun {r['fun_factor_1_10']}/10** · {r['area']} · {r['type']} · "
          f"**{r['distance_km_straight']} km** from the hotel\n")
        A(f"- **Getting there:** {r['metro_plan']} (~{r['metro_min']} min) or DiDi "
          f"{r['didi_min']} min / {r['didi_km']} km.")
        A(f"- **Sweet spot:** {e['sweet']}")
        A(f"- **What to expect:** {e['expect']}")
        A(f"- **Look out for:** {e['watch']}")
        A(f"- **Links:** [Amap pin]({r['amap_link']}) · [Amap route from hotel]({r['amap_route_link']}) · "
          f"[Google Maps]({r['google_link']})")
        A(f"- **DiDi destination (copy this):**")
        A(f"  ```")
        A(f"  {r['chinese_name']}")
        A(f"  ```")
        A("")

    A("---\n")
    A("## 5. Plan for maximum enjoyment\n")
    A("Built around light: the best things here are two sunsets and one evening food street.\n")
    A("**Day 1 — arrive + skyline**")
    A("- Check in, drop bags.")
    A("- 16:00 **Ping'an Free Sky** (booked online; enter ~16:30 for daylight → sunset → lights).")
    A("- Dinner around 购物公园 / COCO Park.")
    A("- Optional: walk the 市民中心 plaza at night.\n")
    A("**Day 2 — Futian + Dongmen (east)**")
    A("- 10:00 **MOCA** (free, closed Mondays).")
    A("- Lunch at **DMD Food City**, then **Dongmen Pedestrian Street**.")
    A("- **MixC City Crossing** for AC and coffee; **大剧院** only if something's on.")
    A("- Evening: back to 福田 for an early night.\n")
    A("**Day 3 — Nanshan (west)**")
    A("- Late morning **Nantou Ancient City** (coffee) — or sleep in and skip it.")
    A("- Lunch at **万象天地 (MixC World)**.")
    A("- 17:00 **Talent Park** for sunset, dinner in 后海.")
    A("- **保利文化广场** is next door if you need a mall.\n")
    A("**Day 4 — Bao'an + departure**")
    A("- **Upper Hills** coffee → bridge → **莲花山公园** for the skyline (or swap to Happy Harbour).")
    A("- **Happy Harbour** for the wheel at sunset and the light show.")
    A("- Back to the hotel; allow 3 h to HKIA if flying out.\n")
    A("**Only one day?** Ping An Free Sky at 16:30 → DMD Food City for dinner → done. "
      "**Only two?** Add MOCA in the morning and Talent Park at sunset.\n")

    A("---\n")
    A("## 6. Amap (高德地图)\n")
    A("Amap share links cap at **10 points**, so the list is split by geography:\n")
    A(f"- **Futian + Luohu (9 places):** [open in Amap]({links['futian_luohu']})")
    A(f"- **Nanshan + Bao'an (5 places):** [open in Amap]({links['nanshan_baoan']})")
    A("")
    A("Open on your phone with the Amap app installed and it opens in-app.\n")
    A("**Save all 14 to your Amap account:**")
    A("1. On a **PC**, open **wia.amap.com** and sign in.")
    A("2. Create a map → **批量导入 (bulk import)** → upload **`amap_import.csv`**.")
    A("3. Columns: 名称 / 经纬度 / 地址 / 颜色 / 描述 / 文件夹. Coordinates are **经度,纬度** in **GCJ-02**.")
    A("4. Imported points sync to the 收藏 (Favorites) folder in your phone app.\n")
    A("If they insist on their own template, download it and paste these columns in — the template must "
      "be used unchanged.\n")

    A("---\n")
    A("## 7. Notes\n")
    A("- **Coordinates:** Google and Amap both use **GCJ-02** in mainland China; `places.csv` gives GCJ "
      "(works in both) plus WGS-84 for GPS tools. They differ by ~500 m — don't mix them.")
    A("- **Closures:** MOCA closed Mondays · Happy Harbour wheel opens 14:00 on Tuesdays · "
      "Futian Port closes 22:30.")
    A("- **Prices:** Free Sky ¥180–200 · Bay Glory ¥150–180 · everything else on this list is free entry.")
    A("- **Data pulled 2026-11-24.** Hours and prices change — re-check the two paid attractions on the day.\n")

    A("---\n")
    A("### Photo credits\n")
    credits = json.load(open('out/image_credits.json'))
    for k, c in credits.items():
        title = c['title'].replace('File:', '')
        lic = c['license'] or 'see file page'
        who = c['artist'] or 'see file page'
        A(f"- **{k}** — [{title}]({c['page']}) · {who} · {lic}")
    A("")
    A("### Files\n")
    A("- `README.md` — this plan")
    A("- `places.csv` — all 14 places with GCJ/WGS coordinates, Amap + Google links, times and notes")
    A("- `amap_import.csv` — bulk-import file for wia.amap.com")
    A("- `amap_links.md` — every Amap link in one place")
    A("- `booking.md` — hotel confirmation and reviews")
    A("- `images/` — photos (credits above)")
    A("- `tools/` — the scripts that generated all of this")

    open('../README.md', 'w', encoding='utf-8').write("\n".join(out) + "\n")
    print("README written:", len("\n".join(out)), "chars")


if __name__ == '__main__':
    main()

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
              "visibility before paying. No tripods.",
        review="Ping An Financial Center is nearby the COCO Park shopping mall, no need to go there, just "
               "a commercial area, unless you want to go to COCO Park shopping mall.",
        verdict="Only the observation deck is worth paying for — the tower and its plaza are a commercial "
                "block. If you don't want the skyline ticket, skip it.",
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
        expect="1.5–2 h at most — and only if you want a coffee stop.",
        watch="If you go anyway, go for coffee in a restored courtyard, not for sightseeing, and only on "
              "a weekday — weekends are packed and the shops repeat.",
        review="I went to Nantou Ancient City with Heidi, it's not very interesting, they turn this place "
               "to a pedestrian street, both sides are small shops and the street is not very long.",
        verdict="**Skip it.** The weakest thing on this list — your contact's verdict, not mine.",
        img2=None),
    "happy": dict(
        img="happy", cap="Happy Harbour (欢乐港湾) and the Bay Glory wheel, Bao'an",
        sweet="The waterfront steps facing the wheel at sunset, then the light show after dark.",
        expect="Wheel ride ~20 min, ¥150 (¥180 public holidays). Promenade free. 2–3 h total.",
        watch="Tuesdays open 14:00 (maintenance day). Ticket sales stop 30 min before close. "
              "High wind closes the wheel — check the weather.",
        img2=None),
    "wondermeet": dict(
        img="wondermeet", cap="Inside 世纪汇 (Century Place) — WonderMeet occupies levels 1–3",
        sweet="Start on **3F**: go-karts and laser tag before queues build, then 2F (ice rink, PS5/Switch, "
              "KTV pods), then 1F arcade as the afternoon fills.",
        expect="One wristband, 10:00–22:00, **re-entry allowed** — leave for lunch and come back. "
               "40+ activities over three levels (5F is a sauna). ¥268 weekday / ¥298 weekend; "
               "night pass ¥168 after 19:00.",
        watch="Karts and laser tag need closed shoes; skates are rented. Weekday afternoons are quietest. "
              "Join their WeChat group at the desk for 20 free claw-machine coins.",
        img2=None),
    "seg": dict(
        img="seg", cap="Inside SEG Plaza (赛格) — six floors of components and repair benches",
        sweet="Floors 1–3 for phones and laptops, the basement for components and tools. The repair "
              "benches are the real show.",
        expect="Dense, loud, almost no English. Vendors quote fast — have the model number written on "
               "your phone. 45–90 min.",
        watch="Check IMEI/serial and that it isn't refurbished. Know the Taobao price first, then "
              "bargain. Cash as backup.",
        img2=None),
    "zijingcheng": dict(
        img="zijingcheng", cap="华强北 — the block that 紫荆城食品交易中心 sits in",
        sweet="Two floors of imported snacks: buy a **box** of nuts or a case of drinks, not singles.",
        expect="100+ stalls, wholesale prices even for one item. 30–45 min.",
        watch="Check the expiry on the box, not the sample. Cards work, cash gets a better number.",
        img2=None),
    "mingtong": dict(
        img="mingtong", cap="The 华强北 wholesale grid — 明通 cosmetics is one of its towers",
        sweet="Korean/Japanese skincare at near-duty-free prices. Ask for **批发价** (wholesale price) "
              "and buy three of something rather than one.",
        expect="Tight stalls, pushy staff, 30–45 min. Branded goods are the draw.",
        watch="Verify batch codes and expiry — some stock is grey-market. Very little haggling on brands.",
        img2=None),
    "shuibei": dict(
        img="shuibei", cap="特发水贝珠宝大厦 — one of the Shuibei jewelry towers",
        sweet="Price = **gold weight × the day's rate + 工费 (labour)**. Ask for both numbers separately, "
              "then compare two or three towers on the same street.",
        expect="Showrooms rather than stalls; staff will weigh and quote without pressure. 1–1.5 h. "
               "Weekdays are calmer than weekends.",
        watch="Insist on the certificate and a receipt, and check the 工费 isn't padded. Don't buy jade "
              "without a loupe and a second opinion.",
        img2=None),
    "baima": dict(
        img="baima", cap="Wholesale clothing floors around 老街 — 白马 / 宝华楼",
        sweet="**2F** women's trend, 3–4F men's, **5F export surplus**. Hit it 16:00–18:00 as they "
              "clear stock.",
        expect="Six floors, 500+ stalls; some want two or three pieces minimum. 1–1.5 h.",
        watch="Sizes run small — try before paying. Walking away is your strongest move.",
        img2=None),
    "techpark": dict(
        img=None, cap="",
        sweet="Walk the deck behind 万象天地 toward 人才公园 — glass towers on one side, open water and the "
              "Houhai skyline on the other. Best light after 16:00.",
        expect="An office campus, not an attraction — 45 min on foot, free, and the natural end point of a "
               "robotaxi ride. Tencent's Binhai towers are 1 km east.",
        watch="Weekday lunchtime is a wall of office workers; weekends are dead. No sights as such — go for "
              "the walk and the ride, not for a 'tech museum'.",
        img2=None),
    "oct": dict(
        img="oct", cap="OCT Loft (华侨城创意文化园) after dark",
        sweet="The lanes around **B10** and 旧天堂书店 — independent coffee, galleries, design shops. "
              "Best 16:00 onward when the light softens and the bars open.",
        expect="A former factory district; 1–2 h on foot. Free to wander, paid for whatever you drink.",
        watch="Weekday mornings are dead; weekends are busy with photo shoots. Some galleries close Mondays.",
        img2=None),
    "baypark": dict(
        img="baypark", cap="Shenzhen Bay Park (深圳湾公园) — the bayfront walk",
        sweet="The promenade at the **Shenzhen Bay Park** metro exit, walking west: Hong Kong's hills "
              "across the water, the Houhai towers behind. 30 min before sunset.",
        expect="Free, flat, 15 km of path. Bikes to rent, no shade in the middle of the day.",
        watch="It's a long walk — pick a direction and commit, or rent a bike. Weekends are packed with "
              "cyclists.",
        img2=None),
    "window": dict(
        img="window", cap="Window of the World (世界之窗) — the Eiffel replica and gardens",
        sweet="The Eiffel copy at dusk, and the evening parade/fireworks show on the central plaza.",
        expect="A theme park of 130 landmark replicas. ¥220ish, half a day if you go inside; the "
               "exterior plaza is free to look at.",
        watch="Kitsch by design — go with that in mind or skip it. Weekends mean queues at the rides.",
        img2=None),
    "spa": dict(
        img=None, cap="",
        sweet="A **21:00–22:30** slot — the city is lit, your feet are done, and it's 10 min from the hotel.",
        expect="金中环商务大厦 A座 21F, room 2109 (会展中心站 E). Chinese/Thai massage, oil and hot-stone; "
               "60–90 min treatments, ¥200–400. Open 10:30–23:30, last slots ~21:30.",
        watch="**Book ahead** on Klook, Trip.com or Ctrip — 21:00 walk-ins often wait. Say if you don't "
              "want oil. Showers and lockers are on site; bring your own underwear or use theirs.",
        img2=None),
    "nanyou": dict(
        img=None, cap="",
        sweet="Dozens of buildings of original-design women's wear in the 南海大道 / 东滨路 grid — "
              "the best-quality clothing market in the city.",
        expect="Higher grade than 白马 at 3–5× the price. 10:00–19:00, 1.5–2 h.",
        watch="25 min each way from the hotel in the wrong direction — only if clothing is the goal; "
              "skip 水贝 if you go.",
        img2=None),
}


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
    "WonderMeet": "wondermeet",
    "SEG Electronics Market": "seg",
    "Mingtong Cosmetics Market": "mingtong",
    "Zijingcheng Food Center": "zijingcheng",
    "Shuibei Jewelry Center": "shuibei",
    "Dongmen Baima Fashion Market": "baima",
    "Nanyou Clothing Market": "nanyou",
    "Manman Wellness SPA": "spa",
    "Shenzhen Bay Tech Park": "techpark",
    "OCT Loft": "oct",
    "Shenzhen Bay Park": "baypark",
    "Window of the World": "window",
}

FOOD = {
    "pingan": [("海底捞", "hotpot, COCO Park"), ("八合里海记", "Chaoshan beef hotpot")],
    "moca": [("中心书城", "book-mall food floor, 市民中心")],
    "upperhills": [("MUJI Diner", "in the mall"), ("深业上城", "upper-floor restaurants")],
    "mixc_crossing": [("万象城", "food hall + restaurants")],
    "dmd": [("东门町美食城", "you're standing in it")],
    "dongmen": [("东门小吃街", "street snacks, 老街 exit")],
    "talent": [("海岸城", "Coastal City food floor"), ("万象天地", "里巷 restaurants")],
    "happy": [("欢乐港湾", "waterfront restaurants")],
    "mixc_tiandi": [("万象天地 里巷", "outdoor restaurant lanes")],
    "poly": [("海岸城", "Coastal City, 10 min walk")],
    "nantou": [("南头古城", "courtyard cafés")],
    "oct": [("旧天堂书店", "bookshop café"), ("B10", "coffee + bars")],
    "baypark": [("海岸城", "10 min inland for a real meal")],
    "window": [("欧洲小镇", "cafés by the Eiffel copy")],
    "grand": [("万象城", "food hall next door")],
    "culture": [("景田", "neighbourhood noodle shops")],
}

def amap_search(name):
    return ("https://uri.amap.com/search?keyword=" + __import__("urllib.parse").parse.quote(name)
            + "&city=%E6%B7%B1%E5%9C%B3&src=trip&callnative=0")

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

    out = []
    A = out.append

    A("# Shenzhen trip plan\n")
    A("**Hotel:** 加来酒店 (Calais Hotel) — 深圳福田口岸店  ")
    A(f"**Address:** {HOTEL_ADDR_ZH}  ")
    A("**Phone:** [+86-755-88257999](tel:+8675588257999) · Booking [removed]\n")
    A("**Live page:** https://influx6.github.io/travel/  ")
    A("**Nearest metro:** 皇岗村 (Huanggangcun), Line 7, Exit A — 430 m / 7 min walk  ")
    A("**Also close:** Futian Checkpoint (福田口岸), Lines 4 & 10 — ~1.1 km / 15 min walk\n")
    A("21 places, sorted closest → furthest. Photos are freely licensed (credits at the bottom).\n")
    A("---\n")

    A("## 1. The short version\n")
    A("- **Arrive:** high-speed rail from West Kowloon to **福田 (Futian)** — 14 min, ¥68 — then a 3 km DiDi.")
    A("- **Two full days + a half-day:** Wed 25 Nov (arrive, Free Sky at sunset), Thu 26 Nov (WonderMeet + "
      "华强北 + 东门 markets), Fri 27 Nov (MOCA in the morning, 水贝 after 14:00 checkout, East Rail home).")
    A("- **Best of the list:** WonderMeet · Ping An Free Sky at sunset · DMD Food City · Upper Hills + "
      "莲花山公园 · 水贝 jewellery · Talent Park at sunset.")
    A("- **Skip:** **南头古城** (not worth the trip — see Fanny's note) · 文化馆 · 保利文化广场 · 东门町广场.")
    A("- **Money:** Alipay or WeChat Pay with a foreign card; metro gates also take contactless Visa/Mastercard.")
    A("- **Bring:** passport everywhere — trains, hotel, museums.\n")

    A("---\n")
    A("## 2. Getting from Tung Chung to the hotel\n")
    A("| Option | Route | Time | Cost | Verdict |")
    A("|---|---|---|---|---|")
    A("| **A. High-speed rail** | Tung Chung → Kowloon → walk to West Kowloon → HSR to 福田 → DiDi | 1 h 50 – 2 h 15 | ≈ HK$19 + ¥68 + ¥15 ≈ **HK$110** | Fastest, one immigration, easiest with bags |")
    A("| **B. East Rail** | Tung Chung → Nam Cheong (南昌) → Hung Hom (红磡) → East Rail → Lok Ma Chau (落马洲) → Futian Port (福田口岸) → ~1.1 km walk | 2 h 10 – 2 h 40 | **HK$57.5** | Cheapest; the port is next to the hotel |")
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


    A("---\n")
    A("## 3. Getting back to Hong Kong (East Rail, not HSR)\n")
    A("You asked for the regular train home — this is the 福田口岸 → 落马洲 crossing, which is the "
      "closest border to the hotel.\n")
    A("| Step | What | Time | Cost |")
    A("|---|---|---|---|")
    A("| 1 | Hotel → **福田口岸 (Futian Port)** — 1.1 km, walk or ¥10 DiDi | 15 min | ¥0–10 |")
    A("| 2 | HK exit + mainland exit at the port (two checks, one covered walkway) | 15–30 min | — |")
    A("| 3 | **落马洲 (Lok Ma Chau)** station, East Rail southbound | — | — |")
    A("| 4 | East Rail → 红磡 (Hung Hom), change to Tuen Ma Line → 南昌 (Nam Cheong) → Tung Chung Line | ~1 h 45 | **HK$57.5** total |")
    A("")
    A("**Timing that matters:** the port is open **06:30–22:30**, and the last East Rail trains leave "
      "落马洲 around **22:55**. Aim to be at the port by **21:00** so a queue can't strand you.\n")
    A("**What to expect:** the walkway is flat and covered, with moving walkways most of the way — easy "
      "with a suitcase. There's no duty-free shop worth stopping for. The East Rail is a normal commuter "
      "train: luggage racks at the carriage ends, no reservation, Octopus or contactless card.\n")
    A("**Alternative:** 罗湖 (Lo Wu) is the same line and the same fare — use it only if 福田口岸 is "
      "heaving, since it's further from the hotel.\n")
    A("---\n")
    A("## 4. Trains and metro — the details\n")
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
    A("**Driverless cars (robotaxi) — how to book**")
    A("Two operators run commercial driverless cars in Shenzhen:\n")
    A("- **Pony.ai (小马智行)** — the one to try. Citywide permit, zone covering 南山 / 前海 / 深圳湾, "
      "~10,000 pickup points, roughly **07:00–22:00**. Book in the **PonyPilot+** app or the WeChat "
      "mini-program (Pony.ai also appears inside Amap). It's the operator that accepts passports and "
      "foreign cards.")
    A("- **Apollo Go (萝卜快跑)** — 南山 / 宝安 / 坪山, **07:00–23:00**, but **station-to-station**: you "
      "walk to a green pickup dot (usually a bus stop or metro exit), you can't pick an exact address. "
      "App, WeChat mini-program, or Baidu Maps. Registration leans on Chinese ID.")
    A("")
    A("**Booking it, in order:**")
    A("1. Install **PonyPilot+** (or open its WeChat mini-program). Register with your phone; have your "
      "**passport** ready for verification — it takes about 10 minutes.")
    A("2. Set pickup + drop-off. Both must sit inside the green zone on the map; for Apollo Go, pick one of "
      "its fixed stations instead.")
    A("3. Request. Waits run 3–15 min off-peak; a busy Saturday can be longer.")
    A("4. Match the **plate and car number**, then unlock from the app (Bluetooth) or type the last four "
      "digits of your phone on the door screen.")
    A("5. Sit in the back (front seats are blocked), belt up, and tap **Start** on the seat screen.")
    A("")
    A("**Cost:** ¥10–30 for a 3–6 km hop. Pony.ai runs ~50% above DiDi; Apollo Go often has promo vouchers "
      "that make it cheaper than a taxi.\n")
    A("**The catch, honestly:** both apps can demand a **+86 phone number** for SMS verification, and "
      "reports differ on whether a foreign SIM gets through. If yours fails, try the WeChat mini-program "
      "(separate registration, sometimes laxer), or ask the hotel front desk to book on their account — "
      "that works and is common. Weather also suspends service, and no eating or drinking in the car.\n")
    A("**The ride to take on this trip:** a 3.5 km hop in Nanshan, **万象天地 → 深圳湾科技生态园** "
      "(~12 min, ¥15–25). It's squarely inside the zone, it lands you at the tech park, and you can walk "
      "the waterfront to 人才公园 afterwards. Book it while you're finishing lunch — if verification "
      "stalls, DiDi is 20 m away.\n")
    A("**About direct DiDi links:** DiDi has no public link format that pre-fills an origin and "
      "destination. The supported way is DiDi's own API (the DiDi MCP, `taxi_generate_ride_app_link`, "
      "free key at mcp.didichuxing.com), which returns a `v.didi.cn` link that opens the app with both "
      "ends filled in. If you want those 14 links generated, get a key and I'll wire them in. "
      "Until then, each place below gives you a **copy-paste Chinese block** for the DiDi destination "
      "field, plus an Amap route link.\n")

    A("**Buying the paid tickets online**")
    A("- **Free Sky (Ping An):** open **Trip.com** (English app, foreign cards accepted) and search "
      "*\"Ping An Finance Center Free Sky\"* — ¥180 instead of ¥200 at the counter. **Klook** sells the "
      "same ticket. Ctrip/携程 and Meituan/大众点评 are usually cheapest but need Alipay or WeChat Pay. "
      "The official WeChat mini-program is called 平安金融中心云际观光层.")
    A("- **WonderMeet (玩美攻略):** Klook and Trip.com list it around HK$192–206; you can also just pay "
      "at the door (¥268 weekday / ¥298 weekend) — walk-ins are normal. Night ticket ¥168 after 19:00.")
    A("- **Bay Glory wheel (欢乐港湾):** KKday, Klook or Trip.com, or buy at the wheel. ¥150 (¥180 holidays).")
    A("- **How it works:** you get a QR code in the app. Show it at the counter; they scan it and print/"
      "link your wristband. No passport needed for the standard adult ticket — bring it only if you're "
      "claiming a student/senior/child rate.")
    A("- **Tip:** book the Free Sky for a specific sunset slot the day before; weekends sell out by "
      "mid-afternoon.\n")

    A("---\n")
    A("## 5. Places, closest → furthest\n")
    A("`km` straight line from the hotel · `DiDi` road distance/time · `Metro` door-to-door · `Fun` 1–10\n")
    A("### Sights\n")
    A("| # | Place | 中文 | Area | km | DiDi | Metro | Fun |")
    A("|---|---|---|---|---|---|---|---|")
    for r in [x for x in rows if x.get('group') != 'venue']:
        A(f"| {r['rank']} | {r['name']} | {r['chinese_name']} | {r['area']} | {r['distance_km_straight']} | "
          f"{r['didi_min']} min · {r['didi_km']} km · {r['didi_cost']} | {r['metro_plan']} · {r['metro_min']} min | "
          f"**{r['fun_factor_1_10']}** |")
    A("")
    A("### WonderMeet + the markets\n")
    A("| # | Place | 中文 | km | DiDi | Metro | Fun |")
    A("|---|---|---|---|---|---|---|")
    for r in [x for x in rows if x.get('group') == 'venue']:
        A(f"| {r['rank']} | [{r['name']}]({r['amap_link']}) | {r['chinese_name']} | "
          f"{r['distance_km_straight']} | "
          f"{r['didi_min']} min · {r['didi_km']} km · {r['didi_cost']} | {r['metro_plan']} · {r['metro_min']} min | "
          f"**{r['fun_factor_1_10']}** |")
    A("")

    EXTRA = {
        'pingan': [('pingan_sunset', 'From the 116F deck at sunset — Shenzhen Bay on the left, Futian below')],
        'talent': [('talent_sunset', 'The Shenzhen Bay skyline from the Talent Park waterfront')],
        'upperhills': [('lianhua_sunset', 'Dusk over the Futian CBD from the top of 莲花山公园')],
        'happy': [('happy_wheel', "Bay Glory (湾区之光), 128 m, on the Bao'an waterfront")],
    }
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
            A(f"*{e['img2cap']}*")
        for ek, ecap in EXTRA.get(key, []):
            A(f"![{ecap}](images/{ek}.jpg)")
            A(f"*{ecap}*")
        A("")
        if e.get('review'):
            A("#### Fanny's review\n")
            A(f"> {e['review']}\n")
            A(f"{e['verdict']}\n")
        A(f"**Fun {r['fun_factor_1_10']}/10** · {r['area']} · {r['type']} · "
          f"**{r['distance_km_straight']} km** from the hotel\n")
        A(f"- **Getting there:** {r['metro_plan']} (~{r['metro_min']} min) or DiDi "
          f"{r['didi_min']} min / {r['didi_km']} km, **{r['didi_cost']}**.")
        A(f"- **Sweet spot:** {e['sweet']}")
        A(f"- **What to expect:** {e['expect']}")
        A(f"- **Look out for:** {e['watch']}")
        if key in FOOD:
            bits = [f"[{zh}]({amap_search(zh)}) — {note}" for zh, note in FOOD[key]]
            A(f"- **Eat nearby:** {' · '.join(bits)}")
        A(f"- **Links:** [Amap pin]({r['amap_link']}) · [Amap route from hotel]({r['amap_route_link']}) · "
          f"[Google Maps]({r['google_link']})")
        A(f"- **DiDi destination (copy this):**")
        A(f"  ```")
        A(f"  {r['chinese_name']}")
        A(f"  ```")
        A("")

    A("---\n")
    A("## 6. The three days\n")
    A("Wednesday 25 Nov · Thursday 26 Nov · Friday 27 Nov (checkout by 14:00). "
      "Two full days plus a half-day.\n")
    A("### Weather (forecast for these dates)\n")
    A("| Day | Temp | Rain | Sky | What to wear |")
    A("|---|---|---|---|---|")
    A("| Wed 25 Nov | 13–19 °C | 14% | Cloudy, drizzle | Layers: tee + light jacket. Cool in the evening. |")
    A("| Thu 26 Nov | 14–23 °C | 33% | Overcast | Same, plus a compact umbrella — the day you're walking markets. |")
    A("| Fri 27 Nov | 16–26 °C | 18% | Mainly clear | Lightest day; a shirt is enough by afternoon. |")
    A("")
    A("*Shenzhen in late November is dry-season cool: 13–16 °C at 08:00, 19–26 °C by 14:00, dropping fast "
      "after 18:00. Comfortable walking shoes matter more than a coat. Check the morning you set off — "
      "a cold front can take 5 °C off in a day.*\n")

    A("### Wednesday 25 Nov — the west side: mall, bay, spa\n")
    A("| Time | What | Cost |")
    A("|---|---|---|")
    A("| On arrival | Check in at 加来酒店, drop bags. | — |")
    A("| 13:00 | DiDi to **MixC World 万象天地** (Nanshan) — 23 min. Lunch, then the outdoor lanes. "
      "Swap for 深圳万象城 (Luohu) if you'd rather stay east. | ¥46–60 |")
    A("| 14:45 | **Robotaxi** (PonyPilot+) from 万象天地 to **深圳湾科技生态园** — 3.5 km, ~12 min. "
      "See the robotaxi guide in §4. | ¥15–25 |")
    A("| 15:00–16:00 | **Tech park + 人才公园 waterfront** on foot — glass towers, open water, the "
      "Houhai skyline. | free |")
    A("| 16:15 | DiDi to **Happy Harbour** (Bao'an) — 25 min. | ~¥50 |")
    A("| 16:45–19:00 | **Bay Glory wheel** (¥150) + the waterfront. Sunset is ~17:35; stay for the light show. | ¥150 |")
    A("| 19:00 | Dinner on the waterfront. | ¥60–100 |")
    A("| 20:15 | DiDi back east to 会展中心 — 30 min. | ~¥60 |")
    A("| 21:00–22:30 | **Manman Wellness SPA** — 金中环商务大厦 A座 21F, room 2109 (会展中心站 E exit). "
      "Open to 23:30; book ahead. | ¥200–400 |")
    A("| 22:45 | DiDi home — 10 min. | ~¥14 |")
    A("")
    A("**This is the long day** — one DiDi chain west and back. If you land after 14:00, cut MixC World and "
      "go straight to Happy Harbour; the wheel still works. If you're wrecked, the spa is the part to keep "
      "— it's 10 minutes from the hotel, not 30.\n")

    A("### Thursday 26 Nov — the fun day\n")
    A("| Time | What | Cost |")
    A("|---|---|---|")
    A("| 09:40 | L4 福田口岸 → 会展中心 → L1 华强路 (4 stops, ~22 min) | ¥3 |")
    A("| 10:00–15:00 | **WonderMeet (玩美攻略)**, 世纪汇 1–3F: go-karts, laser tag, ice rink, PS5/Switch, "
      "KTV pods, arcade, bowling. Wristband = re-entry all day; lunch inside or in 世纪汇. | ¥268 (Thu) |")
    A("| 15:15 | Walk 5 min to **SEG Electronics Market** (华强北路1002号) — 30–45 min | free |")
    A("| 16:00 | **紫荆城食品交易中心** (振兴路55号) — imported snacks, buy a box | free |")
    A("| 16:45 | **明通化妆品市场** — cosmetics, check batch codes | free |")
    A("| 17:30 | L1 华强路 → 老街 (2 stops) — into 东门 | ¥2 |")
    A("| 17:45–19:00 | **东门白马服装市场** — 2F women's, 5F export surplus. Late afternoon is when they clear stock. | free |")
    A("| 19:00 | Dinner at **DMD Food City** (东门町美食城) — the best cheap eating on the trip | ¥40–60 |")
    A("| 20:00 | 东门步行街 for the neon, then L1/L3 home | ¥2 |")
    A("")
    A("**Why this order:** WonderMeet is the only fixed-cost, fixed-hour block — do it first while you're "
      "fresh. The 华强北 markets are a 5-minute walk apart, and 16:00–18:30 is when vendors start clearing "
      "stock (see the haggling section below). 东门 is on the way home.\n")

    A("### Friday 27 Nov — checkout 14:00, skyline, home\n")
    A("| Time | What |")
    A("|---|---|")
    A("| 09:30 | Breakfast, pack, leave the big bag at reception. |")
    A("| 10:00–11:30 | **MOCA** (free, Tue–Sun from 10:00) — L4 福田口岸 → 市民中心, 3 stops. |")
    A("| 12:00 | Lunch near 市民中心 / 购物公园. |")
    A("| 13:30 | Back to the hotel; **14:00 checkout**, bags stay at reception. |")
    A("| 14:30–16:00 | **Ping An Free Sky** — 8 min DiDi from the hotel. Daylight rather than sunset, "
      "but you see the whole bay and there's no queue. |")
    A("| 16:15 | Collect the bags at the hotel. |")
    A("| 16:45 | DiDi to **福田口岸** — 20 min, ~¥25. |")
    A("| 17:15 | Cross at 福田口岸 (open to 22:30) → 落马洲 → East Rail home. |")
    A("")
    A("**Swaps for the afternoon:** if you'd rather shop than go up a tower, take **水贝珠宝 (Shuibei "
      "Jewelry)** — 25 min DiDi, gold and jade, 15:00–16:30 — or **南油服装市场** for designer clothing "
      "(25 min each way, the best clothing market in the city). Both mean leaving the hotel by 14:20 and "
      "going straight to the port afterwards. **Upper Hills + 莲花山公园** is the third option and the "
      "closest to the hotel.\n")
    A("**Don't cut it close:** be at the port by **18:00–18:30**. Friday evening queues build, and the last "
      "East Rail trains leave 落马洲 around 22:55.\n")

    A("---\n")
    A("## 7. Wholesale markets — how to buy without getting tourist-priced\n")
    A("The rule of the trade: **look like a buyer, not a shopper.**\n")
    A("**The black bag.** Carry a plain black plastic bag (the kind stallholders use for stock). It's the "
      "universal signal that you're 拿货 — taking goods for resale — and it changes the price you're quoted "
      "before you say a word. Fold it under your arm; don't put your shopping in it.\n")
    A("**The script:**")
    A("1. Point at the item and ask **\"拿货几多？\"** (na huo ji duo — \"what's the stock price?\") "
      "rather than \"多少钱？\" (retail phrasing).")
    A("2. Ask **\"几件起？\"** (ji jian qi — \"minimum how many pieces?\"). Two or three is normal at "
      "东门白马; 水贝 and 南油 often sell singles.")
    A("3. When they quote, **counter at half** and stay friendly. Settle around 55–65% of the opening price.")
    A("4. If they won't move, **start walking** — the second price usually arrives before you reach the door.")
    A("5. Pay with **WeChat/Alipay**; a few older stalls still prefer cash. Never hand over money before "
      "you've counted the goods.")
    A("")
    A("**Timing:** **from 16:00 they bargain hardest** — the last two hours before closing, when vendors "
      "clear stock and quotes go soft. Mornings are for restocking and the price is firm. Most buildings "
      "shut 18:00–19:00, so don't arrive at 18:45.\n")
    A("**For bigger deals:** ask for the **天虹 (Tianhong) clearance building** — the locals' answer when "
      "you want volume rather than one-off pieces, and where the serious buyers work. Ask any stallholder "
      "to point you to it; it isn't signposted in English.\n")
    A("**What to check:**")
    A("- **Cosmetics (明通):** batch code and expiry on the box; unboxed testers are not the deal they look.")
    A("- **Jewellery (水贝):** price = gold weight × daily rate + **工费** (labour fee). Ask the 工费 "
      "separately, ask for the certificate, and weigh it yourself if you can.")
    A("- **Clothing (白马 / 南油):** try before paying where possible; sizes run small. 南油 is original "
      "design and costs 3–5× 白马 — different market, don't compare prices.")
    A("- **Electronics (SEG):** know the online price first; check the IMEI/serial and that it's not "
      "refurbished.\n")
    A("**Border note:** bringing commercial quantities back to Hong Kong can attract duty — keep receipts, "
      "and if it looks like stock rather than personal use, declare it.\n")

    A("---\n")
    A("## 8. Amap (高德地图)\n")
    A("Amap share links cap at **10 points**, so the list is split into three:\n")
    A(f"- **Futian + Luohu (9 places):** [open in Amap]({links['futian_luohu']})")
    A(f"- **Nanshan + Bao'an (5 places):** [open in Amap]({links['nanshan_baoan']})")
    A(f"- **WonderMeet + markets (7):** [open in Amap]({links['markets']})")
    A("")
    A("Open on your phone with the Amap app installed and it opens in-app.\n")
    A("**Save all 21 to your Amap account:**")
    A("1. On a **PC**, open **wia.amap.com** and sign in.")
    A("2. Create a map → **批量导入 (bulk import)** → upload **`amap_import.csv`**.")
    A("3. Columns: 名称 / 经纬度 / 地址 / 颜色 / 描述 / 文件夹. Coordinates are **经度,纬度** in **GCJ-02**.")
    A("4. Imported points sync to the 收藏 (Favorites) folder in your phone app.\n")
    A("If they insist on their own template, download it and paste these columns in — the template must "
      "be used unchanged.\n")

    A("---\n")
    A("## 9. Notes\n")
    A("- **Coordinates:** Google and Amap both use **GCJ-02** in mainland China; `places.csv` gives GCJ "
      "(works in both) plus WGS-84 for GPS tools. They differ by ~500 m — don't mix them.")
    A("- **Closures:** MOCA closed Mondays · Happy Harbour wheel opens 14:00 on Tuesdays · "
      "Futian Port closes 22:30.")
    A("- **Prices:** Free Sky ¥180–200 · WonderMeet ¥268/¥298 · Bay Glory ¥150–180 · markets are free to enter.")
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
    A("- `index.html` — the mobile-friendly plan (served on GitHub Pages; tap the sun/moon icon to switch theme)")
    A("- `Shenzhen-plan.pdf` / `Shenzhen-plan-dark.pdf` — print/offline versions (light / dark)")
    A("- `places.csv` — all 21 places with GCJ/WGS coordinates, Amap + Google links, times and notes")
    A("- `amap_import.csv` — bulk-import file for wia.amap.com")
    A("- `amap_links.md` — every Amap link in one place")
    A("- `booking.md` — hotel confirmation and reviews")
    A("- `images/` — photos (credits above)")
    A("- `tools/` — the scripts that generated all of this")

    open('../README.md', 'w', encoding='utf-8').write("\n".join(out) + "\n")
    print("README written:", len("\n".join(out)), "chars")


if __name__ == '__main__':
    main()

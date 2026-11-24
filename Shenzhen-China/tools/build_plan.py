"""Build the Shenzhen trip dataset: distances, metro plans, Amap/Google links, CSVs.

Coordinate model: Google Maps mainland-China coordinates are GCJ-02 (verified by
reverse-geocoding the raw values on Amap, which returned the correct POIs). Amap
also uses GCJ-02, so Google values are used as-is for Amap links and imports.
WGS-84 equivalents are derived for GPS/other tools.
"""
import json, math, csv, urllib.parse, os

HOTEL = {"name": "Calais Hotel (加来酒店)", "lat": 22.52147, "lng": 114.05994}

PLACES = [
    dict(key="pingan", name="Ping'an International Financial Center", zh="平安金融中心",
         area="Futian", kind="Observation deck", fun=8,
         note="Free Sky deck on 116F (547 m). ¥180 online / ¥200 on site; 10:00-20:00 (Fri-Sat 21:00). "
              "Enter ~16:30 for sunset. Metro: 购物公园 Exit D.",
         metro="Shopping Park 购物公园 (L1/L3)", metro_walk=210,
         metro_plan="L4 Futian Checkpoint → Convention & Exhibition Center → L1 Shopping Park (3 stops)",
         metro_min=16, cluster="Futian"),
    dict(key="nantou", name="Nantou Ancient City", zh="南头古城",
         area="Nanshan", kind="Historic quarter", fun=5,
         note="Restored old village turned shopping street. Your contact found it thin — "
              "treat it as a coffee/food stop (1.5-2 h), not a headline sight.",
         metro="Nantou Ancient City 南头古城 (L12)", metro_walk=580,
         metro_plan="L7 Huanggangcun → Chegongmiao → L1 Taoyuan → L12 Nantou Ancient City (2 changes)",
         metro_min=55, cluster="West"),
    dict(key="dmd", name="DMD Food City (东门町美食城)", zh="东门町美食城",
         area="Luohu", kind="Street-food hall", fun=7,
         note="Dense snack stalls in Dongmen; the best cheap eating on the list. Go hungry, in the evening.",
         metro="Laojie 老街 (L1/L3)", metro_walk=310,
         metro_plan="L4 Futian Checkpoint → Convention & Exhibition Center → L1 Laojie (2 + 5 stops)",
         metro_min=30, cluster="East"),
    dict(key="dingplaza", name="Dong Men Ding Plaza", zh="东门町广场",
         area="Luohu", kind="Shopping mall", fun=3,
         note="Generic mall attached to the food city — useful only as a shortcut or an AC break.",
         metro="Dongmen 东门 (L5) / Laojie 老街 (L1/L3)", metro_walk=230,
         metro_plan="As DMD Food City, then 230 m walk",
         metro_min=31, cluster="East"),
    dict(key="dongmen", name="Dongmen Pedestrian Street", zh="东门步行街",
         area="Luohu", kind="Shopping street", fun=6,
         note="Shenzhen's original bargain-shopping street. Loud, cheap, snack-heavy — 1-2 h is plenty.",
         metro="Hubei 湖贝 (L2/L5) / Laojie 老街 (L1/L3)", metro_walk=390,
         metro_plan="L4 Futian Checkpoint → Civic Center → L2 Hubei (3 + 5 stops)",
         metro_min=32, cluster="East"),
    dict(key="talent", name="Shenzhen Talent Park", zh="深圳人才公园",
         area="Nanshan", kind="Waterfront park", fun=8,
         note="Free bay-front loop with the Houhai skyline. Best light 17:00-18:30; "
              "pair with dinner in Houhai. Metro: 人才公园 Exit.",
         metro="Talent Park 人才公园 (L13)", metro_walk=320,
         metro_plan="L7 Huanggangcun → Chegongmiao → L11 Houhai → L13 Talent Park",
         metro_min=45, cluster="West"),
    dict(key="happy", name="Happy Harbour", zh="欢乐港湾",
         area="Bao'an", kind="Waterfront + ferris wheel", fun=8,
         note="'Bay Glory' wheel ¥150 (¥180 holidays), 10:30-22:00. Promenade + evening light show. "
              "Metro: 临海 Exit B2.",
         metro="Linhai 临海 (L5)", metro_walk=490,
         metro_plan="L7 Huanggangcun → Chegongmiao → L11 Qianhai Bay → L5 Linhai",
         metro_min=50, cluster="West"),
    dict(key="grand", name="Shenzhen Grand Theatre", zh="深圳大剧院",
         area="Luohu", kind="Performing arts", fun=4,
         note="Only worth it with a booked performance; otherwise a pass-by near Mixc City Crossing.",
         metro="Grand Theater 大剧院 (L1/L2/L5)", metro_walk=300,
         metro_plan="L4 Futian Checkpoint → Civic Center → L2 Grand Theater (3 + 4 stops)",
         metro_min=28, cluster="East"),
    dict(key="moca", name="Museum of Contemporary Art & Planning Exhibition", zh="深圳当代艺术与城市规划馆",
         area="Futian", kind="Museum", fun=7,
         note="Free, no booking, Tue-Sun 10:00-18:00 (closed Mondays). Giant city model + "
              "the 改革开放 exhibition; striking building.",
         metro="Civic Center 市民中心 (L2/L4)", metro_walk=340,
         metro_plan="L4 Futian Checkpoint → Civic Center (3 stops) + 340 m walk",
         metro_min=18, cluster="Futian"),
    dict(key="mixc_tiandi", name="MixC World 万象天地 (Nanshan)", zh="万象天地",
         area="Nanshan", kind="Lifestyle mall", fun=7,
         note="Best-designed mall in town: outdoor lanes, flagships, strong restaurant floor.",
         metro="Hi-Tech Park 高新园 (L1)", metro_walk=220,
         metro_plan="L7 Huanggangcun → Chegongmiao → L1 Hi-Tech Park (4 + 6 stops)",
         metro_min=40, cluster="West"),
    dict(key="poly", name="Shenzhen Poly Cultural Plaza", zh="深圳保利文化广场",
         area="Nanshan", kind="Mall + theatre", fun=3,
         note="Local mall/theatre by Talent Park — a convenience stop, not a destination.",
         metro="Houhai 后海 (L2/L11/L13)", metro_walk=180,
         metro_plan="L7 Huanggangcun → Chegongmiao → L11 Houhai (4 + 2 stops)",
         metro_min=40, cluster="West"),
    dict(key="upperhills", name="Upper Hills (深业上城)", zh="深业上城",
         area="Futian", kind="Lifestyle mall + park bridge", fun=7,
         note="Big open-air mall: coffee, design shops, rooftop-style lanes. A footbridge links it "
              "straight into 莲花山公园 — 15-20 min up to the Deng Xiaoping statue for the classic "
              "CBD skyline sunset, free. Best half-day: coffee here, park at golden hour.",
         metro="Donggualing 冬瓜岭 (L10)", metro_walk=580,
         metro_plan="L10 Futian Checkpoint → Donggualing (5 stops, direct)",
         metro_min=25, cluster="Futian"),
    dict(key="culture", name="Shenzhen Cultural Center (Jingtian)", zh="深圳市文化馆",
         area="Futian", kind="Arts venue", fun=3,
         note="Neighbourhood arts centre at 景田东路2号. Check the programme; first-trip travellers can skip it.",
         metro="Jingtian 景田 (L2/L9)", metro_walk=200,
         metro_plan="L4 Futian Checkpoint → Civic Center → L2 Jingtian (3 + 3 stops)",
         metro_min=28, cluster="Futian"),
    dict(key="mixc_crossing", name="The Mixc of Shenzhen City Crossing", zh="深圳万象城",
         area="Luohu", kind="Luxury mall", fun=5,
         note="Classic luxury mall — good rain plan, food court and cinema.",
         metro="Grand Theater 大剧院 (L1/L2/L5)", metro_walk=340,
         metro_plan="L4 Futian Checkpoint → Civic Center → L2 Grand Theater (3 + 4 stops)",
         metro_min=28, cluster="East"),
]

DRIVING = {
    "Ping'an International Financial Center": (8, 3.0),
    "Nantou Ancient City": (24, 21.7),
    "DMD Food City": (25, 9.4),
    "Dong Men Ding Plaza": (25, 9.5),
    "Shenzhen Dongmen Commercial Pedestrian Street Unit Management Office": (25, 9.7),
    "Shenzhen Talent Park": (25, 16.5),
    "Happy Harbour": (31, 25.4),
    "Shenzhen Grand Theatre": (19, 7.2),
    "Museum of Contemporary Art & Planning Exhibition": (12, 3.5),
    "萬象天地 The Mixc": (23, 16.6),
    "Shenzhen Poly Cultural Plaza": (23, 16.3),
    "Shenzhen Cultural Center": (16, 6.4),
    "The Mixc of Shenzhen City Crossing": (21, 8.1),
    "Shenye Upper Hills": (14, 5.6),
}
KEYMAP = {"pingan": "Ping'an International Financial Center", "nantou": "Nantou Ancient City",
          "dmd": "DMD Food City", "dingplaza": "Dong Men Ding Plaza",
          "dongmen": "Shenzhen Dongmen Commercial Pedestrian Street Unit Management Office",
          "talent": "Shenzhen Talent Park", "happy": "Happy Harbour", "grand": "Shenzhen Grand Theatre",
          "moca": "Museum of Contemporary Art & Planning Exhibition", "mixc_tiandi": "萬象天地 The Mixc",
          "poly": "Shenzhen Poly Cultural Plaza", "culture": "Shenzhen Cultural Center",
          "upperhills": "Shenye Upper Hills",
          "mixc_crossing": "The Mixc of Shenzhen City Crossing"}


def gcj02_to_wgs84(lat, lon):
    a = 6378245.0; ee = 0.00669342162296594323
    def _tlat(x, y):
        r = -100.0 + 2.0*x + 3.0*y + 0.2*y*y + 0.1*x*y + 0.2*math.sqrt(abs(x))
        r += (20.0*math.sin(6.0*x*math.pi) + 20.0*math.sin(2.0*x*math.pi))*2.0/3.0
        r += (20.0*math.sin(y*math.pi) + 40.0*math.sin(y/3.0*math.pi))*2.0/3.0
        r += (160.0*math.sin(y/12.0*math.pi) + 320*math.sin(y*math.pi/30.0))*2.0/3.0
        return r
    def _tlon(x, y):
        r = 300.0 + x + 2.0*y + 0.1*x*x + 0.1*x*y + 0.1*math.sqrt(abs(x))
        r += (20.0*math.sin(6.0*x*math.pi) + 20.0*math.sin(2.0*x*math.pi))*2.0/3.0
        r += (20.0*math.sin(x*math.pi) + 40.0*math.sin(x/3.0*math.pi))*2.0/3.0
        r += (150.0*math.sin(x/12.0*math.pi) + 300.0*math.sin(x/30.0*math.pi))*2.0/3.0
        return r
    def fwd(la, lo):
        dlat = _tlat(lo-105.0, la-35.0); dlon = _tlon(lo-105.0, la-35.0)
        rad = la/180.0*math.pi; magic = 1 - ee*math.sin(rad)**2
        sq = math.sqrt(magic)
        dlat = (dlat*180.0)/((a*(1-ee))/(magic*sq)*math.pi)
        dlon = (dlon*180.0)/(a/sq*math.cos(rad)*math.pi)
        return la+dlat, lo+dlon
    g = (lat, lon)
    for _ in range(8):
        f = fwd(*g)
        g = (g[0] - (f[0] - lat), g[1] - (f[1] - lon))
    return g


def haversine(a, b):
    R = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = p2-p1; dl = math.radians(b[1]-a[1])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))


def main():
    raw = {p['name']: p for p in json.load(open('out/places_raw.json'))}
    rows = []
    for p in PLACES:
        src = raw[KEYMAP[p['key']]]
        lat, lng = src['coords']
        wlat, wlng = gcj02_to_wgs84(lat, lng)
        dmin, dkm = DRIVING[KEYMAP[p['key']]]
        p.update(lat_gcj=round(lat, 6), lng_gcj=round(lng, 6),
                 lat_wgs=round(wlat, 6), lng_wgs=round(wlng, 6),
                 straight_km=round(haversine((HOTEL['lat'], HOTEL['lng']), (lat, lng)), 2),
                 didi_min=dmin, didi_km=dkm, raw=src)
        rows.append(p)

    rows.sort(key=lambda r: r['straight_km'])
    for i, r in enumerate(rows, 1):
        r['rank'] = i

    os.makedirs('out', exist_ok=True)

    with open('../places.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['rank', 'name', 'chinese_name', 'area', 'type', 'fun_factor_1_10',
                    'distance_km_straight', 'didi_km', 'didi_min', 'nearest_metro', 'metro_walk_m',
                    'metro_plan', 'metro_min', 'lat_gcj02', 'lng_gcj02', 'lat_wgs84', 'lng_wgs84',
                    'amap_link', 'amap_route_link', 'google_link', 'why'])
        for r in rows:
            amap = (f"https://uri.amap.com/marker?position={r['lng_gcj']},{r['lat_gcj']}"
                    f"&name={urllib.parse.quote(r['name'])}&src=trip&coordinate=gaode&callnative=0")
            route = (f"https://uri.amap.com/navigation?from={HOTEL['lng']},{HOTEL['lat']},Hotel"
                     f"&to={r['lng_gcj']},{r['lat_gcj']},{urllib.parse.quote(r['name'])}"
                     f"&mode=bus&coordinate=gaode&callnative=0")
            w.writerow([r['rank'], r['name'], r['zh'], r['area'], r['kind'], r['fun'], r['straight_km'],
                        r['didi_km'], r['didi_min'], r['metro'], r['metro_walk'], r['metro_plan'],
                        r['metro_min'], r['lat_gcj'], r['lng_gcj'], r['lat_wgs'], r['lng_wgs'],
                        amap, route, r['raw']['href'], r['note']])

    # Amap map-mini-program import template: 名称,经纬度,地址,颜色,描述,文件夹
    with open('../amap_import.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['名称', '经纬度', '地址', '颜色', '描述', '文件夹'])
        for r in rows:
            addr = r['raw'].get('address') or ''
            w.writerow([r['zh'], f"{r['lng_gcj']},{r['lat_gcj']}", addr, '',
                        f"Fun {r['fun']}/10. {r['note']}", r['area']])

    groups = {'futian_luohu': [r for r in rows if r['cluster'] in ('Futian', 'East')],
              'nanshan_baoan': [r for r in rows if r['cluster'] == 'West']}
    links = {}
    for gname, g in groups.items():
        markers = '|'.join(f"{r['lng_gcj']},{r['lat_gcj']},{urllib.parse.quote(r['name'])}" for r in g)
        links[gname] = f"https://uri.amap.com/marker?markers={markers}&src=trip&coordinate=gaode&callnative=0"

    # Sidecar sheet: every Amap link in one file
    lines = ["# Amap links", "", "## All places (Amap caps a link at 10 points)", "",
             f"- Futian + Luohu: {links['futian_luohu']}",
             f"- Nanshan + Bao'an: {links['nanshan_baoan']}", "",
             "## Hotel",
             f"- https://uri.amap.com/marker?position={HOTEL['lng']},{HOTEL['lat']}"
             f"&name=%E5%8A%A0%E6%9D%A5%E9%85%92%E5%BA%97&src=trip&coordinate=gaode&callnative=0", "",
             "## One link per place", ""]
    for r in rows:
        pin = (f"https://uri.amap.com/marker?position={r['lng_gcj']},{r['lat_gcj']}"
               f"&name={urllib.parse.quote(r['name'])}&src=trip&coordinate=gaode&callnative=0")
        route = (f"https://uri.amap.com/navigation?from={HOTEL['lng']},{HOTEL['lat']},Hotel"
                 f"&to={r['lng_gcj']},{r['lat_gcj']},{urllib.parse.quote(r['name'])}"
                 f"&mode=bus&coordinate=gaode&callnative=0")
        lines += [f"### {r['name']} ({r['zh']})", f"- Pin: {pin}", f"- Route from hotel: {route}", ""]
    open('../amap_links.md', 'w', encoding='utf-8').write("\n".join(lines))

    json.dump({'hotel': HOTEL, 'places': rows, 'links': links},
              open('out/plan.json', 'w'), ensure_ascii=False, indent=1)

    print(f"{'#':>2} {'place':44s} {'km':>6} {'DiDi':>12} {'metro':>6} {'fun':>4}")
    for r in rows:
        print(f"{r['rank']:>2} {r['name'][:44]:44s} {r['straight_km']:6.2f} "
              f"{r['didi_min']:>3}min/{r['didi_km']:>4.1f}km {r['metro_min']:>4}min {r['fun']:>4}")
    print('\nlinks:')
    for k, v in links.items():
        print(k, len(v), 'chars')


if __name__ == '__main__':
    main()

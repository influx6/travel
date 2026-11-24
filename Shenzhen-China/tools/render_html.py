"""Render a mobile-first HTML plan from the dataset + editorial notes."""
import csv, json, html, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_readme import EDIT, key_for, FOOD, amap_search

E = html.escape
import re as _re
def mini(t):
    """Escape then render **bold** / *italic* from the markdown source."""
    t = E(t or '')
    t = _re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = _re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', t)
    return t

def main():
    rows = list(csv.DictReader(open('../places.csv', encoding='utf-8-sig')))
    plan = json.load(open('out/plan.json'))
    links = plan['links']
    sights = [r for r in rows if not r['name'] in [
        'WonderMeet', 'SEG Electronics Market', 'Mingtong Cosmetics Market', 'Zijingcheng Food Center',
        'Shuibei Jewelry Center', 'Dongmen Baima Fashion Market', 'Nanyou Clothing Market']]
    venues = [r for r in rows if r not in sights]
    credits = json.load(open('out/image_credits.json'))

    EXTRA = {
        'pingan': [('pingan_sunset', 'From the 116F deck at sunset')],
        'talent': [('talent_sunset', 'The bay skyline from the park')],
        'upperhills': [('lianhua_sunset', 'Dusk from 莲花山公园')],
        'happy': [('happy_wheel', 'Bay Glory, 128 m')],
    }

    def card(r):
        key = key_for.get(r['name'])
        e = EDIT.get(key, {})
        imgs = []
        if e.get('img'):
            imgs.append((e['img'], e['cap']))
        if e.get('img2'):
            imgs.append((e['img2'], e['img2cap']))
        for ek, ecap in EXTRA.get(key, []):
            imgs.append((ek, ecap))
        pic = ''.join(
            f'<figure><img src="images/{i}.jpg" alt="{E(c)}" loading="lazy"><figcaption>{E(c)}</figcaption></figure>'
            for i, c in imgs)
        phcls = 'ph single' if len(imgs) == 1 else 'ph'
        food = ''
        if key in FOOD:
            bits = ' · '.join(f'<a href="{amap_search(zh)}">{E(en)} ({E(zh)})</a> — {E(note)}' for en, zh, note in FOOD[key])
            food = f'<p><b>Eat nearby:</b> {bits}</p>'
        rev = ''
        if e.get('review'):
            rev = (f'<aside class="review"><h4>Fanny\'s review</h4>'
                   f'<blockquote>{mini(e["review"])}</blockquote>'
                   f'<p>{mini(e["verdict"])}</p></aside>')
        return f'''
        <article class="place" id="{key or r['rank']}">
          <div class="{phcls}">{pic}</div>
          {rev}
          <div class="pb">
            <h3>{E(r['name'])} <span class="zh">{E(r['chinese_name'])}</span></h3>
            <p class="meta"><span class="fun">Fun {r['fun_factor_1_10']}/10</span>
               <span>{E(r['area'])}</span> · <span>{r['distance_km_straight']} km</span> ·
               <span>DiDi {r['didi_min']} min · {r['didi_km']} km · {r['didi_cost']}</span></p>
            <p class="go"><b>Getting there:</b> {E(r['metro_plan'])} · {r['metro_min']} min</p>
            {f'<p><b>Sweet spot:</b> {mini(e["sweet"])}</p>' if e.get('sweet') else ''}
            {f'<p><b>Expect:</b> {mini(e["expect"])}</p>' if e.get('expect') else ''}
            {f'<p class="warn"><b>Look out:</b> {mini(e["watch"])}</p>' if e.get('watch') else ''}
            {food}
            <p class="links"><a href="{r['amap_link']}">Amap pin</a>
              <a href="{r['amap_route_link']}">Amap route</a>
              <a href="{r['google_link']}">Google Maps</a></p>
            <details><summary>DiDi destination (copy) — {E(r['name'])}</summary>
              <code>{E(r['chinese_name'])}</code></details>
          </div>
        </article>'''

    def vcard(r):
        return f'''<tr>
          <td><a href="{r['amap_link']}"><b>{E(r['name'])}</b><br><span class="zh">{E(r['chinese_name'])}</span></a></td>
          <td>{r['distance_km_straight']} km<br><small>{r['didi_min']} min DiDi</small></td>
          <td class="fun">{r['fun_factor_1_10']}</td></tr>'''

    day1 = '''
      <li><b>13:50</b> — at West Kowloon for the <b>14:35 HSR</b>.</li>
      <li><b>14:50</b> — arrive Futian (福田); DiDi to the hotel, 15 min.</li>
      <li><b>15:15</b> — check in at 加来酒店 (Calais Hotel), drop bags.</li>
      <li><b>15:45</b> — DiDi to <a href="#shuibei">Shuibei Jewelry (水贝国际珠宝交易中心)</a>, 25 min, ~¥35.</li>
      <li><b>16:10–17:15</b> — gold and jade: weigh × rate + 工费, compare towers, get the certificate.</li>
      <li><b>17:30</b> — DiDi to <a href="#pingan">Ping An (平安金融中心)</a>, 20 min.</li>
      <li><b>17:45–19:15</b> — <a href="#pingan">Free Sky</a> (116F): dusk into the lights. Last entry 19:15.</li>
      <li><b>19:30</b> — dinner at COCO Park (购物公园).</li>
      <li><b>20:15</b> — DiDi to <a href="#happy">Happy Harbour (欢乐港湾)</a>, 30 min.</li>
      <li><b>20:45–22:00</b> — Bay Glory wheel lit up + the waterfront light show.</li>
      <li><b>22:15</b> — DiDi home, 30 min.</li>'''
    day2 = '''
      <li><b>09:40</b> — L4 Futian Checkpoint (福田口岸) → Convention &amp; Exhibition Center → L1 Huaqiang Rd (华强路), ¥3.</li>
      <li><b>10:00–15:00</b> — <a href="#wondermeet">WonderMeet (玩美攻略)</a>, Century Place (世纪汇) 1–3F. ¥268 on a Thursday.</li>
      <li><b>15:15</b> — <a href="#seg">SEG Electronics Market (赛格电子市场)</a>, 30–45 min.</li>
      <li><b>16:00</b> — <a href="#zijingcheng">Zijingcheng Food Center (紫荆城)</a>, imported snacks.</li>
      <li><b>16:45</b> — <a href="#mingtong">Mingtong Cosmetics (明通)</a>.</li>
      <li><b>17:30</b> — L1 Huaqiang Rd → Laojie (老街), into Dongmen (东门).</li>
      <li><b>17:45–19:00</b> — <a href="#baima">Dongmen Baima (东门白马)</a> clothing market.</li>
      <li><b>19:00</b> — dinner at <a href="#dmd">DMD Food City (东门町美食城)</a>, then East Gate (东门步行街).</li>
      <li><b>20:30</b> — DiDi to <a href="#upperhills">Upper Hills (深业上城)</a>, 15 min: dessert, loft lanes.</li>
      <li><b>21:00–22:00</b> — footbridge to Lianhuashan Park (莲花山公园); the statue for the lit-up skyline.</li>'''
    day3 = '''
      <li><b>09:45</b> — bags to reception; DiDi to <a href="#mixc_tiandi">MixC World (万象天地)</a>, 23 min.</li>
      <li><b>10:15–11:30</b> — coffee and the outdoor lanes.</li>
      <li><b>11:30</b> — <b>Robotaxi</b> to <a href="#techpark">Shenzhen Bay Tech Park (深圳湾科技生态园)</a>, 3.5 km, ¥15–25.</li>
      <li><b>11:45–12:30</b> — tech park + <a href="#talent">Talent Park (人才公园)</a> waterfront.</li>
      <li><b>12:45</b> — DiDi back to the hotel, 25 min; lunch nearby.</li>
      <li><b>14:00</b> — checkout; bags stay at reception.</li>
      <li><b>14:30–16:00</b> — <a href="#spa">Manman Wellness SPA</a>, Jinzhonghuan Building (金中环商务大厦) A座 21F, room 2109.</li>
      <li><b>16:15</b> — collect bags.</li>
      <li><b>Home — two ways:</b> <b>HSR</b> from Futian Station (福田站, 10 min DiDi, ¥68, ~1 h 10 door-to-door, book ahead) <i>or</i> <b>East Rail</b> via Futian Port (福田口岸, 20 min DiDi, cross to Lok Ma Chau 落马洲, HK$57.5, no booking).</li>'''

    doc = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shenzhen · 25–27 Nov</title>
<script>
(function(){{
  var t=null; try{{t=localStorage.getItem('theme')}}catch(e){{}}
  if(!t) t = window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  document.documentElement.dataset.theme=t;
}})();
function toggleTheme(){{
  var cur=document.documentElement.dataset.theme==='dark'?'dark':'light';
  var next=cur==='dark'?'light':'dark';
  document.documentElement.dataset.theme=next;
  try{{localStorage.setItem('theme',next)}}catch(e){{}}
}}
</script>
<style>
  :root {{
    --ink:#15171a; --mut:#5d646e; --line:#e3e6ea; --bg:#fbfbfa; --card:#fff;
    --accent:#0b6b57; --accent2:#b23c1e; --warn:#fbf3e6;
  }}
  :root[data-theme="dark"] {{ --ink:#eceef1; --mut:#9aa2ad; --line:#2a2f36; --bg:#111315;
             --card:#191c20; --accent:#5fd0b4; --accent2:#ff8a63; --warn:#241d15; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
         font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
         -webkit-text-size-adjust:100%; }}
  .wrap {{ max-width:760px; margin:0 auto; padding:0 16px 64px; }}
  header.hero {{ position:relative; padding:28px 16px 20px; background:linear-gradient(160deg,#0b6b57,#0a3f36); color:#fff; }}
  header.hero .wrap {{ padding:0; }}
  header.hero .kicker {{ text-transform:uppercase; letter-spacing:.12em; font-size:12px; opacity:.8; }}
  header.hero h1 {{ margin:6px 0 4px; font-size:30px; line-height:1.15; }}
  header.hero p {{ margin:0; opacity:.9; font-size:14px; }}
  h2 {{ font-size:20px; margin:34px 0 10px; padding-top:14px; border-top:1px solid var(--line); }}
  h2:first-of-type {{ border-top:none; }}
  h3 {{ font-size:18px; margin:0 0 6px; }}
  .zh {{ font-weight:400; color:var(--mut); font-size:.85em; }}
  .themebtn {{ position:absolute; top:16px; right:16px; width:38px; height:38px; border-radius:50%;
    background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.45); color:#fff;
    display:grid; place-items:center; cursor:pointer; padding:0; }}
  .themebtn svg {{ width:18px; height:18px; fill:none; stroke:currentColor; stroke-width:1.8;
    stroke-linecap:round; stroke-linejoin:round; }}
  .themebtn .sun {{ display:none; }}
  :root[data-theme="dark"] .themebtn .sun {{ display:block; }}
  :root[data-theme="dark"] .themebtn .moon {{ display:none; }}
  .strip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:8px; margin:16px 0; }}
  .chip {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:10px 12px; font-size:13px; }}
  .chip b {{ display:block; font-size:12px; color:var(--mut); font-weight:600; text-transform:uppercase; letter-spacing:.06em; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; background:var(--card);
           border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
  th,td {{ text-align:left; padding:9px 10px; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ background:var(--bg); font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--mut); }}
  tr:last-child td {{ border-bottom:none; }}
  .place {{ background:var(--card); border:1px solid var(--line); border-radius:16px; overflow:hidden; margin:18px 0; }}
  .ph {{ display:grid; grid-template-columns:1fr; gap:2px; background:var(--bg); }}
  .ph.single {{ grid-template-columns:1fr; }}
  .ph.single img {{ height:240px; }}
  .ph figure {{ margin:0; }}
  .ph img {{ width:100%; height:210px; object-fit:cover; display:block; }}
  .ph figcaption {{ font-size:11px; color:var(--mut); padding:4px 10px 6px; }}
  .review {{ margin:0; padding:12px 16px; background:var(--warn); border-left:4px solid var(--accent2); }}
  .review h4 {{ margin:0 0 6px; font-size:13px; text-transform:uppercase; letter-spacing:.08em; color:var(--accent2); }}
  .review blockquote {{ margin:0 0 8px; padding:0; font-style:italic; }}
  .review p {{ margin:0; font-weight:600; }}
  .pb {{ padding:14px 16px 16px; }}
  .meta {{ font-size:13px; color:var(--mut); margin:0 0 8px; }}
  .fun {{ color:var(--accent); font-weight:700; }}
  .go {{ font-size:14px; background:var(--bg); border-radius:10px; padding:8px 10px; }}
  .warn {{ background:var(--warn); border-radius:10px; padding:8px 10px; font-size:14px; }}
  p {{ margin:8px 0; }}
  .links a {{ display:inline-block; margin:4px 10px 0 0; font-size:14px; color:var(--accent); font-weight:600;
               text-decoration:none; border-bottom:1px solid currentColor; }}
  details {{ margin-top:10px; font-size:14px; }}
  summary {{ cursor:pointer; color:var(--mut); }}
  code {{ display:block; margin-top:6px; padding:8px 10px; background:var(--bg); border-radius:8px;
          font-size:15px; user-select:all; -webkit-user-select:all; }}
  .day {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:6px 16px 10px; margin:14px 0; }}
  .day h3 {{ margin-top:14px; }}
  .day ol {{ padding-left:20px; margin:8px 0 14px; }}
  .day li {{ margin:7px 0; }}
  .day a {{ color:var(--accent); text-decoration:none; border-bottom:1px solid currentColor; }}
  ol.tips li, ul.tips li {{ margin:8px 0; }}
  .note {{ font-size:13px; color:var(--mut); }}
  footer {{ margin-top:40px; font-size:12px; color:var(--mut); }}
  a {{ color:var(--accent); }}
  @media (min-width:560px) {{ .ph:not(.single) {{ grid-template-columns:1fr 1fr; }} }}
  @media print {{
    @page {{ margin: 0; }}
    body {{ background:var(--bg); color:var(--ink); padding: 12mm 11mm; }}
    header.hero {{ background:#0b6b57 !important; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    .place, .day, table {{ break-inside:avoid; }}
    details, .toggle, .themebtn {{ display:none; }}
    .ph img {{ height:auto; object-fit:contain; }}
    .ph.single img {{ height:auto; max-height:420px; }}
    .ph figure {{ break-inside:avoid; }}
  }}
</style></head>
<body>
<header class="hero"><div class="wrap">
  <div class="kicker">Shenzhen · China</div>
  <h1>25–27 November 2026</h1>
  <p>Two full days + a checkout half-day · 加来酒店 (Calais Hotel), 福田口岸</p>
  <button class="themebtn" type="button" onclick="toggleTheme()" aria-label="Switch theme">
    <svg class="moon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
    <svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
  </button>
</div></header>
<div class="wrap">

  <div class="strip">
    <div class="chip"><b>Weather</b>25 Nov 13–19° · 26 Nov 14–23° · 27 Nov 16–26°<br><span class="note">33% rain Thu — take a compact umbrella</span></div>
    <div class="chip"><b>Metro</b>皇岗村 (L7) 430 m · 福田口岸 (L4/L10) 1.1 km</div>
    <div class="chip"><b>Arrive</b>HSR 西九龙 → 福田, 14 min, ¥68</div>
    <div class="chip"><b>Return</b>福田口岸 → 落马洲 → East Rail, HK$57.5</div>
  </div>

  <h2>The plan</h2>
  <div class="day"><h3>Wed 25 Nov — arrive, first sunset</h3><ol>{day1}</ol></div>
  <div class="day"><h3>Thu 26 Nov — the fun day</h3><ol>{day2}</ol></div>
  <div class="day"><h3>Fri 27 Nov — checkout 14:00, then home</h3><ol>{day3}</ol></div>

  <h2>WonderMeet + the markets <span class="zh">玩美攻略 &amp; 批发市场</span></h2>
  <div class="strip">
    {''.join(f'<a class="chip" href="{r["amap_link"]}" style="text-decoration:none;color:inherit"><b>{E(r["chinese_name"])}</b>{E(r["name"])}<br><small>{r["distance_km_straight"]} km · {r["didi_min"]} min DiDi</small></a>' for r in venues)}
  </div>
  {''.join(card(r) for r in venues)}

  <h2>Buying at the markets</h2>
  <div class="day">
    <p><b>Carry a black plastic bag.</b> It's the trade signal of a 拿货 buyer — prices change before you speak.</p>
    <ol class="tips">
      <li>Ask <b>“拿货几多？”</b> (stock price), not “多少钱？” (retail).</li>
      <li>Ask <b>“几件起？”</b> — minimum pieces. Two or three is normal at 白马.</li>
      <li>Counter at <b>half</b>, settle at 55–65%. Start walking if they won't move.</li>
      <li><b>From 16:00 they bargain hardest</b> — the last two hours before closing. Most buildings shut 18:00–19:00.</li>
      <li><b>Bigger deals:</b> ask for the <b>天虹 (Tianhong) clearance building</b> — where the volume buyers work. Ask a stallholder to point you there.</li>
      <li>Pay by WeChat/Alipay; count goods before paying.</li>
    </ol>
    <p class="note">Cosmetics: check batch code + expiry. Jewellery: price = gold weight × rate + 工费, ask for the certificate. Clothing: sizes run small. Electronics: know the online price first.</p>
  </div>

  <h2>Getting there &amp; back</h2>
  <table><thead><tr><th>Leg</th><th>Route</th><th>Time</th><th>Cost</th></tr></thead><tbody>
    <tr><td><b>In</b></td><td>东涌 → 九龙 (Tung Chung Line) → walk to 西九龙 → HSR to 福田 → DiDi</td><td>1 h 50 – 2 h 15</td><td>≈HK$110</td></tr>
    <tr><td><b>Out</b></td><td>Hotel → 福田口岸 (1.1 km) → 落马洲 → East Rail → 红磡 → 南昌 → 东涌</td><td>~2 h 15</td><td>HK$57.5</td></tr>
  </tbody></table>
  <p class="note">Port hours 06:30–22:30 · last East Rail from 落马洲 ≈ 22:55 · be at the port by 18:00–18:30 on the 27th.</p>

  <h2>Driverless cars <span class="zh">无人驾驶出租车</span></h2>
  <div class="day">
    <p><b>Pony.ai (小马智行)</b> is the one to try — citywide permit, zone over 南山 / 前海 / 深圳湾, ~10,000 pickup points, 07:00–22:00. Book in the <b>PonyPilot+</b> app or its WeChat mini-program. It's the operator that accepts passports and foreign cards.</p>
    <p class="note"><b>Apollo Go (萝卜快跑)</b> also runs in 南山 / 宝安 / 坪山 (07:00–23:00) but is <b>station-to-station</b> — you walk to a green pickup dot, not an address.</p>
    <ol class="tips">
      <li>Register in PonyPilot+ with your phone and <b>passport</b> — ~10 minutes.</li>
      <li>Set pickup + drop-off inside the green zone.</li>
      <li>Wait 3–15 min; match the plate and car number.</li>
      <li>Unlock from the app (Bluetooth) or type your phone's last 4 digits on the door.</li>
      <li>Back seat only, belt up, tap <b>Start</b> on the screen.</li>
    </ol>
    <p><b>Cost:</b> ¥10–30 for 3–6 km. <b>The catch:</b> both apps may demand a +86 number for SMS — if yours fails, try the WeChat mini-program, or ask the front desk to book on their account. Weather suspends service.</p>
    <p><b>Ride to take:</b> 万象天地 → 深圳湾科技生态园, 3.5 km, ~12 min, ¥15–25 — inside the zone and lands you at the tech park.</p>
  </div>

  <h2>All the places</h2>
  {''.join(card(r) for r in sights)}

  <h2>Amap — save everything</h2>
  <p>Amap links cap at 10 points, so there are three:</p>
  <p class="links">
    <a href="{links['futian_luohu']}">Futian + Luohu (9)</a>
    <a href="{links['nanshan_baoan']}">Nanshan + Bao'an (5)</a>
    <a href="{links['markets']}">Markets + WonderMeet (7)</a>
  </p>
  <p class="note">To keep all 21 in your own account, import <code style="display:inline">amap_import.csv</code> at wia.amap.com → 批量导入.</p>

  <footer>
    <p>Coordinates are GCJ-02 (Google &amp; Amap native); WGS-84 in places.csv. Data pulled 24 Nov 2026.
    Photos: Wikimedia Commons / Openverse contributors, freely licensed — see README credits.</p>
  </footer>
</div>
</body></html>'''
    open('../index.html', 'w', encoding='utf-8').write(doc)
    print('wrote index.html', len(doc), 'chars')


if __name__ == '__main__':
    main()

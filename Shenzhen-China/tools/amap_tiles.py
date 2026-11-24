"""Draw a marker at a coordinate on Amap tiles, to verify the coordinate system.

Usage: python3 -I amap_tiles.py LAT LNG Z OUT.png [style]
"""
import math, sys, os, subprocess, urllib.request

def gcj02_forward(lat, lon):
    a = 6378245.0; ee = 0.00669342162296594323
    def tlat(x, y):
        r = -100.0 + 2.0*x + 3.0*y + 0.2*y*y + 0.1*x*y + 0.2*math.sqrt(abs(x))
        r += (20.0*math.sin(6.0*x*math.pi) + 20.0*math.sin(2.0*x*math.pi))*2.0/3.0
        r += (20.0*math.sin(y*math.pi) + 40.0*math.sin(y/3.0*math.pi))*2.0/3.0
        r += (160.0*math.sin(y/12.0*math.pi) + 320*math.sin(y*math.pi/30.0))*2.0/3.0
        return r
    def tlon(x, y):
        r = 300.0 + x + 2.0*y + 0.1*x*x + 0.1*x*y + 0.1*math.sqrt(abs(x))
        r += (20.0*math.sin(6.0*x*math.pi) + 20.0*math.sin(2.0*x*math.pi))*2.0/3.0
        r += (20.0*math.sin(x*math.pi) + 40.0*math.sin(x/3.0*math.pi))*2.0/3.0
        r += (150.0*math.sin(x/12.0*math.pi) + 300.0*math.sin(x/30.0*math.pi))*2.0/3.0
        return r
    dlat = tlat(lon-105.0, lat-35.0); dlon = tlon(lon-105.0, lat-35.0)
    rad = lat/180.0*math.pi; magic = 1 - ee*math.sin(rad)**2
    sq = math.sqrt(magic)
    dlat = (dlat*180.0)/((a*(1-ee))/(magic*sq)*math.pi)
    dlon = (dlon*180.0)/(a/sq*math.cos(rad)*math.pi)
    return lat+dlat, lon+dlon

def tile_xy(lat, lon, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.log(math.tan(math.radians(lat)) + 1/math.cos(math.radians(lat)))/math.pi) / 2.0 * n
    return x, y

def fetch(sub, style, x, y, z):
    if style == '6':
        url = f"https://webst0{sub}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}"
    else:
        url = f"https://webrd0{sub}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}"
    r = subprocess.run(['curl', '-s', '--compressed', '-A', 'Mozilla/5.0',
                        '-H', 'Referer: https://www.amap.com/', url], capture_output=True)
    return r.stdout

def main():
    lat, lon, z, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    style = sys.argv[5] if len(sys.argv) > 5 else '6'
    out = os.path.basename(out)
    tx, ty = tile_xy(lat, lon, z)
    cx, cy = int(tx), int(ty)
    os.makedirs('out/tiles', exist_ok=True)
    files = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            x, y = cx + dx, cy + dy
            data = fetch(1 + ((x + y) % 4), style, x, y, z)
            fn = f'out/tiles/{out}_{x}_{y}.jpg'
            open(fn, 'wb').write(data)
            files.append(fn)
    subprocess.run(['montage', *files, '-tile', '3x3', '-geometry', '+0+0', f'out/{out}_mosaic.png'], check=True)
    px = (tx - cx + 1) * 256
    py = (ty - cy + 1) * 256
    subprocess.run(['magick', f'out/{out}_mosaic.png', '-fill', 'none', '-stroke', 'red', '-strokewidth', '3',
                    '-draw', f'circle {px:.0f},{py:.0f} {px+14:.0f},{py:.0f}', f'out/{out}_marked.png'], check=True)
    print(f'{out}: point pixel ({px:.0f},{py:.0f}) in 768x768 mosaic')

if __name__ == '__main__':
    main()

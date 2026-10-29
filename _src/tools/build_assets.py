"""Converts the raw brand / photo folders into optimised web assets.
Usage: python _src/tools/build_assets.py <urban_dir> <old_site_dir>"""
import os, sys
from PIL import Image

URBAN, OLD = sys.argv[1], sys.argv[2]
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'img')

PHOTOS = {
    '666764a17c17fb0ff66b9f43_phases_of_construction_projects.webp': 'rebar-dusk',
    'CAS01844-JLhMdE-cYKWSWCh2QYzKgg.jpg': 'site-rebar-worker',
    'CAS01870--uTlSr4LI3vt1Sh09CXpTQ.jpg': 'site-worker-cutting',
    'DJI_0294-XM_cKtjP9GdFrGGqBQyfjg.jpg': 'aerial-site-1',
    'DJI_0296-lREajayi18yDIWRh3iZHRg.jpg': 'aerial-site-2',
    'DJI_20260923145514_0848_D.jpg1-s53h8r70Wfc4pGBqiY858Q.jpeg': 'aerial-site-wide',
    'Eagelsvile40-LrNLBvbyZcjb6tRObmnu-w.jpg': 'eaglesvale-backhoe',
    'MazoweWalkShoppingMallatwork-9HqJacbyzbfAkflmQHBIVA.jpeg': 'mazowe-walk-1',
    'MazoweWalkShoppingMallatwork2-MmgjoIXVjpxOzS3gEBd0Pg.jpeg': 'mazowe-walk-2',
    'WhatsAppImage2024-08-28at6.13.55PM1-381BN1aXifhzzUNMcltQWA.jpeg': 'steel-structure',
    'istockphoto-131399470-2048x2048.jpg': 'timber-frame',
    'istockphoto-2155879454-2048x2048.jpg': 'residence-finished',
    'istockphoto-2226261964-2048x2048.jpg': 'cranes-sky',
    'istockphoto-2227010119-2048x2048.jpg': 'engineer-plans',
    'istockphoto-2233111622-2048x2048.jpg': 'roof-framing',
    'istockphoto-2249567115-2048x2048.jpg': 'team-site-review',
    'istockphoto-463070883-2048x2048.jpg': 'excavator-loading',
}
OLD_PHOTOS = {
    'hero-XEFSlMNt.webp': 'hero-harare', 'about-h_nmhQie.webp': 'team-crew',
    'portfolio-1-4f4--9yh.webp': 'highfields-estate', 'portfolio-2-BJO4QptD.webp': 'apex-tower',
    'portfolio-3--_oJ6K8l.webp': 'mutare-gateway', 'portfolio-4-CpxC5KyT.webp': 'borrowdale-villas',
    'service-construction-C1VA_Lm1.webp': 'svc-construction', 'service-land-CLg2f_Ax.webp': 'svc-land',
    'service-management-CqdWGVjA.webp': 'svc-management', 'service-property-Ah92UCBV.webp': 'svc-property',
}
LOGOS = {
    'Capture-removebg-preview1-PGYDhvBl-RUar48i0z7WRg.png': 'original-technology',
    'WhatsApp_Image_2026-03-30_at_3.40.57_PM__1_-removebg-preview-y0Z_UPvK-sNorCEjHy7uwA.png': 'thaton',
    'WhatsApp_Image_2026-03-30_at_3.40.57_PM__2_-removebg-preview-uTkoI4iLV-lbJ3_oqry8Qg.png': 'redan',
    'WhatsApp_Image_2026-03-30_at_3.40.57_PM__3_-removebg-preview-_ot9UfSjiOGCWXAcDkUK9w.png': 'zimasco',
    'WhatsApp_Image_2026-03-30_at_3.40.57_PM__4_-removebg-preview-w4p3lhX79_KrwCIppg7_Jg.png': 'zimtrade',
    'WhatsApp_Image_2026-03-30_at_3.40.57_PM__5_-removebg-preview-lrIlxW3qgnNx0cRCtYGzeA.png': 'old-mutual',
    'WhatsApp_Image_2026-03-30_at_3.40.57_PM__6_-removebg-preview-MG7YVtgTclgT111ixLX8yw.png': 'simbisa',
    'WhatsApp_Image_2026-03-30_at_3.40.57_PM__7_-removebg-preview-WAHe37cAnuw6vH6CV-C_2w.png': 'stanbic',
    'gateway logo.png': 'gateway',
    'mimosa-mining-removebg-preview-B21Kd-R-9vUMYwqCXsTg4g.png': 'mimosa',
    'msc-removebg-preview-x63Ksfz1vXDmavoAckkdOw.png': 'msc',
    'valterra_logo-removebg-preview-LYYjIP0MVE03j1RWE9t7yg.png': 'valterra',
}

def photo(src, name, maxw=1920):
    im = Image.open(src).convert('RGB')
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(os.path.join(OUT, name + '.webp'), 'WEBP', quality=80, method=6)
    print(name, im.size)

def trimmed(src, dst, pad=4, maxh=None):
    im = Image.open(src).convert('RGBA')
    bb = im.getchannel('A').point(lambda a: 255 if a > 12 else 0).getbbox()
    im = im.crop((max(0, bb[0]-pad), max(0, bb[1]-pad), min(im.width, bb[2]+pad), min(im.height, bb[3]+pad)))
    if maxh and im.height > maxh:
        im = im.resize((round(im.width * maxh / im.height), maxh), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=92, method=6)
    print(os.path.basename(dst), im.size)

for f, n in PHOTOS.items(): photo(os.path.join(URBAN, f), n)
for f, n in OLD_PHOTOS.items(): photo(os.path.join(OLD, f), n)
for f, n in LOGOS.items(): trimmed(os.path.join(URBAN, f), os.path.join(OUT, 'clients', n + '.webp'), maxh=160)
trimmed(os.path.join(URBAN, 'iso-removebg-preview-kwsvTvcMcbl7uNQ-1tc7HQ.png'), os.path.join(OUT, 'iso-9001.webp'), maxh=300)

# Logo: full colour + white (reversed) version for dark surfaces
logo = os.path.join(URBAN, 'urbanforge-logo-final-B9Zh3gHe.png')
trimmed(logo, os.path.join(OUT, 'logo.webp'), maxh=240)
im = Image.open(os.path.join(OUT, 'logo.webp')).convert('RGBA')
px = im.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        if b > r:  # navy parts become white, orange stays
            px[x, y] = (255, 255, 255, a)
im.save(os.path.join(OUT, 'logo-light.webp'), 'WEBP', quality=92)
# Mark only (icon) for favicon / preloader
mark = Image.open(logo).convert('RGBA')
mark = mark.crop((0, 0, round(mark.width * 0.235), mark.height))
mark = mark.crop(mark.getchannel('A').getbbox())
side = max(mark.size); sq = Image.new('RGBA', (side, side)); sq.alpha_composite(mark, ((side-mark.width)//2, (side-mark.height)//2))
sq.resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, 'mark.png'))
sq.resize((64, 64), Image.LANCZOS).save(os.path.join(OUT, '..', '..', 'favicon.png'))
print('mark', sq.size)

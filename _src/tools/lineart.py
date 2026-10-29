"""Generates the two decorative construction line-art strips as seamless, horizontally tiling SVGs.

  assets/img/lineart-site.svg   pencil-sketch panorama: skyline of frames/scaffolds/tower cranes (back),
                                plant & machinery (middle), materials and fencing (front)
  assets/img/lineart-tools.svg  row of outlined construction tool icons with soft brand-colour offset fills
  assets/img/pat-*.svg          corner motifs for the How-we-deliver cards (survey, structural grid, gauge)

Usage: python _src/tools/lineart.py
Every stroke is jittered and drawn twice at different weights to read as pencil, not vector.
"""
import math, os, random

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'img')


class Sketch:
    """Collects line segments and emits them as jittered quadratic paths."""

    def __init__(self, seed, jitter=0.7):
        self.segs, self.circles, self.R, self.j = [], [], random.Random(seed), jitter

    # primitives -------------------------------------------------------------
    def line(self, x1, y1, x2, y2):
        self.segs.append((x1, y1, x2, y2))

    def poly(self, pts, close=False):
        for a, b in zip(pts, pts[1:] + (pts[:1] if close else [])):
            self.line(*a, *b)

    def rect(self, x, y, w, h):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True)

    def circle(self, cx, cy, r):
        self.circles.append((cx, cy, r))

    def hatch(self, x, y, w, h, gap=4, ang=45):
        """Diagonal hatching clipped analytically to a rectangle."""
        t = math.tan(math.radians(ang))
        c = -h / t if ang < 90 else 0
        k = c
        while k < w:
            x1, y1 = x + k, y + h
            x2, y2 = x + k + h / t, y
            if x1 < x: y1 = y + h - (x - x1) * t; x1 = x
            if x2 > x + w: y2 = y + (x2 - (x + w)) * t; x2 = x + w
            if y1 >= y and y2 <= y + h and x2 > x1:
                self.line(x1, y1, x2, y2)
            k += gap

    def lattice(self, x1, y1, x2, y2, width, step):
        """Two parallel chords with zig-zag web (crane masts and jibs)."""
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        nx, ny = -uy * width / 2, ux * width / 2
        a = [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny)]
        b = [(x1 - nx, y1 - ny), (x2 - nx, y2 - ny)]
        self.line(*a[0], *a[1]); self.line(*b[0], *b[1])
        n = max(2, int(L / step))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            p = (x1 + (x2 - x1) * t0 + (nx if i % 2 else -nx), y1 + (y2 - y1) * t0 + (ny if i % 2 else -ny))
            q = (x1 + (x2 - x1) * t1 + (-nx if i % 2 else nx), y1 + (y2 - y1) * t1 + (-ny if i % 2 else ny))
            self.line(*p, *q)

    # output -----------------------------------------------------------------
    def _d(self, R, j):
        out = []
        for x1, y1, x2, y2 in self.segs:
            mx, my = (x1 + x2) / 2 + R.uniform(-j, j), (y1 + y2) / 2 + R.uniform(-j, j)
            out.append(f'M{x1 + R.uniform(-j, j):.1f} {y1 + R.uniform(-j, j):.1f}Q{mx:.1f} {my:.1f} {x2 + R.uniform(-j, j):.1f} {y2 + R.uniform(-j, j):.1f}')
        for cx, cy, r in self.circles:
            rr = r + R.uniform(-j, j) * .4
            out.append(f'M{cx - rr:.1f} {cy:.1f}a{rr:.1f} {rr:.1f} 0 1 0 {2 * rr:.1f} 0a{rr:.1f} {rr:.1f} 0 1 0 {-2 * rr:.1f} 0')
        return ''.join(out)

    def svg(self, color, width, opacity):
        a = self._d(random.Random(self.R.random()), self.j)
        b = self._d(random.Random(self.R.random()), self.j * 1.6)   # second, lighter pencil pass
        return (f'<path d="{a}" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>'
                f'<path d="{b}" stroke="{color}" stroke-width="{width * .55:.2f}" opacity="{opacity * .55:.2f}"/>')


# =============================================================================
# SITE PANORAMA
# =============================================================================
W, H, G = 1800, 340, 318          # tile width, height, ground line


WASH = []


def building(s, R, x, w, h, frame_floors=0, scaffold=False):
    top = G - h
    WASH.append(f'<rect x="{x}" y="{top + frame_floors * 15}" width="{w}" height="{h - frame_floors * 15}" fill="#e7eaef"/>')
    fl = 15
    solid_top = top + frame_floors * fl
    s.rect(x, solid_top, w, G - solid_top)
    y = solid_top + fl
    while y < G - 4:                                    # floor lines
        s.line(x, y, x + w, y); y += fl
    bay = R.choice([14, 20, 26, 34])
    xx = x + bay
    while xx < x + w - 4:                               # mullions
        s.line(xx, solid_top + 4, xx, G); xx += bay
    if frame_floors:                                    # exposed concrete frame on top
        cols = max(2, int(w / 22))
        for i in range(cols + 1):
            cx = x + i * w / cols
            s.line(cx, top, cx, solid_top)
        for f in range(frame_floors + 1):
            s.line(x, top + f * fl, x + w, top + f * fl)
        for i in range(cols):
            if R.random() < .6:
                cx = x + i * w / cols
                s.line(cx, top, cx + w / cols, top + fl)
    if scaffold:
        sx0, sx1 = x - 6, x + w + 6
        y = G
        while y > top - 4:
            s.line(sx0, y, sx1, y); y -= fl / 2 * 2
        for sx in (sx0, sx1):
            s.line(sx, top - 4, sx, G)
        s.hatch(sx0, top, 6, h, gap=7, ang=60)


def tower_crane(s, R, x, h, jib_l, jib_r):
    top = G - h
    s.lattice(x, G, x, top, 10, 9)
    s.line(x - 5, top, x, top - 26); s.line(x + 5, top, x, top - 26)     # apex
    s.lattice(x - jib_l, top, x + jib_r, top, 7, 9)                         # jib + counter-jib
    s.line(x, top - 26, x + jib_r, top - 3); s.line(x, top - 26, x - jib_l, top - 3)
    s.rect(x - jib_l + 4, top + 4, 22, 14); s.hatch(x - jib_l + 4, top + 4, 22, 14, gap=3)
    s.rect(x - 9, top + 4, 12, 10)                                          # cab
    tx = x + jib_r * R.uniform(.45, .85)
    hook = top + R.uniform(.35, .65) * h
    s.line(tx - 2, top + 4, tx - 2, hook); s.line(tx + 2, top + 4, tx + 2, hook)
    s.rect(tx - 5, hook, 10, 7); s.line(tx, hook + 7, tx, hook + 13)
    if R.random() < .6:                                                     # suspended load
        s.line(tx, hook + 13, tx - 18, hook + 26); s.line(tx, hook + 13, tx + 18, hook + 26)
        s.rect(tx - 22, hook + 26, 44, 9)


def wheel(s, cx, cy, r):
    s.circle(cx, cy, r); s.circle(cx, cy, r * .45)
    for k in range(6):
        a = k * math.pi / 3
        s.line(cx + math.cos(a) * r * .45, cy + math.sin(a) * r * .45, cx + math.cos(a) * r * .8, cy + math.sin(a) * r * .8)


def tracks(s, x, w, h=16):
    y = G - h
    s.poly([(x + h / 2, y), (x + w - h / 2, y)]); s.poly([(x + h / 2, G), (x + w - h / 2, G)])
    for cx in (x + h / 2, x + w - h / 2):
        s.circle(cx, y + h / 2, h / 2)
    n = int(w / 13)
    for i in range(1, n):
        s.circle(x + i * w / n, y + h / 2, 3.2)
    k = x + 4
    while k < x + w - 4:
        s.line(k, G, k, G - 3); k += 4.5


def excavator(s, x, flip=1):
    tracks(s, x, 92)
    by = G - 16
    s.rect(x + 6, by - 26, 66, 22); s.hatch(x + 6, by - 26, 26, 22, gap=4)
    s.rect(x + 46, by - 50, 28, 26)                                         # cab
    s.rect(x + 50, by - 46, 18, 14)
    bx = x + 74
    pts = [(bx, by - 18), (bx + 44 * flip, by - 82), (bx + 80 * flip, by - 54)]
    s.poly([(bx, by - 26), (bx + 42 * flip, by - 90), (bx + 48 * flip, by - 76), (bx + 6, by - 14)])
    s.line(*pts[1], *pts[2]); s.line(pts[1][0] + 6, pts[1][1] + 6, pts[2][0] - 4, pts[2][1] + 4)
    s.line(bx + 4, by - 30, bx + 30 * flip, by - 70)                        # ram
    cx, cy = pts[2]
    s.poly([(cx, cy), (cx + 16 * flip, cy + 6), (cx + 20 * flip, cy + 26), (cx + 4 * flip, cy + 30), (cx - 6 * flip, cy + 16)], close=True)
    for t in range(4):
        s.line(cx + (4 + t * 4) * flip, cy + 30 + (t % 2), cx + (4 + t * 4) * flip, cy + 34)


def mobile_crane(s, x):
    s.rect(x, G - 30, 150, 14); s.rect(x + 118, G - 52, 32, 22); s.rect(x + 124, G - 48, 18, 12)
    for wx in (x + 18, x + 42, x + 92, x + 132):
        wheel(s, wx, G - 10, 10)
    s.line(x - 6, G - 18, x - 6, G); s.line(x - 14, G, x + 2, G)              # outrigger
    s.rect(x + 20, G - 46, 46, 16)
    base = (x + 30, G - 46)
    tip = (x + 30 + 210, G - 46 - 200)
    s.lattice(*base, (base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2, 12, 400)
    s.lattice((base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2, *tip, 8, 400)
    s.line(x + 40, G - 46, x + 112, G - 132)                                  # luffing ram
    s.line(*tip, tip[0], G - 70); s.rect(tip[0] - 5, G - 70, 10, 8); s.line(tip[0], G - 62, tip[0], G - 54)


def crawler_crane(s, x):
    tracks(s, x, 110, 18)
    s.rect(x + 14, G - 52, 70, 32); s.hatch(x + 14, G - 52, 30, 32, gap=4); s.rect(x + 70, G - 64, 26, 24)
    s.lattice(x + 80, G - 46, x + 260, G - 290, 14, 14)
    s.line(x + 40, G - 52, x + 260, G - 290)                                 # pendant
    s.line(x + 260, G - 290, x + 260, G - 120); s.rect(x + 254, G - 120, 12, 9)
    s.line(x + 260, G - 111, x + 236, G - 92); s.line(x + 260, G - 111, x + 284, G - 92)
    s.rect(x + 220, G - 92, 80, 12); s.hatch(x + 220, G - 92, 80, 12, gap=5, ang=60)   # steel beam load


def mixer(s, x):
    s.rect(x, G - 26, 140, 10); s.rect(x + 108, G - 50, 32, 24); s.rect(x + 114, G - 46, 18, 12)
    for wx in (x + 18, x + 40, x + 124):
        wheel(s, wx, G - 9, 9)
    cx, cy, rx, ry = x + 52, G - 50, 48, 24
    pts = [(cx + rx * math.cos(a / 20 * 2 * math.pi), cy + ry * math.sin(a / 20 * 2 * math.pi)) for a in range(20)]
    s.poly(pts, close=True)
    for k in range(-3, 4):                                                     # drum spiral
        s.line(cx + k * 13 - 6, cy - ry * .9, cx + k * 13 + 6, cy + ry * .9)
    s.line(x + 96, G - 60, x + 106, G - 70); s.line(x + 98, G - 40, x + 112, G - 34)


def dozer(s, x):
    tracks(s, x + 10, 84)
    s.rect(x + 20, G - 46, 56, 30); s.rect(x + 46, G - 70, 30, 24); s.rect(x + 50, G - 66, 20, 14)
    s.hatch(x + 20, G - 46, 24, 30, gap=4)
    s.poly([(x - 8, G - 50), (x - 2, G - 44), (x - 2, G - 8), (x - 10, G)])
    s.line(x - 2, G - 30, x + 20, G - 34); s.line(x - 2, G - 20, x + 24, G - 24)


def tipper(s, x):
    s.rect(x, G - 26, 130, 10); s.rect(x + 100, G - 52, 30, 26); s.rect(x + 106, G - 48, 18, 12)
    for wx in (x + 16, x + 40, x + 112):
        wheel(s, wx, G - 10, 10)
    s.poly([(x - 4, G - 64), (x + 92, G - 58), (x + 92, G - 28), (x + 6, G - 28)], close=True)
    s.hatch(x + 6, G - 58, 84, 28, gap=6, ang=75)
    for k in range(6):                                                         # aggregate heap
        s.circle(x + 14 + k * 13, G - 66 - (k % 3) * 2, 4)


def site_svg():
    R = random.Random(11)
    back, mid, front = Sketch(1, .6), Sketch(2, .8), Sketch(3, .7)
    WASH.clear()
    far = Sketch(4, .5)
    x = 0
    while x < W - 40:                                                          # far skyline, faint
        w = R.randint(26, 60); h = R.randint(120, 300)
        far.rect(x, G - h, w, h)
        for yy in range(G - h + 10, G, 10):
            far.line(x + 4, yy, x + w - 4, yy)
        if R.random() < .3:
            far.line(x + w / 2, G - h, x + w / 2, G - h - 24)
        x += w + R.randint(2, 18)
    # back: skyline
    x = 10
    while x < W - 150:
        w = R.randint(60, 140)
        h = R.randint(90, 250)
        building(back, R, x, w, h, frame_floors=R.choice([0, 0, 2, 3, 4]), scaffold=R.random() < .35)
        x += w + R.randint(8, 40)
    for cx, h, jl, jr in [(190, 300, 50, 170), (760, 280, 46, 150), (1260, 306, 52, 190), (1650, 260, 40, 110)]:
        tower_crane(back, R, cx, h, jl, jr)
    # middle: plant
    excavator(mid, 40)
    tipper(mid, 260)
    crawler_crane(mid, 470)
    mixer(mid, 880)
    mobile_crane(mid, 1090)
    dozer(mid, 1430)
    excavator(mid, 1580, flip=-1)
    # front: ground, materials, fencing
    front.line(0, G, W, G)
    k = 0
    while k < W:
        d = R.choice([6, 10, 18, 30]); front.line(k, G + 8, k + d, G + 8); k += d + R.choice([6, 10, 14])
    for px in (380, 1010, 1380):                                               # pipe stacks
        for row, n in ((0, 4), (1, 3), (2, 2)):
            for i in range(n):
                front.circle(px + i * 11 + row * 5.5, G - 5 - row * 9.5, 5)
    for bx in (820, 1720):                                                     # brick pallets
        front.rect(bx, G - 6, 48, 6)
        for r in range(3):
            for i in range(4):
                front.rect(bx + i * 12 + (r % 2) * 6 - (r % 2) * 3, G - 6 - (r + 1) * 7, 12, 7)
    for fx in (600, 1880 - 260):                                               # mesh fence panels
        for i in range(4):
            x0 = fx + i * 30
            front.rect(x0, G - 34, 28, 34); front.hatch(x0, G - 34, 28, 34, gap=6, ang=45); front.hatch(x0, G - 34, 28, 34, gap=6, ang=135)
    for cx in (230, 720, 1060, 1540):                                          # cones
        front.poly([(cx - 9, G), (cx - 3, G - 22), (cx + 3, G - 22), (cx + 9, G)]); front.line(cx - 12, G, cx + 12, G)
        front.line(cx - 6, G - 10, cx + 6, G - 10)
    wash = f'<g opacity=".55">{"".join(WASH)}</g>'
    body = far.svg('#b9c0cb', .8, .35) + wash + back.svg('#9aa3b2', 1.0, .55) + mid.svg('#7b8596', 1.25, .75) + front.svg('#7b8596', 1.2, .7)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


# =============================================================================
# TOOL ICON ROW
# =============================================================================
TW, TH, TG = 1500, 230, 214
FILLS = ['#f2c1a9', '#c9d6ea', '#f0dcae']      # forge, navy, sand tints


def tools_svg():
    R = random.Random(5)
    s = Sketch(8, .45)
    fills = []

    def blob(kind, *a, c=None):
        c = c or R.choice(FILLS)
        if kind == 'r':
            x, y, w, h = a
            fills.append(f'<rect x="{x + 5:.1f}" y="{y - 5:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{c}"/>')
        else:
            cx, cy, r = a
            fills.append(f'<circle cx="{cx + 4:.1f}" cy="{cy - 4:.1f}" r="{r:.1f}" fill="{c}"/>')

    def hammer(x):
        s.rect(x - 4, TG - 96, 8, 96); s.rect(x - 22, TG - 108, 30, 16)
        s.poly([(x + 8, TG - 106), (x + 22, TG - 112), (x + 26, TG - 100)])
        blob('r', x - 22, TG - 108, 30, 16)

    def wrench(x):
        s.rect(x - 5, TG - 84, 10, 70); s.circle(x, TG - 96, 15); s.rect(x - 5, TG - 112, 10, 14)
        s.circle(x, TG - 8, 9); blob('c', x, TG - 96, 15)

    def pencil(x):
        s.rect(x - 6, TG - 118, 12, 100); s.poly([(x - 6, TG - 18), (x, TG), (x + 6, TG - 18)])
        s.line(x - 6, TG - 106, x + 6, TG - 106); s.line(x - 2, TG - 118, x - 2, TG - 18)
        blob('r', x - 6, TG - 118, 12, 100)

    def ruler(x):
        s.rect(x - 10, TG - 130, 20, 130)
        for i in range(1, 26):
            s.line(x - 10, TG - i * 5, x - (2 if i % 5 == 0 else 5), TG - i * 5)
        blob('r', x - 10, TG - 130, 20, 130)

    def calculator(x):
        s.rect(x - 24, TG - 70, 48, 70); s.rect(x - 18, TG - 64, 36, 14)
        for r in range(4):
            for c in range(3):
                s.rect(x - 18 + c * 13, TG - 44 + r * 10, 9, 6)
        blob('r', x - 24, TG - 70, 48, 70)

    def clipboard(x):
        s.rect(x - 28, TG - 90, 56, 90); s.rect(x - 12, TG - 96, 24, 10)
        for r in range(4):
            y = TG - 72 + r * 17
            s.rect(x - 20, y, 9, 9); s.line(x - 6, y + 5, x + 20, y + 5)
            if r < 3: s.poly([(x - 19, y + 4), (x - 16, y + 8), (x - 10, y - 2)])
        blob('r', x - 28, TG - 90, 56, 90)

    def cone(x):
        s.poly([(x - 16, TG - 4), (x - 5, TG - 62), (x + 5, TG - 62), (x + 16, TG - 4)])
        s.rect(x - 22, TG - 4, 44, 4); s.line(x - 11, TG - 26, x + 11, TG - 26); s.line(x - 8, TG - 42, x + 8, TG - 42)
        blob('r', x - 14, TG - 58, 28, 54, c=FILLS[0])

    def barrier(x):
        s.rect(x - 44, TG - 54, 88, 20); s.hatch(x - 44, TG - 54, 88, 20, gap=12, ang=45)
        for lx in (x - 34, x + 34):
            s.line(lx, TG - 34, lx - 8, TG); s.line(lx, TG - 34, lx + 8, TG)
        s.rect(x - 6, TG - 64, 12, 10); s.line(x, TG - 64, x, TG - 72); s.line(x - 6, TG - 70, x - 9, TG - 74); s.line(x + 6, TG - 70, x + 9, TG - 74)
        blob('r', x - 44, TG - 54, 88, 20, c=FILLS[0])

    def crane(x):
        s.lattice(x, TG, x, TG - 170, 10, 10); s.lattice(x - 30, TG - 170, x + 110, TG - 170, 7, 10)
        s.line(x, TG - 192, x + 110, TG - 172); s.line(x, TG - 192, x - 30, TG - 172)
        s.line(x - 4, TG - 170, x, TG - 192); s.line(x + 4, TG - 170, x, TG - 192)
        hx = x + 80
        s.line(hx, TG - 166, hx, TG - 120); s.line(hx, TG - 120, hx - 26, TG - 104); s.line(hx, TG - 120, hx + 26, TG - 104)
        # tilted "under construction" board
        ang = math.radians(-9)
        cx, cy = hx, TG - 88
        pts = [(-34, -16), (34, -16), (34, 16), (-34, 16)]
        rp = [(cx + px * math.cos(ang) - py * math.sin(ang), cy + px * math.sin(ang) + py * math.cos(ang)) for px, py in pts]
        s.poly(rp, close=True)
        for t in (-6, 4):
            a = (cx - 24 * math.cos(ang) - t * math.sin(ang), cy - 24 * math.sin(ang) + t * math.cos(ang))
            b = (cx + 24 * math.cos(ang) - t * math.sin(ang), cy + 24 * math.sin(ang) + t * math.cos(ang))
            s.line(*a, *b)
        fills.append(f'<polygon points="{" ".join(f"{px + 5:.1f},{py - 5:.1f}" for px, py in rp)}" fill="{FILLS[2]}"/>')

    def hardhat(x):
        pts = [(x - 26 + 52 * i / 16, TG - 30 - math.sin(math.pi * i / 16) * 30) for i in range(17)]
        s.poly(pts); s.rect(x - 34, TG - 30, 68, 7); s.line(x, TG - 60, x, TG - 34); s.line(x - 9, TG - 58, x - 9, TG - 36)
        blob('c', x, TG - 36, 24, c=FILLS[0])

    def magnifier(x):
        s.circle(x, TG - 70, 20); s.circle(x, TG - 70, 14); s.line(x + 14, TG - 56, x + 32, TG - 30); s.line(x + 20, TG - 56, x + 36, TG - 34)
        s.line(x, TG - 30, x, TG); blob('c', x, TG - 70, 20, c=FILLS[1])

    def gear(x):
        cy, r = TG - 40, 26
        pts = []
        for k in range(40):
            a = k / 40 * 2 * math.pi
            rr = r + (6 if (k // 2) % 2 == 0 else 0)
            pts.append((x + rr * math.cos(a), cy + rr * math.sin(a)))
        s.poly(pts, close=True); s.circle(x, cy, 9); blob('c', x, cy, 26)

    def level(x):
        s.rect(x - 60, TG - 18, 120, 18); s.rect(x - 12, TG - 14, 24, 10); s.circle(x, TG - 9, 3)
        s.rect(x - 48, TG - 14, 8, 10); blob('r', x - 60, TG - 18, 120, 18, c=FILLS[2])

    def roller(x):
        s.rect(x - 30, TG - 120, 60, 22); s.poly([(x + 30, TG - 109), (x + 38, TG - 109), (x + 38, TG - 88), (x, TG - 84), (x, TG - 60)])
        s.rect(x - 5, TG - 60, 10, 60); blob('r', x - 30, TG - 120, 60, 22, c=FILLS[1])

    def bricks(x):
        for r in range(4):
            for i in range(3 - (r % 2)):
                s.rect(x - 36 + i * 24 + (r % 2) * 12, TG - (r + 1) * 12, 24, 12)
        blob('r', x - 36, TG - 48, 72, 48, c=FILLS[0])

    def ladder(x):
        s.line(x - 14, TG, x - 6, TG - 130); s.line(x + 14, TG, x + 22, TG - 130)
        for i in range(1, 9):
            t = i / 9
            s.line(x - 14 + 8 * t, TG - 130 * t, x + 14 + 8 * t, TG - 130 * t)

    def drill(x):
        s.rect(x - 26, TG - 92, 52, 26); s.rect(x - 14, TG - 66, 22, 50); s.rect(x - 18, TG - 16, 30, 16)
        s.line(x + 26, TG - 79, x + 52, TG - 79); s.line(x + 26, TG - 83, x + 52, TG - 79)
        blob('r', x - 26, TG - 92, 52, 26, c=FILLS[1])

    def shovel(x):
        s.rect(x - 3, TG - 150, 6, 90); s.rect(x - 10, TG - 160, 20, 10)
        s.poly([(x - 16, TG - 60), (x + 16, TG - 60), (x + 14, TG - 20), (x, TG - 6), (x - 14, TG - 20)], close=True)
        blob('r', x - 16, TG - 60, 32, 46, c=FILLS[2])

    def warning(x):
        s.poly([(x, TG - 64), (x + 32, TG - 8), (x - 32, TG - 8)], close=True)
        s.line(x, TG - 44, x, TG - 24); s.circle(x, TG - 16, 2); s.line(x, TG - 8, x, TG)
        fills.append(f'<polygon points="{x + 5},{TG - 69} {x + 37},{TG - 13} {x - 27},{TG - 13}" fill="{FILLS[2]}"/>')

    seq = [ruler, calculator, hammer, magnifier, barrier, clipboard, crane, wrench, cone, pencil, gear,
           bricks, hardhat, roller, warning, level, drill, ladder, shovel]
    x = 40
    for fn in seq:
        widths = {barrier: 110, crane: 170, level: 140, clipboard: 70, calculator: 62, bricks: 84, drill: 90, ruler: 34}
        w = widths.get(fn, 56)
        fn(x + w / 2)
        x += w + 22
    scale = (TW - 40) / x
    # sparkles
    for _ in range(26):
        sx, sy = R.uniform(20, TW - 20), R.uniform(16, TG - 120)
        kind = R.random()
        if kind < .4:
            s.line(sx - 4, sy, sx + 4, sy); s.line(sx, sy - 4, sx, sy + 4)
        elif kind < .7:
            s.poly([(sx - 6, sy), (sx - 2, sy - 3), (sx + 2, sy + 1), (sx + 6, sy - 2)])
        else:
            s.circle(sx, sy, 2.2)
    k = 0
    while k < TW:                                                    # dashed ground
        d = R.choice([10, 24, 50, 90]); s.line(k, TG + 6, k + d, TG + 6); k += d + R.choice([8, 14, 22])
    s.line(0, TG, TW, TG)
    body = (f'<g transform="scale({scale:.4f} 1)"><g opacity=".55">{"".join(fills)}</g></g>'
            f'<g transform="scale({scale:.4f} 1)" fill="none">{s.svg("#8a93a3", 1.6, .8)}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TW} {TH}" width="{TW}" height="{TH}" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


# =============================================================================
# CARD CORNER MOTIFS (How we deliver): white strokes, opacity set in CSS
# =============================================================================
def _svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 260" width="260" height="260" fill="none" '
            'stroke="#fff" stroke-linecap="round" stroke-linejoin="round" font-family="monospace" font-size="8">' + body + '</svg>')


def pat_plan():
    """Topographic survey: contour rings, spot heights, benchmark."""
    cx, cy, out = 205, 52, []
    for k in range(9):
        rk = 14 + k * 17
        pts = []
        for i in range(73):
            t = i / 72 * 2 * math.pi
            r = rk * (1 + .13 * math.sin(3 * t + k * .55) + .07 * math.cos(5 * t - k * .9))
            pts.append(f'{cx + r * math.cos(t):.1f},{cy + r * math.sin(t) * .86:.1f}')
        dash = ' stroke-dasharray="3 4"' if k % 4 == 3 else ''
        out.append(f'<polyline points="{" ".join(pts)}" stroke-width="{1.3 if k % 4 == 0 else .8}"{dash}/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="4"/><path d="M{cx - 11} {cy}h22M{cx} {cy - 11}v22"/>')
    for x, y, lbl in ((150, 96, '1482'), (96, 40, '1476'), (176, 150, '1470')):
        out.append(f'<path d="M{x - 3} {y - 3}l6 6M{x + 3} {y - 3}l-6 6"/><text x="{x + 6}" y="{y + 3}" fill="#fff" stroke="none">{lbl}</text>')
    return _svg(''.join(out))


def pat_build():
    """Structural gridlines with bubbles, columns, dimension line and a hatched opening."""
    xs, ys, out = (96, 156, 216), (70, 130, 190), []
    for i, x in enumerate(xs):
        out.append(f'<path d="M{x} 30V250" stroke-dasharray="10 4 2 4"/><circle cx="{x}" cy="20" r="9"/>'
                   f'<text x="{x - 2.6}" y="23" fill="#fff" stroke="none">{"ABC"[i]}</text>')
    for i, y in enumerate(ys):
        out.append(f'<path d="M40 {y}H246" stroke-dasharray="10 4 2 4"/><circle cx="252" cy="{y}" r="7" transform="translate(-6 0)"/>'
                   f'<text x="243.6" y="{y + 3}" fill="#fff" stroke="none">{i + 1}</text>')
    for x in xs:
        for y in ys:
            out.append(f'<rect x="{x - 5}" y="{y - 5}" width="10" height="10" fill="#fff" fill-opacity=".5"/>')
    out.append('<path d="M96 46H156M96 42v8M156 42v8M93 49l6-6M153 49l6-6" stroke-width=".8"/><text x="113" y="40" fill="#fff" stroke="none">6000</text>')
    hatch = ''.join(f'<path d="M{164 + k * 7} 122l-{min(k * 7, 44)} {min(k * 7, 44)}"/>' for k in range(1, 7))
    out.append(f'<rect x="164" y="78" width="44" height="44" stroke-width=".8"/><g stroke-width=".6">{hatch}</g>')
    return _svg(''.join(out))


def pat_deliver():
    """Progress gauge: tick ring, arcs, needle and completion arc."""
    cx, cy, out = 214, 46, []
    for i in range(72):
        a = math.radians(i * 5)
        r1, r2 = (100, 112) if i % 6 == 0 else (104, 110)
        out.append(f'<path d="M{cx + r1 * math.cos(a):.1f} {cy + r1 * math.sin(a):.1f}L{cx + r2 * math.cos(a):.1f} {cy + r2 * math.sin(a):.1f}" stroke-width="{1.2 if i % 6 == 0 else .7}"/>')
    for r, w, dash in ((40, 1, ''), (64, .8, ''), (86, 1.6, ' stroke-dasharray="2 5"')):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke-width="{w}"{dash}/>')
    a0, a1 = math.radians(95), math.radians(200)
    out.append(f'<path d="M{cx + 74 * math.cos(a0):.1f} {cy + 74 * math.sin(a0):.1f}A74 74 0 0 1 {cx + 74 * math.cos(a1):.1f} {cy + 74 * math.sin(a1):.1f}" stroke-width="4" stroke-opacity=".6"/>')
    na = math.radians(150)
    out.append(f'<path d="M{cx} {cy}L{cx + 92 * math.cos(na):.1f} {cy + 92 * math.sin(na):.1f}" stroke-width="1.4"/><circle cx="{cx}" cy="{cy}" r="5" fill="#fff" fill-opacity=".6"/>')
    out.append(f'<path d="M{cx - 30} {cy + 4}l6 6 12-14" stroke-width="1.4"/>')
    return _svg(''.join(out))


if __name__ == '__main__':
    for name, fn in (('lineart-site.svg', site_svg), ('lineart-tools.svg', tools_svg),
                     ('pat-plan.svg', pat_plan), ('pat-build.svg', pat_build), ('pat-deliver.svg', pat_deliver)):
        p = os.path.join(OUT, name)
        open(p, 'w', encoding='utf8').write(fn())
        print(name, os.path.getsize(p) // 1024, 'KB')

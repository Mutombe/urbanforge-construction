"""Ray-marched brand objects for Urban Forge.

Every object is a signed distance function (SDF). For each pixel a ray leaves a
virtual camera and steps forward by the SDF value until it touches the surface.
Materials are assigned by surface position, lit by a fake photo studio
(environment reflections + key / rim / top / fill lights), tone-mapped, rendered
at 2x and downsampled with premultiplied alpha so edges blend on any background.

Usage:  python _src/tools/render3d.py            (renders all objects)
        python _src/tools/render3d.py nut cone   (renders only those)
Output: assets/img/obj-<name>.webp  (transparent, 480x480)
"""
import os, sys
import numpy as np
from PIL import Image

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'img')
SIZE = 600            # final canvas before crop
SS = 2                # supersampling factor

# ---------- brand palette (linear-ish rgb) ----------
FORGE = np.array([1.00, 0.46, 0.22])     # orange metal F0  (logo #D56B43)
NAVY = np.array([0.020, 0.060, 0.190])   # lacquer          (logo #1A3460)
WHITE = np.array([0.92, 0.93, 0.95])


def norm(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


def rot(rx, ry, rz):
    rx, ry, rz = np.radians([rx, ry, rz])
    X = np.array([[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]])
    Y = np.array([[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]])
    Z = np.array([[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]])
    return Z @ Y @ X


# ---------- SDF primitives ----------
def sd_box(p, b, r=0.0):
    q = np.abs(p) - (np.asarray(b) - r)
    return np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(q.max(-1), 0) - r


def extrude(d2, z, h):
    w = np.stack([d2, np.abs(z) - h], -1)
    return np.minimum(w.max(-1), 0) + np.linalg.norm(np.maximum(w, 0), axis=-1)


def sd_hex2(px, py, r):
    k = np.array([-0.8660254, 0.5, 0.57735])
    px, py = np.abs(px), np.abs(py)
    d = np.minimum(k[0] * px + k[1] * py, 0)
    px, py = px - 2 * d * k[0], py - 2 * d * k[1]
    cx = np.clip(px, -k[2] * r, k[2] * r)
    return np.hypot(px - cx, py - r) * np.sign(py - r)


# ---------- objects: return (distance, material id) ----------
def obj_nut(p):
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    d = extrude(sd_hex2(x, z, 0.82), y, 0.34) - 0.035
    d = np.maximum(d, (np.hypot(x, z) * 0.78 + np.abs(y) * 0.62) - 0.98)   # chamfer
    hole = np.hypot(x, z) - 0.40
    d = np.maximum(d, -hole)
    # thread grooves inside the bore
    groove = np.hypot(x, z) - 0.40 - 0.035 * (0.5 + 0.5 * np.sin(y * 38))
    mat = np.where(hole < 0.02, 1, 0)
    return np.maximum(d, -groove) * 0.9, mat


def obj_ibeam(p):
    top = sd_box(p - [0, 0.52, 0], [1.25, 0.075, 0.46], 0.025)
    bot = sd_box(p + [0, 0.52, 0], [1.25, 0.075, 0.46], 0.025)
    web = sd_box(p, [1.25, 0.50, 0.06], 0.02)
    d = np.minimum(np.minimum(top, bot), web)
    # orange cut faces at the ends
    mat = np.where(np.abs(p[..., 0]) > 1.235, 0, 1)
    return d, mat


def obj_cone(p):
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    yy = y + 0.15
    r = 0.62 - (yy + 0.85) * (0.62 - 0.08) / 1.8           # radius along height
    d_cone = np.maximum((np.hypot(x, z) - r) * 0.95, np.abs(yy - 0.05) - 0.9) - 0.02
    base = sd_box(p - [0, -1.0, 0], [0.86, 0.07, 0.86], 0.08)
    d = np.minimum(d_cone, base)
    band = ((yy > -0.05) & (yy < 0.22)) | ((yy > 0.42) & (yy < 0.60))
    mat = np.where(band & (d_cone < base), 2, 0)          # 0 = orange plastic, 2 = reflective white
    mat = np.where(base <= d_cone, 1, mat)                  # base in navy rubber
    return d, mat


def obj_gear(p):
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    r = np.hypot(x, z)
    a = np.arctan2(z, x)
    n = 12
    seg = 2 * np.pi / n
    a2 = np.mod(a + seg / 2, seg) - seg / 2
    qx, qz = r * np.cos(a2), r * np.sin(a2)
    tooth = np.linalg.norm(np.maximum(np.abs(np.stack([qx - 0.92, qz], -1)) - [0.14, 0.10], 0), axis=-1) - 0.03
    d2 = np.minimum(r - 0.84, tooth)
    d2 = np.maximum(d2, -(r - 0.30))
    # spoke cut-outs
    seg3 = 2 * np.pi / 5
    b2 = np.mod(a + seg3 / 2, seg3) - seg3 / 2
    hx, hz = r * np.cos(b2) - 0.58, r * np.sin(b2)
    d2 = np.maximum(d2, -(np.hypot(hx, hz) - 0.15))
    d = extrude(d2, y, 0.16) - 0.02
    mat = np.where(r < 0.33, 1, 0)
    return d * 0.8, mat


def obj_globe(p):
    return np.linalg.norm(p, axis=-1) - 1.0, np.full(p.shape[:-1], 3)


OBJECTS = {
    #        sdf          pose (x, y, z)     scale
    'nut':   (obj_nut,    (58, 18, -16),   1.00),
    'ibeam': (obj_ibeam,  (22, -34, -18),  0.82),
    'cone':  (obj_cone,   (12, 22, -10),   0.92),
    'gear':  (obj_gear,   (62, 10, 22),    1.00),
    'globe': (obj_globe,  (18, -28, -14),  0.95),
}


# ---------- studio environment ----------
def env(d):
    y = d[..., 1]
    sky = np.array([0.95, 0.97, 1.0]); hor = np.array([0.30, 0.34, 0.42]); flo = np.array([0.10, 0.09, 0.10])
    t = np.clip(y, -1, 1)[..., None]
    c = np.where(t > 0, hor + (sky - hor) * np.sqrt(np.clip(t, 0, 1)), hor + (flo - hor) * np.sqrt(np.clip(-t, 0, 1)))
    c = c * (0.75 + 0.25 * np.clip(d[..., 0:1] + 0.6, 0, 1))          # darker on the left
    c = c * (0.65 + 0.35 * np.clip(d[..., 2:3] + 0.4, 0, 1))          # darker behind
    c = c + 1.6 * np.exp(-((y - 0.18) / 0.06) ** 2)[..., None]         # horizontal softbox
    c = c + 1.1 * np.exp(-((d[..., 0] - 0.75) / 0.08) ** 2)[..., None] * (y > -0.2)[..., None]
    return c


LIGHTS = [  # direction, sharpness, strength, colour
    (norm(np.array([-0.55, 0.75, 0.65])), 22, 4.2, np.array([1.0, 0.98, 0.95])),
    (norm(np.array([0.85, 0.25, -0.45])), 10, 1.6, np.array([0.75, 0.88, 1.0])),
    (norm(np.array([0.0, 1.0, 0.1])), 6, 0.6, np.array([1.0, 1.0, 1.0])),
    (norm(np.array([0.6, -0.4, 0.7])), 9, 0.5, np.array([1.0, 0.80, 0.55])),
]


def schlick(f0, ndv):
    return f0 + (1 - f0) * (1 - ndv)[..., None] ** 5


def shade(pos, n, v, mat, rotm):
    ndv = np.clip((n * v).sum(-1), 0, 1)
    refl = norm(2 * ndv[..., None] * n - v)
    envc = env(refl)
    diff = np.zeros_like(pos); spec = np.zeros_like(pos)
    for L, sharp, k, col in LIGHTS:
        ndl = np.clip((n * L).sum(-1), 0, 1)
        h = norm(L + v)
        ndh = np.clip((n * h).sum(-1), 0, 1)
        diff += (ndl * k / 4.2)[..., None] * col
        spec += (k / 4.2 * (ndh ** (sharp * 5.5)))[..., None] * col
    out = np.zeros_like(pos)

    # 0: forge-orange metal
    m = mat == 0
    F = schlick(FORGE, ndv[m])
    out[m] = envc[m] * F * 0.95 + FORGE * 0.12 * diff[m] + 2.2 * spec[m] * [1, 0.92, 0.82]
    out[m] *= [1.05, 0.95, 0.85]
    # 1: navy lacquer
    m = mat == 1
    F = schlick(np.full(3, 0.04), ndv[m])
    out[m] = NAVY * (0.35 + 0.9 * diff[m]) + envc[m] * F * 0.75 + 1.4 * spec[m] \
        + np.array([0, 0.15, 0.45]) * ((1 - ndv[m]) ** 3 * 0.35)[..., None]
    # 2: reflective white band
    m = mat == 2
    F = schlick(np.full(3, 0.05), ndv[m])
    out[m] = WHITE * (0.30 + 0.75 * diff[m]) + envc[m] * F * 0.6 + 1.2 * spec[m]
    # 3: pearl globe with forge-orange inlay lines (in object space)
    m = mat == 3
    if m.any():
        lp = pos[m] @ rotm                      # back into object space
        lat = np.arcsin(np.clip(lp[:, 1], -1, 1)); lon = np.arctan2(lp[:, 2], lp[:, 0])
        line = (np.abs(np.sin(lat * 6)) < 0.07) | ((np.abs(np.sin(lon * 3)) < 0.06) & (np.abs(lp[:, 1]) < 0.9))
        up = np.clip(n[m][:, 1] * 0.5 + 0.5, 0, 1)[:, None]
        body = np.array([0.02, 0.07, 0.22]) * (1 - up) + np.array([0.30, 0.45, 0.75]) * up
        F = schlick(np.full(3, 0.04), ndv[m])
        c = body * (0.35 + 0.85 * diff[m]) + np.array([0.55, 0.75, 1.0]) * ((1 - ndv[m]) ** 2.5 * 0.5)[:, None] \
            + envc[m] * F * 0.9 + 2.0 * spec[m] + 0.18 * spec[m] ** 0.05
        Fm = schlick(FORGE, ndv[m])
        metal = envc[m] * Fm * 0.95 + FORGE * 0.15 * diff[m] + 2.0 * spec[m]
        out[m] = np.where(line[:, None], metal, c)
    return out


def render(name):
    sdf, pose, scale = OBJECTS[name]
    R = rot(*pose)
    N = SIZE * SS
    u = (np.arange(N) + 0.5) / N * 2 - 1
    X, Y = np.meshgrid(u, -u)
    ro = np.array([0, 0, 5.0])
    rd = norm(np.stack([X * 0.33 * 1.0, Y * 0.33, -np.ones_like(X)], -1)).reshape(-1, 3)

    def field(p):
        d, m = sdf((p @ R) / scale)
        return d * scale, m

    t = np.full(len(rd), 2.5); hit = np.zeros(len(rd), bool); alive = np.ones(len(rd), bool)
    for _ in range(300):
        idx = np.nonzero(alive)[0]
        if len(idx) == 0:
            break
        d, _ = field(ro + rd[idx] * t[idx, None])
        t[idx] += d * 0.9
        h = d < 0.0008
        hit[idx[h]] = True
        alive[idx[h | (t[idx] > 7.5)]] = False

    idx = np.nonzero(hit)[0]
    pos = ro + rd[idx] * t[idx, None]
    _, mat = field(pos)
    e = 0.0015
    ks = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], float)
    n = sum(k * field(pos + k * e)[0][:, None] for k in ks)
    n = norm(n)
    v = -rd[idx]
    col = shade(pos, n, v, mat, R)
    ao = np.ones(len(idx))
    for i in range(1, 6):
        h = 0.06 * i
        ao -= (h - field(pos + n * h)[0]) * (0.5 ** i) * 2.4
    col *= np.clip(ao, 0.35, 1)[:, None]
    col = 1 - np.exp(-1.75 * np.clip(col, 0, None))     # tone map

    img = np.zeros((N * N, 4))
    img[idx, :3] = col; img[idx, 3] = 1
    img = img.reshape(N, N, 4)
    # premultiplied 2x2 downsample
    img = img.reshape(SIZE, SS, SIZE, SS, 4).mean((1, 3))
    a = img[..., 3:4]
    rgb = np.where(a > 0, img[..., :3] / np.maximum(a, 1e-6), 0)
    out = np.concatenate([rgb, a], -1)
    im = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), 'RGBA')
    bb = im.getchannel('A').getbbox()
    im = im.crop((bb[0] - 16, bb[1] - 16, bb[2] + 16, bb[3] + 16))
    side = max(im.size); sq = Image.new('RGBA', (side, side))
    sq.alpha_composite(im, ((side - im.width) // 2, (side - im.height) // 2))
    sq = sq.resize((480, 480), Image.LANCZOS)
    path = os.path.join(OUT, f'obj-{name}.webp')
    sq.save(path, 'WEBP', quality=90, method=6)
    print('rendered', path)


if __name__ == '__main__':
    for nm in (sys.argv[1:] or OBJECTS):
        render(nm)

# Mythbound, Highwatch Hall portraits as key art.
# capture (green screen, in-game light rig) -> key -> painted sky behind -> rim glow -> painterly pass -> varnish by age
import sys, os, json, math
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
RAW, OUT = os.path.join(HERE, "raw"), os.path.join(HERE, "final")
os.makedirs(OUT, exist_ok=True)

def smooth_noise(h, w, scale, rng, octaves=4):
    acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        s = max(2, int(scale / (2 ** o)))
        small = rng.random((h // s + 2, w // s + 2)).astype(np.float32)
        big = cv2.resize(small, (w + 2 * s, h + 2 * s), interpolation=cv2.INTER_CUBIC)[s:s + h, s:s + w]
        acc += big * amp; tot += amp; amp *= 0.5
    acc /= tot
    return (acc - acc.min()) / (acc.max() - acc.min() + 1e-6)

PALETTES = {
    # top, horizon, glow (BGR order handled below, given as RGB here)
    "dawn":   ((34, 48, 78), (226, 168, 104), (255, 214, 150)),
    "dusk":   ((30, 30, 62), (196, 110, 92), (255, 182, 128)),
    "gold":   ((40, 54, 70), (214, 176, 110), (255, 230, 170)),
    "storm":  ((22, 30, 44), (96, 116, 138), (210, 220, 236)),
    "ember":  ((36, 22, 26), (170, 76, 46), (255, 160, 96)),
    "teal":   ((18, 44, 56), (120, 168, 160), (236, 232, 196)),
}

def sky(h, w, pal, seed, sun=(0.62, 0.30)):
    rng = np.random.default_rng(seed)
    top, hor, glow = [np.array(c[::-1], np.float32) / 255 for c in PALETTES[pal]]
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    grad = top * (1 - y ** 0.9) + hor * (y ** 0.9)
    img = np.broadcast_to(grad, (h, w, 3)).copy()
    # sun glow behind the sitter
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - sun[0] * w) / w) ** 2 + ((yy - sun[1] * h) / h) ** 2)
    g = np.exp(-(d / 0.32) ** 2)[..., None]
    img = img * (1 - 0.75 * g) + glow * 0.75 * g
    # painted clouds: two layers of soft noise, lit from the sun side
    n1 = smooth_noise(h, w, 180, rng, 5); n2 = smooth_noise(h, w, 90, rng, 4)
    band = np.clip(1 - np.abs(y[..., 0] - 0.55) * 2.2, 0, 1)
    cl = np.clip((n1 * 0.7 + n2 * 0.3 - 0.48) * 3.2, 0, 1) * band
    cl = cv2.GaussianBlur(cl, (0, 0), 3)
    lit = np.clip(1.15 - d * 1.6, 0.25, 1)
    cloud_col = hor * 0.55 + glow * 0.45
    img = img * (1 - cl[..., None] * 0.55) + (cloud_col * lit[..., None]) * cl[..., None] * 0.55
    # far mountains: two ridges, cool and hazy
    xs = np.arange(w, dtype=np.float32)
    for k, (base, amp, col, sc) in enumerate([(0.80, 0.10, 0.62, 160), (0.88, 0.07, 0.42, 90)]):
        r = smooth_noise(1, w, sc, rng, 4)[0] if False else None
        line = np.zeros(w, np.float32)
        for f, a in [(1 / 210, 1.0), (1 / 90, 0.45), (1 / 37, 0.2)]:
            line += a * np.sin(xs * f * 2 * math.pi + rng.random() * 6.28)
        line = base * h - amp * h * (0.5 + 0.5 * line / 1.65)
        mask = (yy >= line[None, :]).astype(np.float32)
        mask = cv2.GaussianBlur(mask, (0, 0), 1.2)[..., None]
        mcol = img * col + top * (1 - col) * 0.6
        img = img * (1 - mask) + mcol * mask
    # god rays from the sun
    ang = np.arctan2(yy - sun[1] * h, xx - sun[0] * w)
    rays = (0.5 + 0.5 * np.sin(ang * 23 + rng.random() * 6)) * (0.5 + 0.5 * np.sin(ang * 9 + 1.3))
    rays = rays * np.exp(-(d / 0.6) ** 2)
    img = img + glow * (rays[..., None] * 0.10)
    return np.clip(img, 0, 1)

def key(im):
    f = im.astype(np.float32) / 255
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    dom = g - np.maximum(r, b)
    a = 1 - np.clip((dom - 0.18) / (0.42 - 0.18), 0, 1)
    a = cv2.GaussianBlur(a, (0, 0), 0.7)
    # despill: green never above the brighter of red and blue
    g2 = np.minimum(g, np.maximum(r, b) * 1.02)
    f = np.dstack([b, g2, r])
    return f, a

def painterly(img):
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    oil = cv2.xphoto.oilPainting(u8, 4, 1)
    soft = cv2.edgePreservingFilter(u8, flags=1, sigma_s=20, sigma_r=0.22)
    mix = cv2.addWeighted(oil, 0.45, soft, 0.55, 0)
    blur = cv2.GaussianBlur(mix, (0, 0), 1.4)
    sharp = cv2.addWeighted(mix, 1.5, blur, -0.5, 0)
    return sharp.astype(np.float32) / 255

def canvas(h, w, seed):
    rng = np.random.default_rng(seed)
    x = np.arange(w)[None, :]; y = np.arange(h)[:, None]
    weave = 0.5 + 0.22 * np.sin(x * 2.1) * np.sin(y * 1.9) + 0.28 * rng.random((h, w))
    return cv2.GaussianBlur(weave.astype(np.float32), (0, 0), 0.6)

def crackle(h, w, seed, strength):
    if strength <= 0:
        return np.zeros((h, w), np.float32)
    rng = np.random.default_rng(seed)
    n = smooth_noise(h, w, 26, rng, 3)
    # cell borders of the noise read as fine cracks
    lap = np.abs(cv2.Laplacian(n, cv2.CV_32F, ksize=3))
    lap = np.clip((lap - np.percentile(lap, 91)) * 40, 0, 1)
    return lap * strength

def build(spec):
    name = spec["id"]
    im = cv2.imread(os.path.join(RAW, name + ".png"), cv2.IMREAD_COLOR)
    H0, W0 = im.shape[:2]
    W, H = spec.get("size", (560, 720))
    ch = int(H0 * spec.get("zoom", 1.0))
    cw = int(ch * W / H)
    cx = int(W0 * spec.get("cx", 0.5)); cy = int(H0 * spec.get("cy", 0.5))
    x0 = max(0, min(W0 - cw, cx - cw // 2)); y0 = max(0, min(H0 - ch, cy - ch // 2))
    im = im[y0:y0 + ch, x0:x0 + cw]
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4 if ch < H else cv2.INTER_AREA)
    if spec.get("mirror"):
        im = im[:, ::-1].copy()
    fg, a = key(im)
    fg = np.clip(fg * spec.get('lift', 1.0), 0, 1)
    bg = sky(H, W, spec.get("pal", "dawn"), spec.get("seed", 1), sun=tuple(spec.get("sun", (0.6, 0.3))))
    # soft depth: the sky a touch blurred
    bg = cv2.GaussianBlur(bg, (0, 0), 1.6)
    # warm rim halo around the sitter (light wrapping from the sky)
    edge = cv2.GaussianBlur(a, (0, 0), 6) - a
    halo = np.clip(edge * 2.2, 0, 1)[..., None]
    glow = np.array(PALETTES[spec.get("pal", "dawn")][2][::-1], np.float32) / 255
    A = a[..., None]
    img = fg * A + bg * (1 - A)
    img = img + glow * halo * 0.35 * (1 - A)
    # light wrap on the sitter's edge
    inner = np.clip(A - cv2.GaussianBlur(a, (0, 0), 2.0)[..., None], 0, 1) * 0
    img = painterly(img)
    # grade: S curve, warm varnish (more with age), vignette
    age = spec.get("age", 0.0)
    img = img * img * (3 - 2 * img) * 0.5 + img * 0.5
    warm = np.array([0.86 - 0.08 * age, 0.99, 1.05 + 0.03 * age], np.float32)
    img = np.clip(img * warm + np.array([0, 0.004, 0.018], np.float32) * (1 + age), 0, 1)
    gray = img.mean(axis=2, keepdims=True)
    img = gray + (img - gray) * (0.92 - 0.18 * age)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.42) / (H * 0.72)) ** 2)
    v = np.clip(1.18 - d ** 2.2, 0.32, 1.0)[..., None]
    img = img * v
    cv_ = canvas(H, W, spec.get("seed", 1))[..., None]
    img = np.clip(img * (0.9 + 0.2 * cv_), 0, 1)
    cr = crackle(H, W, spec.get("seed", 1) + 7, 0.35 * age)[..., None]
    img = img * (1 - cr * 0.55)
    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    cv2.imwrite(os.path.join(OUT, name + ".png"), out)
    return out

if __name__ == "__main__":
    specs = json.load(open(os.path.join(HERE, "specs.json")))
    only = sys.argv[1:] or None
    outs = []
    for s in specs:
        if only and s["id"] not in only:
            continue
        if not os.path.exists(os.path.join(RAW, s["id"] + ".png")):
            continue
        outs.append((s["id"], build(s)))
    if outs:
        th = 360
        tiles = [cv2.resize(o, (int(o.shape[1] * th / o.shape[0]), th)) for _, o in outs]
        rows = [tiles[i:i + 5] for i in range(0, len(tiles), 5)]
        wmax = max(sum(t.shape[1] for t in r) for r in rows)
        sheet = np.zeros((th * len(rows), wmax, 3), np.uint8)
        for ri, r in enumerate(rows):
            x = 0
            for t in r:
                sheet[ri * th:(ri + 1) * th, x:x + t.shape[1]] = t; x += t.shape[1]
        cv2.imwrite(os.path.join(HERE, "sheet.png"), sheet)
    print("built", [n for n, _ in outs])

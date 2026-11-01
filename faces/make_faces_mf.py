"""Mythbound faces v5, the clean "man face" look (Philip, 1 November, with three references of sharp anime faces on
Roblox heads: "the faces are so weird, make them more like these"). Our own drawing, not a copy of those items:
  - bold black ink, few lines, confident shapes (no fiddly strands)
  - narrow eyes: a heavy upper lid line that thickens to the outer corner and ends in a sharp flick, the iris tucked
    under the lid, a dark rim, one clean highlight, a thin broken lower lid
  - thick angular brows set low over the eyes, blunt inner end, a peak, a thin tail, a few hairs at the ends
  - a long line down one side of the nose with a painted tip and nostrils
  - a short mouth line with a soft lower lip shadow
  - soft painted shading only as darkening/highlight with alpha, so one decal works on every skin
1024 x 1024, transparent. Parts are drawn by functions taking a dict of numbers, so variants are cheap.
Run: python3 make_faces_mf.py -> faces/mf/*.png and a preview sheet"""
import cairo, math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "mf")
os.makedirs(OUT, exist_ok=True)
S = 1024
INK = (0.06, 0.045, 0.05)
SHADE = (0.36, 0.17, 0.11)
CX = S / 2

def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])

def ribbon(ctx, pts, wf, color=INK, alpha=1.0, n=60):
    """a filled stroke along a cubic bezier, wf(t) gives the width"""
    P = [bez(*pts, i / n) for i in range(n + 1)]
    L, R = [], []
    for i, p in enumerate(P):
        a = P[max(0, i - 1)]; b = P[min(n, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d; w = max(0.0, wf(i / n))
        L.append((p[0] + nx * w / 2, p[1] + ny * w / 2)); R.append((p[0] - nx * w / 2, p[1] - ny * w / 2))
    ctx.new_path(); ctx.move_to(*L[0])
    for q in L[1:]: ctx.line_to(*q)
    for q in reversed(R): ctx.line_to(*q)
    ctx.close_path(); ctx.set_source_rgba(*color, alpha); ctx.fill()

def taper(w0, w1, a=0.12, b=0.25, pw=0.8):
    """width from w0 to w1, pointed at both ends over the first a and last b of the stroke"""
    def f(t):
        w = w0 + (w1 - w0) * t
        if t < a: w *= (t / a) ** pw
        if t > 1 - b: w *= ((1 - t) / b) ** pw
        return w
    return f

def soft(ctx, x, y, rx, ry, color, alpha, angle=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle); ctx.scale(max(rx, 0.1), max(ry, 0.1))
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0, *color, alpha); g.add_color_stop_rgba(1, *color, 0)
    ctx.arc(0, 0, 1, 0, math.tau); ctx.set_source(g); ctx.fill(); ctx.restore()

def shape(ctx, top_pts, bot_pts):
    """closed region between two beziers that share end points (top left->right, bottom right->left)"""
    ctx.new_path(); ctx.move_to(*top_pts[0]); ctx.curve_to(*top_pts[1], *top_pts[2], *top_pts[3])
    ctx.curve_to(*bot_pts[1], *bot_pts[2], *bot_pts[3]); ctx.close_path()

# ============================================================ the parts

BASE = dict(
    eyeY=425, eyeGap=195, eyeW=245, open=64, tilt=10, lidPeak=0.38, lidW=17, flick=40, flickDrop=6, lowerGap=0.25,
    iris=0.72, irisCol=(0.35, 0.33, 0.33), irisY=0.22, look=0.0, pupil="round", shine=True, glow=None, sclera=None,
    crease=1, hatch=0, hatchLow=0,
    browY=74, browW=265, browT=38, browAng=12, browPeak=0.6, browArch=10, browCol=INK, hairs=5,
    noseY=645, noseLen=200, noseSide=1, noseW=1.3, nose="line",
    mouthY=748, mouthW=120, smile=0, smirk=0, mouth="line", lip=0.3,
    socket=0.16, cheeks=0.0, seed=1,
)

# Global eye shape for the player parts (Philip, 1 Nov: "iets meer hoogte in de ogen"): OPEN_K makes every
# eye taller, EYEW_K a little narrower; the brows move up with the taller lid
OPEN_K = float(os.environ.get("FACE_OPEN", "1.0"))
EYEW_K = float(os.environ.get("FACE_EYEW", "1.0"))
# the iris does not grow with the taller eye (Philip: "die pupillen zijn zo groot, ietsjes kleiner")
IRIS_K = float(os.environ.get("FACE_IRIS", str(OPEN_K)))

def eye_geo(f, side):
    cx = CX + side * f["eyeGap"]; cy = f["eyeY"]
    w = f["eyeW"] * EYEW_K; h = f["open"] * OPEN_K; tl = f["tilt"]
    I = (cx - side * w * 0.5, cy + h * 0.18 + tl * 0.3)       # inner corner
    O = (cx + side * w * 0.5, cy - tl * 0.7)                    # outer corner
    Pk = (cx - side * w * (0.5 - f["lidPeak"]), cy - h * 0.62)  # top of the lid
    up = (I, (I[0] + side * w * 0.08, I[1] - h * 0.55), (Pk[0] - side * w * 0.18, Pk[1]), Pk)
    up2 = (Pk, (Pk[0] + side * w * 0.28, Pk[1] + h * 0.02), (O[0] - side * w * 0.1, O[1] - h * 0.25), O)
    Bt = (cx + side * w * 0.06, cy + h * 0.42)
    low = (O, (O[0] - side * w * 0.12, Bt[1] - h * 0.02), (Bt[0] + side * w * 0.25, Bt[1] + 2), (I[0] + side * w * 0.04, I[1] + h * 0.05))
    return cx, cy, w, h, I, O, Pk, up, up2, low

def eye(ctx, f, side, layer=None):
    """layer None draws the whole eye; "white", "iris" (a grey ramp the decal's Color3 tints) and "lines" are the
    three decals of a modular eye (the white, the colour, everything inked on top)"""
    cx, cy, w, h, I, O, Pk, up, up2, low = eye_geo(f, side)
    if f.get("glow") and layer in (None, "white"):
        soft(ctx, cx, cy, w * 0.7, h * 1.4, f["glow"], 0.4)
    # the white, clipped by the lids
    def opening():
        ctx.new_path(); ctx.move_to(*I)
        ctx.curve_to(*up[1], *up[2], *up[3]); ctx.curve_to(*up2[1], *up2[2], *up2[3])
        ctx.curve_to(*low[1], *low[2], *low[3]); ctx.close_path()
    r = f["open"] * IRIS_K * f["iris"] * 1.35
    ix = cx + side * w * 0.03 + f["look"] * w * 0.18
    iy = cy - h * 0.05 + h * f["irisY"]
    if layer in (None, "white"):
        opening(); ctx.set_source_rgba(*(f["sclera"] or (0.97, 0.96, 0.95)), 1); ctx.fill()
        ctx.save(); opening(); ctx.clip()
        # the lid's shadow on the white
        g = cairo.LinearGradient(0, cy - h * 0.7, 0, cy + h * 0.3)
        g.add_color_stop_rgba(0, 0.2, 0.15, 0.17, 0.55); g.add_color_stop_rgba(1, 0.2, 0.15, 0.17, 0.0)
        ctx.rectangle(0, 0, S, S); ctx.set_source(g); ctx.fill()
        ctx.restore()
        if layer == "white":
            return
    ctx.save(); opening(); ctx.clip()
    # the iris: big, tucked under the lid
    col = f["irisCol"]
    if layer == "iris":
        gi = cairo.RadialGradient(ix, iy + r * 0.3, r * 0.1, ix, iy, r)
        gi.add_color_stop_rgba(0, 1, 1, 1, 1); gi.add_color_stop_rgba(0.7, 0.72, 0.72, 0.72, 1); gi.add_color_stop_rgba(1, 0.3, 0.3, 0.3, 1)
        ctx.arc(ix, iy, r, 0, math.tau); ctx.set_source(gi); ctx.fill()
        ctx.restore()
        return
    if layer is None:
        gi = cairo.RadialGradient(ix, iy + r * 0.3, r * 0.1, ix, iy, r)
        gi.add_color_stop_rgba(0, *(min(1, c * 1.5 + 0.12) for c in col), 1); gi.add_color_stop_rgba(0.7, *col, 1)
        gi.add_color_stop_rgba(1, *(c * 0.35 for c in col), 1)
        ctx.arc(ix, iy, r, 0, math.tau); ctx.set_source(gi); ctx.fill()
    ctx.arc(ix, iy, r - 3, 0, math.tau); ctx.set_line_width(6); ctx.set_source_rgba(*INK, 0.95); ctx.stroke()
    pu = f["pupil"]
    if pu == "round":
        ctx.arc(ix, iy, r * 0.42, 0, math.tau); ctx.set_source_rgba(*INK, 1); ctx.fill()
    elif pu == "slit":
        ctx.save(); ctx.translate(ix, iy); ctx.scale(0.14, 0.9); ctx.arc(0, 0, r, 0, math.tau); ctx.restore()
        ctx.set_source_rgba(*INK, 1); ctx.fill()
    elif pu == "dot":
        ctx.arc(ix, iy, r * 0.18, 0, math.tau); ctx.set_source_rgba(*INK, 1); ctx.fill()
    elif pu == "ring":
        ctx.arc(ix, iy, r * 0.55, 0, math.tau); ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.stroke()
        ctx.arc(ix, iy, r * 0.2, 0, math.tau); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill()
    # the top of the iris goes dark under the lid
    g2 = cairo.LinearGradient(0, iy - r, 0, iy + r * 0.2)
    g2.add_color_stop_rgba(0, *INK, 0.8); g2.add_color_stop_rgba(1, *INK, 0)
    ctx.arc(ix, iy, r, 0, math.tau); ctx.set_source(g2); ctx.fill()
    if f["shine"]:
        ctx.save(); ctx.translate(ix - side * r * 0.32, iy - r * 0.05); ctx.rotate(side * 0.4); ctx.scale(r * 0.2, r * 0.15)
        ctx.arc(0, 0, 1, 0, math.tau); ctx.restore(); ctx.set_source_rgba(1, 1, 1, 0.97); ctx.fill()
        ctx.arc(ix + side * r * 0.3, iy + r * 0.38, r * 0.07, 0, math.tau); ctx.set_source_rgba(1, 1, 1, 0.7); ctx.fill()
    ctx.restore()
    lw = f["lidW"]
    # the upper lid line: thin at the inner corner, heavy outward, out to a sharp flick past the corner
    ribbon(ctx, up, lambda t: lw * (0.25 + 0.65 * t), alpha=1)
    T = (O[0] + side * f["flick"], O[1] + f["flickDrop"])
    up3 = (Pk, (Pk[0] + side * w * 0.28, Pk[1] + h * 0.02), (O[0] - side * w * 0.05, O[1] - h * 0.3), T)
    ribbon(ctx, up3, lambda t: (lw * (0.9 + 0.6 * math.sin(math.pi * min(1, t * 1.15)))) * (1 - t) ** 0.45 + 1.5)
    # a second, lower flick under the first (a lash wedge at the outer corner)
    T2 = (O[0] + side * f["flick"] * 0.55, O[1] + f["flickDrop"] + lw * 0.9)
    ribbon(ctx, (lerp(O, Pk, 0.18), lerp(O, T2, 0.3), lerp(O, T2, 0.7), T2), taper(lw * 0.9, lw * 0.2, 0.05, 0.6))
    # the inner corner hook
    ribbon(ctx, ((I[0] + side * 6, I[1] - 4), (I[0] - side * 3, I[1] + 4), (I[0] - side * 6, I[1] + 10), (I[0] - side * 5, I[1] + 18)), taper(lw * 0.45, 1, 0.1, 0.6), alpha=0.9)
    # the lower lid: a thin line from the outer corner, fading before the inner corner
    gap = f["lowerGap"]
    sub = [bez(*low, gap * 0.4 + i * (1 - gap - gap * 0.4) / 3) for i in range(4)]
    ribbon(ctx, (lerp(O, sub[0], 0.6), sub[1], sub[2], sub[3]), lambda t: (lw * 0.36) * (1 - t) ** 0.7 + 1.2, alpha=0.85)
    # the crease above the lid
    for k in range(f["crease"]):
        off = h * (0.45 + k * 0.28)
        c0 = (cx - side * w * 0.2, Pk[1] - off + h * 0.25); c3 = (O[0] + side * 6, O[1] - off * 0.9)
        ribbon(ctx, (c0, (cx, Pk[1] - off), (cx + side * w * 0.3, Pk[1] - off + 4), c3), taper(1, 4.5, 0.3, 0.2), alpha=0.75 - 0.25 * k)
    rng = random.Random(f["seed"] * 7 + side)
    for k in range(f["hatch"]):  # fine hatching between lid and brow
        u = 0.25 + k * 0.6 / max(1, f["hatch"])
        p = bez(*up2, u); y0 = p[1] - h * 0.32 - rng.uniform(0, 5)
        ribbon(ctx, ((p[0] - side * 22, y0 + 7), (p[0] - side * 6, y0), (p[0] + side * 10, y0 - 4), (p[0] + side * 26, y0 - 3)), taper(1, 3, 0.3, 0.4), alpha=0.7)
    for k in range(f["hatchLow"]):  # short strokes under the eye
        x0 = cx + side * (k * 22 - 20); y0 = cy + h * 0.72 + abs(k - 1) * 3
        ribbon(ctx, ((x0, y0), (x0 + side * 4, y0 + 6), (x0 + side * 8, y0 + 12), (x0 + side * 11, y0 + 18)), taper(3, 1, 0.2, 0.5), alpha=0.6)

def brow(ctx, f, side):
    cx = CX + side * f["eyeGap"]; base = f["eyeY"] - f["browY"] - (OPEN_K - 1) * f["open"] * 0.62
    w = f["browW"]; t = f["browT"]; ang = f["browAng"] * 2.2; arch = f["browArch"]
    inner = (cx - side * w * 0.5, base + ang * 0.5)
    peak = (cx + side * w * (f["browPeak"] - 0.5), base - ang * 0.25 - arch)
    tail = (cx + side * w * 0.52, base + 6 - ang * 0.05 + arch * 0.4)
    col = f["browCol"]
    # one closed shape: blunt slanted inner end, thickest a third of the way out, a thin pointed tail
    iT = (inner[0] + side * t * 0.25, inner[1] - t * 0.55)       # inner end, top (slanted cut)
    iB = (inner[0] - side * t * 0.05, inner[1] + t * 0.45)       # inner end, bottom
    pT = (peak[0], peak[1] - t * 0.42); pB = (peak[0] - side * w * 0.04, peak[1] + t * 0.48)
    ctx.new_path(); ctx.move_to(*iT)
    ctx.curve_to(*lerp(iT, pT, 0.4), *(pT[0] - side * w * 0.12, pT[1]), *pT)
    ctx.curve_to(*(pT[0] + side * w * 0.12, pT[1] + t * 0.05), *lerp(pT, tail, 0.6), *tail)
    ctx.curve_to(*lerp(tail, pB, 0.45), *(pB[0] + side * w * 0.1, pB[1]), *pB)
    ctx.curve_to(*(pB[0] - side * w * 0.15, pB[1]), *lerp(pB, iB, 0.6), *iB)
    ctx.close_path(); ctx.set_source_rgba(*col, 1); ctx.fill()
    rng = random.Random(f["seed"] * 11 + side)
    # short hairs: standing up at the inner end, feathering out along the top towards the tail
    for k in range(f["hairs"]):
        u = rng.uniform(0.0, 0.18)
        p = lerp(iB, iT, rng.uniform(0.3, 1.0)); p = (p[0] + side * u * w * 0.5, p[1])
        q = (p[0] + side * rng.uniform(4, 12), p[1] - t * rng.uniform(0.35, 0.6))
        ribbon(ctx, (p, lerp(p, q, 0.4), lerp(p, q, 0.75), q), taper(4.5, 1, 0.05, 0.6), color=col)
    for k in range(5):
        u = 0.15 + k * 0.17
        p = bez(iT, lerp(iT, pT, 0.4), (pT[0] - side * w * 0.12, pT[1]), pT, min(1, u * 1.4)) if u < 0.7 else lerp(pT, tail, (u - 0.7) / 0.5)
        q = (p[0] + side * rng.uniform(14, 24), p[1] - rng.uniform(3, 8))
        ribbon(ctx, ((p[0] - side * 8, p[1] + 3), lerp(p, q, 0.4), lerp(p, q, 0.75), q), taper(4, 1, 0.05, 0.6), color=col)

def nose(ctx, f):
    y = f["noseY"]; s = f["noseW"]; side = f["noseSide"]; kind = f["nose"]
    top = f["eyeY"] + 10; L = y - top
    # the long line down the shadow side of the bridge, curving into the side of the tip
    if kind in ("line", "strong"):
        wmax = 5 if kind == "line" else 8
        ribbon(ctx, ((CX + side * 8, top), (CX + side * 12, top + L * 0.45), (CX + side * 20 * s, top + L * 0.8), (CX + side * 30 * s, y - 14)), taper(1, wmax, 0.25, 0.15), alpha=0.85)
        soft(ctx, CX + side * 24 * s, top + L * 0.6, 16 * s, L * 0.38, SHADE, 0.3)
    # the tip: shadow under it, the light on top, the nostril wings
    soft(ctx, CX, y + 16, 50 * s, 18, SHADE, 0.38)
    soft(ctx, CX - side * 6, y - 12, 20 * s, 16, (1, 1, 1), 0.3)
    soft(ctx, CX - side * 4, top + L * 0.5, 7, L * 0.3, (1, 1, 1), 0.18)
    for sx in (-1, 1):
        ribbon(ctx, ((CX + sx * 30 * s, y - 10), (CX + sx * 40 * s, y + 4), (CX + sx * 30 * s, y + 14), (CX + sx * 14 * s, y + 13)), taper(1.5, 4.5, 0.2, 0.3), alpha=0.85)
        soft(ctx, CX + sx * 18 * s, y + 9, 9 * s, 5, INK, 0.55)
    if kind == "strong":
        ribbon(ctx, ((CX - 16 * s, y + 20), (CX - 4 * s, y + 24), (CX + 6 * s, y + 24), (CX + 16 * s, y + 20)), taper(1, 3), alpha=0.6)

def mouth(ctx, f):
    y = f["mouthY"]; w = f["mouthW"]; c = f["smile"]; sk = f["smirk"]
    l = (CX - w / 2, y - c * 0.5 + sk); r = (CX + w / 2, y - c * 0.5 - sk)
    if f["mouth"] == "open":
        ctx.new_path(); ctx.move_to(*l)
        ctx.curve_to(CX - w * 0.2, y + c * 0.5, CX + w * 0.2, y + c * 0.5, *r)
        ctx.curve_to(CX + w * 0.2, y + c * 0.5 + 34, CX - w * 0.2, y + c * 0.5 + 34, *l)
        ctx.close_path(); ctx.set_source_rgba(0.22, 0.07, 0.07, 1); ctx.fill_preserve(); ctx.save(); ctx.clip()
        ctx.rectangle(CX - w * 0.42, y - 30, w * 0.84, 30 + c * 0.5 + 9); ctx.set_source_rgba(1, 1, 1, 1); ctx.fill(); ctx.restore()
    ribbon(ctx, (l, (CX - w * 0.2, y + c * 0.5), (CX + w * 0.2, y + c * 0.5), r), taper(3, 3, 0.15, 0.15) if False else (lambda t: 2.5 + 6 * math.sin(math.pi * t) ** 0.6), alpha=0.95)
    for p, sx in ((l, -1), (r, 1)):  # the small marks at the corners
        d = -1 if c >= 0 else 1
        ribbon(ctx, ((p[0] - sx * 2, p[1] + 2 * d), (p[0] + sx * 3, p[1] - 3 * d), (p[0] + sx * 5, p[1] - 6 * d), (p[0] + sx * 6, p[1] - 9 * d)), taper(3, 1, 0.1, 0.6), alpha=0.5)
    # the lower lip: a soft shadow under it and a short line
    soft(ctx, CX, y + 32, w * 0.3, 10, SHADE, 0.38 * f["lip"] / 0.3)
    ribbon(ctx, ((CX - w * 0.18, y + 36), (CX - w * 0.06, y + 41), (CX + w * 0.06, y + 41), (CX + w * 0.18, y + 36)), taper(1, 1) if False else (lambda t: 1 + 3 * math.sin(math.pi * t)), alpha=0.45)
    soft(ctx, CX, y + 20, w * 0.22, 6, (1, 1, 1), 0.2)

def shading(ctx, f):
    for sx in (-1, 1):
        x = CX + sx * f["eyeGap"]
        soft(ctx, x - sx * 30, f["eyeY"] - f["browY"] * 0.45, f["eyeW"] * 0.6, 50, SHADE, f["socket"])   # under the brow
        soft(ctx, x + sx * 70, f["eyeY"] + 190, 80, 120, SHADE, f["cheeks"], angle=sx * -0.4)           # cheekbone
                            # between the brows

def face(f, layers=("shade", "eyes", "brows", "nose", "mouth")):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    ctx = cairo.Context(surf); ctx.set_antialias(cairo.ANTIALIAS_BEST)
    k = f.get("zoom", 1.2)  # features read small on a real head, so the whole face is drawn larger round its middle
    ctx.translate(CX, 560); ctx.scale(k, k); ctx.translate(-CX, -560)
    if "shade" in layers: shading(ctx, f)
    if "eyes" in layers:
        for sd in (-1, 1): eye(ctx, f, sd)
    if "brows" in layers:
        for sd in (-1, 1): brow(ctx, f, sd)
    if "nose" in layers: nose(ctx, f)
    if "mouth" in layers: mouth(ctx, f)
    if f.get("scar"):
        x = CX + f["scar"] * (f["eyeGap"] + 20); y = f["eyeY"]
        ribbon(ctx, ((x - 30, y - 190), (x - 10, y - 60), (x + 12, y + 70), (x + 34, y + 190)), taper(4, 4, 0.08, 0.08) if False else (lambda t: 3 + 9 * math.sin(math.pi * t) ** 0.5), color=(0.5, 0.16, 0.14), alpha=0.75)
        ribbon(ctx, ((x - 26, y - 190), (x - 6, y - 60), (x + 16, y + 70), (x + 38, y + 190)), lambda t: 1 + 2 * math.sin(math.pi * t), color=(1, 1, 1), alpha=0.3)
    return surf

def F(**kw):
    f = dict(BASE); f.update(kw); return f

TESTS = {
    "stern_red": F(irisCol=(0.6, 0.08, 0.08), open=50, tilt=4, browAng=16, browY=66, hatch=6, hatchLow=3, crease=2, nose="strong", mouthW=100, smile=-2),
    "calm_amber": F(irisCol=(0.75, 0.55, 0.15), open=46, tilt=6, browAng=8, browT=22, browY=90, lidW=11, flick=26, mouthW=96, smile=-3, nose="line", socket=0.12),
    "goofy": F(irisCol=(0.3, 0.2, 0.12), open=78, tilt=-4, iris=0.48, irisY=0.0, lidW=12, flick=14, browAng=-10, browY=110, browT=24, browArch=18, mouth="open", mouthW=110, smile=10, socket=0.06),
    "dragon": F(irisCol=(0.95, 0.65, 0.12), glow=(1.0, 0.6, 0.15), pupil="slit", open=52, tilt=16, browAng=22, browT=36, browY=68, flick=48, hatch=4, mouthW=120, smile=6, smirk=10),
    "veteran": F(irisCol=(0.3, 0.42, 0.55), open=48, tilt=8, browAng=14, browT=30, browY=72, crease=2, hatchLow=3, scar=1, nose="strong", mouthW=110, smile=-4, socket=0.22),
    "smirk_grey": F(irisCol=(0.3, 0.3, 0.32), open=60, tilt=14, browAng=20, browT=38, browY=70, mouthW=140, smile=8, smirk=8, nose="line"),
}

def preview(names, out="_preview.png"):
    from PIL import Image, ImageDraw
    skins = [(232, 186, 150), (240, 205, 175), (200, 150, 112), (150, 104, 74)]
    size = 512
    img = Image.new("RGB", (len(names) * (size + 20) + 20, size + 40), (40, 42, 48))
    for i, n in enumerate(names):
        head = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(head).rounded_rectangle((0, 0, size - 1, size - 1), radius=110, fill=skins[i % 4] + (255,))
        head.alpha_composite(Image.open(os.path.join(OUT, n + ".png")).resize((size, size), Image.LANCZOS))
        img.paste(head, (20 + i * (size + 20), 20), head)
    p = os.path.join(OUT, out); img.save(p); return p

if __name__ == "__main__":
    for n, f in TESTS.items():
        face(f).write_to_png(os.path.join(OUT, n + ".png"))
    print(preview(list(TESTS)))

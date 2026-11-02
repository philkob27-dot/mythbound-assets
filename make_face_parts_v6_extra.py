"""Extra face parts on top of v5 (Philip, 2 November: "voeg extra faces toe"). Same style, same sizes, same
layering as make_face_parts_v5.py; only new items. Output: faces/v6extra/*.png, parts_v6extra.json and a
catalog sheet. After upload the ids go into FaceImages and the items into FaceParts like the v5 set."""
import os, sys, json, math, random
import cairo
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["FACE_OUT"] = os.path.join(HERE, "v6extra")
import make_face_parts_v5 as V
import make_player_faces as P
M = V.M
A = P.A
B = P.B
S = V.S
F = V.F

OUT = os.environ["FACE_OUT"]
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ eyes

def eye_list():
    out = []
    def add(id_, rar, f, mode="tint"):
        out.append({"id": id_, "rarity": rar, "f": f, "mode": mode})
    add("c_gentle", "Common", F(open=60, tilt=-6, lidW=12, flick=12, iris=0.62, irisY=0.18, crease=1, hatch=0, seed=501))
    add("c_wide", "Common", F(open=74, tilt=2, lidW=12, flick=16, iris=0.56, irisY=0.06, crease=1, hatch=0, lowerGap=0.08, seed=502))
    add("c_calm", "Common", F(open=50, tilt=0, lidW=14, flick=18, iris=0.7, irisY=0.26, crease=1, hatch=0, seed=503))
    add("u_fox", "Uncommon", F(open=46, tilt=22, lidW=16, flick=52, flickDrop=6, iris=0.72, crease=1, hatch=0, hatchLow=2, seed=511))
    add("u_hooded", "Uncommon", F(open=42, tilt=6, lidW=17, flick=34, iris=0.76, irisY=0.3, crease=2, hatch=2, hatchLow=0, seed=512))
    add("u_bright", "Uncommon", F(open=64, tilt=10, lidW=14, flick=40, iris=0.64, irisY=0.12, crease=1, hatch=0, seed=513))
    add("r_hawk", "Rare", F(open=36, tilt=26, lidW=18, flick=56, iris=0.8, crease=2, hatch=6, hatchLow=3, pupil="dot", seed=521))
    add("r_scarred", "Rare", F(open=44, tilt=12, lidW=17, flick=40, iris=0.74, crease=2, hatch=4, hatchLow=2, seed=522), "tint")
    # Legendary, finished colours and glow (the eye colour you pick does not apply)
    add("l_storm", "Legendary", F(open=50, tilt=16, lidW=16, flick=46, irisCol=(0.78, 0.92, 1.0), glow=(0.55, 0.8, 1.0), pupil="slit", iris=0.84, hatch=4, seed=531), "fixed")
    add("l_tide", "Legendary", F(open=54, tilt=10, lidW=15, flick=40, irisCol=(0.18, 0.85, 0.74), glow=(0.2, 0.9, 0.8), pupil="round", iris=0.8, seed=532), "fixed")
    add("l_moon", "Legendary", F(open=50, tilt=12, lidW=16, flick=42, irisCol=(0.93, 0.93, 1.0), glow=(0.82, 0.84, 1.0), sclera=(0.07, 0.07, 0.13), pupil="dot", iris=0.78, seed=533), "fixed")
    add("l_gold", "Legendary", F(open=52, tilt=14, lidW=16, flick=44, irisCol=(1.0, 0.8, 0.28), glow=(1.0, 0.78, 0.3), pupil="ring", iris=0.82, hatch=3, seed=534), "fixed")
    add("l_crimson", "Legendary", F(open=46, tilt=20, lidW=18, flick=52, irisCol=(0.86, 0.1, 0.24), glow=(0.9, 0.15, 0.3), pupil="slit", iris=0.84, hatch=5, seed=535), "fixed")
    add("l_rune", "Legendary", (F(open=52, tilt=14, lidW=16, flick=44, irisCol=(0.3, 0.95, 0.55), glow=(0.3, 0.95, 0.55), pupil="ring", seed=536),
                                F(open=52, tilt=14, lidW=16, flick=44, irisCol=(1.0, 0.82, 0.3), glow=(1.0, 0.8, 0.3), pupil="ring", seed=536)), "fixed")
    return out

def draw_eyes(item):
    files = V.draw_eyes(item)
    if item["id"] == "r_scarred":
        # a pale scar straight through the right eye, on the lines layer so it keeps its own colour
        path = os.path.join(OUT, files["lines"])
        surf = cairo.ImageSurface.create_from_png(path)
        ctx = cairo.Context(surf); ctx.set_antialias(cairo.ANTIALIAS_BEST)
        ctx.translate(M.CX, V.CY); ctx.scale(V.ZOOM, V.ZOOM); ctx.translate(-M.CX, -V.CY)
        x = M.CX + M.BASE["eyeGap"] + 6; y = M.BASE["eyeY"]
        M.ribbon(ctx, ((x - 22, y - 120), (x - 6, y - 40), (x + 8, y + 40), (x + 22, y + 120)), lambda t: 3 + 7 * math.sin(math.pi * t), color=(0.55, 0.2, 0.18), alpha=0.85)
        surf.write_to_png(path)
    return files

# ------------------------------------------------------------------ brows

def brow_list():
    return [
        {"id": "c_soft", "rarity": "Common", "f": F(browT=24, browAng=-4, browArch=16, browY=92, hairs=3, seed=601)},
        {"id": "c_straight", "rarity": "Common", "f": F(browT=30, browAng=0, browArch=2, browY=84, hairs=4, seed=602)},
        {"id": "u_arch", "rarity": "Uncommon", "f": F(browT=28, browAng=10, browArch=26, browY=86, hairs=5, seed=611)},
        {"id": "u_worried", "rarity": "Uncommon", "f": F(browT=26, browAng=-14, browArch=10, browY=92, hairs=4, seed=612)},
        {"id": "r_heavy", "rarity": "Rare", "f": F(browT=50, browAng=18, browArch=4, browY=66, hairs=9, seed=621)},
    ]

# ------------------------------------------------------------------ mouths

def mouth_list():
    return [
        {"id": "c_soft", "rarity": "Common", "f": F(mouthW=90, smile=5, smirk=0, seed=701)},
        {"id": "c_flat", "rarity": "Common", "f": F(mouthW=100, smile=-1, smirk=0, seed=702)},
        {"id": "u_smug", "rarity": "Uncommon", "f": F(mouthW=110, smile=6, smirk=14, seed=711)},
        {"id": "u_frown", "rarity": "Uncommon", "f": F(mouthW=100, smile=-10, smirk=0, seed=712)},
        {"id": "u_laugh", "rarity": "Uncommon", "f": F(mouth="open", mouthW=140, smile=18, seed=713)},
        {"id": "r_fangs_low", "rarity": "Rare", "f": F(mouthW=120, smile=2, seed=721), "tusks": True},
    ]

def draw_mouths(item):
    if not item.get("tusks"):
        return V.draw_mouths(item)
    surf, ctx = V.surface()
    f = item["f"]; y = f["mouthY"]
    M.mouth(ctx, f)
    for sx in (-1, 1):
        x = M.CX + sx * 38; yy = y + 4
        ctx.move_to(x - 8, yy); ctx.line_to(x + 8, yy); ctx.line_to(x + sx * 2, yy - 20); ctx.close_path()
        ctx.set_source_rgba(0.98, 0.97, 0.94, 1); ctx.fill_preserve(); ctx.set_line_width(3); ctx.set_source_rgba(*M.INK, 0.95); ctx.stroke()
    name = f"mouths_{item['id']}.png"
    surf.write_to_png(os.path.join(OUT, name))
    return {"full": name}

# ------------------------------------------------------------------ marks (make_player_faces coordinates)

def mark_lightning(ctx):  # rare: a forked lightning scar over the left eye
    col = (0.55, 0.78, 1.0)
    x = S / 2 - B["eyeGap"] - 10; y = B["eyeY"]
    pts = [(x + 30, y - 190), (x - 10, y - 90), (x + 24, y - 60), (x - 26, y + 40), (x + 6, y + 70), (x - 40, y + 170)]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        A.ribbon(ctx, (a, A.lerp(a, b, 0.35), A.lerp(a, b, 0.7), b), A.taper(13, 10, 13, 0.1, 0.1), color=col, alpha=0.95)
    A.soft(ctx, x, y, 80, 160, col, 0.16)

def mark_sun_dots(ctx):  # uncommon: three gold dots under each eye
    for sx in (-1, 1):
        for k in range(3):
            x = S / 2 + sx * (B["eyeGap"] - 30 + k * 34); y = B["eyeY"] + 120 + (k % 2) * 10
            P.dot(ctx, x, y, 9, (0.96, 0.74, 0.24), 0.95)

def mark_ash_smear(ctx):  # common: a smear of soot over the cheek, from the forge or the camp
    rng = random.Random(91)
    for k in range(10):
        x = S / 2 + B["eyeGap"] + rng.uniform(-40, 120); y = B["eyeY"] + rng.uniform(80, 200)
        A.soft(ctx, x, y, rng.uniform(30, 60), rng.uniform(12, 24), (0.18, 0.17, 0.17), 0.25, angle=rng.uniform(-0.5, 0.2))

def mark_tide_lines(ctx):  # rare: merfolk wave paint across both cheeks
    col = (0.2, 0.6, 0.85)
    for sx in (-1, 1):
        for k in range(2):
            y = B["eyeY"] + 110 + k * 34
            x0 = S / 2 + sx * 120; x1 = S / 2 + sx * 340
            pts = [(x0, y), (x0 + (x1 - x0) * 0.33, y - 18), (x0 + (x1 - x0) * 0.66, y + 18), (x1, y)]
            A.ribbon(ctx, pts, A.taper(7, 3, 9, 0.1, 0.5), color=col, alpha=0.9)

def mark_moon_mark(ctx):  # rare: a crescent on the forehead
    x = S / 2; y = B["eyeY"] - 230; col = (0.92, 0.92, 1.0)
    ctx.save()
    ctx.arc(x, y, 50, 0, math.tau); ctx.set_source_rgba(*col, 0.95); ctx.fill()
    ctx.set_operator(cairo.OPERATOR_CLEAR); ctx.arc(x + 24, y - 12, 44, 0, math.tau); ctx.fill()
    ctx.restore()

def mark_rune_brow(ctx):  # legendary: glowing Valdren runes along the brow line
    col = (0.35, 0.95, 0.6)
    A.soft(ctx, S / 2, B["eyeY"] - 200, 260, 60, col, 0.18)
    for k, x in enumerate((-150, -50, 50, 150)):
        cx = S / 2 + x; cy = B["eyeY"] - 200
        strokes = (((cx, cy - 26), (cx, cy + 26)), ((cx, cy - 8), (cx + 16, cy - 24)) if k % 2 == 0 else ((cx, cy + 8), (cx - 16, cy - 10)))
        for a, b in strokes:
            A.ribbon(ctx, (a, A.lerp(a, b, 0.35), A.lerp(a, b, 0.7), b), A.taper(8, 8, 9, 0.1, 0.1), color=col, alpha=0.95)

def mark_storm_veins(ctx):  # legendary: blue light branching up from the jaw on one side
    rng = random.Random(33); col = (0.5, 0.8, 1.0)
    def branch(p, ang, n, w):
        if n <= 0:
            return
        L = rng.uniform(40, 70)
        q = (p[0] + math.cos(ang) * L, p[1] + math.sin(ang) * L)
        A.ribbon(ctx, (p, A.lerp(p, q, 0.35), A.lerp(p, q, 0.7), q), A.taper(w, w * 0.7, w, 0.1, 0.1), color=col, alpha=0.9)
        A.soft(ctx, q[0], q[1], 16, 16, col, 0.25)
        branch(q, ang + rng.uniform(-0.5, 0.5), n - 1, w * 0.8)
        if rng.random() < 0.45:
            branch(q, ang + rng.choice((-0.9, 0.9)), n - 2, w * 0.6)
    branch((S / 2 - 300, B["mouthY"] + 40), -1.9, 6, 8)

MARKS = [("lightning", mark_lightning, "Rare"), ("sun_dots", mark_sun_dots, "Uncommon"), ("ash_smear", mark_ash_smear, "Common"),
         ("tide_lines", mark_tide_lines, "Rare"), ("moon_mark", mark_moon_mark, "Rare"), ("rune_brow", mark_rune_brow, "Legendary"),
         ("storm_veins", mark_storm_veins, "Legendary")]

def build():
    meta = {"eyes": [], "brows": [], "noses": [], "mouths": [], "marks": []}
    for it in eye_list():
        meta["eyes"].append({"id": it["id"], "rarity": it["rarity"], "mode": it["mode"], "files": draw_eyes(it)})
    for it in brow_list():
        meta["brows"].append({"id": it["id"], "rarity": it["rarity"], "mode": "tint", "files": V.draw_brows(it)})
    for it in mouth_list():
        meta["mouths"].append({"id": it["id"], "rarity": it["rarity"], "files": draw_mouths(it)})
    for name, fn, rar in MARKS:
        meta["marks"].append({"id": name, "rarity": rar, "story": False, "files": V.draw_marks(name, fn)})
    json.dump(meta, open(os.path.join(OUT, "parts_v6extra.json"), "w"), indent=1)
    return meta

if __name__ == "__main__":
    meta = build()
    n = sum(len(v) for v in meta.values())
    print("items", n, "files", len([f for f in os.listdir(OUT) if f.endswith(".png")]))
    # a preview: each new part on a plain head, via the v5 compose
    try:
        V.OUT = OUT
        picks = []
        tiles = []
        from PIL import Image
        skin = (238, 200, 170)
        for pool in ("eyes", "brows", "mouths", "marks"):
            for it in meta[pool]:
                base = [("eyes", {"id": "c01", "mode": "tint", "files": {"white": "eyes_c01_white.png", "iris": "eyes_c01_iris.png", "lines": "eyes_c01_lines.png"}})]
                tiles.append((pool, it))
        print("tiles", len(tiles))
    except Exception as e:
        print("preview skipped", e)

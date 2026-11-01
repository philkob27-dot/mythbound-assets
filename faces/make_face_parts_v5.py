"""Modular faces in the v5 style (make_faces_mf.py; Philip, 1 November: "ja, v5 is goed"). One face is a stack of
decals on the head, every layer chosen on its own (CHARACTER_CREATION_V2.md):
  eyes     three decals for a normal eye: <id>_white, <id>_iris (a grey ramp the decal's Color3 tints to the eye
           colour you pick) and <id>_lines (inked lids, pupil, shine). Legendary eyes are one finished decal (<id>)
           with their own colours and glow, the eye colour does not apply to them
  brows    drawn white, the decal's Color3 makes them your hair colour
  noses, mouths, marks   finished decals
Every part has a rarity: Common and Uncommon are free to pick when you make a character, Rare and Legendary come
from the Mirror (rerolls), the weekly shop or the story.
Run: python3 make_face_parts_v5.py -> faces/v5parts/*.png, parts_v5.json, _catalog_v5.png, _mix_v5.png"""
import os, sys, json, math, random
import cairo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# the eye shape Philip picked (1 Nov, after "nu lijken ze echt chinees"): taller, a bit narrower, the iris
# not growing with it. make_faces_mf reads these when it is imported
os.environ.setdefault("FACE_OPEN", "1.5")
os.environ.setdefault("FACE_EYEW", "0.9")
os.environ.setdefault("FACE_IRIS", "1.15")
import make_faces_mf as M
import make_player_faces as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("FACE_OUT") or os.path.join(HERE, "v5parts")
os.makedirs(OUT, exist_ok=True)
S = M.S
# How big the face sits on the head. 1.2 with eyeGap 195 was far too wide in game (Philip, 1 Nov:
# "way too wide"): a decal fills the whole front of the head, so the eyes ran from edge to edge.
ZOOM = float(os.environ.get("FACE_ZOOM", "0.95"))  # size B was a little too small
M.BASE["eyeGap"] = float(os.environ.get("FACE_GAP", "168"))
CY = 560
WHITE = (1, 1, 1)

def surface():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    ctx = cairo.Context(surf); ctx.set_antialias(cairo.ANTIALIAS_BEST)
    ctx.translate(M.CX, CY); ctx.scale(ZOOM, ZOOM); ctx.translate(-M.CX, -CY)
    return surf, ctx

def F(**kw):
    f = dict(M.BASE); f.update(kw); return f

# ------------------------------------------------------------------------------------------- eyes

def eye_list():
    rng = random.Random(51)
    out = []
    def add(id_, rar, f, mode="tint"):
        out.append({"id": id_, "rarity": rar, "f": f, "mode": mode})
    for i in range(8):  # Common: calm, open shapes
        add(f"c{i + 1:02d}", "Common", F(open=rng.uniform(54, 68), tilt=rng.uniform(0, 8), lidW=rng.uniform(12, 15), flick=rng.uniform(16, 30),
                                       iris=rng.uniform(0.62, 0.74), irisY=rng.uniform(0.14, 0.24), crease=1, hatch=0, hatchLow=0, seed=i + 1))
    # c03 with the smaller iris (Philip picked it from the "iris klein" preview, 1 Nov)
    for it in out:
        if it["id"] == "c03":
            it["f"]["iris"] /= 1.15
    add("c_round", "Common", F(open=82, tilt=-2, lidW=11, flick=10, iris=0.48, irisY=0.0, crease=0, hatch=0, lowerGap=0.1, seed=31))
    add("c_sleepy", "Common", F(open=40, tilt=-4, lidW=16, flick=14, iris=0.8, irisY=0.34, crease=2, hatch=0, hatchLow=2, seed=32))
    for i in range(10):  # Uncommon: sharper, the anime look
        add(f"u{i + 1:02d}", "Uncommon", F(open=rng.uniform(46, 60), tilt=rng.uniform(8, 16), lidW=rng.uniform(14, 18), flick=rng.uniform(30, 46),
                                         flickDrop=rng.uniform(0, 10), iris=rng.uniform(0.66, 0.78), crease=rng.choice((1, 2)), hatch=rng.choice((0, 0, 3)),
                                         hatchLow=rng.choice((0, 2)), seed=40 + i))
    for i in range(6):  # Rare: intense, narrow, hatched
        add(f"r{i + 1:02d}", "Rare", F(open=rng.uniform(38, 48), tilt=rng.uniform(14, 24), lidW=rng.uniform(16, 20), flick=rng.uniform(44, 54),
                                     iris=rng.uniform(0.7, 0.82), crease=2, hatch=rng.choice((4, 6)), hatchLow=3, pupil=rng.choice(("round", "dot")),
                                     seed=60 + i))
    add("r_dead", "Rare", F(open=48, tilt=6, lidW=15, flick=30, iris=0.66, shine=False, hatch=2, hatchLow=3, crease=2, seed=70))
    # Legendary: finished eyes with their own colour and glow
    add("l_dragon", "Legendary", F(open=50, tilt=18, lidW=17, flick=50, irisCol=(0.95, 0.66, 0.12), glow=(1.0, 0.6, 0.15), pupil="slit", iris=0.86, hatch=4, seed=80), "fixed")
    add("l_void", "Legendary", F(open=48, tilt=16, lidW=17, flick=46, irisCol=(0.86, 0.86, 0.9), sclera=(0.05, 0.04, 0.06), pupil="ring", shine=False, hatch=3, seed=81), "fixed")
    add("l_thrall", "Legendary", F(open=48, tilt=14, lidW=16, flick=44, irisCol=(0.25, 0.95, 0.5), glow=(0.2, 0.95, 0.5), pupil="none", shine=False, hatch=3, seed=82), "fixed")
    add("l_frost", "Legendary", F(open=52, tilt=12, lidW=15, flick=40, irisCol=(0.6, 0.9, 1.0), glow=(0.5, 0.85, 1.0), pupil="ring", iris=0.8, seed=83), "fixed")
    add("l_ember", "Legendary", F(open=46, tilt=20, lidW=18, flick=52, irisCol=(0.95, 0.2, 0.12), glow=(1.0, 0.35, 0.15), pupil="slit", iris=0.84, hatch=5, seed=84), "fixed")
    add("l_odd", "Legendary", (F(open=54, tilt=12, lidW=15, flick=40, irisCol=(1.0, 0.45, 0.15), glow=(1.0, 0.45, 0.15), seed=85),
                               F(open=54, tilt=12, lidW=15, flick=40, irisCol=(0.5, 0.88, 1.0), glow=(0.5, 0.88, 1.0), seed=85)), "fixed")
    return out

def draw_eyes(item):
    files = {}
    if item["mode"] == "tint":
        for layer in ("white", "iris", "lines"):
            surf, ctx = surface()
            for sd in (-1, 1):
                M.eye(ctx, item["f"], sd, layer)
            name = f"eyes_{item['id']}_{layer}.png"
            surf.write_to_png(os.path.join(OUT, name)); files[layer] = name
    else:
        surf, ctx = surface()
        fs = item["f"] if isinstance(item["f"], tuple) else (item["f"], item["f"])
        M.eye(ctx, fs[0], -1); M.eye(ctx, fs[1], 1)
        name = f"eyes_{item['id']}.png"
        surf.write_to_png(os.path.join(OUT, name)); files["full"] = name
    return files

# ------------------------------------------------------------------------------------------- brows

def brow_list():
    rng = random.Random(61)
    out = []
    for i, rar in enumerate(["Common"] * 5 + ["Uncommon"] * 6 + ["Rare"] * 3):
        if rar == "Rare":
            f = F(browT=rng.uniform(40, 48), browAng=rng.uniform(20, 28), browArch=rng.uniform(2, 8), browY=rng.uniform(62, 70), hairs=8, seed=200 + i)
        else:
            f = F(browT=rng.uniform(22, 40), browAng=rng.uniform(-8, 20), browArch=rng.uniform(0, 20), browY=rng.uniform(66, 98), hairs=rng.randint(3, 7), seed=200 + i)
        out.append({"id": f"{rar[0].lower()}{i + 1:02d}", "rarity": rar, "f": f})
    out.append({"id": "r_slashed", "rarity": "Rare", "f": F(browT=40, browAng=22, browY=68, hairs=6, seed=230), "slash": True})
    out.append({"id": "c_thin", "rarity": "Common", "f": F(browT=16, browAng=4, browArch=14, browY=90, hairs=2, seed=231)})
    return out

def draw_brows(item):
    surf, ctx = surface()
    f = dict(item["f"]); f["browCol"] = WHITE
    for sd in (-1, 1):
        M.brow(ctx, f, sd)
    if item.get("slash"):
        ctx.save(); ctx.set_operator(cairo.OPERATOR_CLEAR)
        x = M.CX + f["eyeGap"] + 30; y = f["eyeY"] - f["browY"]
        M.ribbon(ctx, ((x - 8, y - 40), (x - 2, y - 12), (x + 4, y + 12), (x + 10, y + 40)), lambda t: 11)
        ctx.restore()
    name = f"brows_{item['id']}.png"
    surf.write_to_png(os.path.join(OUT, name))
    return {"full": name}

# ------------------------------------------------------------------------------------------- noses

def nose_list():
    rng = random.Random(71)
    out = []
    for i, rar in enumerate(["Common"] * 5 + ["Uncommon"] * 5):
        out.append({"id": f"{rar[0].lower()}{i + 1:02d}", "rarity": rar,
                    "f": F(nose=rng.choice(("line", "line", "strong")), noseW=rng.uniform(1.0, 1.5), noseSide=rng.choice((-1, 1)), noseY=rng.uniform(632, 662), seed=300 + i)})
    out.append({"id": "c_button", "rarity": "Common", "f": F(nose="none", noseW=1.0, seed=320)})
    out.append({"id": "r_bandage", "rarity": "Rare", "f": F(nose="line", noseW=1.2, seed=321), "bandage": True})
    out.append({"id": "r_broken", "rarity": "Rare", "f": F(nose="strong", noseW=1.4, noseSide=-1, seed=322), "broken": True})
    return out

def draw_noses(item):
    surf, ctx = surface()
    f = item["f"]
    M.nose(ctx, f)
    if item.get("bandage"):
        y = f["noseY"] - 70
        ctx.save(); ctx.translate(M.CX, y); ctx.rotate(-0.1)
        ctx.rectangle(-120, -20, 240, 40); ctx.set_source_rgba(0.93, 0.88, 0.8, 1); ctx.fill()
        for k in range(-2, 3):
            ctx.rectangle(k * 40 - 2, -20, 4, 40); ctx.set_source_rgba(0.72, 0.65, 0.58, 0.6); ctx.fill()
        ctx.rectangle(-120, -20, 240, 40); ctx.set_line_width(4); ctx.set_source_rgba(*M.INK, 0.8); ctx.stroke()
        ctx.restore()
    if item.get("broken"):
        top = f["eyeY"] + 10; y = f["noseY"]
        M.ribbon(ctx, ((M.CX - 4, top + 50), (M.CX + 10, top + 52), (M.CX + 22, top + 50), (M.CX + 32, top + 54)), lambda t: 3 + 3 * math.sin(math.pi * t), color=(0.45, 0.14, 0.12), alpha=0.7)
    name = f"noses_{item['id']}.png"
    surf.write_to_png(os.path.join(OUT, name))
    return {"full": name}

# ------------------------------------------------------------------------------------------- mouths

def teeth_row(ctx, y, w, n, sharp=False):
    for k in range(n):
        x = M.CX - w / 2 + (k + 0.5) * w / n
        if sharp:
            ctx.move_to(x - w / n * 0.45, y); ctx.line_to(x + w / n * 0.45, y); ctx.line_to(x, y + 14); ctx.close_path()
        else:
            ctx.rectangle(x - w / n * 0.45, y, w / n * 0.9, 12)
        ctx.set_source_rgba(0.98, 0.97, 0.93, 1); ctx.fill_preserve(); ctx.set_line_width(2.5); ctx.set_source_rgba(*M.INK, 0.9); ctx.stroke()

def mouth_list():
    rng = random.Random(81)
    out = []
    for i in range(8):
        out.append({"id": f"c{i + 1:02d}", "rarity": "Common", "f": F(mouthW=rng.uniform(80, 130), smile=rng.uniform(-6, 8), smirk=rng.choice((0, 0, rng.uniform(-6, 6))), seed=400 + i)})
    for i in range(7):
        f = F(mouthW=rng.uniform(100, 150), smile=rng.uniform(-4, 14), smirk=rng.choice((0, rng.uniform(-10, 10))), seed=410 + i)
        if rng.random() < 0.4:
            f.update(mouth="open", smile=abs(f["smile"]) + 8)
        out.append({"id": f"u{i + 1:02d}", "rarity": "Uncommon", "f": f})
    out.append({"id": "u_grin", "rarity": "Uncommon", "f": F(mouth="open", mouthW=150, smile=14, seed=420)})
    out.append({"id": "c_o", "rarity": "Common", "f": F(mouthW=40, smile=0, seed=421), "o": True})
    out.append({"id": "r_fang", "rarity": "Rare", "f": F(mouthW=120, smile=6, smirk=10, seed=430), "fang": True})
    out.append({"id": "r_gritted", "rarity": "Rare", "f": F(mouthW=120, smile=0, seed=431), "gritted": True})
    out.append({"id": "r_scarlip", "rarity": "Rare", "f": F(mouthW=110, smile=-3, seed=432), "scar": True})
    out.append({"id": "r_vampire", "rarity": "Rare", "f": F(mouthW=120, smile=4, seed=433), "vampire": True})
    out.append({"id": "l_sharp", "rarity": "Legendary", "f": F(mouthW=170, smile=18, seed=440), "sharp": True})
    out.append({"id": "l_stitched", "rarity": "Legendary", "f": F(mouthW=150, smile=0, seed=441), "stitched": True})
    return out

def draw_mouths(item):
    surf, ctx = surface()
    f = item["f"]; y = f["mouthY"]; w = f["mouthW"]
    if item.get("o"):
        ctx.save(); ctx.translate(M.CX, y + 6); ctx.scale(20, 26); ctx.arc(0, 0, 1, 0, math.tau); ctx.restore()
        ctx.set_source_rgba(0.22, 0.07, 0.07, 1); ctx.fill_preserve(); ctx.set_line_width(4); ctx.set_source_rgba(*M.INK, 1); ctx.stroke()
        M.soft(ctx, M.CX, y + 44, 30, 8, M.SHADE, 0.35)
    elif item.get("gritted"):
        ctx.rectangle(M.CX - w / 2, y - 14, w, 28); ctx.set_source_rgba(0.98, 0.97, 0.93, 1); ctx.fill_preserve()
        ctx.set_line_width(5); ctx.set_source_rgba(*M.INK, 1); ctx.stroke()
        ctx.move_to(M.CX - w / 2, y); ctx.line_to(M.CX + w / 2, y); ctx.set_line_width(3); ctx.stroke()
        for k in range(1, 6):
            x = M.CX - w / 2 + k * w / 6; ctx.move_to(x, y - 14); ctx.line_to(x, y + 14); ctx.set_line_width(2.5); ctx.stroke()
    elif item.get("sharp"):
        ctx.move_to(M.CX - w / 2, y - 12); ctx.curve_to(M.CX - 50, y + 30, M.CX + 50, y + 30, M.CX + w / 2, y - 12)
        ctx.curve_to(M.CX + 50, y + 8, M.CX - 50, y + 8, M.CX - w / 2, y - 12); ctx.close_path()
        ctx.set_source_rgba(0.98, 0.97, 0.94, 1); ctx.fill_preserve(); ctx.set_line_width(6); ctx.set_source_rgba(*M.INK, 1); ctx.stroke()
        for k in range(9):
            x = M.CX - w * 0.42 + k * w * 0.105; yy = y + 6 + 6 * math.cos((k - 4) / 4 * 1.3)
            ctx.move_to(x, yy - 12); ctx.line_to(x + 5, yy + 4); ctx.set_line_width(3); ctx.set_source_rgba(*M.INK, 0.85); ctx.stroke()
    else:
        M.mouth(ctx, f)
    if item.get("fang"):
        x = M.CX + 34; yy = y - 6
        ctx.move_to(x - 8, yy); ctx.line_to(x + 8, yy); ctx.line_to(x + 1, yy + 18); ctx.close_path()
        ctx.set_source_rgba(0.98, 0.97, 0.94, 1); ctx.fill_preserve(); ctx.set_line_width(3); ctx.set_source_rgba(*M.INK, 0.95); ctx.stroke()
    if item.get("vampire"):
        for sx in (-1, 1):
            x = M.CX + sx * 30; yy = y - 2
            ctx.move_to(x - 7, yy); ctx.line_to(x + 7, yy); ctx.line_to(x, yy + 17); ctx.close_path()
            ctx.set_source_rgba(0.98, 0.97, 0.94, 1); ctx.fill_preserve(); ctx.set_line_width(3); ctx.set_source_rgba(*M.INK, 0.95); ctx.stroke()
    if item.get("scar"):
        M.ribbon(ctx, ((M.CX - 26, y - 46), (M.CX - 22, y - 10), (M.CX - 18, y + 20), (M.CX - 14, y + 52)), lambda t: 3 + 6 * math.sin(math.pi * t), color=(0.5, 0.16, 0.14), alpha=0.7)
    if item.get("stitched"):
        for k in range(7):
            x = M.CX - 64 + k * 21
            M.ribbon(ctx, ((x - 7, y - 15), (x - 2, y - 4), (x + 2, y + 6), (x + 7, y + 15)), lambda t: 4.5, color=(0.12, 0.08, 0.08))
    name = f"mouths_{item['id']}.png"
    surf.write_to_png(os.path.join(OUT, name))
    return {"full": name}

# ------------------------------------------------------------------------------------------- marks
# The markings of the player set (make_player_faces.py), moved onto the v5 face: its eyes sit at
# (CX +-186, 455) there and at (CX +-234, 398) on a v5 face once zoomed

def draw_marks(name, fn):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    ctx = cairo.Context(surf); ctx.set_antialias(cairo.ANTIALIAS_BEST)
    gx = M.BASE["eyeGap"] * ZOOM; gy = CY + (M.BASE["eyeY"] - CY) * ZOOM
    k = gx / 186
    ctx.translate(M.CX, gy); ctx.scale(k, k); ctx.translate(-M.CX, -455)
    fn(ctx)
    file = f"marks_{name}.png"
    surf.write_to_png(os.path.join(OUT, file))
    return {"full": file}

# the marks you earn from the story: not in the Mirror's pool and never sold
STORY_MARKS = {"cracks"}

def build():
    meta = {"odds": {"Common": 50, "Uncommon": 30, "Rare": 15, "Legendary": 5}, "eyes": [], "brows": [], "noses": [], "mouths": [], "marks": []}
    for it in eye_list():
        meta["eyes"].append({"id": it["id"], "rarity": it["rarity"], "mode": it["mode"], "files": draw_eyes(it)})
    for it in brow_list():
        meta["brows"].append({"id": it["id"], "rarity": it["rarity"], "mode": "tint", "files": draw_brows(it)})
    for it in nose_list():
        meta["noses"].append({"id": it["id"], "rarity": it["rarity"], "files": draw_noses(it)})
    for it in mouth_list():
        meta["mouths"].append({"id": it["id"], "rarity": it["rarity"], "files": draw_mouths(it)})
    for name, fn, rar in P.PARTS["marks"]:
        meta["marks"].append({"id": name, "rarity": rar, "story": name in STORY_MARKS, "files": draw_marks(name, fn)})
    json.dump(meta, open(os.path.join(OUT, "parts_v5.json"), "w"), indent=1)
    return meta

# ------------------------------------------------------------------------------------------- sheets

COL = {"Common": (170, 170, 170), "Uncommon": (110, 200, 110), "Rare": (90, 150, 255), "Legendary": (255, 190, 60)}

def compose(picks, skin, size, eyeCol=(70, 110, 160), hairCol=(40, 28, 20)):
    """picks: list of (pool, item) -> RGBA head image; tints iris and brows the way the decal's Color3 would"""
    from PIL import Image, ImageDraw, ImageChops
    head = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(head).rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.2), fill=skin + (255,))
    def layer(file, tint=None):
        im = Image.open(os.path.join(OUT, file)).convert("RGBA").resize((size, size), Image.LANCZOS)
        if tint:
            r, g, b, a = im.split()
            r = r.point(lambda v: v * tint[0] // 255); g = g.point(lambda v: v * tint[1] // 255); b = b.point(lambda v: v * tint[2] // 255)
            im = Image.merge("RGBA", (r, g, b, a))
        head.alpha_composite(im)
    for pool, it in picks:
        fl = it["files"]
        if pool == "eyes" and it["mode"] == "tint":
            layer(fl["white"]); layer(fl["iris"], eyeCol); layer(fl["lines"])
        elif pool == "brows":
            layer(fl["full"], hairCol)
        else:
            layer(fl["full"])
    return head

def best(picks):
    order = ["Common", "Uncommon", "Rare", "Legendary"]
    return max((it["rarity"] for _, it in picks), key=order.index)

def catalog(meta):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    cols, cell = 12, 150
    rows = sum((len(meta[k]) + cols - 1) // cols for k in ("eyes", "brows", "noses", "mouths", "marks"))
    img = Image.new("RGB", (cols * cell, rows * (cell + 20)), (34, 36, 42)); d = ImageDraw.Draw(img); y = 0
    for pool in ("eyes", "brows", "noses", "mouths", "marks"):
        for j, it in enumerate(meta[pool]):
            x = (j % cols) * cell; yy = y + (j // cols) * (cell + 20)
            h = compose([(pool, it)], (226, 182, 146), cell - 14)
            img.paste(h, (x + 7, yy + 4), h)
            d.text((x + 8, yy + cell - 8), f"{pool[:-1]} {it['id']}", fill=COL[it["rarity"]], font=font)
        y += ((len(meta[pool]) + cols - 1) // cols) * (cell + 20)
    p = os.path.join(OUT, "_catalog_v5.png"); img.save(p); return p

def mix(meta, n=24, seed=5):
    from PIL import Image, ImageDraw, ImageFont
    rng = random.Random(seed)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    skins = [(234, 184, 146), (246, 210, 180), (196, 142, 104), (150, 100, 70), (110, 72, 50), (214, 170, 130)]
    eyes = [(70, 110, 160), (90, 60, 40), (60, 120, 70), (120, 120, 130), (150, 110, 50), (40, 30, 30)]
    hairs = [(40, 28, 20), (90, 50, 25), (200, 160, 90), (150, 40, 30), (30, 30, 34), (220, 220, 225)]
    cols, size = 6, 280
    img = Image.new("RGB", (cols * (size + 16) + 16, ((n + cols - 1) // cols) * (size + 40) + 16), (30, 32, 38)); d = ImageDraw.Draw(img)
    order = ["Common", "Uncommon", "Rare", "Legendary"]
    def pick(pool, rng):
        # the mix shows what players will look like: mostly free picks, now and then a reroll result
        tier = rng.choices(order, weights=[45, 35, 15, 5])[0]
        pool_items = [it for it in meta[pool] if it["rarity"] == tier and not it.get("story")] or meta[pool]
        return rng.choice(pool_items)
    for i in range(n):
        picks = [("eyes", pick("eyes", rng)), ("brows", pick("brows", rng)), ("noses", pick("noses", rng)), ("mouths", pick("mouths", rng))]
        if rng.random() < 0.45:
            picks.append(("marks", pick("marks", rng)))
        h = compose(picks, rng.choice(skins), size, rng.choice(eyes), rng.choice(hairs))
        x = 16 + (i % cols) * (size + 16); y = 16 + (i // cols) * (size + 40)
        img.paste(h, (x, y), h)
        d.text((x, y + size + 6), best(picks).upper(), fill=COL[best(picks)], font=font)
    p = os.path.join(OUT, "_mix_v5.png"); img.save(p); return p

if __name__ == "__main__":
    meta = build()
    print({k: len(v) for k, v in meta.items() if isinstance(v, list)})
    print(catalog(meta)); print(mix(meta))

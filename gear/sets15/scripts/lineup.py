# Lineup of all finished armor sets (Legendary, on the blocky R15 dummy), two rows.
import os, sys, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *
from bpy_extras.object_utils import world_to_camera_view

IDS = ["envoy", "kelpfarmer", "stormcaller", "bogwitch", "watcherstone", "climber", "racer", "ledgerwarden",
       "songkeeper", "gatekeeper", "ashknight", "castaway", "lumen", "skylancer", "ascendant"]
ids = [i for i in IDS if os.path.exists(os.path.join(HERE, f"set_{i}.py"))]
rows = [ids[:8], ids[8:]]
SP = 4.5
from PIL import Image, ImageDraw, ImageFont

imgs = []
for r, row in enumerate(rows):
    if not row:
        continue
    clear_scene()
    gear = new_collection("Gear")
    body = new_collection("Mannequin")
    names = []
    for k, sid in enumerate(row):
        mod = importlib.import_module(f"set_{sid}")
        K = Kit(mod.CFG)
        mod.build(K)
        off = ((k - (len(row) - 1) / 2) * SP, 0, 0)
        K.objects(gear, offset=off, name_prefix=f"{sid}_")
        mannequin(body, offset=off)
        names.append((mod.CFG["name"], off))
    cam = setup_render(res=(3000, 760), samples=24)
    aim_camera(cam, (0, 0, 3.0), -22, pitch=6, ortho=8 * SP + 1.0)
    p = os.path.join(REVIEW, "_tmp", f"lineup_row{r}.png")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    render_to(p)
    sc = bpy.context.scene
    labels = []
    for n, off in names:
        v = world_to_camera_view(sc, cam, Vector(off) + Vector((0, 0, -0.2)))
        labels.append((n, v.x * sc.render.resolution_x))
    imgs.append((p, labels))

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
ims = [Image.open(p).convert("RGB") for p, _ in imgs]
W = max(i.size[0] for i in ims)
H = sum(i.size[1] + 40 for i in ims) + 60
out = Image.new("RGB", (W, H), (24, 26, 30))
d = ImageDraw.Draw(out)
d.text((20, 14), "Mythbound: 15 nieuwe armorsets (Legendary)", fill=(240, 230, 200), font=title)
y = 60
for im, (_, labels) in zip(ims, imgs):
    out.paste(im, (0, y))
    for n, x in labels:
        tw = d.textlength(n, font=font)
        d.text((x - tw / 2, y + im.size[1] + 6), n, fill=(225, 225, 225), font=font)
    y += im.size[1] + 40
op = os.path.join(REVIEW, "lineup_sets15.png")
out.save(op)
print("lineup", op)

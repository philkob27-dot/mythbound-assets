# Eyrie Ascendant (set 15): Wild, reverent (symmetric), gold / bone, emblem a stair of bones up to an eye.
# Bone plates over pilgrim wool, a feathered mantle, gold claws on the boots, an eye amulet.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="ascendant", model="Ascendant", name="Eyrie Ascendant",
    palette={
        "Wool": ((172, 148, 114), "cloth"),
        "Bone": ((236, 226, 200), "bone"),
        "Gold": ((224, 182, 86), "metal"),
        "Feather": ((112, 82, 60), "cloth"),
        "Tip": ((242, 238, 228), "cloth"),
        "Sash": ((150, 62, 44), "cloth"),
        "Leather": ((88, 64, 48), "leather"),
    },
    glow=(255, 226, 150),
)


def feather(K, c, L, rar, rot=(0, 0, 0), w=0.2, sway=True, tip=True):
    pts = [(0, -0.5), (0.45, -0.25), (0.5, 0.15), (0.2, 0.42), (0, 0.5), (-0.25, 0.4), (-0.42, 0.1), (-0.35, -0.3)]
    K.prism("Feather", c, [(x * w, z * L) for x, z in pts], 0.04, rar, rot=rot, sway=sway)
    if tip:
        p = Vector(c) + (rot_matrix(rot) @ Vector((0, 0, L * 0.38))).to_3d()
        K.prism("Tip", tuple(p), [(x * w * 1.05, z * L * 0.28) for x, z in pts], 0.045, rar, rot=rot, sway=sway)


def eye(K, c, s, rar, facing=-1, glow_rar=None):
    pts = [(-0.26, 0), (-0.12, 0.12), (0.12, 0.12), (0.26, 0), (0.12, -0.12), (-0.12, -0.12)]
    K.prism("Gold", c, [(x * s, z * s) for x, z in pts], 0.05, rar)
    K.prism("Bone", (c[0], c[1] + facing * 0.025, c[2]), [(x * s * 0.8, z * s * 0.7) for x, z in pts], 0.03, rar)
    K.disc("Gold", (c[0], c[1] + facing * 0.04, c[2]), 0.06 * s, 0.03, rar, n=10)
    if glow_rar:
        K.disc("Glow", (c[0], c[1] + facing * 0.055, c[2]), 0.04 * s, 0.02, glow_rar, n=8)


def stair(K, c, s, rar, steps=4, facing=-1, glow_rar=None):
    """Emblem: a stair of bones rising to an eye."""
    x, y, z = c
    for i in range(steps):
        K.box("Bone", (x + (i - steps / 2 + 0.5) * 0.1 * s, y, z - 0.25 * s + i * 0.09 * s), (0.11 * s, 0.05, 0.05 * s), rar, bevel=0.005)
    eye(K, (x + 0.12 * s, y + facing * 0.01, z + 0.22 * s), 0.6 * s, rar, facing=facing, glow_rar=glow_rar)


def build(K):
    # ---------------- head: pilgrim hood, bone circlet with the stair to an eye, feather ruff
    K.piece("Helm")
    K.hood("Wool", "Common", out=0.1, peak=0.25, back=0.2, drape=0.45, open_w=0.86, trim="Bone")
    K.box("Bone", (0, -0.03, 0.42), (1.42, 1.42, 0.14), "Common", bevel=0.05)
    for i in range(5):  # stair of bones rising at the brow
        K.box("Bone", (0, -0.72, 0.5 + i * 0.1), (0.5 - i * 0.08, 0.08, 0.08), "Common" if i < 3 else "Uncommon", bevel=0.02)
    eye(K, (0, -0.74, 1.08), 0.9, "Rare", glow_rar="Epic")
    K.box("Gold", (0, -0.72, 0.42), (0.6, 0.06, 0.08), "Uncommon", bevel=0.01)
    for sx in (1, -1):  # feather ruff along the hood edge
        for i in range(3):
            feather(K, (sx * (0.55 + i * 0.04), -0.55, 0.2 - i * 0.3), 0.45, "Uncommon" if i == 0 else "Rare", rot=(0, sx * (30 + i * 15), 0), sway=False)
    for i in range(7):  # Legendary: tall feather fan behind the head
        a = -54 + i * 18
        feather(K, (math.sin(math.radians(a)) * 0.5, 0.7, 0.75 + math.cos(math.radians(a)) * 0.4), 1.0, "Legendary", rot=(-10, a, 0), w=0.24)

    # ---------------- chest: wool robe, bone stair plates, eye amulet, feathered mantle
    K.piece("Chest")
    K.shell("Wool", 0.06, "Common", bevel=0.06)
    for i in range(4):  # bone plates stacked like a stair
        w = 1.2 + i * 0.18
        K.box("Bone", (0, -0.6, 0.55 - i * 0.32), (w, 0.1, 0.24), "Common", bevel=0.05)
        K.box("Gold", (0, -0.655, 0.55 - i * 0.32 + 0.1), (w + 0.02, 0.02, 0.03), "Uncommon", bevel=0.0)
    K.box("Sash", (0, -0.56, -0.05), (0.3, 0.06, 1.7), "Common", bevel=0.02)
    K.beads("Gold", (-0.45, -0.68, 0.8), (0.45, -0.68, 0.8), 9, 0.04, "Rare", sag=0.55)
    K.disc("Gold", (0, -0.74, 0.18), 0.2, 0.06, "Rare", n=14, rot=(90, 0, 0))
    eye(K, (0, -0.78, 0.18), 0.7, "Rare", glow_rar="Epic")
    # feather mantle: collar of feathers and a feathered cape
    for i in range(11):
        a = math.radians(-100 + i * 20)
        feather(K, (math.sin(a) * 1.08, -math.cos(a) * 0.7, 0.98), 0.7, "Common" if i % 2 == 0 else "Uncommon",
                rot=(-math.cos(a) * 40, math.sin(a) * 40, 0), w=0.26, sway=False)
    K.cape("Feather", (0, 0.62, 0.82), 1.9, 2.6, "Common", flare=0.45, widen=0.25, curve=0.2, tatter=0.35, teeth=6, thick=0.06, nx=12)
    for row in range(3):
        for i in range(5 + row):
            x = (i - (4 + row) / 2) * 0.36
            feather(K, (x, 0.82 + row * 0.12, 0.25 - row * 0.62), 0.8, ("Uncommon", "Rare", "Epic")[row], rot=(-12 - row * 5, 0, 0), w=0.3)
    stair(K, (0, 0.82, 0.6), 1.0, "Rare", facing=1, glow_rar="Legendary")

    # ---------------- belt: leather belt, gold buckle with the emblem, long wool robe
    K.piece("Belt")
    K.shell("Leather", 0.08, "Common", hz=0.3, bevel=0.04)
    K.box("Gold", (0, -0.6, 0), (0.46, 0.06, 0.3), "Common", bevel=0.03)
    stair(K, (0, -0.64, 0.0), 0.55, "Rare")
    K.panel("Wool", (0, -0.56, -0.12), 1.0, 1.45, "Common", flare=0.2, widen=0.12, thick=0.06)
    K.panel("Wool", (0, 0.56, -0.12), 1.7, 1.45, "Common", flare=0.25, widen=0.1, thick=0.06, face=1)
    K.panel("Sash", (0, -0.6, -0.12), 0.3, 1.5, "Common", flare=0.2, thick=0.05, nx=1)
    K.panel("Bone", (0, -0.6, -1.45), 1.1, 0.08, "Uncommon", flare=0.0, thick=0.05, nx=1, ny=1)
    for sx in (1, -1):
        K.side_panel("Wool", (sx * 1.02, 0, -0.12), 0.9, 1.35, sx, "Common", flare=0.18)
        K.box("Bone", (sx * 0.62, -0.62, -0.35), (0.42, 0.1, 0.36), "Uncommon", bevel=0.04, sway=True)

    # ---------------- shoulders: layered bone plates with a feather fringe (symmetric)
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Wool", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        K.taper("Bone", (0.08 * s, 0, 0.58), (1.3, 1.28), (0.98, 1.02), 0.32, "Common", bevel=0.07)
        K.taper("Bone", (0.16 * s, 0, 0.32), (1.34, 1.32), (1.3, 1.3), 0.2, "Common", bevel=0.05)
        K.box("Gold", (0.16 * s, 0, 0.21), (1.36, 1.34, 0.05), "Uncommon", bevel=0.02)
        for i in range(4):
            feather(K, (0.6 * s, -0.45 + i * 0.3, 0.05), 0.55, "Rare" if i % 2 else "Uncommon", rot=(0, s * 8, 0), w=0.24)
        eye(K, (0.16 * s, -0.69, 0.32), 0.5, "Epic")
        K.cyl("Gold", (0.1 * s, 0, 0.85), 0.05, 0.3, "Legendary", r2=0.0, n=6)

    # ---------------- arms: wool wraps, bone plates, gold talon gloves
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Wool", 0.07, "Common", hz=0.95, bevel=0.05)
        K.box("Bone", (0, -0.6, -0.05), (0.6, 0.1, 0.7), "Common", bevel=0.05)
        K.band("Leather", 0.35, 0.08, 0.1, "Common")
        K.band("Gold", -0.45, 0.05, 0.12, "Uncommon")
        K.piece("Glove" + side)
        K.box("Leather", (0, 0, 0.0), (1.06, 1.1, 0.36), "Common", bevel=0.05)
        for i in range(3):
            K.cyl("Gold", (-0.28 + i * 0.28, -0.52, -0.24), 0.05, 0.2, "Rare", rot=(200, 0, 0), r2=0.0, n=6)

    # ---------------- legs: wool trousers, bone greaves, boots with gold claws
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Wool", 0.05, "Common", hz=1.15, dz=-0.08, bevel=0.05)
        K.piece("Greave" + side)
        K.shell("Leather", 0.07, "Common", hz=1.0, dz=-0.12, bevel=0.06)
        K.box("Bone", (0, -0.58, 0.05), (0.62, 0.12, 0.8), "Common", bevel=0.05)
        stair(K, (0, -0.66, 0.1), 0.6, "Rare")
        K.band("Gold", 0.4, 0.05, 0.1, "Uncommon")
        K.piece("Boot" + side)
        K.box("Leather", (0, -0.06, 0.02), (1.1, 1.24, 0.38), "Common", bevel=0.06)
        for i in range(3):
            K.cyl("Gold", (-0.34 + i * 0.34, -0.78, -0.05), 0.1, 0.42, "Common" if i == 1 else "Uncommon", rot=(110, 0, 0), r2=0.0, n=6)
        K.cyl("Gold", (0, 0.7, -0.05), 0.06, 0.25, "Rare", rot=(-110, 0, 0), r2=0.0, n=6)


if __name__ == "__main__":
    run(CFG, build)

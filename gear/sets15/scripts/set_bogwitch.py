# Bogwitch (set 4): Wild, moss / bone, emblem a goat skull with reeds.
# A goat skull headdress with reed braids, a shawl full of herb pouches, a cauldron at the hip, bone chains.
# Asymmetric: cauldron on the right hip, bone pauldron on the left, reed bundle on the right shoulder.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="bogwitch", model="Bogwitch", name="Bogwitch",
    palette={
        "Dress": ((72, 60, 48), "cloth"),
        "Moss": ((92, 118, 58), "cloth"),
        "Bone": ((226, 214, 186), "bone"),
        "Reed": ((172, 152, 92), "plant"),
        "Leather": ((100, 72, 50), "leather"),
        "Pouch": ((146, 120, 82), "cloth"),
        "Iron": ((104, 106, 108), "metal"),
    },
    glow=(170, 255, 110),
)


def goat_skull(K, c, s, rar, horn_rar=None, glow_rar=None, facing=-1, depth_scale=1.0):
    x, y, z = c
    K.box("Bone", (x, y, z), (0.62 * s, 0.6 * s * depth_scale, 0.5 * s), rar, bevel=0.06 * s)
    K.taper("Bone", (x, y + facing * 0.32 * s * depth_scale, z - 0.12 * s), (0.34 * s, 0.4 * s), (0.42 * s, 0.4 * s), 0.36 * s, rar,
            rot=(facing * 0, 0, 0), bevel=0.04 * s)
    for sx in (1, -1):
        K.box("Iron", (x + sx * 0.15 * s, y + facing * 0.3 * s * depth_scale, z + 0.02 * s), (0.14 * s, 0.04, 0.12 * s), rar, bevel=0.01)
        if glow_rar:
            K.box("Glow", (x + sx * 0.15 * s, y + facing * 0.32 * s * depth_scale, z + 0.02 * s), (0.08 * s, 0.03, 0.06 * s), glow_rar, bevel=0.0)
        hr = horn_rar or rar
        K.torus("Bone", (x + sx * 0.38 * s, y + 0.05 * s, z + 0.12 * s), 0.2 * s, 0.07 * s, hr, rot=(0, 0, 90), n=10, m=5, arc=0.75,
                scale=(1, 1, 1))
        K.cyl("Bone", (x + sx * 0.4 * s, y + 0.06 * s, z - 0.12 * s), 0.065 * s, 0.22 * s, hr, rot=(0, sx * 160, 0), r2=0.0, n=6)


def emblem(K, c, s, rar):
    for i, a in enumerate((-25, 0, 25)):
        K.cyl("Reed", (c[0] + math.sin(math.radians(a)) * 0.15 * s, c[1] + 0.03, c[2] + 0.1 * s), 0.025 * s, 0.6 * s, rar, rot=(0, a, 0), n=5)
    goat_skull(K, c, 0.42 * s, rar, facing=-1, depth_scale=0.4)


def pouch(K, c, s, rar, col="Pouch"):
    K.box(col, c, (0.2 * s, 0.14 * s, 0.24 * s), rar, bevel=0.05 * s, sway=True)
    K.cyl("Reed", (c[0], c[1], c[2] + 0.14 * s), 0.05 * s, 0.06 * s, rar, n=6, sway=True)
    K.sphere(col, (c[0], c[1], c[2] + 0.2 * s), 0.06 * s, rar, n=6, rings=4, sway=True)


def build(K):
    # ---------------- head: goat skull headdress over a ragged hood, reed braids
    K.piece("Helm")
    K.hood("Dress", "Common", out=0.1, peak=0.0, drape=0.4, trim="Moss")
    goat_skull(K, (0, -0.3, 0.86), 1.5, "Common", horn_rar="Common", glow_rar="Epic")
    for sx in (1, -1):  # reed braids hanging at the sides (hanging family: braids, bones, pouches)
        K.rope("Reed", [(sx * 0.78, -0.3, 0.45), (sx * 0.82, -0.36, -0.1), (sx * 0.84, -0.34, -0.7)], 0.06, "Uncommon", sway=True)
        K.sphere("Bone", (sx * 0.84, -0.34, -0.8), 0.08, "Rare", n=6, rings=4, sway=True)
    K.box("Moss", (0.3, 0.1, 1.15), (0.3, 0.4, 0.12), "Rare", bevel=0.05)
    for i in range(5):  # reeds sticking up behind the skull
        a = -30 + i * 15
        K.cyl("Reed", (math.sin(math.radians(a)) * 0.4, 0.35, 1.25), 0.025, 0.8, "Rare", rot=(-15, a, 0), n=5)
    for sx in (1, -1):
        K.torus("Bone", (sx * 0.75, -0.1, 1.15), 0.3, 0.08, "Legendary", rot=(0, 0, 90), n=12, m=5, arc=0.65)
        K.cyl("Bone", (sx * 0.98, -0.08, 0.9), 0.08, 0.35, "Legendary", rot=(0, sx * 150, 0), r2=0.0, n=6)
    K.sphere("Glow", (0, -0.85, 1.4), 0.08, "Legendary", n=8, rings=5)

    # ---------------- chest: dress, moss shawl with herb pouches, bone chain, ragged back shawl
    K.piece("Chest")
    K.shell("Dress", 0.06, "Common", bevel=0.06)
    K.taper("Moss", (0, 0.0, 0.72), (2.25, 1.32), (1.55, 1.2), 0.42, "Common", bevel=0.05)
    K.prism("Moss", (0, -0.6, 0.15), [(-0.95, 0.4), (0.95, 0.4), (0.0, -0.75)], 0.08, "Common")
    K.prism("Bone", (0, -0.645, 0.15), [(-0.2, -0.45), (0.2, -0.45), (0.0, -0.78)], 0.04, "Uncommon")
    for i, (x, z) in enumerate(((-0.55, 0.3), (0.5, 0.25), (-0.25, -0.1), (0.3, -0.15))):
        pouch(K, (x, -0.72, z), 1.0, "Uncommon" if i < 2 else "Rare", col=["Pouch", "Leather", "Pouch", "Leather"][i])
    K.beads("Bone", (-0.75, -0.66, 0.62), (0.75, -0.66, 0.62), 9, 0.055, "Rare", sag=0.55)
    K.box("Bone", (0, -0.74, 0.07), (0.12, 0.06, 0.3), "Rare", bevel=0.02, sway=True)
    K.box("Glow", (-0.25, -0.82, -0.1), (0.1, 0.02, 0.1), "Epic", bevel=0.0, sway=True)
    K.cape("Moss", (0, 0.62, 0.78), 1.95, 2.0, "Common", flare=0.35, widen=0.25, curve=0.2, tatter=0.45, teeth=6, thick=0.05, nx=12)
    K.cape("Dress", (0, 0.66, 0.8), 1.4, 2.7, "Rare", flare=0.45, widen=0.2, curve=0.1, tatter=0.5, teeth=5, thick=0.04, nx=10)
    goat_skull(K, (0, 0.95, 0.2), 0.6, "Legendary", glow_rar="Legendary", facing=1)

    # ---------------- belt: rope belt, skull buckle, ragged skirt, cauldron on the right hip, bone chain left
    K.piece("Belt")
    K.shell("Leather", 0.08, "Common", hz=0.3, bevel=0.04)
    K.band("Reed", 0.0, 0.08, 0.13, "Uncommon", bevel=0.03)
    emblem(K, (0.0, -0.64, -0.02), 1.0, "Rare")
    K.panel("Dress", (0, -0.57, -0.1), 1.9, 1.45, "Common", flare=0.2, widen=0.15, thick=0.05, tatter=0.35, teeth=5, nx=8)
    K.panel("Dress", (0, 0.57, -0.1), 1.9, 1.45, "Common", flare=0.25, widen=0.15, thick=0.05, face=1, tatter=0.35, teeth=5, nx=8)
    for sx in (1, -1):
        K.side_panel("Dress", (sx * 1.02, 0, -0.1), 0.95, 1.35, sx, "Common", flare=0.18, tatter=0.3)
    K.panel("Moss", (0.25, -0.62, -0.12), 0.8, 0.9, "Uncommon", flare=0.15, thick=0.04, tatter=0.25, teeth=3)
    # cauldron
    K.cyl("Iron", (-1.2, -0.15, -0.45), 0.32, 0.42, "Common", n=12, r2=0.36, sway=True)
    K.torus("Iron", (-1.2, -0.15, -0.23), 0.36, 0.05, "Common", n=12, m=5, sway=True)
    K.cyl("Moss", (-1.2, -0.15, -0.26), 0.33, 0.02, "Uncommon", n=12, sway=True)
    K.cyl("Glow", (-1.2, -0.15, -0.25), 0.3, 0.02, "Epic", n=12, sway=True)
    K.torus("Iron", (-1.2, -0.15, -0.15), 0.3, 0.025, "Common", rot=(90, 0, 0), n=10, m=4, arc=0.5, sway=True)
    for i in range(3):
        K.sphere("Glow", (-1.15 + 0.08 * i, -0.2 + 0.07 * i, -0.08 + 0.12 * i), 0.05 - 0.01 * i, "Legendary", n=6, rings=4, sway=True)
    K.beads("Bone", (0.9, -0.55, 0.0), (1.05, 0.0, -0.1), 6, 0.05, "Rare", sag=0.45)
    K.box("Bone", (1.02, -0.2, -0.55), (0.07, 0.25, 0.08), "Rare", bevel=0.02, sway=True)

    # ---------------- shoulders: bone jaw pauldron (left), moss and reed bundle (right)
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Dress", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        if s == 1:
            K.taper("Leather", (0.06, 0, 0.48), (1.22, 1.2), (1.0, 1.04), 0.32, "Common", bevel=0.05)
            for i in range(4):  # ribs of a jaw
                K.torus("Bone", (0.08, -0.36 + i * 0.24, 0.5), 0.56, 0.06, "Uncommon" if i % 2 == 0 else "Rare", rot=(90, 0, 0), n=12, m=5, arc=0.5)
            K.cyl("Bone", (0.72, -0.15, 0.45), 0.06, 0.3, "Rare", rot=(0, 140, 0), r2=0.0, n=6)
            K.cyl("Bone", (0.72, 0.15, 0.45), 0.06, 0.3, "Rare", rot=(0, 140, 0), r2=0.0, n=6)
        else:
            K.taper("Moss", (-0.06, 0, 0.48), (1.3, 1.26), (1.0, 1.06), 0.34, "Common", bevel=0.05)
            for i in range(6):
                a = -40 + i * 16
                K.cyl("Reed", (-0.3 - i * 0.04, -0.2 + i * 0.07, 0.95), 0.03, 0.7, "Rare", rot=(0, a, 0), n=5)
            K.torus("Reed", (-0.35, 0.0, 0.7), 0.15, 0.05, "Rare", n=10, m=4)
            pouch(K, (-0.62, -0.15, 0.1), 1.0, "Rare", col="Leather")

    # ---------------- arms: cloth wraps, bone bangles, leather gloves
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Dress", 0.06, "Common", hz=0.95, bevel=0.05)
        K.band("Moss", -0.3, 0.3, 0.1, "Common", bevel=0.05)
        K.band("Bone", 0.05 if s == 1 else -0.0, 0.07, 0.12, "Uncommon")
        if s == 1:
            K.band("Bone", 0.2, 0.07, 0.12, "Rare")
        K.box("Glow", (0.0, -0.62, -0.3), (0.3, 0.02, 0.04), "Epic", bevel=0.0)
        K.piece("Glove" + side)
        K.box("Leather", (0, 0, 0.0), (1.06, 1.1, 0.36), "Common", bevel=0.05)
        for i in range(3):
            K.cyl("Bone", (-0.25 + i * 0.25, -0.58, -0.18), 0.04, 0.16, "Rare", rot=(180, 0, 0), r2=0.0, n=5)

    # ---------------- legs: ragged leggings, reed bound wraps, soft boots
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Dress", 0.05, "Common", hz=1.15, dz=-0.08, bevel=0.05)
        K.piece("Greave" + side)
        K.shell("Leather", 0.06, "Common", hz=1.0, dz=-0.12, bevel=0.06)
        for i in range(3):
            K.band("Reed", 0.2 - i * 0.3, 0.05, 0.1, "Uncommon")
        if s == -1:
            K.beads("Bone", (-0.45, -0.5, 0.35), (0.45, -0.5, 0.35), 5, 0.05, "Rare", sag=0.2)
        K.piece("Boot" + side)
        K.box("Leather", (0, -0.05, 0.02), (1.08, 1.2, 0.36), "Common", bevel=0.07)
        K.box("Moss", (0, -0.05, 0.18), (1.12, 1.24, 0.08), "Uncommon", bevel=0.03)


if __name__ == "__main__":
    run(CFG, build)

# Lumen Warden (set 13): Sacred, symmetric (solemn), bone white / gold, emblem the Valdren eye in a ring.
# White and gold, a smooth mask without a mouth, a gold ring behind the head, green rune lines, long robes.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="lumen", model="Lumen", name="Lumen Warden",
    palette={
        "Robe": ((238, 234, 224), "cloth"),
        "Ivory": ((226, 216, 194), "bone"),
        "Gold": ((224, 182, 92), "metal"),
        "Stole": ((44, 108, 80), "cloth"),
        "Rune": ((84, 204, 126), "paint"),
    },
    glow=(120, 255, 170),
)


def valdren_eye(K, c, s, rar, facing=-1, glow_rar=None, ring=True):
    x, y, z = c
    if ring:
        K.torus("Gold", c, 0.3 * s, 0.035 * s, rar, rot=(90, 0, 0), n=16, m=4)
    pts = [(-0.24, 0), (-0.12, 0.1), (0.12, 0.1), (0.24, 0), (0.12, -0.1), (-0.12, -0.1)]
    K.prism("Gold", (x, y, z), [(px * s, pz * s) for px, pz in pts], 0.04, rar)
    K.prism("Ivory", (x, y + facing * 0.02, z), [(px * s * 0.8, pz * s * 0.7) for px, pz in pts], 0.03, rar)
    K.disc("Rune", (x, y + facing * 0.035, z), 0.06 * s, 0.03, rar, n=10)
    if glow_rar:
        K.disc("Glow", (x, y + facing * 0.05, z), 0.035 * s, 0.02, glow_rar, n=8)


def rune_line(K, p1, p2, rar, w=0.035, glow_rar=None, out=(0, -0.01, 0)):
    K.strap("Rune", p1, p2, w, 0.02, rar, bevel=0.0)
    if glow_rar:
        q1 = tuple(a + b for a, b in zip(p1, out))
        q2 = tuple(a + b for a, b in zip(p2, out))
        K.strap("Glow", q1, q2, w * 0.5, 0.015, glow_rar, bevel=0.0)


def build(K):
    # ---------------- head: white cowl, smooth mask without a mouth, gold halo ring behind the head
    K.piece("Helm")
    K.hood("Robe", "Common", out=0.1, peak=0.0, drape=0.45, open_w=0.9, trim="Gold")
    K.box("Ivory", (0, -0.62, 0.0), (0.86, 0.08, 1.0), "Common", bevel=0.12)             # smooth mask
    for sx in (1, -1):
        K.box("Gold", (sx * 0.2, -0.665, 0.1), (0.2, 0.02, 0.05), "Common", bevel=0.01)
        K.box("Glow", (sx * 0.2, -0.675, 0.1), (0.14, 0.02, 0.03), "Epic", bevel=0.0)
    rune_line(K, (0, -0.665, 0.42), (0, -0.665, 0.22), "Uncommon", glow_rar="Epic")
    K.torus("Gold", (0, 0.72, 0.35), 0.95, 0.06, "Common", rot=(90, 0, 0), n=28, m=5)    # halo
    K.cyl("Gold", (0, 0.68, -0.25), 0.07, 0.4, "Common", rot=(0, 0, 0), n=8)
    for i in range(12):  # rays
        a = 2 * math.pi * i / 12
        L = 0.28 if i % 2 == 0 else 0.18
        K.strap("Gold", (math.cos(a) * 1.0, 0.72, 0.35 + math.sin(a) * 1.0), (math.cos(a) * (1.0 + L), 0.72, 0.35 + math.sin(a) * (1.0 + L)),
                0.06, 0.04, "Rare" if i % 2 == 0 else "Uncommon", bevel=0.01)
    K.torus("Glow", (0, 0.74, 0.35), 0.86, 0.025, "Epic", rot=(90, 0, 0), n=28, m=4)
    K.torus("Gold", (0, 0.8, 0.35), 0.72, 0.035, "Legendary", rot=(90, 0, 0), n=24, m=4)
    valdren_eye(K, (0, 0.76, 1.42), 0.9, "Legendary", facing=-1, glow_rar="Legendary")

    # ---------------- chest: white robe, ivory breastplate, emblem, green stole, long white mantle
    K.piece("Chest")
    K.shell("Robe", 0.06, "Common", bevel=0.06)
    K.taper("Ivory", (0, -0.03, 0.42), (1.6, 1.18), (1.9, 1.24), 0.8, "Common", bevel=0.08)
    K.box("Gold", (0, -0.03, 0.83), (1.94, 1.28, 0.06), "Common", bevel=0.02)
    K.box("Gold", (0, -0.03, 0.03), (1.62, 1.2, 0.05), "Uncommon", bevel=0.02)
    K.taper("Gold", (0, 0.0, 0.95), (1.4, 1.15), (1.24, 1.06), 0.18, "Common", bevel=0.04)
    valdren_eye(K, (0, -0.66, 0.42), 1.1, "Rare", glow_rar="Epic")
    for sx in (1, -1):
        K.box("Stole", (sx * 0.6, -0.56, -0.05), (0.36, 0.08, 1.75), "Common", bevel=0.03)
        K.box("Stole", (sx * 0.6, 0.0, 0.86), (0.38, 1.2, 0.1), "Common", bevel=0.03)
        rune_line(K, (sx * 0.6, -0.61, 0.6), (sx * 0.6, -0.61, -0.8), "Uncommon", glow_rar="Epic")
        K.box("Gold", (sx * 0.6, -0.61, -0.8), (0.36, 0.03, 0.05), "Uncommon", bevel=0.01)
    K.cape("Gold", (0, 0.6, 0.84), 1.9, 3.2, "Uncommon", flare=0.42, widen=0.12, curve=0.18, thick=0.04, nx=8)
    K.cape("Robe", (0, 0.62, 0.86), 1.9, 3.1, "Common", flare=0.42, widen=0.12, curve=0.18, thick=0.06, nx=8)
    valdren_eye(K, (0, 0.8, 0.3), 1.2, "Rare", facing=1, glow_rar="Legendary")
    for sx in (1, -1):
        rune_line(K, (sx * 0.5, 0.86, 0.0), (sx * 0.62, 1.15, -1.6), "Rare", glow_rar="Legendary", out=(0, 0.01, 0))

    # ---------------- belt: gold belt with the eye, long robe panels with gold hems and rune lines
    K.piece("Belt")
    K.shell("Gold", 0.08, "Common", hz=0.32, bevel=0.04)
    valdren_eye(K, (0, -0.64, 0.0), 0.6, "Rare", ring=True)
    K.panel("Robe", (0, -0.56, -0.12), 1.0, 1.55, "Common", flare=0.2, widen=0.12, thick=0.06)
    K.panel("Robe", (0, 0.56, -0.12), 1.7, 1.6, "Common", flare=0.25, widen=0.1, thick=0.06, face=1)
    K.panel("Gold", (0, -0.6, -1.55), 1.12, 0.08, "Uncommon", flare=0.0, thick=0.05, nx=1, ny=1)
    for sx in (1, -1):
        K.side_panel("Robe", (sx * 1.02, 0, -0.12), 0.9, 1.45, sx, "Common", flare=0.2)
        K.panel("Stole", (sx * 0.6, -0.62, -0.1), 0.36, 1.5, "Common", flare=0.2, thick=0.05, nx=1)
        K.panel("Gold", (sx * 0.6, -0.64, -1.5), 0.38, 0.07, "Uncommon", flare=0.0, thick=0.04, nx=1, ny=1)
    rune_line(K, (0, -0.63, -0.3), (0, -0.82, -1.4), "Uncommon", glow_rar="Epic")

    # ---------------- shoulders: rounded ivory pauldrons with gold rims and rune lines (symmetric)
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Robe", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        K.taper("Ivory", (0.08 * s, 0, 0.55), (1.32, 1.3), (1.0, 1.04), 0.38, "Common", bevel=0.09)
        K.taper("Ivory", (0.16 * s, 0, 0.28), (1.34, 1.32), (1.3, 1.3), 0.2, "Uncommon", bevel=0.05)
        K.box("Gold", (0.16 * s, 0, 0.17), (1.36, 1.34, 0.05), "Common", bevel=0.02)
        rune_line(K, (0.08 * s, -0.68, 0.62), (0.08 * s, -0.68, 0.3), "Uncommon", glow_rar="Epic")
        K.prism("Gold", (0.6 * s, 0.0, 0.62), [(0, -0.2), (0.3 * s, 0.1), (0.25 * s, 0.35), (0, 0.15)], 0.08, "Rare", rot=(0, 0, 0))
        K.sphere("Gold", (0.08 * s, 0, 0.8), 0.08, "Legendary", n=8, rings=5)

    # ---------------- arms: long bell sleeves with gold bands, ivory gloves
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.taper("Robe", (0, 0, -0.12), (1.34, 1.34), (1.1, 1.1), 0.9, "Common", bevel=0.05)
        K.band("Gold", -0.54, 0.08, 0.18, "Common")
        K.band("Gold", 0.2, 0.05, 0.07, "Uncommon")
        rune_line(K, (0, -0.65, 0.1), (0, -0.66, -0.45), "Rare", glow_rar="Epic")
        K.piece("Glove" + side)
        K.box("Ivory", (0, 0, 0.0), (1.06, 1.1, 0.36), "Common", bevel=0.05)
        K.box("Gold", (0, 0, 0.12), (1.1, 1.14, 0.06), "Uncommon", bevel=0.02)

    # ---------------- legs: white robe trousers, ivory greaves, gold toed shoes
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Robe", 0.05, "Common", hz=1.15, dz=-0.08, bevel=0.05)
        K.piece("Greave" + side)
        K.shell("Ivory", 0.08, "Common", hz=1.0, dz=-0.12, bevel=0.07)
        K.band("Gold", 0.35, 0.06, 0.1, "Uncommon")
        valdren_eye(K, (0, -0.58, 0.15), 0.45, "Rare", ring=False)
        K.piece("Boot" + side)
        K.box("Robe", (0, -0.06, 0.02), (1.1, 1.24, 0.38), "Common", bevel=0.06)
        K.box("Gold", (0, -0.5, -0.02), (1.12, 0.3, 0.3), "Uncommon", bevel=0.04)


if __name__ == "__main__":
    run(CFG, build)

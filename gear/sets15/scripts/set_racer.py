# Midnight Racer (set 7): Rider, wine / pale gold, emblem a wing with a round number.
# Tight racing silk in wine red with gold numbers, a wind hood, ribbons at the shoulders that flutter at speed.
# Asymmetric: three ribbons on the left shoulder and one on the right, a gold wing pin on the right.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="racer", model="Racer", name="Midnight Racer",
    palette={
        "Silk": ((128, 30, 54), "cloth"),
        "Night": ((40, 24, 38), "cloth"),
        "Gold": ((232, 206, 140), "metal"),
        "Leather": ((38, 34, 40), "leather"),
        "Visor": ((70, 50, 90), "glass"),
    },
    glow=(255, 222, 150),
)

SEG = {  # seven segment digits
    "0": "abcdef", "1": "bc", "7": "abc", "8": "abcdefg",
}


def digit(K, role, c, h, ch, rar, facing=-1, t=0.03):
    w = h * 0.55
    s = h * 0.13
    x, y, z = c
    segs = {
        "a": ((x, z + h / 2), (w, s)), "d": ((x, z - h / 2), (w, s)), "g": ((x, z), (w, s)),
        "b": ((x + w / 2, z + h / 4), (s, h / 2)), "c": ((x + w / 2, z - h / 4), (s, h / 2)),
        "f": ((x - w / 2, z + h / 4), (s, h / 2)), "e": ((x - w / 2, z - h / 4), (s, h / 2)),
    }
    for k in SEG[ch]:
        (px, pz), (sx, sz) = segs[k]
        if facing == 1:  # seen from the back: mirror so it reads correctly
            px = x - (px - x)
        K.box(role, (px, y, pz), (sx, t, sz), rar, bevel=0.005)


def wing(K, role, c, s, rar, flip=1, depth=0.04, rot=(0, 0, 0), sway=False):
    for i in range(3):
        L = (0.55 - i * 0.12) * s
        pts = [(0, -0.06 * s), (L, 0.02 * s), (L * 0.9, 0.09 * s), (0, 0.07 * s)]
        K.prism(role, (c[0], c[1], c[2] - i * 0.1 * s), [(flip * x, z) for x, z in pts], depth, rar, rot=(0, flip * (-12 + i * 14), 0), sway=sway)


def emblem(K, c, s, rar, facing=-1):
    K.torus("Gold", c, 0.17 * s, 0.03 * s, rar, rot=(90, 0, 0), n=14, m=4)
    digit(K, "Gold", (c[0], c[1], c[2]), 0.18 * s, "1", rar)
    wing(K, "Gold", (c[0] - 0.15 * s, c[1], c[2] + 0.06 * s), 0.7 * s, rar, flip=-1)


def ribbon(K, role, top, length, rar, side=1, width=0.12):
    K.cape(role, top, width, length, rar, flare=0.9, widen=0.4, curve=0.0, tatter=0.08, teeth=1, thick=0.03, nx=1, ny=4, tilt=0.3)


def build(K):
    # ---------------- head: snug wind hood, visor band, swept fin crest
    K.piece("Helm")
    K.hood("Silk", "Common", out=0.08, peak=0.0, drape=0.25, open_w=0.9, trim="Night")
    K.box("Silk", (0, -0.64, 0.5), (1.3, 0.12, 0.2), "Common", bevel=0.05)
    K.box("Visor", (0, -0.7, 0.47), (1.04, 0.06, 0.16), "Uncommon", bevel=0.03)
    K.box("Gold", (0, -0.71, 0.57), (1.08, 0.07, 0.04), "Uncommon", bevel=0.01)
    K.taper("Silk", (0, 0.45, 0.78), (0.18, 0.9), (0.08, 0.3), 0.32, "Common", shift=(0, 0.45), bevel=0.02)  # fin
    K.taper("Gold", (0, 0.48, 0.8), (0.2, 0.92), (0.1, 0.3), 0.06, "Uncommon", shift=(0, 0.1), bevel=0.01)
    for sx in (1, -1):
        wing(K, "Gold", (sx * 0.68, 0.1, 0.25), 0.9, "Rare", flip=sx, rot=(0, 0, 0))
    K.box("Glow", (0, -0.735, 0.47), (0.7, 0.02, 0.05), "Epic", bevel=0.0)
    ribbon(K, "Gold", (0.12, 0.7, 0.55), 1.4, "Legendary")
    ribbon(K, "Silk", (-0.12, 0.7, 0.5), 1.2, "Legendary")

    # ---------------- chest: tight racing silk, gold piping, big number on the back
    K.piece("Chest")
    K.shell("Silk", 0.05, "Common", bevel=0.07)
    K.box("Night", (0.0, -0.53, 0.05), (0.7, 0.06, 1.5), "Common", bevel=0.03)
    for sx in (1, -1):
        K.box("Gold", (sx * 0.36, -0.57, 0.05), (0.04, 0.03, 1.5), "Uncommon", bevel=0.005)
    K.strap("Gold", (0.95, -0.56, 0.75), (-0.95, -0.56, -0.6), 0.06, 0.03, "Uncommon")
    K.taper("Night", (0, 0.0, 0.84), (1.4, 1.14), (1.22, 1.06), 0.18, "Common", bevel=0.04)
    for z in (0.45, 0.15, -0.15):
        K.sphere("Gold", (0.0, -0.58, z), 0.045, "Common", n=8, rings=5)
    emblem(K, (0.0, -0.6, 0.62), 0.9, "Rare")
    K.disc("Gold", (0, 0.56, 0.1), 0.55, 0.04, "Rare", n=20)
    K.disc("Silk", (0, 0.58, 0.1), 0.48, 0.03, "Rare", n=20)
    digit(K, "Gold", (0.17, 0.61, 0.1), 0.55, "0", "Rare", facing=1)
    digit(K, "Gold", (-0.17, 0.61, 0.1), 0.55, "7", "Rare", facing=1)
    K.torus("Glow", (0, 0.6, 0.1), 0.515, 0.015, "Epic", rot=(90, 0, 0), n=20, m=4)

    # ---------------- belt: racing belt, emblem buckle, short silk tails
    K.piece("Belt")
    K.shell("Leather", 0.07, "Common", hz=0.3, bevel=0.04)
    K.box("Gold", (0, -0.58, 0), (0.42, 0.06, 0.24), "Common", bevel=0.03)
    emblem(K, (0, -0.62, 0.0), 0.6, "Rare")
    K.panel("Silk", (0, 0.56, -0.12), 1.8, 0.7, "Common", flare=0.3, widen=0.1, thick=0.05, face=1, tatter=0.25, teeth=2, nx=4)
    K.panel("Gold", (0, 0.58, -0.1), 1.82, 0.06, "Uncommon", flare=0.0, thick=0.04, face=1, nx=1, ny=1, sway=False)
    for sx in (1, -1):
        K.panel("Silk", (sx * 0.55, -0.56, -0.12), 0.7, 0.45, "Common", flare=0.15, thick=0.05, nx=2)
    ribbon(K, "Gold", (0.6, 0.6, -0.1), 1.0, "Epic")

    # ---------------- shoulders: leather caps with gold rims; ribbons (three left, one right), wing pin right
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Silk", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.06)
        K.taper("Leather", (0.05 * s, 0, 0.5), (1.18, 1.16), (1.0, 1.02), 0.28, "Common", bevel=0.05)
        K.band("Gold", 0.36, 0.05, 0.1, "Common")
        if s == 1:
            for i, (col, rar) in enumerate((("Gold", "Common"), ("Silk", "Uncommon"), ("Night", "Rare"))):
                ribbon(K, col, (0.25 + i * 0.1, 0.45, 0.6), 1.3 - i * 0.2, rar)
        else:
            ribbon(K, "Gold", (-0.3, 0.45, 0.6), 1.2, "Uncommon")
            wing(K, "Gold", (-0.2, -0.6, 0.45), 0.8, "Rare", flip=-1)
        K.box("Glow", (0.0, -0.6, 0.36), (0.6, 0.02, 0.03), "Epic", bevel=0.0)

    # ---------------- arms: flared leather gauntlet cuffs, gloves
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Silk", 0.07, "Common", hz=0.95, bevel=0.05)
        K.taper("Leather", (0, 0, -0.25), (1.2, 1.2), (1.32, 1.32), 0.55, "Common", bevel=0.05)
        K.band("Gold", 0.0, 0.05, 0.18, "Uncommon")
        digit(K, "Gold", (0.0, -0.69, -0.28), 0.25, "7" if s == 1 else "0", "Rare")
        K.piece("Glove" + side)
        K.box("Leather", (0, 0, 0.0), (1.06, 1.1, 0.36), "Common", bevel=0.05)

    # ---------------- legs: breeches with a gold stripe, tall riding boots, spurs
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Night", 0.06, "Common", hz=1.15, dz=-0.08, bevel=0.06)
        K.box("Gold", (0.56 * s, 0, -0.08), (0.03, 0.12, 1.1), "Uncommon", bevel=0.005)
        K.piece("Greave" + side)
        K.shell("Leather", 0.09, "Common", hz=1.1, dz=-0.05, bevel=0.07)
        K.taper("Leather", (0, -0.04, 0.47), (1.2, 1.2), (1.28, 1.3), 0.2, "Common", bevel=0.04)
        K.band("Gold", 0.36, 0.05, 0.16, "Uncommon")
        K.box("Glow", (0.0, -0.6, 0.0), (0.04, 0.02, 0.5), "Epic", bevel=0.0)
        K.piece("Boot" + side)
        K.box("Leather", (0, -0.08, 0.03), (1.12, 1.28, 0.38), "Common", bevel=0.07)
        K.cyl("Gold", (0, 0.62, 0.05), 0.07, 0.2, "Rare", rot=(90, 0, 0), n=8)
        K.cyl("Gold", (0, 0.78, 0.05), 0.08, 0.04, "Rare", rot=(0, 90, 0), n=8)


if __name__ == "__main__":
    run(CFG, build)

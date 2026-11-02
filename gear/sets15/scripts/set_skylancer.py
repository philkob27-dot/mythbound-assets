# Sky Lancer (set 14): Rider, saffron / gold, emblem a lance through a sun.
# A gold dive helm with a crest, narrow wing plates on the shoulders, a sun emblem, long riding boots.
# Asymmetric: four wing plates on the left and three on the right, a lance rest on the right of the breastplate.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="skylancer", model="Skylancer", name="Sky Lancer",
    palette={
        "Saffron": ((226, 118, 32), "cloth"),
        "Gold": ((228, 186, 82), "metal"),
        "Navy": ((40, 50, 84), "cloth"),
        "Leather": ((92, 60, 42), "leather"),
        "Steel": ((196, 200, 206), "metal"),
    },
    glow=(255, 210, 110),
)


def sun_lance(K, c, s, rar, facing=-1, glow_rar=None):
    x, y, z = c
    K.disc("Gold", c, 0.2 * s, 0.05, rar, n=14)
    for i in range(8):
        a = 2 * math.pi * i / 8
        K.prism("Gold", (x + math.cos(a) * 0.27 * s, y, z + math.sin(a) * 0.27 * s),
                [(-0.05 * s, -0.06 * s), (0.05 * s, -0.06 * s), (0.0, 0.1 * s)], 0.04, rar, rot=(0, 90 - math.degrees(a), 0))
    K.strap("Steel", (x - 0.45 * s, y + facing * 0.04, z - 0.45 * s), (x + 0.4 * s, y + facing * 0.04, z + 0.4 * s), 0.05 * s, 0.03, rar)
    K.prism("Steel", (x + 0.45 * s, y + facing * 0.04, z + 0.45 * s), [(-0.06 * s, 0), (0.06 * s, 0), (0, 0.18 * s)], 0.03, rar, rot=(0, 45, 0))
    if glow_rar:
        K.disc("Glow", (x, y + facing * 0.03, z), 0.12 * s, 0.02, glow_rar, n=12)


def wing_plate(K, base, L, rar, s, tilt, back=0.0, sway=False):
    """A narrow, feather like plate sweeping up and out from base."""
    a = math.radians(tilt)
    tip = (base[0] + s * math.sin(a) * L, base[1] + back, base[2] + math.cos(a) * L)
    K.strap("Gold", base, tip, 0.16, 0.06, rar, bevel=0.02, sway=sway)
    K.strap("Saffron", (base[0], base[1] - 0.035, base[2]), (base[0] + s * math.sin(a) * L * 0.7, base[1] + back * 0.7 - 0.035, base[2] + math.cos(a) * L * 0.7),
            0.06, 0.02, rar, bevel=0.0, sway=sway)


def build(K):
    # ---------------- head: gold dive helm, beak visor, comb crest, saffron plume
    K.piece("Helm")
    K.box("Gold", (0, 0.04, 0.1), (1.36, 1.36, 1.36), "Common", bevel=0.2)
    K.taper("Gold", (0, -0.62, -0.05), (0.7, 0.2), (0.9, 0.12), 0.7, "Common", shift=(0, 0.04), rot=(10, 0, 0), bevel=0.04)  # beak visor
    K.box("Navy", (0, -0.71, 0.2), (0.9, 0.04, 0.1), "Common", bevel=0.01)
    K.box("Glow", (0, -0.73, 0.2), (0.7, 0.02, 0.05), "Epic", bevel=0.0)
    K.prism("Gold", (0, 0.05, 0.8), [(-0.75, 0.0), (0.7, 0.0), (0.55, 0.35), (-0.2, 0.45), (-0.65, 0.25)], 0.12, "Common", rot=(0, 0, 90))
    K.prism("Saffron", (0, 0.05, 0.86), [(-0.6, 0.0), (0.6, 0.0), (0.45, 0.3), (-0.2, 0.36), (-0.5, 0.2)], 0.16, "Uncommon", rot=(0, 0, 90))
    K.cape("Saffron", (0, 0.7, 0.95), 0.4, 1.3, "Rare", flare=0.7, widen=0.5, curve=0.0, tatter=0.2, teeth=2, thick=0.04, nx=3, tilt=0.2)
    for sx in (1, -1):
        wing_plate(K, (sx * 0.66, 0.1, 0.3), 0.55, "Rare", sx, 35)
    for i in range(7):  # sun rays behind the crest
        a = math.radians(-60 + i * 20)
        K.prism("Gold", (math.sin(a) * 0.95, 0.5, 0.75 + math.cos(a) * 0.95), [(-0.08, -0.1), (0.08, -0.1), (0.0, 0.22)], 0.05, "Legendary",
                rot=(0, math.degrees(a), 0))
    K.torus("Glow", (0, 0.52, 0.75), 0.8, 0.02, "Legendary", rot=(90, 0, 0), n=20, m=4, arc=0.35)

    # ---------------- chest: gold breastplate, saffron tabard with the sun, lance rest, split cape
    K.piece("Chest")
    K.shell("Navy", 0.05, "Common", bevel=0.05)
    K.taper("Gold", (0, -0.02, 0.32), (2.0, 1.2), (2.22, 1.28), 1.05, "Common", bevel=0.08)
    K.taper("Gold", (0, -0.02, -0.5), (1.86, 1.14), (2.0, 1.2), 0.56, "Common", bevel=0.06)
    K.box("Saffron", (0, -0.68, 0.0), (0.9, 0.06, 1.6), "Common", bevel=0.03)
    K.box("Steel", (0, -0.02, 0.85), (2.26, 1.32, 0.06), "Uncommon", bevel=0.02)
    K.taper("Gold", (0, 0.0, 0.98), (1.5, 1.2), (1.3, 1.1), 0.2, "Common", bevel=0.05)
    sun_lance(K, (0, -0.73, 0.25), 1.0, "Rare", glow_rar="Epic")
    K.box("Steel", (-0.75, -0.7, -0.2), (0.12, 0.2, 0.25), "Rare", bevel=0.02)             # lance rest
    K.box("Steel", (-0.75, -0.8, -0.1), (0.3, 0.06, 0.06), "Rare", bevel=0.01)
    K.cape("Saffron", (0, 0.62, 0.84), 1.6, 2.4, "Common", flare=0.6, widen=0.25, curve=0.18, thick=0.05, nx=10, notch=0.9)
    K.cape("Gold", (0, 0.6, 0.82), 1.62, 2.46, "Uncommon", flare=0.6, widen=0.25, curve=0.18, thick=0.03, nx=10, notch=0.9)
    sun_lance(K, (0, 0.92, 0.2), 1.2, "Legendary", facing=1, glow_rar="Legendary")

    # ---------------- belt: gold belt, long saffron tabard front and back
    K.piece("Belt")
    K.shell("Leather", 0.08, "Common", hz=0.3, bevel=0.04)
    K.box("Gold", (0, -0.6, 0), (0.42, 0.06, 0.26), "Common", bevel=0.03)
    sun_lance(K, (0, -0.64, 0.0), 0.45, "Rare")
    K.panel("Saffron", (0, -0.58, -0.12), 0.9, 1.4, "Common", flare=0.25, widen=0.1, thick=0.05)
    K.panel("Saffron", (0, 0.58, -0.12), 0.9, 1.3, "Common", flare=0.3, widen=0.1, thick=0.05, face=1)
    K.panel("Gold", (0, -0.62, -1.42), 1.0, 0.08, "Uncommon", flare=0.0, thick=0.04, nx=1, ny=1)
    for sx in (1, -1):
        K.box("Gold", (sx * 0.75, -0.6, -0.35), (0.5, 0.1, 0.5), "Common", bevel=0.05, sway=True)

    # ---------------- shoulders: narrow wing plates, four left and three right
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Navy", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        K.taper("Gold", (0.08 * s, 0, 0.55), (1.28, 1.26), (0.98, 1.02), 0.34, "Common", bevel=0.07)
        K.box("Steel", (0.08 * s, 0, 0.38), (1.3, 1.28, 0.05), "Uncommon", bevel=0.02)
        n = 4 if s == 1 else 3
        for i in range(n):
            wing_plate(K, (s * (0.25 + i * 0.1), 0.2 + i * 0.05, 0.7), 0.95 - i * 0.12, ("Common", "Uncommon", "Rare", "Epic")[i], s,
                       20 + i * 16, back=0.35)
        K.box("Glow", (0.3 * s, -0.64, 0.5), (0.5, 0.02, 0.03), "Epic", bevel=0.0)

    # ---------------- arms: gold vambraces, saffron cuffs, gauntlets
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Gold", 0.09, "Common", hz=0.95, dz=-0.05, bevel=0.07)
        K.band("Saffron", 0.38, 0.12, 0.13, "Common")
        K.band("Steel", -0.48, 0.06, 0.14, "Uncommon")
        K.prism("Gold", (0.62 * s, 0, -0.1), [(-0.3, -0.3), (0.3, -0.3), (0.0, 0.4)], 0.06, "Rare", rot=(0, 0, 90))
        K.piece("Glove" + side)
        K.box("Leather", (0, 0, 0.0), (1.08, 1.12, 0.36), "Common", bevel=0.05)
        K.box("Gold", (0, -0.57, 0.06), (0.7, 0.04, 0.1), "Uncommon", bevel=0.01)

    # ---------------- legs: navy breeches, long riding boots, gold knee cops, spurs
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Navy", 0.06, "Common", hz=1.15, dz=-0.08, bevel=0.06)
        K.box("Saffron", (0.56 * s, 0, -0.08), (0.03, 0.14, 1.1), "Uncommon", bevel=0.005)
        K.piece("Greave" + side)
        K.shell("Leather", 0.09, "Common", hz=1.15, dz=-0.03, bevel=0.07)
        K.box("Gold", (0, -0.6, 0.5), (0.7, 0.2, 0.36), "Common", bevel=0.07)
        sun_lance(K, (0, -0.71, 0.5), 0.35, "Rare")
        K.band("Gold", -0.2, 0.05, 0.12, "Uncommon")
        K.piece("Boot" + side)
        K.box("Leather", (0, -0.08, 0.03), (1.12, 1.28, 0.38), "Common", bevel=0.07)
        K.cyl("Gold", (0, 0.62, 0.05), 0.07, 0.2, "Rare", rot=(90, 0, 0), n=8)
        K.cyl("Gold", (0, 0.78, 0.05), 0.1, 0.04, "Rare", rot=(0, 90, 0), n=8)


if __name__ == "__main__":
    run(CFG, build)

# Ashfall Knight (set 11): Heavy rider, ash / silver, emblem a broken lance.
# Burnt knight's plate, a broken lance emblem, a half cape scorched at the edge, ash on the shoulders.
# Asymmetric: half cape and a jousting grandguard on the left, a rondel on the right.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="ashknight", model="Ashknight", name="Ashfall Knight",
    palette={
        "Plate": ((122, 118, 116), "metal"),
        "Ashcloth": ((152, 148, 142), "cloth"),
        "Silver": ((204, 208, 214), "metal"),
        "Char": ((34, 30, 30), "paint"),
        "Leather": ((82, 62, 50), "leather"),
        "Ash": ((196, 192, 186), "stone"),
    },
    glow=(255, 122, 60),
)


def broken_lance(K, c, s, rar, role="Silver", facing=-1, depth=0.05):
    x, y, z = c
    K.prism(role, (x - 0.06 * s, y, z), [(-0.05 * s, -0.5 * s), (0.05 * s, -0.5 * s), (0.04 * s, 0.05 * s), (0.08 * s, 0.1 * s), (0.0, 0.0),
                                         (-0.06 * s, 0.08 * s)], depth, rar, rot=(0, 15, 0))
    K.prism(role, (x + 0.08 * s, y, z + 0.08 * s), [(-0.04 * s, 0.0), (0.03 * s, 0.05 * s), (0.08 * s, 0.0), (0.03 * s, 0.45 * s),
                                                    (0.0, 0.55 * s)], depth, rar, rot=(0, -20, 0))
    K.box(role, (x - 0.1 * s, y, z - 0.3 * s), (0.22 * s, depth, 0.05 * s), rar, rot=(0, 15, 0), bevel=0.005)


def emblem(K, c, s, rar, glow_rar=None):
    K.prism("Silver", c, [(x * s, z * s) for x, z in ((-0.3, 0.3), (0.3, 0.3), (0.3, -0.05), (0.0, -0.38), (-0.3, -0.05))], 0.06, rar)
    K.prism("Char", (c[0], c[1] - 0.03, c[2]), [(x * s, z * s) for x, z in ((-0.25, 0.25), (0.25, 0.25), (0.25, -0.04), (0.0, -0.31),
                                                                            (-0.25, -0.04))], 0.04, rar)
    broken_lance(K, (c[0], c[1] - 0.06, c[2] - 0.02 * s), 0.55 * s, rar, depth=0.03)
    if glow_rar:
        K.box("Glow", (c[0] + 0.02 * s, c[1] - 0.08, c[2] + 0.03 * s), (0.08 * s, 0.02, 0.03 * s), glow_rar, bevel=0.0)


def ash_pile(K, c, s, rar):
    for i, (dx, dy, r) in enumerate(((0, 0, 0.22), (0.18, 0.12, 0.15), (-0.15, -0.1, 0.16), (0.05, -0.2, 0.12))):
        K.sphere("Ash", (c[0] + dx * s, c[1] + dy * s, c[2]), (r * s, r * s, r * s * 0.45), rar, n=8, rings=4)


def build(K):
    # ---------------- head: burnt great helm, silver cross, scorched plume
    K.piece("Helm")
    K.box("Plate", (0, 0.0, 0.08), (1.4, 1.4, 1.42), "Common", bevel=0.12)
    K.taper("Plate", (0, 0.0, 0.88), (1.36, 1.36), (1.0, 1.0), 0.2, "Common", bevel=0.04)
    K.box("Char", (0, -0.71, 0.18), (0.9, 0.04, 0.1), "Common", bevel=0.01)              # eye slit
    K.box("Silver", (0, -0.72, 0.0), (0.12, 0.05, 1.1), "Common", bevel=0.02)            # cross
    K.box("Silver", (0, -0.72, 0.32), (1.0, 0.05, 0.1), "Uncommon", bevel=0.02)
    for sx in (1, -1):
        for i in range(3):
            K.box("Char", (sx * 0.38, -0.715, -0.15 - i * 0.14), (0.16, 0.03, 0.05), "Uncommon", bevel=0.005)
    K.box("Glow", (0, -0.735, 0.18), (0.7, 0.02, 0.04), "Epic", bevel=0.0)
    K.cyl("Silver", (0, 0.2, 1.05), 0.08, 0.2, "Common", n=8)
    K.prism("Ashcloth", (0, 0.1, 1.12), [(-0.65, -0.05), (0.55, -0.05), (0.75, 0.25), (0.35, 0.5), (-0.3, 0.45), (-0.75, 0.15)], 0.14, "Common",
            rot=(0, 0, 90))
    K.prism("Char", (0, 0.1, 1.15), [(-0.7, 0.12), (-0.3, 0.5), (0.35, 0.55), (0.8, 0.27), (0.6, 0.38), (0.3, 0.45), (-0.3, 0.4)], 0.16,
            "Uncommon", rot=(0, 0, 90))
    K.cape("Ashcloth", (0, 0.72, 1.0), 0.3, 1.1, "Rare", flare=0.5, widen=0.5, curve=0.0, tatter=0.2, teeth=2, thick=0.04, nx=3)
    ash_pile(K, (0.3, -0.1, 0.92), 0.8, "Rare")
    for sx in (1, -1):  # broken lance stubs as horns of a burnt crown
        K.cyl("Silver", (sx * 0.6, -0.1, 1.1), 0.06, 0.5, "Legendary", rot=(0, sx * 20, 0), n=6, r2=0.04)
        K.cyl("Char", (sx * 0.68, -0.1, 1.36), 0.05, 0.08, "Legendary", rot=(0, sx * 20, 0), n=6)

    # ---------------- chest: burnt plate with silver edges, emblem, half cape on the left, ember cracks
    K.piece("Chest")
    K.shell("Leather", 0.05, "Common", bevel=0.05)
    K.taper("Plate", (0, -0.02, 0.32), (2.02, 1.22), (2.24, 1.3), 1.05, "Common", bevel=0.08)
    K.taper("Plate", (0, -0.02, -0.5), (1.88, 1.15), (2.02, 1.22), 0.58, "Common", bevel=0.06)
    K.box("Silver", (0, -0.02, 0.85), (2.28, 1.34, 0.07), "Common", bevel=0.03)
    K.box("Silver", (0, -0.02, -0.2), (2.06, 1.26, 0.06), "Uncommon", bevel=0.02)
    K.taper("Plate", (0, 0.0, 0.98), (1.5, 1.2), (1.3, 1.1), 0.2, "Common", bevel=0.05)
    K.box("Plate", (0, -0.68, 0.3), (0.12, 0.1, 1.0), "Common", bevel=0.03)              # ridge
    emblem(K, (0.45, -0.68, 0.35), 0.9, "Rare", glow_rar="Epic")
    for (x, z, a) in ((-0.5, 0.1, 30), (-0.3, -0.5, -20), (0.7, -0.45, 50)):
        K.box("Char", (x, -0.66, z), (0.3, 0.03, 0.04), "Uncommon", rot=(0, a, 0), bevel=0.0)
        K.box("Glow", (x, -0.675, z), (0.2, 0.02, 0.02), "Epic", rot=(0, a, 0), bevel=0.0)
    # half cape: left shoulder only, scorched edge
    K.cape("Char", (0.42, 0.6, 0.84), 1.25, 2.95, "Common", flare=0.4, widen=0.25, curve=0.15, tatter=0.4, teeth=4, thick=0.04, nx=8)
    K.cape("Ashcloth", (0.42, 0.63, 0.86), 1.2, 2.65, "Common", flare=0.4, widen=0.22, curve=0.15, tatter=0.3, teeth=4, thick=0.06, nx=8)
    K.box("Silver", (0.45, 0.68, 0.86), (1.3, 0.1, 0.14), "Common", bevel=0.03)
    for i in range(4):
        K.box("Glow", (0.0 + i * 0.28, 1.05, -1.9 + 0.1 * (i % 2)), (0.14, 0.02, 0.03), "Legendary", bevel=0.0, sway=True)

    # ---------------- belt: plate fauld, silver belt, tassets
    K.piece("Belt")
    K.shell("Silver", 0.09, "Common", hz=0.3, bevel=0.04)
    emblem(K, (0, -0.65, -0.02), 0.6, "Rare")
    for x in (-0.6, 0.0, 0.6):
        K.taper("Plate", (x, -0.66, -0.48), (0.56, 0.12), (0.6, 0.12), 0.6, "Common", bevel=0.05, sway=True)
        K.box("Silver", (x, -0.73, -0.76), (0.6, 0.05, 0.06), "Uncommon", bevel=0.02, sway=True)
    for sx in (1, -1):
        K.box("Plate", (sx * 1.12, 0.0, -0.4), (0.14, 0.92, 0.6), "Common", bevel=0.05, sway=True)
    K.panel("Ashcloth", (0, 0.58, -0.12), 1.7, 1.0, "Common", flare=0.22, thick=0.05, face=1, tatter=0.3, teeth=4, nx=6)

    # ---------------- shoulders: heavy plates, grandguard on the left, rondel on the right, ash
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Leather", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        big = s == 1
        K.taper("Plate", (0.12 * s, 0, 0.62), (1.45 if big else 1.32, 1.42), (1.05, 1.1), 0.42, "Common", bevel=0.07)
        K.taper("Plate", (0.22 * s, 0, 0.32), (1.42, 1.38), (1.36, 1.34), 0.24, "Common", bevel=0.05)
        K.box("Silver", (0.22 * s, 0, 0.19), (1.44, 1.4, 0.06), "Uncommon", bevel=0.02)
        ash_pile(K, (0.15 * s, 0.0, 0.86), 1.0, "Uncommon")
        if big:
            K.box("Plate", (0.12, -0.72, 0.42), (1.05, 0.12, 0.7), "Rare", rot=(-10, 0, 0), bevel=0.06)     # grandguard
            K.box("Silver", (0.12, -0.79, 0.72), (1.07, 0.04, 0.08), "Rare", rot=(-10, 0, 0), bevel=0.01)
            K.box("Glow", (0.12, -0.8, 0.3), (0.6, 0.02, 0.03), "Epic", rot=(-10, 0, 0), bevel=0.0)
        else:
            K.disc("Silver", (-0.2, -0.75, 0.45), 0.3, 0.06, "Rare", n=14)
            K.disc("Plate", (-0.2, -0.79, 0.45), 0.22, 0.04, "Rare", n=14)

    # ---------------- arms: plate vambraces, gauntlets
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Plate", 0.1, "Common", hz=0.95, dz=-0.05, bevel=0.07)
        K.band("Silver", 0.38, 0.06, 0.14, "Common")
        K.band("Silver", -0.48, 0.06, 0.14, "Uncommon")
        K.taper("Plate", (0.0, -0.05, 0.5), (1.3, 1.3), (1.22, 1.24), 0.2, "Rare", bevel=0.04)      # couter
        K.piece("Glove" + side)
        K.box("Plate", (0, 0, 0.0), (1.12, 1.14, 0.38), "Common", bevel=0.06)
        K.box("Silver", (0, -0.58, 0.08), (0.7, 0.04, 0.08), "Uncommon", bevel=0.01)

    # ---------------- legs: cuisses, poleyns, greaves, sabatons with spurs
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Plate", 0.08, "Common", hz=1.0, dz=-0.15, bevel=0.07)
        K.band("Silver", 0.33, 0.06, 0.1, "Uncommon")
        K.piece("Greave" + side)
        K.shell("Plate", 0.1, "Common", hz=1.0, dz=-0.12, bevel=0.07)
        K.box("Plate", (0, -0.6, 0.42), (0.7, 0.2, 0.42), "Common", bevel=0.07)
        K.disc("Silver", (0, -0.71, 0.42), 0.13, 0.04, "Uncommon", n=10)
        broken_lance(K, (0, -0.73, 0.42), 0.35, "Rare", role="Char", depth=0.02)
        K.band("Silver", -0.6, 0.06, 0.11, "Uncommon")
        K.piece("Boot" + side)
        K.box("Plate", (0, -0.08, 0.02), (1.16, 1.3, 0.42), "Common", bevel=0.08)
        K.cyl("Silver", (0, 0.66, 0.05), 0.06, 0.22, "Rare", rot=(90, 0, 0), n=8)
        K.cyl("Silver", (0, 0.8, 0.05), 0.09, 0.04, "Rare", rot=(0, 90, 0), n=8)


if __name__ == "__main__":
    run(CFG, build)

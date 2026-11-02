# Storm Caller Regalia (set 3): Hooded, sky / copper, emblem an open hand with a lightning bolt.
# A tall hood with copper coils, a cape that ends in tatters like rain, glass orbs with lightning at the belt,
# a staff holder on the back (no sword). Asymmetric: copper coil pauldron on the left, three orbs left, one right.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="stormcaller", model="Stormcaller", name="Storm Caller Regalia",
    palette={
        "Robe": ((58, 70, 98), "cloth"),
        "Sky": ((122, 172, 222), "cloth"),
        "Copper": ((198, 112, 60), "metal"),
        "Glass": ((176, 214, 240), "glass"),
        "Leather": ((72, 56, 48), "leather"),
        "Patina": ((92, 164, 146), "paint"),
    },
    glow=(150, 222, 255),
)


def bolt(K, role, c, s, rar, depth=0.04, rot=(0, 0, 0), sway=False):
    pts = [(0.05, 0.5), (-0.18, 0.02), (0.0, 0.02), (-0.08, -0.5), (0.2, 0.08), (0.02, 0.08), (0.18, 0.5)]
    K.prism(role, c, [(x * s, z * s) for x, z in pts], depth, rar, rot=rot, sway=sway)


def emblem(K, c, s, rar):
    """Open hand with a lightning bolt on a copper roundel."""
    K.disc("Copper", c, 0.32 * s, 0.06, rar, n=16)
    K.disc("Robe", (c[0], c[1] - 0.03, c[2]), 0.26 * s, 0.03, rar, n=16)
    x, y, z = c[0], c[1] - 0.06, c[2]
    K.box("Sky", (x, y, z - 0.05 * s), (0.2 * s, 0.03, 0.18 * s), rar, bevel=0.01)
    for i in range(4):
        K.box("Sky", (x - 0.075 * s + i * 0.05 * s, y, z + 0.1 * s), (0.04 * s, 0.03, 0.14 * s), rar, bevel=0.005)
    K.box("Sky", (x + 0.13 * s, y, z - 0.02 * s), (0.04 * s, 0.03, 0.12 * s), rar, rot=(0, -40, 0), bevel=0.005)
    bolt(K, "Copper", (x, y - 0.02, z - 0.02 * s), 0.3 * s, rar, depth=0.02)


def orb(K, c, r, rar, glow_rar="Epic"):
    K.strap("Leather", (c[0], c[1], c[2] + r + 0.25), (c[0], c[1], c[2] + r), 0.03, 0.03, rar, sway=True, roundn=4)
    K.cyl("Copper", (c[0], c[1], c[2] + r * 0.95), r * 0.45, 0.07, rar, n=8, sway=True)
    K.sphere("Glass", c, r, rar, n=10, rings=6, sway=True)
    K.torus("Copper", c, r * 1.02, 0.018, rar, rot=(90, 0, 0), n=10, m=4, sway=True)
    K.torus("Copper", c, r * 1.02, 0.018, rar, rot=(0, 90, 0), n=10, m=4, sway=True)
    K.sphere("Glow", c, r * 0.45, glow_rar, n=6, rings=4, sway=True)


def build(K):
    # ---------------- head: tall hood with copper coils and a rod
    K.piece("Helm")
    K.hood("Robe", "Common", out=0.12, peak=0.75, back=0.35, drape=0.4, trim="Sky")
    for i, (z, r) in enumerate(((0.92, 0.36), (1.12, 0.26), (1.3, 0.17))):
        K.torus("Copper", (0, 0.12 + i * 0.09, z), r, 0.045, "Uncommon" if i == 0 else "Rare", n=14, m=5, scale=(1.2, 1.0, 1))
    K.cyl("Copper", (0, 0.38, 1.55), 0.035, 0.45, "Rare", rot=(-15, 0, 0), n=6)
    K.sphere("Glow", (0, 0.44, 1.8), 0.07, "Epic", n=8, rings=5)
    K.box("Copper", (0, -0.69, 0.59), (0.5, 0.06, 0.1), "Uncommon", bevel=0.02)
    bolt(K, "Copper", (0, -0.72, 0.59), 0.22, "Rare", depth=0.03)
    bolt(K, "Glow", (0, -0.75, 0.59), 0.16, "Epic", depth=0.02)
    for sx in (1, -1):  # copper rods fanning out of the hood like a storm crown
        for j, a in enumerate((25, 45)):
            K.cyl("Copper", (sx * (0.5 + j * 0.12), 0.1, 0.85 + j * 0.05), 0.03, 0.5, "Legendary", rot=(0, sx * a, 0), n=6)
            K.sphere("Glow", (sx * (0.6 + j * 0.17 + 0.05 * j), 0.1, 1.06 + j * 0.1), 0.05, "Legendary", n=6, rings=4)

    # ---------------- chest: robe, sky tabard, copper gorget with the emblem, staff holder, rain cape
    K.piece("Chest")
    K.shell("Robe", 0.07, "Common", bevel=0.06)
    K.box("Sky", (0.12, -0.58, -0.05), (0.62, 0.08, 1.7), "Common", bevel=0.03)
    for sx in (1, -1):
        K.box("Copper", (0.12 + sx * 0.33, -0.62, -0.05), (0.05, 0.04, 1.7), "Uncommon", bevel=0.01)
    K.taper("Copper", (0, -0.06, 0.82), (1.6, 1.25), (1.2, 1.1), 0.22, "Common", bevel=0.05)    # gorget
    K.box("Copper", (0.0, -0.62, 0.62), (0.9, 0.1, 0.32), "Common", bevel=0.05)
    emblem(K, (0.0, -0.7, 0.5), 1.0, "Rare")
    K.disc("Glow", (0.0, -0.79, 0.5), 0.07, 0.02, "Epic", n=8)
    # staff holder on the back: leather strap and a copper tube (no weapon in it)
    K.strap("Leather", (-0.7, -0.58, 0.8), (0.75, -0.58, -0.85), 0.14, 0.05, "Rare")
    K.strap("Leather", (-0.7, 0.58, 0.8), (0.75, 0.58, -0.85), 0.14, 0.05, "Rare")
    K.cyl("Leather", (0.25, 0.76, -0.25), 0.14, 1.7, "Rare", rot=(0, -28, 0), n=10)
    for dz in (-0.8, -0.2, 0.75):
        K.cyl("Copper", (0.25 - dz * 0.47, 0.76, -0.25 + dz * 0.88), 0.16, 0.08, "Rare", rot=(0, -28, 0), n=10)
    K.cyl("Copper", (0.25 + 0.47 * 0.9, 0.76, -0.25 - 0.88 * 0.9), 0.1, 0.12, "Rare", rot=(0, -28, 0), n=10, r2=0.15)
    # cape ending in rain: two layers, the sky layer longer and more tattered
    K.cape("Sky", (0, 0.6, 0.8), 1.8, 3.0, "Common", flare=0.5, widen=0.2, curve=0.2, tatter=0.75, teeth=9, thick=0.04, nx=18)
    K.cape("Robe", (0, 0.63, 0.82), 1.85, 2.4, "Common", flare=0.42, widen=0.2, curve=0.2, tatter=0.45, teeth=7, thick=0.06, nx=14)
    for i in range(5):
        x = -0.6 + i * 0.3
        K.box("Glow", (x, 1.02 + 0.05 * (i % 2), -1.5 - 0.15 * (i % 2)), (0.03, 0.02, 0.45), "Legendary", bevel=0.0, sway=True)

    # ---------------- belt: leather belt, copper buckle, glass orbs (three left, one right), tattered skirt
    K.piece("Belt")
    K.shell("Leather", 0.08, "Common", hz=0.32, bevel=0.04)
    K.box("Copper", (0.0, -0.6, 0.0), (0.34, 0.06, 0.3), "Common", bevel=0.03)
    bolt(K, "Sky", (0.0, -0.64, 0.0), 0.22, "Uncommon", depth=0.02)
    K.panel("Robe", (0.12, -0.57, -0.12), 0.75, 1.35, "Common", flare=0.18, widen=0.2, thick=0.05, tatter=0.3, teeth=3)
    K.panel("Robe", (0, 0.57, -0.12), 1.7, 1.2, "Common", flare=0.25, widen=0.1, thick=0.05, face=1, tatter=0.3, teeth=4)
    K.panel("Copper", (0.12, -0.6, -0.14), 0.8, 0.06, "Uncommon", flare=0.0, thick=0.05, nx=1, ny=1)
    for i, (y, z) in enumerate(((-0.35, -0.42), (0.0, -0.52), (0.33, -0.4))):
        orb(K, (1.12, y, z), 0.13, "Rare" if i != 1 else "Uncommon")
    orb(K, (-1.12, -0.15, -0.5), 0.15, "Rare", glow_rar="Legendary")

    # ---------------- shoulders: copper coil pauldron (left), robe capelet (right)
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Robe", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        if s == 1:
            K.taper("Copper", (0.08, 0, 0.5), (1.28, 1.26), (1.0, 1.04), 0.36, "Common", bevel=0.05)
            K.taper("Copper", (0.18, 0, 0.22), (1.3, 1.28), (1.22, 1.22), 0.22, "Uncommon", bevel=0.04)
            for i in range(3):
                K.torus("Copper", (0.55 + i * 0.03, 0, 0.78 + i * 0.14), 0.28 - i * 0.06, 0.04, "Rare", rot=(0, 90, 0), n=12, m=5)
            K.cyl("Copper", (0.64, 0, 1.1), 0.03, 0.4, "Epic", n=6)
            K.sphere("Glow", (0.64, 0, 1.33), 0.07, "Epic", n=8, rings=5)
        else:
            K.taper("Robe", (-0.05, 0, 0.48), (1.24, 1.22), (1.02, 1.08), 0.34, "Common", bevel=0.05)
            K.band("Sky", 0.32, 0.06, 0.13, "Common")
            K.side_panel("Sky", (-0.64, 0, 0.36), 0.9, 0.6, -1, "Rare", flare=0.06, thick=0.04, tatter=0.2)

    # ---------------- arms: leather wraps with copper coils, gloves
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Leather", 0.07, "Common", hz=0.9, dz=-0.05, bevel=0.06)
        K.band("Sky", 0.4, 0.12, 0.1, "Common")
        for i in range(3):
            K.band("Copper", -0.3 + i * 0.2, 0.05, 0.11, "Uncommon" if i == 1 else "Rare")
        K.box("Glow", (0.58 * s, -0.0, -0.1), (0.02, 0.5, 0.04), "Epic", bevel=0.0)
        K.piece("Glove" + side)
        K.box("Leather", (0, 0, 0.0), (1.08, 1.1, 0.36), "Common", bevel=0.05)
        K.box("Copper", (0, -0.57, 0.0), (0.6, 0.04, 0.12), "Uncommon", bevel=0.01)

    # ---------------- legs: robe trousers, leather wraps, copper bands, soft boots
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Robe", 0.05, "Common", hz=1.15, dz=-0.08, bevel=0.05)
        K.piece("Greave" + side)
        K.shell("Leather", 0.07, "Common", hz=1.0, dz=-0.1, bevel=0.06)
        K.band("Copper", 0.35, 0.06, 0.1, "Uncommon")
        K.box("Sky", (0, -0.55, 0.05), (0.36, 0.06, 0.5), "Common", bevel=0.02)
        bolt(K, "Copper", (0, -0.59, 0.05), 0.3, "Rare", depth=0.03)
        K.piece("Boot" + side)
        K.box("Leather", (0, -0.06, 0.02), (1.1, 1.24, 0.38), "Common", bevel=0.06)
        K.box("Copper", (0, -0.62, 0.05), (0.5, 0.06, 0.12), "Uncommon", bevel=0.02)


if __name__ == "__main__":
    run(CFG, build)

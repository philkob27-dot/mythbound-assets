# Ledgerwarden (set 8): Hooded, ash / bronze, emblem a closed book with a key.
# A grey archivist's mantle, a chain lock around the waist, keys on the belt, a reading lamp on the shoulder,
# ink stains on the gloves. Asymmetric: lamp on the right shoulder, key ring on the left hip, monocle on the right.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="ledgerwarden", model="Ledgerwarden", name="Ledgerwarden",
    palette={
        "Ash": ((132, 130, 126), "cloth"),
        "Darkash": ((72, 72, 76), "cloth"),
        "Bronze": ((178, 128, 70), "metal"),
        "Iron": ((120, 122, 126), "metal"),
        "Parchment": ((226, 212, 172), "cloth"),
        "Leather": ((92, 68, 52), "leather"),
        "Ink": ((26, 30, 58), "paint"),
        "Lamp": ((255, 214, 130), "glass"),
    },
    glow=(255, 200, 120),
)


def book(K, c, s, rar, facing=-1, rot=(0, 0, 0)):
    """Closed book with a key across it."""
    K.box("Leather", c, (0.5 * s, 0.14 * s, 0.62 * s), rar, rot=rot, bevel=0.03 * s)
    K.box("Parchment", (c[0] + 0.03 * s, c[1], c[2]), (0.46 * s, 0.1 * s, 0.56 * s), rar, rot=rot, bevel=0.01)
    K.box("Bronze", (c[0], c[1] + facing * 0.07 * s, c[2]), (0.06 * s, 0.03, 0.64 * s), rar, rot=rot, bevel=0.005)
    key(K, (c[0], c[1] + facing * 0.09 * s, c[2]), 0.5 * s, rar, rot=(rot[0], rot[1] + 45, rot[2]))


def key(K, c, s, rar, rot=(0, 0, 0), sway=False, role="Bronze"):
    M = rot_matrix(rot)
    def p(x, z):
        return tuple(Vector(c) + (M @ Vector((x * s, 0, z * s))).to_3d())
    K.torus(role, p(0, 0.35), 0.12 * s, 0.035 * s, rar, rot=(rot[0] + 90, rot[1], rot[2]), n=10, m=4, sway=sway)
    K.strap(role, p(0, 0.23), p(0, -0.45), 0.06 * s, 0.05 * s, rar, sway=sway)
    K.strap(role, p(0, -0.35), p(0.15, -0.35), 0.06 * s, 0.05 * s, rar, sway=sway)
    K.strap(role, p(0, -0.45), p(0.12, -0.45), 0.06 * s, 0.05 * s, rar, sway=sway)


def emblem(K, c, s, rar):
    K.box("Bronze", c, (0.5 * s, 0.06, 0.56 * s), rar, bevel=0.03)
    K.box("Darkash", (c[0], c[1] - 0.03, c[2]), (0.42 * s, 0.04, 0.48 * s), rar, bevel=0.02)
    book(K, (c[0], c[1] - 0.07, c[2]), 0.6 * s, rar)


def build(K):
    # ---------------- head: deep archivist's hood, monocle on a chain, crossed keys, quill
    K.piece("Helm")
    K.hood("Ash", "Common", out=0.12, peak=0.3, back=0.3, drape=0.45, trim="Darkash")
    K.box("Bronze", (0, -0.69, 0.58), (0.36, 0.06, 0.12), "Uncommon", bevel=0.02)
    K.torus("Bronze", (-0.22, -0.66, 0.08), 0.12, 0.025, "Uncommon", rot=(90, 0, 0), n=12, m=4)   # monocle
    K.cyl("Lamp", (-0.22, -0.665, 0.08), 0.1, 0.01, "Uncommon", rot=(90, 0, 0), n=10)
    K.cyl("Glow", (-0.22, -0.68, 0.08), 0.05, 0.01, "Epic", rot=(90, 0, 0), n=8)
    K.beads("Bronze", (-0.33, -0.66, 0.02), (-0.6, -0.6, -0.5), 6, 0.022, "Rare", sag=0.1)
    K.strap("Parchment", (0.55, -0.2, 0.55), (0.62, 0.35, 1.25), 0.1, 0.03, "Rare")          # quill
    K.strap("Ink", (0.55, -0.2, 0.55), (0.53, -0.28, 0.42), 0.03, 0.03, "Rare", roundn=4)
    for sx in (1, -1):
        key(K, (sx * 0.12, -0.71, 0.77), 0.45, "Legendary", rot=(0, sx * 35, 0))

    # ---------------- chest: ash robe, dark mantle, clasp chain, emblem gorget, ledger on the back, long mantle
    K.piece("Chest")
    K.shell("Ash", 0.07, "Common", bevel=0.06)
    for sx in (1, -1):
        K.box("Darkash", (sx * 0.6, 0.0, 0.74), (0.85, 1.22, 0.24), "Common", bevel=0.05)
        K.box("Darkash", (sx * 0.62, -0.55, 0.15), (0.5, 0.1, 1.2), "Common", bevel=0.04)
        K.box("Bronze", (sx * 0.36, -0.61, 0.15), (0.05, 0.04, 1.2), "Uncommon", bevel=0.01)
    K.beads("Iron", (0.38, -0.63, 0.5), (-0.38, -0.63, 0.5), 7, 0.04, "Uncommon", sag=0.15, sway=False)
    emblem(K, (0, -0.64, 0.12), 1.0, "Rare")
    K.box("Glow", (0, -0.72, -0.25), (0.3, 0.02, 0.04), "Epic", bevel=0.0)
    book(K, (0.15, 0.92, 0.0), 2.1, "Rare", facing=1, rot=(0, -8, 0))
    K.strap("Leather", (0.75, -0.6, 0.78), (-0.6, -0.6, -0.75), 0.1, 0.04, "Rare")
    K.cape("Ash", (0, 0.62, 0.82), 1.9, 3.0, "Common", flare=0.48, widen=0.18, curve=0.18, thick=0.06, nx=8)
    K.cape("Bronze", (0, 0.6, 0.8), 1.88, 3.08, "Uncommon", flare=0.48, widen=0.18, curve=0.18, thick=0.04, nx=8)
    for i in range(3):
        K.panel("Parchment", (-0.5 + i * 0.5, 1.0, 0.2 - 0.2 * i), 0.22, 0.35, "Legendary", flare=0.05, thick=0.02, face=1, nx=1, ny=1)

    # ---------------- belt: chain lock around the waist, padlock, key ring on the left hip
    K.piece("Belt")
    K.shell("Leather", 0.08, "Common", hz=0.3, bevel=0.04)
    for i in range(14):
        a = 2 * math.pi * i / 14
        K.torus("Iron", (math.sin(a) * 1.12, -math.cos(a) * 0.62, -0.02), 0.09, 0.025, "Common", rot=(90 if i % 2 else 0, 0, math.degrees(a)), n=8, m=4)
    K.box("Iron", (0, -0.72, -0.2), (0.34, 0.14, 0.3), "Common", bevel=0.04, sway=True)
    K.torus("Iron", (0, -0.72, -0.02), 0.11, 0.035, "Common", rot=(90, 0, 0), n=10, m=4, arc=0.5, sway=True)
    K.box("Bronze", (0, -0.8, -0.2), (0.06, 0.03, 0.12), "Uncommon", bevel=0.005, sway=True)
    K.box("Glow", (0, -0.805, -0.25), (0.04, 0.02, 0.04), "Epic", bevel=0.0, sway=True)
    K.torus("Bronze", (0.85, -0.56, -0.12), 0.14, 0.03, "Uncommon", rot=(90, 0, 0), n=10, m=4, sway=True)
    for i, a in enumerate((-25, 5, 30)):
        key(K, (0.85 + 0.1 * math.sin(math.radians(a)), -0.6, -0.38), 0.5, "Uncommon" if i == 1 else "Rare", rot=(0, a, 0), sway=True)
    K.panel("Ash", (0, -0.56, -0.12), 1.0, 1.45, "Common", flare=0.18, widen=0.15, thick=0.06)
    K.panel("Ash", (0, 0.56, -0.12), 1.7, 1.45, "Common", flare=0.22, widen=0.12, thick=0.06, face=1)
    for sx in (1, -1):
        K.side_panel("Ash", (sx * 1.02, 0, -0.12), 0.9, 1.35, sx, "Common", flare=0.18)
    K.panel("Darkash", (0, -0.6, -1.5), 1.1, 0.08, "Uncommon", flare=0.0, thick=0.05, nx=1, ny=1)
    K.box("Parchment", (-0.55, -0.66, -0.55), (0.3, 0.03, 0.4), "Rare", rot=(0, 8, 0), bevel=0.01, sway=True)

    # ---------------- shoulders: dark mantle caps, reading lamp on the right
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Ash", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        K.taper("Darkash", (0.05 * s, 0, 0.5), (1.24, 1.22), (1.02, 1.06), 0.32, "Common", bevel=0.05)
        K.band("Bronze", 0.33, 0.05, 0.13, "Uncommon")
        if s == -1:
            K.cyl("Bronze", (-0.2, 0.25, 0.95), 0.04, 0.6, "Rare", n=6)
            K.strap("Bronze", (-0.2, 0.25, 1.22), (-0.2, -0.2, 1.3), 0.06, 0.06, "Rare", roundn=6)
            K.cyl("Bronze", (-0.2, -0.25, 1.24), 0.14, 0.05, "Rare", n=8)
            K.cyl("Lamp", (-0.2, -0.25, 1.1), 0.1, 0.22, "Rare", n=8)
            K.cyl("Bronze", (-0.2, -0.25, 0.97), 0.13, 0.05, "Rare", n=8)
            K.cyl("Glow", (-0.2, -0.25, 1.1), 0.06, 0.16, "Epic", n=6)
        else:
            K.box("Parchment", (0.62, -0.1, 0.25), (0.04, 0.45, 0.5), "Rare", rot=(8, 0, 0), bevel=0.01)
            K.box("Bronze", (0.64, -0.1, 0.5), (0.05, 0.3, 0.05), "Rare", bevel=0.01)

    # ---------------- arms: wide sleeves, leather gloves with ink stains
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.taper("Ash", (0, 0, -0.1), (1.32, 1.32), (1.12, 1.12), 0.9, "Common", bevel=0.05)
        K.band("Darkash", -0.5, 0.1, 0.17, "Common")
        K.band("Bronze", 0.2, 0.05, 0.08, "Uncommon")
        K.piece("Glove" + side)
        K.box("Leather", (0, 0, 0.0), (1.06, 1.1, 0.36), "Common", bevel=0.05)
        K.box("Ink", (0.2 * s, -0.56, -0.05), (0.3, 0.03, 0.18), "Uncommon", bevel=0.01)
        K.box("Ink", (-0.25 * s, -0.56, 0.08), (0.14, 0.03, 0.1), "Rare", bevel=0.01)

    # ---------------- legs: dark robe trousers, leather boots with bronze buckles
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Darkash", 0.05, "Common", hz=1.15, dz=-0.08, bevel=0.05)
        K.piece("Greave" + side)
        K.shell("Leather", 0.07, "Common", hz=1.0, dz=-0.12, bevel=0.06)
        K.band("Darkash", 0.33, 0.1, 0.1, "Common")
        K.box("Bronze", (0.0, -0.58, 0.0), (0.2, 0.05, 0.14), "Uncommon", bevel=0.01)
        K.piece("Boot" + side)
        K.box("Leather", (0, -0.06, 0.02), (1.1, 1.24, 0.38), "Common", bevel=0.06)
        K.box("Bronze", (0, -0.62, 0.08), (0.3, 0.05, 0.1), "Uncommon", bevel=0.01)


if __name__ == "__main__":
    run(CFG, build)

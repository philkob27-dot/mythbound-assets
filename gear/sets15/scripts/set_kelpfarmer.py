# Kelpfarmer (set 2): Sea, moss / brass, emblem a sickle through a kelp leaf.
# Oil coat with kelp in the pockets, a sickle at the belt, a broad straw hat with a float, thigh high boots.
# Asymmetric: sickle on the left hip, float hangs from the right side of the brim, net basket on the back.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="kelpfarmer", model="Kelpfarmer", name="Kelpfarmer",
    palette={
        "Oilskin": ((184, 156, 70), "leather"),
        "Moss": ((92, 122, 58), "cloth"),
        "Brass": ((192, 150, 72), "metal"),
        "Straw": ((222, 196, 128), "cloth"),
        "Kelp": ((58, 100, 50), "plant"),
        "Rubber": ((50, 56, 52), "leather"),
        "Float": ((204, 66, 50), "paint"),
        "Wood": ((122, 88, 54), "wood"),
        "Steel": ((170, 178, 182), "metal"),
    },
    glow=(120, 255, 170),
)


def leaf(K, role, c, w, h, rar, rot=(0, 0, 0), depth=0.04, sway=False):
    pts = [(0, -h / 2), (w * 0.5, -h * 0.15), (w * 0.42, h * 0.2), (0, h / 2), (-w * 0.42, h * 0.2), (-w * 0.5, -h * 0.15)]
    K.prism(role, c, pts, depth, rar, rot=rot, sway=sway)


def sickle(K, c, s, rar, rot=(0, 0, 0), facing="front", sway=False):
    """Sickle: wooden handle and a curved blade, drawn in the XZ plane at c."""
    rx = 90 if facing == "front" else 0
    K.cyl("Wood", (c[0], c[1], c[2] - 0.22 * s), 0.05 * s, 0.42 * s, rar, rot=(0, 0, 0), n=8, sway=sway)
    K.cyl("Brass", (c[0], c[1], c[2] - 0.0 * s), 0.065 * s, 0.06 * s, rar, n=8, sway=sway)
    K.torus("Steel", (c[0] + 0.2 * s, c[1], c[2] + 0.02 * s), 0.22 * s, 0.035 * s, rar, rot=(rx, 0, 0) if facing == "front" else (0, 90, 0),
            n=10, m=4, arc=0.55, scale=(1, 1, 1), sway=sway)


def emblem(K, c, s, rar):
    K.box("Brass", c, (0.5 * s, 0.07, 0.42 * s), rar, bevel=0.03)
    K.box("Rubber", (c[0], c[1] - 0.03, c[2]), (0.4 * s, 0.04, 0.32 * s), rar, bevel=0.01)
    leaf(K, "Kelp", (c[0], c[1] - 0.06, c[2]), 0.18 * s, 0.34 * s, rar, rot=(0, 25, 0), depth=0.03)
    K.box("Brass", (c[0] + 0.02 * s, c[1] - 0.08, c[2] - 0.02 * s), (0.04 * s, 0.03, 0.34 * s), rar, rot=(0, -40, 0), bevel=0.005)
    K.box("Steel", (c[0] - 0.09 * s, c[1] - 0.08, c[2] + 0.12 * s), (0.16 * s, 0.03, 0.04 * s), rar, rot=(0, 20, 0), bevel=0.005)


def build(K):
    # ---------------- head: broad straw hat with a moss band, kelp tuft and a float on a cord
    K.piece("Helm")
    K.cyl("Straw", (0, 0.02, 0.44), 1.28, 0.08, "Common", n=18, r2=0.98, smooth=False)       # brim, drooping
    K.cyl("Straw", (0, 0.02, 0.7), 0.64, 0.5, "Common", n=14, r2=0.5, smooth=False)        # crown
    K.cyl("Straw", (0, 0.02, 0.96), 0.54, 0.04, "Common", n=14, smooth=False)
    K.cyl("Moss", (0, 0.02, 0.56), 0.66, 0.13, "Common", n=14, smooth=False)                # hat band
    K.box("Brass", (0.38, -0.54, 0.56), (0.16, 0.06, 0.15), "Uncommon", rot=(0, 0, -35), bevel=0.02)
    K.torus("Straw", (0, 0.02, 0.4), 1.17, 0.045, "Uncommon", n=18, m=4)                    # rolled brim edge
    for i, a in enumerate((-20, 5, 30)):
        leaf(K, "Kelp", (0.55 + i * 0.05, -0.36 + i * 0.1, 0.86 + i * 0.04), 0.16, 0.55, "Rare", rot=(0, a, 60), depth=0.03)
    # float on a cord, right side of the brim (hanging family: kelp and floats)
    K.strap("Rubber", (-1.05, -0.2, 0.4), (-1.05, -0.2, 0.0), 0.03, 0.03, "Rare", sway=True, roundn=4)
    K.sphere("Float", (-1.05, -0.2, -0.13), 0.15, "Rare", sway=True)
    K.cyl("Straw", (-1.05, -0.2, -0.13), 0.155, 0.08, "Rare", n=10, sway=True)
    for i in range(3):
        K.sphere("Glow", (0.53 + i * 0.06, -0.42 + i * 0.1, 1.16 + i * 0.04), 0.05, "Epic", n=6, rings=4)
    K.strap("Rubber", (0.95, 0.5, 0.4), (0.95, 0.5, 0.07), 0.03, 0.03, "Legendary", sway=True, roundn=4)
    K.sphere("Float", (0.95, 0.5, -0.05), 0.12, "Legendary", sway=True)
    for i in range(4):
        x = -0.6 + i * 0.4
        K.panel("Kelp", (x, 0.95, 0.4), 0.12, 0.55 + 0.1 * (i % 2), "Legendary", flare=0.1, thick=0.03, face=1, tatter=0.1, teeth=1, nx=1, ny=2)

    # ---------------- chest: oil coat, scarf, toggles off centre, chest pocket with kelp, net basket on the back
    K.piece("Chest")
    K.shell("Oilskin", 0.07, "Common", bevel=0.07)
    K.box("Oilskin", (0.25, -0.6, -0.02), (0.08, 0.06, 1.8), "Common", bevel=0.02)          # coat flap edge
    K.box("Brass", (0.29, -0.62, -0.02), (0.03, 0.03, 1.8), "Uncommon", bevel=0.005)
    for i in range(4):
        K.box("Brass", (0.28, -0.64, 0.55 - i * 0.36), (0.22, 0.05, 0.07), "Common", bevel=0.02)
    K.taper("Moss", (0, -0.02, 0.9), (1.5, 1.2), (1.3, 1.12), 0.24, "Common", bevel=0.06)     # scarf
    K.panel("Moss", (0.42, -0.62, 0.86), 0.24, 0.75, "Uncommon", flare=0.05, thick=0.05, tatter=0.08, teeth=2)
    K.box("Oilskin", (-0.52, -0.6, 0.15), (0.48, 0.1, 0.42), "Common", bevel=0.03)          # chest pocket
    K.box("Brass", (-0.52, -0.66, 0.31), (0.5, 0.03, 0.05), "Uncommon", bevel=0.01)
    for i, a in enumerate((-15, 10, 30)):
        leaf(K, "Kelp", (-0.66 + i * 0.12, -0.6, 0.55), 0.12, 0.42, "Rare", rot=(0, a, 0), depth=0.03, sway=True)
    K.sphere("Glow", (-0.42, -0.62, 0.78), 0.05, "Epic", n=6, rings=4)
    # basket on the back with a strap
    K.taper("Straw", (0.08, 0.84, -0.05), (0.95, 0.5), (1.15, 0.62), 1.0, "Rare", bevel=0.05)
    for z in (-0.4, 0.0, 0.38):
        K.box("Wood", (0.08, 0.84, z), (1.12, 0.62, 0.06), "Rare", bevel=0.02)
    K.strap("Rubber", (0.55, -0.56, 0.78), (-0.75, -0.56, -0.75), 0.12, 0.05, "Rare")
    K.strap("Rubber", (0.55, 0.56, 0.78), (-0.55, 0.56, -0.5), 0.12, 0.05, "Rare")
    for i in range(5):
        x = -0.32 + i * 0.16
        leaf(K, "Kelp", (x, 0.9, 0.62 + 0.08 * (i % 2)), 0.14, 0.5, "Rare", rot=(0, -20 + i * 10, 0), depth=0.03, sway=True)
    for i in range(3):
        K.sphere("Glow", (-0.2 + i * 0.22, 0.95, 0.85 + 0.05 * (i % 2)), 0.06, "Epic", n=6, rings=4)
    sickle(K, (-0.3, 0.88, 1.05), 1.2, "Legendary", facing="side")

    # ---------------- belt: leather belt, brass buckle emblem, coat tails, sickle on the left hip, net pouch
    K.piece("Belt")
    K.shell("Rubber", 0.09, "Common", hz=0.3, bevel=0.04)
    emblem(K, (0.0, -0.62, 0.0), 1.0, "Rare")
    K.box("Brass", (0.0, -0.6, 0.0), (0.36, 0.06, 0.26), "Common", bevel=0.03)
    K.panel("Oilskin", (0.52, -0.58, -0.12), 0.95, 1.05, "Common", flare=0.22, widen=0.12, thick=0.07)
    K.panel("Oilskin", (-0.52, -0.58, -0.12), 0.95, 1.05, "Common", flare=0.22, widen=0.12, thick=0.07)
    K.panel("Oilskin", (0, 0.58, -0.12), 2.05, 1.1, "Common", flare=0.25, widen=0.08, thick=0.07, face=1)
    K.panel("Brass", (0.52, -0.6, -1.13), 1.05, 0.06, "Uncommon", flare=0.0, thick=0.06, nx=1, ny=1)
    K.panel("Brass", (-0.52, -0.6, -1.13), 1.05, 0.06, "Uncommon", flare=0.0, thick=0.06, nx=1, ny=1)
    sickle(K, (0.78, -0.66, -0.12), 1.3, "Common", facing="front", sway=True)
    K.box("Rubber", (0.78, -0.62, -0.02), (0.16, 0.08, 0.2), "Common", bevel=0.02)
    # net pouch on the right hip with kelp
    K.box("Straw", (-1.1, -0.1, -0.35), (0.24, 0.5, 0.42), "Rare", bevel=0.06, sway=True)
    for i in range(3):
        leaf(K, "Kelp", (-1.12, -0.25 + i * 0.15, -0.05), 0.12, 0.36, "Rare", rot=(0, 0, 90), depth=0.03, sway=True)
    K.box("Glow", (-1.23, -0.1, -0.35), (0.02, 0.36, 0.05), "Epic", bevel=0.0)

    # ---------------- shoulders: oilskin capelets; kelp strands over the left, rope coil on the right
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Oilskin", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        K.taper("Oilskin", (0.05 * s, 0, 0.48), (1.24, 1.22), (1.04, 1.08), 0.36, "Common", bevel=0.06)
        K.band("Brass", 0.31, 0.05, 0.13, "Uncommon")
        if s == 1:
            for i in range(3):
                K.panel("Kelp", (0.25 + i * 0.12, -0.62, 0.62), 0.12, 0.85 - i * 0.12, "Rare", flare=0.12, thick=0.03, tatter=0.08, teeth=1, nx=1)
            K.sphere("Glow", (0.37, -0.7, -0.15), 0.05, "Epic", n=6, rings=4)
        else:
            K.torus("Wood", (-0.62, 0.0, 0.42), 0.38, 0.06, "Rare", rot=(0, 90, 0), n=14, m=5)
            K.torus("Wood", (-0.66, 0.0, 0.42), 0.3, 0.06, "Rare", rot=(0, 90, 0), n=14, m=5)

    # ---------------- arms: rolled moss sleeves, rubber work gloves
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Moss", 0.06, "Common", hz=0.95, bevel=0.05)
        K.band("Moss", 0.32, 0.18, 0.12, "Common", bevel=0.06)
        K.band("Rubber", -0.36, 0.28, 0.12, "Common", bevel=0.05)
        K.band("Brass", -0.24, 0.05, 0.14, "Uncommon")
        K.piece("Glove" + side)
        K.box("Rubber", (0, 0, 0.0), (1.1, 1.12, 0.38), "Common", bevel=0.06)

    # ---------------- legs: thigh high rubber boots with brass buckles
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Moss", 0.04, "Common", hz=1.25, dz=-0.05, bevel=0.04)
        K.band("Rubber", -0.18, 0.75, 0.1, "Common", bevel=0.06)
        K.band("Rubber", 0.22, 0.16, 0.15, "Common", bevel=0.05)          # folded boot top
        K.box("Brass", (0.0, -0.64, 0.22), (0.2, 0.05, 0.14), "Uncommon", bevel=0.02)
        K.box("Brass", (0.0, -0.6, -0.3), (0.16, 0.05, 0.12), "Uncommon", bevel=0.02)
        K.piece("Greave" + side)
        K.shell("Rubber", 0.1, "Common", hz=1.15, dz=-0.05, bevel=0.06)
        K.band("Brass", 0.12, 0.04, 0.12, "Uncommon")
        if s == 1:
            leaf(K, "Kelp", (0.3, -0.62, 0.35), 0.14, 0.45, "Rare", rot=(0, -15, 0), depth=0.03, sway=True)
        K.piece("Boot" + side)
        K.box("Rubber", (0, -0.08, 0.02), (1.16, 1.3, 0.42), "Common", bevel=0.08)
        K.box("Wood", (0, -0.08, -0.17), (1.18, 1.32, 0.08), "Uncommon", bevel=0.02)


if __name__ == "__main__":
    run(CFG, build)

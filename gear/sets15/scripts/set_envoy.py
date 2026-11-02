# Accord Envoy (set 1): Sacred, sea glass / pearl, emblem three hands around a shell.
# Long sea green mantle with pearl buttons, a shell collar, a sash with the three seals of the peoples,
# a diplomat's bag with wax seals. Asymmetric: shell pauldron on the left, bag on the right hip.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="envoy", model="Envoy", name="Accord Envoy",
    palette={
        "Robe": ((228, 220, 198), "cloth"),
        "Mantle": ((96, 172, 156), "cloth"),
        "Sash": ((34, 92, 100), "cloth"),
        "Pearl": ((238, 234, 222), "pearl"),
        "Gold": ((206, 170, 96), "metal"),
        "Leather": ((108, 78, 58), "leather"),
        "Wax": ((168, 44, 46), "paint"),
    },
    glow=(130, 255, 214),
)


def shell(K, role, c, s, rar, facing=-1, ribs="Pearl", rib_rar=None, depth=0.06):
    """Scallop shell standing upright, facing front (-Y) or back."""
    pts = []
    for i in range(13):
        a = math.radians(-80 + 160 * i / 12)
        r = 1.0 if i % 2 == 0 else 0.9
        pts.append((math.sin(a) * r * s, math.cos(a) * r * s * 0.9))
    pts += [(0.25 * s, -0.15 * s), (0.32 * s, -0.32 * s), (-0.32 * s, -0.32 * s), (-0.25 * s, -0.15 * s)]
    K.prism(role, c, pts, depth, rar)
    for i in range(5):
        a = -50 + 25 * i
        K.box(ribs, (c[0] + math.sin(math.radians(a)) * 0.45 * s, c[1] + facing * depth * 0.55, c[2] + math.cos(math.radians(a)) * 0.4 * s),
              (0.07 * s, 0.03, 0.8 * s), rib_rar or rar, rot=(0, a, 0), bevel=0.01)


def emblem(K, c, s, rar):
    """Three hands around a shell, on a pearl medallion."""
    K.disc("Gold", c, 0.3 * s, 0.06, rar, n=16)
    K.disc("Pearl", (c[0], c[1] - 0.035, c[2]), 0.24 * s, 0.04, rar, n=16)
    shell(K, "Sash", (c[0], c[1] - 0.065, c[2] - 0.02 * s), 0.11 * s, rar, ribs="Mantle", depth=0.03)
    for i in range(3):
        a = math.radians(90 + 120 * i)
        K.box("Gold", (c[0] + math.cos(a) * 0.18 * s, c[1] - 0.06, c[2] + math.sin(a) * 0.18 * s), (0.11 * s, 0.03, 0.07 * s), rar,
              rot=(0, -math.degrees(a) + 90, 0), bevel=0.01)


def build(K):
    # ---------------- head: soft envoy cap with a scallop crest and pearl strands
    K.piece("Helm")
    K.taper("Mantle", (0, 0.04, 0.62), (1.28, 1.28), (1.0, 1.05), 0.42, "Common", bevel=0.06)
    K.box("Pearl", (0, 0.04, 0.42), (1.34, 1.34, 0.12), "Common", bevel=0.04)
    K.box("Mantle", (0, 0.05, 0.86), (1.02, 1.07, 0.1), "Common", bevel=0.04)
    shell(K, "Pearl", (0, -0.66, 0.72), 0.36, "Common", ribs="Gold", rib_rar="Uncommon")
    for sx in (1, -1):  # side flaps over the ears
        K.box("Mantle", (sx * 0.64, 0.08, 0.05), (0.1, 0.9, 0.66), "Uncommon", bevel=0.03)
        K.box("Pearl", (sx * 0.69, 0.08, -0.29), (0.04, 0.92, 0.07), "Uncommon", bevel=0.01)
    K.beads("Pearl", (0.69, -0.32, 0.36), (0.69, -0.36, -0.5), 6, 0.05, "Rare", sag=0.0)   # strand on the left temple
    K.sphere("Gold", (0.69, -0.36, -0.58), 0.07, "Rare", sway=True)
    K.cyl("Glow", (0, -0.7, 0.72), 0.11, 0.03, "Epic", rot=(90, 0, 0), n=10)
    for i, a in enumerate((-35, 0, 35)):  # three seal discs rising behind the crest
        x = math.sin(math.radians(a)) * 0.42
        z = 1.05 + math.cos(math.radians(a)) * 0.18
        K.disc("Gold", (x, -0.25, z), 0.12, 0.05, "Legendary", n=12)
        K.disc(["Wax", "Pearl", "Mantle"][i], (x, -0.28, z), 0.08, 0.03, "Legendary", n=12)

    # ---------------- chest: robe, open mantle with pearl buttons, shell collar, sash with three seals, long mantle
    K.piece("Chest")
    K.shell("Robe", 0.06, "Common", bevel=0.06)
    for sx in (1, -1):  # mantle fronts
        K.box("Mantle", (sx * 0.72, -0.53, -0.02), (0.56, 0.1, 1.78), "Common", bevel=0.04)
        K.box("Pearl", (sx * 0.43, -0.59, -0.02), (0.06, 0.04, 1.78), "Common", bevel=0.01)
    for sx in (1, -1):  # mantle over the shoulders
        K.box("Mantle", (sx * 0.62, 0.0, 0.8), (0.76, 1.18, 0.18), "Common", bevel=0.05)
    for i in range(4):
        K.sphere("Pearl", (0.36, -0.6, 0.55 - i * 0.38), 0.055, "Uncommon", n=8, rings=5)
    # shell collar: a ring of small shells around the neck
    for i, a in enumerate(range(-70, 71, 28)):
        r = math.radians(a)
        shell(K, "Pearl", (math.sin(r) * 0.75, -0.66 - math.cos(r) * 0.06 + abs(math.sin(r)) * 0.25, 0.84), 0.2, "Rare", ribs="Mantle", depth=0.05)
    K.box("Pearl", (0, 0, 0.9), (1.25, 1.12, 0.1), "Uncommon", bevel=0.04)
    # sash: left shoulder to right hip, with three seals
    K.strap("Sash", (0.72, -0.58, 0.8), (-0.82, -0.58, -0.9), 0.32, 0.06, "Rare")
    K.strap("Sash", (0.72, 0.58, 0.8), (-0.82, 0.58, -0.9), 0.32, 0.06, "Rare")
    for i, col in enumerate(("Wax", "Pearl", "Mantle")):
        t = 0.32 + i * 0.2
        x = 0.72 + (-0.82 - 0.72) * t
        z = 0.8 + (-0.9 - 0.8) * t
        K.disc("Gold", (x, -0.64, z), 0.13, 0.05, "Rare", n=12)
        K.disc(col, (x, -0.67, z), 0.09, 0.03, "Rare", n=12)
    K.cyl("Glow", (0.72 + (-1.54) * 0.52, -0.69, 0.8 - 1.7 * 0.52), 0.05, 0.02, "Epic", rot=(90, 0, 0), n=8)
    # long mantle at the back (hanging family: mantle, pearls)
    K.cape("Pearl", (0, 0.58, 0.82), 1.9, 3.14, "Common", flare=0.45, widen=0.18, curve=0.2, thick=0.04)
    K.cape("Mantle", (0, 0.6, 0.84), 1.9, 3.05, "Common", flare=0.45, widen=0.18, curve=0.2, thick=0.06)
    K.cape("Sash", (0, 0.66, 0.84), 0.7, 2.5, "Legendary", flare=0.52, widen=0.1, curve=0.03, thick=0.04, notch=0.3)
    shell(K, "Pearl", (0, 0.76, 0.35), 0.3, "Epic", facing=1, ribs="Gold")
    K.cyl("Glow", (0, 0.81, 0.33), 0.1, 0.03, "Epic", rot=(90, 0, 0), n=10)

    # ---------------- belt: cloth belt, emblem, robe skirt panels, diplomat's bag (right hip)
    K.piece("Belt")
    K.shell("Sash", 0.08, "Common", hz=0.36, bevel=0.04)
    K.band("Gold", 0.17, 0.05, 0.1, "Uncommon")
    K.band("Gold", -0.17, 0.05, 0.1, "Uncommon")
    emblem(K, (0, -0.62, 0.0), 1.0, "Rare")
    K.panel("Robe", (0, -0.56, -0.12), 0.95, 1.45, "Common", flare=0.18, widen=0.15, thick=0.06)
    K.panel("Robe", (0, 0.56, -0.12), 1.6, 1.5, "Common", flare=0.25, widen=0.12, thick=0.06, face=1)
    K.panel("Pearl", (0, -0.58, -1.45), 1.06, 0.07, "Uncommon", flare=0.0, thick=0.05, sway=True, ny=1, nx=1)
    for sx in (1, -1):
        K.side_panel("Robe", (sx * 1.02, 0, -0.12), 0.9, 1.35, sx, "Common", flare=0.2)
        K.panel("Mantle", (sx * 0.72, -0.6, -0.1), 0.5, 1.55, "Common", flare=0.2, widen=0.1, thick=0.05)
        K.panel("Pearl", (sx * 0.47, -0.66, -0.1), 0.05, 1.55, "Uncommon", flare=0.2, thick=0.05, nx=1)
    # diplomat's bag on the right hip, strap from the belt
    K.box("Leather", (-1.1, -0.15, -0.45), (0.26, 0.62, 0.5), "Rare", bevel=0.05, sway=True)
    K.box("Leather", (-1.24, -0.15, -0.3), (0.06, 0.66, 0.3), "Rare", bevel=0.02, sway=True)
    for dy in (-0.32, 0.0):
        K.disc("Wax", (-1.28, dy, -0.42), 0.07, 0.04, "Rare", facing="side")
    K.box("Gold", (-1.28, -0.15, -0.25), (0.04, 0.12, 0.08), "Rare", bevel=0.01, sway=True)
    K.cyl("Glow", (-1.29, -0.16, -0.42), 0.05, 0.02, "Legendary", rot=(0, 90, 0), n=8)

    # ---------------- shoulders: mantle caps, a shell pauldron on the left, a tassel on the right
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Robe", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        K.taper("Mantle", (0.04 * s, 0, 0.5), (1.22, 1.22), (1.02, 1.08), 0.34, "Common", bevel=0.05)
        K.band("Pearl", 0.31, 0.06, 0.13, "Common")
        if s == 1:
            shell(K, "Pearl", (0.12, 0.0, 0.72), 0.5, "Rare", ribs="Gold")
            K.box("Gold", (0.12, 0.0, 0.42), (0.6, 0.18, 0.1), "Rare", bevel=0.02)
            K.cyl("Glow", (0.12, -0.05, 0.75), 0.08, 0.04, "Epic", rot=(90, 0, 0), n=8)
        else:
            K.cyl("Gold", (-0.6, -0.1, 0.4), 0.05, 0.1, "Rare", rot=(0, 90, 0), n=8)
            K.strap("Sash", (-0.62, -0.1, 0.36), (-0.62, -0.1, -0.15), 0.08, 0.08, "Rare", sway=True, roundn=6)
            K.cyl("Sash", (-0.62, -0.1, -0.25), 0.07, 0.2, "Rare", r2=0.03, n=8, sway=True)
            K.beads("Pearl", (-0.3, -0.62, 0.55), (0.3, -0.62, 0.55), 5, 0.045, "Legendary", sag=0.12)

    # ---------------- arms: bell cuffs with pearl bands, cream gloves
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.taper("Mantle", (0, 0, -0.15), (1.28, 1.28), (1.08, 1.08), 0.8, "Common", bevel=0.05)
        K.band("Pearl", -0.5, 0.08, 0.15, "Common")
        K.band("Gold", 0.25, 0.05, 0.07, "Uncommon")
        K.box("Glow", (0.0, -0.66, -0.2), (0.04, 0.02, 0.5), "Epic", bevel=0.0)
        K.piece("Glove" + side)
        K.box("Robe", (0, 0, 0.02), (1.06, 1.1, 0.36), "Common", bevel=0.05)
        K.box("Pearl", (0.0, -0.57, 0.02), (0.3, 0.04, 0.18), "Uncommon", bevel=0.01)

    # ---------------- legs: robe trousers, soft boots with pearl bands
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Robe", 0.05, "Common", hz=1.1, dz=-0.1, bevel=0.05)
        K.piece("Greave" + side)
        K.shell("Leather", 0.07, "Common", hz=0.95, dz=-0.15, bevel=0.06)
        K.band("Pearl", 0.32, 0.08, 0.1, "Common")
        K.box("Mantle", (0, -0.55, 0.0), (0.42, 0.08, 0.46), "Uncommon", bevel=0.02)
        shell(K, "Pearl", (0, -0.6, 0.0), 0.16, "Rare", ribs="Gold", depth=0.04)
        K.piece("Boot" + side)
        K.box("Leather", (0, -0.06, 0.02), (1.1, 1.22, 0.38), "Common", bevel=0.06)
        K.box("Pearl", (0, -0.06, -0.15), (1.12, 1.24, 0.06), "Uncommon", bevel=0.02)


if __name__ == "__main__":
    run(CFG, build)

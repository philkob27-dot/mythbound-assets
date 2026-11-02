# Castaway (set 12): Wild, ash / bone, emblem a rib with a sail.
# Sailcloth and rope over a bone harness, a ribcage as breastplate, a small skull at the belt, bare ankles with rope.
# Asymmetric: sail poncho over the right shoulder, scapula plate on the left, skull on the right hip, bandana tails left.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="castaway", model="Castaway", name="Castaway",
    palette={
        "Sail": ((218, 206, 176), "cloth"),
        "Ashcloth": ((122, 114, 104), "cloth"),
        "Bone": ((234, 224, 198), "bone"),
        "Rope": ((196, 158, 96), "rope"),
        "Drift": ((132, 110, 86), "wood"),
        "Tar": ((62, 54, 48), "leather"),
    },
    glow=(170, 255, 236),
)


def rib_sail(K, c, s, rar, facing=-1):
    """Emblem: a curved rib with a small sail on it."""
    K.torus("Bone", (c[0] + 0.12 * s, c[1], c[2]), 0.3 * s, 0.04 * s, rar, rot=(90, 0, 0), n=10, m=4, arc=0.45)
    K.prism("Sail", (c[0], c[1] + facing * 0.02, c[2] + 0.02 * s), [(-0.02 * s, -0.05 * s), (0.2 * s, -0.05 * s), (0.0, 0.3 * s)], 0.025, rar)


def skull(K, c, s, rar, sway=True, glow_rar=None):
    K.sphere("Bone", (c[0], c[1], c[2] + 0.04 * s), (0.15 * s, 0.15 * s, 0.14 * s), rar, n=10, rings=6, sway=sway)
    K.box("Bone", (c[0], c[1] - 0.04 * s, c[2] - 0.1 * s), (0.17 * s, 0.17 * s, 0.1 * s), rar, bevel=0.02 * s, sway=sway)
    for sx in (1, -1):
        K.box("Tar", (c[0] + sx * 0.06 * s, c[1] - 0.14 * s, c[2] + 0.02 * s), (0.07 * s, 0.03, 0.06 * s), rar, bevel=0.005, sway=sway)
        if glow_rar:
            K.box("Glow", (c[0] + sx * 0.06 * s, c[1] - 0.155 * s, c[2] + 0.02 * s), (0.04 * s, 0.02, 0.03 * s), glow_rar, bevel=0.0, sway=sway)


def build(K):
    # ---------------- head: sailcloth bandana, gull skull, knot tails on the left, tiny sail crest
    K.piece("Helm")
    K.box("Ashcloth", (0, 0.04, 0.42), (1.28, 1.28, 0.44), "Common", bevel=0.12)
    K.box("Sail", (0, 0.0, 0.3), (1.3, 1.3, 0.16), "Common", bevel=0.05)
    K.box("Ashcloth", (0, 0.04, 0.66), (1.12, 1.12, 0.1), "Common", bevel=0.05)
    K.sphere("Sail", (0.6, 0.35, 0.3), 0.14, "Common", n=8, rings=5)
    K.panel("Sail", (0.62, 0.42, 0.25), 0.2, 0.75, "Common", flare=0.25, thick=0.04, face=1, tatter=0.12, teeth=1, nx=1)
    K.panel("Ashcloth", (0.7, 0.32, 0.25), 0.18, 0.6, "Uncommon", flare=0.15, thick=0.04, face=1, tatter=0.1, teeth=1, nx=1)
    K.box("Rope", (0, 0.0, 0.42), (1.32, 1.32, 0.05), "Uncommon", bevel=0.02)
    skull(K, (-0.25, -0.65, 0.5), 1.1, "Rare", sway=False, glow_rar="Epic")
    K.cyl("Bone", (-0.25, -0.88, 0.45), 0.04, 0.18, "Rare", rot=(90, 0, 0), n=6, r2=0.0)    # beak
    K.torus("Bone", (-0.66, -0.15, -0.15), 0.08, 0.02, "Uncommon", rot=(0, 90, 0), n=8, m=4, arc=0.6, sway=True)  # hook earring
    K.cyl("Drift", (0.15, 0.1, 1.1), 0.04, 0.9, "Legendary", n=6)
    K.prism("Sail", (0.15, 0.08, 1.15), [(0.02, -0.3), (0.45, -0.3), (0.02, 0.4)], 0.03, "Legendary", rot=(0, 0, 20))
    K.strap("Rope", (0.15, 0.1, 1.5), (0.5, 0.2, 0.85), 0.02, 0.02, "Legendary", roundn=4)

    # ---------------- chest: ash tunic, ribcage breastplate, rope bindings, sail poncho right, patched sail at the back
    K.piece("Chest")
    K.shell("Ashcloth", 0.06, "Common", bevel=0.06)
    K.box("Bone", (0, -0.62, 0.1), (0.14, 0.12, 1.3), "Common", bevel=0.04)                 # sternum
    for i in range(4):  # ribs: arcs from the sternum round to the sides
        z = 0.55 - i * 0.3
        for sx in (1, -1):
            pts = [(sx * x, y, z - d) for x, y, d in ((0.08, -0.64, 0.0), (0.5, -0.67, 0.05), (0.88, -0.64, 0.1), (1.08, -0.42, 0.14),
                                                       (1.1, -0.05, 0.16))]
            K.rope("Bone", pts, 0.05, "Common" if i < 3 else "Uncommon", n=5)
    K.taper("Bone", (0, 0.0, 0.88), (1.3, 1.1), (1.15, 1.0), 0.14, "Uncommon", bevel=0.04)
    K.strap("Rope", (0.85, -0.62, 0.8), (-0.85, -0.62, -0.8), 0.06, 0.06, "Uncommon", roundn=5)
    K.strap("Rope", (0.85, 0.62, 0.8), (-0.85, 0.62, -0.8), 0.06, 0.06, "Uncommon", roundn=5)
    rib_sail(K, (0.45, -0.7, -0.35), 1.0, "Rare")
    K.box("Glow", (0, -0.69, 0.1), (0.04, 0.02, 0.9), "Epic", bevel=0.0)
    # sail poncho over the right shoulder
    K.box("Sail", (-0.55, 0.0, 0.78), (0.95, 1.22, 0.16), "Common", bevel=0.05)
    K.panel("Sail", (-0.62, -0.58, 0.8), 0.75, 1.0, "Common", flare=0.08, widen=0.1, thick=0.05, tatter=0.2, teeth=2, nx=4)
    K.box("Tar", (-0.62, -0.66, 0.1), (0.3, 0.03, 0.25), "Rare", bevel=0.01)              # patch
    K.cape("Sail", (0, 0.62, 0.84), 1.85, 2.4, "Common", flare=0.4, widen=0.2, curve=0.15, tatter=0.45, teeth=5, thick=0.05, nx=10)
    K.box("Ashcloth", (0.4, 0.83, -0.2), (0.45, 0.03, 0.45), "Uncommon", bevel=0.01)        # patches on the sail
    K.box("Tar", (-0.45, 0.88, -0.75), (0.35, 0.03, 0.35), "Rare", bevel=0.01)
    for i in range(5):  # spine down the back
        K.box("Bone", (0, 0.63 + 0.03 * i, 0.6 - i * 0.28), (0.2, 0.1, 0.16), "Rare", bevel=0.03)
    for i in range(3):
        K.sphere("Glow", (0.4 - 0.4 * i, 0.95 + 0.04 * i, -1.2 + 0.3 * (i % 2)), 0.05, "Legendary", n=6, rings=4, sway=True)

    # ---------------- belt: rope belt, skull at the right hip, driftwood knife, ragged wraps
    K.piece("Belt")
    K.shell("Tar", 0.07, "Common", hz=0.28, bevel=0.04)
    K.torus("Rope", (0, 0, 0.0), 1.1, 0.07, "Common", n=18, m=5, scale=(1.0, 0.58, 1.0))
    K.sphere("Rope", (0.25, -0.62, -0.02), 0.11, "Common", n=8, rings=5)
    K.strap("Rope", (0.25, -0.62, -0.05), (0.32, -0.66, -0.55), 0.06, 0.06, "Uncommon", sway=True, roundn=5)
    skull(K, (-0.85, -0.55, -0.35), 1.2, "Rare", glow_rar="Epic")
    K.strap("Rope", (-0.85, -0.55, -0.02), (-0.85, -0.55, -0.2), 0.04, 0.04, "Rare", sway=True, roundn=4)
    K.box("Drift", (0.85, -0.45, -0.2), (0.1, 0.12, 0.4), "Uncommon", bevel=0.02, sway=True)
    K.prism("Bone", (0.85, -0.45, -0.58), [(-0.05, 0.2), (0.05, 0.2), (0.02, -0.25), (-0.03, -0.18)], 0.04, "Uncommon", sway=True)
    rib_sail(K, (0.0, -0.66, 0.0), 0.5, "Rare")
    K.panel("Ashcloth", (0, -0.56, -0.1), 1.8, 0.85, "Common", flare=0.15, widen=0.1, thick=0.05, tatter=0.3, teeth=5, nx=8)
    K.panel("Ashcloth", (0, 0.56, -0.1), 1.8, 0.85, "Common", flare=0.2, widen=0.1, thick=0.05, face=1, tatter=0.3, teeth=5, nx=8)

    # ---------------- shoulders: scapula plate (left), rolled sail (right)
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Ashcloth", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        if s == 1:
            K.prism("Bone", (0.32, 0.0, 0.6), [(-0.55, -0.35), (0.45, -0.25), (0.35, 0.35), (-0.3, 0.4)], 0.12, "Common", rot=(0, 0, 90))
            K.taper("Bone", (0.1, 0, 0.55), (1.2, 1.18), (0.95, 1.0), 0.24, "Common", bevel=0.05)
            K.band("Rope", 0.35, 0.06, 0.12, "Uncommon")
            K.strap("Rope", (0.6, -0.55, 0.65), (0.6, 0.55, 0.65), 0.05, 0.05, "Uncommon", roundn=5)
            K.cyl("Bone", (0.55, -0.2, 0.85), 0.05, 0.35, "Rare", rot=(0, 30, 0), r2=0.0, n=6)
            K.cyl("Bone", (0.55, 0.2, 0.85), 0.05, 0.3, "Rare", rot=(0, 40, 0), r2=0.0, n=6)
        else:
            K.cyl("Sail", (-0.2, 0, 0.65), 0.28, 1.3, "Common", rot=(90, 0, 0), n=10)
            for dy in (-0.4, 0.4):
                K.cyl("Rope", (-0.2, dy, 0.65), 0.3, 0.06, "Uncommon", rot=(90, 0, 0), n=10)
            K.side_panel("Sail", (-0.64, -0.1, 0.4), 0.5, 0.55, -1, "Rare", flare=0.05, thick=0.03, tatter=0.15)
        K.box("Glow", (0.5 * s, -0.55, 0.3), (0.2, 0.02, 0.03), "Epic", bevel=0.0)

    # ---------------- arms: rope wrapped forearms, bone bangle, cloth hand wraps
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Sail", 0.075, "Common", hz=0.6, dz=0.15, bevel=0.05)
        for i in range(4):
            K.band("Rope", 0.2 - i * 0.15, 0.06, 0.1, "Common" if i % 2 == 0 else "Uncommon", bevel=0.03)
        if s == 1:
            K.band("Bone", -0.42, 0.08, 0.12, "Rare")
        K.piece("Glove" + side)
        K.box("Sail", (0, 0, 0.02), (1.04, 1.08, 0.32), "Common", bevel=0.05)
        K.box("Rope", (0, 0, 0.1), (1.08, 1.12, 0.05), "Uncommon", bevel=0.02)

    # ---------------- legs: ragged trousers, rope at the bare ankles, foot wraps
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Ashcloth", 0.05, "Common", hz=1.2, dz=-0.1, bevel=0.05)
        K.box("Ashcloth", (0.0, 0.0, -0.66), (1.12, 1.1, 0.14), "Common", bevel=0.04)
        K.piece("Greave" + side)
        K.box("Ashcloth", (0, 0, 0.48), (1.1, 1.08, 0.3), "Common", bevel=0.05)               # trouser ends below the knee
        for i in range(2):
            K.band("Rope", -0.45 + i * 0.12, 0.06, 0.06, "Common", bevel=0.03)
        if s == -1:
            K.box("Bone", (0, -0.55, 0.0), (0.3, 0.08, 0.6), "Rare", bevel=0.04)              # shin bone guard
            K.band("Rope", 0.12, 0.05, 0.08, "Rare")
        K.piece("Boot" + side)
        K.box("Sail", (0, -0.06, -0.05), (1.04, 1.2, 0.22), "Common", bevel=0.05)
        K.box("Tar", (0, -0.06, -0.14), (1.06, 1.22, 0.06), "Common", bevel=0.02)
        K.strap("Rope", (-0.5, -0.4, 0.06), (0.5, -0.2, 0.06), 0.05, 0.05, "Uncommon", roundn=4)


if __name__ == "__main__":
    run(CFG, build)

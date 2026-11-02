# Coral Songkeeper (set 9): Sacred, coral / pearl, emblem a shell with four notes.
# A coral crown, pearl strands before the face, a robe that moves like seaweed, a shell horn at the hip.
# Asymmetric: coral growth on the left pauldron, the horn on the right hip, the stole over the right shoulder.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="songkeeper", model="Songkeeper", name="Coral Songkeeper",
    palette={
        "Robe": ((38, 82, 112), "cloth"),
        "Coralcloth": ((232, 114, 98), "cloth"),
        "Coral": ((244, 128, 104), "paint"),
        "Pearl": ((242, 238, 228), "pearl"),
        "Seaweed": ((58, 122, 96), "cloth"),
        "Shell": ((234, 204, 172), "bone"),
    },
    glow=(140, 240, 255),
)


def scallop(K, role, c, s, rar, ribs="Pearl", depth=0.05, facing=-1, rot=(0, 0, 0)):
    pts = []
    for i in range(13):
        a = math.radians(-80 + 160 * i / 12)
        r = 1.0 if i % 2 == 0 else 0.9
        pts.append((math.sin(a) * r * s, math.cos(a) * r * s * 0.9))
    pts += [(0.25 * s, -0.15 * s), (0.32 * s, -0.32 * s), (-0.32 * s, -0.32 * s), (-0.25 * s, -0.15 * s)]
    K.prism(role, c, pts, depth, rar, rot=rot)
    for i in range(5):
        a = -50 + 25 * i
        K.box(ribs, (c[0] + math.sin(math.radians(a)) * 0.45 * s, c[1] + facing * depth * 0.55, c[2] + math.cos(math.radians(a)) * 0.4 * s),
              (0.07 * s, 0.03, 0.8 * s), rar, rot=(0, a, 0), bevel=0.01)


def coral(K, base, h, rar, spread=1.0, role="Coral", seed=0):
    """Branching coral growing up from base."""
    x, y, z = base
    K.cyl(role, (x, y, z + h * 0.35), 0.06, h * 0.7, rar, n=6, r2=0.045)
    for i, (a, t, L) in enumerate(((-35, 0.35, 0.5), (40, 0.5, 0.45), (-20, 0.7, 0.35), (25, 0.85, 0.3))):
        a = a * spread
        p = Vector((x, y, z + h * t))
        d = Vector((math.sin(math.radians(a)), 0, math.cos(math.radians(a)))) * h * L
        K.strap(role, tuple(p), tuple(p + d), 0.07, 0.07, rar, roundn=5)
        K.sphere(role, tuple(p + d), 0.045, rar, n=6, rings=4)
    K.sphere(role, (x, y, z + h * 0.72), 0.05, rar, n=6, rings=4)


def note(K, c, s, rar, role="Pearl", sway=False):
    K.sphere(role, c, (0.07 * s, 0.03, 0.055 * s), rar, n=8, rings=4, sway=sway)
    K.box(role, (c[0] + 0.06 * s, c[1], c[2] + 0.13 * s), (0.025 * s, 0.025, 0.26 * s), rar, bevel=0.0, sway=sway)


def emblem(K, c, s, rar):
    K.disc("Pearl", c, 0.34 * s, 0.05, rar, n=18)
    K.disc("Robe", (c[0], c[1] - 0.03, c[2]), 0.29 * s, 0.03, rar, n=18)
    scallop(K, "Coral", (c[0], c[1] - 0.06, c[2] - 0.06 * s), 0.14 * s, rar, ribs="Pearl", depth=0.03)
    for i in range(4):
        a = math.radians(150 - i * 40)
        note(K, (c[0] + math.cos(a) * 0.2 * s, c[1] - 0.06, c[2] + math.sin(a) * 0.17 * s - 0.02), 0.55 * s, rar)


def build(K):
    # ---------------- head: coral crown on a pearl circlet, pearl strands before the face
    K.piece("Helm")
    K.box("Robe", (0, 0.05, 0.47), (1.28, 1.28, 0.52), "Common", bevel=0.14)        # sea cap
    K.box("Pearl", (0, 0.03, 0.24), (1.34, 1.34, 0.12), "Common", bevel=0.05)
    for i, x in enumerate((-0.4, 0.0, 0.4)):
        coral(K, (x, -0.4, 0.68), 0.7 if i == 1 else 0.55, "Common", spread=1.0 if i != 1 else 0.7)
    for i, x in enumerate((-0.45, 0.45)):
        coral(K, (x, 0.2, 0.68), 0.5, "Uncommon", spread=1.2)
    for x in (-0.48, -0.3, 0.3, 0.48):  # pearl strands before the face (hanging family: pearls and seaweed)
        K.beads("Pearl", (x, -0.68, 0.2), (x, -0.7, -0.3 - 0.1 * (abs(x) > 0.4)), 6, 0.045, "Rare", sag=0.0)
    K.beads("Pearl", (-0.48, -0.69, 0.2), (0.48, -0.69, 0.2), 9, 0.04, "Uncommon", sag=0.0)
    K.sphere("Pearl", (0, -0.7, 0.3), 0.1, "Common", n=10, rings=6)
    K.sphere("Glow", (0, -0.76, 0.3), 0.06, "Epic", n=8, rings=5)
    coral(K, (0.62, 0.0, 0.5), 0.95, "Legendary", spread=1.3)
    coral(K, (-0.62, 0.0, 0.5), 0.85, "Legendary", spread=1.3)
    for i in range(3):
        note(K, (-0.95 + i * 0.12, -0.2, 1.3 + i * 0.18), 1.2, "Legendary", role="Glow")

    # ---------------- chest: robe, pearl collar, coral stole, emblem, seaweed strips at the back
    K.piece("Chest")
    K.shell("Robe", 0.07, "Common", bevel=0.06)
    K.taper("Pearl", (0, -0.02, 0.86), (1.65, 1.25), (1.3, 1.1), 0.2, "Common", bevel=0.05)
    K.beads("Pearl", (-0.6, -0.62, 0.72), (0.6, -0.62, 0.72), 9, 0.05, "Uncommon", sag=0.3, sway=False)
    emblem(K, (0, -0.6, 0.15), 1.0, "Rare")
    K.disc("Glow", (0, -0.68, 0.1), 0.05, 0.02, "Epic", n=8)
    K.box("Coralcloth", (-0.6, -0.56, 0.0), (0.4, 0.1, 1.75), "Common", bevel=0.03)          # stole, right side
    K.box("Coralcloth", (-0.6, 0.0, 0.84), (0.42, 1.2, 0.12), "Common", bevel=0.03)
    K.box("Pearl", (-0.6, -0.62, -0.5), (0.42, 0.04, 0.06), "Uncommon", bevel=0.01)
    for i in range(7):  # seaweed strips down the back
        x = -0.78 + i * 0.26
        L = 2.6 + 0.35 * math.sin(i * 1.7)
        K.cape("Seaweed" if i % 2 == 0 else "Robe", (x, 0.6 + 0.02 * (i % 2), 0.82), 0.3, L, "Common" if i % 2 == 0 else "Uncommon",
               flare=0.42 + 0.05 * (i % 3), widen=0.2, curve=0.0, tatter=0.25, teeth=1, thick=0.04, nx=2, ny=6, tilt=0.05 * math.sin(i))
    K.cape("Coralcloth", (0.0, 0.66, 0.84), 0.5, 2.2, "Rare", flare=0.5, widen=0.4, curve=0.0, tatter=0.3, teeth=2, thick=0.04, nx=4)

    # ---------------- belt: pearl belt, seaweed strip skirt, shell horn on the right hip
    K.piece("Belt")
    K.shell("Coralcloth", 0.08, "Common", hz=0.32, bevel=0.04)
    K.band("Pearl", 0.16, 0.05, 0.1, "Uncommon")
    K.band("Pearl", -0.16, 0.05, 0.1, "Uncommon")
    scallop(K, "Shell", (0, -0.63, -0.02), 0.2, "Rare", ribs="Coral", depth=0.04)
    for i in range(6):
        x = -0.8 + i * 0.32
        K.panel("Seaweed" if i % 2 else "Robe", (x, -0.56, -0.12), 0.34, 1.35 + 0.15 * math.sin(i * 2.1), "Common", flare=0.18, widen=0.1,
                thick=0.04, tatter=0.2, teeth=1, nx=2)
        K.panel("Robe" if i % 2 else "Seaweed", (x, 0.56, -0.12), 0.34, 1.4 + 0.15 * math.cos(i * 1.3), "Common", flare=0.22, widen=0.1,
                thick=0.04, face=1, tatter=0.2, teeth=1, nx=2)
    for sx in (1, -1):
        K.side_panel("Robe", (sx * 1.02, 0, -0.12), 0.9, 1.3, sx, "Common", flare=0.18, tatter=0.2)
    # shell horn: a conch on a cord
    K.cyl("Shell", (-1.15, -0.1, -0.4), 0.18, 0.55, "Rare", rot=(0, 0, 0), n=10, r2=0.0, sway=True)
    K.torus("Shell", (-1.15, -0.1, -0.15), 0.18, 0.06, "Rare", n=10, m=5, sway=True)
    K.torus("Coral", (-1.15, -0.1, -0.33), 0.13, 0.04, "Rare", n=10, m=4, sway=True)
    K.cyl("Pearl", (-1.15, -0.1, -0.7), 0.05, 0.08, "Rare", n=8, sway=True)
    K.cyl("Glow", (-1.15, -0.1, -0.09), 0.13, 0.02, "Legendary", n=10, sway=True)

    # ---------------- shoulders: shell pauldrons, coral growth on the left
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Robe", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        K.taper("Shell", (0.06 * s, 0, 0.5), (1.24, 1.24), (0.98, 1.02), 0.34, "Common", bevel=0.06)
        K.band("Pearl", 0.31, 0.06, 0.14, "Common")
        scallop(K, "Shell", (0.2 * s, -0.66, 0.55), 0.32, "Uncommon", ribs="Coral")
        if s == 1:
            coral(K, (0.3, 0.0, 0.65), 0.75, "Rare", spread=1.2)
            coral(K, (0.05, 0.25, 0.65), 0.55, "Epic", spread=1.0)
        else:
            K.beads("Pearl", (-0.62, -0.4, 0.35), (-0.62, 0.4, 0.35), 7, 0.045, "Rare", sag=0.35)
        K.sphere("Glow", (0.2 * s, -0.7, 0.62), 0.05, "Epic", n=6, rings=4)

    # ---------------- arms: flowing sleeves with seaweed tails, pearl banded gloves
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.taper("Robe", (0, 0, -0.12), (1.3, 1.3), (1.1, 1.1), 0.85, "Common", bevel=0.05)
        K.band("Coralcloth", -0.5, 0.1, 0.16, "Common")
        K.panel("Seaweed", (0.0, 0.62, -0.45), 0.5, 0.7, "Rare", flare=0.15, thick=0.03, face=1, tatter=0.25, teeth=2, nx=4)
        K.piece("Glove" + side)
        K.box("Robe", (0, 0, 0.0), (1.06, 1.1, 0.36), "Common", bevel=0.05)
        K.box("Pearl", (0, 0, 0.12), (1.1, 1.14, 0.06), "Uncommon", bevel=0.02)

    # ---------------- legs: robe leggings, shell capped sandals
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Robe", 0.05, "Common", hz=1.15, dz=-0.08, bevel=0.05)
        K.piece("Greave" + side)
        K.shell("Seaweed", 0.06, "Common", hz=1.0, dz=-0.12, bevel=0.06)
        K.band("Pearl", 0.32, 0.06, 0.1, "Uncommon")
        scallop(K, "Shell", (0, -0.58, 0.2), 0.18, "Rare", ribs="Coral", depth=0.04)
        K.piece("Boot" + side)
        K.box("Shell", (0, -0.06, 0.02), (1.1, 1.24, 0.38), "Common", bevel=0.07)
        K.box("Coral", (0, -0.62, 0.05), (0.4, 0.05, 0.14), "Uncommon", bevel=0.01)


if __name__ == "__main__":
    run(CFG, build)

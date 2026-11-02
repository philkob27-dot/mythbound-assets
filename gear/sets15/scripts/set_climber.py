# Thunderhead Climber (set 6): Rider, sky / silver, emblem a feather with a lightning bolt.
# A climbing harness with hooks, feathers on the shoulders, wind goggles, a rope over the shoulder, gloves with claws.
# Asymmetric: rope coil over the right shoulder, a bigger feather fan on the left, the plume on the left of the cap.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="climber", model="Climber", name="Thunderhead Climber",
    palette={
        "Jacket": ((112, 162, 214), "cloth"),
        "Leather": ((104, 82, 62), "leather"),
        "Silver": ((204, 210, 216), "metal"),
        "Rope": ((214, 192, 140), "rope"),
        "Feather": ((240, 238, 230), "cloth"),
        "Storm": ((62, 72, 92), "cloth"),
        "Lens": ((150, 206, 240), "glass"),
    },
    glow=(170, 224, 255),
)


def feather(K, c, length, rar, rot=(0, 0, 0), sway=True, tip=True, w=0.22):
    pts = [(0, -0.5), (0.45, -0.25), (0.5, 0.15), (0.2, 0.42), (0, 0.5), (-0.25, 0.4), (-0.42, 0.1), (-0.35, -0.3)]
    K.prism("Feather", c, [(x * w, z * length) for x, z in pts], 0.035, rar, rot=rot, sway=sway)
    if tip:
        M = rot_matrix(rot)
        p = Vector(c) + (M @ Vector((0, 0, length * 0.36))).to_3d()
        K.prism("Storm", tuple(p), [(x * w * 1.04, z * length * 0.3) for x, z in pts], 0.04, rar, rot=rot, sway=sway)
    K.strap("Silver", tuple(Vector(c) - (rot_matrix(rot) @ Vector((0, 0, length * 0.5))).to_3d()),
            tuple(Vector(c) + (rot_matrix(rot) @ Vector((0, 0, length * 0.45))).to_3d()), 0.025, 0.05, rar, sway=sway, roundn=4)


def bolt(K, role, c, s, rar, depth=0.03, rot=(0, 0, 0)):
    pts = [(0.05, 0.5), (-0.18, 0.02), (0.0, 0.02), (-0.08, -0.5), (0.2, 0.08), (0.02, 0.08), (0.18, 0.5)]
    K.prism(role, c, [(x * s, z * s) for x, z in pts], depth, rar, rot=rot)


def emblem(K, c, s, rar):
    K.box("Silver", c, (0.42 * s, 0.07, 0.42 * s), rar, bevel=0.04)
    K.box("Storm", (c[0], c[1] - 0.03, c[2]), (0.34 * s, 0.04, 0.34 * s), rar, bevel=0.02)
    feather(K, (c[0] - 0.03 * s, c[1] - 0.06, c[2]), 0.3 * s, rar, rot=(0, 30, 0), sway=False, tip=False, w=0.18 * s)
    bolt(K, "Jacket", (c[0] + 0.08 * s, c[1] - 0.07, c[2]), 0.22 * s, rar, depth=0.02)


def carabiner(K, c, rar, rot=(0, 0, 0)):
    K.torus("Silver", c, 0.08, 0.02, rar, rot=(90 + rot[0], rot[1], rot[2]), n=10, m=4, scale=(0.7, 1.0, 1.0), sway=True)


def build(K):
    # ---------------- head: leather aviator cap with ear flaps, wind goggles, a feather plume
    K.piece("Helm")
    K.box("Leather", (0, 0.04, 0.2), (1.32, 1.3, 0.85), "Common", bevel=0.14)
    K.box("Leather", (0, 0.06, 0.62), (1.18, 1.18, 0.12), "Common", bevel=0.06)
    for sx in (1, -1):
        K.box("Leather", (sx * 0.64, -0.02, -0.35), (0.1, 0.62, 0.55), "Common", bevel=0.04)    # ear flaps
        K.box("Feather", (sx * 0.7, -0.02, -0.35), (0.04, 0.5, 0.42), "Uncommon", bevel=0.02)  # fleece
    K.band("Storm", 0.32, 0.12, 0.1, "Common")
    for sx in (1, -1):  # goggles pushed up on the cap
        K.cyl("Silver", (sx * 0.24, -0.66, 0.34), 0.2, 0.12, "Common", rot=(90, 0, 0), n=12)
        K.cyl("Lens", (sx * 0.24, -0.73, 0.34), 0.15, 0.04, "Common", rot=(90, 0, 0), n=12)
        K.cyl("Glow", (sx * 0.24, -0.755, 0.34), 0.08, 0.02, "Epic", rot=(90, 0, 0), n=8)
    K.box("Silver", (0, -0.7, 0.34), (0.12, 0.06, 0.06), "Common", bevel=0.01)
    feather(K, (0.6, 0.15, 0.85), 0.75, "Uncommon", rot=(-20, 25, 0), sway=True)
    feather(K, (0.64, 0.3, 0.75), 0.6, "Rare", rot=(-35, 40, 0), sway=True)
    for i in range(5):  # Legendary: feather crest down the back of the cap
        a = -30 + i * 15
        feather(K, (math.sin(math.radians(a)) * 0.35, 0.78, 0.55 + math.cos(math.radians(a)) * 0.1), 0.6, "Legendary", rot=(-60, a, 0), sway=True)

    # ---------------- chest: padded jacket, climbing harness, rope coil over the right shoulder, scarf
    K.piece("Chest")
    K.shell("Jacket", 0.08, "Common", bevel=0.08)
    for z in (-0.4, 0.0, 0.4):
        K.box("Storm", (0, -0.585, z), (1.9, 0.02, 0.04), "Uncommon", bevel=0.0)
    K.taper("Storm", (0, 0.0, 0.84), (1.5, 1.2), (1.3, 1.1), 0.2, "Common", bevel=0.05)       # collar
    for sx in (1, -1):  # harness straps
        K.box("Leather", (sx * 0.42, -0.6, 0.0), (0.18, 0.06, 1.7), "Common", bevel=0.02)
        K.box("Leather", (sx * 0.42, 0.6, 0.0), (0.18, 0.06, 1.7), "Common", bevel=0.02)
        K.box("Leather", (sx * 0.42, 0.0, 0.86), (0.18, 1.26, 0.06), "Common", bevel=0.02)
    K.box("Leather", (0, -0.62, 0.2), (1.1, 0.06, 0.16), "Common", bevel=0.02)
    emblem(K, (0, -0.68, 0.2), 0.9, "Rare")
    for sx in (1, -1):
        K.box("Silver", (sx * 0.42, -0.65, -0.4), (0.24, 0.05, 0.12), "Uncommon", bevel=0.01)
    carabiner(K, (0.42, -0.68, -0.6), "Rare")
    carabiner(K, (-0.42, -0.68, -0.6), "Rare")
    # rope coil: right shoulder to left hip
    K.torus("Rope", (-0.05, -0.05, 0.0), 1.05, 0.08, "Uncommon", rot=(0, 52, 0), n=22, m=6, scale=(1.0, 0.72, 1.0))
    K.torus("Rope", (-0.05, -0.05, 0.0), 1.05, 0.08, "Rare", rot=(0, 46, 0), n=22, m=6, scale=(1.02, 0.74, 1.0))
    K.box("Leather", (-0.9, -0.62, 0.62), (0.16, 0.1, 0.28), "Rare", rot=(0, 52, 0), bevel=0.02)
    # scarf trailing behind (hanging family: feathers, carabiners, scarf)
    K.cape("Storm", (0.3, 0.62, 0.8), 0.5, 1.6, "Uncommon", flare=0.6, widen=0.3, curve=0.0, tatter=0.25, teeth=2, thick=0.04, nx=4, tilt=0.3)
    K.cape("Jacket", (-0.2, 0.64, 0.8), 0.4, 1.2, "Rare", flare=0.55, widen=0.3, curve=0.0, tatter=0.2, teeth=2, thick=0.04, nx=4, tilt=0.25)
    K.box("Glow", (0, -0.64, -0.2), (1.0, 0.02, 0.04), "Epic", bevel=0.0)

    # ---------------- belt: harness waist belt, hooks, chalk pouch, belay loop
    K.piece("Belt")
    K.shell("Leather", 0.1, "Common", hz=0.36, bevel=0.04)
    K.box("Silver", (0.0, -0.62, 0.0), (0.4, 0.06, 0.24), "Common", bevel=0.03)
    K.torus("Silver", (0.0, -0.68, -0.2), 0.14, 0.035, "Uncommon", rot=(90, 0, 0), n=10, m=4, sway=True)
    for i, x in enumerate((0.55, 0.8, -0.6)):
        carabiner(K, (x, -0.62, -0.22), "Uncommon" if i < 2 else "Rare")
        K.cyl("Silver", (x, -0.62, -0.4), 0.03, 0.2, "Rare", n=6, sway=True)
    K.cyl("Feather", (0.7, 0.55, -0.15), 0.18, 0.36, "Rare", n=10, sway=True)      # chalk pouch
    K.cyl("Storm", (0.7, 0.55, 0.06), 0.19, 0.06, "Rare", n=10, sway=True)
    K.panel("Jacket", (0, 0.58, -0.12), 1.6, 0.6, "Common", flare=0.15, widen=0.1, thick=0.06, face=1)

    # ---------------- shoulders: feather fans, big on the left, small on the right
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Jacket", 0.06, "Common", hz=0.95, dz=0.05, bevel=0.06)
        K.taper("Leather", (0.06 * s, 0, 0.5), (1.22, 1.2), (1.02, 1.04), 0.3, "Common", bevel=0.05)
        K.band("Silver", 0.34, 0.05, 0.12, "Uncommon")
        n = 5 if s == 1 else 3
        for i in range(n):
            a = 15 + i * 22
            L = (1.0 if s == 1 else 0.8) - 0.08 * i
            feather(K, (s * (0.3 + 0.12 * i), 0.15 - i * 0.12, 0.72 + L * 0.42), L,
                    ("Common", "Uncommon", "Rare", "Rare", "Epic")[i], rot=(-10, s * a, 0), sway=True)
        if s == 1:
            K.box("Glow", (0.62, -0.0, 0.5), (0.03, 0.8, 0.03), "Epic", bevel=0.0)

    # ---------------- arms: leather bracers with silver bands, clawed gloves
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Jacket", 0.08, "Common", hz=0.95, bevel=0.05)
        K.band("Leather", -0.25, 0.5, 0.12, "Common", bevel=0.05)
        K.band("Silver", -0.05, 0.05, 0.14, "Uncommon")
        K.band("Silver", -0.45, 0.05, 0.14, "Rare")
        K.piece("Glove" + side)
        K.box("Leather", (0, 0, 0.0), (1.08, 1.1, 0.38), "Common", bevel=0.05)
        for i in range(4):
            K.cyl("Silver", (-0.33 + i * 0.22, -0.52, -0.25), 0.05, 0.22, "Uncommon" if i % 2 == 0 else "Rare", rot=(200, 0, 0), r2=0.0, n=6)

    # ---------------- legs: harness leg loops, tall boots, crampon soles
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Leather", 0.05, "Common", hz=1.15, dz=-0.08, bevel=0.05)
        K.band("Storm", 0.35, 0.1, 0.11, "Common")
        K.box("Silver", (0.0, -0.6, 0.35), (0.16, 0.05, 0.12), "Uncommon", bevel=0.01)
        if s == 1:
            carabiner(K, (0.55, -0.1, 0.25), "Rare")
        K.piece("Greave" + side)
        K.shell("Leather", 0.09, "Common", hz=1.05, dz=-0.08, bevel=0.07)
        K.band("Storm", 0.42, 0.14, 0.12, "Common")
        for z in (0.1, -0.25):
            K.box("Silver", (0.3 * s, -0.6, z), (0.18, 0.06, 0.1), "Uncommon", bevel=0.01)
        K.box("Silver", (0, -0.62, 0.4), (0.3, 0.06, 0.06), "Rare", bevel=0.01)
        K.piece("Boot" + side)
        K.box("Leather", (0, -0.08, 0.04), (1.12, 1.26, 0.38), "Common", bevel=0.07)
        K.box("Storm", (0, -0.08, -0.15), (1.14, 1.28, 0.08), "Common", bevel=0.02)
        for i in range(3):
            K.cyl("Silver", (-0.35 + i * 0.35, -0.6, -0.22), 0.05, 0.12, "Rare", rot=(180, 0, 0), r2=0.0, n=5)


if __name__ == "__main__":
    run(CFG, build)

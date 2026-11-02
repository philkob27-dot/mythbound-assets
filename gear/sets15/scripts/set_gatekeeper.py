# Abyss Gatekeeper (set 10): Heavy, teal / silver, emblem a gate with a lock.
# Heavy nacre plates, a gate shaped breastplate with a lock, lobster shoulders, a cape of kelp.
# Asymmetric: a lobster claw rises from the left pauldron, the antennae sweep to the right.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="gatekeeper", model="Gatekeeper", name="Abyss Gatekeeper",
    palette={
        "Nacre": ((212, 226, 226), "pearl"),
        "Teal": ((30, 108, 116), "cloth"),
        "Silver": ((196, 204, 212), "metal"),
        "Steel": ((62, 74, 84), "metal"),
        "Lobster": ((52, 86, 122), "paint"),
        "Kelp": ((52, 94, 58), "plant"),
    },
    glow=(90, 255, 230),
)


def gate(K, c, w, h, rar, bars=4, facing=-1, lock=True, glow_rar=None, depth=0.06):
    """Gate: two pillars, an arch, bars and a lock."""
    x, y, z = c
    for sx in (1, -1):
        K.box("Silver", (x + sx * w / 2, y, z - h * 0.1), (w * 0.14, depth, h * 0.8), rar, bevel=0.01)
    K.torus("Silver", (x, y, z + h * 0.3), w / 2, w * 0.07, rar, rot=(90, 0, 0), n=12, m=4, arc=0.5)
    for i in range(bars):
        bx = x - w / 2 + w * (i + 1) / (bars + 1)
        top = z + h * 0.3 + math.sqrt(max(0.0, (w / 2) ** 2 - (bx - x) ** 2)) * 0.9
        K.box("Steel", (bx, y - facing * 0.01, (top + z - h / 2) / 2), (w * 0.06, depth * 0.7, top - (z - h / 2)), rar, bevel=0.005)
    if lock:
        K.box("Silver", (x, y + facing * depth * 0.6, z - h * 0.05), (w * 0.3, depth, w * 0.28), rar, bevel=0.02)
        K.torus("Silver", (x, y + facing * depth * 0.6, z + w * 0.1), w * 0.1, w * 0.03, rar, rot=(90, 0, 0), n=8, m=4, arc=0.5)
        if glow_rar:
            K.box("Glow", (x, y + facing * depth * 1.1, z - h * 0.05), (w * 0.05, 0.02, w * 0.12), glow_rar, bevel=0.0)


def claw(K, c, s, rar, rot=(0, 0, 0)):
    K.prism("Lobster", c, [(x * s, z * s) for x, z in ((0, 0), (0.25, 0.1), (0.32, 0.6), (0.18, 0.95), (0.05, 0.55))], 0.2 * s, rar, rot=rot)
    K.prism("Lobster", c, [(x * s, z * s) for x, z in ((0, 0), (-0.2, 0.1), (-0.25, 0.5), (-0.12, 0.8), (-0.02, 0.45))], 0.18 * s, rar,
            rot=rot)
    K.box("Silver", c, (0.5 * s, 0.24 * s, 0.12 * s), rar, rot=rot, bevel=0.02)


def lobster_plates(K, s, n, rar_list, top=0.72):
    for i in range(n):
        z = top - i * 0.22
        w = 1.32 + i * 0.04
        K.taper("Lobster", (s * (0.1 + i * 0.05), 0, z), (w, 1.34), (w - 0.18, 1.18), 0.24, rar_list[i], bevel=0.05)
        K.box("Silver", (s * (0.1 + i * 0.05), 0, z - 0.11), (w + 0.02, 1.36, 0.04), rar_list[i], bevel=0.01)


def build(K):
    # ---------------- head: closed nacre helm, barred visor, lobster tail crest, antennae
    K.piece("Helm")
    K.visor_helm("Nacre", "Common", out=0.13, bevel=0.1)
    K.box("Steel", (0, -0.72, 0.05), (0.8, 0.04, 0.4), "Common", bevel=0.01)
    for i in range(5):
        K.box("Silver", (-0.32 + i * 0.16, -0.75, 0.05), (0.05, 0.04, 0.44), "Common", bevel=0.005)
    K.box("Glow", (0, -0.735, 0.05), (0.72, 0.02, 0.06), "Epic", bevel=0.0)
    K.box("Silver", (0, -0.72, 0.32), (1.1, 0.1, 0.1), "Uncommon", bevel=0.02)
    for i in range(4):  # lobster tail crest running back over the helm
        K.taper("Lobster", (0, -0.25 + i * 0.28, 0.98 - i * 0.06), (0.5 - i * 0.05, 0.32), (0.3 - i * 0.04, 0.26), 0.2, "Uncommon" if i < 2 else "Rare",
                bevel=0.04)
    K.prism("Lobster", (0, 0.85, 0.65), [(-0.35, -0.3), (0.35, -0.3), (0.45, 0.15), (0.0, 0.3), (-0.45, 0.15)], 0.12, "Rare",
            rot=(-50, 0, 0))
    K.rope("Lobster", [(-0.2, -0.55, 0.85), (-0.5, -0.8, 1.3), (-0.95, -0.6, 1.55), (-1.35, -0.1, 1.5)], 0.03, "Rare", sway=True, n=4)
    K.rope("Lobster", [(0.2, -0.55, 0.85), (0.1, -0.7, 1.35), (-0.3, -0.5, 1.8), (-0.75, 0.0, 1.95)], 0.03, "Epic", sway=True, n=4)
    gate(K, (0, -0.25, 1.25), 0.7, 0.6, "Legendary", bars=3, lock=False)

    # ---------------- chest: nacre plate with the gate and lock, teal surcoat edges, kelp cape
    K.piece("Chest")
    K.shell("Teal", 0.05, "Common", bevel=0.05)
    K.taper("Nacre", (0, -0.02, 0.3), (2.04, 1.22), (2.28, 1.3), 1.1, "Common", bevel=0.08)
    K.taper("Nacre", (0, -0.02, -0.52), (1.9, 1.15), (2.04, 1.22), 0.5, "Common", bevel=0.06)
    K.box("Silver", (0, -0.02, 0.86), (2.32, 1.34, 0.08), "Common", bevel=0.03)
    K.taper("Steel", (0, 0.0, 0.98), (1.5, 1.2), (1.3, 1.1), 0.2, "Common", bevel=0.05)
    gate(K, (0, -0.7, 0.2), 0.95, 1.1, "Common", bars=4, glow_rar="Epic")
    K.box("Silver", (0, -0.66, -0.52), (1.5, 0.06, 0.08), "Uncommon", bevel=0.01)
    for sx in (1, -1):
        K.box("Silver", (sx * 1.05, -0.02, 0.3), (0.08, 1.34, 1.06), "Uncommon", bevel=0.02)
    for i in range(8):  # kelp cape: narrow tattered strips
        x = -0.84 + i * 0.24
        K.cape("Kelp", (x, 0.66, 0.84), 0.28, 2.7 + 0.3 * math.sin(i * 2.3), "Common" if i % 2 == 0 else "Rare",
               flare=0.45, widen=0.25, curve=0.0, tatter=0.35, teeth=1, thick=0.04, nx=2, ny=6, tilt=0.04 * math.cos(i))
    K.box("Silver", (0, 0.7, 0.84), (2.0, 0.12, 0.16), "Common", bevel=0.04)
    for sx in (1, -1):
        K.disc("Nacre", (sx * 0.85, 0.74, 0.84), 0.16, 0.06, "Rare", n=12)

    # ---------------- belt: heavy silver belt, lock buckle emblem, nacre tassets
    K.piece("Belt")
    K.shell("Silver", 0.1, "Common", hz=0.34, bevel=0.04)
    gate(K, (0, -0.66, 0.0), 0.36, 0.34, "Rare", bars=2, lock=True)
    for x in (-0.62, 0.62):
        K.box("Nacre", (x, -0.65, -0.5), (0.62, 0.12, 0.66), "Common", bevel=0.05, sway=True)
        K.box("Silver", (x, -0.72, -0.82), (0.64, 0.06, 0.07), "Uncommon", bevel=0.02, sway=True)
    K.panel("Teal", (0, -0.6, -0.12), 0.55, 1.1, "Common", flare=0.15, thick=0.05, tatter=0.15, teeth=1, nx=2)
    for sx in (1, -1):
        K.box("Nacre", (sx * 1.12, 0.0, -0.42), (0.14, 0.92, 0.62), "Common", bevel=0.05, sway=True)
    K.box("Nacre", (0, 0.66, -0.45), (1.7, 0.12, 0.62), "Common", bevel=0.05, sway=True)

    # ---------------- shoulders: lobster plates, a claw on the left
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Teal", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        lobster_plates(K, s, 3, ["Common", "Common", "Uncommon"])
        if s == 1:
            claw(K, (0.45, 0.0, 0.95), 1.1, "Rare", rot=(0, 25, 0))
            K.sphere("Glow", (0.5, -0.12, 1.2), 0.06, "Epic", n=6, rings=4)
        else:
            K.taper("Lobster", (-0.45, 0, 0.92), (0.4, 0.5), (0.1, 0.15), 0.35, "Rare", bevel=0.02)
            K.box("Glow", (-0.72, 0.0, 0.5), (0.03, 0.9, 0.03), "Epic", bevel=0.0)

    # ---------------- arms: nacre vambraces, silver gauntlets
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Nacre", 0.1, "Common", hz=0.95, dz=-0.05, bevel=0.07)
        K.band("Silver", 0.38, 0.07, 0.14, "Common")
        K.band("Lobster", -0.12, 0.08, 0.13, "Uncommon")
        K.band("Silver", -0.48, 0.07, 0.14, "Rare")
        K.piece("Glove" + side)
        K.box("Silver", (0, 0, 0.0), (1.12, 1.14, 0.38), "Common", bevel=0.06)
        K.box("Steel", (0, -0.58, -0.08), (0.8, 0.04, 0.1), "Uncommon", bevel=0.01)

    # ---------------- legs: nacre cuisses, greaves with gate knee plates, sabatons
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Nacre", 0.08, "Common", hz=1.0, dz=-0.15, bevel=0.07)
        K.band("Silver", 0.33, 0.06, 0.1, "Uncommon")
        K.piece("Greave" + side)
        K.shell("Nacre", 0.1, "Common", hz=1.0, dz=-0.12, bevel=0.07)
        K.box("Lobster", (0, -0.6, 0.42), (0.7, 0.2, 0.42), "Common", bevel=0.07)
        gate(K, (0, -0.71, 0.42), 0.28, 0.3, "Rare", bars=2, lock=False)
        K.band("Silver", -0.6, 0.06, 0.11, "Uncommon")
        K.piece("Boot" + side)
        K.box("Silver", (0, -0.08, 0.02), (1.16, 1.3, 0.42), "Common", bevel=0.08)
        K.box("Lobster", (0, -0.5, 0.12), (1.0, 0.4, 0.14), "Uncommon", bevel=0.03)


if __name__ == "__main__":
    run(CFG, build)

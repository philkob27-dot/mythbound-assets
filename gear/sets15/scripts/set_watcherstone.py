# Watcherstone (set 5): Heavy, symmetric (solemn), bone white / bronze, emblem a stone eye.
# Stone plates like a statue, moss in the seams, a smooth stone face mask, a green glass eye stone on the chest.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbkit2 import *

CFG = dict(
    id="watcherstone", model="Watcherstone", name="Watcherstone",
    palette={
        "Stone": ((216, 208, 190), "stone"),
        "Darkstone": ((140, 134, 124), "stone"),
        "Bronze": ((178, 124, 62), "metal"),
        "Moss": ((92, 128, 62), "plant"),
        "Cloth": ((70, 94, 66), "cloth"),
        "Eye": ((86, 196, 128), "glass"),
    },
    glow=(110, 255, 160),
)


def stone_eye(K, c, s, rar, glass_rar=None, glow_rar=None, facing=-1):
    """Stone eye: almond lid in bronze, a green glass iris."""
    pts = [(-0.5, 0), (-0.25, 0.22), (0.25, 0.22), (0.5, 0), (0.25, -0.22), (-0.25, -0.22)]
    K.prism("Bronze", c, [(x * s, z * s) for x, z in pts], 0.06, rar)
    K.prism("Darkstone", (c[0], c[1] + facing * 0.03, c[2]), [(x * s * 0.82, z * s * 0.75) for x, z in pts], 0.04, rar)
    K.disc("Eye", (c[0], c[1] + facing * 0.05, c[2]), 0.13 * s, 0.05, glass_rar or rar, n=12)
    if glow_rar:
        K.disc("Glow", (c[0], c[1] + facing * 0.08, c[2]), 0.06 * s, 0.02, glow_rar, n=8)


def build(K):
    # ---------------- head: closed stone helm with a smooth face mask, bronze crest, moss
    K.piece("Helm")
    K.visor_helm("Stone", "Common", out=0.12, bevel=0.1, top_round=True)
    K.box("Stone", (0, -0.7, -0.02), (0.98, 0.1, 1.05), "Common", bevel=0.08)           # smooth mask
    for sx in (1, -1):
        K.box("Darkstone", (sx * 0.22, -0.755, 0.12), (0.22, 0.03, 0.07), "Common", bevel=0.01)
        K.box("Glow", (sx * 0.22, -0.77, 0.12), (0.16, 0.02, 0.04), "Epic", bevel=0.0)
    K.box("Bronze", (0, -0.72, 0.5), (1.06, 0.12, 0.1), "Common", bevel=0.03)
    K.box("Bronze", (0, -0.72, -0.53), (1.06, 0.12, 0.08), "Uncommon", bevel=0.03)
    K.box("Bronze", (0, 0.0, 0.92), (0.16, 1.4, 0.2), "Uncommon", bevel=0.04)            # crest ridge
    K.box("Stone", (0, 0.05, 1.08), (0.1, 1.1, 0.2), "Rare", bevel=0.03)
    for sx in (1, -1):
        K.box("Moss", (sx * 0.62, 0.0, 0.73), (0.14, 1.32, 0.1), "Rare", bevel=0.04)
        K.panel("Moss", (sx * 0.73, 0.4, 0.62), 0.25, 0.45, "Rare", flare=0.0, thick=0.03, tatter=0.15, teeth=2, nx=2)
    stone_eye(K, (0, -0.79, 0.68), 0.5, "Legendary", glow_rar="Legendary")
    for sx in (1, -1):  # side wings of stone like a statue's headdress
        K.taper("Stone", (sx * 0.85, 0.1, 0.25), (0.12, 0.9), (0.12, 0.5), 1.1, "Epic", rot=(0, 0, 0), bevel=0.04)
        K.box("Bronze", (sx * 0.85, 0.1, 0.82), (0.16, 0.6, 0.08), "Epic", bevel=0.02)

    # ---------------- chest: stone breastplate in segments, moss in the seams, the green eye stone
    K.piece("Chest")
    K.shell("Cloth", 0.05, "Common", bevel=0.05)
    K.taper("Stone", (0, -0.02, 0.38), (2.08, 1.24), (2.3, 1.3), 0.92, "Common", bevel=0.08)
    K.taper("Stone", (0, -0.02, -0.45), (1.9, 1.16), (2.04, 1.22), 0.62, "Common", bevel=0.07)
    K.box("Moss", (0, -0.02, -0.11), (2.0, 1.2, 0.07), "Uncommon", bevel=0.02)                # seam
    K.box("Bronze", (0, -0.02, 0.86), (2.34, 1.34, 0.08), "Common", bevel=0.03)
    K.taper("Darkstone", (0, 0.0, 0.98), (1.5, 1.2), (1.3, 1.1), 0.2, "Common", bevel=0.05)     # gorget
    K.disc("Bronze", (0, -0.66, 0.32), 0.36, 0.07, "Common", n=16)
    K.disc("Darkstone", (0, -0.7, 0.32), 0.3, 0.04, "Common", n=16)
    K.sphere("Eye", (0, -0.7, 0.32), (0.22, 0.12, 0.22), "Uncommon", n=12, rings=6)
    K.disc("Glow", (0, -0.83, 0.32), 0.1, 0.02, "Epic", n=10)
    for sx in (1, -1):
        K.box("Moss", (sx * 0.45, -0.66, 0.0), (0.06, 0.04, 0.5), "Rare", rot=(0, sx * 20, 0), bevel=0.01)   # cracks
        K.box("Bronze", (sx * 0.98, -0.02, 0.3), (0.08, 1.32, 1.0), "Uncommon", bevel=0.02)
    # straight solemn cape in the accent cloth, moss trailing at the hem
    K.cape("Cloth", (0, 0.66, 0.85), 1.95, 2.9, "Common", flare=0.35, widen=0.08, curve=0.15, thick=0.07, nx=8)
    K.cape("Moss", (0, 0.64, 0.83), 1.9, 2.98, "Rare", flare=0.35, widen=0.08, curve=0.15, thick=0.05, tatter=0.25, teeth=8, nx=16)
    K.box("Stone", (0, 0.72, 0.84), (2.1, 0.16, 0.2), "Common", bevel=0.05)
    stone_eye(K, (0, 0.82, 0.3), 0.7, "Legendary", glow_rar="Legendary", facing=1)

    # ---------------- belt: bronze belt, emblem, stone tassets on short chains
    K.piece("Belt")
    K.shell("Bronze", 0.09, "Common", hz=0.34, bevel=0.04)
    stone_eye(K, (0, -0.64, 0.0), 0.55, "Rare", glow_rar="Epic")
    for i, x in enumerate((-0.6, 0.0, 0.6)):
        K.box("Stone", (x, -0.64, -0.55), (0.55, 0.12, 0.62), "Common", bevel=0.05, sway=True)
        K.box("Bronze", (x, -0.71, -0.28), (0.57, 0.06, 0.07), "Uncommon", bevel=0.02, sway=True)
    for sx in (1, -1):
        K.box("Stone", (sx * 1.1, 0.0, -0.45), (0.14, 0.9, 0.6), "Common", bevel=0.05, sway=True)
        K.panel("Moss", (sx * 0.6, -0.72, -0.86), 0.3, 0.2, "Rare", flare=0.0, thick=0.03, tatter=0.1, teeth=2, nx=2, ny=1)
    K.box("Stone", (0, 0.64, -0.5), (1.7, 0.12, 0.7), "Common", bevel=0.05, sway=True)

    # ---------------- shoulders: layered stone pauldrons, bronze edges, moss on top (symmetric)
    for s, side in K.sides():
        K.piece("Pauldron" + side)
        K.shell("Cloth", 0.05, "Common", hz=0.95, dz=0.05, bevel=0.05)
        K.taper("Stone", (0.12 * s, 0, 0.62), (1.42, 1.4), (1.06, 1.12), 0.42, "Common", bevel=0.07)
        K.taper("Stone", (0.22 * s, 0, 0.3), (1.38, 1.36), (1.34, 1.34), 0.26, "Common", bevel=0.05)
        K.box("Bronze", (0.22 * s, 0, 0.16), (1.42, 1.4, 0.07), "Uncommon", bevel=0.02)
        K.box("Bronze", (0.12 * s, 0, 0.85), (1.1, 1.16, 0.06), "Uncommon", bevel=0.02)
        K.box("Moss", (0.12 * s, 0, 0.9), (0.9, 0.95, 0.06), "Rare", bevel=0.03)
        K.panel("Moss", (0.92 * s, -0.3, 0.3), 0.2, 0.35, "Rare", flare=0.0, thick=0.03, tatter=0.12, teeth=1, nx=1, ny=2)
        stone_eye(K, (0.22 * s, -0.71, 0.32), 0.42, "Epic")
        K.taper("Stone", (0.3 * s, 0, 1.0), (0.5, 0.5), (0.3, 0.3), 0.26, "Legendary", bevel=0.03)
        K.sphere("Glow", (0.3 * s, 0, 1.18), 0.06, "Legendary", n=8, rings=5)

    # ---------------- arms: stone vambraces with bronze bands, stone gauntlets
    for s, side in K.sides():
        K.piece("Bracer" + side)
        K.shell("Stone", 0.1, "Common", hz=0.95, dz=-0.05, bevel=0.07)
        K.band("Bronze", 0.38, 0.07, 0.14, "Common")
        K.band("Bronze", -0.48, 0.07, 0.14, "Uncommon")
        K.box("Moss", (0.0, -0.62, -0.05), (0.5, 0.03, 0.05), "Rare", bevel=0.01)
        K.box("Glow", (0.0, -0.64, 0.12), (0.4, 0.02, 0.04), "Epic", bevel=0.0)
        K.piece("Glove" + side)
        K.box("Stone", (0, 0, 0.0), (1.12, 1.14, 0.38), "Common", bevel=0.06)
        K.box("Bronze", (0, -0.58, 0.08), (0.7, 0.04, 0.08), "Uncommon", bevel=0.01)

    # ---------------- legs: stone cuisses, greaves with the eye on the knee, stone sabatons
    for s, side in K.sides():
        K.piece("Thigh" + side)
        K.shell("Stone", 0.08, "Common", hz=1.0, dz=-0.15, bevel=0.07)
        K.band("Bronze", 0.33, 0.06, 0.1, "Uncommon")
        K.band("Moss", -0.1, 0.05, 0.09, "Rare")
        K.piece("Greave" + side)
        K.shell("Stone", 0.1, "Common", hz=1.0, dz=-0.12, bevel=0.07)
        K.box("Stone", (0, -0.6, 0.42), (0.7, 0.2, 0.42), "Common", bevel=0.07)          # knee cop
        stone_eye(K, (0, -0.71, 0.42), 0.4, "Rare", glow_rar="Epic")
        K.band("Bronze", -0.6, 0.06, 0.11, "Uncommon")
        K.piece("Boot" + side)
        K.box("Stone", (0, -0.08, 0.02), (1.16, 1.3, 0.42), "Common", bevel=0.08)
        K.box("Bronze", (0, -0.08, 0.2), (1.18, 1.32, 0.06), "Uncommon", bevel=0.02)


if __name__ == "__main__":
    run(CFG, build)

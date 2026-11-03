# Renders the crew outfits on blocky R15 mannequins (for review before the import).
# python3 preview.py [front|back|three]
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix
import crew_kit as K

OUTFITS = {
    "grunt": ["Hood", "Wrap", "Tunic", "Cloak", "Belt", "SleeveL", "SleeveR", "BracerL", "BracerR", "GloveL", "GloveR",
              "TrouserL", "TrouserR", "BootL", "BootR", "FootL", "FootR", "PauldronR"],
    "archer": ["Hood", "Wrap", "Tunic", "Quiver", "Belt", "SleeveL", "SleeveR", "BracerL", "BracerR", "GloveL", "GloveR",
               "TrouserL", "TrouserR", "BootL", "BootR", "FootL", "FootR"],
    "drawer": ["HoodLong", "RobeTop", "RobeBelt", "Satchel", "SleeveL", "SleeveR", "BellSleeveL", "BellSleeveR",
               "RobeSkirtL", "RobeSkirtR", "BootL", "BootR", "FootL", "FootR"],
    "brute": ["Wrap", "BruteTop", "Belt", "PauldronHeavyL", "PauldronHeavyR", "BracerL", "BracerR", "GloveL", "GloveR",
              "TrouserL", "TrouserR", "BootL", "BootR", "FootL", "FootR"],
    "leader": ["Hood", "BoneMask", "Tunic", "CloakLong", "Belt", "PauldronL", "PauldronR", "SleeveL", "SleeveR", "BracerL", "BracerR",
               "GloveL", "GloveR", "TrouserL", "TrouserR", "BootL", "BootR", "FootL", "FootR"],
    "vane": ["VaneMask", "Coat", "SashBelt", "CoatSleeveL", "CoatSleeveR", "CoatCuffL", "CoatCuffR", "GloveL", "GloveR", "CoatTailL", "CoatTailR",
             "TrouserL", "TrouserR", "TallBootL", "TallBootR", "FootL", "FootR"],
    "knight": ["KnightHelm", "Surcoat", "Belt", "PauldronL", "PauldronR", "SleeveL", "SleeveR", "KnightBracerL", "KnightBracerR", "GloveL", "GloveR",
               "TrouserL", "TrouserR", "KnightBootL", "KnightBootR", "FootL", "FootR"],
}


def mannequin(coll, off):
    m = bpy.data.materials.get("Skin") or bpy.data.materials.new("Skin")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.75, 0.48, 0.3, 1)
    d = bpy.data.materials.get("Eye") or bpy.data.materials.new("Eye")
    d.use_nodes = True
    d.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
    for part, (c, s) in K.BODY.items():
        bm = K.g_rbox(tuple(x * 0.99 for x in s), r=0.04, seg=1)
        me = bpy.data.meshes.new("B_" + part)
        bm.to_mesh(me)
        me.materials.append(m)
        ob = bpy.data.objects.new("B_" + part, me)
        ob.location = Vector(c) + off
        coll.objects.link(ob)
    hc = Vector(K.BODY["Head"][0]) + off
    for sx in (-1, 1):
        bm = K.g_rbox((0.1, 0.04, 0.17), r=0.02, seg=1)
        me = bpy.data.meshes.new("eye")
        bm.to_mesh(me)
        me.materials.append(d)
        ob = bpy.data.objects.new("eye", me)
        ob.location = hc + Vector((sx * 0.2, -0.585, 0.05))
        coll.objects.link(ob)


def render(view, names):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 16
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 420 * len(names)
    sc.render.resolution_y = 640
    w = bpy.data.worlds.new("W")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.32, 0.36, 0.42, 1)
    sc.world = w
    for name, rot, e in (("Key", (50, 0, -35), 4.0), ("Fill", (65, 0, 140), 1.5), ("Rim", (35, 0, 170), 2.5)):
        ld = bpy.data.lights.new(name, "SUN")
        ld.energy = e
        ob = bpy.data.objects.new(name, ld)
        ob.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(ob)
    cd = bpy.data.cameras.new("C")
    cd.type = "ORTHO"
    cd.ortho_scale = 4.4 * len(names) * (0.45 if view == "head" else 1.0)
    cam = bpy.data.objects.new("C", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    yaw = {"front": 20, "back": 200, "three": 45, "head": 25}[view]
    cx = (len(names) - 1) * 4.4 / 2
    t = Vector((cx, 0, 4.2 if view == "head" else 2.7))
    yr = math.radians(yaw)
    pr = math.radians(8)
    dvec = Vector((math.sin(yr) * math.cos(pr), -math.cos(yr) * math.cos(pr), math.sin(pr)))
    cam.location = t + dvec * 40
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.clip_end = 200
    sc.render.filepath = os.path.join(K.OUT, f"preview_{view}.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    view = sys.argv[-1] if sys.argv[-1] in ("front", "back", "three", "head") else "front"
    pick = [a for a in sys.argv[1:] if a in OUTFITS] or list(OUTFITS)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    K.build_all()
    coll = bpy.data.collections.new("P")
    bpy.context.scene.collection.children.link(coll)
    for i, name in enumerate(pick):
        off = Vector((i * 4.4, 0, 0))
        mannequin(coll, off)
        K.build_objects(coll, off, only=set(OUTFITS[name]))
    render(view, pick)

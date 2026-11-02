# mbkit2: Blender kit for the 15 Mythbound armor sets (2 November 2026).
#
# Modeling frame (Blender): the character faces -Y, +X is the character's LEFT, +Z is up, 1 unit = 1 stud.
# Roblox frame: X = Blender -x, Y = Blender z, Z = Blender y (the same mapping GearKitSetup expects).
#
# Every primitive goes into a bucket (piece, role, rarity, sway). A bucket becomes one mesh object named
#   Armor_<Model>_<Piece>_<Role>[Sway]_<Rarity>      e.g. Armor_Envoy_Chest_ClothSway_Rare
# Glow buckets are named Armor_<Model>_<Piece>_Glow_<Rarity> (only Epic and Legendary).
# Coordinates passed to the primitives are relative to the centre of the body part the piece attaches to.

import bpy, bmesh, json, math, os, sys, time
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT = os.path.join(HERE, "export")
REVIEW = os.path.join(HERE, "review")

RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]

# Reference R15 body (default blocky R15 part sizes as used by GearMeshes ref), Blender axes (x, y, z).
# Centres are a stacked layout of the default rig; armor is stored relative to them, so only the
# relative fit matters in game (GearFit scales per axis to the player's own part).
BODY = {
    "Head":          ((0.0, 0.0, 4.54), (1.159, 1.161, 1.182)),
    "UpperTorso":    ((0.0, 0.0, 3.15), (1.943, 1.004, 1.698)),
    "LowerTorso":    ((0.0, 0.0, 2.15), (1.991, 1.004, 0.401)),
    "LeftUpperArm":  ((1.472, 0.0, 3.38), (1.001, 1.002, 1.242)),
    "LeftLowerArm":  ((1.472, 0.0, 2.71), (1.001, 1.002, 1.118)),
    "LeftHand":      ((1.472, 0.0, 2.11), (0.984, 1.028, 0.316)),
    "RightUpperArm": ((-1.472, 0.0, 3.38), (1.001, 1.002, 1.242)),
    "RightLowerArm": ((-1.472, 0.0, 2.71), (1.001, 1.002, 1.118)),
    "RightHand":     ((-1.472, 0.0, 2.11), (0.984, 1.028, 0.316)),
    "LeftUpperLeg":  ((0.497, 0.0, 1.38), (0.993, 0.973, 1.363)),
    "LeftLowerLeg":  ((0.497, 0.0, 0.80), (0.993, 0.973, 1.301)),
    "LeftFoot":      ((0.497, 0.0, 0.156), (1.009, 1.001, 0.312)),
    "RightUpperLeg": ((-0.497, 0.0, 1.38), (0.993, 0.973, 1.363)),
    "RightLowerLeg": ((-0.497, 0.0, 0.80), (0.993, 0.973, 1.301)),
    "RightFoot":     ((-0.497, 0.0, 0.156), (1.009, 1.001, 0.312)),
}

# piece -> (slot, R15 part)
PIECES = {
    "Helm": ("Head", "Head"),
    "Chest": ("Chest", "UpperTorso"),
    "Belt": ("Chest", "LowerTorso"),
    "PauldronL": ("Shoulders", "LeftUpperArm"), "PauldronR": ("Shoulders", "RightUpperArm"),
    "BracerL": ("Arms", "LeftLowerArm"), "BracerR": ("Arms", "RightLowerArm"),
    "GloveL": ("Arms", "LeftHand"), "GloveR": ("Arms", "RightHand"),
    "ThighL": ("Legs", "LeftUpperLeg"), "ThighR": ("Legs", "RightUpperLeg"),
    "GreaveL": ("Legs", "LeftLowerLeg"), "GreaveR": ("Legs", "RightLowerLeg"),
    "BootL": ("Legs", "LeftFoot"), "BootR": ("Legs", "RightFoot"),
}
PIECE_ORDER = list(PIECES.keys())

# material kinds -> (metallic, roughness, Roblox material hint)
KINDS = {
    "metal": (1.0, 0.32, "Metal"),
    "cloth": (0.0, 0.88, "Fabric"),
    "leather": (0.0, 0.62, "Leather"),
    "bone": (0.0, 0.55, "SmoothPlastic"),
    "stone": (0.0, 0.92, "Slate"),
    "wood": (0.0, 0.75, "Wood"),
    "pearl": (0.15, 0.25, "SmoothPlastic"),
    "glass": (0.0, 0.08, "Glass"),
    "plant": (0.0, 0.7, "SmoothPlastic"),
    "rope": (0.0, 0.9, "Fabric"),
    "paint": (0.0, 0.45, "SmoothPlastic"),
}


def srgb_to_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


# ---------------------------------------------------------------- primitive generators (local meshes)

def _bm_to_lists(bm):
    bm.verts.ensure_lookup_table()
    verts = [tuple(v.co) for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    faces = [[idx[v] for v in f.verts] for f in bm.faces]
    bm.free()
    return verts, faces


def gen_box(size, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if bevel > 0:
        b = min(bevel, min(size) * 0.45)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, segments=1, affect="EDGES", clamp_overlap=True)
    return _bm_to_lists(bm)


def gen_taper(bot, top, h, shift=(0.0, 0.0), bevel=0.0):
    """Frustum box: bottom rect bot=(w,d) at z=-h/2, top rect top=(w,d) at z=+h/2, top shifted by shift."""
    bm = bmesh.new()
    vs = []
    for (w, d, z, sx, sy) in ((bot[0], bot[1], -h / 2, 0, 0), (top[0], top[1], h / 2, shift[0], shift[1])):
        for (a, b) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new((a * w / 2 + sx, b * d / 2 + sy, z)))
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    for q in f:
        bm.faces.new([vs[i] for i in q])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        b = min(bevel, min(min(bot), min(top), h) * 0.4)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, segments=1, affect="EDGES", clamp_overlap=True)
    return _bm_to_lists(bm)


def gen_cyl(r, h, n=12, r2=None, cap=True):
    r2 = r if r2 is None else r2
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        verts.append((math.cos(a) * r, math.sin(a) * r, -h / 2))
    for i in range(n):
        a = 2 * math.pi * i / n
        verts.append((math.cos(a) * r2, math.sin(a) * r2, h / 2))
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    if cap:
        faces.append(list(range(n - 1, -1, -1)))
        if r2 > 1e-5:
            faces.append(list(range(n, 2 * n)))
    if r2 <= 1e-5:  # cone: collapse top ring
        verts = verts[:n] + [(0, 0, h / 2)]
        faces = [[i, (i + 1) % n, n] for i in range(n)] + [list(range(n - 1, -1, -1))]
    return verts, faces


def gen_sphere(n=10, rings=6):
    verts, faces = [(0, 0, -1)], []
    for r in range(1, rings):
        t = math.pi * r / rings - math.pi / 2
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append((math.cos(t) * math.cos(a), math.cos(t) * math.sin(a), math.sin(t)))
    verts.append((0, 0, 1))
    top = len(verts) - 1
    for i in range(n):
        faces.append([0, 1 + (i + 1) % n, 1 + i])
    for r in range(rings - 2):
        b = 1 + r * n
        for i in range(n):
            j = (i + 1) % n
            faces.append([b + i, b + j, b + n + j, b + n + i])
    b = 1 + (rings - 2) * n
    for i in range(n):
        faces.append([b + i, b + (i + 1) % n, top])
    return verts, faces


def gen_torus(R, r, n=16, m=6, arc=1.0):
    verts, faces = [], []
    closed = arc >= 0.999
    nn = n if closed else n + 1
    for i in range(nn):
        a = 2 * math.pi * arc * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            rr = R + r * math.cos(b)
            verts.append((rr * math.cos(a), rr * math.sin(a), r * math.sin(b)))
    for i in range(n):
        i2 = (i + 1) % nn if closed else i + 1
        for j in range(m):
            j2 = (j + 1) % m
            faces.append([i * m + j, i2 * m + j, i2 * m + j2, i * m + j2])
    if not closed:
        faces.append([j for j in range(m)][::-1])
        faces.append([n * m + j for j in range(m)])
    return verts, faces


def gen_prism(points2d, depth):
    """Extruded polygon in XZ plane (points (x,z)), depth along Y."""
    n = len(points2d)
    verts = [(x, -depth / 2, z) for x, z in points2d] + [(x, depth / 2, z) for x, z in points2d]
    faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, n + i, n + j, j])
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in verts]
    for f in faces:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _bm_to_lists(bm)


def rot_matrix(rot):
    return Euler([math.radians(a) for a in rot], "XYZ").to_matrix().to_4x4()


# ---------------------------------------------------------------- the kit

class Kit:
    def __init__(self, cfg):
        self.cfg = cfg
        self.model = cfg["model"]
        self.palette = cfg["palette"]  # role -> ((r,g,b), kind)
        self.glow_color = cfg.get("glow", (255, 255, 255))
        self.buckets = {}  # (piece, role, rarity, sway) -> [verts, faces, smooth flags]
        self.cur = None
        self.offset = Vector((0, 0, 0))

    # current piece
    def piece(self, name):
        assert name in PIECES, name
        self.cur = name
        return self

    def sides(self):
        return ((1, "L"), (-1, "R"))

    def body(self, piece=None):
        part = PIECES[piece or self.cur][1]
        return BODY[part]

    def _add(self, role, verts, faces, mat, rar, sway, smooth, piece=None):
        piece = piece or self.cur
        assert rar in RARITIES, rar
        if role == "Glow":
            assert rar in ("Epic", "Legendary"), "glow only from Epic"
        else:
            assert role in self.palette, role
        c = Vector(self.body(piece)[0])
        key = (piece, role, rar, bool(sway))
        b = self.buckets.setdefault(key, [[], [], []])
        base = len(b[0])
        M = Matrix.Translation(c) @ mat
        for v in verts:
            b[0].append(tuple(M @ Vector(v)))
        for f in faces:
            b[1].append([base + i for i in f])
            b[2].append(smooth)

    @staticmethod
    def _mat(c, rot=(0, 0, 0), scale=(1, 1, 1)):
        return Matrix.Translation(Vector(c)) @ rot_matrix(rot) @ Matrix.Diagonal((*scale, 1.0))

    # primitives ------------------------------------------------------------
    def box(self, role, c, size, rar="Common", rot=(0, 0, 0), bevel=0.035, sway=False):
        v, f = gen_box(size, bevel)
        self._add(role, v, f, self._mat(c, rot), rar, sway, False)

    def taper(self, role, c, bot, top, h, rar="Common", rot=(0, 0, 0), shift=(0, 0), bevel=0.03, sway=False):
        v, f = gen_taper(bot, top, h, shift, bevel)
        self._add(role, v, f, self._mat(c, rot), rar, sway, False)

    def cyl(self, role, c, r, h, rar="Common", rot=(0, 0, 0), n=12, r2=None, scale=(1, 1, 1), sway=False, smooth=True):
        v, f = gen_cyl(r, h, n, r2)
        self._add(role, v, f, self._mat(c, rot, scale), rar, sway, smooth)

    def sphere(self, role, c, r, rar="Common", rot=(0, 0, 0), n=10, rings=6, sway=False):
        rs = (r, r, r) if isinstance(r, (int, float)) else r
        v, f = gen_sphere(n, rings)
        self._add(role, v, f, self._mat(c, rot, rs), rar, sway, True)

    def torus(self, role, c, R, r, rar="Common", rot=(0, 0, 0), n=16, m=6, arc=1.0, scale=(1, 1, 1), sway=False):
        v, f = gen_torus(R, r, n, m, arc)
        self._add(role, v, f, self._mat(c, rot, scale), rar, sway, True)

    def prism(self, role, c, pts, depth, rar="Common", rot=(0, 0, 0), scale=(1, 1, 1), sway=False):
        v, f = gen_prism(pts, depth)
        self._add(role, v, f, self._mat(c, rot, scale), rar, sway, False)

    def strap(self, role, p1, p2, w, t, rar="Common", sway=False, twist=0.0, bevel=0.02, roundn=0):
        """A bar from p1 to p2 (relative coords), width w (sideways), thickness t."""
        p1, p2 = Vector(p1), Vector(p2)
        d = p2 - p1
        L = d.length
        z = d.normalized()
        ref = Vector((0, 1, 0)) if abs(z.y) < 0.9 else Vector((1, 0, 0))
        x = ref.cross(z).normalized()
        y = z.cross(x)
        R = Matrix((x, y, z)).transposed().to_4x4() @ rot_matrix((0, 0, twist))
        M = Matrix.Translation((p1 + p2) / 2) @ R
        if roundn:
            v, f = gen_cyl(w / 2, L, roundn)
            self._add(role, v, f, M @ Matrix.Diagonal((1, t / w, 1, 1)), rar, sway, True)
        else:
            v, f = gen_box((w, t, L), bevel)
            self._add(role, v, f, M, rar, sway, False)

    def beads(self, role, p1, p2, n, r, rar="Common", sway=True, sag=0.0, nseg=6):
        p1, p2 = Vector(p1), Vector(p2)
        for i in range(n):
            t = i / max(1, n - 1)
            p = p1.lerp(p2, t)
            p.z -= sag * 4 * t * (1 - t)
            self.sphere(role, tuple(p), r, rar, n=nseg, rings=4, sway=sway)

    def rope(self, role, pts, r, rar="Common", sway=False, n=6):
        for a, b in zip(pts[:-1], pts[1:]):
            self.strap(role, a, b, 2 * r, 2 * r, rar, sway, roundn=n)
            self.sphere(role, b, r * 1.02, rar, n=n, rings=4, sway=sway)

    def cape(self, role, top, width, length, rar="Common", flare=0.35, widen=0.25, curve=0.18, tatter=0.0,
             teeth=7, thick=0.06, nx=8, ny=6, tilt=0.0, sway=True, notch=0.0):
        """Cape hanging from top (centre of the top edge, relative), down -Z and back +Y."""
        bm = bmesh.new()
        grid = []
        for j in range(ny + 1):
            row = []
            v = j / ny
            for i in range(nx + 1):
                u = i / nx
                uu = 2 * u - 1
                L = length
                if tatter > 0:
                    k = (u * teeth) % 1.0
                    L = length - tatter * (abs(2 * k - 1))
                if notch > 0:
                    L = L - notch * max(0, 1 - abs(uu) * 3)
                vv = v * L / length
                x = uu * width / 2 * (1 + widen * vv)
                y = flare * vv ** 1.4 - curve * uu * uu * (1 - 0.5 * vv) + tilt * vv
                z = -vv * length
                row.append(bm.verts.new((top[0] + x, top[1] + y, top[2] + z)))
            grid.append(row)
        faces = []
        for j in range(ny):
            for i in range(nx):
                faces.append(bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])))
        bm.normal_update()
        bmesh.ops.solidify(bm, geom=faces, thickness=thick)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        v, f = _bm_to_lists(bm)
        self._add(role, v, f, Matrix.Identity(4), rar, sway, False)

    def panel(self, role, top, width, length, rar="Common", flare=0.1, widen=0.1, curve=0.0, tatter=0.0,
              teeth=4, thick=0.06, face=-1, sway=True, nx=3, ny=3):
        """A hanging panel (tabard, tasset, sash end). face=-1 hangs on the front (flares to -Y), +1 back."""
        bm = bmesh.new()
        grid = []
        for j in range(ny + 1):
            row = []
            v = j / ny
            for i in range(nx + 1):
                u = i / nx
                uu = 2 * u - 1
                L = length
                if tatter > 0:
                    k = (u * teeth) % 1.0
                    L = length - tatter * abs(2 * k - 1)
                vv = v * L / length
                x = uu * width / 2 * (1 + widen * vv)
                y = face * (flare * vv - curve * uu * uu)
                z = -vv * length
                row.append(bm.verts.new((top[0] + x, top[1] + y, top[2] + z)))
            grid.append(row)
        faces = []
        for j in range(ny):
            for i in range(nx):
                faces.append(bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])))
        bm.normal_update()
        bmesh.ops.solidify(bm, geom=faces, thickness=thick)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        v, f = _bm_to_lists(bm)
        self._add(role, v, f, Matrix.Identity(4), rar, sway, False)

    def side_panel(self, role, top, width, length, side, rar="Common", flare=0.12, thick=0.06, sway=True, tatter=0.0):
        """Hanging panel on the left (side=+1) or right (-1) hip, facing outward."""
        bm = bmesh.new()
        grid = []
        nx, ny = 3, 3
        for j in range(ny + 1):
            row = []
            v = j / ny
            for i in range(nx + 1):
                u = i / nx
                uu = 2 * u - 1
                L = length
                if tatter > 0:
                    L = length - tatter * abs(2 * ((u * 3) % 1.0) - 1)
                vv = v * L / length
                row.append(bm.verts.new((top[0] + side * flare * vv, top[1] + uu * width / 2, top[2] - vv * length)))
            grid.append(row)
        faces = []
        for j in range(ny):
            for i in range(nx):
                faces.append(bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])))
        bm.normal_update()
        bmesh.ops.solidify(bm, geom=faces, thickness=thick)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        v, f = _bm_to_lists(bm)
        self._add(role, v, f, Matrix.Identity(4), rar, sway, False)

    # common compound shapes -----------------------------------------------
    def shell(self, role, out=0.08, rar="Common", dz=0.0, hz=None, bevel=0.06, front=0.0, y=0.0):
        """A plate around the current body part, out studs larger on each side."""
        _, s = self.body()
        h = hz if hz is not None else s[2] + 2 * out
        self.box(role, (0, y - front / 2, dz), (s[0] + 2 * out, s[1] + 2 * out + front, h), rar, bevel=bevel)

    def band(self, role, z, h=0.1, out=0.12, rar="Common", bevel=0.03, wx=None, wy=None):
        """A trim band around the current body part at height z (relative)."""
        _, s = self.body()
        self.box(role, (0, 0, z), (wx or s[0] + 2 * out, wy or s[1] + 2 * out, h), rar, bevel=bevel)

    def disc(self, role, c, r, t=0.05, rar="Common", n=16, facing="front", rot=None):
        rr = {"front": (90, 0, 0), "back": (90, 0, 0), "side": (0, 90, 0), "up": (0, 0, 0)}[facing]
        self.cyl(role, c, r, t, rar, rot=rot or rr, n=n, smooth=False)

    def hood(self, role, rar="Common", out=0.1, peak=0.35, back=0.25, drape=0.35, open_w=0.82, trim=None):
        """Hood around the head, open at the front so the face shows."""
        _, s = self.body("Helm")
        w, d, h = s[0] + 2 * out, s[1] + 2 * out, s[2] + out
        t = 0.1
        top_z = s[2] / 2 + out / 2
        self.box(role, (0, 0.03, top_z + t / 2 - 0.02), (w, d + 0.02, t + 0.06), rar, bevel=0.06)          # crown
        for sx in (1, -1):
            self.box(role, (sx * (w / 2 - t / 2), 0.02, -0.02), (t + 0.04, d, h - 0.05), rar, bevel=0.05)    # sides
        self.box(role, (0, d / 2 - t / 2 + 0.02, -0.02), (w, t + 0.04, h - 0.05), rar, bevel=0.05)          # back
        # front cowl lip around the opening
        lip = (w - open_w) / 2
        for sx in (1, -1):
            self.box(trim or role, (sx * (open_w / 2 + lip / 2), -d / 2 + 0.02, -0.05), (lip, 0.08, h - 0.1), rar, bevel=0.03)
        self.box(trim or role, (0, -d / 2 + 0.02, top_z - 0.02), (w, 0.08, 0.14), rar, bevel=0.03)
        if peak > 0:
            self.taper(role, (0, back * 0.6, top_z + t + peak / 2 - 0.03), (w * 0.8, d * 0.75), (0.08, 0.08), peak, rar,
                       shift=(0, back * 0.8), bevel=0.02)
        if drape > 0:  # hood drapes onto the shoulders at the back
            self.taper(role, (0, d / 2 - 0.05, -h / 2 - drape / 2 + 0.05), (w + 0.25, d * 0.6), (w, 0.3), drape, rar, bevel=0.03)

    def visor_helm(self, role, rar="Common", out=0.1, slit_role=None, slit_h=0.1, slit_z=0.08, bevel=0.08, top_round=True):
        _, s = self.body("Helm")
        w, d, h = s[0] + 2 * out, s[1] + 2 * out, s[2] + out * 1.5
        self.box(role, (0, 0, out * 0.25), (w, d, h), rar, bevel=bevel)
        if top_round:
            self.taper(role, (0, 0, h / 2 + 0.1 + out * 0.25 - 0.02), (w, d), (w * 0.7, d * 0.7), 0.2, rar, bevel=0.03)
        if slit_role:
            self.box(slit_role, (0, -d / 2 - 0.005, slit_z), (w * 0.62, 0.04, slit_h), rar, bevel=0.01)

    # ---------------------------------------------------------------- build objects
    def materials(self):
        mats = {}
        for role, (rgb, kind) in list(self.palette.items()) + [("Glow", (self.glow_color, "glow"))]:
            name = f"{self.model}_{role}"
            m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
            m.use_nodes = True
            nt = m.node_tree
            p = nt.nodes.get("Principled BSDF")
            col = [srgb_to_lin(c) for c in rgb] + [1.0]
            p.inputs["Base Color"].default_value = col
            m.diffuse_color = col
            if kind == "glow":
                p.inputs["Emission Color"].default_value = col
                p.inputs["Emission Strength"].default_value = 3.0
                p.inputs["Roughness"].default_value = 0.4
            else:
                met, rough, _ = KINDS[kind]
                p.inputs["Metallic"].default_value = met
                p.inputs["Roughness"].default_value = rough
                if kind == "glass":
                    p.inputs["Transmission Weight"].default_value = 0.6
            mats[role] = m
        return mats

    def objects(self, collection, offset=(0, 0, 0), max_rarity="Legendary", name_prefix=""):
        mats = self.materials()
        lim = RARITIES.index(max_rarity)
        objs = []
        for key in sorted(self.buckets, key=lambda k: (PIECE_ORDER.index(k[0]), k[1], RARITIES.index(k[2]), k[3])):
            piece, role, rar, sway = key
            if RARITIES.index(rar) > lim:
                continue
            verts, faces, smooth = self.buckets[key]
            name = f"{name_prefix}Armor_{self.model}_{piece}_{role}{'Sway' if sway else ''}_{rar}"
            me = bpy.data.meshes.new(name)
            me.from_pydata([tuple(Vector(v) + Vector(offset)) for v in verts], [], faces)
            me.validate()
            me.update()
            for poly, sm in zip(me.polygons, smooth):
                poly.use_smooth = sm
            me.materials.append(mats[role])
            ob = bpy.data.objects.new(name, me)
            collection.objects.link(ob)
            # origin at bbox centre (Roblox uses the bounding box anyway)
            xs = [v.co for v in me.vertices]
            mn = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs)))
            mx = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
            ctr = (mn + mx) / 2
            me.transform(Matrix.Translation(-ctr))
            ob.location = ctr
            ob["mb_key"] = json.dumps([piece, role, rar, sway])
            objs.append(ob)
        return objs


# ---------------------------------------------------------------- scene helpers

def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for d in list(coll):
            coll.remove(d)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def new_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def mannequin(collection, offset=(0, 0, 0), skin=(176, 132, 104)):
    m = bpy.data.materials.new("Mannequin")
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = [srgb_to_lin(c) for c in skin] + [1]
    p.inputs["Roughness"].default_value = 0.7
    dark = bpy.data.materials.new("MannequinEyes")
    dark.use_nodes = True
    dark.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.025, 1)
    off = Vector(offset)
    for part, (c, s) in BODY.items():
        shrink = 0.0
        sz = list(s)
        cc = Vector(c)
        # visible blocky proportions: trim the overlaps a bit so the dummy reads as R15 blocks
        if "UpperLeg" in part:
            sz[2] = 0.9; cc.z = 1.55
        if "LowerLeg" in part:
            sz[2] = 0.85; cc.z = 0.68
        if "UpperArm" in part:
            sz[2] = 0.95; cc.z = 3.52
        if "LowerArm" in part:
            sz[2] = 0.8; cc.z = 2.67
        v, f = gen_box(tuple(x * 0.985 for x in sz), 0.05)
        me = bpy.data.meshes.new("Body_" + part)
        me.from_pydata([tuple(Vector(p) + cc + off) for p in v], [], f)
        me.materials.append(m)
        ob = bpy.data.objects.new("Body_" + part, me)
        collection.objects.link(ob)
    hc = Vector(BODY["Head"][0]) + off
    for sx in (1, -1):
        v, f = gen_box((0.12, 0.04, 0.2), 0.02)
        me = bpy.data.meshes.new("Eye")
        me.from_pydata([tuple(Vector(p) + hc + Vector((sx * 0.2, -0.585, 0.05))) for p in v], [], f)
        me.materials.append(dark)
        ob = bpy.data.objects.new("Body_Eye", me)
        collection.objects.link(ob)


def setup_render(res=(420, 640), samples=20):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    sc.cycles.max_bounces = 4
    sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 2
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
    sc.view_settings.look = "None"
    w = bpy.data.worlds.get("W") or bpy.data.worlds.new("W")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.19, 0.21, 0.25, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    sc.world = w
    # lights
    for name, rot, energy, col in (("Key", (50, 0, -35), 4.0, (1, 0.96, 0.9)), ("Fill", (65, 0, 140), 1.2, (0.8, 0.88, 1.0)),
                                   ("Rim", (35, 0, 170), 2.5, (1, 1, 1))):
        ld = bpy.data.lights.new(name, "SUN")
        ld.energy = energy
        ld.color = col
        ld.angle = math.radians(8)
        ob = bpy.data.objects.new(name, ld)
        ob.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(ob)
    cam_d = bpy.data.cameras.new("Cam")
    cam_d.type = "ORTHO"
    cam = bpy.data.objects.new("Cam", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def aim_camera(cam, target, yaw, pitch=8, dist=30, ortho=7.3):
    t = Vector(target)
    yr, pr = math.radians(yaw), math.radians(pitch)
    # yaw 0 = looking at the front of the character (camera at -Y)
    d = Vector((math.sin(yr) * math.cos(pr), -math.cos(yr) * math.cos(pr), math.sin(pr)))
    cam.location = t + d * dist
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = ortho
    cam.data.clip_end = 200


def render_to(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- export

def roblox_vec(v):
    return (-v[0], v[2], v[1])


def roblox_size(s):
    return (s[0], s[2], s[1])


def tri_count(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def export_set(cfg, K, objs, collection):
    model = cfg["model"]
    os.makedirs(EXPORT, exist_ok=True)
    manifest = {"set": cfg["id"], "model": model, "name": cfg["name"], "glow": list(K.glow_color),
                "axes": "Roblox studs: X = character right, Y = up, -Z = front; centres relative to the body part centre",
                "objects": []}
    entries = {}
    total = 0
    for ob in objs:
        piece, role, rar, sway = json.loads(ob["mb_key"])
        slot, part = PIECES[piece]
        bc, bs = BODY[part]
        me = ob.data
        xs = [Vector(ob.location) + v.co for v in me.vertices]
        mn = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs)))
        mx = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
        ctr = (mn + mx) / 2 - Vector(bc)
        size = mx - mn
        tris = tri_count(me)
        total += tris
        pname = f"{role}{'Sway' if sway else ''}_{rar}"
        if role == "Glow":
            rgb, kind = K.glow_color, "glow"
            met, rough, hint = 0.0, 0.4, "Neon"
        else:
            rgb, kind = K.palette[role]
            met, rough, hint = KINDS[kind]
        rec = {
            "object": ob.name, "entry": f"Armor_{model}_{piece}", "part": pname, "piece": piece, "slot": slot, "attach": part,
            "rarity": rar, "sway": sway, "role": "glow" if role == "Glow" else "solid", "colorRole": role,
            "color": list(rgb), "material": {"kind": kind, "metal": met, "roughness": rough, "roblox": hint},
            "glow": list(K.glow_color) if role == "Glow" else None,
            "center": [round(x, 4) for x in roblox_vec(ctr)], "size": [round(x, 4) for x in roblox_size(size)],
            "bodyCenter": [round(x, 4) for x in roblox_vec(bc)], "bodySize": [round(x, 4) for x in roblox_size(bs)],
            "tris": tris,
        }
        manifest["objects"].append(rec)
        e = entries.setdefault(rec["entry"], {"attach": part, "slot": slot, "ref": rec["bodySize"], "parts": {}, "mn": None, "mx": None})
        e["parts"][pname] = rec
        lmn, lmx = roblox_vec(mn - Vector(bc)), roblox_vec(mx - Vector(bc))
        lo = [min(a, b) for a, b in zip(lmn, lmx)]
        hi = [max(a, b) for a, b in zip(lmn, lmx)]
        e["mn"] = lo if e["mn"] is None else [min(a, b) for a, b in zip(e["mn"], lo)]
        e["mx"] = hi if e["mx"] is None else [max(a, b) for a, b in zip(e["mx"], hi)]
    # triangle budget per rarity
    budget = {}
    for r in RARITIES:
        lim = RARITIES.index(r)
        budget[r] = sum(o["tris"] for o in manifest["objects"] if RARITIES.index(o["rarity"]) <= lim)
    manifest["tris"] = budget
    manifest["largestMesh"] = max((o["tris"], o["object"]) for o in manifest["objects"])
    slots = {}
    for en, e in entries.items():
        slots.setdefault(e["slot"], []).append(en)
    manifest["slots"] = slots
    with open(os.path.join(EXPORT, f"{model}.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    # Luau snippet
    def v3(v):
        return "Vector3.new(%s)" % ", ".join(("%.4f" % x).rstrip("0").rstrip(".") if abs(x) > 1e-9 else "0" for x in v)
    L = [f"-- {cfg['name']} ({model}): GearMeshes entries, generated by gear15/mbkit2.py from the Blender kit.",
         "-- Paste inside the table M of ReplicatedStorage.Shared.data.GearMeshes. Parts with role \"solid\" carry",
         "-- their own colour and material; rarity says from which item rarity the part is shown (see GEARKIT_SOLID_PATCH.luau).",
         f"-- Pieces per slot (Gear.luau models lists): " + "; ".join(f"{s} = {{ {', '.join(chr(34) + n + chr(34) for n in slots[s])} }}" for s in ["Head", "Chest", "Shoulders", "Arms", "Legs"] if s in slots)]
    for en in sorted(entries):
        e = entries[en]
        L.append(f"\t{en} = {{")
        L.append('\t\tkind = "armor",')
        L.append(f'\t\tattach = "{e["attach"]}",')
        L.append(f'\t\tref = {v3(e["ref"])},')
        L.append("\t\tparts = {")
        for pn in sorted(e["parts"], key=lambda n: (RARITIES.index(e["parts"][n]["rarity"]), n)):
            r = e["parts"][pn]
            extra = f'rarity = "{r["rarity"]}"'
            if r["sway"]:
                extra += ", sway = true"
            if r["role"] == "glow":
                L.append(f'\t\t\t{pn} = {{ role = "glow", center = {v3(r["center"])}, size = {v3(r["size"])}, glow = Color3.fromRGB({", ".join(map(str, r["glow"]))}), {extra} }},')
            else:
                L.append(f'\t\t\t{pn} = {{ role = "solid", center = {v3(r["center"])}, size = {v3(r["size"])}, color = Color3.fromRGB({", ".join(map(str, r["color"]))}), material = "{r["material"]["roblox"]}", {extra} }},')
        L.append("\t\t},")
        L.append("\t\tpoints = {")
        L.append("\t\t},")
        L.append(f'\t\tmin = {v3(e["mn"])},')
        L.append(f'\t\tmax = {v3(e["mx"])},')
        L.append("\t},")
    with open(os.path.join(EXPORT, f"{model}_GearMeshes.luau"), "w") as f:
        f.write("\n".join(L) + "\n")
    # FBX
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=os.path.join(EXPORT, f"{model}.fbx"), use_selection=True, object_types={"MESH"},
                             mesh_smooth_type="FACE", apply_unit_scale=True, axis_forward="-Z", axis_up="Y",
                             use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False)
    return manifest


def sheet(cfg, K, manifest, cam):
    """Render the review sheet: Legendary front, back, three-quarter, and Common front."""
    from PIL import Image, ImageDraw, ImageFont
    sc = bpy.context.scene
    paths = []
    tmp = os.path.join(REVIEW, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    tgt = (0, 0, 3.0)
    coll = bpy.data.collections["Gear"]
    views = [("front", 0, "Legendary"), ("back", 180, "Legendary"), ("3q", -40, "Legendary"), ("3qb", 140, "Legendary"),
             ("common", -25, "Common")]
    for tag, yaw, rar in views:
        lim = RARITIES.index(rar)
        for ob in coll.objects:
            r = json.loads(ob["mb_key"])[2]
            ob.hide_render = RARITIES.index(r) > lim
        aim_camera(cam, tgt, yaw)
        p = os.path.join(tmp, f"{cfg['id']}_{tag}.png")
        render_to(p)
        paths.append((p, f"{rar} {tag}"))
    for ob in coll.objects:
        ob.hide_render = False
    ims = [Image.open(p).convert("RGB") for p, _ in paths]
    w, h = ims[0].size
    out = Image.new("RGB", (w * len(ims), h + 70), (24, 26, 30))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except Exception:
        font = small = ImageFont.load_default()
    d = ImageDraw.Draw(out)
    for i, (im, (_, label)) in enumerate(zip(ims, paths)):
        out.paste(im, (i * w, 70))
        d.text((i * w + 10, 76), label, fill=(220, 220, 220), font=small)
    t = manifest["tris"]
    d.text((12, 8), f"{cfg['name']}  ({cfg['model']})", fill=(240, 230, 200), font=font)
    d.text((12, 40), f"tris  Common {t['Common']}  Rare {t['Rare']}  Epic {t['Epic']}  Legendary {t['Legendary']}   largest mesh {manifest['largestMesh'][0]}   meshes {len(manifest['objects'])}",
           fill=(190, 190, 190), font=small)
    sp = os.path.join(REVIEW, f"{cfg['model']}_review.png")
    out.save(sp)
    return sp


def run(cfg, build, render=True):
    t0 = time.time()
    clear_scene()
    K = Kit(cfg)
    build(K)
    gear = new_collection("Gear")
    objs = K.objects(gear)
    manifest = export_set(cfg, K, objs, gear)
    body = new_collection("Mannequin")
    mannequin(body)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(EXPORT, f"{cfg['model']}.blend"), compress=True)
    t = manifest["tris"]
    print(f"[{cfg['model']}] meshes {len(objs)} tris {t} largest {manifest['largestMesh']}")
    if render:
        cam = setup_render()
        sp = sheet(cfg, K, manifest, cam)
        print("sheet", sp)
    print(f"[{cfg['model']}] done in {time.time() - t0:.1f}s")
    return K, manifest

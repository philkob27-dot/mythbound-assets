# Crew kit: 3D clothing for the human enemies of Mythbound (Thrallbinders, their villain, knights for the
# portraits). 3 November 2026. Our own meshes, built procedurally in Blender (bpy as a module).
#
# Frame (Blender): character faces -Y, +X is the character's LEFT, +Z up, 1 unit = 1 stud.
# Every piece is modelled around ONE R15 body part (the default blocky R15, sizes below) with coordinates
# relative to that part's centre, so in Roblox it is welded to that part and moves with its joint.
# Every (piece, role) becomes one mesh object named  CK_<Piece>__<Role>  ; roles are coloured in Roblox
# (Cloth, Cloth2, Lining, Leather, Metal, Bone, Glow, Fur, Wood, Fletch, Paint, Gold), so one mesh set
# gives every crew variant.  Two marker cubes (CK_RefA at the origin, CK_RefB at z=10) let the Studio
# setup script find the importer's offset and scale.
#
# Run: python3 crew_kit.py            -> out/CrewKit.glb, out/CrewKit.json, out/preview_*.png

import bpy, bmesh, json, math, os, sys, random
from mathutils import Vector, Matrix, Euler, noise

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# default blocky R15 (measured in Studio, 3 Nov): Blender (x wide, y deep, z tall), centres of a stacked rig
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

# preview colours per role (Roblox recolours them per variant)
ROLES = {
    "Cloth": ((40, 38, 46), 0.0, 0.9), "Cloth2": ((70, 66, 74), 0.0, 0.9), "Lining": ((110, 26, 32), 0.0, 0.85),
    "Leather": ((78, 54, 40), 0.0, 0.6), "Metal": ((120, 124, 132), 0.9, 0.35), "Bone": ((226, 218, 196), 0.0, 0.5),
    "Glow": ((110, 255, 160), 0.0, 0.4), "Fur": ((92, 80, 70), 0.0, 1.0), "Wood": ((112, 80, 52), 0.0, 0.7),
    "Fletch": ((200, 190, 170), 0.0, 0.9), "Paint": ((150, 24, 30), 0.0, 0.5), "Gold": ((214, 170, 80), 0.9, 0.3),
}

PIECES = {}   # piece -> attach part
BUCKETS = {}  # (piece, role) -> bmesh


def bm_for(piece, role):
    key = (piece, role)
    if key not in BUCKETS:
        BUCKETS[key] = bmesh.new()
    return BUCKETS[key]


def merge(dst, src, M):
    """Append bmesh src into dst transformed by M."""
    src.transform(M) if False else None
    vmap = {}
    for v in src.verts:
        vmap[v] = dst.verts.new(M @ v.co)
    for f in src.faces:
        try:
            nf = dst.faces.new([vmap[v] for v in f.verts])
            nf.smooth = f.smooth
        except ValueError:
            pass
    src.free()


def mat(c=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    return Matrix.Translation(Vector(c)) @ Euler([math.radians(a) for a in rot], "XYZ").to_matrix().to_4x4() @ Matrix.Diagonal((*scale, 1.0))


class P:
    """Context: current piece and its body part."""
    piece = None
    part = None

    @staticmethod
    def set(piece, part):
        P.piece, P.part = piece, part
        PIECES[piece] = part

    @staticmethod
    def size():
        return Vector(BODY[P.part][1])


def put(role, bm, M=Matrix.Identity(4), smooth=True):
    for f in bm.faces:
        f.smooth = smooth
    merge(bm_for(P.piece, role), bm, M)


# ------------------------------------------------------------------ shape generators (return bmesh)

def g_rbox(size, r=0.08, seg=3, bot=(1, 1), top=(1, 1), shift=(0, 0), bulge=0.0):
    """Rounded box. bot/top scale the bottom/top faces (flare), shift moves the top, bulge puffs the sides."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        t = v.co.z + 0.5
        sx = bot[0] + (top[0] - bot[0]) * t
        sy = bot[1] + (top[1] - bot[1]) * t
        v.co = Vector((v.co.x * size[0] * sx + shift[0] * t, v.co.y * size[1] * sy + shift[1] * t, v.co.z * size[2]))
    rr = min(r, min(size) * 0.45)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=rr, segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
    if bulge:
        bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=1, use_grid_fill=True)
        for v in bm.verts:
            k = 1 - (2 * v.co.z / size[2]) ** 2
            v.co.x *= 1 + bulge * max(0, k)
            v.co.y *= 1 + bulge * max(0, k)
    return bm


def g_cyl(r, h, n=16, r2=None, cap=True, rx=1.0, ry=1.0):
    r2 = r if r2 is None else r2
    bm = bmesh.new()
    bot = [bm.verts.new((math.cos(2 * math.pi * i / n) * r * rx, math.sin(2 * math.pi * i / n) * r * ry, -h / 2)) for i in range(n)]
    top = [bm.verts.new((math.cos(2 * math.pi * i / n) * r2 * rx, math.sin(2 * math.pi * i / n) * r2 * ry, h / 2)) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    if cap:
        bm.faces.new(list(reversed(bot)))
        bm.faces.new(top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def g_sphere(r, seg=16, rings=10):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    rs = (r, r, r) if isinstance(r, (int, float)) else r
    for v in bm.verts:
        v.co = Vector((v.co.x * rs[0], v.co.y * rs[1], v.co.z * rs[2]))
    return bm


def g_torus(R, r, n=20, m=8, arc=1.0, a0=0.0):
    bm = bmesh.new()
    closed = arc >= 0.999
    nn = n if closed else n + 1
    rings = []
    for i in range(nn):
        a = a0 + 2 * math.pi * arc * i / n
        ring = []
        for j in range(m):
            b = 2 * math.pi * j / m
            rr = R + r * math.cos(b)
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), r * math.sin(b))))
        rings.append(ring)
    for i in range(n):
        i2 = (i + 1) % nn if closed else i + 1
        for j in range(m):
            j2 = (j + 1) % m
            bm.faces.new((rings[i][j], rings[i2][j], rings[i2][j2], rings[i][j2]))
    if not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def g_sheet(fn, nu, nv, thick=0.05):
    """A cloth sheet: fn(u, v) -> Vector, u,v in 0..1, solidified (offset to the outside of the fn normal)."""
    bm = bmesh.new()
    grid = [[bm.verts.new(fn(i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
    faces = []
    for j in range(nv):
        for i in range(nu):
            faces.append(bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])))
    bm.normal_update()
    bmesh.ops.solidify(bm, geom=faces, thickness=thick)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def g_tube(fn, nu, nv, closed_u=True, thick=0.05, cap=False):
    """A tube surface fn(u, v) (u around, v along), solidified."""
    bm = bmesh.new()
    cols = nu if closed_u else nu + 1
    grid = [[bm.verts.new(fn(i / nu, j / nv)) for i in range(cols)] for j in range(nv + 1)]
    faces = []
    for j in range(nv):
        for i in range(nu):
            i2 = (i + 1) % cols if closed_u else i + 1
            faces.append(bm.faces.new((grid[j][i], grid[j][i2], grid[j + 1][i2], grid[j + 1][i])))
    bm.normal_update()
    if thick:
        bmesh.ops.solidify(bm, geom=faces, thickness=thick)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def g_prism(pts, depth):
    bm = bmesh.new()
    n = len(pts)
    a = [bm.verts.new((x, -depth / 2, z)) for x, z in pts]
    b = [bm.verts.new((x, depth / 2, z)) for x, z in pts]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def strap(role, p1, p2, w, t, smooth=False, round_=False):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    z = d.normalized()
    ref = Vector((0, 1, 0)) if abs(z.y) < 0.9 else Vector((1, 0, 0))
    x = ref.cross(z).normalized()
    y = z.cross(x)
    R = Matrix((x, y, z)).transposed().to_4x4()
    M = Matrix.Translation((p1 + p2) / 2) @ R
    if round_:
        put(role, g_cyl(w / 2, d.length, 8, ry=t / w), M, True)
    else:
        put(role, g_rbox((w, t, d.length), r=min(w, t) * 0.3, seg=1), M, smooth)


def sweep(role, pts, r, n=8, closed=False, ry_=None):
    """A smooth tube along a polyline of Vectors (radius r, flattened to ry_ across if given)."""
    bm = bmesh.new()
    rings = []
    N = len(pts)
    for i, p in enumerate(pts):
        a = pts[(i - 1) % N] if (closed or i > 0) else pts[0]
        b = pts[(i + 1) % N] if (closed or i < N - 1) else pts[-1]
        t = (b - a).normalized()
        ref = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
        x = ref.cross(t).normalized()
        y = t.cross(x)
        ring = []
        for k in range(n):
            ang = 2 * math.pi * k / n
            ring.append(bm.verts.new(p + x * math.cos(ang) * r + y * math.sin(ang) * (ry_ or r)))
        rings.append(ring)
    segs = N if closed else N - 1
    for i in range(segs):
        r1, r2 = rings[i], rings[(i + 1) % N]
        for k in range(n):
            k2 = (k + 1) % n
            bm.faces.new((r1[k], r1[k2], r2[k2], r2[k]))
    if not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put(role, bm, smooth=True)


def wrap_band(role, z, h, rx, ry, out=0.0, thick=0.05, n=24, tilt=0.0, c=(0, 0)):
    """A band hugging a rounded rectangle cross-section (a belt, a strap round a limb)."""
    def fn(u, v):
        a = 2 * math.pi * u
        # superellipse for blocky limbs
        ca, sa = math.cos(a), math.sin(a)
        px = (abs(ca) ** 0.3) * (1 if ca >= 0 else -1) * (rx + out)
        py = (abs(sa) ** 0.3) * (1 if sa >= 0 else -1) * (ry + out)
        return Vector((c[0] + px, c[1] + py, z - h / 2 + h * v + tilt * px))
    put(role, g_tube(fn, n, 1, True, thick), smooth=True)


def shell(role, rx, ry, z0, z1, n=28, nv=4, flare=0.0, bulge=0.0, ex=2.4, thick=0.05, top_in=0.0, c=(0, 0), front=0.0, fold=0.0, seed=0):
    """A sleeve / trouser / tunic shell: superellipse cross-section (ex: 2 = ellipse, higher = boxier),
    z0 bottom .. z1 top, flare widens the bottom, bulge puffs the middle, top_in narrows the top edge,
    fold adds soft cloth folds."""
    rnd = random.Random(seed)
    phase = [rnd.random() * 6.28 for _ in range(4)]

    def fn(u, v):
        a = 2 * math.pi * u
        ca, sa = math.cos(a), math.sin(a)
        e = 2.0 / ex
        px = (abs(ca) ** e) * (1 if ca >= 0 else -1)
        py = (abs(sa) ** e) * (1 if sa >= 0 else -1)
        k = 1 + flare * (1 - v) ** 1.5 + bulge * math.sin(math.pi * v) - top_in * v ** 3
        if fold:
            k += fold * (math.sin(a * 5 + phase[0]) * 0.6 + math.sin(a * 3 + phase[1]) * 0.4) * (1 - v) ** 1.2
        z = z0 + (z1 - z0) * v
        yy = py * ry * k
        if front and py < 0:
            yy -= front * (-py)
        return Vector((c[0] + px * rx * k, c[1] + yy, z))
    put(role, g_tube(fn, n, nv, True, thick), smooth=True)


# ------------------------------------------------------------------ pieces

def head_size():
    return Vector(BODY["Head"][1])


def hood(piece, peak=0.55, long_drape=0.0, cloth="Cloth", lining="Lining", trim=None, rune=True, tall=0.0):
    """A deep soft hood. The face opening shows the face (our face decals); the tip droops back.
    long_drape: a back drape that falls onto the shoulders."""
    P.set(piece, "Head")
    s = head_size()
    rx, ry, rz = s.x / 2 + 0.15, s.y / 2 + 0.15, s.z / 2 + 0.16
    cy, cz = 0.06, 0.07
    nu, nv = 40, 24

    def sq(t, e):
        return math.copysign(abs(t) ** e, t)

    def surf(u, v, inset=0.0):
        # superquadric round the blocky head: u around (0 = front), v from below the jaw (0) to the crown (1)
        th = 2 * math.pi * u
        ph = -0.55 * math.pi / 2 + v * (0.55 * math.pi / 2 + math.pi / 2)
        cp, sp = math.cos(ph), math.sin(ph)
        x = sq(math.sin(th), 0.35) * sq(cp, 0.6 if sp < 0 else 0.5) * rx
        y = -sq(math.cos(th), 0.35) * sq(cp, 0.6 if sp < 0 else 0.5) * ry
        z = sq(sp, 0.6 if sp < 0 else 0.5) * rz + tall * max(0, sp) ** 2
        low = max(0.0, -sp)
        # cowl: the lower part widens over the shoulders and pulls back
        x *= 1 + 0.3 * low ** 1.2
        y = y * (1 + 0.22 * low ** 1.2) + 0.1 * low
        back = max(0.0, -math.cos(th))
        top = max(0.0, sp) ** 3
        z += peak * 0.42 * top * (0.35 + 0.65 * back)
        y += peak * 0.85 * top * back
        f = 0.015 * math.sin(th * 7 + v * 3) * (1 - top)
        return Vector((x * (1 + f), cy + y * (1 + f), cz + z))

    bm = bmesh.new()
    grid = [[bm.verts.new(surf(i / nu, j / nv)) for i in range(nu)] for j in range(nv + 1)]
    faces = []
    for j in range(nv):
        for i in range(nu):
            i2 = (i + 1) % nu
            c = (grid[j][i].co + grid[j][i2].co + grid[j + 1][i2].co + grid[j + 1][i].co) / 4
            # the face opening: an oval round the face (eyes and mouth free), only on the front
            if c.y < -0.1 and ((c.x / 0.45) ** 2 + ((c.z - (cz - 0.1)) / 0.47) ** 2) < 1:
                continue
            faces.append(bm.faces.new((grid[j][i], grid[j][i2], grid[j + 1][i2], grid[j + 1][i])))
    # crown cap
    topv = bm.verts.new(surf(0.5, 1.0) + Vector((0, 0, 0.0)))
    for i in range(nu):
        i2 = (i + 1) % nu
        faces.append(bm.faces.new((grid[nv][i], grid[nv][i2], topv)))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.004)
    bm.normal_update()
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.07)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put(cloth, bm)
    # lining: an inner rim round the face opening (reads as the hood's darker inside)
    def rim(u, v):
        a = (u - 0.5) * 2 * math.pi * 0.98
        w = 0.47 + 0.05 * math.cos(a)
        return Vector((math.sin(a) * w, -ry - 0.0 + cy + 0.10 + 0.06 * (1 - math.cos(a)) * 0.5 * 0 - 0.02 + v * 0.08, cz + 0.02 + math.cos(a) * 0.52))
    # simple rim tube following the opening
    pts = []
    N = 26
    for k in range(N + 1):
        a = -math.pi * 0.92 + 2 * math.pi * 0.92 * k / N
        x = math.sin(a) * 0.45
        z = cz - 0.1 + math.cos(a) * 0.47
        y = -ry + cy + 0.02 + 0.1 * (abs(math.sin(a)) ** 3)
        pts.append(Vector((x, y, z)))
    sweep(lining, pts, 0.055, 8, ry_=0.035)
    if trim:
        sweep(trim, [p + Vector((0, -0.035, 0)) for p in pts], 0.022, 6)
    if rune:
        # the crew mark on the brow of the hood: a ring cut by a line (the binding ring)
        put("Glow", g_torus(0.085, 0.016, 16, 6), mat((0, -ry + cy + 0.02, 0.74), (90 - 25, 0, 0)))
        strap("Glow", (0, -ry + cy + 0.0, 0.62), (0, -ry + cy + 0.06, 0.86), 0.025, 0.02)
    if long_drape > 0:
        # a drape down the back onto the shoulders
        def dr(u, v):
            x = (u - 0.5) * (1.25 + 0.5 * v)
            y = ry + cy - 0.05 + 0.18 * v + 0.06 * math.cos((u - 0.5) * math.pi) - 0.1 * (u - 0.5) ** 2
            z = cz - 0.25 - v * long_drape
            return Vector((x, y, z))
        put(cloth, g_sheet(dr, 8, 5, 0.06))


def face_wrap(piece, role="Cloth2", knot=True):
    """A cloth wrapped over the nose and mouth, the eyes free."""
    P.set(piece, "Head")
    s = head_size()
    rx, ry = s.x / 2 + 0.05, s.y / 2 + 0.06

    def fn(u, v):
        a = math.pi * (-0.62 + 1.24 * u)  # front arc
        x = math.sin(a) * rx
        y = -math.cos(a) * ry
        dip = 0.06 * math.cos(a) ** 2  # a soft V under the nose
        z = -0.52 + v * (0.42 - dip) + 0.02 * math.sin(a * 6) * (1 - v)
        return Vector((x, y, z))
    put(role, g_sheet(fn, 18, 3, 0.05))
    # folds
    for k, z in enumerate((-0.18, -0.32)):
        def fb(u, v, z=z):
            a = math.pi * (-0.6 + 1.2 * u)
            return Vector((math.sin(a) * (rx + 0.03), -math.cos(a) * (ry + 0.03), z + 0.025 * v))
        put(role, g_sheet(fb, 16, 1, 0.025))
    if knot:
        put(role, g_sphere((0.12, 0.09, 0.1), 10, 6), mat((0.0, ry + 0.02, -0.25)))
        for sx in (-1, 1):
            strap(role, (0.03 * sx, ry + 0.05, -0.28), (0.12 * sx, ry + 0.12, -0.7), 0.12, 0.03)


def bone_mask(piece):
    """The officers' mask: a carved bone face with a rune line, eye holes glowing."""
    P.set(piece, "Head")
    s = head_size()
    rx, ry = s.x / 2 + 0.04, s.y / 2 + 0.05
    holes = [(-0.21, 0.07), (0.21, 0.07)]

    def fn(u, v):
        a = math.pi * (-0.42 + 0.84 * u)
        x = math.sin(a) * rx
        y = -math.cos(a) * ry - 0.05 * math.cos(a) ** 4 * (1 - abs(v - 0.55) * 1.2)
        z = -0.56 + v * 1.0
        # brow ridge and cheek bones
        y -= 0.04 * math.exp(-((z - 0.2) / 0.06) ** 2) * math.cos(a) ** 2
        y -= 0.03 * math.exp(-((z + 0.1) / 0.1) ** 2) * (abs(math.sin(a)) * 2)
        # chin narrows
        x *= 1 - 0.25 * max(0, -z - 0.25) / 0.3
        return Vector((x, y, z))
    bm = bmesh.new()
    nu, nv = 22, 18
    grid = [[bm.verts.new(fn(i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            c = (grid[j][i].co + grid[j + 1][i + 1].co) / 2
            if any(((c.x - hx) / 0.11) ** 2 + ((c.z - hz) / 0.065) ** 2 < 1 for hx, hz in holes):
                continue
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bm.normal_update()
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.06)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put("Bone", bm)
    # glowing eyes behind the holes, and the rune line down the forehead
    for hx, hz in holes:
        put("Glow", g_sphere((0.085, 0.02, 0.045), 10, 6), mat((hx, -ry + 0.02, hz)))
    strap("Glow", (0, -ry - 0.075, 0.44), (0, -ry - 0.085, 0.22), 0.03, 0.02)
    put("Glow", g_torus(0.06, 0.012, 14, 5), mat((0, -ry - 0.08, 0.33), (90, 0, 0)))
    # three teeth notches painted on the mouth
    for k in range(-2, 3):
        strap("Paint", (k * 0.06, -ry - 0.06, -0.3), (k * 0.06, -ry - 0.06, -0.38), 0.022, 0.015)


def porcelain_mask(piece):
    """Vane's half mask: smooth white porcelain over the eyes, one crimson line under the left eye."""
    P.set(piece, "Head")
    s = head_size()
    rx, ry = s.x / 2 + 0.035, s.y / 2 + 0.045
    holes = [(-0.2, 0.06), (0.2, 0.06)]

    def fn(u, v):
        a = math.pi * (-0.46 + 0.92 * u)
        x = math.sin(a) * rx
        z = -0.12 + v * 0.48
        y = -math.cos(a) * ry - 0.035 * math.exp(-((z - 0.2) / 0.07) ** 2) * math.cos(a) ** 2
        # the lower edge sweeps up at the sides like wings
        return Vector((x, y, z + 0.1 * abs(math.sin(a)) ** 2 * (1 - v)))
    bm = bmesh.new()
    nu, nv = 24, 10
    grid = [[bm.verts.new(fn(i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            c = (grid[j][i].co + grid[j + 1][i + 1].co) / 2
            if any(((c.x - hx) / 0.1) ** 2 + ((c.z - hz) / 0.06) ** 2 < 1 for hx, hz in holes):
                continue
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bm.normal_update()
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.045)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put("Bone", bm)
    # crimson tear line under her left eye (+x), gold edge on the brow
    strap("Paint", (0.21, -ry - 0.05, -0.01), (0.25, -ry - 0.045, -0.2), 0.03, 0.015)
    pts = [Vector((math.sin(math.pi * (-0.44 + 0.88 * k / 14)) * (rx + 0.01), -math.cos(math.pi * (-0.44 + 0.88 * k / 14)) * (ry + 0.01) - 0.02, 0.36 + 0.02 * abs(math.sin(math.pi * (-0.44 + 0.88 * k / 14))))) for k in range(15)]
    for a_, b_ in zip(pts[:-1], pts[1:]):
        strap("Gold", a_, b_, 0.035, 0.03, round_=True)


def tunic(piece, kind="crew"):
    """UpperTorso: a fitted tunic with a collar, crossbelt and the crew mark. kind: crew | robe | coat | brute | knight"""
    P.set(piece, "UpperTorso")
    s = Vector(BODY["UpperTorso"][1])
    rx, ry = s.x / 2 + 0.04, s.y / 2 + 0.05
    h2 = s.z / 2
    shell("Cloth", rx, ry, -h2 - 0.04, h2 + 0.03, n=32, nv=5, flare=0.05, bulge=0.02, ex=6.0, thick=0.05, top_in=0.05, seed=3, fold=0.006)
    # shoulder tops closed (a yoke)
    put("Cloth", g_rbox((s.x + 0.06, s.y + 0.1, 0.12), r=0.05, seg=2), mat((0, 0, h2 + 0.02)))
    if kind in ("crew", "brute"):
        # V collar in lining colour
        put("Lining", g_prism([(-0.36, 0.0), (0.36, 0.0), (0.0, -0.55)], 0.04), mat((0, -ry - 0.015, h2 - 0.01)))
        put("Cloth2", g_torus(0.42, 0.07, 20, 8, arc=0.5, a0=math.pi), mat((0, 0.05, h2 + 0.06), scale=(1.15, 0.8, 1)))
        # crossbelt right shoulder (-x) to left hip (+x), front and back
        strap("Leather", (-0.72, -ry - 0.04, h2 - 0.02), (0.82, -ry - 0.04, -h2 + 0.08), 0.2, 0.05)
        strap("Leather", (-0.72, ry + 0.04, h2 - 0.02), (0.82, ry + 0.04, -h2 + 0.08), 0.2, 0.05)
        put("Metal", g_rbox((0.16, 0.05, 0.2), r=0.03, seg=1), mat((0.05, -ry - 0.08, 0.02), (0, -45, 0)))
        # the crew mark on the left chest: the binding ring
        put("Glow", g_torus(0.13, 0.024, 18, 6), mat((0.48, -ry - 0.03, 0.32), (90, 0, 0)))
        strap("Glow", (0.48, -ry - 0.035, 0.12), (0.48, -ry - 0.035, 0.52), 0.035, 0.025)
    if kind == "robe":
        # long front panel with rune lines, a sash
        put("Cloth2", g_rbox((0.6, 0.06, s.z + 0.02), r=0.03, seg=2), mat((0, -ry - 0.02, 0)))
        for sx in (-1, 1):
            strap("Glow", (sx * 0.3, -ry - 0.06, h2 - 0.05), (sx * 0.3, -ry - 0.06, -h2 + 0.05), 0.035, 0.02)
        put("Glow", g_torus(0.14, 0.025, 18, 6), mat((0, -ry - 0.07, 0.2), (90, 0, 0)))
        strap("Glow", (0, -ry - 0.075, 0.0), (0, -ry - 0.075, 0.4), 0.035, 0.025)
        put("Cloth2", g_torus(0.42, 0.08, 20, 8, arc=0.5, a0=math.pi), mat((0, 0.05, h2 + 0.06), scale=(1.15, 0.8, 1)))
        # satchel strap
        strap("Leather", (0.72, -ry - 0.03, h2 - 0.02), (-0.82, -ry - 0.03, -h2 + 0.05), 0.12, 0.04)
        strap("Leather", (0.72, ry + 0.03, h2 - 0.02), (-0.82, ry + 0.03, -h2 + 0.05), 0.12, 0.04)
    if kind == "coat":
        # Vane's coat: high standing collar, double row of silver buttons, piping
        shell("Cloth", 0.5, 0.38, h2 - 0.02, h2 + 0.32, n=24, nv=2, ex=2.2, thick=0.05, flare=0.12, c=(0, 0.04))
        put("Lining", g_rbox((0.5, 0.05, 0.3), r=0.02, seg=1), mat((0, -0.36, h2 + 0.14)))
        for sx in (-1, 1):
            strap("Gold", (sx * 0.14, -ry - 0.03, h2), (sx * 0.14, -ry - 0.03, -h2), 0.035, 0.02)
            for k in range(4):
                put("Gold", g_sphere(0.045, 8, 6), mat((sx * 0.26, -ry - 0.05, h2 - 0.25 - k * 0.36)))
        put("Lining", g_rbox((0.24, 0.05, s.z), r=0.02, seg=1), mat((0, -ry - 0.01, 0)))
        # epaulettes
        for sx in (-1, 1):
            put("Cloth2", g_rbox((0.62, 0.62, 0.08), r=0.04, seg=2), mat((sx * 0.72, 0, h2 + 0.08), (0, sx * 8, 0)))
            strap("Gold", (sx * 0.42, -0.31, h2 + 0.12), (sx * 1.02, -0.31, h2 + 0.06), 0.04, 0.03, round_=True)
        # Ashfall pin: a dragon tear in crimson
        put("Paint", g_sphere((0.07, 0.03, 0.1), 10, 6), mat((-0.5, -ry - 0.05, 0.42)))
    if kind == "brute":
        # fur mantle around the neck and shoulders
        rng = random.Random(7)
        for k in range(26):
            a = math.pi * 2 * k / 26
            x, y = math.cos(a) * 0.82, math.sin(a) * 0.55
            r = 0.2 + 0.07 * rng.random()
            put("Fur", g_sphere((r * 1.25, r, r * 0.85), 10, 7), mat((x, y + 0.06, h2 + 0.06 + 0.05 * rng.random())))
    if kind == "knight":
        # surcoat over mail: tabard front and back in Cloth2 with a gold trim, mail collar
        for sy in (-1, 1):
            put("Cloth2", g_rbox((1.3, 0.05, s.z + 0.05), r=0.03, seg=2), mat((0, sy * (ry + 0.02), -0.02)))
            strap("Gold", (-0.65, sy * (ry + 0.05), h2 - 0.02), (0.65, sy * (ry + 0.05), h2 - 0.02), 0.06, 0.03)
        put("Metal", g_torus(0.48, 0.1, 22, 8), mat((0, 0.03, h2 + 0.05), scale=(1.2, 0.85, 1)))
        # the Knights' emblem: a lance crossing a wing (gold)
        strap("Gold", (-0.22, -ry - 0.06, -0.3), (0.22, -ry - 0.06, 0.45), 0.06, 0.03)
        put("Gold", g_prism([(0, 0), (0.32, 0.18), (0.38, 0.0), (0.3, -0.12), (0.05, -0.08)], 0.03), mat((0.02, -ry - 0.06, 0.05)))


def cloak(piece, length=2.3, width=2.25, lining=True, mantle=True, split=True, tatter=0.0, cloth="Cloth"):
    """A cloak from the shoulders down the back, flaring away from the legs. In two halves (split) so the
    legs show through the slit when walking."""
    P.set(piece, "UpperTorso")
    s = Vector(BODY["UpperTorso"][1])
    top = s.z / 2 + 0.05
    ry = s.y / 2 + 0.1
    halves = ((-1, 0.0), (1, 0.0)) if split else ((0, 0),)
    for side, _ in halves:
        def fn(u, v, side=side):
            if split:
                uu = (u * 0.5 + (0.5 if side > 0 else 0.0)) * 2 - 1  # -1..1 across the whole cloak
            else:
                uu = 2 * u - 1
            L = length - (tatter * abs(math.sin(uu * 9.0)) if tatter else 0.0)
            vv = v
            x = uu * width / 2 * (1 + 0.22 * vv)
            if split:
                x += side * 0.04 * vv
            # wrap round the shoulders at the top, hang straight lower
            wrap = (1 - vv) ** 3
            y = ry + 0.55 * vv ** 1.3 - 0.45 * wrap * uu * uu + 0.04 * math.sin(uu * 7 + vv * 2) * vv
            z = top - vv * L
            return Vector((x, y, z))
        bm = g_sheet(fn, 8 if split else 14, 10, 0.06)
        put(cloth, bm)
        if lining:
            def fl(u, v, side=side):
                p = fn(u, v, side)
                return p + Vector((0, -0.045, 0))
            put("Lining", g_sheet(fl, 8 if split else 14, 10, 0.02))
    if mantle:
        # a short shoulder mantle over the top of the cloak, round the neck
        def mn(u, v):
            a = math.pi * (-0.15 + 1.3 * u)  # from the left front, round the back, to the right front
            rx_, ry_ = 1.08 + 0.12 * v, 0.62 + 0.14 * v
            x = math.cos(a) * rx_
            y = math.sin(a) * ry_ + 0.05
            z = top + 0.1 - v * 0.62 - 0.05 * math.sin(a * 6) * v
            return Vector((x, y, z))
        put(cloth, g_sheet(mn, 22, 4, 0.06))
        # clasp on the chest
        put("Metal", g_torus(0.08, 0.025, 12, 6), mat((0.0, -0.58, top - 0.12), (90, 0, 0)))


def quiver(piece):
    P.set(piece, "UpperTorso")
    s = Vector(BODY["UpperTorso"][1])
    ry = s.y / 2
    M = mat((0.25, ry + 0.3, 0.05), (0, -25, 0))
    put("Leather", g_cyl(0.2, 1.55, 14, r2=0.24), M)
    put("Metal", g_cyl(0.255, 0.07, 14), M @ mat((0, 0, 0.7)))
    put("Metal", g_cyl(0.21, 0.06, 14), M @ mat((0, 0, -0.74)))
    rng = random.Random(4)
    for k in range(7):
        a = rng.random() * 6.28
        r = rng.random() * 0.12
        base = M @ Vector((math.cos(a) * r, math.sin(a) * r, 0.6))
        tip = M @ Vector((math.cos(a) * r * 1.4, math.sin(a) * r * 1.4, 1.05 + rng.random() * 0.12))
        strap("Wood", base, tip, 0.035, 0.035, round_=True)
        d = (tip - base).normalized()
        put("Fletch", g_prism([(0, 0), (0.07, 0.04), (0.06, 0.2), (0, 0.16)], 0.012), Matrix.Translation(tip - d * 0.22) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4())
    strap("Leather", (0.72, -ry - 0.05, s.z / 2 - 0.02), (-0.82, -ry - 0.05, -s.z / 2 + 0.1), 0.14, 0.04)


def belt(piece, flaps=True, pouches=True, sash=False, robe_top=False, cloth="Cloth"):
    P.set(piece, "LowerTorso")
    s = Vector(BODY["LowerTorso"][1])
    rx, ry = s.x / 2 + 0.05, s.y / 2 + 0.06
    shell(cloth, rx - 0.01, ry - 0.01, -0.3, 0.22, n=28, nv=2, ex=6.0, thick=0.05)
    wrap_band("Leather", 0.02, 0.2, rx, ry, out=0.03, thick=0.05, n=32)
    put("Metal", g_rbox((0.24, 0.05, 0.22), r=0.03, seg=1), mat((0, -ry - 0.08, 0.02)))
    put("Glow", g_torus(0.055, 0.014, 12, 5), mat((0, -ry - 0.11, 0.02), (90, 0, 0)))
    if pouches:
        for sx, sz in ((1, 0.3), (-1, 0.24)):
            put("Leather", g_rbox((0.12, 0.26, sz), r=0.04, seg=2), mat((sx * (rx + 0.08), -0.15, -0.06)))
            put("Leather", g_rbox((0.14, 0.28, 0.07), r=0.02, seg=1), mat((sx * (rx + 0.09), -0.15, 0.08)))
    if flaps:
        # short front and back flaps, flared forward so a stepping leg does not cut through
        for sy, L in ((-1, 0.62), (1, 0.75)):
            def fn(u, v, sy=sy, L=L):
                x = (u - 0.5) * 0.62 * (1 + 0.15 * v)
                y = sy * (ry + 0.05 + 0.22 * v ** 1.2)
                return Vector((x, y, -0.05 - v * L))
            put(cloth, g_sheet(fn, 3, 4, 0.05))
    if sash:
        # Vane's crimson sash, knotted on the left hip with two tails
        wrap_band("Lining", 0.0, 0.26, rx, ry, out=0.06, thick=0.04, n=32)
        put("Lining", g_sphere((0.12, 0.1, 0.12), 10, 6), mat((rx + 0.05, -0.2, 0.0)))
        for k, L in ((0, 0.9), (1, 0.7)):
            strap("Lining", (rx + 0.06, -0.22 + k * 0.1, -0.05), (rx + 0.12 + k * 0.03, -0.25 + k * 0.12, -0.05 - L), 0.16, 0.03)


def skirt_half(piece, side, length=1.6, cloth="Cloth", trim=None, slit_back=False):
    """A robe/coat skirt panel round one upper leg (moves with that leg, so walking never cuts through)."""
    part = ("Left" if side > 0 else "Right") + "UpperLeg"
    P.set(piece, part)
    s = Vector(BODY[part][1])
    top = s.z / 2 + 0.15
    rx, ry = s.x / 2 + 0.07, s.y / 2 + 0.1

    def fn(u, v):
        a = 2 * math.pi * u
        ca, sa = math.cos(a), math.sin(a)
        e = 2.0 / 2.6
        px = (abs(ca) ** e) * (1 if ca >= 0 else -1)
        py = (abs(sa) ** e) * (1 if sa >= 0 else -1)
        k = 1 + 0.45 * v ** 1.2
        x = px * rx * k + side * 0.06 * v
        y = py * ry * k + 0.08 * v
        f = 0.02 * math.sin(a * 6 + side) * v
        return Vector((x * (1 + f), y * (1 + f), top - v * length))
    put(cloth, g_tube(fn, 28, 6, True, 0.05), smooth=True)
    if trim:
        def tr(u, v):
            p = fn(u, 1.0)
            return Vector((p.x * 1.02, p.y * 1.02, p.z + v * 0.1))
        put(trim, g_tube(tr, 28, 1, True, 0.03))


def sleeve(piece, side, kind="crew"):
    part = ("Left" if side > 0 else "Right") + "UpperArm"
    P.set(piece, part)
    s = Vector(BODY[part][1])
    rx, ry = s.x / 2 + 0.05, s.y / 2 + 0.05
    h2 = s.z / 2
    shell("Cloth", rx, ry, -h2 - 0.02, h2 + 0.02, n=24, nv=4, flare=0.04, bulge=0.03, ex=6.0, thick=0.045, seed=int(side + 5), fold=0.008)
    put("Cloth", g_rbox((s.x + 0.1, s.y + 0.1, 0.1), r=0.045, seg=2), mat((0, 0, h2 + 0.01)))
    if kind == "crew":
        wrap_band("Cloth2", -h2 + 0.06, 0.12, rx, ry, out=0.02, thick=0.04)
        # leather strap round the arm with the crew mark
        wrap_band("Leather", 0.08, 0.12, rx, ry, out=0.03, thick=0.035)
    if kind == "coat":
        wrap_band("Gold", -h2 + 0.08, 0.05, rx, ry, out=0.03, thick=0.02)


def pauldron(piece, side, heavy=False, rune=True):
    part = ("Left" if side > 0 else "Right") + "UpperArm"
    P.set(piece, part)
    s = Vector(BODY[part][1])
    h2 = s.z / 2
    n = 3 if heavy else 2
    for k in range(n):
        w = 1.28 - k * 0.1 + (0.12 if heavy else 0)
        put("Metal", g_rbox((w, 1.2 - k * 0.06 + (0.1 if heavy else 0), 0.16), r=0.07, seg=3, bot=(1.04, 1.04), top=(0.94, 0.94)),
            mat((side * (0.06 + k * 0.05), 0, h2 + 0.12 - k * 0.2), (0, side * (12 + k * 10), 0)))
        put("Leather", g_rbox((w - 0.02, 1.16 - k * 0.06, 0.04), r=0.02, seg=1), mat((side * (0.06 + k * 0.05), 0, h2 + 0.03 - k * 0.2), (0, side * (12 + k * 10), 0)))
    if heavy:
        for k in range(3):
            put("Metal", g_cyl(0.07, 0.3, 8, r2=0.0), mat((side * (0.25 + k * 0.17) + 0.0, -0.25 + k * 0.25, h2 + 0.32 - k * 0.02), (0, side * 20, 0)))
    if rune:
        put("Glow", g_torus(0.1, 0.02, 14, 5), mat((side * 0.3, -0.52, h2 + 0.1), (90, 0, side * 0)))


def bracer(piece, side, kind="crew"):
    part = ("Left" if side > 0 else "Right") + "LowerArm"
    P.set(piece, part)
    s = Vector(BODY[part][1])
    rx, ry = s.x / 2 + 0.05, s.y / 2 + 0.05
    h2 = s.z / 2
    if kind == "bell":
        # a wide rune drawer's sleeve that hangs open over the hand
        shell("Cloth", rx, ry, -h2 - 0.25, h2 + 0.02, n=24, nv=4, flare=0.35, ex=3.0, thick=0.045, seed=9, fold=0.02)
        wrap_band("Glow", -h2 - 0.2, 0.04, rx * 1.5, ry * 1.5, out=0.0, thick=0.02)
        return
    if kind == "coat":
        shell("Cloth", rx, ry, -h2 - 0.04, h2 + 0.02, n=32, nv=3, ex=6.0, thick=0.045, flare=0.08)
        shell("Cloth2", rx + 0.04, ry + 0.04, -h2 - 0.06, -h2 + 0.22, n=32, nv=1, ex=6.0, thick=0.04, flare=0.06)
        wrap_band("Gold", -h2 + 0.2, 0.04, rx + 0.06, ry + 0.06, thick=0.02)
        for k in range(2):
            put("Gold", g_sphere(0.04, 8, 6), mat((side * 0.0 + (k - 0.5) * 0.2, -ry - 0.1, -h2 + 0.08)))
        return
    shell("Cloth", rx - 0.01, ry - 0.01, -h2 + 0.0, h2 + 0.02, n=32, nv=3, ex=6.0, thick=0.04)
    # leather bracer over the forearm, laced
    shell("Leather", rx + 0.02, ry + 0.02, -h2 - 0.02, 0.15, n=32, nv=2, ex=6.0, thick=0.05, flare=0.06)
    for z in (-0.35, -0.05):
        wrap_band("Metal" if kind == "knight" else "Leather", z, 0.06, rx + 0.04, ry + 0.04, thick=0.025)
    if kind == "knight":
        put("Metal", g_rbox((0.12, 0.9, 0.62), r=0.05, seg=2), mat((side * (rx + 0.06), 0, -0.17)))


def glove(piece, side):
    part = ("Left" if side > 0 else "Right") + "Hand"
    P.set(piece, part)
    s = Vector(BODY[part][1])
    put("Leather", g_rbox((s.x + 0.08, s.y + 0.08, s.z + 0.06), r=0.09, seg=3), mat((0, 0, -0.01)))
    put("Leather", g_rbox((s.x + 0.16, s.y + 0.16, 0.12), r=0.04, seg=2, bot=(1.0, 1.0), top=(1.08, 1.08)), mat((0, 0, s.z / 2 + 0.03)))


def trouser(piece, side, baggy=0.04):
    part = ("Left" if side > 0 else "Right") + "UpperLeg"
    P.set(piece, part)
    s = Vector(BODY[part][1])
    rx, ry = s.x / 2 + 0.04, s.y / 2 + 0.04
    h2 = s.z / 2
    shell("Cloth2", rx, ry, -h2 - 0.02, h2 + 0.06, n=24, nv=4, bulge=baggy, ex=6.0, thick=0.045, seed=int(side + 11), fold=0.01)


def boot(piece, side, tall=False, kind="crew"):
    part = ("Left" if side > 0 else "Right") + "LowerLeg"
    P.set(piece, part)
    s = Vector(BODY[part][1])
    rx, ry = s.x / 2 + 0.06, s.y / 2 + 0.06
    h2 = s.z / 2
    top = h2 + (0.12 if tall else -0.15)
    shell("Leather", rx, ry, -h2 - 0.02, top, n=32, nv=3, ex=6.0, thick=0.05, flare=0.04, top_in=-0.08)
    # folded cuff
    shell("Leather", rx + 0.05, ry + 0.05, top - 0.2, top + 0.02, n=32, nv=1, ex=6.0, thick=0.05, flare=-0.03)
    if kind == "crew":
        # cloth wraps round the shin
        for k in range(3):
            wrap_band("Cloth2", -0.25 + k * 0.2, 0.09, rx + 0.02, ry + 0.02, thick=0.025, tilt=0.12 * (1 if k % 2 else -1))
        if not tall:
            shell("Cloth2", rx - 0.02, ry - 0.02, top - 0.05, h2 + 0.02, n=32, nv=1, ex=6.0, thick=0.03)
    if kind == "coat":
        put("Gold", g_rbox((0.18, 0.05, 0.12), r=0.02, seg=1), mat((side * 0.25, -ry - 0.05, top - 0.35)))
        wrap_band("Leather", top - 0.35, 0.07, rx + 0.02, ry + 0.02, thick=0.025)
    if kind == "knight":
        put("Metal", g_rbox((0.7, 0.18, 1.0), r=0.08, seg=3, bot=(0.95, 1), top=(1.05, 1)), mat((0, -ry - 0.04, 0.0)))
        put("Metal", g_sphere((0.22, 0.12, 0.18), 10, 6), mat((0, -ry - 0.06, h2 + 0.02)))


def boot_foot(piece, side):
    part = ("Left" if side > 0 else "Right") + "Foot"
    P.set(piece, part)
    s = Vector(BODY[part][1])
    put("Leather", g_rbox((s.x + 0.1, s.y + 0.26, s.z + 0.08), r=0.12, seg=3, bot=(1, 1), top=(0.96, 0.9)), mat((0, -0.1, 0.02)))
    put("Leather", g_rbox((s.x + 0.12, s.y + 0.3, 0.07), r=0.03, seg=1), mat((0, -0.11, -s.z / 2 - 0.0)))


def satchel(piece):
    P.set(piece, "LowerTorso")
    s = Vector(BODY["LowerTorso"][1])
    put("Leather", g_rbox((0.5, 0.2, 0.45), r=0.06, seg=2), mat((-(s.x / 2 + 0.12), -0.1, -0.25), (0, 0, 8)))
    put("Leather", g_rbox((0.52, 0.22, 0.12), r=0.03, seg=1), mat((-(s.x / 2 + 0.12), -0.12, -0.05), (0, 0, 8)))
    # chalk sticks and a brush poking out
    for k in range(3):
        strap("Bone", (-(s.x / 2 + 0.02) - k * 0.08, -0.1, -0.05), (-(s.x / 2 + 0.02) - k * 0.08, -0.1 - 0.02 * k, 0.15 + 0.03 * k), 0.05, 0.05, round_=True)
    put("Glow", g_sphere(0.04, 8, 6), mat((-(s.x / 2 + 0.02), -0.1, 0.17)))


def knight_helm(piece):
    P.set(piece, "Head")
    s = head_size()
    rx, ry, rz = s.x / 2 + 0.12, s.y / 2 + 0.12, s.z / 2 + 0.1
    bm = g_rbox((rx * 2, ry * 2, rz * 2), r=0.35, seg=4)
    # open face: drop front faces in the face window
    rem = [f for f in bm.faces if f.calc_center_median().y < -ry * 0.6 and abs(f.calc_center_median().x) < 0.4 and -0.42 < f.calc_center_median().z < 0.32]
    bmesh.ops.delete(bm, geom=rem, context="FACES")
    put("Metal", bm, mat((0, 0.0, 0.08)))
    put("Gold", g_torus(rx * 0.98, 0.04, 28, 6), mat((0, 0, 0.28), scale=(1, ry / rx, 1)))
    # nose guard and a plume
    put("Metal", g_rbox((0.1, 0.08, 0.5), r=0.03, seg=1), mat((0, -ry - 0.03, 0.05)))
    put("Lining", g_rbox((0.12, 1.0, 0.35), r=0.1, seg=3, bot=(1, 0.8), top=(1, 1.1)), mat((0, 0.15, rz + 0.25)))


# ------------------------------------------------------------------ the catalogue

def build_all():
    hood("Hood", peak=0.55)
    hood("HoodLong", peak=0.85, long_drape=0.55, tall=0.06)
    face_wrap("Wrap")
    bone_mask("BoneMask")
    porcelain_mask("VaneMask")
    knight_helm("KnightHelm")
    tunic("Tunic", "crew")
    tunic("RobeTop", "robe")
    tunic("Coat", "coat")
    tunic("BruteTop", "brute")
    tunic("Surcoat", "knight")
    cloak("Cloak", length=2.25)
    cloak("CloakLong", length=3.0, width=2.4, tatter=0.18)
    cloak("Mantle", length=0.0, lining=False, mantle=True, split=False) if False else None
    quiver("Quiver")
    belt("Belt")
    belt("SashBelt", flaps=False, pouches=False, sash=True)
    belt("RobeBelt", flaps=False, pouches=True)
    satchel("Satchel")
    for side, t in ((1, "L"), (-1, "R")):
        sleeve("Sleeve" + t, side)
        sleeve("CoatSleeve" + t, side, "coat")
        pauldron("Pauldron" + t, side, rune=True)
        pauldron("PauldronHeavy" + t, side, heavy=True, rune=False)
        bracer("Bracer" + t, side)
        bracer("BellSleeve" + t, side, "bell")
        bracer("KnightBracer" + t, side, "knight")
        bracer("CoatCuff" + t, side, "coat")
        glove("Glove" + t, side)
        trouser("Trouser" + t, side)
        boot("Boot" + t, side)
        boot("TallBoot" + t, side, tall=True, kind="coat")
        boot("KnightBoot" + t, side, tall=True, kind="knight")
        boot_foot("Foot" + t, side)
        skirt_half("RobeSkirt" + t, side, length=1.75, trim="Glow")
        skirt_half("CoatTail" + t, side, length=1.55, trim="Gold")


# ------------------------------------------------------------------ objects, export, preview

def make_materials():
    mats = {}
    for role, (rgb, met, rough) in ROLES.items():
        m = bpy.data.materials.new("CK_" + role)
        m.use_nodes = True
        p = m.node_tree.nodes["Principled BSDF"]
        col = [((c / 255) / 12.92 if c / 255 <= 0.04045 else ((c / 255 + 0.055) / 1.055) ** 2.4) for c in rgb] + [1]
        p.inputs["Base Color"].default_value = col
        p.inputs["Metallic"].default_value = met
        p.inputs["Roughness"].default_value = rough
        if role == "Glow":
            p.inputs["Emission Color"].default_value = col
            p.inputs["Emission Strength"].default_value = 4.0
        mats[role] = m
    return mats


def build_objects(coll, offset=Vector((0, 0, 0)), only=None):
    mats = make_materials() if not bpy.data.materials.get("CK_Cloth") else {r: bpy.data.materials["CK_" + r] for r in ROLES}
    objs = []
    for (piece, role), bm in sorted(BUCKETS.items()):
        if only and piece not in only:
            continue
        part = PIECES[piece]
        c = Vector(BODY[part][0])
        me = bpy.data.meshes.new(f"CK_{piece}__{role}")
        bm2 = bm.copy()
        bmesh.ops.remove_doubles(bm2, verts=bm2.verts, dist=0.0005)
        bm2.to_mesh(me)
        bm2.free()
        me.materials.append(mats[role])
        ob = bpy.data.objects.new(me.name, me)
        ob.location = c + offset
        coll.objects.link(ob)
        objs.append(ob)
    return objs


def manifest():
    m = {"axes": "Blender: -Y front, +X character left, Z up. Roblox: X = -bx, Y = bz, Z = by", "pieces": {}, "body": {k: {"center": v[0], "size": v[1]} for k, v in BODY.items()}}
    for (piece, role), bm in BUCKETS.items():
        e = m["pieces"].setdefault(piece, {"attach": PIECES[piece], "roles": []})
        e["roles"].append(role)
    tris = {}
    for (piece, role), bm in BUCKETS.items():
        tris[piece] = tris.get(piece, 0) + sum(len(f.verts) - 2 for f in bm.faces)
    m["tris"] = tris
    return m


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build_all()
    coll = bpy.data.collections.new("CrewKit")
    bpy.context.scene.collection.children.link(coll)
    objs = build_objects(coll)
    # reference markers
    for name, loc in (("CK_RefA", (0, 0, 0)), ("CK_RefB", (0, 0, 10)), ("CK_RefC", (10, 0, 0)), ("CK_RefD", (0, -10, 0))):
        me = bpy.data.meshes.new(name)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=0.1)
        bm.to_mesh(me)
        ob = bpy.data.objects.new(name, me)
        ob.location = loc
        coll.objects.link(ob)
    with open(os.path.join(OUT, "CrewKit.json"), "w") as f:
        json.dump(manifest(), f, indent=1)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "CrewKit.glb"), export_format="GLB", use_selection=False, export_apply=True)
    print("pieces", len(PIECES), "objects", len(objs))

"""Small Blender (bpy) toolkit for toy-like, outlined 3D story shorts.

Everything is built from primitives in code: materials, inverted-hull
outlines, stick-limbed round-headed characters, text props, lights, camera.
"""
import math
import random

import addon_utils
import bmesh
import bpy
from mathutils import Matrix, Vector

FPS = 24
FONTS = {
    "bold": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "black": "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "regular": "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    "hand": "/usr/share/fonts/truetype/crosextra/Carlito-BoldItalic.ttf",
}
_mats = {}
_fonts = {}
SHOT = {"frames": 48, "seed": 0}  # set by render.py for each shot


# ----------------------------------------------------------------- scene
def reset(width=720, height=1280, samples=5):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable("cycles")
    _mats.clear()
    _fonts.clear()
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.render.resolution_x, s.render.resolution_y = width, height
    s.render.fps = FPS
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.compression = 15
    s.render.use_persistent_data = True
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.cycles.use_adaptive_sampling = False
    s.cycles.denoising_quality = "FAST"
    # direct light only: indirect bounces add little to this flat look but double the cost
    s.cycles.max_bounces = 0
    s.cycles.diffuse_bounces = 0
    s.cycles.glossy_bounces = 0
    s.cycles.use_light_tree = False
    s.cycles.transparent_max_bounces = 12
    s.cycles.caustics_reflective = False
    s.cycles.caustics_refractive = False
    s.view_settings.view_transform = "Standard"
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "BEZIER"
    return s


def col(hexstr):
    """'#rrggbb' (sRGB) -> linear RGBA tuple."""
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def mat(hexstr, rough=0.85, emit=0.0):
    key = (hexstr, rough, emit)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(hexstr)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col(hexstr)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = col(hexstr)
        b.inputs["Emission Strength"].default_value = emit
    _mats[key] = m
    return m


def outline_mat():
    """Black hull material: only the faces pointing away from the camera show."""
    if "OUTLINE" in _mats:
        return _mats["OUTLINE"]
    m = bpy.data.materials.new("OUTLINE")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.012, 0.01, 0.014, 1)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nt.links.new(geo.outputs["Backfacing"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    _mats["OUTLINE"] = m
    return m


def add_outline(ob, th=0.012):
    """Inverted-hull outline as a camera-only copy of the mesh pushed out along
    its normals, so it costs nothing for shadow and bounce rays."""
    ol = bpy.data.objects.new(ob.name + "_ol", ob.data)
    bpy.context.scene.collection.objects.link(ol)
    ol.parent = ob
    for md in ob.modifiers:
        if md.type == "BEVEL":
            b = ol.modifiers.new("bevel", "BEVEL")
            b.width, b.segments = md.width, md.segments
    d = ol.modifiers.new("push", "DISPLACE")
    d.strength = th
    d.mid_level = 0.0
    for slot in ol.material_slots:
        slot.link = "OBJECT"
        slot.material = outline_mat()
    ol.visible_shadow = ol.visible_diffuse = ol.visible_glossy = False
    ol.visible_transmission = ol.visible_volume_scatter = False
    return ob


def world(hexstr, strength=1.0):
    w = bpy.data.worlds.new("world")
    bpy.context.scene.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = col(hexstr)
    bg.inputs["Strength"].default_value = strength
    return w


def sky(top, horizon, strength=1.0):
    """Vertical gradient background: `horizon` colour low, `top` colour overhead."""
    w = world(top, strength * 1.15)
    nt = w.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.05
    mr.inputs["From Max"].default_value = 0.55
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.inputs["Color1"].default_value = col(horizon)
    mix.inputs["Color2"].default_value = col(top)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs[0], mix.inputs["Fac"])
    nt.links.new(mix.outputs[0], nt.nodes["Background"].inputs["Color"])
    return w


def sun(strength=3.0, rot=(50, 0, 30), hexstr="#fff4e0", angle=8):
    d = bpy.data.lights.new("sun", "SUN")
    d.energy = strength
    d.color = col(hexstr)[:3]
    d.angle = math.radians(angle)
    ob = bpy.data.objects.new("sun", d)
    ob.rotation_euler = [math.radians(a) for a in rot]
    bpy.context.scene.collection.objects.link(ob)
    return ob


def lamp(loc, power=200, hexstr="#ffd58a", radius=0.15):
    d = bpy.data.lights.new("lamp", "POINT")
    d.energy = power
    d.color = col(hexstr)[:3]
    d.shadow_soft_size = radius
    ob = bpy.data.objects.new("lamp", d)
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ------------------------------------------------------------ primitives
def _finish(name, bm, material, loc, rot, scale, ol, smooth, bevel, parent):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    ob.scale = scale
    if material is not None:
        me.materials.append(material if not isinstance(material, str) else mat(material))
    bpy.context.scene.collection.objects.link(ob)
    if bevel:
        b = ob.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = 3
    if ol:
        add_outline(ob, ol if isinstance(ol, float) else 0.012)
    if parent is not None:
        ob.parent = parent
    return ob


def box(size, loc=(0, 0, 0), m=None, rot=(0, 0, 0), ol=True, bevel=0.0, parent=None, name="box"):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    return _finish(name, bm, m, loc, rot, (1, 1, 1), ol, False, bevel, parent)


def sph(r, loc=(0, 0, 0), m=None, scale=(1, 1, 1), rot=(0, 0, 0), ol=True, parent=None, name="sph", seg=32):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    return _finish(name, bm, m, loc, rot, (1, 1, 1), ol, True, 0, parent)


def cyl(r, h, loc=(0, 0, 0), m=None, r2=None, rot=(0, 0, 0), ol=True, parent=None, name="cyl", seg=24, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r,
                          radius2=r if r2 is None else r2, depth=h)
    ob = _finish(name, bm, m, loc, rot, (1, 1, 1), ol, smooth, 0, parent)
    if smooth:
        ob.data.set_sharp_from_angle(angle=math.radians(50))
    return ob


def torus(R, r, loc=(0, 0, 0), m=None, rot=(0, 0, 0), parent=None, name="torus"):
    bm = bmesh.new()
    n, k = 28, 8
    rings = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ring = []
        for j in range(k):
            b = 2 * math.pi * j / k
            rr = R + r * math.cos(b)
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), r * math.sin(b))))
        rings.append(ring)
    for i in range(n):
        for j in range(k):
            bm.faces.new((rings[i][j], rings[(i + 1) % n][j],
                          rings[(i + 1) % n][(j + 1) % k], rings[i][(j + 1) % k]))
    return _finish(name, bm, m, loc, rot, (1, 1, 1), False, True, 0, parent)


def text(body, size, loc=(0, 0, 0), m="#111111", rot=(90, 0, 0), font="bold", align="CENTER",
         extrude=0.002, parent=None, name="text", spacing=1.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.extrude = extrude
    cu.space_line = spacing
    if font not in _fonts:
        _fonts[font] = bpy.data.fonts.load(FONTS[font])
    cu.font = _fonts[font]
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    cu.materials.append(mat(m) if isinstance(m, str) else m)
    ob.visible_shadow = False
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def empty(loc=(0, 0, 0), parent=None, name="empty"):
    ob = bpy.data.objects.new(name, None)
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def arc(radius, a0, a1, th, loc, m="#111111", rot=(0, 0, 0), parent=None, n=10):
    """Thin tube along a circular arc in the local XZ plane (mouths, handles)."""
    cu = bpy.data.curves.new("arc", "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(n)
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        sp.points[i].co = (radius * math.cos(a), 0, radius * math.sin(a), 1)
    cu.bevel_depth = th
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    cu.materials.append(mat(m))
    ob = bpy.data.objects.new("arc", cu)
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def limb(parent, start, target, r=0.02, m="#141414"):
    """Thin cylinder from `start` (in parent space) that stretches to `target`."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=r, radius2=r, depth=1.0)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-90), 3, "X"))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0.5, 0))
    ob = _finish("limb", bm, mat(m), start, (0, 0, 0), (1, 1, 1), False, True, 0, parent)
    c = ob.constraints.new("STRETCH_TO")
    c.target = target
    c.rest_length = 1.0
    c.volume = "NO_VOLUME"
    return ob


# -------------------------------------------------------------- animation
def key(ob, frame, loc=None, rot=None, scale=None):
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert("location", frame=frame)
    if rot is not None:
        ob.rotation_euler = [math.radians(a) for a in rot]
        ob.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        ob.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3
        ob.keyframe_insert("scale", frame=frame)


def show(ob, frame, visible=True):
    """Keyframe render visibility for an object and its children."""
    for o in [ob, *ob.children_recursive]:
        o.hide_render = not visible
        o.keyframe_insert("hide_render", frame=frame)


def bob(ob, n, amp=0.02, period=14, axis=2, phase=0):
    base = list(ob.location)
    f, i = 1, phase
    while f <= n + period:
        p = list(base)
        p[axis] += amp if i % 2 else 0
        key(ob, f, loc=p)
        f += period // 2
        i += 1


def wipe(parent, x0, x1, y, h, z, colr, f0, f1):
    """Paper-coloured cover that shrinks towards its right edge between f0 and
    f1, revealing whatever is written underneath from left to right."""
    w = x1 - x0
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, h, 0.0015), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(-w / 2, 0, 0), verts=bm.verts)
    ob = _finish("wipe", bm, mat(colr), (x1, y, z), (0, 0, 0), (1, 1, 1), False, False, 0, parent)
    ob.visible_shadow = False
    edit = bpy.context.preferences.edit
    edit.keyframe_new_interpolation_type = "LINEAR"
    key(ob, max(1, f0), scale=(1, 1, 1))
    key(ob, f1, scale=(0.0001, 1, 1))
    edit.keyframe_new_interpolation_type = "BEZIER"
    return ob


def camera(keys, lens=50, fstop=None):
    """keys: [(frame, cam_location, look_at_point), ...]"""
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = 36
    cam = bpy.data.objects.new("cam", cd)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    tgt = empty(name="cam_target")
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    edit = bpy.context.preferences.edit
    edit.keyframe_new_interpolation_type = "LINEAR" if len(keys) == 2 else "BEZIER"
    for f, loc, look in keys:
        key(cam, f, loc=loc)
        key(tgt, f, loc=look)
    edit.keyframe_new_interpolation_type = "BEZIER"
    if fstop:
        cd.dof.use_dof = True
        cd.dof.focus_object = tgt
        cd.dof.aperture_fstop = fstop
    return cam


# -------------------------------------------------------------- character
class Char:
    pass


def noodle(parent, start, hand, sx, r=0.021, m="#141414"):
    """Curved 'noodle' arm: a bezier from the shoulder that follows `hand`."""
    cu = bpy.data.curves.new("arm", "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(1)
    p0, p1 = sp.bezier_points
    s, h = Vector(start), Vector(hand.location)
    for p in (p0, p1):
        p.handle_left_type = p.handle_right_type = "FREE"
    p0.co = s
    p0.handle_left = s + Vector((-sx * 0.05, 0, 0.03))
    p0.handle_right = s + Vector((sx * 0.15, 0, -0.05))
    p1.co = h
    p1.handle_left = h + Vector((sx * 0.09, 0.02, 0.07))
    p1.handle_right = h + Vector((-sx * 0.03, 0, -0.03))
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    cu.resolution_u = 14
    cu.use_fill_caps = True
    cu.materials.append(mat(m))
    ob = bpy.data.objects.new("arm", cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = parent
    hk = ob.modifiers.new("hook", "HOOK")
    hk.object = hand
    hk.vertex_indices_set([3, 4, 5])
    hk.matrix_inverse = Matrix.Translation(hand.location).inverted()
    return ob


def character(coat="#3f8f86", loc=(0, 0, 0), rotz=0, s=1.0, hat=None, hat_col="#7a5536",
              hair=None, hair_col="#5a3b28", glasses=False, mouth="flat", brows=0,
              sit=False, bowtie=None, skin="#f4f1ea", scarf=None, blinks=True):
    """Round-headed, noodle-armed figure facing -Y. Returns a Char with
    .root .head .body .handL .handR .mouth .hips .eyeballs for animation."""
    c = Char()
    root = empty(loc, name="char")
    root.rotation_euler[2] = math.radians(rotz)
    root.scale = (s, s, s)
    c.root = root
    leg = 0.24 if sit else 0.5
    c.leg = leg
    black, white = mat("#141414"), mat(skin)
    c.hips = []
    for sx in (-1, 1):
        hip = empty((sx * 0.09, 0, leg), root, name="hip")
        cyl(0.022, leg, (0, 0, -leg / 2), black, ol=False, parent=hip)
        sph(0.075, (0, -0.045, -leg + 0.04), mat("#3a2a22"), scale=(1, 1.5, 0.6), parent=hip)
        c.hips.append(hip)
    c.body = sph(1.0, (0, 0, leg + 0.36), mat(coat), scale=(0.25, 0.2, 0.42), parent=root)
    for i in range(3):
        sph(0.022, (0, -0.2 + 0.012 * i * i, leg + 0.52 - i * 0.13), mat("#2a2a2a"), ol=False, parent=root)
    if scarf:
        cyl(0.2, 0.07, (0, 0, leg + 0.72), mat(scarf), r2=0.17, ol=0.008, parent=root)
        box((0.07, 0.03, 0.2), (0.09, -0.19, leg + 0.62), mat(scarf), rot=(0, 8, 0), ol=0.008, parent=root)
    head = sph(0.3, (0, 0, leg + 1.0), white, parent=root, name="head")
    c.head = head
    if bowtie:
        for sx in (-1, 1):
            cyl(0.0, 0.11, (sx * 0.05, -0.19, leg + 0.72), mat(bowtie), r2=0.055, rot=(0, sx * 90, 0),
                ol=0.006, parent=root, seg=12)
        sph(0.022, (0, -0.2, leg + 0.72), mat(bowtie), ol=0.006, parent=root, seg=12)
    # face (children of the head, front is -Y)
    c.eyeballs, c.brows = [], []
    for sx in (-1, 1):
        e = sph(0.042, (sx * 0.105, -0.272, 0.035), black, scale=(1, 0.45, 1.25), ol=False, parent=head)
        sph(0.012, (0.012, -0.018, 0.02), mat("#ffffff", emit=1.0), ol=False, parent=e, seg=8)
        c.eyeballs.append(e)
        c.brows.append(box((0.115, 0.012, 0.02), (sx * 0.105, -0.283, 0.125), black, rot=(0, sx * brows, 0),
                           ol=False, parent=head))
        sph(0.03, (sx * 0.19, -0.215, -0.07), mat("#f2b8ae"), scale=(1, 0.3, 0.7), ol=False, parent=head, seg=12)
        if glasses:
            torus(0.085, 0.009, (sx * 0.105, -0.285, 0.035), mat("#2a2a2a"), rot=(90, 0, 0), parent=head)
    if glasses:
        box((0.05, 0.01, 0.012), (0, -0.297, 0.05), mat("#2a2a2a"), ol=False, parent=head)
    if mouth == "flat":
        c.mouth = box((0.12, 0.012, 0.018), (0, -0.287, -0.115), black, ol=False, parent=head)
    elif mouth == "smile":
        c.mouth = arc(0.09, 215, 325, 0.011, (0, -0.283, -0.06), parent=head)
    elif mouth == "frown":
        c.mouth = arc(0.09, 55, 125, 0.011, (0, -0.279, -0.21), parent=head)
    else:  # open
        c.mouth = sph(1.0, (0, -0.268, -0.13), black, scale=(0.085, 0.03, 0.075), ol=False, parent=head)
        sph(1.0, (0, -0.012, -0.03), mat("#d9534f"), scale=(0.05, 0.022, 0.03), ol=False, parent=c.mouth)
    # headwear
    hm = mat(hat_col)
    if hat == "cap":
        sph(1.0, (0, 0.02, 0.2), hm, scale=(0.3, 0.31, 0.13), parent=head)
        sph(1.0, (0, -0.26, 0.17), hm, scale=(0.2, 0.14, 0.03), parent=head)
        sph(0.03, (0, 0.02, 0.33), hm, ol=0.006, parent=head, seg=12)
    elif hat == "fedora":
        cyl(0.42, 0.03, (0, 0, 0.21), hm, parent=head)
        cyl(0.24, 0.2, (0, 0, 0.32), hm, r2=0.2, parent=head)
        cyl(0.245, 0.05, (0, 0, 0.25), mat("#2a2a2a"), ol=False, parent=head)
    elif hat == "beanie":
        sph(1.0, (0, 0.01, 0.13), hm, scale=(0.305, 0.305, 0.24), parent=head)
        cyl(0.31, 0.07, (0, 0.01, 0.12), mat("#f4f1ea"), ol=0.008, parent=head)
        sph(0.06, (0, 0.01, 0.39), mat("#f4f1ea"), parent=head)
    if hair in ("short", "bun", "long"):
        sph(1.0, (0, 0.06, 0.07), mat(hair_col), scale=(0.31, 0.3, 0.28), parent=head)
        if hair == "bun":
            sph(0.13, (0, 0.08, 0.36), mat(hair_col), parent=head)
        if hair == "long":
            sph(1.0, (0, 0.12, -0.12), mat(hair_col), scale=(0.3, 0.22, 0.3), parent=head)
    # arms
    hands = []
    for sx in (-1, 1):
        h = sph(0.075, (sx * 0.34, -0.03, leg + 0.2), white, parent=root, name="hand")
        noodle(root, (sx * 0.22, 0, leg + 0.6), h, sx)
        hands.append(h)
    c.handL, c.handR = hands  # L is at -X (screen left when facing the camera)
    if blinks:
        SHOT["seed"] += 1
        blink(c, SHOT["frames"], SHOT["seed"])
    return c


def hand_world(c, hand, point):
    """Location for `hand` (in the character's local space) to reach a world point."""
    bpy.context.view_layer.update()
    return tuple(c.root.matrix_world.inverted() @ Vector(point))


def blink(c, n, seed=0):
    rnd = random.Random(seed)
    f = rnd.randint(6, 40)
    while f < n - 3:
        for e in c.eyeballs:
            key(e, f - 2, scale=(1, 1, 1))
            key(e, f, scale=(1, 1, 0.08))
            key(e, f + 2, scale=(1, 1, 1))
        f += rnd.randint(30, 70)


def talk(c, f0, f1, step=3):
    """Flap an open mouth between f0 and f1."""
    for i, f in enumerate(range(f0, f1 + 1, step)):
        key(c.mouth, f, scale=(1, 1, 1.15) if i % 2 else (0.9, 1, 0.45))


def walk(c, f0, f1, a, b, step=6, swing=30):
    """Move the character from a to b with swinging legs and a little bounce."""
    edit = bpy.context.preferences.edit
    edit.keyframe_new_interpolation_type = "LINEAR"
    key(c.root, f0, loc=a)
    key(c.root, f1, loc=b)
    edit.keyframe_new_interpolation_type = "BEZIER"
    base = [tuple(h.location) for h in (c.handL, c.handR)]
    for i, f in enumerate(range(f0, f1 + 1, step)):
        last = f + step > f1
        ang = 0 if last else (swing if i % 2 else -swing)
        key(c.hips[0], f, rot=(ang, 0, 0))
        key(c.hips[1], f, rot=(-ang, 0, 0))
        key(c.body, f, loc=(0, 0, c.leg + 0.36 + (0 if i % 2 else 0.02)))
        for hnd, bl, sg in ((c.handL, base[0], 1), (c.handR, base[1], -1)):
            key(hnd, f, loc=(bl[0], bl[1] + sg * ang / swing * 0.12, bl[2]))

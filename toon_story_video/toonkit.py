"""Small Blender (bpy) toolkit for toy-like, outlined 3D story shorts.

Everything is built from primitives in code: materials, inverted-hull
outlines, stick-limbed round-headed characters, text props, lights, camera.
"""
import math

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


# ----------------------------------------------------------------- scene
def reset(width=720, height=1280, samples=12):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable("cycles")
    _mats.clear()
    _fonts.clear()
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.render.resolution_x, s.render.resolution_y = width, height
    s.render.fps = FPS
    s.render.image_settings.file_format = "PNG"
    s.render.use_persistent_data = True
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.cycles.use_adaptive_sampling = False
    s.cycles.denoising_quality = "FAST"
    s.cycles.max_bounces = 3
    s.cycles.diffuse_bounces = 1
    s.cycles.glossy_bounces = 1
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
    """Black shell visible only on its inward faces and only to the camera."""
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
    lp = nt.nodes.new("ShaderNodeLightPath")
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    mx = nt.nodes.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    nt.links.new(lp.outputs["Is Camera Ray"], inv.inputs[1])
    nt.links.new(geo.outputs["Backfacing"], mx.inputs[0])
    nt.links.new(inv.outputs[0], mx.inputs[1])
    nt.links.new(mx.outputs[0], mix.inputs[0])
    nt.links.new(em.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    _mats["OUTLINE"] = m
    return m


def add_outline(ob, th=0.012):
    ob.data.materials.append(outline_mat())
    md = ob.modifiers.new("outline", "SOLIDIFY")
    md.thickness = th
    md.offset = 1
    md.use_flip_normals = True
    md.use_rim = False
    md.material_offset = len(ob.data.materials) - 1
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
        md = ob.modifiers.new("es", "EDGE_SPLIT")
        md.split_angle = math.radians(50)
        ob.modifiers.move(len(ob.modifiers) - 1, 0)
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
    for f, loc, look in keys:
        key(cam, f, loc=loc)
        key(tgt, f, loc=look)
    if fstop:
        cd.dof.use_dof = True
        cd.dof.focus_object = tgt
        cd.dof.aperture_fstop = fstop
    return cam


# -------------------------------------------------------------- character
class Char:
    pass


def character(coat="#3f8f86", loc=(0, 0, 0), rotz=0, s=1.0, hat=None, hat_col="#7a5536",
              hair=None, hair_col="#5a3b28", glasses=False, mouth="flat", brows=0,
              sit=False, bowtie=None, skin="#f4f1ea"):
    """Round-headed, stick-limbed figure facing -Y. Returns a Char with
    .root .head .body .handL .handR .mouth for animation."""
    c = Char()
    root = empty(loc, name="char")
    root.rotation_euler[2] = math.radians(rotz)
    root.scale = (s, s, s)
    c.root = root
    leg = 0.24 if sit else 0.5
    black, white = mat("#141414"), mat(skin)
    for sx in (-1, 1):
        cyl(0.022, leg, (sx * 0.09, 0, leg / 2), black, ol=False, parent=root)
        sph(0.075, (sx * 0.09, -0.045, 0.04), mat("#3a2a22"), scale=(1, 1.5, 0.6), parent=root)
    c.body = sph(1.0, (0, 0, leg + 0.36), mat(coat), scale=(0.25, 0.2, 0.42), parent=root)
    for i in range(3):
        sph(0.022, (0, -0.2 + 0.012 * i * i, leg + 0.52 - i * 0.13), mat("#2a2a2a"), ol=False, parent=root)
    head = sph(0.3, (0, 0, leg + 1.0), white, parent=root, name="head")
    c.head = head
    if bowtie:
        for sx in (-1, 1):
            cyl(0.0, 0.11, (sx * 0.05, -0.19, leg + 0.72), mat(bowtie), r2=0.055, rot=(0, sx * 90, 0),
                ol=0.006, parent=root, seg=12)
    # face (children of the head, front is -Y)
    c.eyes = []
    for sx in (-1, 1):
        c.eyes.append(sph(0.042, (sx * 0.105, -0.272, 0.035), black, scale=(1, 0.45, 1.25), ol=False, parent=head))
        b = box((0.115, 0.012, 0.02), (sx * 0.105, -0.283, 0.125), black, rot=(0, sx * brows, 0), ol=False, parent=head)
        c.eyes.append(b)
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
    elif hat == "fedora":
        cyl(0.42, 0.03, (0, 0, 0.21), hm, parent=head)
        cyl(0.24, 0.2, (0, 0, 0.32), hm, r2=0.2, parent=head)
    elif hat == "beanie":
        sph(1.0, (0, 0.01, 0.13), hm, scale=(0.305, 0.305, 0.24), parent=head)
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
        limb(root, (sx * 0.23, 0, leg + 0.6), h)
        hands.append(h)
    c.handL, c.handR = hands  # L is at -X (screen left when facing the camera)
    return c


def hand_world(c, hand, point):
    """Location for `hand` (in the character's local space) to reach a world point."""
    bpy.context.view_layer.update()
    return tuple(c.root.matrix_world.inverted() @ Vector(point))

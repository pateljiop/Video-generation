import bpy
from mathutils import Vector
from pathlib import Path
import math

W, H, FPS = 360, 640, 20
D = 15.0
OUT = Path("build")
OUT.mkdir(exist_ok=True)
MP4 = OUT / "techmind-cinematic.mp4"

def mat(name, color, emission=None, metallic=0.0, rough=0.4):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = 4.0
    return m

DARK = mat("Desk", (.012, .018, .030), metallic=.25, rough=.32)
BLACK = mat("Black", (.002, .004, .008), metallic=.35, rough=.22)
SCREEN = mat("Screen", (.006, .035, .075), rough=.2)
CYAN = mat("Cyan", (.015, .35, .75), emission=(.01, .55, 1))
GREEN = mat("Green", (.02, .32, .08), emission=(.02, .65, .15))
WHITE = mat("White", (.62, .76, .9), rough=.3)
AMBER = mat("Amber", (.62, .18, .015), emission=(1, .22, .01))
MAGENTA = mat("Magenta", (.42, .03, .3), emission=(.9, .04, .5))

def cube(name, loc, scale, material, bevel=.03):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 1
    o.data.materials.append(material)
    return o

def text(body, loc, size=.16, material=WHITE, align="LEFT"):
    curve = bpy.data.curves.new("Text", "FONT")
    curve.body = body
    curve.align_x = align
    curve.size = size
    curve.extrude = .004
    o = bpy.data.objects.new("TXT_" + body, curve)
    bpy.context.collection.objects.link(o)
    o.location = loc
    # Text lies in XY by default; rotate it so its face points toward the camera at -Y.
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(material)
    return o

def area_light(loc, energy, color, size):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.data.energy = energy
    l.data.color = color
    l.data.shape = "DISK"
    l.data.size = size
    return l

def camera(loc, lens=48):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    return c

def aim(c, target):
    c.rotation_euler = (Vector(target) - c.location).to_track_quat("-Z", "Y").to_euler()

def key(obj, frame, location=None, rotation=None, scale=None):
    if location is not None:
        obj.location = location
        obj.keyframe_insert("location", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)

# Clean scene.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = W
sc.render.resolution_y = H
sc.render.resolution_percentage = 100
sc.render.fps = FPS
sc.frame_start = 1
sc.frame_end = int(D * FPS)
sc.world.color = (.001, .002, .006)
try:
    sc.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass

# Cinematic workstation.
cube("Desk", (0, 0, 0), (5, 4, .12), DARK, .06)
cube("Monitor", (0, 0, 2.0), (2.35, .14, 1.35), BLACK, .10)
display = cube("Display", (0, -.16, 2.0), (2.08, .035, 1.08), SCREEN, .03)
cube("Base", (0, -1.05, .48), (2.5, .78, .08), BLACK, .08)

for r in range(4):
    for c in range(9):
        cube(f"Key_{r}_{c}", (-1.35 + c*.34, -1.10 + r*.27, .59), (.115, .07, .018), WHITE, .008)

area_light((-3.5, -3.5, 4.5), 900, (.03, .22, 1), 3.2)
area_light((3.2, 1.5, 3.5), 700, (.02, .65, 1), 2.5)
area_light((0, 2.0, 4.0), 450, (.55, .08, .7), 2.0)

# Screen content.
text("AI AGENT", (-1.65, -.215, 2.48), .22, CYAN)
text("PLAN   >   ACT   >   VERIFY", (-1.65, -.215, 2.15), .115, WHITE)

apps = [("MAIL", -1.25, CYAN), ("CODE", 0, GREEN), ("TERM", 1.25, AMBER)]
for name, x, material in apps:
    cube("APP_" + name, (x, -.215, 1.25), (.48, .025, .22), material, .03)
    text(name, (x, -.255, 1.20), .12, WHITE)

# Additional depth layers: browser/code/terminal cards.
for i, (label, x, z, material) in enumerate([
    ("SEARCH", -1.15, 1.68, CYAN),
    ("WRITE", 0, 1.68, GREEN),
    ("TEST", 1.15, 1.68, AMBER),
]):
    cube("CARD_" + label, (x, -.225, z), (.45, .018, .12), BLACK, .02)
    text(label, (x, -.255, z-.045), .085, material, "CENTER")

# Animated cursor.
cursor = cube("Cursor", (-1.4, -.28, 1.65), (.035, .02, .10), WHITE, .008)
cursor_points = [
    (.4, (-1.0, -.28, 1.25)),
    (3.3, (0, -.28, 1.25)),
    (6.4, (1.0, -.28, 1.25)),
    (9.5, (-.7, -.28, 1.68)),
    (12.6, (.8, -.28, 1.68)),
]
for t, p in cursor_points:
    key(cursor, int(t*FPS), location=p)

# Six deliberate commercial-style shots with real camera direction keyframes.
C = camera((-4.2, -8.2, 3.2), 52)
sc.camera = C
shots = [
    (0.0, 3.1, (-4.2,-8.2,3.2), (-1.6,-6.0,2.0)),
    (3.1, 6.2, (3.9,-7.4,2.9), (1.0,-5.9,1.9)),
    (6.2, 9.3, (-3.4,-7.7,2.5), (1.5,-6.0,2.0)),
    (9.3, 12.4, (3.7,-7.5,3.3), (-.7,-5.9,2.05)),
    (12.4, 15.5, (-3.5,-7.2,2.8), (1.9,-6.0,2.0)),
    (12.5, 15.0, (2.9,-8.0,3.8), (0,-6.0,1.7)),
]
for start, end, p0, target0 in shots:
    C.location = p0
    aim(C, target0)
    C.keyframe_insert("location", frame=int(start*FPS))
    C.keyframe_insert("rotation_euler", frame=int(start*FPS))
    C.location = target0
    aim(C, target0)
    C.keyframe_insert("location", frame=int(end*FPS))
    C.keyframe_insert("rotation_euler", frame=int(end*FPS))

C.data.dof.use_dof = True
C.data.dof.focus_object = display
C.data.dof.aperture_fstop = 2.0

# Status words appear like a live system HUD.
for t, label, material in [
    (.7, "OPEN", CYAN), (4.1, "RUN", GREEN), (7.2, "READ", CYAN),
    (10.7, "TEST", AMBER), (13.8, "DONE", GREEN)
]:
    o = text(label, (1.15, -.31, .75), .19, material)
    key(o, int((t-.15)*FPS), scale=(.01,.01,.01))
    key(o, int(t*FPS), scale=(1,1,1))

# Ending brand reveal.
brand = text("TECHMIND", (0, -.46, .95), .56, CYAN, "CENTER")
key(brand, int(13.0*FPS), scale=(.01,.01,.01))
key(brand, int(13.5*FPS), scale=(1,1,1))
tag = text("AI  +  COMPUTER  +  ACTION", (0, -.46, .48), .17, WHITE, "CENTER")
key(tag, int(13.4*FPS), scale=(.01,.01,.01))
key(tag, int(14.0*FPS), scale=(1,1,1))

# Render to MP4.
sc.render.image_settings.file_format = "FFMPEG"
sc.render.ffmpeg.format = "MPEG4"
sc.render.ffmpeg.codec = "H264"
sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
sc.render.ffmpeg.audio_codec = "AAC"
sc.render.filepath = str(MP4)

bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "techmind-cinematic.blend"))
bpy.ops.render.render(animation=True)
print("BLENDER_DONE=" + str(MP4))

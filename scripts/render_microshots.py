import bpy, math, subprocess
from mathutils import Vector
from pathlib import Path

# Micro-shot editor: render five independent hero shots, then assemble them.
W, H, FPS = 432, 768, 20
SHOT_D = 3.0
OUT = Path("build/shots")
OUT.mkdir(parents=True, exist_ok=True)

def mat(name, c, e=None, metallic=0.0, rough=.35, emission_strength=1.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*c, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    if e:
        p.inputs["Emission Color"].default_value = (*e, 1)
        p.inputs["Emission Strength"].default_value = emission_strength
    return m

DESK   = mat("Desk",   (.006, .009, .016), None, .45, .22)
BLACK  = mat("Black",  (.0005, .0008, .0015), None, .65, .18)
SCREEN = mat("Screen", (.002, .006, .012), (.004, .035, .08), .15, .28, .45)
GLASS  = mat("Glass",  (.008, .018, .028), (.01, .09, .16), .05, .12, .55)
CYAN   = mat("Cyan",   (.004, .06, .11), (.01, .55, 1.0), .15, .20, 2.2)
BLUE   = mat("Blue",   (.003, .025, .09), (.01, .16, 1.0), .15, .24, 1.4)
GREEN  = mat("Green",  (.005, .06, .018), (.02, .85, .20), .10, .24, 1.8)
AMBER  = mat("Amber",  (.10, .025, .002), (1.0, .20, .01), .08, .25, 1.7)
WHITE  = mat("White",  (.30, .42, .52), (.15, .30, .45), .05, .30, .7)
MAG    = mat("Mag",    (.10, .003, .06), (.85, .02, .40), .10, .24, 1.7)
GRID   = mat("Grid",   (.008, .015, .025), (.01, .04, .07), .1, .38, .25)

def cube(n, loc, scale, ma, bev=.02):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = n
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bev:
        b = o.modifiers.new("SoftEdges", "BEVEL")
        b.width = bev
        b.segments = 2
    o.data.materials.append(ma)
    return o

def text(body, loc, size=.16, ma=WHITE, align="LEFT"):
    c = bpy.data.curves.new("T", "FONT")
    c.body = body
    c.size = size
    c.align_x = align
    c.extrude = .002
    c.space_character = 1.05
    o = bpy.data.objects.new("T_" + body, c)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(ma)
    return o

def light(loc, energy, color, size):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.data.energy = energy
    l.data.color = color
    l.data.shape = "DISK"
    l.data.size = size

def cam(loc, target, lens=50):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    c.data.sensor_width = 36
    c.rotation_euler = (Vector(target) - c.location).to_track_quat("-Z", "Y").to_euler()
    c.data.dof.use_dof = True
    return c

def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

def glow_strip(loc, scale, ma=CYAN):
    return cube("GlowStrip", loc, scale, ma, .012)

def base_world():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = W
    sc.render.resolution_y = H
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.frame_start = 1
    sc.frame_end = int(SHOT_D * FPS)
    sc.world.color = (.0002, .0004, .001)
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except:
        pass

    # Cinematic three-point lighting.
    light((-4, -5, 5), 900, (.02, .22, 1.0), 3.5)
    light((4, -1, 4), 650, (.04, .65, 1.0), 2.5)
    light((0, 4, 5), 500, (.70, .03, .35), 2.8)

    # Subtle floor grid for depth.
    for x in range(-6, 7):
        cube("GridX", (x * .65, 1.0, .015), (.006, 3.0, .004), GRID, .001)
    for y in range(-4, 6):
        cube("GridY", (0, y * .65, .016), (4.2, .006, .004), GRID, .001)

def render_shot(idx, builder):
    clear()
    base_world()
    builder()
    p = OUT / f"shot{idx:02d}.mp4"
    sc = bpy.context.scene
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
    sc.render.ffmpeg.audio_codec = "AAC"
    sc.render.filepath = str(p)
    bpy.ops.render.render(animation=True)
    print("SHOT_DONE", idx, p)

def add_monitor(title, subtitle, accent=CYAN):
    cube("MonitorBody", (0, .25, 2.35), (2.35, .13, 1.45), BLACK, .10)
    cube("MonitorScreen", (0, .105, 2.35), (2.12, .025, 1.20), SCREEN, .025)
    glow_strip((-1.85, .065, 3.34), (.38, .015, .025), accent)
    glow_strip((-1.85, .065, 1.36), (.20, .015, .018), accent)
    text(title, (-1.72, .06, 3.02), .20, accent)
    text(subtitle, (-1.72, .06, 2.73), .105, WHITE)
    # UI cards
    for i, (z, w, ma) in enumerate([(2.38, 1.35, accent), (1.98, 1.70, BLUE), (1.58, 1.05, GREEN)]):
        cube("UI", (-.55, .045, z), (w, .012, .07), ma, .008)
    cube("Status", (1.15, .045, 2.98), (.52, .012, .10), GREEN, .015)
    text("LIVE", (1.15, .015, 2.95), .075, GREEN, "CENTER")

def shot1():
    cube("Desk", (0, 0, 0), (4.2, 3.2, .12), DESK, .05)
    add_monitor("AI AGENT", "TASK RECEIVED  /  PRIORITY HIGH", CYAN)
    # Agent core hovering above desk.
    core = cube("AgentCore", (0, -.25, .92), (.42, .42, .42), CYAN, .10)
    for i in range(10):
        a = i * math.tau / 10
        orb = cube("Orbit", (math.cos(a) * .72, -.24, .92 + math.sin(a) * .72),
                   (.045, .045, .045), CYAN, .012)
        orb.rotation_euler[1] = a
    glow_strip((0, -.72, .20), (1.6, .025, .018), MAG)
    c = cam((-4.2, -7.4, 3.35), (0, 0, 1.75), 52)
    bpy.context.scene.camera = c
    c.keyframe_insert("location", frame=1)
    c.location = (-1.2, -5.0, 2.25)
    c.rotation_euler = (Vector((0, 0, 1.75)) - c.location).to_track_quat("-Z", "Y").to_euler()
    c.keyframe_insert("location", frame=60)
    c.keyframe_insert("rotation_euler", frame=60)

def shot2():
    cube("Desk", (0, 0, 0), (4.2, 3.2, .12), DESK, .05)
    cube("BrowserFrame", (0, .15, 2.25), (2.55, .11, 1.55), BLACK, .10)
    cube("BrowserPage", (0, .025, 2.25), (2.30, .025, 1.30), SCREEN, .025)
    text("WEB BROWSER", (-1.92, -.02, 3.28), .18, CYAN)
    cube("SearchBar", (-.25, -.005, 2.83), (1.65, .015, .11), GLASS, .018)
    glow_strip((-1.55, -.03, 2.83), (.35, .012, .018), CYAN)
    text("SEARCH  >  READ  >  DECIDE", (-1.88, -.02, 1.40), .105, WHITE)
    for i, (x, z, w, ma) in enumerate([
        (-1.25, 2.28, .75, CYAN), (.05, 2.28, .92, BLUE), (1.18, 2.28, .55, GREEN),
        (-1.15, 1.83, 1.10, BLUE), (.40, 1.83, .85, CYAN)
    ]):
        cube("ResultCard", (x, -.01, z), (w, .015, .10), ma, .015)
    # Browser cursor.
    cursor = cube("Cursor", (1.35, -.035, 2.60), (.025, .012, .11), WHITE, .006)
    cursor.rotation_euler[1] = math.radians(-25)
    c = cam((4.4, -7.4, 3.65), (0, .0, 2.15), 52)
    bpy.context.scene.camera = c
    c.keyframe_insert("location", frame=1)
    c.location = (1.25, -5.0, 2.45)
    c.rotation_euler = (Vector((0, 0, 2.15)) - c.location).to_track_quat("-Z", "Y").to_euler()
    c.keyframe_insert("location", frame=60)
    c.keyframe_insert("rotation_euler", frame=60)

def shot3():
    cube("Desk", (0, 0, 0), (4.2, 3.2, .12), DESK, .05)
    cube("TerminalFrame", (-.15, .15, 2.20), (2.55, .11, 1.60), BLACK, .10)
    cube("TerminalScreen", (-.15, -.005, 2.20), (2.30, .025, 1.35), SCREEN, .025)
    text("WRITE / RUN / TEST", (-1.98, -.02, 3.30), .17, GREEN)
    lines = [
        ("$ write_agent.py", CYAN),
        ("agent.plan()", WHITE),
        ("agent.execute()", WHITE),
        ("pytest -q", AMBER),
        ("PASS   18 TESTS", GREEN),
    ]
    for i, (s, ma) in enumerate(lines):
        text(s, (-1.82, -.02, 2.78 - i * .38), .105, ma)
    glow_strip((-1.82, -.03, 1.32), (.80, .012, .018), GREEN)
    text("AUTOMATED VERIFICATION", (.05, -.02, 1.32), .095, WHITE)
    c = cam((-4.2, -7.4, 3.25), (-.1, 0, 2.15), 52)
    bpy.context.scene.camera = c
    c.keyframe_insert("location", frame=1)
    c.location = (-1.15, -5.0, 2.38)
    c.rotation_euler = (Vector((-.1, 0, 2.15)) - c.location).to_track_quat("-Z", "Y").to_euler()
    c.keyframe_insert("location", frame=60)
    c.keyframe_insert("rotation_euler", frame=60)

def shot4():
    cube("Floor", (0, 0, 0), (4.2, 4.2, .08), DESK, .03)
    for x in [-1.65, 0, 1.65]:
        cube("Rack", (x, .45, 1.55), (.68, .62, 1.50), BLACK, .08)
        for z in [.55, .98, 1.41, 1.84, 2.27]:
            cube("LED", (x - .48, -.20, z), (.045, .02, .028),
                 [CYAN, GREEN, AMBER][int(z * 3) % 3], .008)
        for z in [.65, 1.20, 1.75, 2.30]:
            cube("RackSlot", (x, -.19, z), (.46, .018, .025), GRID, .006)
    text("EXECUTE", (-2.70, -.18, 3.55), .25, CYAN)
    text("TOOL  >  VERIFY  >  DONE", (-2.70, -.18, 3.12), .115, WHITE)
    glow_strip((-2.70, -.22, 2.68), (1.00, .018, .020), GREEN)
    c = cam((4.6, -7.6, 3.65), (0, .35, 1.55), 52)
    bpy.context.scene.camera = c
    c.keyframe_insert("location", frame=1)
    c.location = (1.20, -5.1, 2.55)
    c.rotation_euler = (Vector((0, .35, 1.55)) - c.location).to_track_quat("-Z", "Y").to_euler()
    c.keyframe_insert("location", frame=60)
    c.keyframe_insert("rotation_euler", frame=60)

def shot5():
    cube("Stage", (0, 0, 0), (4.2, 3.0, .08), BLACK, .03)
    for i in range(14):
        ma = CYAN if i % 3 else MAG
        cube("Bar", (-2.75 + i * .42, .2, .22), (.12, .30, .12), ma, .02)
    text("TECHMIND", (0, -.35, 2.00), .62, CYAN, "CENTER")
    text("AI  +  COMPUTER  +  ACTION", (0, -.35, 1.12), .15, WHITE, "CENTER")
    text("WORKS WHILE YOU WORK", (0, -.35, .62), .115, GREEN, "CENTER")
    glow_strip((0, -.45, .35), (2.2, .02, .02), CYAN)
    c = cam((3.8, -7.5, 3.6), (0, -.2, 1.35), 52)
    bpy.context.scene.camera = c
    c.keyframe_insert("location", frame=1)
    c.location = (0, -5.0, 2.35)
    c.rotation_euler = (Vector((0, -.2, 1.35)) - c.location).to_track_quat("-Z", "Y").to_euler()
    c.keyframe_insert("location", frame=60)
    c.keyframe_insert("rotation_euler", frame=60)

for i, builder in enumerate([shot1, shot2, shot3, shot4, shot5], 1):
    render_shot(i, builder)

# Editor pass: short dissolves between independent hero shots.
inputs = "".join([f"-i {OUT/f'shot{i:02d}.mp4'} " for i in range(1, 6)])
filt = (
    "[0:v][1:v]xfade=transition=fade:duration=0.18:offset=2.82[x1];"
    "[x1][2:v]xfade=transition=fade:duration=0.18:offset=5.64[x2];"
    "[x2][3:v]xfade=transition=fade:duration=0.18:offset=8.46[x3];"
    "[x3][4:v]xfade=transition=fade:duration=0.18:offset=11.28[v]"
)
cmd = f"ffmpeg -y {inputs} -filter_complex \"{filt}\" -map '[v]' -an -c:v libx264 -pix_fmt yuv420p -crf 22 build/techmind-cinematic.mp4"
subprocess.run(cmd, shell=True, check=True)
print("EDITOR_DONE build/techmind-cinematic.mp4")

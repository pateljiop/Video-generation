import bpy, math, subprocess
from mathutils import Vector
from pathlib import Path

W,H,FPS = 360,640,20
SHOT_D = 3.0
OUT = Path("build/shots")
OUT.mkdir(parents=True, exist_ok=True)

def mat(name, c, e=None, metallic=0, rough=.35):
    m=bpy.data.materials.new(name); m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*c,1)
    p.inputs["Metallic"].default_value=metallic; p.inputs["Roughness"].default_value=rough
    if e:
        p.inputs["Emission Color"].default_value=(*e,1); p.inputs["Emission Strength"].default_value=5
    return m

DARK=mat("Desk",(.008,.012,.022),None,.4,.25)
BLACK=mat("Black",(.001,.002,.004),None,.5,.2)
CYAN=mat("Cyan",(.01,.18,.38),(.01,.65,1),.15,.2)
BLUE=mat("Blue",(.01,.08,.3),(.02,.2,1),.2,.25)
GREEN=mat("Green",(.01,.18,.05),(.02,.8,.18),.1,.25)
AMBER=mat("Amber",(.3,.08,.005),(1,.22,.01),.1,.25)
WHITE=mat("White",(.55,.7,.85),None,.1,.3)
MAG=mat("Mag",(.25,.01,.2),(.9,.03,.5),.1,.25)

def cube(n,loc,scale,ma,bev=.02):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=n; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bev:
        b=o.modifiers.new("B","BEVEL"); b.width=bev; b.segments=1
    o.data.materials.append(ma); return o

def text(body,loc,size=.16,ma=WHITE,align="LEFT"):
    c=bpy.data.curves.new("T","FONT"); c.body=body; c.size=size; c.align_x=align; c.extrude=.003
    o=bpy.data.objects.new("T_"+body,c); bpy.context.collection.objects.link(o); o.location=loc
    o.rotation_euler=(math.radians(90),0,0); o.data.materials.append(ma); return o

def light(loc,energy,color,size):
    bpy.ops.object.light_add(type="AREA",location=loc); l=bpy.context.object
    l.data.energy=energy; l.data.color=color; l.data.shape="DISK"; l.data.size=size

def cam(loc,target,lens=50):
    bpy.ops.object.camera_add(location=loc); c=bpy.context.object; c.data.lens=lens
    c.rotation_euler=(Vector(target)-c.location).to_track_quat("-Z","Y").to_euler(); return c

def clear():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)

def base_world():
    sc=bpy.context.scene; sc.render.engine="BLENDER_EEVEE"
    sc.render.resolution_x=W; sc.render.resolution_y=H; sc.render.resolution_percentage=100
    sc.render.fps=FPS; sc.frame_start=1; sc.frame_end=int(SHOT_D*FPS); sc.world.color=(.0005,.001,.003)
    try: sc.view_settings.look="AgX - Medium High Contrast"
    except: pass
    light((-3,-4,5),850,(.02,.25,1),3); light((3,1,4),650,(.05,.7,1),2); light((0,3,3),400,(.7,.05,.5),2)

def render_shot(idx, builder):
    clear(); base_world(); builder()
    p=OUT/f"shot{idx:02d}.mp4"; sc=bpy.context.scene
    sc.render.image_settings.file_format="FFMPEG"; sc.render.ffmpeg.format="MPEG4"; sc.render.ffmpeg.codec="H264"
    sc.render.ffmpeg.constant_rate_factor="MEDIUM"; sc.render.ffmpeg.audio_codec="AAC"; sc.render.filepath=str(p)
    bpy.ops.render.render(animation=True); print("SHOT_DONE",idx,p)

def shot1():
    cube("Desk",(0,0,0),(4,3,.12),DARK,.05); cube("Monitor",(0,.2,2.0),(2.1,.12,1.25),BLACK,.08)
    cube("Screen",(0,.05,2.0),(1.85,.025,1.0),BLUE,.02)
    text("AI AGENT",(-1.45,-.0,2.5),.22,CYAN); text("TASK RECEIVED",(-1.45,-.0,2.12),.13,WHITE)
    core=cube("Core",(0,-.25,1.2),(.42,.42,.42),CYAN,.08)
    for i in range(8):
        a=i*math.pi/4; cube("orb",(math.cos(a)*.75,-.2,1.2+math.sin(a)*.75),(.07,.07,.07),CYAN,.02)
    c=cam((-3.2,-6,2.4),(0,-.1,1.5),58); bpy.context.scene.camera=c
    c.keyframe_insert("location",frame=1); c.location=(-.7,-4.2,1.65); c.rotation_euler=(Vector((0,-.1,1.2))-c.location).to_track_quat("-Z","Y").to_euler(); c.keyframe_insert("location",frame=60); c.keyframe_insert("rotation_euler",frame=60)

def shot2():
    cube("Desk",(0,0,0),(4,3,.12),DARK,.05)
    cube("Browser",(0,0,2.1),(2.2,.08,1.35),BLACK,.08); cube("Page",(0,-.1,2.1),(2,.025,1.15),BLUE,.02)
    for y,w in [(2.7,1.2),(2.3,1.7),(1.9,1.45),(1.5,1.1)]:
        cube("line",(-.25,-.15,y),(w,.02,.035),CYAN,.01)
    text("WEB BROWSER",(-1.55,-.16,2.95),.18,CYAN); text("SEARCH  >  READ  >  DECIDE",(-1.55,-.16,1.38),.10,WHITE)
    for x in [-1.5,0,1.5]: cube("card",(x,-.35,0.9),(.5,.3,.12),[CYAN,GREEN,AMBER][[-1.5,0,1.5].index(x)],.03)
    c=cam((3.4,-6.2,3.0),(0,0,2),55); bpy.context.scene.camera=c
    c.keyframe_insert("location",frame=1); c.location=(1.1,-4.0,2.15); c.rotation_euler=(Vector((0,0,2))-c.location).to_track_quat("-Z","Y").to_euler(); c.keyframe_insert("location",frame=60); c.keyframe_insert("rotation_euler",frame=60)

def shot3():
    cube("Desk",(0,0,0),(4,3,.12),DARK,.05); cube("Terminal",(-.2,0,1.8),(2.2,.08,1.5),BLACK,.08)
    cube("TermScreen",(-.2,-.1,1.8),(2,.025,1.28),GREEN,.02)
    lines=["$ write_agent.py","agent.plan()","agent.execute()","pytest -q","PASS  18 tests"]
    for i,s in enumerate(lines): text(s,(-1.75,-.15,2.65-i*.38),.11,WHITE)
    text("WRITE  /  RUN  /  TEST",(-1.75,-.15,.62),.13,GREEN)
    c=cam((-3.5,-6,2.7),(-.2,0,1.8),58); bpy.context.scene.camera=c
    c.keyframe_insert("location",frame=1); c.location=(-.5,-3.8,2.0); c.rotation_euler=(Vector((-.2,0,1.8))-c.location).to_track_quat("-Z","Y").to_euler(); c.keyframe_insert("location",frame=60); c.keyframe_insert("rotation_euler",frame=60)

def shot4():
    cube("Floor",(0,0,0),(4,4,.08),DARK,.03)
    for x in [-1.6,0,1.6]:
        cube("Rack",(x,0,1.5),(.6,.6,1.45),BLACK,.08)
        for z in [.5,1,1.5,2,2.5]: cube("led",(x-.45,-.65,z),(.06,.025,.025),[CYAN,GREEN,AMBER][int(z*2)%3],.01)
    text("EXECUTE",(-2.5,-.7,3.35),.25,CYAN); text("TOOL  >  VERIFY  >  DONE",(-2.5,-.7,2.95),.12,WHITE)
    c=cam((4,-6,3.0),(0,0,1.5),55); bpy.context.scene.camera=c
    c.keyframe_insert("location",frame=1); c.location=(1.0,-3.8,2.0); c.rotation_euler=(Vector((0,0,1.5))-c.location).to_track_quat("-Z","Y").to_euler(); c.keyframe_insert("location",frame=60); c.keyframe_insert("rotation_euler",frame=60)

def shot5():
    cube("Stage",(0,0,0),(4,3,.08),BLACK,.03)
    for i in range(12): cube("bar",(-2.4+i*.44,0,.25),( .12,.25,.12),CYAN,.02)
    text("TECHMIND",(0,-.35,1.75),.58,CYAN,"CENTER"); text("AI  +  COMPUTER  +  ACTION",(0,-.35,.95),.15,WHITE,"CENTER")
    text("WORKS WHILE YOU WORK",(0,-.35,.48),.12,GREEN,"CENTER")
    c=cam((2.8,-6,3.0),(0,-.2,1.25),55); bpy.context.scene.camera=c
    c.keyframe_insert("location",frame=1); c.location=(0,-4.5,2.0); c.rotation_euler=(Vector((0,-.2,1.2))-c.location).to_track_quat("-Z","Y").to_euler(); c.keyframe_insert("location",frame=60); c.keyframe_insert("rotation_euler",frame=60)

for i,b in enumerate([shot1,shot2,shot3,shot4,shot5],1): render_shot(i,b)

# Editor pass: short dissolves between independent hero shots.
inputs="".join([f"-i {OUT/f'shot{i:02d}.mp4'} " for i in range(1,6)])
filt="[0:v][1:v]xfade=transition=fade:duration=0.18:offset=2.82[x1];[x1][2:v]xfade=transition=fade:duration=0.18:offset=5.64[x2];[x2][3:v]xfade=transition=fade:duration=0.18:offset=8.46[x3];[x3][4:v]xfade=transition=fade:duration=0.18:offset=11.28[v]"
cmd=f"ffmpeg -y {inputs} -filter_complex \"{filt}\" -map '[v]' -an -c:v libx264 -pix_fmt yuv420p -crf 23 build/techmind-cinematic.mp4"
subprocess.run(cmd,shell=True,check=True)
print("EDITOR_DONE build/techmind-cinematic.mp4")

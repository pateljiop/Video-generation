import bpy
from mathutils import Vector
from pathlib import Path

W,H,FPS=540,960,24
D=18.6
OUT=Path("build"); OUT.mkdir(exist_ok=True)
MP4=OUT/"techmind-cinematic.mp4"

def M(name,c,emit=None,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF"); b.inputs["Base Color"].default_value=(*c,1); b.inputs["Metallic"].default_value=metal; b.inputs["Roughness"].default_value=rough
    if emit: b.inputs["Emission Color"].default_value=(*emit,1); b.inputs["Emission Strength"].default_value=3
    return m
DARK=M("desk",(.015,.022,.035),metal=.2); BLACK=M("black",(.004,.007,.012),metal=.2); SCREEN=M("screen",(.01,.06,.12),rough=.25)
CYAN=M("cyan",(.02,.45,.9),emit=(.02,.65,1)); GREEN=M("green",(.03,.4,.12),emit=(.02,.7,.2)); WHITE=M("white",(.65,.8,.95)); AMBER=M("amber",(.7,.25,.02),emit=(1,.3,.02))

def cube(n,loc,sc,ma,bev=.03):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=n; o.scale=sc; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bev: q=o.modifiers.new("bevel","BEVEL"); q.width=bev; q.segments=2
    o.data.materials.append(ma); return o
def txt(s,loc,size=.16,ma=WHITE,align='LEFT'):
    c=bpy.data.curves.new("font","FONT"); c.body=s; c.align_x=align; c.size=size; c.extrude=.003
    o=bpy.data.objects.new(s,c); bpy.context.collection.objects.link(o); o.location=loc; o.data.materials.append(ma); return o
def light(loc,e,col,size):
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=e; l.data.color=col; l.data.shape='DISK'; l.data.size=size
def cam(loc):
    bpy.ops.object.camera_add(location=loc); c=bpy.context.object; c.data.lens=48; return c
def aim(c,target):
    c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=W; sc.render.resolution_y=H; sc.render.resolution_percentage=100; sc.render.fps=FPS
sc.world.color=(.002,.004,.009); sc.view_settings.look='AgX - Medium High Contrast'
cube("desk",(0,0,0),(5,4,.12),DARK,.06)
light((-3,-3,4),800,(.04,.3,1),3); light((3,1,3),650,(.02,.7,1),2)

# Physical laptop/workstation.
cube("monitor",(0,0,2.0),(2.35,.14,1.35),BLACK,.1); cube("display",(0,-.16,2.0),(2.08,.035,1.08),SCREEN,.03)
cube("base",(0,-1.05,.48),(2.5,.78,.08),BLACK,.08)
for r in range(5):
    for c in range(12): cube(f"k{r}{c}",(-1.8+c*.33,-1.27+r*.27,.59),(.115,.07,.018),WHITE,.008)

# UI is part of the 3D scene, so camera movement creates depth instead of flat slides.
txt("AI AGENT",(-1.65,-.21,2.48),.22,CYAN)
txt("PLAN  >  ACT  >  VERIFY",(-1.65,-.21,2.15),.13,WHITE)
apps=[("MAIL",-1.25,CYAN),("CODE",0,GREEN),("TERM",1.25,AMBER)]
for name,x,ma in apps:
    cube(name,(x,-.21,1.25),(.48,.025,.22),ma,.03); txt(name,(x-.27,-.25,1.2),.13,WHITE)

cur=cube("cursor",(-1.4,-.27,1.65),(.035,.02,.1),WHITE,.008)
def k(obj,t,p):
    obj.location=p; obj.keyframe_insert("location",frame=int(t*FPS))
for t,p in [(0.4,(-1.0,-.27,1.25)),(3.3,(0,-.27,1.25)),(6.4,(1.0,-.27,1.25)),(9.5,(-.7,-.27,2.0)),(12.6,(.8,-.27,2.0))]: k(cur,t,p)
for t,p in [(1.0,(-.9,-.27,1.25)),(4.0,(.05,-.27,1.25)),(7.1,(1.05,-.27,1.25)),(10.4,(-.65,-.27,2.0)),(13.4,(.85,-.27,2.0))]: k(cur,t,p)

C=cam((-4.2,-8,3.0)); sc.camera=C
shots=[(0,3.1,(-4.2,-8,3.0),(-1.8,-6.5,2.2)),(3.1,6.2,(3.8,-7.2,2.8),(1.0,-6,2.0)),(6.2,9.3,(-3.2,-7.6,2.3),(1.8,-6.1,2.2)),(9.3,12.4,(3.5,-7.5,3.1),(-.8,-6.1,2.0)),(12.4,15.5,(-3.4,-7.1,2.7),(2.1,-6.1,2.0)),(15.5,18.6,(2.8,-7.8,3.8),(0,-6.0,1.8))]
for a,b,p,q in shots:
    C.location=p; C.keyframe_insert("location",frame=int(a*FPS)); C.location=q; C.keyframe_insert("location",frame=int(b*FPS)); aim(C,q); C.keyframe_insert("rotation_euler",frame=int(b*FPS))
C.data.dof.use_dof=True; C.data.dof.focus_object=bpy.data.objects["display"]; C.data.dof.aperture_fstop=2.4

# Kinetic status words.
for t,s,ma in [(0.7,"OPEN",CYAN),(4.1,"RUN",GREEN),(7.2,"READ",CYAN),(10.7,"TEST",AMBER),(13.8,"DONE",GREEN)]:
    o=txt(s,(1.15,-.3,.75),.19,ma); o.scale=(.01,)*3; o.keyframe_insert("scale",frame=int((t-.15)*FPS)); o.scale=(1,1,1); o.keyframe_insert("scale",frame=int(t*FPS))

brand=txt("TECHMIND",(0,-.45,.95),.56,CYAN,'CENTER'); brand.scale=(.01,)*3; brand.keyframe_insert("scale",frame=int(15.7*FPS)); brand.scale=(1,1,1); brand.keyframe_insert("scale",frame=int(16.2*FPS))
tag=txt("AI + COMPUTER + ACTION",(0,-.45,.48),.17,WHITE,'CENTER'); tag.scale=(.01,)*3; tag.keyframe_insert("scale",frame=int(16.1*FPS)); tag.scale=(1,1,1); tag.keyframe_insert("scale",frame=int(16.6*FPS))

sc.frame_start=1; sc.frame_end=int(D*FPS); sc.render.image_settings.file_format='FFMPEG'; sc.render.ffmpeg.format='MPEG4'; sc.render.ffmpeg.codec='H264'; sc.render.ffmpeg.constant_rate_factor='MEDIUM'; sc.render.filepath=str(MP4)
bpy.ops.render.render(animation=True)
print("BLENDER_DONE="+str(MP4))

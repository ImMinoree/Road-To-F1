"""Fit the supplied MakeHuman character; preserve both source .blend files."""
import bpy, math, json, os, hashlib
from pathlib import Path
from mathutils import Vector,Matrix

ART=Path(r'D:\Boring\GitHub\Road-To-F1-New\Road_To_F1_New\Art')
OUT=ART/'DesertKarting/KartDriver_Fitted'; OUT.mkdir(exist_ok=True)
BASE=ART/'HumanBase/KartDriver_Base.blend'
KART=ART/'DesertKarting/Kart/Kart_Reference.blend'
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE,KART)}
bpy.ops.wm.open_mainfile(filepath=str(KART))
kart_objects=list(bpy.context.scene.objects)
kart_signature={o.name: {'verts':len(o.data.vertices),'matrix':[list(r) for r in o.matrix_world]} for o in kart_objects if o.type=='MESH'}
human_collection=bpy.data.collections.new('MakeHuman | fitted original character');bpy.context.scene.collection.children.link(human_collection)
with bpy.data.libraries.load(str(BASE),link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n in ['Game_engine','kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh','high-polyMesh']]
human=list(dst.objects)
for o in human:human_collection.objects.link(o)
arm=next(o for o in human if o.type=='ARMATURE')
body=next(o for o in human if o.name.startswith('kart_driverMesh'))

# The companion FBX has identical vertices and the original MakeHuman weights.
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(ART/'HumanBase/KartDriver_Rigged.fbx'))
imported=list(set(bpy.data.objects)-before)
matches={'kart_driverMesh':'kartdriver_riggedMesh','male_casualsuit04Mesh':'male_casualsuit04Mesh','shoes05Mesh':'shoes05Mesh','high-polyMesh':'high-polyMesh'}
binding_report={}
for original in [o for o in human if o.type=='MESH']:
 key=next(k for k in matches if original.name.startswith(k))
 source=next(o for o in imported if o.type=='MESH' and o.name.startswith(matches[key]))
 assert len(original.data.vertices)==len(source.data.vertices)
 delta=max((a.co-b.co).length for a,b in zip(original.data.vertices,source.data.vertices))
 assert delta<.001,(original.name,delta)
 if not original.vertex_groups:
  for g in source.vertex_groups:original.vertex_groups.new(name=g.name)
  for v in source.data.vertices:
   for w in v.groups:original.vertex_groups[w.group].add([v.index],w.weight,'REPLACE')
 modifier=next((m for m in original.modifiers if m.type=='ARMATURE'),None) or original.modifiers.new('MakeHuman original skin binding','ARMATURE')
 modifier.object=arm;modifier.use_deform_preserve_volume=True
 binding_report[original.name]={'groups':len(original.vertex_groups),'max_source_vertex_delta':delta,'weight_origin':'Original companion KartDriver_Rigged.fbx, exact vertex correspondence'}
for o in imported:bpy.data.objects.remove(o,do_unlink=True)

# Source body is Y-up; source bone rest data is already Z-up.
S=.0112 # 160.3 source units -> 1.795 m adult stature, uniform scale only.
rz=Matrix.Rotation(math.pi/2,4,'Z');rx=Matrix.Rotation(math.pi/2,4,'X')
arm.matrix_world=rz@Matrix.Scale(S,4)
for o in human:
 if o.type=='MESH':
  o.parent=None;o.matrix_world=rz@rx@Matrix.Scale(S,4)
  for p in o.data.polygons:p.use_smooth=True
  if o.data.has_custom_normals:
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
   bpy.ops.mesh.customdata_custom_splitnormals_clear()

# Resolve source image paths relative to HumanBase, retaining original materials.
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:
  candidate=ART/'HumanBase/textures'/Path(im.filepath.replace('\\','/')).name
  if candidate.exists():im.filepath=str(candidate);im.reload()

scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
pb=arm.pose.bones
def world_head(name):return arm.matrix_world@pb[name].head
def world_tail(name):return arm.matrix_world@pb[name].tail
def aim(name,target):
 b=pb[name];current=(world_tail(name)-world_head(name)).normalized()
 desired=(Vector(target)-world_head(name)).normalized()
 q=current.rotation_difference(desired)
 wm=arm.matrix_world@b.matrix
 wm=Matrix.Translation(wm.translation)@q.to_matrix().to_4x4()@Matrix.Translation(-wm.translation)@wm
 b.matrix=arm.matrix_world.inverted()@wm
 bpy.context.view_layer.update()

# Translate whole character to put the hip joint inside the open seat pan.
hip_target=Vector((.100,0,.505))
shift=hip_target-world_head('pelvis')
for o in human:o.matrix_world.translation+=shift
bpy.context.view_layer.update()
# Mild rearward trunk lean, independent of lower limbs.
pelvis=world_head('pelvis');torso=world_head('neck_01')-pelvis
q=torso.normalized().rotation_difference(Vector((-.055,0,.55)).normalized())
wm=arm.matrix_world@pb['pelvis'].matrix
wm=Matrix.Translation(pelvis)@q.to_matrix().to_4x4()@Matrix.Translation(-pelvis)@wm
pb['pelvis'].matrix=arm.matrix_world.inverted()@wm
bpy.context.view_layer.update()

controls=bpy.data.collections.new('Fit controls | IK wrists and ankles');scene.collection.children.link(controls)
def empty(name,point):
 o=bpy.data.objects.new(name,None);controls.objects.link(o);o.location=point;o.empty_display_type='SPHERE';o.empty_display_size=.025;o.hide_render=True;return o

# Solve two-bone chains analytically, retaining existing bone lengths and weights.
def solve_two(upper,lower,end,pole):
 A=world_head(upper);D=Vector(end);direction=(D-A).normalized()
 L1=(world_tail(upper)-A).length;L2=(world_tail(lower)-world_head(lower)).length
 distance=(D-A).length
 if distance>L1+L2-.0001:raise RuntimeError(f'{upper} target unreachable: {distance:.3f}>{L1+L2:.3f}')
 bend=Vector(pole)-A;bend=(bend-direction*bend.dot(direction)).normalized()
 along=(L1*L1-L2*L2+distance*distance)/(2*distance)
 height=math.sqrt(max(0,L1*L1-along*along))
 elbow=A+direction*along+bend*height
 aim(upper,elbow);aim(lower,D)
 return {'target':list(D),'joint':list(elbow),'actual_error_m':(world_tail(lower)-D).length,'lengths_m':[L1,L2]}

fits={}
for side,sign in [('l',1),('r',-1)]:
 # Wrist stays behind the wheel; fingers extend toward and close over its rim.
 wrist=Vector((.505,sign*.225,.710))
 fits['arm_'+side]=solve_two('upperarm_'+side,'lowerarm_'+side,wrist,(.25,sign*.43,.65))
 aim('hand_'+side,wrist+Vector((.10,0,-.015)))
 # Roll the palm so the fingers spread vertically, with thumbs uppermost.
 long=(world_tail('hand_'+side)-world_head('hand_'+side)).normalized()
 across=world_head('index_01_'+side)-world_head('pinky_01_'+side)
 across=(across-long*across.dot(long)).normalized()
 wanted=Vector((0,0,1));wanted=(wanted-long*wanted.dot(long)).normalized()
 q=across.rotation_difference(wanted)
 wm=arm.matrix_world@pb['hand_'+side].matrix
 pb['hand_'+side].matrix=arm.matrix_world.inverted()@(Matrix.Translation(wrist)@q.to_matrix().to_4x4()@Matrix.Translation(-wrist)@wm)
 bpy.context.view_layer.update()
 empty('Wrist fit '+side,wrist)
 # Feet lie on the pedal tops; knees bend forward and rise inside the cockpit.
 ankle=Vector((.385,sign*.205,.286))
 fits['leg_'+side]=solve_two('thigh_'+side,'calf_'+side,ankle,(.68,sign*.30,.86))
 aim('foot_'+side,ankle+Vector((.076,-sign*.012,-.068)))
 aim('ball_'+side,world_head('ball_'+side)+Vector((.12,-sign*.020,-.012)))
 empty('Ankle fit '+side,ankle)

# Keep head vertical with its source face axis +X; remove inherited torso tilt.
aim('neck_01',world_head('neck_01')+Vector((.012,0,.12)))
aim('head',world_head('head')+Vector((0,0,.12)))

# Curl the original finger bones around the wheel grip; no replacement hand mesh.
for side,sign in [('l',1),('r',-1)]:
 for digit in ('index','middle','ring','pinky'):
  for segment,direction in [('01',(1,-sign*.2,0)),('02',(.45,-sign*.9,0)),('03',(-.65,-sign*.7,0))]:
   name=f'{digit}_{segment}_{side}'
   aim(name,world_head(name)+Vector(direction)*.1)
 # Opposed thumbs lie across the upper, inside quadrant of the rim.
 for seg,target in [('01',(.59,sign*.18,.745)),('02',(.62,sign*.17,.73)),('03',(.63,sign*.18,.71))]:
  aim(f'thumb_{seg}_{side}',target)
bpy.context.view_layer.update()

# Store a separate posed action without touching source animation files.
for b in pb:
 b.rotation_mode='QUATERNION' if b.rotation_mode=='QUATERNION' else b.rotation_mode
 b.keyframe_insert(data_path='location',frame=1)
 b.keyframe_insert(data_path='rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1)
 b.keyframe_insert(data_path='scale',frame=1)
if arm.animation_data and arm.animation_data.action:arm.animation_data.action.name='Kart | seated fit inspection'
arm.show_in_front=True;arm['Fit notes']='Original MakeHuman skeleton; original FBX weights restored by identical vertex correspondence. Kart untouched. Seated static fit, not Unreal imported.'

def camera(name,location,target,lens=55,ortho=None):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=location;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return o
views={
 'front':camera('Fit inspection | front',(3.6,0,1.25),(.05,0,.69),58),
 'side':camera('Fit inspection | side',(.05,-3.6,1.00),(.05,0,.70),55,2.55),
 'three_quarter':camera('Fit inspection | three quarter',(2.65,-3.45,2.03),(.03,0,.70),58),
}
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1080;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.camera=views['three_quarter']
scene['Fit source']='Art/HumanBase/KartDriver_Base.blend; skin bindings recovered from its companion KartDriver_Rigged.fbx'
scene['Kart unchanged']='Original component geometry, object transforms and materials preserved.'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_distance=3.5;area.spaces.active.region_3d.view_location=Vector((.05,0,.7))
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);bpy.context.view_layer.objects.active=arm
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted.blend'))
report={'source_hashes':hashes,'source_files_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items()),'character_stature_m':1.795,'bindings':binding_report,'fit':fits,'kart_unchanged':all(o.name in kart_signature and len(o.data.vertices)==kart_signature[o.name]['verts'] and [list(r) for r in o.matrix_world]==kart_signature[o.name]['matrix'] for o in kart_objects if o.type=='MESH'),'bone_heads':{n:list(world_head(n)) for n in ('pelvis','head','upperarm_l','upperarm_r','hand_l','hand_r','thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r')}}
(OUT/'fit_validation.json').write_text(json.dumps(report,indent=2))
for name,cam in views.items():
 scene.camera=cam;scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
print('FIT_COMPLETE',json.dumps(report),flush=True)

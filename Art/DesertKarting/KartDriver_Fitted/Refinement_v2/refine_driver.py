"""Refine only the supplied scene's pose. No source geometry or weight edits."""
import sys,math,json,hashlib,struct
from pathlib import Path
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import probe_pose as fit
bpy=fit.bpy;scene=fit.scene;arm=fit.arm;pb=fit.pb
def digest(data):return hashlib.sha256(json.dumps(data,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def invariant():
 result={}
 for o in scene.objects:
  if o.type=='MESH':
   result[o.name]={'geometry':digest([[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]]),'weights':digest([[g.name for g in o.vertex_groups],[[[w.group,w.weight] for w in v.groups] for v in o.data.vertices]]),'materials':[m.name if m else None for m in o.data.materials]}
   if o.name.startswith('SK_Kart_'):result[o.name]['matrix']=list(map(list,o.matrix_world))
 result['ARMATURE_REST']=digest([[b.name,b.parent.name if b.parent else None,list(map(list,b.matrix_local)),b.use_deform] for b in arm.data.bones])
 return result
before_signature=invariant()
source_hash=hashlib.sha256((fit.ROOT/'Kart_With_MakeHuman_Fitted.blend').read_bytes()).hexdigest()
baseline=fit.metrics()

def camera(name,location,target,ortho):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
 o.location=location;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=ortho
 return o
views={
 'front':camera('Refinement | front',(4,0,1.05),(.04,0,.68),2.5),
 'side':camera('Refinement | side',(0,-4,1.0),(.04,0,.68),2.5),
 'top':camera('Refinement | top',(.05,0,4.4),(.05,0,0),2.55),
 'three_quarter':camera('Refinement | three quarter',(2.7,-3.4,2.2),(.04,0,.68),2.6),
}
scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
def render_set(label):
 for name,cam in views.items():
  scene.camera=cam;scene.render.filepath=str(HERE/f'{label}_{name}.png');bpy.ops.render.render(write_still=True)
if '--skip-before' not in sys.argv:render_set('before')

params={'hip_x':.10,'hip_z':.52,'lean_deg':-5,'ankle_x':.48,'knee_pole_y':.45,'knee_pole_z':.65}
assert fit.pose(params)

# Grip: align the real index-to-pinky knuckle line to the wheel's tangent.
for side,s in [('l',1),('r',-1)]:
 wrist=Vector((.490,s*.225,.715))
 assert fit.two('upperarm_'+side,'lowerarm_'+side,wrist,(.26,s*.39,.68))
 wm=fit.original_hand_world[side].copy();wm.translation=wrist
 pb['hand_'+side].matrix=arm.matrix_world.inverted()@wm;bpy.context.view_layer.update()
 across=fit.head('index_01_'+side)-fit.head('pinky_01_'+side)
 fit.rotate('hand_'+side,across.normalized().rotation_difference(Vector((0,0,1))))
 for digit in ('index','middle','ring','pinky'):
  z=fit.head(digit+'_01_'+side).z
  ring_y=math.sqrt(max(.001,.184**2-(z-.70)**2))
  if digit=='pinky':
   targets=[(.625,s*(ring_y+.028),z),(.642,s*(ring_y+.022),z),(.648,s*(ring_y+.008),z)]
  else:targets=[(.636,s*(ring_y+.026),z),(.650,s*ring_y,z),(.636,s*(ring_y-.027),z)]
  for i,t in enumerate(targets,1):fit.aim(f'{digit}_{i:02}_{side}',t)
 for seg,t in [('01',(.596,s*.191,.748)),('02',(.625,s*.167,.736)),('03',(.645,s*.175,.722))]:fit.aim('thumb_'+seg+'_'+side,t)

# Flat soles, using the source foot's anatomical ankle/ball directions.
for side,s in [('l',1),('r',-1)]:
 ankle=Vector((.470,s*.187,.255))
 assert fit.two('thigh_'+side,'calf_'+side,ankle,(.68,s*.45,.65))
 fit.aim('foot_'+side,ankle+Vector((.120,-s*.004,-.063)))
 fit.aim('ball_'+side,fit.head('ball_'+side)+Vector((.134,-s*.006,-.006)))
bpy.context.view_layer.update()

# Source rig weights remain immutable. Only pose rotations/translations are saved.
for o in scene.objects:
 if o.name.startswith('Wrist fit '):o.location=fit.head('hand_'+o.name[-1])
 if o.name.startswith('Ankle fit '):o.location=fit.head('foot_'+o.name[-1])
for b in pb:
 b.keyframe_insert(data_path='location',frame=1)
 b.keyframe_insert(data_path='rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1)
 b.keyframe_insert(data_path='scale',frame=1)
if arm.animation_data and arm.animation_data.action:arm.animation_data.action.name='Kart | seating refinement v2'
scene.camera=views['three_quarter'];scene['Fit status']='Incomplete: original fuel tank continues to occupy the lap; see validation_v2.json and actual comparison renders.'
new_path=HERE/'Kart_With_MakeHuman_Fitted_v2.blend'
assert before_signature==invariant(),'Source geometry, weights, rest skeleton or kart transform changed'
bpy.ops.wm.save_as_mainfile(filepath=str(new_path))
after=fit.metrics()
validation={'source_file':str(fit.ROOT/'Kart_With_MakeHuman_Fitted.blend'),'source_sha256':source_hash,'source_unchanged':hashlib.sha256((fit.ROOT/'Kart_With_MakeHuman_Fitted.blend').read_bytes()).hexdigest()==source_hash,'geometry_weights_rest_skeleton_and_kart_transforms_unchanged':before_signature==invariant(),'before':baseline,'after':after,'pose_parameters':params,'joint_positions':{n:list(fit.head(n)) for n in ('pelvis','neck_01','upperarm_l','upperarm_r','hand_l','hand_r','calf_l','calf_r','foot_l','foot_r')},'status':'Incomplete; collisions require further review, not a collision-free fit.'}
(HERE/'validation_v2.json').write_text(json.dumps(validation,indent=2))
render_set('refined')
print('REFINEMENT_V2',json.dumps(validation),flush=True)

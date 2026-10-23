import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent;SOURCE=OUT.parent/'Refinement_v2/Kart_With_MakeHuman_Fitted_v2.blend';FINAL=OUT/'Kart_With_MakeHuman_Fitted_v3.blend'
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def head(arm,n):return arm.matrix_world@arm.pose.bones[n].head
def signature():
 result={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   result[o.name]={'geometry':digest([[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]]),'weights':digest([[g.name for g in o.vertex_groups],[[[w.group,w.weight] for w in v.groups] for v in o.data.vertices]]),'materials':[m.name if m else None for m in o.data.materials]}
   if o.name.startswith('SK_Kart_'):result[o.name]['matrix']=list(map(list,o.matrix_world))
 arm=bpy.data.objects['Game_engine'];result['rest_rig']=digest([[b.name,b.parent.name if b.parent else None,list(map(list,b.matrix_local))] for b in arm.data.bones])
 return result
def geometry(o,deps):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
def collisions():
 deps=bpy.context.evaluated_depsgraph_get();trees={o.name:BVHTree.FromPolygons(*geometry(o,deps)) for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')};report={}
 for name in ('kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh'):
  tree=BVHTree.FromPolygons(*geometry(bpy.data.objects[name],deps));report[name]={n:len(tree.overlap(t)) for n,t in trees.items() if tree.overlap(t)}
 return report
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));before=signature();before_collisions=collisions();arm=bpy.data.objects['Game_engine']
lengths={b.name:(arm.matrix_world.to_3x3()@(b.tail-b.head)).length for b in arm.pose.bones}
control_heads={n:head(arm,n).copy() for n in ('hand_l','hand_r','foot_l','foot_r')}
bpy.ops.wm.open_mainfile(filepath=str(FINAL));after=signature();after_collisions=collisions();arm=bpy.data.objects['Game_engine']
assert before==after,'Geometry, weights, material assignments, rest rig or kart/tank transforms changed'
length_delta=max(abs((arm.matrix_world.to_3x3()@(b.tail-b.head)).length-lengths[b.name]) for b in arm.pose.bones)
assert length_delta<.00001,('Bone stretch',length_delta)
control_error={n:(head(arm,n)-p).length for n,p in control_heads.items()};assert max(control_error.values())<.00001
recline=json.loads((OUT/'recline_validation.json').read_text())
report={'source':str(SOURCE),'source_sha256':source_hash,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,'mesh_geometry_weights_material_assignments_rest_rig_and_all_kart_transforms_unchanged':before==after,'refined_v2_tank_placement_unchanged':True,'maximum_bone_length_difference_m':length_delta,'wrist_ankle_world_position_errors_m':control_error,'selected_pose':recline['selected'],'support_and_reach':recline['after'],'before_intersections':before_collisions,'after_intersections':after_collisions,'status':'Rearward recline improved. Hips/lower back are closer to seat; full backrest contact is not achieved. Residual garment/seat/bodywork and shoe/chassis/axle contacts remain.'}
(OUT/'validation_final.json').write_text(json.dumps(report,indent=2))
scene=bpy.context.scene;scene['Fit status']=report['status'];scene['Preservation']='v2 mesh geometry, armature rest skeleton, skin weights, materials and every kart transform including the refined tank retained.'
scene.camera=bpy.data.objects['Refinement | three quarter'];scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL))
for name,camera_name in [('front','front'),('side','side'),('three_quarter','three quarter')]:
 scene.camera=bpy.data.objects['Refinement | '+camera_name];scene.render.filepath=str(OUT/f'reclined_{name}.png');bpy.ops.render.render(write_still=True)
print('RECLINE_FINAL',json.dumps(report),flush=True)

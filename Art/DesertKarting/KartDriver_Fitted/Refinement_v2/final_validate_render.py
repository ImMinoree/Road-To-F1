import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent;SOURCE=OUT.parent/'Kart_With_MakeHuman_Fitted.blend';FINAL=OUT/'Kart_With_MakeHuman_Fitted_v2.blend'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
def signature():
 result={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   result[o.name]={'geometry':digest([[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]]),'weights':digest([[g.name for g in o.vertex_groups],[[[w.group,w.weight] for w in v.groups] for v in o.data.vertices]]),'materials':[m.name if m else None for m in o.data.materials]}
   if o.name.startswith('SK_Kart_'):result[o.name]['matrix']=list(map(list,o.matrix_world))
 arm=bpy.data.objects['Game_engine']
 result['rest_skeleton']=digest([[b.name,b.parent.name if b.parent else None,list(map(list,b.matrix_local))] for b in arm.data.bones])
 return result
def geometry(o,deps):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
def collision_report():
 deps=bpy.context.evaluated_depsgraph_get();kart=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')]
 trees={o.name:BVHTree.FromPolygons(*geometry(o,deps)) for o in kart};result={}
 for name in ('kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh'):
  tree=BVHTree.FromPolygons(*geometry(bpy.data.objects[name],deps));result[name]={n:len(tree.overlap(t)) for n,t in trees.items() if tree.overlap(t)}
 tank=[o for o in kart if o.name.startswith('SK_Kart_Fuel_Tank_And_Cap')];others=[o for o in kart if o not in tank]+[bpy.data.objects[n] for n in ('kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh')]
 tank_report={}
 for o in tank:
  tree=trees[o.name]
  for other in others:
   t=trees.get(other.name) or BVHTree.FromPolygons(*geometry(other,deps))
   hits=tree.overlap(t)
   if hits:tank_report[o.name+' / '+other.name]=len(hits)
 result['tank_assembly_against_driver_and_all_other_kart_parts']=tank_report
 return result
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));original=signature();before=collision_report()
arm=bpy.data.objects['Game_engine'];original_lengths={b.name:(arm.matrix_world.to_3x3()@(b.tail-b.head)).length for b in arm.pose.bones}
bpy.ops.wm.open_mainfile(filepath=str(FINAL));updated=signature();after=collision_report();arm=bpy.data.objects['Game_engine']
changed_geometry=[n for n in original if n!='rest_skeleton' and original[n]['geometry']!=updated[n]['geometry']]
changed_weights=[n for n in original if n!='rest_skeleton' and original[n]['weights']!=updated[n]['weights']]
changed_transforms=[n for n in original if n.startswith('SK_Kart_') and original[n]['matrix']!=updated[n]['matrix']]
assert not changed_geometry and not changed_weights and original['rest_skeleton']==updated['rest_skeleton']
assert all(n.startswith('SK_Kart_Fuel_Tank_And_Cap') for n in changed_transforms)
def head(n):return arm.matrix_world@arm.pose.bones[n].head
def flex(a,b,c):
 A=head(a);B=head(b);C=head(c);return 180-math.degrees((A-B).angle(C-B))
length_change=max(abs((arm.matrix_world.to_3x3()@(b.tail-b.head)).length-original_lengths[b.name]) for b in arm.pose.bones)
assert length_change<.00001,('Unexpected bone stretch',length_change)
report={'source_file_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,'source_sha256':source_hash,'changed_mesh_geometry':changed_geometry,'changed_skin_weights':changed_weights,'rest_skeleton_unchanged':original['rest_skeleton']==updated['rest_skeleton'],'kart_parts_with_transform_changes':changed_transforms,'only_authorized_tank_transforms_changed':all(n.startswith('SK_Kart_Fuel_Tank_And_Cap') for n in changed_transforms),'maximum_posed_bone_length_change_m':length_change,'before_collisions':before,'after_collisions':after,'joint_positions':{n:list(head(n)) for n in ('pelvis','neck_01','upperarm_l','upperarm_r','hand_l','hand_r','thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r')},'elbow_flexion_deg':[flex('upperarm_'+s,'lowerarm_'+s,'hand_'+s) for s in ('l','r')],'knee_flexion_deg':[flex('thigh_'+s,'calf_'+s,'foot_'+s) for s in ('l','r')],'fit_status':'Tank and wheel rim clear. Residual garment/seat-rib and lower-leg/shoe contacts with unchanged chassis, axle and hoses remain. Not a fully collision-free production fit.'}
(OUT/'validation_final.json').write_text(json.dumps(report,indent=2))
scene=bpy.context.scene;scene['Fit status']=report['fit_status'];scene['Geometry and weights']='Validated unchanged from original fitted source. Only authorized tank assembly world transforms changed.'
for side in ('l','r'):
 bpy.data.objects['Wrist fit '+side].location=head('hand_'+side);bpy.data.objects['Ankle fit '+side].location=head('foot_'+side)
scene.camera=bpy.data.objects['Refinement | three quarter'];scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
if '--validate-only' not in sys.argv:
 bpy.ops.wm.save_as_mainfile(filepath=str(FINAL))
 for name,cam_name in [('front','front'),('side','side'),('top','top'),('three_quarter','three quarter')]:
  scene.camera=bpy.data.objects['Refinement | '+cam_name];scene.render.filepath=str(OUT/f'refined_{name}.png');bpy.ops.render.render(write_still=True)
print('FINAL_VALIDATION',json.dumps(report),flush=True)

import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
arm=bpy.data.objects['Game_engine'];pb=arm.pose.bones
if arm.animation_data:arm.animation_data.action=None
human=[bpy.data.objects[n] for n in ('Game_engine','kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh','high-polyMesh')]
original_mats={o.name:o.matrix_world.copy() for o in human};original_pose={b.name:b.matrix_basis.copy() for b in pb}
deps=bpy.context.evaluated_depsgraph_get()
def head(n):return arm.matrix_world@pb[n].head
def tail(n):return arm.matrix_world@pb[n].tail
def rotate(n,q):
 p=head(n);m=arm.matrix_world@pb[n].matrix;pb[n].matrix=arm.matrix_world.inverted()@(Matrix.Translation(p)@q.to_matrix().to_4x4()@Matrix.Translation(-p)@m);bpy.context.view_layer.update()
def aim(n,t):rotate(n,(tail(n)-head(n)).normalized().rotation_difference((Vector(t)-head(n)).normalized()))
def two(upper,lower,D,pole):
 A=head(upper);u=(D-A).normalized();d=(D-A).length;l1=(tail(upper)-A).length;l2=(tail(lower)-head(lower)).length
 if not abs(l1-l2)+.001<d<l1+l2-.001:return False
 v=pole-A;v=(v-u*v.dot(u)).normalized();a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-a*a));aim(upper,A+u*a+v*h);aim(lower,D);return True
hands={s:arm.matrix_world@pb['hand_'+s].matrix for s in ('l','r')};feet={s:arm.matrix_world@pb['foot_'+s].matrix for s in ('l','r')}
def geometry(o):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
relevant=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_') and any(s in o.name for s in ('Seat','Fuel_Tank','Steering_Column'))]
trees={o.name:BVHTree.FromPolygons(*geometry(o)) for o in relevant}
seat_trees={n:t for n,t in trees.items() if 'Seat' in n}
cloth=bpy.data.objects['male_casualsuit04Mesh'];pelvis_ids={v.index for v in cloth.data.vertices if any(cloth.vertex_groups[w.group].name=='pelvis' and w.weight>.3 for w in v.groups)}
def pose(x,z,lean):
 for o in human:o.matrix_world=original_mats[o.name].copy()
 for b in pb:b.matrix_basis=original_pose[b.name].copy()
 bpy.context.view_layer.update()
 delta=Vector((x,0,z))-head('pelvis')
 for o in human:o.matrix_world.translation+=delta
 bpy.context.view_layer.update();r=math.radians(lean)
 rotate('pelvis',(head('neck_01')-head('pelvis')).normalized().rotation_difference(Vector((math.sin(r),0,math.cos(r)))))
 for s,sign in [('l',1),('r',-1)]:
  if not two('upperarm_'+s,'lowerarm_'+s,hands[s].translation,Vector((.26,sign*.39,.68))):return False
  pb['hand_'+s].matrix=arm.matrix_world.inverted()@hands[s];bpy.context.view_layer.update()
  if not two('thigh_'+s,'calf_'+s,feet[s].translation,Vector((.68,sign*.45,.65))):return False
  pb['foot_'+s].matrix=arm.matrix_world.inverted()@feet[s];bpy.context.view_layer.update()
 aim('neck_01',head('neck_01')+Vector((.008,0,.13)));aim('head',head('head')+Vector((0,0,.13)))
 return True
def measure():
 v,f=geometry(cloth);t=BVHTree.FromPolygons(v,f);hits={n:len(t.overlap(bt)) for n,bt in trees.items() if t.overlap(bt)}
 seat=sum(k for n,k in hits.items() if 'Seat' in n);other=sum(k for n,k in hits.items() if 'Seat' not in n)
 contact=min(min(bt.find_nearest(v[i])[3] for i in pelvis_ids) for bt in seat_trees.values())
 # A contact-near pose with zero surface intersections is preferred.
 score=seat+other*3+max(0,contact-.004)*5000+abs(head('pelvis').z-.52)*20
 return {'seat_surface_pairs':seat,'other_surface_pairs':other,'pelvic_garment_minimum_seat_distance_m':contact,'score':score,'hits':hits,'knees':[list(head('calf_l')),list(head('calf_r'))]}
baseline=measure();records=[]
for x in (-.06,-.02,.02,.06,.10,.12):
 for z in (.52,.54,.56,.58,.60,.62):
  for lean in (-5,5,15,25):
   if pose(x,z,lean):records.append({'params':[x,z,lean],'metrics':measure()})
records.sort(key=lambda r:r['metrics']['score']);best=records[0]
(OUT/'seat_probe.json').write_text(json.dumps({'baseline':baseline,'selected':best,'candidates':records},indent=2))
print('SEAT_TOP',json.dumps(records[:5]),flush=True)
# Save only if the candidate improves contacts and remains close to seat support.
if best['metrics']['score']<baseline['score'] and best['metrics']['pelvic_garment_minimum_seat_distance_m']<.008:
 pose(*best['params'])
 for b in pb:
  b.keyframe_insert(data_path='location',frame=1);b.keyframe_insert(data_path='rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1);b.keyframe_insert(data_path='scale',frame=1)
 if arm.animation_data and arm.animation_data.action:arm.animation_data.action.name='Kart | seating refinement v2 final pose'
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
 print('SEAT_ADJUSTMENT_SAVED',best['params'],flush=True)

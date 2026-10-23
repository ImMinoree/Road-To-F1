"""Seat-support search with independent pelvis and torso rotations."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
arm=bpy.data.objects['Game_engine'];pb=arm.pose.bones
if arm.animation_data:arm.animation_data.action=None
human=[bpy.data.objects[n] for n in ('Game_engine','kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh','high-polyMesh')]
mats={o.name:o.matrix_world.copy() for o in human};basis={b.name:b.matrix_basis.copy() for b in pb};deps=bpy.context.evaluated_depsgraph_get()
def head(n):return arm.matrix_world@pb[n].head
def tail(n):return arm.matrix_world@pb[n].tail
hands={s:arm.matrix_world@pb['hand_'+s].matrix for s in ('l','r')};feet={s:arm.matrix_world@pb['foot_'+s].matrix for s in ('l','r')}
def rotate(n,q):
 p=head(n);m=arm.matrix_world@pb[n].matrix;pb[n].matrix=arm.matrix_world.inverted()@(Matrix.Translation(p)@q.to_matrix().to_4x4()@Matrix.Translation(-p)@m);bpy.context.view_layer.update()
def aim(n,t):rotate(n,(tail(n)-head(n)).normalized().rotation_difference((Vector(t)-head(n)).normalized()))
def two(a,b,D,pole):
 A=head(a);u=(D-A).normalized();d=(D-A).length;l1=(tail(a)-A).length;l2=(tail(b)-head(b)).length
 if not abs(l1-l2)+.001<d<l1+l2-.001:return False
 v=pole-A;v=(v-u*v.dot(u)).normalized();p=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-p*p));aim(a,A+u*p+v*h);aim(b,D);return True
def geom(o):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
cloth=bpy.data.objects['male_casualsuit04Mesh']
glutes=[v.index for v in cloth.data.vertices if v.co.z<0 and v.co.y<90 and any(cloth.vertex_groups[w.group].name=='pelvis' and w.weight>.4 for w in v.groups)]
print('GLUTE_LANDMARKS',len(glutes),flush=True)
so=bpy.data.objects['SK_Kart_Seat_Sculpted_Tub_Seat_Moulded_Polymer'];v,f=geom(so)
sheet=BVHTree.FromPolygons(v,[p for p in f if all(i<759 for i in p)])
relevant=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_') and any(s in o.name for s in ('Seat','Fuel_Tank','Steering_Column'))]
trees={o.name:BVHTree.FromPolygons(*geom(o)) for o in relevant}
def pose(x,z,lean,posterior):
 for o in human:o.matrix_world=mats[o.name].copy()
 for b in pb:
  b.matrix_basis=basis[b.name].copy() if any(n in b.name for n in ('thumb','index','middle','ring','pinky','ball')) else Matrix.Identity(4)
 bpy.context.view_layer.update()
 delta=Vector((x,0,z))-head('pelvis')
 for o in human:o.matrix_world.translation+=delta
 bpy.context.view_layer.update();h=(head('neck_01')-head('pelvis')).length;r=math.radians(lean)
 target=head('pelvis')+Vector((h*math.sin(r),0,h*math.cos(r)))
 rotate('pelvis',(head('neck_01')-head('pelvis')).normalized().rotation_difference((target-head('pelvis')).normalized()))
 rotate('pelvis',Quaternion(Vector((0,1,0)),math.radians(posterior)))
 rotate('spine_01',(head('neck_01')-head('spine_01')).normalized().rotation_difference((target-head('spine_01')).normalized()))
 for s,sign in [('l',1),('r',-1)]:
  if not two('upperarm_'+s,'lowerarm_'+s,hands[s].translation,Vector((.26,sign*.39,.68))):return False
  pb['hand_'+s].matrix=arm.matrix_world.inverted()@hands[s];bpy.context.view_layer.update()
  if not two('thigh_'+s,'calf_'+s,feet[s].translation,Vector((.68,sign*.45,.65))):return False
  pb['foot_'+s].matrix=arm.matrix_world.inverted()@feet[s];bpy.context.view_layer.update()
 aim('neck_01',head('neck_01')+Vector((.008,0,.13)));aim('head',head('head')+Vector((0,0,.13)))
 return True
def metrics():
 v,f=geom(cloth);bt=BVHTree.FromPolygons(v,f);hits={n:len(bt.overlap(t)) for n,t in trees.items() if bt.overlap(t)}
 gaps=[]
 for i in glutes:
  p=v[i];near,n,_,d=sheet.find_nearest(p)
  if n.x<0:n=-n
  gaps.append((p-near).dot(n))
 gaps.sort();mean=sum(gaps[:max(1,len(gaps)//4)])/max(1,len(gaps)//4)
 # Require back/bottom glute contact with the seat sheet, rather than a nearest limb touching a rim.
 score=sum(hits.values())+max(0,mean-.015)*3000+max(0,-mean-.002)*3000
 return {'score':score,'hits':hits,'glute_signed_quartile_mean_m':mean,'glute_min_m':gaps[0],'glute_max_m':gaps[-1],'knees':[list(head('calf_l')),list(head('calf_r'))]}
records=[]
for x in (.02,.06,.10):
 for z in (.49,.52,.55,.58):
  for lean in (-5,5,15):
   for posterior in (-25,-10,0,10):
    if pose(x,z,lean,posterior):records.append({'params':[x,z,lean,posterior],'metrics':metrics()})
records.sort(key=lambda r:r['metrics']['score'])
# Do not trade natural pelvic tilt and actual support for a floating zero-pair pose.
supported=[r for r in records if -.002<=r['metrics']['glute_signed_quartile_mean_m']<=.008 and r['params'][3] in (-10,0) and abs(r['params'][2])<=15 and all('Seat_Texture_And_Mounts_Rubber_Grip' in n for n in r['metrics']['hits'])]
best=min(supported,key=lambda r:sum(r['metrics']['hits'].values())+abs(r['params'][2])*.5) if supported else records[0]
(OUT/'seat_support.json').write_text(json.dumps({'selected':best,'glute_landmark_count':len(glutes),'candidates':records},indent=2))
print('SEAT_SUPPORT_TOP',json.dumps(records[:5]),flush=True)
pose(*best['params'])
for b in pb:
 b.keyframe_insert(data_path='location',frame=1);b.keyframe_insert(data_path='rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1);b.keyframe_insert(data_path='scale',frame=1)
if arm.animation_data and arm.animation_data.action:arm.animation_data.action.name='Kart | seating refinement v2 supported pelvis'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))

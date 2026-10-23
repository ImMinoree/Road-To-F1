import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
arm=bpy.data.objects['Game_engine'];pb=arm.pose.bones
if arm.animation_data:arm.animation_data.action=None
deps=bpy.context.evaluated_depsgraph_get()
def head(n):return arm.matrix_world@pb[n].head
def tail(n):return arm.matrix_world@pb[n].tail
def aim(n,t):
 p=head(n);q=(tail(n)-p).normalized().rotation_difference((Vector(t)-p).normalized());m=arm.matrix_world@pb[n].matrix
 pb[n].matrix=arm.matrix_world.inverted()@(Matrix.Translation(p)@q.to_matrix().to_4x4()@Matrix.Translation(-p)@m);bpy.context.view_layer.update()
def two(a,b,D,pole):
 A=head(a);u=(D-A).normalized();d=(D-A).length;l1=(tail(a)-A).length;l2=(tail(b)-head(b)).length
 v=pole-A;v=(v-u*v.dot(u)).normalized();p=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-p*p));aim(a,A+u*p+v*h);aim(b,D)
def geom(o):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_') and any(n in o.name for n in ('Bodywork','Fuel_Tank','Steering_Column','Brake_Hydraulic'))]
trees={o.name:BVHTree.FromPolygons(*geom(o)) for o in parts};report={}
for s,sign in [('l',1),('r',-1)]:
 foot=arm.matrix_world@pb['foot_'+s].matrix;starting={n:pb[n].matrix_basis.copy() for n in ('thigh_'+s,'calf_'+s,'foot_'+s)}
 def setpole(y,z):
  for n,m in starting.items():pb[n].matrix_basis=m.copy()
  bpy.context.view_layer.update();two('thigh_'+s,'calf_'+s,foot.translation,Vector((.68,sign*y,z)));pb['foot_'+s].matrix=arm.matrix_world.inverted()@foot;bpy.context.view_layer.update()
 def measure():
  hits={}
  for name in ('kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh'):
   t=BVHTree.FromPolygons(*geom(bpy.data.objects[name]));hits[name]={n:len(t.overlap(bt)) for n,bt in trees.items() if t.overlap(bt)}
  knee=head('calf_'+s);hip=head('thigh_'+s)
  blocked=sum(v*1000 for hs in hits.values() for n,v in hs.items() if 'Fuel_Tank' in n or 'Steering_Column' in n)
  bodywork=sum(v for hs in hits.values() for n,v in hs.items() if 'Bodywork' in n)
  hoses=sum(v for hs in hits.values() for n,v in hs.items() if 'Brake_Hydraulic' in n)
  score=blocked+bodywork*5+hoses*.1+max(0,abs(knee.y)-.28)*3000+max(0,.23-abs(knee.y))*3000+abs(abs(knee.y)-.25)*10+max(0,knee.z-hip.z-.18)*1000
  return {'score':score,'hits':hits,'knee':list(knee)}
 before=measure();candidates=[]
 for y in (.20,.25,.30,.35,.40,.45):
  for z in (.55,.65,.75,.85):
   setpole(y,z);candidates.append({'pole':[y,z],'metrics':measure()})
 candidates.sort(key=lambda c:c['metrics']['score']);best=candidates[0];setpole(*best['pole']);report[s]={'before':before,'selected':best,'candidates':candidates}
 print('KNEE',s,json.dumps(best),flush=True)
for b in pb:
 b.keyframe_insert(data_path='location',frame=1);b.keyframe_insert(data_path='rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1);b.keyframe_insert(data_path='scale',frame=1)
if arm.animation_data and arm.animation_data.action:arm.animation_data.action.name='Kart | supported seated posture v2'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'));(OUT/'knee_fit.json').write_text(json.dumps(report,indent=2))

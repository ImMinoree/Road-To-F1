import bpy,math,json,numpy as np,sys
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;SOURCE=P.parent/'Racing_Visual_v4/Kart_With_MakeHuman_Racer_v4.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));arm=bpy.data.objects['Game_engine'];scene=bpy.context.scene
if arm.animation_data and arm.animation_data.action:arm.animation_data.action.use_fake_user=True;arm.animation_data.action=None
pb=arm.pose.bones;basis={b.name:b.matrix_basis.copy() for b in pb};deps=bpy.context.evaluated_depsgraph_get()
def head(n):return arm.matrix_world@pb[n].head
def tail(n):return arm.matrix_world@pb[n].tail
def aim(n,target):
 h=head(n);q=(tail(n)-h).normalized().rotation_difference((Vector(target)-h).normalized());m=arm.matrix_world@pb[n].matrix;pb[n].matrix=arm.matrix_world.inverted()@(Matrix.Translation(h)@q.to_matrix().to_4x4()@Matrix.Translation(-h)@m);bpy.context.view_layer.update()
def two(a,b,D,pole):
 A=head(a);u=(D-A).normalized();d=(D-A).length;l1=(tail(a)-A).length;l2=(tail(b)-head(b)).length
 if not abs(l1-l2)+.0001<d<l1+l2-.0001:return False
 v=pole-A;v=(v-u*v.dot(u)).normalized();p=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-p*p));aim(a,A+u*p+v*h);aim(b,D);return True
def geom(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();v=[ev.matrix_world@v.co for v in me.vertices];f=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return v,f
wheel=bpy.data.objects['SK_Kart_Steering_Column_And_Wheel_Rubber_Grip'];wt=BVHTree.FromPolygons(*geom(wheel));glove=bpy.data.objects['RACER | anatomical five-finger gloves'];body=bpy.data.objects['kart_driverMesh']
# Moderate-resolution probe; final validation uses full evaluated/render geometry.
for o in [glove,body]:
 for m in o.modifiers:
  if m.type=='SUBSURF':m.levels=1
def reset():
 for b in pb:b.matrix_basis=basis[b.name].copy()
 bpy.context.view_layer.update()
def pose(p):
 reset()
 for s,sgn in [('l',1),('r',-1)]:
  h=Vector((p['x'],sgn*p['y'],.705));mat=arm.matrix_world@pb['hand_'+s].matrix
  if not two('upperarm_'+s,'lowerarm_'+s,h,Vector((.22,sgn*.35,.74))):return False
  mat.translation=h;pb['hand_'+s].matrix=arm.matrix_world.inverted()@mat;bpy.context.view_layer.update();aim('hand_'+s,h+Vector((.09,-sgn*p['aim_y'],p['aim_z'])))
  for finger in ['index','middle','ring','pinky']:
   n=finger+'_01_'+s;hh=head(n);z=hh.z;r=sgn*math.sqrt(max(.001,.184**2-(z-.7)**2));o=p['out']
   aim(n,(.608,r+sgn*o,z));aim(finger+'_02_'+s,(.637,r+sgn*o*.75,z-.001));aim(finger+'_03_'+s,(.653,r-sgn*.003,z-.003))
 return True
def metrics():
 result={}
 for o in [glove,body]:
  v,f=geom(o);a=np.array(v);rad=np.sqrt(a[:,1]**2+(a[:,2]-.7)**2);sdf=np.sqrt((a[:,0]-.62)**2+(rad-.184)**2)-.017
  close=np.sort(np.abs(sdf))[:max(1,len(sdf)//50)];pen=np.minimum(sdf,0)
  result[o.name]={'pairs':len(BVHTree.FromPolygons(v,f).overlap(wt)),'worst_penetration_m':float(-min(sdf)),'penetration_cost':float(np.sum(pen**2)),'near_contact_gap_m':float(np.mean(close))}
 return result
if '--save' not in sys.argv:
 records=[]
 for x in [.472,.480,.488]:
  for y in [.205,.217,.229]:
   for out in [.030,.042,.054]:
    p={'x':x,'y':y,'aim_y':.021,'aim_z':0,'out':out}
    if not pose(p):continue
    m=metrics();score=sum(v['pairs'] for v in m.values())+100000*sum(v['penetration_cost'] for v in m.values())+abs(m[glove.name]['near_contact_gap_m']-.001)*1000
    records.append({'params':p,'metrics':m,'score':score})
 records.sort(key=lambda r:r['score']);(P/'grip_probe.json').write_text(json.dumps(records,indent=2));print('TOP_GRIP',json.dumps(records[:4]),flush=True)
else:
 p=json.loads((P/'grip_probe.json').read_text())[0]['params'];pose(p)
 for b in pb:
  b.keyframe_insert('location',frame=1);b.keyframe_insert('rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1);b.keyframe_insert('scale',frame=1)
 for o in [glove,body]:
  for m in o.modifiers:
   if m.type=='SUBSURF':m.levels=2 if o==glove else 1
 scene.camera=bpy.data.objects['Refinement | three quarter'];scene.cycles.samples=16;scene.render.filepath=str(P/'grip_preview.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'V5_grip_working.blend'));bpy.ops.render.render(write_still=True)

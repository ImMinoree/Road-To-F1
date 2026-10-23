import bpy,math,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(r'D:\Boring\GitHub\Road-To-F1-New\Road_To_F1_New\Art\DesertKarting\KartDriver_Fitted')
OUT=ROOT/'Refinement_v2';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Kart_With_MakeHuman_Fitted.blend'))
scene=bpy.context.scene;arm=bpy.data.objects['Game_engine'];pb=arm.pose.bones
human=[bpy.data.objects[n] for n in ('Game_engine','kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh','high-polyMesh')]
original_matrices={o.name:o.matrix_world.copy() for o in human}
original_pose={b.name:b.matrix_basis.copy() for b in pb}
old_action=arm.animation_data.action if arm.animation_data else None
if old_action:old_action.use_fake_user=True;arm.animation_data.action=None
deps=bpy.context.evaluated_depsgraph_get()
def head(n):return arm.matrix_world@pb[n].head
def tail(n):return arm.matrix_world@pb[n].tail
def rotate(n,q):
 p=head(n);wm=arm.matrix_world@pb[n].matrix
 pb[n].matrix=arm.matrix_world.inverted()@(Matrix.Translation(p)@q.to_matrix().to_4x4()@Matrix.Translation(-p)@wm)
 bpy.context.view_layer.update()
def aim(n,t):rotate(n,(tail(n)-head(n)).normalized().rotation_difference((Vector(t)-head(n)).normalized()))
def two(upper,lower,target,pole):
 A=head(upper);D=Vector(target);delta=D-A;d=delta.length;u=delta.normalized()
 l1=(tail(upper)-A).length;l2=(tail(lower)-head(lower)).length
 if d>=l1+l2-.002 or d<=abs(l1-l2)+.002:return False
 v=Vector(pole)-A;v=(v-u*v.dot(u)).normalized()
 a=(l1*l1-l2*l2+d*d)/(2*d);b=math.sqrt(max(0,l1*l1-a*a))
 aim(upper,A+u*a+v*b);aim(lower,D);return True
def geometry(o):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
def bvh(objects):
 vs=[];fs=[]
 for o in objects:
  v,f=geometry(o);offset=len(vs);vs.extend(v);fs.extend([tuple(i+offset for i in p) for p in f])
 return BVHTree.FromPolygons(vs,fs)
part_objects={
 'tank':[o for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_Fuel_Tank_And_Cap')],
 'seat':[o for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_Seat_Sculpted_Tub')],
 'pedals':[o for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_Driver_Controls_And_Pedals')],
 'wheel':[bpy.data.objects['SK_Kart_Steering_Column_And_Wheel_Rubber_Grip']],
}
trees={n:bvh(os) for n,os in part_objects.items()}
tank_shell=bpy.data.objects['SK_Kart_Fuel_Tank_And_Cap_Fuel_Tank_Clouded_Polymer']
tank_tree=bvh([tank_shell]);tank_center=Vector((.12,0,.56))
def metrics():
 result={};score=0
 for name in ('kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh'):
  v,f=geometry(bpy.data.objects[name]);t=BVHTree.FromPolygons(v,f)
  result[name]={n:len(t.overlap(tree)) for n,tree in trees.items()}
  depths=[]
  for p in v:
   if -.04<p.x<.27 and abs(p.y)<.23 and .44<p.z<.74:
    direction=Vector((.933,.274,.234)).normalized();origin=p.copy();hits=0
    for _ in range(12):
     hit,normal,index,distance=tank_tree.ray_cast(origin,direction,2)
     if hit is None:break
     hits+=1;origin=hit+direction*.00001
    if hits%2:
     near,n,_,d=tank_tree.find_nearest(p)
     if d>.001:depths.append(d)
  result[name]['tank_inside_vertices']=len(depths)
  result[name]['tank_max_vertex_depth_m']=max(depths,default=0)
  score+=len(depths)*5+sum(depths)*600
  score+=result[name]['seat']*.8+result[name]['tank']*.3
  if name=='shoes05Mesh':score+=result[name]['pedals']*.2
 knees=[head('calf_l').z,head('calf_r').z]
 result['knees_z_m']=knees
 score+=max(0,max(knees)-.64)*500
 result['score']=score
 return result

def pose(params):
 for o in human:o.matrix_world=original_matrices[o.name].copy()
 for b in pb:b.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update()
 shift=Vector((params['hip_x'],0,params['hip_z']))-head('pelvis')
 for o in human:o.matrix_world.translation+=shift
 bpy.context.view_layer.update()
 # Tilt the spine as a unit at the pelvis, without changing any bone length.
 lean=math.radians(params['lean_deg']);vec=Vector((math.sin(lean),0,math.cos(lean)))
 rotate('pelvis',(head('neck_01')-head('pelvis')).normalized().rotation_difference(vec))
 for side,s in [('l',1),('r',-1)]:
  wrist=Vector((.490,s*.225,.710))
  if not two('upperarm_'+side,'lowerarm_'+side,wrist,(.25,s*.40,.68)):return False
  # Preserve the already fitted hand and individual finger orientations.
  for name in ['hand_'+side]+[n for n in original_pose if n.endswith('_'+side) and any(d in n for d in ('thumb','index','middle','ring','pinky'))]:
   pb[name].matrix_basis=original_pose[name]
  bpy.context.view_layer.update()
  # Hand orientation in world space comes from the saved fit, independent of elbow roll.
  wm=original_hand_world[side].copy();wm.translation=wrist
  pb['hand_'+side].matrix=arm.matrix_world.inverted()@wm;bpy.context.view_layer.update()
  ankle=Vector((params['ankle_x'],s*.19,.25))
  if not two('thigh_'+side,'calf_'+side,ankle,(.68,s*params.get('knee_pole_y',.33),params.get('knee_pole_z',.85))):return False
  aim('foot_'+side,ankle+Vector((.078,-s*.008,-.052)))
  aim('ball_'+side,head('ball_'+side)+Vector((.12,-s*.010,-.008)))
 aim('neck_01',head('neck_01')+Vector((.008,0,.13)))
 aim('head',head('head')+Vector((0,0,.13)))
 return True

for b in pb:b.matrix_basis=original_pose[b.name]
bpy.context.view_layer.update()
original_hand_world={s:arm.matrix_world@pb['hand_'+s].matrix for s in ('l','r')}
def probe_main():
 baseline=metrics();print('BASELINE',json.dumps(baseline),flush=True)
 best=[];tested=0
 for hip_x in (.02,.06,.10):
  for hip_z in (.50,.52):
   for lean in (-5,5,15):
    for ankle_x in (.46,.48):
     for pole_y,pole_z in ((.33,.85),(.45,.65),(.60,.50)):
      p={'hip_x':hip_x,'hip_z':hip_z,'lean_deg':lean,'ankle_x':ankle_x,'knee_pole_y':pole_y,'knee_pole_z':pole_z}
      if not pose(p):continue
      m=metrics();best.append({'params':p,'metrics':m});tested+=1
 best.sort(key=lambda r:r['metrics']['score'])
 (OUT/'pose_probe.json').write_text(json.dumps({'baseline':baseline,'tested':tested,'candidates':best},indent=2))
 print('TOP_CANDIDATES',json.dumps(best[:5]),flush=True)
if __name__=='__main__':probe_main()

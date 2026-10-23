"""Pose-only recline refinement from v2; retain its complete kart/tank layout."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
SOURCE=OUT.parent/'Refinement_v2/Kart_With_MakeHuman_Fitted_v2.blend'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene;arm=bpy.data.objects['Game_engine'];pb=arm.pose.bones
original_action=arm.animation_data.action if arm.animation_data else None
if original_action:original_action.use_fake_user=True;arm.animation_data.action=None
human=[bpy.data.objects[n] for n in ('Game_engine','kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh','high-polyMesh')]
matrices={o.name:o.matrix_world.copy() for o in human};basis={b.name:b.matrix_basis.copy() for b in pb}
deps=bpy.context.evaluated_depsgraph_get()
def head(n):return arm.matrix_world@pb[n].head
def tail(n):return arm.matrix_world@pb[n].tail
hands={s:arm.matrix_world@pb['hand_'+s].matrix for s in ('l','r')}
feet={s:arm.matrix_world@pb['foot_'+s].matrix for s in ('l','r')}
knees={s:head('calf_'+s).copy() for s in ('l','r')}
def geometry(o):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
kart=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')]
trees={o.name:BVHTree.FromPolygons(*geometry(o)) for o in kart}
seat=bpy.data.objects['SK_Kart_Seat_Sculpted_Tub_Seat_Moulded_Polymer'];v,f=geometry(seat)
sheet=BVHTree.FromPolygons(v,[p for p in f if all(i<759 for i in p)])
cloth=bpy.data.objects['male_casualsuit04Mesh']
glutes=[v.index for v in cloth.data.vertices if v.co.z<0 and v.co.y<90 and any(cloth.vertex_groups[w.group].name=='pelvis' and w.weight>.4 for w in v.groups)]
back=[v.index for v in cloth.data.vertices if v.co.z<-2 and 90<v.co.y<130 and sum(w.weight for w in v.groups if cloth.vertex_groups[w.group].name.startswith('spine'))>.4]
def rotate(n,q):
 p=head(n);m=arm.matrix_world@pb[n].matrix
 pb[n].matrix=arm.matrix_world.inverted()@(Matrix.Translation(p)@q.to_matrix().to_4x4()@Matrix.Translation(-p)@m);bpy.context.view_layer.update()
def aim(n,t):rotate(n,(tail(n)-head(n)).normalized().rotation_difference((Vector(t)-head(n)).normalized()))
def two(a,b,D,pole):
 A=head(a);u=(D-A).normalized();d=(D-A).length;l1=(tail(a)-A).length;l2=(tail(b)-head(b)).length
 if not abs(l1-l2)+.001<d<l1+l2-.001:return False
 v=pole-A;v=(v-u*v.dot(u)).normalized();p=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-p*p));aim(a,A+u*p+v*h);aim(b,D);return True
def reset():
 for o in human:o.matrix_world=matrices[o.name].copy()
 for b in pb:b.matrix_basis=basis[b.name].copy()
 bpy.context.view_layer.update()
def flex(a,b,c):return 180-math.degrees((head(a)-head(b)).angle(head(c)-head(b)))
def pose(p):
 reset()
 for n in ('pelvis','spine_01','spine_02','spine_03','clavicle_l','clavicle_r'):pb[n].matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update()
 delta=Vector((p['hip_x'],0,p['hip_z']))-head('pelvis')
 for o in human:o.matrix_world.translation+=delta
 bpy.context.view_layer.update();length=(head('neck_01')-head('pelvis')).length;r=math.radians(p['lean_deg'])
 target=head('pelvis')+Vector((length*math.sin(r),0,length*math.cos(r)))
 rotate('pelvis',(head('neck_01')-head('pelvis')).normalized().rotation_difference((target-head('pelvis')).normalized()))
 rotate('pelvis',Quaternion(Vector((0,1,0)),math.radians(p['pelvic_tilt_deg'])))
 rotate('spine_01',(head('neck_01')-head('spine_01')).normalized().rotation_difference((target-head('spine_01')).normalized()))
 for s,sign in [('l',1),('r',-1)]:
  # Small scapular protraction permits a rearward trunk with relaxed, lowered shoulders.
  aim('clavicle_'+s,tail('clavicle_'+s)+Vector((p['shoulder_reach_m'],0,-.004)))
  if not two('upperarm_'+s,'lowerarm_'+s,hands[s].translation,Vector((.24,sign*.38,.67))):return False
  pb['hand_'+s].matrix=arm.matrix_world.inverted()@hands[s];bpy.context.view_layer.update()
  if flex('upperarm_'+s,'lowerarm_'+s,'hand_'+s)<12:return False
  if not two('thigh_'+s,'calf_'+s,feet[s].translation,knees[s]):return False
  pb['foot_'+s].matrix=arm.matrix_world.inverted()@feet[s];bpy.context.view_layer.update()
 aim('neck_01',head('neck_01')+Vector((.008,0,.13)));aim('head',head('head')+Vector((0,0,.13)))
 return True
def signed_support(points):
 gaps=[]
 for p in points:
  near,n,_,d=sheet.find_nearest(p)
  if n.x<0:n=-n
  gaps.append((p-near).dot(n))
 gaps.sort()
 return {'min_m':min(gaps,default=0),'contact_quartile_mean_m':sum(gaps[:max(1,len(gaps)//4)])/max(1,len(gaps)//4),'count':len(gaps)}
def metrics(full=False):
 result={};counts={};positions={}
 for name in ('kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh'):
  v,f=geometry(bpy.data.objects[name]);positions[name]=v;t=BVHTree.FromPolygons(v,f)
  relevant=trees if full else {n:bt for n,bt in trees.items() if any(k in n for k in ('Seat','Fuel_Tank','Steering_Column','Chassis_MainFrame','Axles_Steering','Bodywork'))}
  counts[name]={n:len(t.overlap(bt)) for n,bt in relevant.items() if t.overlap(bt)}
 v=positions['male_casualsuit04Mesh']
 result['glute_support']=signed_support([v[i] for i in glutes]);result['back_support']=signed_support([v[i] for i in back if v[i].z<.875])
 result['collisions']=counts
 result['actual_torso_lean_deg']=math.degrees(math.atan2((head('neck_01')-head('pelvis')).x,(head('neck_01')-head('pelvis')).z))
 result['elbow_flexion_deg']=[flex('upperarm_'+s,'lowerarm_'+s,'hand_'+s) for s in ('l','r')]
 result['control_errors_m']={n:(head(n)-target.translation).length for n,target in [(f'hand_{s}',hands[s]) for s in ('l','r')]+[(f'foot_{s}',feet[s]) for s in ('l','r')]}
 return result
reset();baseline=metrics(full=True)
def score(p,m):
 critical=sum(v for hs in m['collisions'].values() for n,v in hs.items() if 'Fuel_Tank' in n or 'Steering_Column' in n)
 seat_pairs=sum(v for hs in m['collisions'].values() for n,v in hs.items() if 'Seat_Sculpted_Tub' in n)
 old_seat=sum(v for hs in baseline['collisions'].values() for n,v in hs.items() if 'Seat_Sculpted_Tub' in n)
 all_pairs=sum(v for hs in m['collisions'].values() for v in hs.values())
 gs=m['glute_support']['contact_quartile_mean_m'];bs=m['back_support']['contact_quartile_mean_m']
 pen=max(0,-gs-.003)*15000+max(0,-bs-.003)*15000
 gaps=max(0,gs-.012)*5000+max(0,bs-.02)*4000
 return critical*10000+max(0,seat_pairs-old_seat)*8+all_pairs*.15+pen+gaps+abs(p['lean_deg']+10)*.5+p['shoulder_reach_m']*30

if '--save' not in sys.argv:
 records=[];tested=0
 for x in (.045,.05,.055,.06):
  for z in (.575,.58,.585,.59):
   for lean in (-10,-12,-14):
    for tilt in (-20,-30,-40):
     for reach in (.10,.12):
      p={'hip_x':x,'hip_z':z,'lean_deg':lean,'pelvic_tilt_deg':tilt,'shoulder_reach_m':reach}
      if not pose(p):continue
      m=metrics();records.append({'params':p,'metrics':m,'score':score(p,m)});tested+=1
 records.sort(key=lambda r:r['score']);(OUT/'recline_probe.json').write_text(json.dumps({'baseline':baseline,'feasible_count':tested,'candidates':records},indent=2))
 print('RECLINE_TOP',json.dumps(records[:4]),flush=True)
else:
 records=json.loads((OUT/'recline_probe.json').read_text());index=next((int(s.split('=')[1]) for s in sys.argv if s.startswith('--candidate=')),0);selected=records['candidates'][index]
 assert pose(selected['params'])
 for b in pb:
  b.keyframe_insert(data_path='location',frame=1);b.keyframe_insert(data_path='rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1);b.keyframe_insert(data_path='scale',frame=1)
 if arm.animation_data and arm.animation_data.action:arm.animation_data.action.name='Kart | supported recline v3'
 for s in ('l','r'):
  bpy.data.objects['Wrist fit '+s].location=head('hand_'+s);bpy.data.objects['Ankle fit '+s].location=head('foot_'+s)
 scene.camera=bpy.data.objects['Refinement | three quarter'];scene['Fit status']='Pose-only backward recline refinement; v2 tank placement retained. See recline_validation.json for remaining contacts.'
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v3.blend'))
 result={'source':str(SOURCE),'selected':selected['params'],'before':baseline,'after':metrics(full=True)}
 (OUT/'recline_validation.json').write_text(json.dumps(result,indent=2))
 scene.camera=bpy.data.objects['Refinement | side'];scene.cycles.samples=16;scene.render.filepath=str(OUT/'side_review.png');bpy.ops.render.render(write_still=True)
 print('RECLINE_SAVED',json.dumps(result),flush=True)

import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;source=P.parent/'Cockpit_Reference_v2/diagnose_wheel_visibility.py';scope={'__file__':str(source)};exec(compile(source.read_text().split('rows=[]')[0],str(source),'exec'),scope)
s,r,o,w=scope['s'],scope['r'],scope['o'],scope['w'];deps=scope['deps'];inv=scope['inv'];af,lf=scope['af'],scope['lf'];aim=scope['aim'];T,C,eye=scope['T'],scope['C'],scope['eye'];karttree=scope['karttree'];rows=[]
for back,down in [(x,z) for x in [0,.025,.05,.075,.10] for z in [0,.025,.05,.075]]:
 if back==down==0:continue
 case={'hip_back_m':back,'hip_down_m':down,'samples':[]}
 for frame in [1,25,49]:
  s.frame_set(frame);bpy.context.view_layer.update();pose={b.name:r.matrix_world@b.matrix.copy() for b in r.pose.bones};delta=Vector((-back,0,-down));pelvis=pose['pelvis'].copy();pelvis.translation+=delta;r.pose.bones['pelvis'].matrix=inv@pelvis;bpy.context.view_layer.update();r.pose.bones['spine_01'].matrix=inv@pose['spine_01'];bpy.context.view_layer.update()
  for side in ['l','r']:
   up='thigh_'+side;lo='calf_'+side;foot='foot_'+side;H=pose[up].translation+delta;oldK=pose[lo].translation;W=pose[foot].translation;L1=(pose[lo].translation-pose[up].translation).length;L2=(W-oldK).length;D=(W-H).normalized();d=(W-H).length;a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));pole=oldK-(H+W)/2;pole=(pole-D*pole.dot(D)).normalized();K=H+D*a+pole*h
   r.pose.bones[up].matrix=inv@aim(pose[up],H,K);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(pose[lo],K,W);bpy.context.view_layer.update();r.pose.bones[foot].matrix=inv@pose[foot];bpy.context.view_layer.update()
  ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];a=BVHTree.FromPolygons(vs,af);l=BVHTree.FromPolygons(vs,lf);A=T@Matrix.Rotation(math.radians((frame-25)/24*25),4,'X')@T.inverted();rim=[C+A@v.co for v in w.data.vertices[:3360]];masked=0
  for i in range(168):
   section=rim[i*20:(i+1)*20];p=min(section,key=lambda p:(p-eye).length);local=T.inverted()@(sum(section,Vector())/20-C)
   if local.z>-.08:continue
   if l.ray_cast(eye,(p-eye).normalized(),(p-eye).length-.001)[0] is not None:masked+=1
  case['samples'].append({'frame':frame,'rim_hidden_by_legs':masked,'arm_leg_crossings':len(a.overlap(l)),'leg_chassis_crossings':len(l.overlap(karttree))});ev.to_mesh_clear()
 case['cost']=max(x['rim_hidden_by_legs'] for x in case['samples'])*100+max(x['arm_leg_crossings'] for x in case['samples'])+max(x['leg_chassis_crossings'] for x in case['samples']);rows.append(case)
(P/'seating_trials.json').write_text(json.dumps(rows,indent=2));print('SEAT_BEST',sorted(rows,key=lambda x:(x['cost'],x['hip_back_m']+x['hip_down_m']))[:7],flush=True)

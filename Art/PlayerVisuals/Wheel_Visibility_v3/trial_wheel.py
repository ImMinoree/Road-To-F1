import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;source=P.parent/'Cockpit_Reference_v2/diagnose_wheel_visibility.py'
q={'__file__':str(source)};exec(compile(source.read_text().split('rows=[]')[0],str(source),'exec'),q)
s,r,o,w=q['s'],q['r'],q['o'],q['w'];T,C,eye=q['T'],q['C'],q['eye'];inv=q['inv'];rows=[]
for lift in [.02,.04,.06,.08]:
 case={'lift_m':lift,'samples':[]};delta=Vector((0,0,lift))
 for frame in [1,25,49]:
  s.frame_set(frame);bpy.context.view_layer.update()
  for side in ['l','r']:
   up,lo,hand=['upperarm_'+side,'lowerarm_'+side,'hand_'+side];m={n:r.matrix_world@r.pose.bones[n].matrix for n in [up,lo,hand]};S,E,W=[m[n].translation for n in [up,lo,hand]];target=m[hand].copy();target.translation+=delta;N=target.translation;L1=(E-S).length;L2=(W-E).length;D=(N-S).normalized();d=(N-S).length;a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));pole=(E-S)-D*(E-S).dot(D);K=S+D*a+pole.normalized()*h
   r.pose.bones[up].matrix=inv@q['aim'](m[up],S,K);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@q['aim'](m[lo],K,N);bpy.context.view_layer.update();r.pose.bones[hand].matrix=inv@target;bpy.context.view_layer.update()
  ev=o.evaluated_get(q['deps']);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];leg=BVHTree.FromPolygons(vs,q['lf']);arm=BVHTree.FromPolygons(vs,q['af']);A=T@Matrix.Rotation(math.radians((frame-25)/24*25),4,'X')@T.inverted();rim=[C+delta+A@v.co for v in w.data.vertices[:3360]];hidden=0
  for i in range(168):
   section=rim[i*20:(i+1)*20];p=min(section,key=lambda p:(p-eye).length);local=T.inverted()@(sum(section,Vector())/20-C-delta)
   if local.z<-.08 and leg.ray_cast(eye,(p-eye).normalized(),(p-eye).length-.001)[0] is not None:hidden+=1
  s.camera.data.angle=math.radians(110);s.camera.rotation_euler=Vector((math.cos(math.radians(8)),0,-math.sin(math.radians(8)))).to_track_quat('-Z','Y').to_euler();pr=[world_to_camera_view(s,s.camera,p) for p in rim]
  case['samples'].append({'frame':frame,'hidden':hidden,'arm_leg':len(arm.overlap(leg)),'arm_chassis':len(arm.overlap(q['karttree'])),'top':min(1-p.y for p in pr),'bottom':max(1-p.y for p in pr)});ev.to_mesh_clear()
 rows.append(case)
(P/'wheel_trials.json').write_text(json.dumps(rows,indent=2));print(rows,flush=True)

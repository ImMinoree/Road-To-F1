import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;source=P.parent/'Cockpit_Reference_v2/diagnose_wheel_visibility.py'
scope={'__file__':str(source)};exec(compile(source.read_text().split('rows=[]')[0],str(source),'exec'),scope)
s,r,o,w=scope['s'],scope['r'],scope['o'],scope['w'];deps=scope['deps'];inv=scope['inv'];base=scope['base'];af,lf=scope['af'],scope['lf'];setlegs=scope['setlegs'];aim=scope['aim'];T,C,eye=scope['T'],scope['C'],scope['eye'];karttree=scope['karttree'];oldverts=[v.co.copy() for v in o.data.vertices];rows=[]
for narrow in [0,.1,.2,.3]:
 for v,original in zip(o.data.vertices,oldverts):
  v.co=original
  if v.index not in scope['legids']:continue
  side='l' if v.co.y>0 else 'r';K=base['calf_'+side].translation;d=v.co-K;weight=math.exp(-((d.length/.17)**4));v.co.y-=d.y*narrow*weight
 for deg in [-20,-18,-16,-14]:
  for elbow in [0,20,40]:
   case={'narrow':narrow,'knees':deg,'elbow':elbow,'samples':[]}
   for frame in [1,25,49]:
    s.frame_set(frame);bpy.context.view_layer.update();setlegs(deg)
    for side in ['l','r']:
     names=['upperarm_'+side,'lowerarm_'+side,'hand_'+side];m={n:r.matrix_world@r.pose.bones[n].matrix for n in names};S=m[names[0]].translation;K=m[names[1]].translation;W=m[names[2]].translation;D=(W-S).normalized();pivot=S+D*(K-S).dot(D);R=Matrix.Rotation(math.radians(elbow),4,D);newK=pivot+R.to_3x3()@(K-pivot)
     if newK.z<K.z:R=Matrix.Rotation(-math.radians(elbow),4,D);newK=pivot+R.to_3x3()@(K-pivot)
     r.pose.bones[names[0]].matrix=inv@aim(m[names[0]],S,newK);bpy.context.view_layer.update();r.pose.bones[names[1]].matrix=inv@aim(m[names[1]],newK,W);bpy.context.view_layer.update();r.pose.bones[names[2]].matrix=inv@m[names[2]];bpy.context.view_layer.update()
    ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];a=BVHTree.FromPolygons(vs,af);l=BVHTree.FromPolygons(vs,lf);A=T@Matrix.Rotation(math.radians((frame-25)/24*25),4,'X')@T.inverted();rim=[C+A@v.co for v in w.data.vertices[:3360]];masked=0
    for i in range(168):
     section=rim[i*20:(i+1)*20];p=min(section,key=lambda p:(p-eye).length);local=T.inverted()@(sum(section,Vector())/20-C)
     if local.z>-.08:continue
     if l.ray_cast(eye,(p-eye).normalized(),(p-eye).length-.001)[0] is not None:masked+=1
    case['samples'].append({'frame':frame,'rim_hidden_by_legs':masked,'arm_leg_crossings':len(a.overlap(l)),'arm_chassis_crossings':len(a.overlap(karttree)),'leg_chassis_crossings':len(l.overlap(karttree))});ev.to_mesh_clear()
   case['score']=max(x['rim_hidden_by_legs'] for x in case['samples'])*100+max(x['arm_leg_crossings'] for x in case['samples']);rows.append(case)
(P/'fit_trials.json').write_text(json.dumps(rows,indent=2));print('FIT_BEST',sorted(rows,key=lambda r:(r['score'],r['narrow']+r['elbow']/100))[:10],flush=True)

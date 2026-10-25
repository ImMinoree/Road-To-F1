import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;source=P.parent/'Cockpit_Reference_v2/diagnose_wheel_visibility.py'
q={'__file__':str(source)};exec(compile(source.read_text().split('rows=[]')[0],str(source),'exec'),q)
s,r,o,w=q['s'],q['r'],q['o'],q['w'];T,C=q['T'],q['C'];rows=[]
for x in [.05,.10,.15,.20,.25]:
 for z in [1.05,1.10,1.15,1.20]:
  eye=Vector((x,0,z));s.camera.location=eye;s.camera.data.angle=math.radians(110);case={'eye':list(eye),'samples':[]}
  for frame in [1,25,49]:
   s.frame_set(frame);ev=o.evaluated_get(q['deps']);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];leg=BVHTree.FromPolygons(vs,q['lf']);A=T@Matrix.Rotation(math.radians((frame-25)/24*25),4,'X')@T.inverted();rim=[C+A@v.co for v in w.data.vertices[:3360]];hidden=0
   for i in range(168):
    section=rim[i*20:(i+1)*20];p=min(section,key=lambda p:(p-eye).length);local=T.inverted()@(sum(section,Vector())/20-C)
    if local.z<-.08 and leg.ray_cast(eye,(p-eye).normalized(),(p-eye).length-.001)[0] is not None:hidden+=1
   pr=[world_to_camera_view(s,s.camera,p) for p in rim];case['samples'].append({'frame':frame,'hidden':hidden,'top':min(1-p.y for p in pr),'bottom':max(1-p.y for p in pr)});ev.to_mesh_clear()
  rows.append(case)
(P/'camera_trials.json').write_text(json.dumps(rows,indent=2));print('CAMERA',rows,flush=True)

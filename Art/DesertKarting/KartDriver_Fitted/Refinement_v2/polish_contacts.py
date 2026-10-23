import bpy,sys,json,math
from pathlib import Path
import numpy as np
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
arm=bpy.data.objects['Game_engine'];pb=arm.pose.bones
if arm.animation_data:arm.animation_data.action=None
deps=bpy.context.evaluated_depsgraph_get()
def geometry(o):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
kart=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')]
trees={o.name:BVHTree.FromPolygons(*geometry(o)) for o in kart}
def collisions():
 report={}
 for name in ('kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh'):
  t=BVHTree.FromPolygons(*geometry(bpy.data.objects[name]))
  report[name]={n:len(t.overlap(tree)) for n,tree in trees.items() if t.overlap(tree)}
 return report
report={'before':collisions(),'grips':{}}
body=bpy.data.objects['kart_driverMesh']
def positions():
 e=body.evaluated_get(deps);m=e.to_mesh();a=np.empty(len(m.vertices)*3,dtype=np.float64);m.vertices.foreach_get('co',a);a=a.reshape(-1,3);wm=np.array(e.matrix_world);v=a@wm[:3,:3].T+wm[:3,3];e.to_mesh_clear();return v
for side in ('l','r'):
 ids={g.index for g in body.vertex_groups if g.name.endswith('_'+side) and any(s in g.name for s in ('hand','thumb','index','middle','ring','pinky'))}
 mask=np.array([v.index for v in body.data.vertices if sum(w.weight for w in v.groups if w.group in ids)>.25])
 def sdf():
  a=positions()[mask];rho=np.sqrt(a[:,1]**2+(a[:,2]-.70)**2)
  return np.sqrt((a[:,0]-.62)**2+(rho-.184)**2)-.017
 def loss():
  p=np.maximum(0,.0005-sdf());return float(np.sum(p*p)+4*np.max(p)**2)
 def summary():
  d=sdf();return {'vertices_inside_torus':int(np.sum(d<-.0005)),'max_depth_m':max(0,-float(np.min(d))),'loss':loss()}
 start=summary()
 names=[b.name for b in pb if b.name.endswith('_'+side) and any(s in b.name for s in ('thumb','index','middle','ring','pinky'))]
 # Small coordinate-descent rotation corrections, never changing lengths or weights.
 for step in (6,3,1):
  for _ in range(2):
   changed=False
   for name in names:
    b=pb[name];initial=b.matrix_basis.copy();best=initial;score=loss()
    for axis in ((1,0,0),(0,0,1),(0,1,0)):
     for sign in (-1,1):
      candidate=initial@Quaternion(Vector(axis),math.radians(step*sign)).to_matrix().to_4x4()
      b.matrix_basis=candidate;bpy.context.view_layer.update();newscore=loss()
      if newscore<score-.000000001:score=newscore;best=candidate.copy();changed=True
    b.matrix_basis=best;bpy.context.view_layer.update()
   if not changed:break
 report['grips'][side]={'before':start,'after':summary()}
 print('GRIP',side,json.dumps(report['grips'][side]),flush=True)
for b in pb:
 b.keyframe_insert(data_path='location',frame=1)
 b.keyframe_insert(data_path='rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1)
 b.keyframe_insert(data_path='scale',frame=1)
if arm.animation_data and arm.animation_data.action:arm.animation_data.action.name='Kart | seating refinement v2 contact correction'
report['after']=collisions()
(OUT/'contact_polish.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
print('CONTACT_REPORT',json.dumps(report),flush=True)

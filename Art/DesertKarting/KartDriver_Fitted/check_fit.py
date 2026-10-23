import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(r'D:\Boring\GitHub\Road-To-F1-New\Road_To_F1_New\Art\DesertKarting\KartDriver_Fitted')
bpy.ops.wm.open_mainfile(filepath=str(out/'Kart_With_MakeHuman_Fitted.blend'))
deps=bpy.context.evaluated_depsgraph_get()
def verts(o):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[list(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
def tree(objects):
 vs=[];fs=[]
 for o in objects:
  v,f=verts(o);offset=len(vs);vs.extend(v);fs.extend([[i+offset for i in face] for face in f])
 return BVHTree.FromPolygons(vs,fs)
parts={
 'seat':[o for o in bpy.data.objects if o.name.startswith('SK_Kart_Seat_Sculpted_Tub')],
 'wheel':[o for o in bpy.data.objects if o.name=='SK_Kart_Steering_Column_And_Wheel_Rubber_Grip'],
 'pedals':[o for o in bpy.data.objects if o.name.startswith('SK_Kart_Driver_Controls_And_Pedals')],
 'tank':[o for o in bpy.data.objects if 'Fuel' in o.name and o.type=='MESH'],
}
trees={k:tree(v) for k,v in parts.items() if v}
report={}
for name in ['kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh']:
 o=bpy.data.objects[name];v,f=verts(o)
 groups={g.index:g.name for g in o.vertex_groups}
 regions={}
 for i,p in enumerate(v):
  weights=o.data.vertices[i].groups
  region=max(weights,key=lambda w:w.weight).group if weights else -1
  region=groups.get(region,'none')
  regions.setdefault(region,[]).append(p)
 for side in ('l','r'):
  hand=[p for g,ps in regions.items() if g.endswith('_'+side) and any(s in g for s in ('hand','thumb','index','middle','ring','pinky')) for p in ps]
  shoe=[p for p in v if p.y*(1 if side=='l' else -1)>0] if name=='shoes05Mesh' else []
  for label,points,part in [('hand',hand,'wheel'),('shoe',shoe,'pedals')]:
   if points:
    distances=[trees[part].find_nearest(p)[3] for p in points]
    report[name+' '+label+' '+side]={'min_clearance_m':min(distances),'bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]}
 for part,t in trees.items():
  report[name+' overlap '+part]=len(BVHTree.FromPolygons(v,f).overlap(t))
arm=bpy.data.objects['Game_engine']
report['fingers']={b.name:{'head':list(arm.matrix_world@b.head),'tail':list(arm.matrix_world@b.tail)} for b in arm.pose.bones if any(s in b.name for s in ('hand','index','pinky'))}
report['materials']={m.name:{'diffuse':list(m.diffuse_color),'nodes':[(n.type,{s.name:s.default_value for s in n.inputs if s.name in ('Alpha','Roughness','Transmission Weight')}) for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']} for m in bpy.data.objects['male_casualsuit04Mesh'].data.materials}
(out/'contact_check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

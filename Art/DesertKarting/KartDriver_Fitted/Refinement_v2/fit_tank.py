"""Authorized uniform tank-assembly transform in the fitted copy only."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
tank=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_Fuel_Tank_And_Cap')]
original={o.name:o.matrix_world.copy() for o in tank}
shell=next(o for o in tank if 'Clouded_Polymer' in o.name)
bm=bmesh.new();bm.from_mesh(shell.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=False)*abs(shell.matrix_world.to_3x3().determinant());bm.free()
print('SOURCE_TANK_LITRES',volume*1000,flush=True)
def geometry(o):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
obstacles=[o for o in scene.objects if o.type=='MESH' and ((o.name.startswith('SK_Kart_') and o not in tank) or o.name in ('kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh'))]
trees={o.name:BVHTree.FromPolygons(*geometry(o)) for o in obstacles}
def combined():
 vs=[];fs=[]
 for o in tank:
  v,f=geometry(o);off=len(vs);vs.extend(v);fs.extend([tuple(i+off for i in p) for p in f])
 return vs,fs
pivot=Vector((.12,0,.56))
def place(scale,x,z):
 transform=Matrix.Translation(Vector((x,0,z)))@Matrix.Scale(scale,4)@Matrix.Translation(-pivot)
 for o in tank:o.matrix_world=transform@original[o.name]
 bpy.context.view_layer.update()
records=[]
# Start with the least resizing consistent with a plausible adult kart reservoir.
max_scale=min(1,(.0095/volume)**(1/3))
min_scale=(.0065/volume)**(1/3)
scales=[max_scale-i*.015 for i in range(12) if max_scale-i*.015>=min_scale]
for scale in scales:
 for x in (.28,.30,.32,.34,.36,.38):
  for z in (.14,.16,.18,.20,.22,.24):
   place(scale,x,z);v,f=combined();tb=BVHTree.FromPolygons(v,f)
   hits={n:len(tb.overlap(t)) for n,t in trees.items() if tb.overlap(t)}
   if hits:continue
   # Minimum distance from real assembly vertices to every obstacle, not just bounds.
   near=sorted([(min(t.find_nearest(p)[3] for p in v),n) for n,t in trees.items()])
   clearance=near[0][0]
   if clearance<.003:continue
   translation=(Vector((x,0,z))-pivot).length
   score=(1-scale)*.8+translation
   records.append({'scale':scale,'center':[x,0,z],'external_shell_volume_litres':volume*scale**3*1000,'minimum_vertex_clearance_m':clearance,'nearest':near[:7],'score':score})
records.sort(key=lambda r:r['score'])
if not records:
 (OUT/'tank_fit.json').write_text(json.dumps({'source_shell_litres':volume*1000,'candidates':[],'status':'No collision-free tank candidate found'},indent=2))
 raise RuntimeError('No feasible tank transform found; fitted scene left unchanged')
best=records[0];place(best['scale'],best['center'][0],best['center'][2]);v,f=combined();tb=BVHTree.FromPolygons(v,f)
intersections={n:len(tb.overlap(t)) for n,t in trees.items() if tb.overlap(t)}
report={'authorization':'User allowed repositioning and proportional resizing of existing fuel tank in new fitted scene only. No other kart object transform changed.','source_shell_litres':volume*1000,'selected':best,'candidates':records,'final_surface_intersections':intersections,'tank_objects':[o.name for o in tank],'geometry_unchanged':True,'volume_note':'Closed external shell geometric volume; not measured internal fuel capacity. Official KG and OTK adult kart tank catalogs list 8.5 and 9.5 L products.','sources':['https://www.kgkarting.it/products/fuel-tanks/?lang=en','https://www.tonykart.com/parts_en.php?ID_categoria=21&ID_macrocategoria=2']}
(OUT/'tank_fit.json').write_text(json.dumps(report,indent=2))
scene['Tank fit']='Existing tank assembly uniformly scaled and repositioned with user authorization. Meshes unchanged; see tank_fit.json.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
print('TANK_FIT',json.dumps(best),'intersections',intersections,flush=True)

"""Non-destructive scenery filtering and low infield terrain infill."""
import bpy,bmesh,json,math,re
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/DesertOpenInfield';(OUT/'Meshes').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.glb'))
align=Matrix(((0,1,0,28),(-1,0,0,103),(0,0,1,-.16),(0,0,0,1)))
ob=next(o for o in bpy.context.scene.objects if o.name=='03 Infield lawns and pit lane | white')
ob.data=ob.data.copy();ob.data.transform(align@ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);seen=set();remove=[];count=0
for v in bm.verts:
 if v in seen:continue
 stack=[v];group=[];seen.add(v)
 while stack:
  q=stack.pop();group.append(q)
  for e in q.link_edges:
   w=e.other_vert(q)
   if w not in seen:seen.add(w);stack.append(w)
 cy=sum(v.co.y for v in group)/len(group)
 # Source X=-86/-89 are pit parking marks. Starting grid X=-105/-98 is retained.
 if abs(cy-17)<.02 or abs(cy-14)<.02:remove.extend(group);count+=1
assert count==22,count
bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(ob.data);bm.free();ob.data.update();ob.name='SM_OI_StartingGridRetained'
def export(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(OUT/'Meshes'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',bake_anim=False)
export(ob)
# Infill stays below asphalt, outside the entire racing/runoff corridor. Existing lawn closes its perimeter.
audit=json.loads((ROOT/'Art/DesertRoute/audit.json').read_text());route=[(p[0]/100,p[1]/100) for p in audit['route_cm']]
verts=[];faces=[];ids={}
def vertex(x,y):
 key=(x,y)
 if key not in ids:
  edge=min(x+48,50-x,y+76,-8-y);fade=max(0,min(1,edge/7))
  z=-.124+fade*(.018+.012*math.sin(x*.21+y*.17)+.009*math.cos(x*.35-y*.27))
  ids[key]=len(verts);verts.append((x,-y,z))
 return ids[key]
for x in range(-48,50,2):
 for y in range(-76,-8,2):
  # Union of the former pit pad and central transporter/service clearing.
  sourcex=-y-103;sourcey=x-28
  if not ((-94<sourcex<-78 and -69<sourcey<20) or (-85<sourcex<-28 and -75<sourcey<-1)):continue
  if min(math.hypot(x+1-p[0],y+1-p[1]) for p in route)<11.8:continue
  # Reverse Y for Blender; winding points upward.
  faces.append(tuple(vertex(*p) for p in [(x,y),(x,y+2),(x+2,y+2),(x+2,y)]))
mesh=bpy.data.meshes.new('OpenInfield');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('SM_OI_InfieldTerrain',mesh);bpy.context.collection.objects.link(o)
for p in mesh.polygons:p.use_smooth=True
export(o)
(OUT/'manifest.json').write_text(json.dumps({'removed_parking_marks':count,'terrain_vertices':len(verts),'terrain_triangles':len(faces)*2,'terrain_collision':'None; existing continuous infield ground retained','route_exclusion_m':11.8},indent=2))
print('OPEN_INFIELD_AUTHORED',flush=True)


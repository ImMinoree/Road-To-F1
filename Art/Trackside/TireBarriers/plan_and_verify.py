"""Reopen saved blend, verify FBX/mesh properties, derive safe outside paths."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[2];E=R/'Evidence/TireBarriers'
bpy.ops.wm.open_mainfile(filepath=str(P/'TireBarriers.blend'))
for im in bpy.data.images:
 if im.source=='FILE' and im.name.startswith('T_Tire_'):im.pack();im.filepath='//Textures/'+im.name+'.png'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'TireBarriers.blend'))
o=bpy.data.objects['SM_TB_Tire_Black'];mesh=o.data
assert abs(o.dimensions.x-.55)<.0001 and abs(o.dimensions.z-.184)<.003
bm=__import__('bmesh').new();bm.from_mesh(mesh);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free();assert nonmanifold==0
groups={c.name:len([o for o in c.objects if o.type=='MESH']) for c in bpy.data.collections if c.name.startswith('Module_')};assert all(v==12 for v in groups.values())
report={'blend_reopened':True,'tire_dimensions_m':list(o.dimensions),'nonmanifold_edges':nonmanifold,'uv_layers':len(mesh.uv_layers),'module_individual_tires':groups,'fbx':{p.name:p.stat().st_size for p in (P/'Exports').glob('*.fbx')}}
assert len(report['fbx'])==5
# Verify a round-trip export, not just file existence.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(P/'Exports/SM_TB_Module_Alternating.fbx'))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==12
lo=Vector((1e6,1e6,1e6));hi=-lo
for o in objs:
 assert o.data.uv_layers
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  for j in range(3):lo[j]=min(lo[j],p[j]);hi[j]=max(hi[j],p[j])
report['fbx_roundtrip']={'individual_tires':len(objs),'bounds_m':list(hi-lo),'bottom_z_m':lo.z};assert 2.17<(hi-lo).x<2.22 and .54<(hi-lo).z<.57
(E/'blender_validation.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True);trees=[]
for p in (R/'Art/DesertKarting/Meshes').glob('SM_DK_02_*.fbx'):
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(p))
 for ob in set(bpy.data.objects)-before:
  if ob.type=='MESH':trees.append(BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(f.vertices) for f in ob.data.polygons]))
assert trees
g=json.loads((R/'Art/DesertRoute/audit.json').read_text());route=[Vector((p[0]/100,p[1]/100,0)) for p in g['route_cm']];n=len(route)
paths=[];placements=[]
for corner in [g['corners'][0],g['corners'][3]]:
 i=corner['index'];side=-1 if corner['angle_deg']>0 else 1;selected=None
 for offset in [12.5,14,16,18,20]:
  path=[]
  for k in range(i-7,i+8):
   tangent=(route[(k+1)%n]-route[(k-1)%n]).normalized();normal=Vector((-tangent.y,tangent.x,0));path.append(route[k%n]+normal*side*offset)
  # Uniform column spacing along an offset polyline, 24 columns = 6 modules.
  middle=len(path)//2;segments=[(path[j+1]-path[j]).length for j in range(len(path)-1)];total=sum(segments);start=max(0,total/2-6.29);sample=[]
  for d in [start+j*.547 for j in range(24)]:
   remaining=d
   for j,length in enumerate(segments):
    if remaining<=length:
     sample.append(path[j].lerp(path[j+1],remaining/length));break
    remaining-=length
  if len(sample)!=24:continue
  clearances=[]
  for p in sample:
   native=Vector((p.x,-p.y,.16));clearances.append(min(t.find_nearest(native)[3] for t in trees))
  # Entire tire footprint is at least 1 m beyond all source asphalt/kerb/runoff.
  # Keep a minimum 10 m to every route branch and 30 m to the grid origin.
  if min(clearances)>1.55 and min((p-q).length for p in sample for q in route)>10 and min(p.length for p in sample)>30:
   selected=(sample,offset,min(clearances));break
 if selected is None:continue
 sample,offset,clearance=selected;paths.append({'corner':corner['number'],'offset_m':offset,'min_road_runoff_clearance_m':clearance,'route_index':i,'columns':len(sample),'spline_cm':[[p.x*100,p.y*100,0] for p in sample]})
 for j,p in enumerate(sample):
  q=sample[min(j+1,len(sample)-1)]-sample[max(0,j-1)];yaw=math.degrees(math.atan2(q.y,q.x))
  for level in range(3):placements.append({'corner':corner['number'],'column':j,'level':level,'color':'Red' if (j//4)%2==0 else 'Black','location_cm':[p.x*100,p.y*100,level*18.4],'yaw':(yaw+j*137.508+level*79.3)%360})
assert paths,'No verified clear corner locations; do not place barriers'
(P/'placement.json').write_text(json.dumps({'paths':paths,'tires':placements,'source_geometry_checked':'All SM_DK_02 asphalt, curb and runoff FBXs; minimum tire centre clearance >1.55m, all route branches >10m, grid origin >30m','ground_z':'Unreal ground traces set each column bottom before placement','seed':281026},indent=2))
print('BLENDER_AND_PLACEMENT_VALIDATED',len(paths),len(placements),flush=True)

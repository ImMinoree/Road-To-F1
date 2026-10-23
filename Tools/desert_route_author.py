"""Additive route paint/sign meshes only. Does not edit source track or pit geometry."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/DesertRoute';g=json.loads((OUT/'audit.json').read_text());(OUT/'Meshes').mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);assets=[];parts=[]
with bpy.data.libraries.load(str(ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.blend'),link=False) as (lib,data):data.meshes=['02 Track surface curbs and runoff | asphalt']
native=data.meshes[0];bvh=BVHTree.FromPolygons([v.co for v in native.vertices],[p.vertices for p in native.polygons])
def mat(name):return bpy.data.materials.get(name) or bpy.data.materials.new(name)
def mesh(name,vs,fs,slots,indices=None):
 me=bpy.data.meshes.new(name);me.from_pydata([(x,-y,z) for x,y,z in vs],[],[tuple(reversed(f)) for f in fs]);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 for s in slots:me.materials.append(mat(s))
 for i,p in enumerate(me.polygons):p.material_index=indices[i] if indices else 0
 return o
def export(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(OUT/'Meshes'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False)
 assets.append({'name':o.name,'slots':[m.name for m in o.data.materials],'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)})
# +X is the direction of travel. White arrow plane is lifted 1.5 mm above road.
arrow=mesh('SM_Route_Arrow',[(-1.3,-.18,.0015),(.15,-.18,.0015),(.15,-.70,.0015),(1.3,0,.0015),(.15,.70,.0015),(.15,.18,.0015),(-1.3,.18,.0015)],[tuple(range(7))],['White']);export(arrow)
route=g['route_cm'];arc=g['arc_cm'];N=len(route);placements=[];last=-10000
for i,p in enumerate(route):
 if arc[i]-last<4800:continue
 q=route[(i+1)%N];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));placements.append({'location_cm':p,'yaw':yaw});last=arc[i]
# Existing gantry station, centred across the verified carriageway, above asphalt.
i=g['start_index'];a=Vector(route[i]);b=Vector(route[(i+1)%N]);t=(b-a).normalized();n=Vector((-t.y,t.x,0));center=Vector(g['start_finish_cm'])/100;vs=[];fs=[];indices=[]
for row in range(2):
 for col in range(20):
  start=len(vs)
  for u,v in [(0,0),(1,0),(1,1),(0,1)]:
   p=center+t*((row+u-1)*.60)+n*((col+v-10)*.60);vs.append((p.x,p.y,.0018))
  fs.append(tuple(range(start,start+4)));indices.append((row+col)%2)
finish=mesh('SM_Route_Finish',vs,fs,['White','Black'],indices);export(finish)
# One batched board mesh for all seven corner IDs; signs are outside the kerbs.
boards=[];signs=[]
for c in g['corners']:
 i=(c['index']-10)%N;p=Vector(route[i])/100;q=Vector(route[(i+1)%N])/100;t=(q-p).normalized();normal=Vector((-t.y,t.x,0));yaw=math.atan2(t.y,t.x)
 # Choose the outside of the bend, beyond the 10 m runoff envelope.
 side=-1 if c['angle_deg']>0 else 1;origin=p.copy();chosen=None
 for offset in [11.2,12.5,14,16,-11.2,-12.5,-14,-16]:
  candidate=origin+normal*side*offset;sample=Vector((candidate.y+103,candidate.x-28,.16));loc,no,idx,d=bvh.find_nearest(sample)
  if d>1.0:chosen=candidate;break
 assert chosen is not None,('No safe sign location',c['number']);p=chosen
 def point(x,y,z):return Vector((p.x+t.x*x+normal.x*y,p.y+t.y*x+normal.y*y,z))
 for size,local,material in [((.06,.86,.62),(0,0,1.10),'Black'),((.06,.06,.85),(.035,0,.42),'Steel')]:
  pos=point(*local);bpy.ops.mesh.primitive_cube_add(size=1,location=(pos.x,-pos.y,pos.z));o=bpy.context.object;o.scale=size;o.rotation_euler.z=-yaw;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat(material));m=o.modifiers.new('Manufactured edge radius','BEVEL');m.width=.015;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name);boards.append(o)
 pos=point(-.036,0,1.10);bpy.ops.object.text_add(location=(pos.x,-pos.y,pos.z),rotation=(math.pi/2,0,-math.pi/2-yaw));o=bpy.context.object;o.data.body='C'+str(c['number']);o.data.size=.40;o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.extrude=.001;o.data.materials.append(mat('White'));bpy.ops.object.convert(target='MESH');boards.append(bpy.context.object)
 signs.append({'corner':c['number'],'location_cm':[p.x*100,p.y*100,0],'route_index':i,'offset_m':float(offset*side),'source_asphalt_clearance_m':float(d)})
bpy.ops.object.select_all(action='DESELECT')
for o in boards:o.select_set(True)
bpy.context.view_layer.objects.active=boards[0];bpy.ops.object.join();board=bpy.context.object;board.name='SM_Route_CornerBoards';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');export(board)
(OUT/'markings.json').write_text(json.dumps({'assets':assets,'arrows':placements,'corner_signs':signs,'pit_changes':False,'finish_station_cm':g['start_finish_cm'],'direction':'User-confirmed +X on main straight, increasing source route index','pit_proposals':{'A':'entry proposed only','B':'exit proposed only','connectors_verified':False},'collision':'All new marking and sign geometry nonblocking; no race surface changes'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'RouteReadability.blend'));print('ROUTE_MARKINGS_EXPORTED',len(placements),len(signs),flush=True)

"""Read-only source topology audit and route extraction, using installed Blender."""
import bpy,bmesh,ast,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/DesertRoute';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT.parent/'artifacts/desert-karting-circuit';tree=ast.parse((SOURCE/'build_scene.py').read_text())
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name=='path':exec(compile(ast.Module(body=[n],type_ignores=[]),'source_path','exec'))
assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='track' for t in n.targets));control=ast.literal_eval(assignment.value.args[0]);route=path(control,22)
alignment=Matrix(((0,1,0,28),(-1,0,0,103),(0,0,1,-.16),(0,0,0,1)))
def ue(p):return [(p[1]+28)*100,(-p[0]-103)*100,0]
xy=np.array([ue(p)[:2] for p in route]);delta=np.roll(xy,-1,axis=0)-xy;lengths=np.linalg.norm(delta,axis=1);arc=np.r_[0,np.cumsum(lengths)];length=arc[-1]
startidx=int(np.argmin(np.linalg.norm(xy-np.array([-1800,0]),axis=1)))
# Source start/finish gantry is explicitly at original Blender Y=-46.
for i in range(22):
 if xy[i,0]<=-1800<xy[i+1,0]:
  f=(-1800-xy[i,0])/(xy[i+1,0]-xy[i,0]);finish=(xy[i]*(1-f)+xy[i+1]*f).tolist();startidx=i;break
else:raise RuntimeError('Cannot resolve source gantry crossing')
heading=np.unwrap(np.arctan2(delta[:,1],delta[:,0]));turn=np.arctan2(np.sin(np.roll(heading,-1)-heading),np.cos(np.roll(heading,-1)-heading))
# Group genuine bends by integrating signed heading, with short straight gaps.
smooth=np.convolve(np.r_[turn[-5:],turn,turn[:5]],np.ones(11)/11,mode='valid')[:len(turn)]
active=np.abs(smooth)>.008;groups=[];group=[]
for i in range(len(route)):
 if active[i]:group.append(i)
 elif group:
  if len(group)>=4 and abs(sum(turn[j] for j in group))>math.radians(24):groups.append(group)
  group=[]
if group and len(group)>=4:groups.append(group)
groups.sort(key=lambda ids:(arc[ids[len(ids)//2]]-arc[startidx])%length)
corners=[]
for ids in groups:
 idx=max(ids,key=lambda j:abs(smooth[j]));corners.append({'number':len(corners)+1,'index':idx,'location_cm':ue(route[idx]),'angle_deg':math.degrees(sum(turn[j] for j in ids)),'label_status':'Analytical bend numbering, not official circuit names'})
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(SOURCE/'desert_karting.glb'))
road=next(o for o in bpy.context.scene.objects if o.name=='02 Track surface curbs and runoff | asphalt')
bm=bmesh.new();bm.from_mesh(road.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
seen=set();components=0
for v in bm.verts:
 if v in seen:continue
 components+=1;stack=[v];seen.add(v)
 while stack:
  v=stack.pop()
  for e in v.link_edges:
   w=e.other_vert(v)
   if w not in seen:seen.add(w);stack.append(w)
boundary=[e for e in bm.edges if len(e.link_faces)==1];be=set();rings=0
for e in boundary:
 if e in be:continue
 rings+=1;stack=[e];be.add(e)
 while stack:
  q=stack.pop()
  for v in q.verts:
   for r in v.link_edges:
    if r in boundary and r not in be:be.add(r);stack.append(r)
mesh=road.data;mesh.calc_loop_triangles();verts=np.array([list(v.co) for v in mesh.vertices]);tri=np.array([[list(mesh.vertices[j].co)[:2] for j in t.vertices] for t in mesh.loop_triangles]);centers=tri.mean(1)
# Imported Blender coordinates are reflected X; convert face centres back for route association.
source_route=np.array([[-p.x,p.y] for p in route]);face_route=np.argmin(((centers[:,None,:]-source_route[None,:,:])**2).sum(2),axis=1)
lo=tri.min(1);hi=tri.max(1)
def area(poly):return abs(sum(np.cross(poly[(i+1)%len(poly)]-poly[i],poly[(i+2)%len(poly)]-poly[(i+1)%len(poly)]) for i in [])) if False else abs(sum(np.cross(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))))*.5
def clip(subject,clipper):
 out=list(subject);sign=1 if np.cross(clipper[1]-clipper[0],clipper[2]-clipper[0])>0 else -1
 for k in range(3):
  a=clipper[k];b=clipper[(k+1)%3];inp=out;out=[]
  if not inp:break
  for j,p in enumerate(inp):
   q=inp[j-1];dp=sign*np.cross(b-a,p-a);dq=sign*np.cross(b-a,q-a)
   if (dp>=-1e-8)!=(dq>=-1e-8):out.append(q+(p-q)*dq/(dq-dp))
   if dp>=-1e-8:out.append(p)
 return out
overlaps=[]
for i in range(len(tri)):
 candidates=np.where((lo[:,0]<hi[i,0])&(hi[:,0]>lo[i,0])&(lo[:,1]<hi[i,1])&(hi[:,1]>lo[i,1]))[0]
 for j in candidates:
  if j<=i:continue
  dist=abs(arc[face_route[i]]-arc[face_route[j]]);dist=min(dist,length-dist)
  if dist<2500:continue
  polygon=clip(tri[i],tri[j]);overlap=area(polygon) if len(polygon)>2 else 0
  if overlap>.03:overlaps.append({'triangle_pair':[int(i),int(j)],'route_indices':[int(face_route[i]),int(face_route[j])],'area_m2':float(overlap),'world_cm':ue(Vector((-float(centers[i,0]),float(centers[i,1]))))})
# Main surface widths reproduce the source generator's inside-edge curvature clamp.
width=[]
for i,p in enumerate(route):
 a=p-route[i-1];b=route[(i+1)%len(route)]-p;cross=a.cross(b);r=a.length*b.length*(a+b).length/(2*abs(cross)) if abs(cross)>1e-8 else 1e8;width.append(6.3+min(6.3,r*.78))
bvh=BVHTree.FromPolygons([v.co for v in mesh.vertices],[p.vertices for p in mesh.polygons]);missing=[]
for i,p in enumerate(route):
 loc,normal,face,d=bvh.ray_cast(Vector((-p.x,p.y,1)),Vector((0,0,-1)),2)
 if loc is None:missing.append(i)
# Pit rectangle ends and support at the missing lateral connections.
pit=[[-3850,-1700,0],[4450,-1700,0]] # original rectangle Y=-66.5..16.5; X=-86
report={'source_glb_sha256':hashlib.sha256((SOURCE/'desert_karting.glb').read_bytes()).hexdigest(),'source_blend':str(SOURCE/'desert_karting.blend'),'main_mesh':road.name,'source_control_points':control,'route_cm':[ue(p) for p in route],'arc_cm':arc[:-1].tolist(),'length_m':length/100,'start_index':startidx,'start_finish_cm':finish+[0],'direction':'Increasing source path indices; agrees with original kart heading generator and +X first-person spawn. Not an independently confirmed official race direction.','corners':corners,'connected_components':components,'boundary_loops':rings,'non_manifold_edges':sum(len(e.link_faces)>2 for e in bm.edges),'centerline_missing_source_faces':missing,'min_source_width_m':min(width),'max_source_width_m':max(width),'nonlocal_surface_overlaps':overlaps,'pit_endpoints_cm':pit,'pit_status':'Rectangle and separator exist, but no explicit entry/exit connector meshes, arrows or rules are authored. Ends A/B must remain unconfirmed.','verified_marker_defect':'Source checkerboard z=0.135m is below road z=0.16m and covers only part of the carriageway. Grid paint also sits below road. Gantry at original Y=-46 identifies the existing finish station.','shortcut_limit':'Infield and runoff are physically drivable; no checkpoint enforcement in temporary ProofPawn. Absence of off-track shortcuts cannot be certified from mesh connectivity.'}
with bpy.data.libraries.load(str(SOURCE/'desert_karting.blend'),link=False) as (lib,data):
 data.meshes=[n for n in lib.meshes if n=='02 Track surface curbs and runoff | asphalt']
native=data.meshes[0];assert native,'Native Blender main mesh missing'
from mathutils.kdtree import KDTree
kd=KDTree(len(mesh.vertices))
for i,v in enumerate(mesh.vertices):kd.insert(v.co,i)
kd.balance();max_delta=max(kd.find(v.co)[2] for v in native.vertices)
report['native_blend_comparison']={'mesh':native.name,'native_vertices':len(native.vertices),'native_faces':len(native.polygons),'glb_vertices':len(mesh.vertices),'glb_triangles':len(mesh.loop_triangles),'max_vertex_error_m':max_delta};assert max_delta<.0001,'GLB differs from native blend road'
pit_sections=[]
for endpoint in pit:
 y_source=endpoint[0]/100-28;intervals=[]
 for face in tri:
  xs=[]
  for k in range(3):
   a=face[k];b=face[(k+1)%3]
   if (a[1]<=y_source<=b[1] or b[1]<=y_source<=a[1]) and abs(b[1]-a[1])>1e-9:xs.append(float(a[0]+(b[0]-a[0])*(y_source-a[1])/(b[1]-a[1])))
  if len(xs)>=2:intervals.append([(min(xs)-103)*100,(max(xs)-103)*100])
 merged=[]
 for a,b in sorted(intervals):
  if merged and a<=merged[-1][1]+.001:merged[-1][1]=max(merged[-1][1],b)
  else:merged.append([a,b])
 gap=min(max(a+1100,-2300-b,0) for a,b in merged)
 overlap=max(max(0,min(b,-1100)-max(a,-2300)) for a,b in merged)
 pit_sections.append({'endpoint_cm':endpoint,'main_asphalt_intervals_world_y_cm':merged,'pit_interval_world_y_cm':[-2300,-1100],'lateral_asphalt_gap_m':gap/100,'shared_asphalt_width_m':overlap/100,'junction_status':'Proposed only; an overlap is not an authored or approved pit connector'})
report['pit_geometry_sections']=pit_sections
assert components==1 and rings==2 and not missing,'Source main-road topology failed'
(OUT/'audit.json').write_text(json.dumps(report,indent=2));bm.free();print('ROUTE_AUDIT',json.dumps({k:report[k] for k in ['length_m','connected_components','boundary_loops','min_source_width_m','nonlocal_surface_overlaps','pit_status']}),flush=True)

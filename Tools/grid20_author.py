"""Measure the supplied kart, fit twenty positions to the source route, and author additive paint."""
import bpy,bmesh,ast,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/Grid20';(OUT/'Meshes').mkdir(parents=True,exist_ok=True)
tree=ast.parse((ROOT.parent/'artifacts/desert-karting-circuit/build_scene.py').read_text());scope={'math':math,'Vector':Vector,'B':defaultdict(lambda:[[],[]]),'group':'Measured kart'}
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['mesh','box','rod','ball','ring','kart']:exec(compile(ast.Module(body=[node],type_ignores=[]),'supplied_kart','exec'),scope)
scope['kart']((0,0),0,0);coords=np.array([v for vs,fs in scope['B'].values() for v in vs]);lo=coords.min(0);hi=coords.max(0);dims=hi-lo
kart={'width_cm':float(dims[0]*100),'length_cm':float(dims[1]*100),'height_cm':float(dims[2]*100),'source':'Exact geometry produced by the supplied Blender kart function; not a new vehicle model','current_pawn_collision_sphere_diameter_cm':56,'clearance_envelope_cm':[220,180,155]}
g=json.loads((ROOT/'Art/DesertRoute/audit.json').read_text());r=[Vector(p) for p in g['route_cm']];a=g['arc_cm'];total=a[-1]+(r[-1]-r[0]).length
# The approved relocated finish lies on the long main straight. No route vertices are edited.
finish_x=5000.;i=next(i for i in range(7,65) if r[i].x<=finish_x<r[i+1].x);f=(finish_x-r[i].x)/(r[i+1].x-r[i].x);finish=r[i].lerp(r[i+1],f);finish_s=a[i]+f*(r[i+1]-r[i]).length
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.blend'),link=False) as (lib,data):data.meshes=['02 Track surface curbs and runoff | asphalt']
road=data.meshes[0];bvh=BVHTree.FromPolygons([v.co for v in road.vertices],[p.vertices for p in road.polygons])
def surface(x,y):
 # Native Blender (before reflected GLB) maps UE to source coordinates.
 hit=bvh.ray_cast(Vector((y/100+103,x/100-28,3)),Vector((0,0,-1)))
 assert hit[0] is not None,('No racing asphalt',x,y)
 return (hit[0].z-.16)*100

def station(s):
 s%=total;k=next((j for j in range(len(a)-1) if a[j]<=s<a[j+1]),len(a)-1);q=(k+1)%len(r);ds=(r[q]-r[k]).length;t=(s-a[k])/ds;p=r[k].lerp(r[q],t);direction=(r[q]-r[k]).normalized();return p,direction,k
p,t,k=station(finish_s);finish.z=surface(finish.x,finish.y);finish_yaw=math.degrees(math.atan2(t.y,t.x));slots=[]
for number in range(1,21):
 row=(number-1)//2;col=(number-1)%2;back=1400+row*360+col*180;p,t,k=station(finish_s-back);n=Vector((-t.y,t.x,0));p+=n*(-210 if col==0 else 210);p.z=surface(p.x,p.y);yaw=math.degrees(math.atan2(t.y,t.x))
 points=[]
 for dx in [-110,0,110]:
  for dy in [-90,0,90]:
   q=p+t*dx+n*dy;q.z=surface(q.x,q.y);points.append(list(q))
 slots.append({'number':number,'row':row+1,'column':col+1,'location_cm':list(p+Vector((0,0,40))),'yaw_deg':yaw,'tangent':list(t),'surface_samples_cm':points,'s_before_finish_cm':back})
# Exact oriented rectangle SAT for all 190 full-kart safety-envelope pairs.
def overlap(sa,sb):
 pa=Vector(sa['location_cm']);pb=Vector(sb['location_cm']);ta=Vector(sa['tangent']);tb=Vector(sb['tangent']);na=Vector((-ta.y,ta.x,0));nb=Vector((-tb.y,tb.x,0))
 for axis in [ta,na,tb,nb]:
  ra=110*abs(axis.dot(ta))+90*abs(axis.dot(na));rb=110*abs(axis.dot(tb))+90*abs(axis.dot(nb))
  if abs((pa-pb).dot(axis))>=ra+rb:return False
 return True
assert not any(overlap(x,y) for j,x in enumerate(slots) for y in slots[j+1:])
assets=[]
def export(ob):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.fbx(filepath=str(OUT/'Meshes'/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',bake_anim=False);assets.append({'name':ob.name,'materials':[m.name for m in ob.data.materials]})
def mesh(name,vs,fs,matids=None,mats=['White']):
 me=bpy.data.meshes.new(name);me.from_pydata([(x/100,-y/100,z/100) for x,y,z in vs],[],[tuple(reversed(f)) for f in fs]);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 for m in mats:me.materials.append(bpy.data.materials.get(m) or bpy.data.materials.new(m))
 if matids:
  for p,idx in zip(me.polygons,matids):p.material_index=idx
 return ob
vs=[];fs=[]
for s in slots:
 p=Vector(s['location_cm']);p.z-=40;t=Vector(s['tangent']);n=Vector((-t.y,t.x,0))
 def rect(x0,y0,x1,y1):
  idx=len(vs)
  for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:
   q=p+t*x+n*y;q.z=surface(q.x,q.y)+.20;vs.append(list(q))
  fs.append(tuple(range(idx,idx+4)))
 for x in [-130,122]:
  for y in [-100,92]:rect(x,y if y<0 else y-50,x+8,y+58 if y<0 else y+8);rect(x if x<0 else x-52,y,x+60 if x<0 else x+8,y+8)
ob=mesh('SM_Grid20_BoxPaint',vs,fs);export(ob)
texts=[]
for s in slots:
 p=Vector(s['location_cm'])-Vector(s['tangent'])*173;p.z=surface(p.x,p.y)+.22;bpy.ops.object.text_add(location=(p.x/100,-p.y/100,p.z/100),rotation=(0,0,-math.pi/2-math.radians(s['yaw_deg'])));o=bpy.context.object;o.data.body=str(s['number']);o.data.size=.52;o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.space_character=1.1;o.data.materials.append(bpy.data.materials.get('White'));bpy.ops.object.convert(target='MESH');texts.append(bpy.context.object)
bpy.ops.object.select_all(action='DESELECT')
for o in texts:o.select_set(True)
bpy.context.view_layer.objects.active=texts[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_Grid20_Numbers';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');export(o)
vs=[];fs=[];ids=[];t=Vector((math.cos(math.radians(finish_yaw)),math.sin(math.radians(finish_yaw)),0));n=Vector((-t.y,t.x,0))
for row in range(2):
 for col in range(20):
  idx=len(vs)
  for x,y in [(0,0),(1,0),(1,1),(0,1)]:
   q=finish+t*((row+x-1)*60)+n*((col+y-10)*60);q.z=surface(q.x,q.y)+.20;vs.append(list(q))
  fs.append(tuple(range(idx,idx+4)));ids.append((row+col)%2)
export(mesh('SM_Grid20_Finish',vs,fs,ids,['White','Black']))
# Separate only the original overhead beam from the source group that also includes marshal booths.
bpy.ops.import_scene.gltf(filepath=str(ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.glb'))
source=next(o for o in bpy.context.scene.objects if o.name=='14 Timing gantry signs and pit furniture | white');align=Matrix(((0,1,0,28),(-1,0,0,103),(0,0,1,-.16),(0,0,0,1)));source.data=source.data.copy();source.data.transform(align@source.matrix_world);source.matrix_world=Matrix.Identity(4)
bm=bmesh.new();bm.from_mesh(source.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);seen=set();beam=[];booths=[]
for v in bm.verts:
 if v in seen:continue
 group=[];stack=[v];seen.add(v)
 while stack:
  q=stack.pop();group.append(q)
  for e in q.link_edges:
   w=e.other_vert(q)
   if w not in seen:seen.add(w);stack.append(w)
 lo=Vector([min(v.co[j] for v in group) for j in range(3)]);hi=Vector([max(v.co[j] for v in group) for j in range(3)]);c=(lo+hi)/2;d=hi-lo
 if d.y>15 and d.z>1:beam.extend(group)
 elif abs(d.z-2.4)<.01 and not(abs(c.x+45)<2.1 and abs(c.y-20)<2.1):booths.extend(group)
assert beam and len(booths)==16
for name,selected in [('SM_Grid20_OriginalBeam',beam),('SM_Grid20_RetainedBooths',booths)]:
 sel=set(selected);vertices=list(selected);lookup={v:i for i,v in enumerate(vertices)};faces=[tuple(lookup[v] for v in f.verts) for f in bm.faces if all(v in sel for v in f.verts)];me=bpy.data.meshes.new(name);me.from_pydata([v.co for v in vertices],[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(bpy.data.materials.get('White'));export(ob)
bm.free()
(OUT/'layout.json').write_text(json.dumps({'kart':kart,'finish_cm':list(finish),'finish_yaw_deg':finish_yaw,'pole_distance_cm':1400,'row_pitch_cm':360,'column_stagger_cm':180,'lateral_offset_cm':210,'box_cm':[260,200],'slots':slots,'pair_tests':190,'overlaps':0,'source_route_unchanged':True,'assets':assets},indent=2));print('GRID20_LAYOUT_READY',kart,flush=True)



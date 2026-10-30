"""Original layered desert scenery; extracts existing palms/rocks, never edits source art."""
import bpy,bmesh,json,math,random
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'Art/EnvironmentDepth';(O/'Meshes').mkdir(parents=True,exist_ok=True);rng=random.Random(281026);assets=[];placements=[];parts=[]
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(n):return bpy.data.materials.get(n) or bpy.data.materials.new(n)
def export(obj,name):
 bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(O/'Meshes'/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',bake_anim=False)
 assets.append({'name':name,'slots':[m.name for m in obj.data.materials],'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons)});obj.hide_set(True)
def mesh(name,verts,faces,slots,indices=None,smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();obj=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(obj)
 for s in slots:me.materials.append(mat(s))
 uv=me.uv_layers.new(name='PhysicalUV')
 for p in me.polygons:
  p.use_smooth=smooth;p.material_index=indices[p.index] if indices else 0
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.5,v.y*.5+v.z*.5)
 return obj
# Reuse individual trees from the existing source grove, with original trunk/frond geometry.
bpy.ops.import_scene.gltf(filepath=str(R.parent/'artifacts/desert-karting-circuit/desert_karting.glb'))
source=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('12 ')]
for variant,cy in enumerate([-112,-99]):
 vs=[];fs=[];indices=[]
 for obj in source:
  slot=obj.name.rsplit(' | ',1)[-1]
  if slot not in ['trunk','leaf']:continue
  verts=[obj.matrix_world@v.co for v in obj.data.vertices];mapping={}
  for p in obj.data.polygons:
   if not all(abs(verts[i].x-153)<5.2 and abs(verts[i].y-cy)<5.2 for i in p.vertices):continue
   face=[]
   for i in p.vertices:
    if i not in mapping:mapping[i]=len(vs);v=verts[i];vs.append((v.x-153,v.y-cy,v.z))
    face.append(mapping[i])
   fs.append(tuple(face));indices.append(0 if slot=='trunk' else 1)
 assert len(fs)>150,('Palm extraction',len(fs));export(mesh('Palm',vs,fs,['trunk','leaf'],indices),'SM_ED_Palm_'+str(variant))
# A single original rock becomes an efficient, reusable landscaping module.
obj=next(o for o in source if o.name.endswith(' | sandlight'));bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);seed=next(iter(bm.verts));group=set([seed]);todo=[seed]
while todo:
 v=todo.pop()
 for edge in v.link_edges:
  q=edge.other_vert(v)
  if q not in group:group.add(q);todo.append(q)
points=[obj.matrix_world@v.co for v in group];origin=Vector(((min(v.x for v in points)+max(v.x for v in points))/2,(min(v.y for v in points)+max(v.y for v in points))/2,min(v.z for v in points)));mapping={v:i for i,v in enumerate(group)};vs=[tuple(obj.matrix_world@v.co-origin) for v in group];fs=[tuple(mapping[v] for v in f.verts) for f in bm.faces if all(v in group for v in f.verts)];assert len(fs)>10;export(mesh('Rock',vs,fs,['sandlight']),'SM_ED_Rock');bm.free()
for obj in list(bpy.context.scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
# Gently shaped horizon ridges. Separate near/far placement creates real parallax.
for variant in range(3):
 vs=[];fs=[];nx=100;ny=30
 for j in range(ny+1):
  y=(j/ny-.5)*130;envelope=math.sin(math.pi*j/ny)**2
  for i in range(nx+1):
   x=(i/nx-.5)*400;end=math.sin(math.pi*i/nx)**.55
   crest=7.5+3.6*math.sin(x*.022+variant*1.8)+2.3*math.sin(x*.051+variant)+1.1*math.cos(x*.091)
   z=envelope*end*crest+.12*envelope*math.sin(x*.16+y*.1)-.5;vs.append((x,y,z))
 for j in range(ny):
  for i in range(nx):
   a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
 export(mesh('Ridge',vs,fs,['sand']),'SM_ED_Ridge_'+str(variant))
def box(c,size,material,bevel=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=c);obj=bpy.context.object;obj.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat(material))
 if bevel:
  mod=obj.modifiers.new('Rounded manufactured edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 parts.append(obj);return obj
def cylinder(c,r,h,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=h,location=c);obj=bpy.context.object;obj.data.materials.append(mat(material));parts.append(obj);return obj
def text(body,c,size,material):
 bpy.ops.object.text_add(location=c);obj=bpy.context.object;obj.rotation_euler=Matrix(((0,0,-1),(-1,0,0),(0,1,0))).to_euler();obj.data.body=body;obj.data.align_x='CENTER';obj.data.align_y='CENTER';obj.data.size=size;obj.data.extrude=.001;obj.data.resolution_u=5;obj.data.materials.append(mat(material));bpy.ops.object.convert(target='MESH');parts.append(bpy.context.object)
def finish(name):
 bpy.ops.object.select_all(action='DESELECT')
 for obj in parts:obj.hide_set(False);obj.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();obj=bpy.context.object;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');export(obj,name);parts.clear()
# Restrained track branding, readable ahead at kart-eye height.
for label,body in [('Circuit','DESERT KARTING'),('Series','ROAD TO F1')]:
 box((0,0,1.1),(.10,4.8,1.05),'Trim',.025);box((-.062,0,1.1),(.018,4.65,.91),'Ivory');text(body,(-.078,0,1.13),.39,'Trim');box((-.08,0,.72),(.02,3.9,.035),'Teal',0)
 for y in [-1.9,1.9]:cylinder((.03,y,.45),.035,.9,'Metal')
 finish('SM_ED_Board_'+label)
for number in range(1,8):
 box((0,0,1.55),(.10,1.10,2.50),'Trim',.035);box((-.063,0,1.65),(.018,.98,1.85),'Teal');text('%02d'%number,(-.08,0,1.85),.70,'Letter');text('TURN',(-.08,0,1.15),.19,'Letter');box((-.075,0,.57),(.018,1,.11),'Ivory',0)
 for y in [-.35,.35]:cylinder((0,y,.25),.04,.5,'Metal')
 finish('SM_ED_Turn_%02d'%number)
# Narrow curved event pennant with anchored pole, no noisy animation.
cylinder((0,0,2.6),.033,5.2,'Metal');vs=[];fs=[]
for j in range(13):
 t=j/12;z=1.5+t*3.6;width=.65*math.sin(math.pi*(.10+.86*t));bend=.10*math.sin(t*math.pi)
 vs.extend([(bend,0,z),(bend+.035*math.sin(t*7),width,z)])
for j in range(12):fs.append((j*2,j*2+1,j*2+3,j*2+2))
parts.append(mesh('Pennant',vs,fs,['Teal']));finish('SM_ED_EventPennant')
# Small marshal shade station; no paddock, trailers or garage area.
for x in [-1.05,1.05]:
 for y in [-1.25,1.25]:cylinder((x,y,1.2),.045,2.4,'Metal')
roof=mesh('Shade', [(-1.3,-1.5,2.45),(-1.3,1.5,2.45),(1.3,-1.5,2.65),(1.3,1.5,2.65)],[(0,1,3,2)],['Fabric']);parts.append(roof);box((-1.28,0,2.29),(.08,2.85,.27),'Trim');text('MARSHAL',(-1.33,0,2.28),.20,'Letter');box((.98,0,1),(.10,2.4,.6),'Teal');finish('SM_ED_MarshalShade')
# Save authored assets separately, never overwriting existing work.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'EnvironmentDepth.blend'))
# Placement uses actual road/curb/runoff source geometry and measured boundaries.
trees=[]
for p in sorted((R/'Art/DesertKarting/Meshes').glob('SM_DK_02_*.fbx')):
 old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(p))
 for obj in set(bpy.data.objects)-old:
  if obj.type=='MESH':trees.append(BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[list(p.vertices) for p in obj.data.polygons]))
def clearance(x,y):return min(t.find_nearest(Vector((x*.01,-y*.01,.16)))[3]*100 for t in trees)
def place(name,xy,yaw=0,scale=(1,1,1),kind='landscape',z=None):placements.append({'mesh':name,'xy':list(xy),'yaw':yaw,'scale':list(scale),'kind':kind,'z':z})
data=json.loads((R/'Art/RacingAI/track_edges.json').read_text());route=data['center'];n=len(route);corners=json.loads((R/'Art/DesertRoute/audit.json').read_text())['corners']
for i,(x,y,yaw,variant,scale) in enumerate([(-23500,-10500,90,0,1),(28500,-11000,90,1,1.15),(2000,15000,0,2,1),(1000,-38000,0,1,1.15),(-40000,-11000,88,2,1.8),(44000,-13000,95,0,1.8)]):place('SM_ED_Ridge_'+str(variant),(x,y),yaw,(scale,scale,1 if i<4 else 1.5),'horizon',-60)
anchors=[]
for i in range(30,n,22):
 for side in ['left','right']:
  c=Vector(route[i][:2]);e=Vector(data[side][i][:2]);normal=(e-c).normalized();p=e+normal*rng.uniform(1500,2600)
  if not (-11000<p.x<13500 and -25500<p.y<4500):continue
  if clearance(p.x,p.y)<650 or any((p-a).length<1100 for a in anchors):continue
  anchors.append(p)
for i,a in enumerate(anchors):
 if i%2==0:
  for j in range(2 if i%4 else 3):
   x=a.x+rng.uniform(-280,280);y=a.y+rng.uniform(-280,280)
   if clearance(x,y)<550:continue
   scale=rng.uniform(.80,1.13);place('SM_ED_Palm_'+str((i+j)%2),(x,y),rng.uniform(0,360),(scale,scale,scale),'palm')
 for j in range(3):
  x=a.x+rng.uniform(-400,400);y=a.y+rng.uniform(-400,400)
  if clearance(x,y)>180:
   scale=rng.uniform(.9,2.0);place('SM_ED_Rock',(x,y),rng.uniform(0,360),(scale,scale*.85,scale),'rock')
 for j in range(26):
  angle=rng.uniform(0,math.tau);r=rng.uniform(120,480);x=a.x+math.cos(angle)*r;y=a.y+math.sin(angle)*r
  if clearance(x,y)>110:
   s=rng.uniform(.9,1.6);place('Grass'+str(j%3),(x,y),rng.uniform(0,360),(s,s,s),'grass')
for corner in corners:
 i=(corner['index']-9)%n;c=Vector(route[i][:2]);side='left' if corner['angle_deg']<0 else 'right';e=Vector(data[side][i][:2]);normal=(e-c).normalized();p=e+normal*650;target=Vector(route[(i-15)%n][:2]);yaw=math.degrees(math.atan2(target.y-p.y,target.x-p.x))+180
 if clearance(p.x,p.y)>250:place('SM_ED_Turn_%02d'%corner['number'],p,yaw,kind='turn_marker')
 p=e+normal*950
 if clearance(p.x,p.y)>180:place('SM_ED_EventPennant',p,yaw,kind='pennant')
 if corner['number'] in [2,5,7]:
  p=e+normal*1450
  if clearance(p.x,p.y)>450:place('SM_ED_MarshalShade',p,yaw,kind='marshal')
for i in [34,80,153,193,277,370,457,568,641,704]:
 c=Vector(route[i][:2]);e=Vector(data['left'][i][:2]);p=e+(e-c).normalized()*950;target=Vector(route[(i-12)%n][:2]);yaw=math.degrees(math.atan2(target.y-p.y,target.x-p.x))+180
 if clearance(p.x,p.y)>300:place('SM_ED_Board_'+('Circuit' if i%2 else 'Series'),p,yaw,kind='branding')
(O/'manifest.json').write_text(json.dumps({'assets':assets,'placements':placements,'source':'Original source GLB palms/rock; original ridge and trackside prop geometry; existing PBR materials and grass meshes reused.','reference':'https://www.instagram.com/p/De-ALBPIpU1/','reference_observed':'F1 game cockpit start and later circuit frame; layered signage/fencing/vegetation/hills. Dry desert environment retained.'},indent=2));print('DEPTH_ASSETS',len(assets),'PLACEMENTS',len(placements),'GROVES',len(anchors),flush=True)



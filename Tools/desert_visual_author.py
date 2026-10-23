"""Blender 5.2: additive visual assets only. Never saves or edits the source GLB/blend."""
import bpy,bmesh,math,json,re,struct,zlib
import numpy as np
from mathutils import Matrix,Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/DesertVisual';(OUT/'Meshes').mkdir(parents=True,exist_ok=True);(OUT/'Textures').mkdir(exist_ok=True)
N=1024;rng=np.random.default_rng(21783)
def noise(c):
 g=rng.random((c,c));t=np.arange(N)*c/N;i=t.astype(int);f=t-i;f=f*f*(3-2*f)
 a=g[i[:,None]%c,i[None,:]%c];b=g[i[:,None]%c,(i[None,:]+1)%c];d=g[(i[:,None]+1)%c,i[None,:]%c];e=g[(i[:,None]+1)%c,(i[None,:]+1)%c]
 return (a*(1-f[None,:])+b*f[None,:])*(1-f[:,None])+(d*(1-f[None,:])+e*f[None,:])*f[:,None]
def png(name,a):
 a=np.uint8(np.clip(a,0,1)*255)
 if a.ndim==2:a=np.repeat(a[:,:,None],3,axis=2)
 h,w,_=a.shape
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 (OUT/'Textures'/(name+'.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+r.tobytes() for r in a),6))+chunk(b'IEND',b''))
def pbr(name,base,height,rough):
 dx=(np.roll(height,-1,1)-np.roll(height,1,1))*N/4;dy=(np.roll(height,-1,0)-np.roll(height,1,0))*N/4
 n=np.stack([-dx,dy,np.ones_like(dx)],2);n/=np.linalg.norm(n,axis=2)[:,:,None]
 png(name+'_BaseColor',base);png(name+'_NormalDX',n*.5+.5);png(name+'_Roughness',rough)
fine=noise(320);med=noise(90);broad=noise(9);grain=rng.random((N,N))
aggregate=np.clip((fine-.43)*1.8,0,1);tone=.16+.085*aggregate+.016*(broad-.5)+.018*(grain-.5)
pbr('Asphalt',tone[:,:,None]*np.array([.94,.98,1.04]),.0013*fine+.0003*grain,.84+.13*med)
chips=np.clip((noise(110)-.62)*5,0,1);png('Wear',chips*(.4+.6*fine))
pbr('Paint',(.70+.17*med-.17*chips)[:,:,None]*np.array([1.,.98,.92]),.0006*fine+.001*chips,.72+.22*med)
yy,xx=np.mgrid[:N,:N];mortar=np.maximum((yy%170<5).astype(float),((xx+(yy//170%2)*128)%256<4).astype(float))
pbr('Masonry',(.71+.12*broad+.09*med-.20*mortar)[:,:,None]*np.array([1,.94,.82]),.001*fine-.002*mortar,.82+.13*med)
ribs=(.5+.5*np.cos(yy/N*math.tau*42))**7
pbr('Metal',(.61+.09*med-.13*ribs)[:,:,None]*np.ones(3),.0004*fine+.002*ribs,.42+.26*med)
weave=(np.sin(xx*math.pi/2)*np.sin(yy*math.pi/2))*.5+.5
pbr('Fabric',(.71+.12*broad+.05*weave)[:,:,None]*np.array([1,.99,.97]),.00045*weave,.85+.1*med)
pbr('Rubber',(.20+.06*med+.03*grain)[:,:,None]*np.ones(3),.0006*fine,.85+.12*med)
# Macro racing-rubber atlas follows the actual source road, not a replacement layout.
import ast
source=ast.parse((ROOT.parent/'artifacts/desert-karting-circuit/build_scene.py').read_text())
for n in source.body:
 if isinstance(n,ast.FunctionDef) and n.name=='path':exec(compile(ast.Module(body=[n],type_ignores=[]),'source_path','exec'))
tracknode=next(n for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='track' for t in n.targets))
route=path(ast.literal_eval(tracknode.value.args[0]),22)
SZ=2048;atlas=np.zeros((SZ,SZ,3));origin=(-15000,-26000);span=(32000,30000)
for i,p in enumerate(route):
 prev=route[(i-1)%len(route)];nxt=route[(i+1)%len(route)];t=(nxt-prev).normalized();normal=Vector((-t.y,t.x))
 curvature=abs((p-prev).normalized().cross((nxt-p).normalized()))
 for off in [-.82,.82]:
  for f in np.linspace(0,1,max(2,math.ceil((nxt-p).length/.08)),endpoint=False):
   a=p.lerp(nxt,float(f))+normal*off;x=(a.y+28)*100;y=(-a.x-103)*100
   px=int((x-origin[0])/span[0]*SZ);py=int((y-origin[1])/span[1]*SZ)
   if 1<=px<SZ-1 and 1<=py<SZ-1:
    strength=min(.70,.08+curvature*24)*(.7+.3*math.sin(i*.19)**2)
    atlas[py-1:py+2,px-1:px+2,0]=np.maximum(atlas[py-1:py+2,px-1:px+2,0],strength*np.array([[.02,.15,.02],[.15,1,.15],[.02,.15,.02]]))
png('RoadMask',atlas)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.glb'))
align=Matrix(((0,1,0,28),(-1,0,0,103),(0,0,1,-.16),(0,0,0,1)))
assets=[];placements=[];replacements={};heads=[];barriers=[]
def export(ob,name,slots=None):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(OUT/'Meshes'/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False)
 assets.append({'name':name,'slots':slots or [s.name for s in ob.data.materials],'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons)})
def components(bm):
 seen=set()
 for v in bm.verts:
  if v in seen:continue
  stack=[v];group=[];seen.add(v)
  while stack:
   w=stack.pop();group.append(w)
   for e in w.link_edges:
    q=e.other_vert(w)
    if q not in seen:seen.add(q);stack.append(q)
  yield group
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH':continue
 name=ob.name
 selected=name.startswith(('07 ','09 ')) and name.rsplit(' | ',1)[-1] in ['cream','stone','white','red','blue']
 filter_seats=name.startswith('05 ') and name.endswith((' | blue',' | red'))
 filter_blocks=name.startswith('04 ') and name.endswith((' | green',' | white'))
 get_heads=name.startswith('05 ') and name.endswith(' | skin')
 if not(selected or filter_seats or filter_blocks or get_heads):continue
 ob.data=ob.data.copy();ob.data.transform(align@ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
 remove=[]
 for group in list(components(bm)) if filter_seats or filter_blocks or get_heads else []:
  coords=np.array([list(v.co) for v in group]);lo=coords.min(0);hi=coords.max(0);d=hi-lo;c=(hi+lo)/2
  if filter_seats and np.allclose(d,[.59,.55,.20],atol=.006):remove+=group
  if filter_blocks and abs(d[2]-.90)<.006 and len(group)==8:
   xy=coords[:,:2]-c[:2];vals,vecs=np.linalg.eigh(xy.T@xy);v=vecs[:,-1]
   barriers.append({'location_cm':[c[0]*100,-c[1]*100,(c[2]-.45)*100],'yaw':math.degrees(math.atan2(-v[1],v[0])),'white':name.endswith('white')});remove+=group
  if get_heads and .26<d[2]<.29 and .19<d[0]<.24:heads.append([c[0]*100,-c[1]*100,(c[2]+.10)*100])
 if get_heads:bm.free();continue
 if remove:bmesh.ops.delete(bm,geom=remove,context='VERTS')
 bm.to_mesh(ob.data);bm.free()
 if not len(ob.data.polygons):replacements[name]=None;continue
 if selected:
  mod=ob.modifiers.new('Small manufactured edge radii','BEVEL');mod.width=.025;mod.segments=2;mod.limit_method='ANGLE';mod.angle_limit=.7
  bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=ob.modifiers.new('Face weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True
  try:bpy.ops.object.modifier_apply(modifier=mod.name)
  except RuntimeError:pass
 nm='SM_DV_'+re.sub('[^A-Za-z0-9]+','_',name).strip('_');export(ob,nm);replacements[name]=nm
# Modular meshes use Unreal centimetres only at placement. Local mesh units remain metres.
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
parts=[]
def material(n):return bpy.data.materials.get(n) or bpy.data.materials.new(n)
def cube(c,s,mat,bevel=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(c[0],-c[1],c[2]));o=bpy.context.object;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material(mat))
 if bevel:
  m=o.modifiers.new('Beveled edges','BEVEL');m.width=bevel;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
 parts.append(o);return o
def cyl(c,r,depth,mat,vertices=12):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=(c[0],-c[1],c[2]));o=bpy.context.object;o.data.materials.append(material(mat));parts.append(o);return o
def text(body,c,size,mat):
 bpy.ops.object.text_add(location=(c[0],-c[1],c[2]),rotation=(math.pi/2,0,math.pi));o=bpy.context.object;o.data.body=body;o.data.align_x='CENTER';o.data.size=size;o.data.extrude=.001;o.data.materials.append(material(mat));bpy.ops.object.convert(target='MESH');parts.append(bpy.context.object)
def finish(name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');o.name=name;export(o,name);parts.clear();o.select_set(False);o.hide_set(True)
def place(name,p,yaw=0,scale=(1,1,1)):placements.append({'mesh':name,'location_cm':p,'yaw':yaw,'scale':scale})
# Priority 2: actual shutter relief, recessed frame, sill, pilaster caps and trim.
cube((0,.10,1.95),(3.05,.10,3.50),'Shutter')
for z in np.arange(.30,3.70,.20):cube((0,.025,float(z)),(2.96,.065,.055),'Shutter',.01)
for x in [-1.62,1.62]:
 cube((x,0,2.1),(.18,.20,4.2),'Trim');cube((x,-.03,.17),(.28,.28,.25),'Stone');cube((x,-.03,4.12),(.30,.28,.20),'Stone')
cube((0,-.015,3.93),(3.42,.25,.18),'Trim');cube((0,-.20,4.15),(3.75,.60,.12),'Metal')
cube((0,-.05,.16),(3.25,.25,.10),'Metal');cube((1.10,-.02,1.12),(.25,.055,.09),'Metal')
cube((0,-.065,3.48),(1.35,.04,.25),'Trim');text('PIT SERVICE',(0,-.092,3.41),.14,'Letter')
finish('SM_DV_PitBay')
for i,y in enumerate(range(-86,16,5)):place('SM_DV_PitBay',[(y+28)*100,1155,-16])
cube((0,0,0),(1.0,.055,.42),'Trim');text('ROAD TO F1',(0,-.04,-.055),.11,'Letter');finish('SM_DV_Banner')
for y in [-76,-56,-36,-16,4]:place('SM_DV_Banner',[(y+28)*100,1140,465],scale=(2.6,1,2))
# Priority 3: rounded water barriers with molded top, feet, handles and reflectors.
for color in ['Teal','Ivory']:
 cube((0,0,.42),(1.30,.65,.72),color,.09);cube((0,0,.82),(1.18,.44,.10),color,.04)
 for x in [-.48,.48]:
  cube((x,0,.08),(.24,.78,.16),'Dark',.04);cube((x,-.334,.48),(.19,.018,.16),'Letter',.02);cube((x,0,.875),(.22,.13,.025),'Dark',.02)
 for x in [-.25,0,.25]:cube((x,-.334,.36),(.018,.025,.40),color,.005)
 finish('SM_DV_Barrier'+color)
for i,b in enumerate(barriers):place('SM_DV_Barrier'+('Ivory' if b['white'] else 'Teal'),b['location_cm'],b['yaw'])
cube((0,0,.47),(1.29,1.08,.85),'Trim',.045);cube((0,-.55,.48),(1.16,.04,.66),'Shutter',.025)
for x in [-.53,.53]:
 for z in [.16,.80]:cube((x,-.59,z),(.17,.08,.12),'Metal',.02)
cube((0,-.59,.57),(.25,.07,.05),'Metal');cube((0,0,.94),(1.35,1.14,.10),'Metal',.025)
for x in [-.48,.48]:
 for y in [-.38,.38]:cyl((x,y,.06),.07,.12,'Rubber')
finish('SM_DV_ToolChest')
for x in [-73,-56]:
 for y in range(-64,-8,8):place('SM_DV_ToolChest',[(y+29)*100,(-x-107)*100,-16])
for z in [.13,.38,.63]:
 bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=10,location=(0,0,z),major_radius=.29,minor_radius=.105);o=bpy.context.object;o.data.materials.append(material('Rubber'))
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o)
 for a in range(0,360,30):
  rad=math.radians(a);o=cube((.392*math.cos(rad),.392*math.sin(rad),z),(.016,.025,.13),'Rubber',.003);o.rotation_euler.z=-rad
finish('SM_DV_TireStack')
for y in [-65,-49,-33,-17]:place('SM_DV_TireStack',[(y+28)*100,-5600,-16])
cube((0,0,-.025),(.90,.40,.05),'Dark',.01)
for x in np.arange(-.43,.44,.05):cube((float(x),0,.005),(.016,.38,.025),'Metal',.003)
finish('SM_DV_Drain')
for y in range(-80,16,5):place('SM_DV_Drain',[(y+28)*100,1050,-4])
cyl((0,0,.42),.12,.64,'Red');cyl((0,0,.78),.04,.10,'Metal');cube((0,-.13,.43),(.13,.02,.25),'Letter');cube((0,0,.88),(.22,.10,.045),'Dark');finish('SM_DV_Extinguisher')
for y in [-81,-61,-41,-21,-1]:place('SM_DV_Extinguisher',[(y+28)*100,1090,20])
cube((0,0,.50),(1.55,.66,1.02),'Trim',.07);cube((0,-.35,.57),(1.30,.04,.55),'Red',.025)
cube((0,0,1.03),(1.58,.70,.08),'Metal',.025);text('PIT',(0,-.38,.48),.20,'Letter')
for x in [-.57,.57]:cube((x,0,.06),(.25,.78,.12),'Dark',.025)
finish('SM_DV_PitSignPod')
for y in range(-73,25,8):place('SM_DV_PitSignPod',[(y+28)*100,-1100,-16])
replacements['14 Timing gantry signs and pit furniture | red']=None
# Priority 4: reusable bucket seat backs replace the original flat seat cubes.
for color in ['SeatBlue','SeatRed','SeatGold']:
 cube((0,0,.15),(.54,.50,.14),color,.06);cube((0,.22,.42),(.54,.10,.55),color,.055)
 for x in [-.19,.19]:cube((x,0,.045),(.035,.38,.09),'Metal',.008)
 for x in [-.18,.18]:cyl((x,.20,.66),.018,.025,'Metal',8)
 finish('SM_DV_'+color)
for r in range(12):
 for k in range(95):
  if k%31<3:continue
  color='SeatRed' if r%3==0 else ('SeatGold' if k%31==3 else 'SeatBlue')
  place('SM_DV_'+color,[(33+k*.8)*100,(12+r*.9)*100,(1.5+r*.4-.16)*100])
for color in ['CapBlue','CapRed','CapIvory']:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=(0,0,.015));o=bpy.context.object;o.scale=(.125,.12,.065);o.data.materials.append(material(color));parts.append(o)
 cube((0,-.12,.005),(.18,.12,.02),color,.03);finish('SM_DV_'+color)
for i,p in enumerate(heads):
 if i%3==0:place('SM_DV_'+['CapBlue','CapRed','CapIvory'][i%7%3],p,yaw=((i*71)%100)-50)
(OUT/'manifest.json').write_text(json.dumps({'assets':assets,'replacements':replacements,'placements':placements,'barrier_count':len(barriers),'spectator_heads':len(heads),'mask_origin_cm':origin,'mask_span_cm':span,'texture_tile_cm':200,'sources':'User GLB; new original procedural PBR maps and secondary modeling. No external downloads.','style':'Warm stone, dark teal trim, saturated blue/red seating, softly bevelled secondary forms'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'DesertVisual_Details.blend'))
print('DESERT_VISUAL_AUTHOR_COMPLETE',len(assets),len(placements),flush=True)

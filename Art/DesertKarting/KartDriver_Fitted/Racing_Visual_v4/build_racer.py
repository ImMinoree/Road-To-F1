"""Non-destructive outfit adaptation using the installed CC0 MakeHuman work suit.
No replacement human, changes to rest rig/body weights, kart or lighting.
"""
import bpy,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
SOURCE=OUT.parent/'Refinement_v3/Kart_With_MakeHuman_Fitted_v3.blend'
ASSETS=Path('C:/Users/GBURG-4/AppData/Local/makehuman-community/makehuman/data')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene;arm=bpy.data.objects['Game_engine'];body=bpy.data.objects['kart_driverMesh'];casual=bpy.data.objects['male_casualsuit04Mesh'];shoe=bpy.data.objects['shoes05Mesh']
col=bpy.data.collections.new('RACER V4 | separate editable outfit');scene.collection.children.link(col)
made=[]
def sig():
 def h(x):return hashlib.sha256(repr(x).encode()).hexdigest()
 return {'kart':{o.name:h((list(map(list,o.matrix_world)),[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])) for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')},'lighting':{o.name:h((list(map(list,o.matrix_world)),o.data.energy,o.data.color[:],o.data.type,o.data.size if hasattr(o.data,'size') else None)) for o in scene.objects if o.type=='LIGHT'},'world':h([(n.name,n.type,[(s.name,str(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]) for n in scene.world.node_tree.nodes]),'rig':h([(b.name,b.parent.name if b.parent else '',list(map(list,b.matrix_local))) for b in arm.data.bones]),'body_weights':h([[(g.group,g.weight) for g in v.groups] for v in body.data.vertices]),'body_geometry':h([tuple(v.co) for v in body.data.vertices])}
BEFORE=sig()
def smooth(o):
 for p in o.data.polygons:p.use_smooth=True
def mesh(name,v,f,mat=None,matrix=None,uv=None,weights=None,sub=0,thick=0):
 me=bpy.data.meshes.new(name+' | topology');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);made.append(o)
 if matrix is not None:o.matrix_world=matrix
 if mat:me.materials.append(mat)
 if uv:
  layer=me.uv_layers.new(name='UV | tailored');
  for p,coords in zip(me.polygons,uv):
   for li,co in zip(p.loop_indices,coords):layer.data[li].uv=co
 if weights:
  for i,ws in enumerate(weights):
   for n,w in ws.items():
    g=o.vertex_groups.get(n) or o.vertex_groups.new(name=n)
    if w>1e-5:g.add([i],w,'REPLACE')
  m=o.modifiers.new('MakeHuman skeleton | original bind','ARMATURE');m.object=arm;m.use_deform_preserve_volume=True
 if sub:
  m=o.modifiers.new('Tailored surface subdivision','SUBSURF');m.levels=min(sub,2);m.render_levels=sub
 if thick:
  m=o.modifiers.new('Physical material thickness','SOLIDIFY');m.thickness=thick;m.offset=-1
 smooth(o);return o
def material(name,color,rough=.4,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
black=material('Racer | charcoal woven nylon',(0.003,.004,.006),.57)
red=material('Racer | crimson woven panels',(.21,.003,.008),.5)
white=material('Racer | warm white woven panels',(.68,.7,.69),.58)
rubber=material('Racer | elastic cuffs and rubber',(.009,.011,.014),.7)
leather=material('Racer | black glove leather',(.019,.02,.025),.44)
leather_red=material('Racer | red glove leather',(.35,.012,.02),.45)
thread=material('Racer | light seam thread',(.35,.36,.34),.7)
darkthread=material('Racer | black raised seam piping',(.009,.011,.015),.65)
metal=material('Racer | brushed titanium hardware',(.24,.25,.27),.29,.83)
paint=material('Helmet | gloss black multilayer paint',(.009,.012,.019),.19,.18)
paintred=material('Helmet | gloss crimson panels',(.48,.006,.015),.21,.1)
paintwhite=material('Helmet | porcelain white graphics',(.75,.77,.77),.19,.08)
visor=material('Helmet | dark smoked polycarbonate',(.011,.018,.024),.095,.1)
vp=visor.node_tree.nodes.get('Principled BSDF');vp.inputs['Transmission Weight'].default_value=.12;vp.inputs['IOR'].default_value=1.54
for m in [paint,paintred,paintwhite]:
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.65;p.inputs['Coat Roughness'].default_value=.13
# Small repeatable UV textures, packed plus exported; no AI or external downloads.
TEX=OUT/'textures';TEX.mkdir(exist_ok=True)
N=512;y,x=np.mgrid[:N,:N];u=x/N;v=y/N
height=.5+.20*np.sin(2*np.pi*u*32)*np.cos(2*np.pi*v*32)+.08*np.cos(2*np.pi*(u+v)*64)
dy,dx=np.gradient(height);norm=np.stack([-dx*3,-dy*3,np.ones_like(dx)],axis=-1);norm/=np.linalg.norm(norm,axis=-1)[...,None]
def image_array(name,arr,noncolor=True):
 if arr.ndim==2:arr=np.repeat(arr[...,None],3,axis=-1)
 rgba=np.concatenate((arr,np.ones((N,N,1))),axis=-1).astype(np.float32)
 im=bpy.data.images.new(name,width=N,height=N);im.colorspace_settings.name='Non-Color' if noncolor else 'sRGB';im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
normalimg=image_array('woven_twill_normal',norm*.5+.5);roughimg=image_array('woven_twill_roughness',np.clip(.52+.12*(height-.5),0,1))
for m in [black,red,white,leather,leather_red,rubber]:
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');uv=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs['Scale'].default_value=13;nt.links.new(uv.outputs['UV'],mapping.inputs[0])
 tx=nt.nodes.new('ShaderNodeTexImage');tx.image=normalimg;nt.links.new(mapping.outputs[0],tx.inputs['Vector']);n=nt.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.23 if m in [black,red,white] else .12;nt.links.new(tx.outputs['Color'],n.inputs['Color']);nt.links.new(n.outputs['Normal'],p.inputs['Normal'])
 tx=nt.nodes.new('ShaderNodeTexImage');tx.image=roughimg;nt.links.new(mapping.outputs[0],tx.inputs['Vector']);nt.links.new(tx.outputs['Color'],p.inputs['Roughness'])
 if m in [black,red,white]:
  p.inputs['Sheen Weight'].default_value=.08;p.inputs['Sheen Roughness'].default_value=.8;p.inputs['Specular IOR Level'].default_value=.12
  for link in list(nt.links):
   if link.to_socket==p.inputs['Roughness']:nt.links.remove(link)
  p.inputs['Roughness'].default_value=.82
# Recover the exported base vertex correspondence from MakeHuman's own hide-face mask.
base=np.load(ASSETS/'3dobjs/base.npz');cp=np.load(ASSETS/'clothes/male_casualsuit04/male_casualsuit04.mhpxy');sp=np.load(ASSETS/'clothes/shoes05/shoes05.mhpxy');wp=np.load(ASSETS/'clothes/male_worksuit01/male_worksuit01.mhpxy');wm=np.load(ASSETS/'clothes/male_worksuit01/male_worksuit01.npz')
lic=wp['lic_str'].tobytes().decode();assert 'CC0' in lic
delete=cp['deleteVerts']|sp['deleteVerts'];f=base['fvert'];mask=(base['group']==0)&(~np.all(delete[f],axis=1));ids=np.unique(f[mask]);remap={int(x):i for i,x in enumerate(ids)}
assert len(ids)==len(body.data.vertices)
assert all(tuple(remap[int(i)] for i in a)==tuple(b.vertices) for a,b in zip(f[mask],body.data.polygons)),'Source topology correspondence differs'
def default_proxy(p):return (base['coord'][p['ref_vIdxs']]*p['weights'][...,None]).sum(axis=1)+p['offsets']
samples=np.concatenate((base['coord'][ids],default_proxy(cp)));targets=np.array([tuple(v.co) for v in body.data.vertices]+[tuple(v.co) for v in casual.data.vertices])
A=np.column_stack((samples,np.ones(len(samples))));affine=np.linalg.lstsq(A,targets,rcond=None)[0];residual=targets-A@affine
kd=KDTree(len(samples))
for i,p in enumerate(samples):kd.insert(p,i)
kd.balance()
workdefault=default_proxy(wp);coords=[]
for p in workdefault:
 nn=kd.find_n(p,10);w=np.array([1/max(d,.025)**3 for _,_,d in nn]);w/=w.sum();coords.append(np.append(p,1)@affine+sum(residual[j]*a for (_,j,_),a in zip(nn,w)))
# Transfer garment binding by nearby original rest cloth/skin, preserving ALL source weights.
weightsamples=[{o.vertex_groups[g.group].name:g.weight for g in v.groups} for o in (body,casual) for v in o.data.vertices]
targetkd=KDTree(len(targets))
for i,p in enumerate(targets):targetkd.insert(p,i)
targetkd.balance()
def bind_near(p,k=4):
 nn=targetkd.find_n(p,k);s={};den=0
 for _,idx,d in nn:
  w=1/max(d,.1)**3;den+=w
  for n,a in weightsamples[idx].items():s[n]=s.get(n,0)+w*a
 s={n:w/den for n,w in s.items() if w/den>.001};total=sum(s.values());return {n:w/total for n,w in s.items()}
weights=[bind_near(p) for p in coords]
faces=[tuple(dict.fromkeys(map(int,f))) for f in wm['fvert']];uvs=[[tuple(wm['texco'][i]) for i in f[:len(face)]] for f,face in zip(wm['fuvs'],faces)]
suit=mesh('RACER | fitted one-piece suit',coords,faces,black,body.matrix_world,uvs,weights,sub=2,thick=.14)
# Work-suit topology is a new separate CC0 garment, not a recolored casual mesh.
suit.data.materials.append(red);suit.data.materials.append(white)
def panel(p,ws):
 x,y,z=p;side=abs(x)
 armw=sum(w for n,w in ws.items() if 'arm_' in n or 'clavicle_' in n)
 if armw>.45:
  if y>112 and side<30:return 1
  return 2 if z>1.0 and y>92 else (1 if z<-1 else 0)
 if y>116:return 1 if side>9 else 0
 if y>89:return 2 if 10<side<14 else 0
 if y>35:return 1 if side>15 else 0
 return 0
for p in suit.data.polygons:
 center=sum((suit.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices);ws={}
 for i in p.vertices:
  for n,w in weights[i].items():ws[n]=ws.get(n,0)+w/len(p.vertices)
 p.material_index=1 if center.y>119 and abs(center.x)>13 else 0
# Tailoring sculpt: broad tension folds, small compression wrinkles, no polygon-only claim.
for ve in suit.data.vertices:
 p=ve.co;ws=weights[ve.index];y=p.y;side=abs(p.x)
 joint=sum(w for n,w in ws.items() if n.startswith(('calf','lowerarm')))
 amp=.10+.11*joint
 wave=math.sin(y*2.1+p.x*.32)*math.sin(y*.38+side*.25)
 ve.co+=ve.normal*(amp*wave)
suit.data.update()
casual.hide_render=True;casual.hide_set(True)
shoe.hide_render=True;shoe.hide_set(True)
# Add surface-bound geometric seam piping and panels. All use the same skinning.
def tubes(name,paths,radius,mat,matrix,weightpaths=None,sides=6):
 vv=[];ff=[];uv=[];ww=[]
 for pi,path in enumerate(paths):
  start=len(vv)
  for j,p in enumerate(path):
   p=Vector(p);t=Vector(path[min(j+1,len(path)-1)])-Vector(path[max(0,j-1)])
   if t.length<1e-9:t=Vector((0,1,0))
   t.normalize();u=t.cross(Vector((0,0,1)))
   if u.length<.1:u=t.cross(Vector((1,0,0)))
   u.normalize();v=t.cross(u).normalized()
   for k in range(sides):vv.append(p+radius*(u*math.cos(k*2*math.pi/sides)+v*math.sin(k*2*math.pi/sides)));ww.append(weightpaths[pi][j] if weightpaths else {})
  for j in range(len(path)-1):
   for k in range(sides):
    ff.append((start+j*sides+k,start+j*sides+(k+1)%sides,start+(j+1)*sides+(k+1)%sides,start+(j+1)*sides+k));uv.append(((k/sides,j/20),((k+1)/sides,j/20),((k+1)/sides,(j+1)/20),(k/sides,(j+1)/20)))
 return mesh(name,vv,ff,mat,matrix,uv,ww if weightpaths else None)
# Material boundary seams follow original garment edges, so they deform with the outfit.
edgefaces={}
for p in suit.data.polygons:
 for a,b in p.edge_keys:edgefaces.setdefault(tuple(sorted((a,b))),[]).append(p.material_index)
paths=[];wps=[];stitches=[];stitchw=[]
for (a,b),mats in edgefaces.items():
 if len(mats)==2 and mats[0]!=mats[1]:
  pa=suit.data.vertices[a].co+suit.data.vertices[a].normal*.18;pb=suit.data.vertices[b].co+suit.data.vertices[b].normal*.18
  paths.append([pa,pb]);wps.append([weights[a],weights[b]])
  d=(pb-pa).length
  for t in np.arange(.08,.95,max(.12,.40/max(d,.1))):
   stitches.append([pa.lerp(pb,float(t)),pa.lerp(pb,min(.99,float(t)+.13))]);stitchw.append([weights[a],weights[b]])
tubes('RACER | raised panel seam piping',paths,.075,darkthread,body.matrix_world,wps)
tubes('RACER | seam top stitching',stitches,.022,thread,body.matrix_world,stitchw,4)
# Surface patches from existing garment topology: padding is independent real geometry.
def patch(source,name,predicate,mat,offset=.15,sub=1,thick=.1):
 polys=[p for p in source.data.polygons if predicate(p)];idx=sorted(set(i for p in polys for i in p.vertices));mp={x:i for i,x in enumerate(idx)}
 if not idx:return None
 vs=[source.data.vertices[i].co+source.data.vertices[i].normal*offset for i in idx];fs=[tuple(mp[i] for i in p.vertices) for p in polys];ws=[{source.vertex_groups[g.group].name:g.weight for g in source.data.vertices[i].groups} for i in idx]
 uv=[[tuple(source.data.uv_layers.active.data[l].uv) for l in p.loop_indices] for p in polys] if source.data.uv_layers else None
 return mesh(name,vs,fs,mat,source.matrix_world,uv,ws,sub,thick)
def center(source,p):return sum((source.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
# Long sleeves follow the organic source anatomy and its precise arm weights.
def sleevepoly(p):
 def w(i):
  v=body.data.vertices[i]
  return sum(g.weight for g in v.groups if any(t in body.vertex_groups[g.group].name for t in ['upperarm_','lowerarm_']))
 return all(w(i)>.62 for i in p.vertices)
sleeves=patch(body,'RACER | tailored long anatomical sleeves',sleevepoly,black,.34,2,.14)
if sleeves:
 sleeves.data.materials.clear();sleeves.data.materials.append(white)
# Continuous sewn-on panels are sampled from the garment surface, not assigned per coarse face.
def projected_panel(source,name,grid,mat,direction='front',offset=.15,stitch=True):
 disabled=[m for m in source.modifiers if m.type=='ARMATURE']
 for m in disabled:m.show_viewport=False
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=source.evaluated_get(deps);me=ev.to_mesh();verts=[v.co.copy() for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons];tree=BVHTree.FromPolygons(verts,faces);ev.to_mesh_clear()
 for m in disabled:m.show_viewport=True
 bpy.context.view_layer.update()
 skd=KDTree(len(source.data.vertices))
 for ve in source.data.vertices:skd.insert(ve.co,ve.index)
 skd.balance()
 def surface_weights(p):
  nn=skd.find_n(p,4);ws={};total=0
  for _,i,d in nn:
   w=1/max(d,.01)**3;total+=w
   for g in source.data.vertices[i].groups:
    name=source.vertex_groups[g.group].name;ws[name]=ws.get(name,0)+w*g.weight
  return {n:w/total for n,w in ws.items()}
 vv=[];ww=[];ff=[];uv=[];rows=len(grid);cols=len(grid[0])
 for row in grid:
  for x,y in row:
   origin=Vector((x,y,60 if direction=='front' else -60));hit,n,idx,d=tree.ray_cast(origin,Vector((0,0,-1 if direction=='front' else 1)))
   if hit is None:hit,n,idx,d=tree.find_nearest(Vector((x,y,0)))
   vv.append(hit+n*offset);ww.append(surface_weights(hit))
 for j in range(rows-1):
  for k in range(cols-1):a=j*cols+k;ff.append((a,a+1,a+cols+1,a+cols));uv.append(((k/(cols-1),j/(rows-1)),((k+1)/(cols-1),j/(rows-1)),((k+1)/(cols-1),(j+1)/(rows-1)),(k/(cols-1),(j+1)/(rows-1))))
 o=mesh(name,vv,ff,mat,body.matrix_world,uv,ww,2,.08)
 if stitch:
  paths=[[vv[j*cols] for j in range(rows)],[vv[j*cols+cols-1] for j in range(rows)]];wps=[[ww[j*cols] for j in range(rows)],[ww[j*cols+cols-1] for j in range(rows)]]
  tubes(name+' | sewn edges',paths,.028,thread,body.matrix_world,wps,5)
 return o
for sign,label in [(-1,'right'),(1,'left')]:
 grid=[]
 for t in np.linspace(0,1,35):
  yy=95+34*t;cx=sign*(12.0+2*math.sin(t*math.pi));width=1.6+1.5*t
  grid.append([(cx+sign*width*(u-.5),yy) for u in np.linspace(0,1,7)])
 projected_panel(suit,'RACER | '+label+' continuous red chest panel',grid,red)
 grid=[[(sign*(9.7+1.8*math.sin(t*math.pi)) + sign*.8*(u-.5),96+29*t) for u in np.linspace(0,1,5)] for t in np.linspace(0,1,35)]
 projected_panel(suit,'RACER | '+label+' white chest accent',grid,white,'front',.24)
 grid=[[(sign*(12+2*t)+sign*2.5*(u-.5),45+34*t) for u in np.linspace(0,1,9)] for t in np.linspace(0,1,45)]
 projected_panel(suit,'RACER | '+label+' red thigh insert',grid,red)
 # Visible white forearm and red shoulder patches sampled onto organic skin sleeves.
 if sleeves:
  grid=[[(sign*(37+6*t)+sign*2.8*(u-.5),104-8*t) for u in np.linspace(0,1,7)] for t in np.linspace(0,1,30)]
  projected_panel(sleeves,'RACER | '+label+' white sleeve panel',grid,white,offset=.22)
 # Spine-side red panels also give a clear rear outfit view.
 grid=[[(sign*(10+2*math.sin(t*math.pi))+sign*3*(u-.5),98+28*t) for u in np.linspace(0,1,7)] for t in np.linspace(0,1,32)]
 projected_panel(suit,'RACER | '+label+' rear red panel',grid,red,'back',.17)
grid=[[(.55*(u-.5),94+35*t) for u in np.linspace(0,1,4)] for t in np.linspace(0,1,60)]
projected_panel(suit,'RACER | central zipper placket',grid,rubber,offset=.28)
# Original high-top shoe topology retained as independent boots, with leather panels and sole.
boots=shoe.copy();boots.data=shoe.data.copy();boots.name='RACER | sculpted racing boots';col.objects.link(boots);made.append(boots);boots.hide_render=False;boots.hide_set(False);boots.data.materials.clear()
for m in [leather,leather_red,white,rubber]:boots.data.materials.append(m)
for p in boots.data.polygons:
 c=center(boots,p);p.material_index=3 if c.y<1.5 else (1 if c.y>9 else (2 if abs(c.x)>19 and c.z>1 else 0));p.use_smooth=True
m=boots.modifiers.new('Smooth leather boot surfaces','SUBSURF');m.levels=2;m.render_levels=2
# Surface-fitted laces and ankle closure are separate weighted geometry.
bootverts=[ve.co.copy() for ve in boots.data.vertices];bootfaces=[tuple(p.vertices) for p in boots.data.polygons];boottree=BVHTree.FromPolygons(bootverts,bootfaces)
for sign,s in [(1,'l'),(-1,'r')]:
 paths=[];wps=[]
 for j in range(7):
  path=[];ws=[]
  for t in np.linspace(0,1,12):
   x=sign*(16.5+2.4*(2*t-1));y=4.3+j*.95+.4*(t-.5);hit,n,_,_=boottree.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))
   if hit is None:continue
   path.append(hit+n*.12);ws.append({'foot_'+s:1})
  if len(path)>1:paths.append(path);wps.append(ws)
 if paths:tubes('RACER | '+s+' boot lacing',paths,.045,thread,body.matrix_world,wps,6)
# Glove shells are extracted from actual MakeHuman hand anatomy with original finger weights.
def handpoly(p):
 return all(sum(g.weight for g in body.data.vertices[i].groups if any(k in body.vertex_groups[g.group].name for k in ['hand_','index_','middle_','ring_','pinky_','thumb_']))>.23 for i in p.vertices)
gloves=patch(body,'RACER | anatomical five-finger gloves',handpoly,leather,.14,2,.09)
gloves.data.materials.append(leather_red);gloves.data.materials.append(white)
for p in gloves.data.polygons:
 c=center(gloves,p);p.material_index=1 if c.z<15 and c.y>90 else 0
patch(gloves,'RACER | raised glove knuckle panels',lambda p: center(gloves,p).y>91 and 46<abs(center(gloves,p).x)<50 and center(gloves,p).z<20,leather_red,.13,2,.08)
# Collar and cuff rings are fitted lofts following the anatomical bone axis in rest space.
def ring_axis(name,a,b,r1,r2,mat,bind,segments=48):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0)))
 if u.length<.1:u=axis.cross(Vector((1,0,0)))
 u.normalize();v=axis.cross(u).normalized();vv=[];ff=[];uv=[]
 for j in range(6):
  t=j/5;r=r1*(1-t)+r2*t
  for k in range(segments):
   theta=2*math.pi*k/segments;vv.append(a.lerp(b,t)+(u*math.cos(theta)+v*math.sin(theta))*r*(1+.025*math.cos(k*2*math.pi/3)))
 for j in range(5):
  for k in range(segments):ff.append((j*segments+k,j*segments+(k+1)%segments,(j+1)*segments+(k+1)%segments,(j+1)*segments+k));uv.append(((k/segments,j/5),((k+1)/segments,j/5),((k+1)/segments,(j+1)/5),(k/segments,(j+1)/5)))
 return mesh(name,vv,ff,mat,body.matrix_world,uv,[bind]*len(vv),1,.12)
invbody=body.matrix_world.inverted();invArm=arm.matrix_world.inverted()
def rest_in_body(n,tail=False):return invbody@(arm.matrix_world@(arm.data.bones[n].tail_local if tail else arm.data.bones[n].head_local))
for s in ['l','r']:
 a=rest_in_body('hand_'+s);b=rest_in_body('lowerarm_'+s);d=(b-a).normalized();ring_axis('RACER | '+s+' knitted gauntlet cuff',a+d*.3,a+d*3.9,3.3,3.6,rubber,{'lowerarm_'+s:.75,'hand_'+s:.25})
ring_axis('RACER | raised padded collar',(-.28,131,0),(-.28,137,-1.6),5.25,4.8,black,{'neck_01':.5,'spine_03':.5})
# Helmet constructed as a profiled shell with real visor aperture and chin bar.
head=arm.pose.bones['head'];headworld=arm.matrix_world@head.head
HC=Vector((headworld.x+.008,headworld.y,headworld.z+.091))
profile=[(-.153,.087,.091),(-.146,.109,.109),(-.132,.143,.124),(-.111,.162,.131),(-.073,.164,.136),(-.041,.155,.139),(-.022,.148,.14),(.006,.146,.142),(.040,.14,.139),(.072,.133,.133),(.084,.127,.128),(.105,.115,.116),(.132,.094,.096),(.153,.063,.066),(.168,.014,.015)]
SEG=96;vv=[];ff=[];uv=[];mids=[]
def shellpoint(z,rx,ry,t):
 front=max(0,math.cos(t));chin=.014*front**4*max(0,1-abs(z+.09)/.085);return HC+Vector((rx*math.cos(t)+chin,ry*math.sin(t),z))
for z,rx,ry in profile:
 for k in range(SEG):vv.append(shellpoint(z,rx,ry,2*math.pi*k/SEG))
for j in range(len(profile)-1):
 for k in range(SEG):
  t=2*math.pi*(k+.5)/SEG;wrapped=(t+math.pi)%(2*math.pi)-math.pi
  if 6<=j<10 and abs(wrapped)<1.18:continue
  ff.append((j*SEG+k,j*SEG+(k+1)%SEG,(j+1)*SEG+(k+1)%SEG,(j+1)*SEG+k));uv.append(((k/SEG,j/14),((k+1)/SEG,j/14),((k+1)/SEG,(j+1)/14),(k/SEG,(j+1)/14)))
  mids.append(0)
def headmesh(name,v,f,mat,uv=None,sub=1,thick=0):
 # Inverse rigid bind ensures exact placement in this pose and head following later.
 m=arm.data.bones['head'].matrix_local@head.matrix.inverted()@arm.matrix_world.inverted()
 return mesh(name,[m@Vector(p) for p in v],f,mat,arm.matrix_world,uv,[{'head':1}]*len(v),sub,thick/.0112 if thick else 0)
shell=headmesh('HELMET | profiled composite shell and chin bar',vv,ff,paint,uv,2,.003)
shell.data.materials.append(paintred);shell.data.materials.append(paintwhite)
for p,i in zip(shell.data.polygons,mids):p.material_index=i
# Smooth separate lacquer graphic strips follow shell curvature, including the chin bar.
for sign in [-1,1]:
 for begin,width,mat,label in [(.5,.27,paintred,'red sweep'),(.8,.075,paintwhite,'white pinstripe')]:
  vs=[];fs=[];uv=[];cols=9
  for j,(z,rx,ry) in enumerate(profile[:-1]):
   for k in range(cols):t=sign*(begin+width*k/(cols-1)-z*2.7);vs.append(shellpoint(z,rx+.0009,ry+.0009,t))
  for j in range(len(profile)-2):
   for k in range(cols-1):
    z=profile[j][0];t=abs(begin+width*(k+.5)/(cols-1)-z*2.7)
    if 6<=j<10 and t<1.18:continue
    a=j*cols+k;fs.append((a,a+1,a+cols+1,a+cols));uv.append(((k/8,j/14),((k+1)/8,j/14),((k+1)/8,(j+1)/14),(k/8,(j+1)/14)))
  headmesh('HELMET | '+label+' '+str(sign),vs,fs,mat,uv,2)
# Curved lens with a proper hollow aperture behind it, rather than a dark sticker.
def visorpoint(t,w):
 z=-.023+w*.108;rx=.153-.025*w+.012*math.sin(math.pi*w);ry=.143-.012*w
 return HC+Vector((rx*math.cos(t)+.009,ry*math.sin(t),z))
vv=[];ff=[];uv=[]
for j in range(13):
 for k in range(49):vv.append(visorpoint(-1.20+2.40*k/48,j/12))
for j in range(12):
 for k in range(48):a=j*49+k;ff.append((a,a+1,a+50,a+49));uv.append(((k/48,j/12),((k+1)/48,j/12),((k+1)/48,(j+1)/12),(k/48,(j+1)/12)))
headmesh('HELMET | curved smoked visor',vv,ff,visor,uv,2,.0018)
def headtubes(name,paths,r,mat):
 m=arm.data.bones['head'].matrix_local@head.matrix.inverted()@arm.matrix_world.inverted()
 return tubes(name,[[m@Vector(p) for p in path] for path in paths],r/.0112,mat,arm.matrix_world,[[{'head':1}]*len(path) for path in paths],8)
paths=[[visorpoint(t,w)+Vector((.001,0,0)) for t in np.linspace(-1.20,1.20,97)] for w in [0,1]]
paths += [[visorpoint(t,w) for w in np.linspace(0,1,25)] for t in [-1.2,1.2]]
headtubes('HELMET | visor gasket and brow trim',paths,.0029,rubber)
headtubes('HELMET | lower shell rolled trim',[[shellpoint(*profile[1],t) for t in np.linspace(0,2*math.pi,129)]],.003,rubber)
# Hardware disks, slots, brow/chin vents, internal neck roll. These are separate 3D parts.
def disk(name,c,axis,r,depth,mat):
 c=Vector(c);axis=Vector(axis).normalized();u=axis.cross(Vector((0,0,1))).normalized();v=axis.cross(u);vv=[];ff=[]
 for d in [-depth/2,depth/2]:
  for k in range(48):vv.append(c+axis*d+r*(u*math.cos(2*math.pi*k/48)+v*math.sin(2*math.pi*k/48)))
 for k in range(48):ff.append((k,(k+1)%48,(k+1)%48+48,k+48))
 ff.extend([tuple(range(47,-1,-1)),tuple(range(48,96))]);return headmesh(name,vv,ff,mat,None,0)
for s in [-1,1]:
 c=HC+Vector((.042,s*.137,.023));axis=Vector((.22,s,0));disk('HELMET | visor pivot base '+str(s),c,axis,.020,.006,rubber);disk('HELMET | visor hinge plate '+str(s),c+axis.normalized()*.004,axis,.014,.004,metal);disk('HELMET | visor pivot screw '+str(s),c+axis.normalized()*.007,axis,.004,.002,paint)
for j in [-1,0,1]:
 # Flattened recessed vent shapes conform to chin, with raised red lips.
 path=[HC+Vector((.176,j*.033+.012*math.cos(t*2*math.pi),-.09+.0035*math.sin(t*2*math.pi))) for t in np.linspace(0,1,33)]
 headtubes('HELMET | chin vent surround '+str(j),[path],.0013,rubber)
 headmesh('HELMET | recessed chin vent '+str(j),[HC+Vector((.1755,j*.033,-.09))]+path,[(0,k,k+1) for k in range(1,len(path))],rubber,None,0)
for s in [-1,1]:
 paths=[]
 for z in [.098,.108]:paths.append([HC+Vector((.116-.018*t,s*(.045+.01*t),z+.01*t)) for t in np.linspace(0,1,15)])
 headtubes('HELMET | crown intake '+str(s),paths,.003,paintred)
headtubes('HELMET | padded neck roll',[[HC+Vector((.085*math.cos(t),.091*math.sin(t),-.148)) for t in np.linspace(0,2*math.pi,97)]],.011,rubber)
# Preserve source action and record the fitted pose as a distinct editable action.
if arm.animation_data and arm.animation_data.action:
 arm.animation_data.action.use_fake_user=True;arm.animation_data.action=arm.animation_data.action.copy();arm.animation_data.action.name='Racer V4 | recline and steering grip'
# Curl the existing fingers around the unchanged rim, using their real bone lengths.
def aim_world(n,target):
 b=arm.pose.bones[n];h=arm.matrix_world@b.head;t=arm.matrix_world@b.tail;q=(t-h).normalized().rotation_difference((Vector(target)-h).normalized());m=arm.matrix_world@b.matrix;b.matrix=arm.matrix_world.inverted()@(Matrix.Translation(h)@q.to_matrix().to_4x4()@Matrix.Translation(-h)@m);bpy.context.view_layer.update()
for s,sign in [('l',1),('r',-1)]:
 for finger in ['index','middle','ring','pinky']:
  n=finger+'_01_'+s;b=arm.pose.bones[n];h=arm.matrix_world@b.head;z=h.z;rim=sign*math.sqrt(max(.001,.225**2-(z-.70)**2))
  aim_world(n,(.616,rim+sign*.003,z-.001));aim_world(finger+'_02_'+s,(.638,rim-sign*.016,z-.002));aim_world(finger+'_03_'+s,(.613,rim-sign*.023,z-.004))
 for n in [b.name for b in arm.pose.bones if any(b.name.startswith(f) for f in ['index','middle','ring','pinky'])]:
  b=arm.pose.bones[n];b.keyframe_insert('rotation_quaternion',frame=1) if b.rotation_mode=='QUATERNION' else b.keyframe_insert('rotation_euler',frame=1)
# Smooth the existing human without changing source vertices/weights.
smooth(body);m=body.modifiers.new('Non-destructive human surface smoothing','SUBSURF');m.levels=1;m.render_levels=2
scene.frame_set(1);bpy.context.view_layer.update()
assert sig()==BEFORE,'Protected geometry, lighting, rest rig or weights changed'
scene['Racer v4 | limitations']='Tailored CC0 work-suit is a procedural adaptation, not a manually sculpted production race garment. Full backrest contact and pre-existing foot/chassis fit remain imperfect. Inspect validation and actual renders.'
scene['Racer v4 | source license']='Local MakeHuman male_worksuit01: CC0, MakeHuman Team; gloves derive from existing MakeHuman hands; boots from existing shoes05; helmet authored in this script.'
scene.camera=bpy.data.objects['Refinement | three quarter'];scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Racer_v4.blend'))
(OUT/'preservation.json').write_text(json.dumps({'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'protected_signatures':BEFORE,'preserved':sig()==BEFORE,'local_garment_license':lic,'new_meshes':[o.name for o in made]},indent=2))
scene.render.filepath=str(OUT/'preview_three_quarter.png');bpy.ops.render.render(write_still=True)
print('RACER_BUILD_DONE',flush=True)

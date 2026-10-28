"""Blender 5.2: original lathed tire, portable PBR maps, editable modules.
Run from the project root: blender -b --python Art/Trackside/TireBarriers/generate.py
"""
import bpy, math, json, random, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent; R=P.parents[2]; E=R/'Evidence/TireBarriers'
for p in [P/'Exports',P/'Textures',E]:p.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'SM_Tire_Black.blend'))
inspection=[{'name':o.name,'type':o.type,'dimensions':list(o.dimensions),'vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in bpy.context.scene.objects]
(E/'source_inspection.json').write_text(json.dumps({'source_sha256':hashlib.sha256((R/'SM_Tire_Black.blend').read_bytes()).hexdigest(),'objects':inspection},indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
rng=random.Random(281026)
def collection(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c
prototypes=collection('01_Tire_Prototypes'); modules=collection('02_Editable_Modules');stage=collection('03_Inspection_Studio')
def move(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o)
# Profile follows the complete rubber section: tread, shoulder, sidewall,
# bead, inner liner and opposite bead. It is not a torus or capped cylinder.
profile=[]
for z in np.linspace(-.060,.060,31):
 r=.275-.0006*(z/.060)**2
 for groove in [-.036,0,.036]:r-=.0018*math.exp(-((z-groove)/.0027)**2)
 profile.append((r,float(z)))
profile += [(.272,.069),(.266,.078)]
for r in np.linspace(.258,.174,15):
 z=.087+.005*math.sin((r-.174)/.084*math.pi)
 z+=.0007*math.exp(-((r-.245)/.0025)**2)+.0006*math.exp(-((r-.184)/.0025)**2)
 profile.append((float(r),z))
profile += [(.168,.081),(.164,.073),(.163,.062),(.170,.057),(.187,.064),(.221,.070),(.245,.062),(.252,.049),(.253,0),(.252,-.049),(.245,-.062),(.221,-.070),(.187,-.064),(.170,-.057),(.163,-.062),(.164,-.073),(.168,-.081)]
profile += [(r,-z) for r,z in reversed(profile[33:48])]
profile += [(.266,-.078),(.272,-.069)]
lengths=[0.0]
for i in range(len(profile)):lengths.append(lengths[-1]+math.dist(profile[i],profile[(i+1)%len(profile)]))
vcoord=np.array(lengths)/lengths[-1];N=80;J=len(profile)
verts=[(r*math.cos(math.tau*i/N),r*math.sin(math.tau*i/N),z+.093) for i in range(N) for r,z in profile]
faces=[];uv=[]
for i in range(N):
 for j in range(J):
  faces.append((i*J+j,((i+1)%N)*J+j,((i+1)%N)*J+(j+1)%J,i*J+(j+1)%J))
  uv.append([(i/N,vcoord[j]),((i+1)/N,vcoord[j]),((i+1)/N,vcoord[j+1]),(i/N,vcoord[j+1])])
me=bpy.data.meshes.new('Tire_Hollow_Profile');me.from_pydata(verts,[],faces);me.update();layer=me.uv_layers.new(name='TireUV')
for p,coords in zip(me.polygons,uv):
 p.use_smooth=True
 for li,coord in zip(p.loop_indices,coords):layer.data[li].uv=coord
# Recalculate outward normals on the closed tube section.
import bmesh
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
# Generate seamless UV-space PBR maps. These portable maps do not rely on FBX
# carrying Blender Noise/Bump nodes into Unreal.
size=1024;u,v=np.meshgrid(np.arange(size)/size,np.arange(size)/size)
def field(seed):
 rr=np.random.default_rng(seed);a=np.zeros((size,size))
 for frequency,amplitude in [(2,.48),(5,.25),(13,.16),(37,.08),(107,.03)]:
  for k in range(3):
   x,y=rr.integers(1,frequency+1,2);a+=amplitude/3*np.sin(math.tau*(x*u+y*v)+rr.uniform(0,math.tau))
 return a
coarse=field(286);grain=np.random.default_rng(85).normal(0,1,(size,size));wear=field(733)
def save_image(name,array,color=False):
 if array.ndim==2:array=np.repeat(array[:,:,None],3,axis=2)
 rgba=np.concatenate([np.clip(array,0,1),np.ones((size,size,1))],axis=2).astype(np.float32)
 im=bpy.data.images.new(name,width=size,height=size,alpha=True);im.colorspace_settings.name='sRGB' if color else 'Non-Color';im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(P/'Textures'/(name+'.png'));im.file_format='PNG';im.save();return im
dirt=np.clip((coarse+.15)*.25,0,.16)
black=np.stack([.033+dirt*.52,.036+dirt*.44,.038+dirt*.32],axis=2)*(1+grain[:,:,None]*.055)
paint=np.clip((wear-.04)*7,0,1)[:,:,None]
red=np.array([.38,.033,.022])*(.83+coarse[:,:,None]*.18)+dirt[:,:,None]*np.array([.3,.19,.10])
red=red*(1-paint*.88)+black*paint*.88
images={}
for name,color in [('Black',black),('Red',red)]:
 images[name+'Color']=save_image('T_Tire_'+name+'_BaseColor',color,True)
 images[name+'Roughness']=save_image('T_Tire_'+name+'_Roughness',np.clip(.85+coarse*.10+grain*.009,.76,.94))
height=coarse*.1+grain*.018;dx=(np.roll(height,-1,1)-np.roll(height,1,1))*.5;dy=(np.roll(height,-1,0)-np.roll(height,1,0))*.5
norm=np.stack([-dx*.7,-dy*.7,np.ones_like(dx)],axis=2);norm/=np.linalg.norm(norm,axis=2)[:,:,None]
images['NormalGL']=save_image('T_Tire_NormalGL',norm*.5+.5);norm[:,:,1]*=-1;images['NormalDX']=save_image('T_Tire_NormalDX',norm*.5+.5)
def material(variant):
 m=bpy.data.materials.new('M_Tire_'+variant);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 out=n.new('ShaderNodeOutputMaterial');out.location=(700,0);bs=n.new('ShaderNodeBsdfPrincipled');bs.location=(430,0);bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.85;l.new(bs.outputs['BSDF'],out.inputs['Surface'])
 for suffix,input in [('Color','Base Color'),('Roughness','Roughness')]:
  t=n.new('ShaderNodeTexImage');t.image=images[variant+suffix];t.label='Portable '+suffix;t.location=(-550,250 if suffix=='Color' else 0)
  if suffix=='Color':
   info=n.new('ShaderNodeObjectInfo');info.location=(-800,550);scale=n.new('ShaderNodeMath');scale.operation='MULTIPLY_ADD';scale.inputs[1].default_value=.20;scale.inputs[2].default_value=.90;l.new(info.outputs['Random'],scale.inputs[0])
   tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.location=(100,250);l.new(t.outputs['Color'],tint.inputs[1]);l.new(scale.outputs[0],tint.inputs[2]);l.new(tint.outputs[0],bs.inputs[input])
  else:l.new(t.outputs['Color'],bs.inputs[input])
 coord=n.new('ShaderNodeTexCoord');coord.location=(-800,-400);noise=n.new('ShaderNodeTexNoise');noise.location=(-550,-400);noise.inputs['Scale'].default_value=270;noise.inputs['Detail'].default_value=2;l.new(coord.outputs['Object'],noise.inputs['Vector'])
 bump=n.new('ShaderNodeBump');bump.location=(180,-220);bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.00035;l.new(noise.outputs['Fac'],bump.inputs['Height'])
 t=n.new('ShaderNodeTexImage');t.image=images['NormalGL'];t.location=(-550,-650);nm=n.new('ShaderNodeNormalMap');nm.location=(-150,-520);l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],bump.inputs['Normal']);l.new(bump.outputs['Normal'],bs.inputs['Normal']);return m
mats={name:material(name) for name in ['Black','Red']};assets=[]
def tire(name,variant,c):
 mesh=me.copy();mesh.materials.append(mats[variant]);o=bpy.data.objects.new(name,mesh);c.objects.link(o);return o
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.fbx(filepath=str(P/'Exports'/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,mesh_smooth_type='FACE')
 assets.append({'name':name,'tires':len(objects),'triangles':len(objects)*len(faces)*2})
for variant in ['Black','Red']:
 o=tire('SM_TB_Tire_'+variant,variant,prototypes);export(o.name,[o]);o.hide_render=True;o.hide_set(True)
for variant,row in [('Black',0),('Alternating',1),('Mixed',2)]:
 c=collection('Module_'+variant);root=bpy.data.objects.new('Pivot_'+variant,None);c.objects.link(root);objs=[]
 for col in range(4):
  for level in range(3):
   color='Black' if variant=='Black' else ('Red' if (col%2==0 if variant=='Alternating' else rng.random()<.40) else 'Black')
   o=tire('Tire_'+variant+'_'+str(col)+'_'+str(level),color,c);o.parent=root
   o.location=((col-1.5)*.547+(rng.uniform(-.001,.001) if level else 0),rng.uniform(-.002,.002),level*.184)
   o.rotation_euler.z=rng.uniform(-math.pi,math.pi);o['paint_variation']=rng.uniform(.88,1.08);objs.append(o)
 export('SM_TB_Module_'+variant,objs);root.location=(0,row*1.3,0)
 # Neutral, deterministic object display colours; materials are portable maps.
 for o in objs:o.color=(1,1,1,1)
# Studio plane and lighting, excluded from FBX exports.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005));floor=bpy.context.object;floor.name='Studio_Ground';move(floor,stage)
fm=bpy.data.materials.new('Studio_Concrete');fm.diffuse_color=(.15,.14,.12,1);floor.data.materials.append(fm)
for loc,power,area in [((2,-3,5),850,4),((-3,1,3),1000,3),((1,5,4),1200,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=area;o.rotation_euler=(Vector((0,1,.2))-o.location).to_track_quat('-Z','Y').to_euler();move(o,stage)
s.world=bpy.data.worlds.new('Soft_Studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.30,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
bpy.ops.object.camera_add(location=(3.4,-4.3,2.9));cam=bpy.context.object;move(cam,stage);s.camera=cam;cam.data.lens=55
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100
cam.rotation_euler=(Vector((0,1,.23))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(E/'barrier_modules.png')
manifest={'outer_diameter_m':.55,'section_width_m':.184,'bead_inner_diameter_m':.326,'module_length_m':2.191,'module_height_m':.554,'individual_tire_triangles':len(faces)*2,'radial_segments':N,'profile_points':J,'assets':assets,'seed':281026,'source_inspection':inspection,'portable_maps':'Generated seamless 1024px base color, roughness and tangent normal maps; supplemental Blender micro Noise->Bump detail','axis':'FBX forward -Y / up Z; meters converted by importer to cm; origin bottom centre','limitations':'No brand logos, cords or tire deformation. Reused passenger-car tire dimensions, not racing kart wheel dimensions.'}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2))
for image in images.values():image.pack();image.filepath='//Textures/'+image.name+'.png'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'TireBarriers.blend'));bpy.ops.render.render(write_still=True)
# A separate close view reveals tread, hollow centre and molded sidewall.
for c in s.collection.children:
 if c.name.startswith('Module_'):c.hide_render=True
o=bpy.data.objects['SM_TB_Tire_Black'];o.hide_render=False;o.hide_set(False)
cam.location=(.60,-.67,.60);cam.rotation_euler=(Vector((0,0,.09))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60;s.render.filepath=str(E/'tire_closeup.png');bpy.ops.render.render(write_still=True)
print('TIRE_BARRIERS_GENERATED',json.dumps(manifest['assets']),flush=True)

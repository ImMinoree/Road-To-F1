"""Original modular kart start display; source circuit assets remain untouched."""
import bpy,math,json,wave,struct
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/RaceStart';(OUT/'Meshes').mkdir(parents=True,exist_ok=True);(OUT/'Textures').mkdir(exist_ok=True);(OUT/'Audio').mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);parts=[]
def mat(name,color,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.38;p.inputs['Metallic'].default_value=metal;return m
black=mat('Charcoal',(.012,.018,.024));metal=mat('Hardware',(.17,.19,.21),.7);lensmat=mat('Lens',(.045,.001,.001))
def cube(p,size,m,bevel=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(p[0],-p[1],p[2]));o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel:
  b=o.modifiers.new('Manufactured edge radii','BEVEL');b.width=bevel;b.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 parts.append(o);return o
def finish(name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 slots=[m.name for m in o.data.materials];bpy.ops.export_scene.fbx(filepath=str(OUT/'Meshes'/(name+'.fbx')),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',bake_anim=False);parts.clear();return {'mesh':name,'slots':slots}
items=[]
cube((.025,0,0),(.36,.75,.80),black,.045);cube((-.166,0,0),(.028,.65,.69),metal,.015);cube((-.187,0,0),(.025,.62,.66),black,.02)
# Cylindrical bezel and a modest rain/sun visor.
bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,location=(-.211,0,0),rotation=(0,math.pi/2,0),major_radius=.25,minor_radius=.019);o=bpy.context.object;o.data.materials.append(metal);parts.append(o)
cube((-.245,0,.365),(.30,.76,.045),black,.012)
for yy in [-.285,.285]:
 for zz in [-.29,.29]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.017,depth=.012,location=(-.217,-yy,zz),rotation=(0,math.pi/2,0));o=bpy.context.object;o.data.materials.append(metal);parts.append(o)
items.append(finish('SM_RS_Housing'))
cube((.12,0,.56),(.14,5.1,.12),metal,.018)
for yy in [-2.25,0,2.25]:cube((.12,yy,.71),(.13,.12,.28),metal,.015)
items.append(finish('SM_RS_MountFrame'))
v=[(-.239,0,0)];uv=[(.5,.5)]
for i in range(64):
 a=i*math.tau/64;y=.232*math.cos(a);z=.232*math.sin(a);v.append((-.221,-y,z));uv.append((.5+y/.464,.5+z/.464))
f=[(0,i+1,(i+1)%64+1) for i in range(64)];mesh=bpy.data.meshes.new('Convex lens');mesh.from_pydata(v,[],f);mesh.update();o=bpy.data.objects.new('Lens',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(lensmat)
layer=mesh.uv_layers.new(name='LED_UV')
for poly in mesh.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:layer.data[li].uv=uv[mesh.loops[li].vertex_index]
parts.append(o);items.append(finish('SM_RS_RedLens'))
N=512;yy,xx=np.mgrid[:N,:N];u=xx/N;w=yy/N;dist=np.sqrt(((u*28)%1-.5)**2+((w*28)%1-.5)**2);mask=np.clip((.36-dist)*18,0,1)*.94+.06
pixels=np.ones((N,N,4),dtype=np.float32);pixels[:,:,:3]=mask[:,:,None];im=bpy.data.images.new('T_RS_LEDMask',width=N,height=N,alpha=True);im.pixels.foreach_set(pixels.ravel());im.filepath_raw=str(OUT/'Textures/T_RS_LEDMask.png');im.file_format='PNG';im.save()
for name,seconds,freq in [('RS_Countdown',.10,880),('RS_LightsOut',.18,660)]:
 rate=24000;data=[]
 for i in range(int(rate*seconds)):
  t=i/rate;f=freq if name=='RS_Countdown' or t<.085 else 990;env=min(1,t/.008,(seconds-t)/.025);sample=.35*max(0,env)*math.sin(2*math.pi*f*t);data.append(struct.pack('<h',int(sample*32767)))
 with wave.open(str(OUT/'Audio'/(name+'.wav')),'wb') as wav:wav.setparams((1,2,rate,0,'NONE','not compressed'));wav.writeframes(b''.join(data))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'RaceStartGantry.blend'))
(OUT/'manifest.json').write_text(json.dumps({'assets':items,'sources':'Original Blender modeling, generated LED mask and original synthesized beep waveforms; no third-party downloads','module_width_m':.75,'module_spacing_m':.95,'lens_diameter_m':.464,'mount_height_cm':560,'all_geometry_collision':'None; existing gantry supports retained'},indent=2));print('RACE_START_ASSETS_READY',flush=True)

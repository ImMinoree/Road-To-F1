"""Dedicated FP art from V5. Does not save/change V5 or any third-person asset."""
import bpy,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent;ROOT=P.parents[2];SOURCE=ROOT/'Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend'
sourcehash=hashlib.sha256(SOURCE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;arm=bpy.data.objects['Game_engine'];deps=bpy.context.evaluated_depsgraph_get();scene.frame_set(25)
poses={}
for frame in range(1,50):
 scene.frame_set(frame);bpy.context.view_layer.update();poses[frame]={b.name:b.matrix.copy() for b in arm.pose.bones}
scene.frame_set(25);bpy.context.view_layer.update()
col=bpy.data.collections.new('FIRST PERSON | separate local cockpit asset');scene.collection.children.link(col)
# New rest pose already grips the wheel. This avoids DQ-vs-linear skinning changes at the hands.
data=bpy.data.armatures.new('FP_KartArms_Skeleton');rig=bpy.data.objects.new('FP_KartArms_Rig',data);col.objects.link(rig);rig.matrix_world=arm.matrix_world.copy();bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for b in arm.data.bones:
 e=data.edit_bones.new(b.name);e.head=(0,0,0);e.tail=(0,b.length,0);e.matrix=poses[25][b.name];e.length=b.length;e.use_deform=b.use_deform
for b in arm.data.bones:
 if b.parent:data.edit_bones[b.name].parent=data.edit_bones[b.parent.name]
bpy.ops.object.mode_set(mode='OBJECT')
def material(name,color,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Specular IOR Level'].default_value=.3;return m
materials={
 'leather':material('M_FP_Leather',(.012,.014,.019),.5),
 'red':material('M_FP_RedSuede',(.22,.004,.009),.65),
 'white':material('M_FP_WhiteFabric',(.55,.57,.58),.72),
 'fabric':material('M_FP_BlackFabric',(.006,.008,.012),.78),
 'rubber':material('M_FP_Rubber',(.008,.009,.011),.72),
 'thread':material('M_FP_Stitch',(.27,.28,.27),.78),
 'metal':material('M_FP_Metal',(.2,.21,.23),.29,.8)}
# Explicit normal/roughness texture tiles, packed and exported for the Unreal materials.
T=P/'Textures';T.mkdir(exist_ok=True);N=1024;y,x=np.mgrid[:N,:N];rng=np.random.default_rng(71)
height=.5+.08*np.sin(x*2*math.pi/16)*np.cos(y*2*math.pi/16)+rng.normal(0,.018,(N,N));dy,dx=np.gradient(height);n=np.stack((-dx*1.6,-dy*1.6,np.ones_like(dx)),axis=-1);n/=np.linalg.norm(n,axis=-1)[...,None]
def image(name,a):
 if a.ndim==2:a=np.repeat(a[...,None],3,axis=-1)
 rgba=np.concatenate((a,np.ones((N,N,1))),axis=-1).astype('float32');im=bpy.data.images.new(name,width=N,height=N);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(T/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
normal=image('T_FP_Microfiber_N',n*.5+.5);rough=image('T_FP_Microfiber_R',np.clip(.58+.08*(height-.5),0,1))
for key,m in materials.items():
 if key in ['metal','thread']:continue
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');tc=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=5;nt.links.new(tc.outputs['UV'],scale.inputs[0]);tx=nt.nodes.new('ShaderNodeTexImage');tx.image=normal;nt.links.new(scale.outputs[0],tx.inputs['Vector']);nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.17;nt.links.new(tx.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],p.inputs['Normal'])
def choose(mat):
 name=mat.name.lower()
 if 'red' in name or 'crimson' in name:return materials['red']
 if 'white' in name:return materials['white']
 if 'thread' in name:return materials['thread']
 if 'rubber' in name or 'elastic' in name:return materials['rubber']
 if 'leather' in name:return materials['leather']
 return materials['fabric']
parts=[]
names=['RACER | anatomical five-finger gloves','RACER | tailored long anatomical sleeves','RACER | raised glove knuckle panels','RACER | l knitted gauntlet cuff','RACER | r knitted gauntlet cuff']
for name in names:
 source=bpy.data.objects.get(name)
 if source is None:continue
 for mod in source.modifiers:
  if mod.type=='SUBSURF':mod.levels=mod.render_levels
 bpy.context.view_layer.update();ev=source.evaluated_get(deps);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps);me.transform(source.matrix_world);o=bpy.data.objects.new('FP | '+name.split('|')[-1].strip(),me);col.objects.link(o)
 for g in source.vertex_groups:
  if o.vertex_groups.get(g.name) is None:o.vertex_groups.new(name=g.name)
 old=list(me.materials);me.materials.clear()
 for m in old:me.materials.append(choose(m))
 mod=o.modifiers.new('FP separate grip-bind skeleton','ARMATURE');mod.object=rig;parts.append(o)
gloves=parts[0]
# Real padded dorsal panels follow the anatomical surface, with inherited skin weights.
def subset(name,polys,mat,offset):
 ids=sorted({i for p in polys for i in p.vertices});mp={i:j for j,i in enumerate(ids)};me=bpy.data.meshes.new(name);me.from_pydata([gloves.data.vertices[i].co+gloves.data.vertices[i].normal*offset for i in ids],[],[tuple(mp[i] for i in p.vertices) for p in polys]);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(mat)
 for g in gloves.vertex_groups:o.vertex_groups.new(name=g.name)
 for j,i in enumerate(ids):
  for g in gloves.data.vertices[i].groups:o.vertex_groups[g.group].add([j],g.weight,'REPLACE')
 uv=me.uv_layers.new(name='UV_FP_Pads')
 for p in me.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*8,v.z*8)
 m=o.modifiers.new('FP skin','ARMATURE');m.object=rig
 parts.append(o);return o
for s,sign in [('l',1),('r',-1)]:
 polys=[]
 for p in gloves.data.polygons:
  c=p.center;w=sum(g.weight for i in p.vertices for g in gloves.data.vertices[i].groups if gloves.vertex_groups[g.group].name in ['hand_'+s,'index_01_'+s,'middle_01_'+s,'ring_01_'+s,'pinky_01_'+s])/len(p.vertices)
  if c.y*sign>0 and p.normal.y*sign>.4 and .52<c.x<.61 and .65<c.z<.76 and w>.65:polys.append(p)
 if polys:subset('FP | '+s+' shaped suede knuckle reinforcement',polys,materials['red'],.00075)
# Raised panel-edge stitching is mesh geometry, not painted lines.
stitchverts=[];stitchfaces=[];stitchweights=[]
for o in list(parts):
 if 'reinforcement' not in o.name:continue
 edges={}
 for p in o.data.polygons:
  for a,b in p.edge_keys:edges[tuple(sorted((a,b)))]=edges.get(tuple(sorted((a,b))),0)+1
 for (a,b),count in edges.items():
  if count!=1:continue
  A=o.data.vertices[a].co;B=o.data.vertices[b].co
  if (B-A).length<.0005:continue
  # Dense boundary segments read as a stitched welt at cockpit distance.
  d=(B-A).normalized();n=o.data.vertices[a].normal;side=d.cross(n).normalized()*.00022;base=len(stitchverts)
  stitchverts.extend([A+side+n*.00035,B+side+n*.00035,B-side+n*.00035,A-side+n*.00035]);stitchfaces.append(tuple(base+i for i in range(4)))
  ws=[(o.vertex_groups[g.group].name,g.weight) for g in o.data.vertices[a].groups];stitchweights.extend([ws]*4)
if stitchfaces:
 me=bpy.data.meshes.new('FP actual seam geometry');me.from_pydata(stitchverts,[],stitchfaces);me.update();o=bpy.data.objects.new('FP | glove sewn edging',me);col.objects.link(o);me.materials.append(materials['thread'])
 for i,ws in enumerate(stitchweights):
  for name,w in ws:g=o.vertex_groups.get(name) or o.vertex_groups.new(name=name);g.add([i],w,'REPLACE')
 m=o.modifiers.new('FP skin','ARMATURE');m.object=rig;parts.append(o)
# Combine dedicated arms into a single skeletal mesh, retaining finger weights and UVs.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=gloves;bpy.ops.object.join();fp=gloves;fp.name='SK_FP_KartArms'
for p in fp.data.polygons:p.use_smooth=True
# Bake the evaluated V5 motion into the new grip bind, without external IK/driver dependencies.
for frame in range(1,50):
 scene.frame_set(frame)
 for b in rig.pose.bones:
  b.matrix=poses[frame][b.name];bpy.context.view_layer.update()
 for b in rig.pose.bones:
  b.rotation_mode='QUATERNION';b.keyframe_insert('location',frame=frame);b.keyframe_insert('rotation_quaternion',frame=frame);b.keyframe_insert('scale',frame=frame)
rig.animation_data.action.name='A_FP_KartSteering'
scene.frame_set(25);bpy.context.view_layer.update()
# Owner-only cockpit wheel, centered pivot, same measured rim used by the arm animation.
wv=[];wf=[];wmats=[];wheelM=[materials['rubber'],materials['metal']]
for source in list(scene.objects):
 if source.type!='MESH' or not source.name.startswith('SK_Kart_Steering_Column_And_Wheel_'):continue
 ev=source.evaluated_get(deps);me=ev.to_mesh();allowed=None
 if 'Frame_Brushed' in source.name:
  hook=next((m for m in source.modifiers if m.type=='HOOK'),None);allowed=set(hook.vertex_indices) if hook else set()
 ids=set(i for p in me.polygons if allowed is None or all(i in allowed for i in p.vertices) for i in p.vertices);mapping={i:len(wv)+j for j,i in enumerate(sorted(ids))}
 for i in sorted(ids):wv.append(source.matrix_world@me.vertices[i].co-Vector((.62,0,.70)))
 for p in me.polygons:
  if all(i in ids for i in p.vertices):wf.append(tuple(mapping[i] for i in p.vertices));wmats.append(0 if 'Rubber' in source.name else 1)
 ev.to_mesh_clear()
me=bpy.data.meshes.new('FP wheel original isolated components');me.from_pydata(wv,[],wf);me.update();wheel=bpy.data.objects.new('SM_FP_SteeringWheel',me);col.objects.link(wheel);wheel.location=(.62,0,.70)
for m in wheelM:me.materials.append(m)
for p,i in zip(me.polygons,wmats):p.material_index=i;p.use_smooth=True
# Remove source objects only from this new in-memory copy. V5 on disk is untouched.
keep={fp,rig,wheel}
for o in list(scene.objects):
 if o not in keep and o.type not in ['LIGHT','CAMERA'] and o.name!='Studio Ground (render only)':bpy.data.objects.remove(o,do_unlink=True)
for o in list(scene.objects):
 if o.type=='CAMERA':bpy.data.objects.remove(o,do_unlink=True)
data=bpy.data.cameras.new('FP cockpit review');cam=bpy.data.objects.new('FP cockpit review',data);scene.collection.objects.link(cam);cam.location=(-.15,0,1.05);cam.rotation_euler=Vector((1,0,0)).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.angle=math.radians(85);scene.camera=cam
scene.frame_start=1;scene.frame_end=49;scene.render.fps=24;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene['FP scope']='Separate V5-derived first-person art placeholder, glove reinforcement and microfiber detail added. Source full-body V5 unchanged. Not a photorealistic finished glove asset.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'FP_KartArms.blend'))
E=P/'Exports';E.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT');fp.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(E/'SK_FP_KartArms.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
bpy.ops.object.select_all(action='DESELECT');wheel.select_set(True);bpy.context.view_layer.objects.active=wheel;wheel.location=(0,0,0)
bpy.ops.export_scene.fbx(filepath=str(E/'SM_FP_SteeringWheel.fbx'),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='COPY',embed_textures=True)
wheel.location=(.62,0,.70)
(P/'manifest.json').write_text(json.dumps({'source':str(SOURCE),'source_sha256':sourcehash,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==sourcehash,'vertices':len(fp.data.vertices),'triangles':sum(len(p.vertices)-2 for p in fp.data.polygons),'bones':len(rig.data.bones),'materials':[m.name for m in fp.data.materials],'steering_frames':[1,25,49],'steering_degrees':[-25,0,25],'wheel_center_cm':[62,0,70],'wheel_radius_cm':18.4,'source_camera_anchor_cm':[-15,0,105],'blender_to_unreal_expected':'X preserved, Y mirrored, Z preserved; verify import bounds/bone samples before runtime alignment.','quality':'V5-derived FP placeholder with separate padded glove panels and geometric sewn edges; manual glove/forearm art polish still required.'},indent=2))
for name,frame in [('center',25),('left',1),('right',49)]:
 scene.frame_set(frame);wheel.rotation_euler.x=math.radians((frame-25)/24*25);scene.render.filepath=str(P/('fp_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('FP_EXPORT_COMPLETE',len(fp.data.vertices),flush=True)

"""Incremental editable local cockpit art. No source scene or gameplay edits."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;ROOT=P.parents[2];E=P/'Exports';E.mkdir(exist_ok=True);TEX=P/'Textures';T=Matrix.Rotation(math.radians(18),4,'Y');C=Vector((.62,0,.67));source=P.parent/'Wheel_Visibility_v3/Kart_Cockpit_Wheel_Visibility_v3.blend';hash0=hashlib.sha256(source.read_bytes()).hexdigest()
# Recover original material categories, in the exact source join order. Geometry stays intact.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend'));bpy.context.scene.frame_set(25);deps=bpy.context.evaluated_depsgraph_get();categories=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or not ob.name.startswith('SK_Kart_') or ob.name.startswith('SK_Kart_Steering_Column_And_Wheel_'):continue
 ev=ob.evaluated_get(deps);me=ev.to_mesh();categories.append((ob.name,len({v for f in me.polygons for v in f.vertices})));ev.to_mesh_clear()
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(25);rig=bpy.data.objects['FP_KartArms_Rig'];arms=bpy.data.objects['SK_WV3_DriverPOV'];wheel=bpy.data.objects['SM_CV2_SteeringWheel'];kart=bpy.data.objects['SM_WV3_PlayerChassis'];newmats={}
def image(name):
 im=bpy.data.images.load(str(TEX/name),check_existing=True);return im
def mat(name,color,rough=.5,metal=0,tile=None):
 m=bpy.data.materials.new('M_CT4_'+name);m.use_nodes=True;m.diffuse_color=(*color,1);nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 data={'color':[*color,1],'roughness':rough,'metallic':metal,'tile':tile};newmats[m.name]=data
 if tile:
  uv=nt.nodes.new('ShaderNodeTexCoord');sc=nt.nodes.new('ShaderNodeVectorMath');sc.operation='SCALE';sc.inputs['Scale'].default_value=tile;nt.links.new(uv.outputs['UV'],sc.inputs[0])
  for suffix,prop in [('C','Base Color'),('R','Roughness'),('N','Normal')]:
   tx=nt.nodes.new('ShaderNodeTexImage');tx.image=image('T_CT4_Weave_'+suffix+'.png');nt.links.new(sc.outputs[0],tx.inputs['Vector'])
   if suffix=='C':
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=(*color,1);nt.links.new(tx.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],p.inputs[prop])
   elif suffix=='N':
    tx.image.colorspace_settings.name='Non-Color';n=nt.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.45;nt.links.new(tx.outputs[0],n.inputs['Color']);nt.links.new(n.outputs[0],p.inputs['Normal'])
   else:tx.image.colorspace_settings.name='Non-Color';nt.links.new(tx.outputs[0],p.inputs[prop])
 return m
red=mat('RedKnit',(.48,.012,.022),.76,0,12);fabric=mat('GraphiteNomex',(.028,.030,.033),.82,0,16);leg=mat('LegNomex',(.017,.019,.022),.82,0,14);blue=mat('BlueSuede',(.018,.025,.11),.84,0,11);palm=mat('PalmSuede',(.015,.018,.019),.85,0,14);thread=mat('IvoryStitch',(.64,.65,.59),.83);trim=mat('BlackPolymer',(.007,.009,.010),.44);metal=mat('SatinAlloy',(.35,.39,.41),.29,.92);steel=mat('DarkSteel',(.065,.073,.082),.31,.9);lcd=mat('LCD',(.3,.4,.3),.42);ink=mat('LCDInk',(.008,.022,.01),.8)
for i,m in enumerate(arms.data.materials):arms.data.materials[i]=red if 'RedTextile' in m.name else leg if 'LegFabric' in m.name else palm if 'Palm' in m.name else thread if 'Thread' in m.name else fabric
# Existing anatomy, weights and actions remain; subdivide existing garment topology, then sculpt small cloth folds.
bpy.ops.object.select_all(action='DESELECT');arms.select_set(True);bpy.context.view_layer.objects.active=arms
sub=arms.modifiers.new('POV surface refinement','SUBSURF');sub.levels=1;sub.render_levels=1;bpy.ops.object.modifier_move_up(modifier=sub.name);bpy.ops.object.modifier_apply(modifier=sub.name)
cached_normals=[v.normal.copy() for v in arms.data.vertices]
for v in arms.data.vertices:
 hand=sum(g.weight for g in v.groups if arms.vertex_groups[g.group].name.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')))
 if hand>.1:continue
 fore=sum(g.weight for g in v.groups if arms.vertex_groups[g.group].name.startswith(('lowerarm_','upperarm_')))
 if fore<.5:continue
 co=v.co;envelope=.0015*fore;fold=math.sin(co.x*210+math.sin(co.y*55))*math.exp(-((co.x-.30)/.19)**2);v.co+=cached_normals[v.index]*envelope*fold
arms.data.update()
# Raised glove piping and double top stitches projected onto the actual source glove surface.
ids={v.index for v in arms.data.vertices if sum(g.weight for g in v.groups if arms.vertex_groups[g.group].name.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_','lowerarm_')))>.5};faces=[tuple(p.vertices) for p in arms.data.polygons if all(i in ids for i in p.vertices)];tree=BVHTree.FromPolygons([v.co for v in arms.data.vertices],faces);detail=[]
def tube(name,points,radius,material,weights=None):
 vs=[];fs=[];N=6
 for i,p in enumerate(points):
  d=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized();u=d.cross(Vector((0,0,1))).normalized()
  if u.length<.1:u=Vector((1,0,0))
  v=d.cross(u).normalized()
  for j in range(N):vs.append(p+radius*(u*math.cos(j*2*math.pi/N)+v*math.sin(j*2*math.pi/N)))
 for i in range(len(points)-1):
  for j in range(N):fs.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob)
 for p in me.polygons:p.use_smooth=True
 if weights:
  for i,ws in enumerate(weights):
   for n,w in ws:
    g=ob.vertex_groups.get(n) or ob.vertex_groups.new(name=n);g.add(list(range(i*N,(i+1)*N)),w,'REPLACE')
  a=ob.modifiers.new('Original rig weights','ARMATURE');a.object=rig
 detail.append(ob);return ob
for side,sign in [('l',1),('r',-1)]:
 W=rig.data.bones['hand_'+side].head_local;D=rig.data.bones['hand_'+side].matrix_local.to_3x3().col[1].normalized();B=Vector((0,sign,0));pts=[];ws=[]
 for i in range(97):
  a=i*2*math.pi/96;p=W+D*(.012+.062*math.cos(a))+B*(.024*math.sin(a));hit=tree.ray_cast(p+Vector((0,0,.18)),Vector((0,0,-1)),.36)
  if hit[0] is None:continue
  pos,n,face,dist=hit;pts.append(pos+n*.0011);vi=min(faces[face],key=lambda j:(arms.data.vertices[j].co-pos).length);ws.append([(arms.vertex_groups[g.group].name,g.weight) for g in arms.data.vertices[vi].groups])
 if len(pts)>4:
  tube('Glove shaped raised piping '+side,pts,.0009,trim,ws)
  for i in range(0,len(pts)-2,3):tube('Glove stitch '+side,pts[i:i+2],.00032,thread,ws[i:i+2])
# Join the genuine mesh details, keeping skin weights and the existing skeleton.
bpy.ops.object.select_all(action='DESELECT');arms.select_set(True)
for ob in detail:ob.select_set(True)
bpy.context.view_layer.objects.active=arms;bpy.ops.object.join();arms.name='SK_CT4_DriverPOV'
# Preserve the closed 335mm padded rim and its hand-contact surface.
vs=[v.co.copy() for v in wheel.data.vertices[:3360]];fs=[tuple(p.vertices) for p in wheel.data.polygons if all(i<3360 for i in p.vertices)];me=bpy.data.meshes.new('Unchanged closed rim');me.from_pydata(vs,[],fs);bpy.data.objects.remove(wheel,do_unlink=True);wheel=bpy.data.objects.new('SM_CT4_SteeringWheel',me);s.collection.objects.link(wheel);me.materials.append(blue)
for p in me.polygons:p.use_smooth=True
# Rim UVs follow the grip circumference rather than disconnected smart-project islands.
uv=me.uv_layers.new(name='Grip circumference')
for p in me.polygons:
 for li in p.loop_indices:
  vi=me.loops[li].vertex_index;uv.data[li].uv=(vi//20/168,vi%20/20)
parts=[wheel]
def plate(name,outline,depth,material,x=-.004):
 v=[(x+d,y,z) for d in [-depth/2,depth/2] for y,z in outline];n=len(outline);f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);me.materials.append(material);bpy.context.view_layer.objects.active=ob;ob.select_set(True);b=ob.modifiers.new('Machined edge bevel','BEVEL');b.width=.0012;b.segments=3;bpy.ops.object.modifier_apply(modifier=b.name);ob.select_set(False);parts.append(ob);return ob
for sign in [-1,1]:plate('Stamped upper spoke',[(sign*.018,.027),(sign*.127,.038),(sign*.127,.018),(sign*.036,-.022),(sign*.015,-.038)],.005,metal)
plate('Central boss',[(.033,.031),(.039,-.013),(.022,-.040),(-.022,-.040),(-.039,-.013),(-.033,.031)],.009,metal,x=-.009)
for sign in [-1,1]:plate('Lower slotted spoke rail',[(sign*.012,-.028),(sign*.020,-.128),(sign*.010,-.133),(sign*.004,-.036)],.005,metal)
def box(name,loc,dim,material,bevel=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(material);m=ob.modifiers.new('Molded corner radii','BEVEL');m.width=bevel;m.segments=5;bpy.ops.object.modifier_apply(modifier=m.name);parts.append(ob);return ob
def cyl(name,loc,radius,depth,material,verts=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc,rotation=(0,math.pi/2,0));ob=bpy.context.object;ob.name=name;ob.data.materials.append(material)
 for p in ob.data.polygons:p.use_smooth=len(p.vertices)==4
 parts.append(ob);return ob
for a in [math.pi/2,math.pi*7/6,math.pi*11/6]:
 y,z=.023*math.cos(a),.023*math.sin(a);cyl('Recessed hub washer',(-.015,y,z),.005,.0012,steel);cyl('Socket screw',(-.016,y,z),.0036,.0018,metal,32);cyl('Hexagonal screw recess',(-.017,y,z),.0018,.0003,trim,6)
box('Logger bracket',(.008,0,.078),(.015,.09,.023),steel)
box('145mm digital logger housing',(-.012,0,.087),(.040,.145,.098),trim,.013)
box('Display recessed bezel',(-.033,0,.087),(.004,.124,.078),steel,.007)
# Screen is a genuine UV-mapped inset quad; only labels/background are baked. Speed/time use local 3D text.
screen=plate('Inset LCD face',[(-.057,.053),(.057,.053),(.057,.121),(-.057,.121)],.0005,lcd,x=-.036)
im=image('T_CT4_LCD.png');nt=lcd.node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=im;p=nt.nodes.get('Principled BSDF');nt.links.new(tx.outputs['Color'],p.inputs['Base Color']);p.inputs['Emission Strength'].default_value=.12;nt.links.new(tx.outputs['Color'],p.inputs['Emission Color']);newmats[lcd.name]['screen_texture']='T_CT4_LCD.png'
uv=screen.data.uv_layers.new(name='ScreenUV')
for p in screen.data.polygons:
 for li in p.loop_indices:
  co=screen.data.vertices[screen.data.loops[li].vertex_index].co;uv.data[li].uv=((.057-co.y)/.114,(co.z-.053)/.068)
for i in range(9):
 m=mat('LED_'+str(i),(.012,.65,.035) if i<5 else (.8,.45,.008) if i<7 else (.8,.008,.01),.35);nd=m.node_tree.nodes.get('Principled BSDF');nd.inputs['Emission Color'].default_value=m.diffuse_color;nd.inputs['Emission Strength'].default_value=.6;newmats[m.name]['emission']=.6;cyl('Shift indicator lens',(-.034,(i-4)*.009,.130),.0024,.0018,m)
for sign in [-1,1]:
 for z in [.055,.119]:cyl('Logger recessed fastener',(-.034,sign*.064,z),.0022,.0012,steel,6)
# The rim was already tilted; transform only the newly modeled components before joining.
for ob in parts[1:]:
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);ob.data.transform(T);ob.select_set(False)
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=wheel;bpy.ops.object.join();wheel.location=C
# Restore proper tire, alloy, body and frame materials to the preserved cosmetic kart.
rubber=mat('SlickRubber',(.019,.021,.023),.63,.02);frame=mat('Chromoly',(.24,.27,.28),.25,.88);body=mat('BodyGraphite',(.012,.016,.021),.39,.16);anod=mat('Anodised',(.025,.03,.036),.34,.76);tank=mat('TankPolymer',(.49,.46,.32),.55);seat=mat('BucketComposite',(.015,.017,.02),.52,.05)
offset=0;kart.data.materials.clear();km=[rubber,frame,body,anod,metal,tank,seat];[kart.data.materials.append(m) for m in km];ranges=[]
for name,count in categories:
 idx=0 if any(x in name for x in ['Tire','Rubber']) else 1 if any(x in name for x in ['Chromoly','Stainless']) else 4 if any(x in name for x in ['Aluminium','Aluminium','Aluminum']) else 2 if any(x in name for x in ['Body','Wear']) else 5 if 'Tank' in name else 6 if 'Seat' in name else 3;ranges.append((offset,offset+count,idx));offset+=count
assert offset+112==len(kart.data.vertices),(offset,len(kart.data.vertices))
idx=0
for p in kart.data.polygons:
 vi=p.vertices[0]
 while idx<len(ranges)-1 and vi>=ranges[idx][1]:idx+=1
 p.material_index=ranges[idx][2] if vi<offset else 1
kart.name='SM_CT4_PlayerChassis'
s.camera.location=(.05,0,.90);s.camera.data.angle=math.radians(100);s.camera.rotation_euler=Vector((math.cos(math.radians(10)),0,-math.sin(math.radians(10)))).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();s.frame_set(25);s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_percentage=100;rig.animation_data.action.name='A_CT4_Steering'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Target_v4.blend'))
bpy.ops.object.select_all(action='DESELECT');arms.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(E/'SK_CT4_DriverPOV.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,mesh_smooth_type='FACE',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0)
for ob in [wheel,kart]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;loc=ob.location.copy();ob.location=(0,0,0);bpy.ops.export_scene.fbx(filepath=str(E/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',bake_anim=False);ob.location=loc
(P/'manifest.json').write_text(json.dumps({'materials':newmats,'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==hash0,'source_sha256':hash0,'camera_eye_m':[.05,0,.9],'camera_fov':100,'camera_pitch':-10,'rim_vertices':3360,'kart_vertices':len(kart.data.vertices),'driver_vertices':len(arms.data.vertices),'runtime_display':'actual speed and elapsed session/race time; fixed direct-drive 1, decorative load bar'},indent=2))
for name,f in [('center',25),('left',1),('right',49)]:
 s.frame_set(f);wheel.rotation_euler=(T@Matrix.Rotation(math.radians((f-25)/24*25),4,'X')@T.inverted()).to_euler();s.render.filepath=str(P/('blender_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('CT4_BUILD_COMPLETE',flush=True)

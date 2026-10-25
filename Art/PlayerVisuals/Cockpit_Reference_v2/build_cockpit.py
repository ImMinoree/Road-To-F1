"""Separate measured cockpit revision. Originals are read only. Units: meters, +X forward."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OLD=ROOT/'Art/PlayerVisuals/FirstPerson/FP_KartArms.blend';V5=ROOT/'Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend'
E=P/'Exports';E.mkdir(exist_ok=True)
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OLD,V5]}
bpy.ops.wm.open_mainfile(filepath=str(V5));s=bpy.context.scene;s.frame_set(25);deps=bpy.context.evaluated_depsgraph_get()
# Capture posed original lower suit geometry and untouched kart as independent cosmetic copies.
legs=[];kart=[]
for o in list(s.objects):
 isleg=o.name in ['RACER | fitted one-piece suit','RACER | sculpted racing boots']
 iskart=o.type=='MESH' and o.name.startswith('SK_Kart_') and not o.name.startswith('SK_Kart_Steering_Column_And_Wheel_')
 if o.type!='MESH' or not(isleg or iskart):continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();coords=[o.matrix_world@v.co for v in me.vertices]
 legids={v.index for v in me.vertices if sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(('pelvis','thigh_','calf_','foot_','ball_')))>.5} if isleg else set()
 polys=[p for p in me.polygons if not isleg or all(i in legids for i in p.vertices)]
 ids=sorted({i for p in polys for i in p.vertices});mp={i:j for j,i in enumerate(ids)}
 ws=[[(o.vertex_groups[g.group].name,g.weight) for g in me.vertices[i].groups] for i in ids] if isleg else []
 record={'name':o.name,'v':[tuple(coords[i]) for i in ids],'f':[tuple(mp[i] for i in p.vertices) for p in polys],'w':ws,'mi':[p.material_index for p in polys],'mats':[m.name for m in me.materials],'uv':[[tuple(me.uv_layers.active.data[i].uv) for i in p.loop_indices] for p in polys] if me.uv_layers.active else []}
 (legs if isleg else kart).append(record);ev.to_mesh_clear()
bpy.ops.wm.open_mainfile(filepath=str(OLD));s=bpy.context.scene;rig=bpy.data.objects['FP_KartArms_Rig'];arms=bpy.data.objects['SK_FP_KartArms'];oldwheel=bpy.data.objects['SM_FP_SteeringWheel'];bpy.data.objects.remove(oldwheel,do_unlink=True)
s.frame_set(25);bpy.context.view_layer.update();center={b.name:b.matrix.copy() for b in rig.pose.bones};world={n:rig.matrix_world@m for n,m in center.items()};inv=rig.matrix_world.inverted();rig.animation_data_clear()

def mat(name,col,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*col,1);q.inputs['Roughness'].default_value=rough;q.inputs['Metallic'].default_value=metal;return m
M={
 'red':mat('M_CV2_RedTextile',(.42,.009,.025),.70),
 'dark':mat('M_CV2_SuitGraphite',(.028,.035,.045),.8),
 'legs':mat('M_CV2_LegFabric',(.012,.017,.023),.84),
 'palm':mat('M_CV2_PalmSuede',(.018,.021,.025),.83),
 'blue':mat('M_CV2_BlueGrip',(.018,.026,.16),.79),
 'rubber':mat('M_CV2_TrimRubber',(.008,.01,.014),.7),
 'metal':mat('M_CV2_BrushedAluminum',(.39,.42,.46),.37,.88),
 'bolt':mat('M_CV2_DarkSteel',(.065,.075,.09),.3,.9),
 'screen':mat('M_CV2_LCD',(.22,.30,.22),.36),
 'ink':mat('M_CV2_LCDInk',(.012,.025,.018),.65),
 'thread':mat('M_CV2_LightThread',(.48,.50,.49),.8),
 'green':mat('M_CV2_LEDGreen',(.025,.55,.065),.35),
 'amber':mat('M_CV2_LEDAmber',(.8,.24,.012),.35),
}
# Reuse the authored microfiber normal tile at low amplitude; form comes from geometry.
normal=next((i for i in bpy.data.images if i.name.startswith('T_FP_Microfiber_N')),None)
for key in ['red','dark','legs','palm','blue']:
 m=M[key];nt=m.node_tree;q=nt.nodes.get('Principled BSDF');tx=nt.nodes.new('ShaderNodeTexImage');tx.image=normal;uv=nt.nodes.new('ShaderNodeTexCoord');sc=nt.nodes.new('ShaderNodeVectorMath');sc.operation='SCALE';sc.inputs['Scale'].default_value=6;nt.links.new(uv.outputs['UV'],sc.inputs[0]);nt.links.new(sc.outputs[0],tx.inputs['Vector']);nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.12;nt.links.new(tx.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],q.inputs['Normal'])
for i,m in enumerate(list(arms.data.materials)):
 name=m.name
 if 'Rubber' in name:
  ids={v for p in arms.data.polygons if p.material_index==i for v in p.vertices}
  for j in ids:
   v=arms.data.vertices[j];side='l' if v.co.y>0 else 'r';W=world['hand_'+side].translation;D=(W-world['lowerarm_'+side].translation).normalized();delta=v.co-W
   if delta.length<.13:v.co-=(delta-D*delta.dot(D))*.14
 arms.data.materials[i]=M['red' if any(x in name for x in ['Leather','Red','Rubber']) else 'dark' if 'White' in name else 'thread']

def mesh_obj(name,vs,fs,material):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);me.materials.append(material)
 for p in me.polygons:p.use_smooth=True
 return o
def add_record(rec,material,skinned=False):
 o=mesh_obj(rec['name']+' | CV2 copy',rec['v'],rec['f'],material)
 if rec['uv']:
  uv=o.data.uv_layers.new(name='SourceUV')
  for p,values in zip(o.data.polygons,rec['uv']):
   for i,v in zip(p.loop_indices,values):uv.data[i].uv=v
 if skinned:
  for i,ws in enumerate(rec['w']):
   for n,w in ws:
    g=o.vertex_groups.get(n) or o.vertex_groups.new(name=n);g.add([i],w,'REPLACE')
  a=o.modifiers.new('Preserved MakeHuman weights','ARMATURE');a.object=rig
 return o
lp=[add_record(r,M['legs'] if 'suit' in r['name'] else M['palm'],True) for r in legs]
# Tailor the inherited baggy knee cloth locally, without replacing source weights or human topology.
for o in lp:
 if 'suit' not in o.name:continue
 for v in o.data.vertices:
  side='l' if v.co.y>0 else 'r';K=world['calf_'+side].translation;d=v.co-K;w=math.exp(-((d.length/.16)**4));v.co.y-=d.y*.25*w
  H=world['thigh_'+side].translation;D=K-H;t=max(0,min(1,(v.co-H).dot(D)/D.length_squared));axis=H+D*t;tw=sum(g.weight for g in v.groups if o.vertex_groups[g.group].name=='thigh_'+side);v.co.y-=(v.co.y-axis.y)*.17*tw
# Preserve source kart surfaces/material categories; remove old wheel/column only in the new local copy.
chassisparts=[]
for r in kart:
 o=add_record(r,M['rubber']);o.data.materials.clear()
 for name in r['mats']:
  old=bpy.data.materials.get(name)
  if old:o.data.materials.append(old)
  else:o.data.materials.append(M['metal' if 'Alloy' in name else 'rubber'])
 for p,i in zip(o.data.polygons,r['mi']):p.material_index=min(i,len(o.data.materials)-1)
 chassisparts.append(o)

# Smooth contoured path, flattened upper bridge and lower corners; 330 mm outer width.
controls=[(-.080,.143),(0,.148),(.080,.143),(.124,.110),(.148,.040),(.146,-.047),(.112,-.120),(.067,-.143),(0,-.147),(-.067,-.143),(-.112,-.120),(-.146,-.047),(-.148,.040),(-.124,.110)]
def catmull(points,steps=12):
 out=[];N=len(points)
 for i in range(N):
  p0,p1,p2,p3=[Vector(points[j%N]) for j in [i-1,i,i+1,i+2]]
  for k in range(steps):
   t=k/steps;out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 return out
path=catmull(controls);wv=[];wf=[];bands=[];N=len(path);sides=20
for i,p in enumerate(path):
 tangent=(path[(i+1)%N]-path[(i-1)%N]).normalized();rad=Vector((tangent.y,-tangent.x))
 for j in range(sides):
  a=2*math.pi*j/sides;wv.append((.017*math.cos(a),p.x+.017*math.sin(a)*rad.x,p.y+.017*math.sin(a)*rad.y))
for i,p in enumerate(path):
 for j in range(sides):wf.append((i*sides+j,i*sides+(j+1)%sides,((i+1)%N)*sides+(j+1)%sides,((i+1)%N)*sides+j));bands.append(1 if p.y<-.120 else 0)
rim=mesh_obj('Contoured padded kart wheel | 330mm',wv,wf,M['blue']);rim.data.materials.append(M['metal'])
for p,i in zip(rim.data.polygons,bands):p.material_index=i
wheelparts=[rim]
def plate(name,outline,depth,material,x=-.004):
 vs=[(x+d,y,z) for d in [-depth/2,depth/2] for y,z in outline];n=len(outline);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=mesh_obj(name,vs,fs,material);b=o.modifiers.new('Machined edge radii','BEVEL');b.width=.0012;b.segments=3;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=b.name);o.select_set(False);wheelparts.append(o);return o
# Open three-spoke construction with split side arms (actual gaps, not dark painted slots).
plate('Hub plate',[(.04,.025),(.042,-.027),(0,-.045),(-.042,-.027),(-.04,.025),(0,.040)],.005,M['metal'])
for sign in [-1,1]:
 for dz in [-.016,.016]:
  plate('Split slotted spoke',[(sign*.025,dz-.006),(sign*.122,dz+.018),(sign*.131,dz+.031),(sign*.030,dz+.008)],.004,M['metal'])
plate('Lower open spoke L',[(-.022,-.029),(-.078,-.128),(-.063,-.135),(-.004,-.038)],.004,M['metal'])
plate('Lower open spoke R',[(.022,-.029),(.078,-.128),(.063,-.135),(.004,-.038)],.004,M['metal'])

def box(name,loc,scale,material,bevel=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:
  m=o.modifiers.new('Molded edge radii','BEVEL');m.width=bevel;m.segments=4;bpy.ops.object.modifier_apply(modifier=m.name)
 return o
def cylinder(name,loc,radius,depth,material,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=(0,math.pi/2,0));o=bpy.context.object;o.name=name;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 return o
for i in range(6):
 a=i*math.pi/3;wheelparts.append(cylinder('Hub washer',(-.009,.026*math.cos(a),.026*math.sin(a)),.0042,.001,M['bolt']))
 wheelparts.append(cylinder('Hex socket bolt',(-.011,.026*math.cos(a),.026*math.sin(a)),.0028,.002,M['metal'],6))
 wheelparts.append(cylinder('Recess in bolt',(-.0122,.026*math.cos(a),.026*math.sin(a)),.0013,.0002,M['bolt'],6))
# Standalone digital logger. No live gameplay telemetry is implied.
wheelparts.append(box('Logger mounting bridge',(.004,0,.082),(.012,.090,.016),M['metal']))
wheelparts.append(box('Digital logger molded housing',(-.011,0,.110),(.032,.122,.071),M['rubber'],.009))
wheelparts.append(box('Recessed LCD glass',(-.028,0,.110),(.001,.090,.043),M['screen'],.004))
for sign in [-1,1]:
 for dz in [-.018,0,.018]:wheelparts.append(cylinder('Logger tactile button',(-.029,sign*.052,.11+dz),.003,.002,M['bolt']))
for i in range(7):wheelparts.append(box('Shift LED lens',(-.029,(i-3)*.009,.139),(.002,.0045,.003),M['green' if i<5 else 'amber'],.001))
def text_obj(body,loc,size,material):
 c=bpy.data.curves.new('LCD glyph geometry','FONT');c.body=body;c.size=size;c.align_x='CENTER';c.extrude=.00006;c.resolution_u=5;o=bpy.data.objects.new('LCD | '+body,c);s.collection.objects.link(o);o.location=loc
 # text local +X goes toward world -Y, local +Y toward +Z, normal toward camera -X
 o.rotation_euler=Matrix(((0,0,-1),(-1,0,0),(0,1,0))).to_euler();c.materials.append(material);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);wheelparts.append(o)
text_obj('12 350',(-.029,0,.110),.013,M['ink']);text_obj('LAP  01    00:42.80',(-.029,0,.097),.005,M['ink']);text_obj('DEMO',(-.029,0,.083),.0035,M['thread'])

# Shaped glove dorsal pads follow existing anatomy and retain existing weights.
# Source first-person glove already has genuine raised panels and sewn edges.
for o in [arms]+lp:
 for p in o.data.polygons:p.use_smooth=True
bpy.ops.object.select_all(action='DESELECT')
for o in [arms]+lp:o.select_set(True)
bpy.context.view_layer.objects.active=arms;bpy.ops.object.join();arms.name='SK_CV2_DriverPOV'

TILT=Matrix.Rotation(math.radians(18),4,'Y');CENTER=Vector((.62,0,.67));OLD_CENTER=Vector((.62,0,.70));stats=[]
def aim_matrix(base,head,tail):
 olddir=base.to_3x3().col[1].normalized();rot=olddir.rotation_difference((tail-head).normalized()).to_matrix().to_4x4()@base.copy();rot.translation=head;return rot
# Analytic two-bone arm solve, fixed bone lengths, constant curled-finger grasp.
for frame in range(1,50):
 s.frame_set(frame)
 for b in rig.pose.bones:b.rotation_mode='QUATERNION';b.matrix_basis=Matrix.Identity(4)
 angle=math.radians((frame-25)/24*25);R=Matrix.Rotation(angle,4,'X');bpy.context.view_layer.update()
 # Relax only the separate POV shoulder girdle by 20 mm forward / 40 mm down.
 upperroot=rig.pose.bones['spine_03'];rootmat=world['spine_03'].copy();rootmat.translation+=Vector((.020,0,-.040));upperroot.matrix=inv@rootmat;bpy.context.view_layer.update()
 for side,sign in [('l',1),('r',-1)]:
  hand='hand_'+side;up='upperarm_'+side;lo='lowerarm_'+side
  grip_delta=Vector((0,sign*(.148-.184),.025))
  target=Matrix.Translation(CENTER)@TILT@R@Matrix.Translation(grip_delta-OLD_CENTER)@world[hand]
  W=target.translation;S=(rig.matrix_world@rig.pose.bones[up].matrix).translation
  L1=(world[lo].translation-world[up].translation).length;L2=(world[hand].translation-world[lo].translation).length;d=(W-S).length
  assert d<L1+L2-.001, ('unreachable',frame,side,d,L1+L2)
  D=(W-S).normalized();pole=world[lo].translation+Vector((0,sign*.025,-.04))-S;pole=(pole-D*pole.dot(D)).normalized();a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));elbow=S+D*a+pole*h
  rig.pose.bones[up].matrix=inv@aim_matrix(world[up],S,elbow);bpy.context.view_layer.update();rig.pose.bones[lo].matrix=inv@aim_matrix(world[lo],elbow,W);bpy.context.view_layer.update();rig.pose.bones[hand].matrix=inv@target;bpy.context.view_layer.update()
  error=((rig.matrix_world@rig.pose.bones[hand].matrix).translation-W).length;bend=180-math.degrees(math.acos(max(-1,min(1,(L1*L1+L2*L2-d*d)/(2*L1*L2)))))
  stats.append({'frame':frame,'side':side,'wrist_error_m':error,'elbow_bend_degrees':bend})
 # Adduct the knees into the free space inside the wheel. Hip/ankle positions and both segment lengths stay fixed.
 for side,sign in [('l',1),('r',-1)]:
  up='thigh_'+side;lo='calf_'+side;foot='foot_'+side;H=world[up].translation;K=world[lo].translation;W=world[foot].translation;D=(W-H).normalized();pivot=H+D*(K-H).dot(D);A=Matrix.Rotation(math.radians(21),4,D);newK=pivot+A.to_3x3()@(K-pivot)
  if (newK.y-K.y)*sign>0:A=Matrix.Rotation(-math.radians(21),4,D);newK=pivot+A.to_3x3()@(K-pivot)
  rig.pose.bones[up].matrix=inv@aim_matrix(world[up],H,newK);bpy.context.view_layer.update();rig.pose.bones[lo].matrix=inv@aim_matrix(world[lo],newK,W);bpy.context.view_layer.update();rig.pose.bones[foot].matrix=inv@world[foot];bpy.context.view_layer.update()
 for b in rig.pose.bones:
  b.rotation_mode='QUATERNION';b.keyframe_insert('location',frame=frame);b.keyframe_insert('rotation_quaternion',frame=frame);b.keyframe_insert('scale',frame=frame)
rig.animation_data.action.name='A_CV2_Steering';s.frame_set(25);bpy.context.view_layer.update()

def join(parts,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=parts[0];o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);return o
wheel=join(wheelparts,'SM_CV2_SteeringWheel')
# Wheel is modeled around origin; bake tilt into vertices. Runtime rolls around the tilted shaft.
wheel.data.transform(TILT);wheel.location=CENTER
# New local-only steering shaft replaces the disconnected old source column.
shaft_a=CENTER+TILT.to_3x3()@Vector((.02,0,0));shaft_b=Vector((.96,0,.22));dv=shaft_b-shaft_a
bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.009,depth=dv.length,location=(shaft_a+shaft_b)/2);shaft=bpy.context.object;shaft.name='Local cockpit steering shaft';shaft.rotation_euler=dv.to_track_quat('Z','Y').to_euler();shaft.data.materials.append(M['metal']);chassisparts.append(shaft)
chassis=join(chassisparts,'SM_CV2_PlayerChassis')
# UV unwrap only new hard surfaces; source garment UVs and weights remain intact.
for o in [wheel,chassis]:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.005);bpy.ops.object.mode_set(mode='OBJECT')
s.camera.location=(.05,0,1.05);s.camera.rotation_euler=Vector((math.cos(math.radians(10)),0,-math.sin(math.radians(10)))).to_track_quat('-Z','Y').to_euler();s.camera.data.angle=math.radians(105)
s.frame_set(25);s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
s['CV2 limitations']='Reference-inspired geometry; glove/cloth art remains below photographic reference quality. Logger is cosmetic DEMO.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Reference_v2.blend'))
bpy.ops.object.select_all(action='DESELECT');arms.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(E/'SK_CV2_DriverPOV.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,mesh_smooth_type='FACE',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
for o in [wheel,chassis]:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;loc=o.location.copy();o.location=(0,0,0)
 bpy.ops.export_scene.fbx(filepath=str(E/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',bake_anim=False,path_mode='COPY',embed_textures=True);o.location=loc
report={'source_hashes':hashes,'sources_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items()),'wheel_center_m':list(CENTER),'wheel_outer_width_m':wheel.dimensions.y,'wheel_tilt_degrees':18,'steering_degrees':[-25,25],'minimum_elbow_bend_degrees':min(r['elbow_bend_degrees'] for r in stats),'maximum_wrist_error_m':max(r['wrist_error_m'] for r in stats),'arm_samples':stats,'materials':{m.name:{'color':list(m.diffuse_color),'roughness':m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value,'metallic':m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value} for m in M.values()},'camera_eye_m':[.05,0,1.05],'camera_pitch_degrees':-10,'horizontal_fov_degrees':105}
(P/'manifest.json').write_text(json.dumps(report,indent=2))
for name,frame in [('center',25),('left',1),('right',49)]:
 s.frame_set(frame);wheel.rotation_euler=(TILT@Matrix.Rotation(math.radians((frame-25)/24*25),4,'X')@TILT.inverted()).to_euler();s.render.filepath=str(P/('blender_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('COCKPIT_BUILD_COMPLETE',report['minimum_elbow_bend_degrees'],report['maximum_wrist_error_m'],flush=True)

"""Versioned visual assembly. Reuses authored CL5/MakeHuman art; never saves sources."""
import bpy, math, json, bmesh, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
P=Path(__file__).resolve().parent; ROOT=P.parents[1]; E=P/'Exports'; E.mkdir(exist_ok=True)
source=ROOT/'Art/PlayerVisuals/Cockpit_Layout_v5/Kart_Cockpit_Layout_v5.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source)); s=bpy.context.scene; s.frame_set(25)
k=bpy.data.objects['SM_CL5_PlayerChassis']; wheel=bpy.data.objects['SM_CL5_SteeringWheel']; rig=bpy.data.objects['FP_KartArms_Rig']; pov=bpy.data.objects['SK_CL5_DriverPOV']
parts=json.loads((source.parent/'parts.json').read_text()); exported=[]; manifest={}
SHIFT=Vector((-.31,0,0)); C=Vector((.23,0,.52)); tilt=Matrix.Rotation(math.radians(55),4,'Y'); oldtilt=Matrix.Rotation(math.radians(18),4,'Y')
# Compact the inherited oversized engine and nose within this version only.
for part in parts:
 for i in range(part['start'],part['end']):
  v=k.data.vertices[i];name=part['name']
  if 'Engine_' in name or 'Exhaust_' in name:
   v.co=Vector((-.32,-.30,.40))-SHIFT+(v.co+SHIFT-Vector((-.36,0,.55)))*.60
  if 'Nose_And_Front' in name and v.co.x+SHIFT.x>.72:v.co.x=.72-SHIFT.x+(v.co.x+SHIFT.x-.72)*.45
def join(obs,name,origin=(0,0,0)):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]; bpy.ops.object.join(); o=obs[0]; o.name=name
 world=o.matrix_world.copy(); o.data.transform(world); o.matrix_world=Matrix.Identity(4)
 o.data.transform(Matrix.Translation(-Vector(origin)));o.location=origin;return o
def export(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 loc=o.location.copy();o.location=(0,0,0)
 bpy.ops.export_scene.fbx(filepath=str(E/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',bake_anim=False,mesh_smooth_type='FACE')
 o.location=loc;exported.append(o);manifest[o.name]={'origin_m':list(loc),'dimensions_m':list(o.dimensions),'vertices':len(o.data.vertices)}
def subset(name,indices,origin=(0,0,0),offset=SHIFT):
 o=k.copy();o.data=k.data.copy();bpy.context.collection.objects.link(o);o.name=name
 bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in indices],context='VERTS');bm.to_mesh(o.data);bm.free()
 o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4);o.data.transform(Matrix.Translation(offset-Vector(origin)));o.location=origin;return o
def ids(predicate):return {i for p in parts if predicate(p['name']) for i in range(p['start'],p['end'])}
wheelids=ids(lambda n:'_Wheel_' in n)
remove=ids(lambda n:any(t in n for t in ['Axles_Steering','Front_Brake','Steering_Rod','Driver_Controls','Drivetrain_Chain','Drivetrain_Bearing','Brake_Hydraulic']) or ('Engine_Ignition' in n and any(t in n for t in ['Chain_Hardened','Frame_Brushed'])))|set(range(54912,len(k.data.vertices)))
chassis=subset('SM_V4_Chassis',set(range(len(k.data.vertices)))-wheelids-remove)
def paint(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.36;bs.inputs['Metallic'].default_value=.12;return m
chassis.data.materials.append(paint('M_V4_RacingRed',(.52,.008,.015)));red=len(chassis.data.materials)-1
chassis.data.materials.append(paint('M_V4_RacingWhite',(.75,.77,.78)));white=len(chassis.data.materials)-1
for face in chassis.data.polygons:
 name=chassis.data.materials[face.material_index].name
 if 'Body_Satin' in name or 'BodyGraphite' in name:
  center=sum((chassis.data.vertices[i].co for i in face.vertices),Vector())/len(face.vertices)
  if abs(center.y)>.23:face.material_index=red if center.z<.21 else white
  elif center.x>.70:face.material_index=red
export(chassis)
centres={}
for code,x,y in [('FL',.60,.53),('FR',.60,-.53),('RL',-.44,.53),('RR',-.44,-.53)]:
 ix=ids(lambda n:'_Wheel_'+code+'_' in n); vv=[k.matrix_world@k.data.vertices[i].co for i in ix]
 lo=Vector(tuple(min(v[j] for v in vv) for j in range(3)));hi=Vector(tuple(max(v[j] for v in vv) for j in range(3)));center=(lo+hi)*.5
 radius=(hi.z-lo.z)*.5;new=Vector((x,y,radius));o=subset('SM_V4_Wheel'+code,ix,new,new-center);export(o);centres[code]=list(new)
# Existing sculpted wheel/cluster, reoriented to a continuous shaft inclined 55 degrees.
wheel.data.transform(tilt@oldtilt.inverted());wheel.location=C;wheel.name='SM_V4_SteeringWheel';export(wheel)
metal=bpy.data.materials.get('M_CT4_SatinAlloy');dark=bpy.data.materials.get('M_CT4_Anodised')
if not metal:metal=chassis.data.materials[0]
if not dark:dark=metal
def rod(name,a,b,r=.008,mat=metal):
 a=Vector(a);b=Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=(b-a).length,location=(a+b)*.5);o=bpy.context.object;o.name=name;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);return o
axis=tilt.to_3x3()@Vector((1,0,0));bottom=C+axis*.35
shaft=join([rod('shaft',C,bottom,.012)],'SM_V4_Column',C);export(shaft)
pin=bottom+Vector((.08,0,.08/math.tan(math.radians(55))))
pit=join([rod('pitman',bottom,pin,.012)],'SM_V4_Pitman',bottom);export(pit)
export(join([rod('unit rod',(0,0,0),(1,0,0),.006)],'SM_V4_TieRod'))
for code,sign in [('FL',1),('FR',-1)]:
 center=Vector(centres[code]);kp=Vector((center.x,sign*.46,center.z));pickup=kp+Vector((-.11,-sign*.049,0))
 knuckle=join([rod('kingpin',kp-Vector((0,0,.04)),kp+Vector((0,0,.04)),.014),rod('stub',kp,center,.018),rod('arm',kp,pickup,.012)],'SM_V4_Knuckle'+code,kp);export(knuckle)
export(join([rod('axle',(-.44,-.61,centres['RL'][2]),(-.44,.61,centres['RL'][2]),.025)],'SM_V4_RearAxle',(-.44,0,centres['RL'][2])))
for name,y,r,th in [('Sprocket',-.36,.10,.008),('BrakeDisc',.30,.09,.006)]:
 c=Vector((-.44,y,centres['RL'][2]));obs=[rod(name,c-Vector((0,th*.5,0)),c+Vector((0,th*.5,0)),r)]
 if name=='Sprocket':
  for i in range(42):
   a=math.tau*i/42;p=c+Vector((math.cos(a)*r,0,math.sin(a)*r));obs.append(rod('tooth',p,p+Vector((math.cos(a)*.009,0,math.sin(a)*.009)),.004))
 export(join(obs,'SM_V4_'+name,c))
caliper=join([rod('caliper',(-.38,.285,.25),(-.38,.315,.25),.028,dark)],'SM_V4_Caliper');export(caliper)
# A rigid instanced link follows a closed path at runtime; no deforming chain mesh.
export(join([rod('plate',(0,-.008,0),(.0127,-.008,0),.003),rod('plate',(0,.008,0),(.0127,.008,0),.003),rod('pin',(0,-.011,0),(0,.011,0),.003)],'SM_V4_ChainLink'))
for side in ['l','r']:
 foot=(rig.matrix_world@rig.pose.bones['foot_'+side].matrix).translation+SHIFT
 pivot=foot+Vector((.08,0,-.035));o=join([rod('pedal',pivot,pivot+Vector((0,0,.09)),.008),rod('pad',pivot+Vector((0,-.045,.09)),pivot+Vector((0,.045,.09)),.012,dark)],'SM_V4_Pedal'+side,pivot);export(o)
manifest['mechanism']={'wheel_center_m':list(C),'column_bottom_m':list(bottom),'pitman_pin_m':list(pin),'axis':list(axis),'wheel_centres_m':centres,'wheelbase_m':1.04,'track_m':1.06}
# Import the preserved full-body weighted racer onto the same seated grip-bind skeleton.
base={b.name:rig.matrix_world@b.matrix for b in rig.pose.bones};before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ROOT/'Art/RacingAI/SK_AI_KartDriver.fbx'))
added=set(bpy.data.objects)-before;full=next(o for o in added if o.type=='MESH');full.name='SK_V4_DriverFull'
for mod in full.modifiers:
 if mod.type=='ARMATURE':mod.object=rig
full_world=full.matrix_world.copy();full.parent=None;full.matrix_world=full_world
for o in added:
 if o.type=='ARMATURE':bpy.data.objects.remove(o,do_unlink=True)
# The old exterior gloves/boots use an earlier bind fit. Reuse the fitted weighted
# POV limbs in both views, retaining the full racer's torso and helmet.
limbs=('lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_','thigh_','calf_','foot_','ball_')
drop={v.index for v in full.data.vertices if sum(g.weight for g in v.groups if full.vertex_groups[g.group].name.startswith(limbs))>.35}
bm=bmesh.new();bm.from_mesh(full.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index in drop],context='VERTS');bm.to_mesh(full.data);bm.free()
limbcopy=pov.copy();limbcopy.data=pov.data.copy();bpy.context.collection.objects.link(limbcopy)
full=join([limbcopy,full],'SK_V4_DriverFull')
# Bake two-bone arm IK to 49 fixed-grip steering samples. Fingers retain their authored curl.
rig.animation_data_clear();bpy.context.view_layer.update();inv=rig.matrix_world.inverted()
# Restoring the source centre pose after clearing the action avoids rebinding any skin.
# Source action centre was evaluated before animation_data_clear and is retained in pose.
def aim(m,a,b):
 out=m.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@m;out.translation=a;return out
def solve(side,target):
 up,lo,end=['upperarm_'+side,'lowerarm_'+side,'hand_'+side];H=base[up].translation;W=target.translation;L1=(base[lo].translation-H).length;L2=(base[end].translation-base[lo].translation).length;D=(W-H).normalized();d=(W-H).length
 if d>=L1+L2:raise RuntimeError(('unreachable grip',side,d,L1+L2))
 a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));pole=Vector((-.3,.35 if side=='l' else -.35,-1));pole=(pole-D*pole.dot(D)).normalized();K=H+D*a+pole*h
 rig.pose.bones[up].matrix=inv@aim(base[up],H,K);bpy.context.view_layer.update();rig.pose.bones[lo].matrix=inv@aim(base[lo],K,W);bpy.context.view_layer.update();rig.pose.bones[end].matrix=inv@target;bpy.context.view_layer.update()
originalC=Vector((.62,0,.52));grips={side:base['hand_'+side].copy() for side in ['l','r']};errors=[]
for f in range(1,50):
 s.frame_set(f)
 for n,m in base.items():rig.pose.bones[n].matrix=inv@m
 bpy.context.view_layer.update();ang=(f-25)/24*45;rot=tilt@Matrix.Rotation(math.radians(ang),4,'X')@oldtilt.inverted()
 for side in ['l','r']:
  target=Matrix.Translation(originalC)@rot@Matrix.Translation(-originalC)@grips[side];target.translation.x-=.08;solve(side,target);errors.append(((rig.matrix_world@rig.pose.bones['hand_'+side].matrix).translation-target.translation).length)
 for b in rig.pose.bones:
  for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=f)
rig.location+=SHIFT;pov.location+=SHIFT;full.location+=SHIFT
rig.animation_data.action.name='A_V4_Steering';pov.name='SK_V4_DriverPOV'
for skin in [pov,full]:
 bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(E/(skin.name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
k.hide_render=True;k.hide_set(True);pov.hide_render=True;s.frame_set(25)
manifest['source']=str(source);manifest['source_sha256']=digest;manifest['max_grip_bone_error_m']=max(errors);manifest['materials']={}
for o in exported+[full,pov]:
 for m in o.data.materials:
  if not m:continue
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
  manifest['materials'][m.name]={'color':list(bs.inputs['Base Color'].default_value if bs else m.diffuse_color),'roughness':float(bs.inputs['Roughness'].default_value if bs else .6),'metallic':float(bs.inputs['Metallic'].default_value if bs else 0)}
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
bpy.ops.wm.save_as_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'));(P/'manifest.json').write_text(json.dumps(manifest,indent=2));print('V4_EXPORT_COMPLETE')








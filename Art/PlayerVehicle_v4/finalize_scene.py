"""Assemble the editable Blender hierarchy and steering preview from exported parts.
Only the .blend is changed; Unreal meshes remain normalized and pivot-local.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'))
s=bpy.context.scene;m=json.loads((P/'manifest.json').read_text());mechanism=m['mechanism']
for name in ['Column','Pitman','TieRod','KnuckleFL','KnuckleFR','RearAxle','Sprocket','BrakeDisc','Caliper','Pedall','Pedalr','ChainLink']:
 o=bpy.data.objects['SM_V4_'+name]
 for i in range(len(o.data.materials)):o.data.materials[i]=bpy.data.materials['M_CT4_Anodised' if name=='Caliper' else 'M_CT4_SatinAlloy']
root=bpy.data.objects.new('VehicleRoot',None);s.collection.objects.link(root)
def parent(o,p):
 world=o.matrix_world.copy();o.parent=p;o.matrix_world=world
for o in list(s.objects):
 if o.name.startswith('SM_V4_') or o.name=='FP_KartArms_Rig' or o.name=='SK_V4_DriverFull':parent(o,root)
for side in ['FL','FR']:parent(bpy.data.objects['SM_V4_Wheel'+side],bpy.data.objects['SM_V4_Knuckle'+side])
for name in ['WheelRL','WheelRR','BrakeDisc','Sprocket']:parent(bpy.data.objects['SM_V4_'+name],bpy.data.objects['SM_V4_RearAxle'])
prototype=bpy.data.objects['SM_V4_TieRod'];other=prototype.copy();other.data=prototype.data;s.collection.objects.link(other);other.name='FrontRightTieRod';parent(other,root)
rods=[prototype,other];axis=Vector(mechanism['axis']);bottom=Vector(mechanism['column_bottom_m']);offset=Vector(mechanism['pitman_pin_m'])-bottom
def pin(a):return bottom+Quaternion(axis,math.radians(a))@offset
def pickup(side,a):return Vector((.60,side*.46,.17589))+Quaternion(Vector((0,0,1)),math.radians(a))@Vector((-.11,-side*.049,0))
def knuckle(side,c):
 length=(pin(0)-pickup(side,0)).length;a=c*.6
 for i in range(16):
  def error(a):return (pin(c)-pickup(side,a)).length-length
  derivative=(error(a+.05)-error(a-.05))/.1
  if abs(derivative)<1e-6:break
  a=max(-60,min(60,a-error(a)/derivative))
 return a
for frame in range(1,50):
 s.frame_set(frame);a=(frame-25)/24*45
 for name in ['Column','Pitman','SteeringWheel']:
  o=bpy.data.objects['SM_V4_'+name];o.rotation_mode='QUATERNION';o.rotation_quaternion=Quaternion(axis,math.radians(a));o.keyframe_insert('rotation_quaternion',frame=frame)
 for i,(name,side) in enumerate([('FL',1),('FR',-1)]):
  angle=knuckle(side,a);o=bpy.data.objects['SM_V4_Knuckle'+name];o.rotation_mode='QUATERNION';o.rotation_quaternion=Quaternion(Vector((0,0,1)),math.radians(angle));o.keyframe_insert('rotation_quaternion',frame=frame)
  A=pin(a);B=pickup(side,angle);rod=rods[i];rod.location=A;rod.rotation_mode='QUATERNION';rod.rotation_quaternion=(B-A).to_track_quat('X','Z');rod.scale=((B-A).length,1,1)
  for prop in ['location','rotation_quaternion','scale']:rod.keyframe_insert(prop,frame=frame)
bpy.data.objects['SM_V4_ChainLink'].hide_render=True;bpy.data.objects['SM_V4_ChainLink'].hide_set(True)
root['runtime']='UKartMechanicalVisuals; centimetre conversion in FBX; source preview frames are steering poses, not driving physics.'
root['chain']='SM_V4_ChainLink is the pivot-local prototype; Unreal instantiates its loop at runtime.'
s.frame_set(25);bpy.ops.wm.save_as_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'));print('V4_EDITABLE_HIERARCHY_SAVED')


import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent;E=P/'Exports';E.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'Cockpit_Target_v4/Kart_Cockpit_Target_v4.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CT4_DriverPOV'];k=bpy.data.objects['SM_CT4_PlayerChassis'];w=bpy.data.objects['SM_CT4_SteeringWheel'];inv=r.matrix_world.inverted()
bases={}
for f in range(1,50):
 s.frame_set(f);bases[f]={b.name:r.matrix_world@b.matrix for b in r.pose.bones}
def aim(m,a,b):
 out=m.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@m;out.translation=a;return out
def solve(base,names,target,pole):
 up,lo,end=names;H=(r.matrix_world@r.pose.bones[up].matrix).translation;W=target.translation;L1=(base[lo].translation-base[up].translation).length;L2=(base[end].translation-base[lo].translation).length;D=(W-H).normalized();d=(W-H).length
 assert d<L1+L2,(names,d,L1+L2)
 a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));pole=(pole-D*pole.dot(D)).normalized();K=H+D*a+pole*h
 r.pose.bones[up].matrix=inv@aim(base[up],H,K);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(base[lo],K,W);bpy.context.view_layer.update();r.pose.bones[end].matrix=inv@target;bpy.context.view_layer.update()
for f,base in bases.items():
 s.frame_set(f)
 for n,dz in [('pelvis',-.18),('spine_01',-.15)]:
  m=base[n].copy();m.translation.z+=dz;r.pose.bones[n].matrix=inv@m;bpy.context.view_layer.update()
 for side in ['l','r']:
  target=base['foot_'+side].copy();target.translation.x+=.4;solve(base,['thigh_'+side,'calf_'+side,'foot_'+side],target,Vector((0,0,1)))
  solve(base,['upperarm_'+side,'lowerarm_'+side,'hand_'+side],base['hand_'+side],Vector((-.3, .35 if side=='l' else -.35,-1)))
 for b in r.pose.bones:
  for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=f)
for p in json.loads((P/'parts.json').read_text()):
 for i in range(p['start'],p['end']):
  v=k.data.vertices[i];name=p['name']
  if 'Seat_' in name:v.co.z-=.08
  elif 'Fuel_Tank' in name:pass
  elif 'Driver_Controls' in name:v.co.x+=.4
  else:v.co.x+=.35
  if 'Nose_And_Front' in name:v.co.z-=.24
# Extend the existing shaft towards relocated steering linkage, keeping wheel end fixed.
for v in k.data.vertices[54912:]:v.co.x+=.35*max(0,min(1,(.66-v.co.z)/.36))
o.name='SK_CL5_DriverPOV';k.name='SM_CL5_PlayerChassis';w.name='SM_CL5_SteeringWheel';r.animation_data.action.name='A_CL5_Steering'
s.camera.location=(.05,0,.9);s.camera.data.angle=math.radians(95);s.camera.rotation_euler=Vector((math.cos(math.radians(10)),0,-math.sin(math.radians(10)))).to_track_quat('-Z','Y').to_euler();s.frame_set(25)
s.cycles.samples=16;s.render.resolution_percentage=70;bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'))
s.render.filepath=str(P/'preview_center.png');bpy.ops.render.render(write_still=True)

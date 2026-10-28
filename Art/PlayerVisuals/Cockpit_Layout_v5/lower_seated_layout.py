import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];inv=r.matrix_world.inverted();bases={}
for f in range(1,50):
 s.frame_set(f);bases[f]={b.name:r.matrix_world@b.matrix for b in r.pose.bones}
def aim(m,a,b):
 out=m.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@m;out.translation=a;return out
for f,base in bases.items():
 s.frame_set(f)
 for b in r.pose.bones:
  m=base[b.name].copy();m.translation.z-=.15;r.pose.bones[b.name].matrix=inv@m;bpy.context.view_layer.update()
 for side in ['l','r']:
  up,lo,end=['thigh_'+side,'calf_'+side,'foot_'+side];H=(r.matrix_world@r.pose.bones[up].matrix).translation;target=base[end].copy();target.translation.x+=.05;W=target.translation;L1=(base[lo].translation-base[up].translation).length;L2=(base[end].translation-base[lo].translation).length;D=(W-H).normalized();d=(W-H).length;assert d<L1+L2;a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));pole=Vector((0,0,1));pole=(pole-D*pole.dot(D)).normalized();K=H+D*a+pole*h;r.pose.bones[up].matrix=inv@aim(base[up],H,K);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(base[lo],K,W);bpy.context.view_layer.update();r.pose.bones[end].matrix=inv@target;bpy.context.view_layer.update()
 for b in r.pose.bones:
  for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=f)
k=bpy.data.objects['SM_CL5_PlayerChassis']
for p in json.loads((P/'parts.json').read_text()):
 for i in range(p['start'],p['end']):
  v=k.data.vertices[i];name=p['name']
  if 'Seat_' in name:v.co.z-=.15
  if 'Driver_Controls' in name:v.co.x+=.05
  if 'Sidepod' in name or 'Vent_Details' in name:v.co.z-=.1
  if 'Brake_Hydraulic_Lines' in name:v.co.y+=.08 if v.co.y>0 else -.08
for v in k.data.vertices[54912:]:v.co.z-=.15*max(0,min(1,(v.co.z-.3)/.36))
w=bpy.data.objects['SM_CL5_SteeringWheel'];w.location.z-=.15;s.camera.location.z-=.15;s.frame_set(25);bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'))

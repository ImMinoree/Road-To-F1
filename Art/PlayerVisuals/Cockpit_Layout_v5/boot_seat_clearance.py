import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];k=bpy.data.objects['SM_CL5_PlayerChassis'];inv=r.matrix_world.inverted();bases={}
for f in range(1,50):
 s.frame_set(f);bases[f]={b.name:r.matrix_world@b.matrix for b in r.pose.bones}
def aim(m,a,b):
 out=m.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@m;out.translation=a;return out
for f,base in bases.items():
 s.frame_set(f)
 for side in ['l','r']:
  up,lo,end=['thigh_'+side,'calf_'+side,'foot_'+side];H=base[up].translation;target=base[end].copy();target.translation.z+=.08;W=target.translation;L1=(base[lo].translation-H).length;L2=(base[end].translation-base[lo].translation).length;D=(W-H).normalized();d=(W-H).length;a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));pole=Vector((0,0,1));pole=(pole-D*pole.dot(D)).normalized();K=H+D*a+pole*h
  r.pose.bones[up].matrix=inv@aim(base[up],H,K);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(base[lo],K,W);bpy.context.view_layer.update();r.pose.bones[end].matrix=inv@target;bpy.context.view_layer.update()
  for n in [up,lo,end]:
   for prop in ['location','rotation_quaternion','scale']:r.pose.bones[n].keyframe_insert(prop,frame=f)
for p in json.loads((P/'parts.json').read_text()):
 for i in range(p['start'],p['end']):
  v=k.data.vertices[i]
  if 'Seat_' in p['name']:v.co.x+=.15
  if 'Driver_Controls' in p['name']:v.co.z+=.08
s.frame_set(25);bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'))

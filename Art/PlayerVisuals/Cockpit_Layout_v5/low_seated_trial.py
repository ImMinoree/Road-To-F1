import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));s=bpy.context.scene;s.frame_set(25);r=bpy.data.objects['FP_KartArms_Rig'];inv=r.matrix_world.inverted();base={b.name:r.matrix_world@b.matrix for b in r.pose.bones};pel=base['pelvis'].copy();pel.translation.z-=.15;r.pose.bones['pelvis'].matrix=inv@pel;bpy.context.view_layer.update()
for b in r.pose.bones:
 m=base[b.name].copy();m.translation.z-=.15;r.pose.bones[b.name].matrix=inv@m;bpy.context.view_layer.update()
def aim(m,a,b):
 out=m.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@m;out.translation=a;return out
for side in ['l','r']:
 up,lo,end=['thigh_'+side,'calf_'+side,'foot_'+side];H=(r.matrix_world@r.pose.bones[up].matrix).translation;target=base[end].copy();target.translation.x+=.05;W=target.translation;L1=(base[lo].translation-base[up].translation).length;L2=(base[end].translation-base[lo].translation).length;D=(W-H).normalized();d=(W-H).length;a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));pole=Vector((0,0,1));pole=(pole-D*pole.dot(D)).normalized();K=H+D*a+pole*h;r.pose.bones[up].matrix=inv@aim(base[up],H,K);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(base[lo],K,W);bpy.context.view_layer.update();r.pose.bones[end].matrix=inv@target;bpy.context.view_layer.update()
for b in r.pose.bones:
 for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=25)
w=bpy.data.objects['SM_CL5_SteeringWheel'];w.location.z-=.15;s.camera.location.z-=.15;s.cycles.samples=16;s.render.filepath=str(P/'low_seated_trial.png');bpy.ops.render.render(write_still=True)



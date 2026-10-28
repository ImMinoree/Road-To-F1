import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));bpy.context.scene.frame_set(25);r=bpy.data.objects['FP_KartArms_Rig'];print(json.dumps({b.name:list((r.matrix_world@b.matrix).translation) for b in r.pose.bones if b.name.startswith(('pelvis','calf_','thigh_','foot_','ball_'))}))

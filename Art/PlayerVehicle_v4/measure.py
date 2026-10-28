import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'));s=bpy.context.scene;s.frame_set(25);r=bpy.data.objects['FP_KartArms_Rig'];print('MEASURE',json.dumps({b.name:list((r.matrix_world@b.matrix).translation) for b in r.pose.bones if b.name in ['head','neck_01','spine_03','hand_l','hand_r','upperarm_l','upperarm_r']}))

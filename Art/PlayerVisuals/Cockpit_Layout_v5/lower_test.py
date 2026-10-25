import bpy,math
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Layout_Test.blend'));s=bpy.context.scene
# Test a physically lower driver-eye and complete upper cockpit, without scaling rim or arms.
r=bpy.data.objects['FP_KartArms_Rig'];r.location.z-=.15
w=bpy.data.objects['SM_CT4_SteeringWheel'];w.location.z-=.15
s.camera.location.z-=.15
s.camera.rotation_euler=Vector((math.cos(math.radians(18)),0,-math.sin(math.radians(18)))).to_track_quat('-Z','Y').to_euler()
k=bpy.data.objects['SM_CT4_PlayerChassis']
for v in k.data.vertices:
 if 5608<=v.index<20632:v.co.x+=.25
s.render.filepath=str(P/'lower_test.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'Lower_Test.blend'));bpy.ops.render.render(write_still=True)

import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Forward_Test.blend'));s=bpy.context.scene;s.camera.location.z=.9;s.camera.data.angle=math.radians(95);s.camera.rotation_euler=Vector((math.cos(math.radians(10)),0,-math.sin(math.radians(10)))).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/'eye_test.png');bpy.ops.render.render(write_still=True)

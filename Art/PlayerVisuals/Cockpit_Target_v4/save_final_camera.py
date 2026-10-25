import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Target_v4.blend'));s=bpy.context.scene;s.camera.location.z=1.05;s.camera.data.angle=math.radians(95);s.camera.rotation_euler=Vector((math.cos(math.radians(22)),0,-math.sin(math.radians(22)))).to_track_quat('-Z','Y').to_euler();bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Target_v4.blend'));m=json.loads((P/'manifest.json').read_text());m.update(camera_eye_m=[.05,0,1.05],camera_fov=95,camera_pitch=-22);(P/'manifest.json').write_text(json.dumps(m,indent=2))

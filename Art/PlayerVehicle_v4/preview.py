import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'));s=bpy.context.scene;s.frame_set(25)
for o in s.objects:
 if o.name.startswith('SM_V4_TieRod') or o.name.startswith('SM_V4_ChainLink'):o.hide_render=True
cam=s.camera;cam.location=(2.5,-3.2,1.9);cam.rotation_euler=(Vector((0,0,.45))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=45
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(P/'assembly_preview.png');bpy.ops.render.render(write_still=True)
print(json.dumps({o.name:{'dimensions':list(o.dimensions),'location':list(o.location)} for o in s.objects if o.name.startswith(('SK_V4','SM_V4_Chassis'))}))

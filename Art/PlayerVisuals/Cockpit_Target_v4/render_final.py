import bpy,math
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Target_v4.blend'));s=bpy.context.scene;w=bpy.data.objects['SM_CT4_SteeringWheel'];T=Matrix.Rotation(math.radians(18),4,'Y');s.cycles.samples=24;s.render.resolution_percentage=100
for name,f in [('center',25),('left',1),('right',49)]:
 s.frame_set(f);w.rotation_euler=(T@Matrix.Rotation(math.radians((f-25)/24*25),4,'X')@T.inverted()).to_euler();s.render.filepath=str(P/('final_blender_'+name+'.png'));bpy.ops.render.render(write_still=True)

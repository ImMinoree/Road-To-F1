import bpy, math, json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'FP_KartArms.blend'))
s=bpy.context.scene;rig=bpy.data.objects['FP_KartArms_Rig'];wheel=bpy.data.objects['SM_FP_SteeringWheel']
s.camera.location=(0,0,.95)
s.camera.rotation_euler=Vector((math.cos(math.radians(12)),0,-math.sin(math.radians(12)))).to_track_quat('-Z','Y').to_euler()
samples={}
for frame in [1,13,25,37,49]:
 s.frame_set(frame);bpy.context.view_layer.update()
 samples[str(frame)]={n:list(rig.matrix_world@rig.pose.bones[n].matrix.translation) for n in ['hand_l','hand_r','lowerarm_l','lowerarm_r']}
(P/'bone_samples.json').write_text(json.dumps(samples,indent=2))
for name,frame in [('center',25),('left',1),('right',49)]:
 s.frame_set(frame);wheel.rotation_euler.x=math.radians((frame-25)/24*25);s.render.filepath=str(P/('fp_'+name+'.png'));bpy.ops.render.render(write_still=True)
s.frame_set(25);wheel.rotation_euler.x=0
bpy.ops.wm.save_as_mainfile(filepath=str(P/'FP_KartArms.blend'))
r=json.loads((P/'manifest.json').read_text());r['source_camera_anchor_cm']=[0,0,95];(P/'manifest.json').write_text(json.dumps(r,indent=2))

import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P.parent/'Wheel_Visibility_v3/Kart_Cockpit_Wheel_Visibility_v3.blend'));s=bpy.context.scene;s.frame_set(25);r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_WV3_DriverPOV'];w=bpy.data.objects['SM_CV2_SteeringWheel'];rows=[]
for fov in [90,95,100]:
 for pitch in [18,20,22]:
  s.camera.data.angle=math.radians(fov);s.camera.rotation_euler=Vector((math.cos(math.radians(pitch)),0,-math.sin(math.radians(pitch)))).to_track_quat('-Z','Y').to_euler();cases=[]
  T=Matrix.Rotation(math.radians(18),4,'Y')
  for a in [-25,0,25]:
   A=T@Matrix.Rotation(math.radians(a),4,'X')@T.inverted();pr=[world_to_camera_view(s,s.camera,w.location+A@v.co) for v in w.data.vertices[:3360]];cases.append({'steering':a,'top':min(1-p.y for p in pr),'bottom':max(1-p.y for p in pr),'left':min(p.x for p in pr),'right':max(p.x for p in pr)})
  rows.append({'fov':fov,'pitch':pitch,'cases':cases})
s.camera.data.angle=math.radians(90);s.camera.rotation_euler=Vector((math.cos(math.radians(20)),0,-math.sin(math.radians(20)))).to_track_quat('-Z','Y').to_euler();s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_percentage=60;s.render.filepath=str(P/'framing_trial.png');bpy.ops.render.render(write_still=True)
report={'cameras':rows,'materials':[(i,m.name) for i,m in enumerate(o.data.materials)],'kart_materials':[m.name for m in bpy.data.objects['SM_WV3_PlayerChassis'].data.materials],'bones':{n:list((r.matrix_world@r.data.bones[n].matrix_local).translation) for n in ['hand_l','hand_r','lowerarm_l','lowerarm_r']}}
(P/'source_inspection.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)

import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'));bpy.context.scene.frame_set(25)
r=bpy.data.objects['FP_KartArms_Rig']; w=bpy.data.objects['SM_V4_SteeringWheel']
d={'rig_world':[list(x) for x in r.matrix_world],'wheel_world':[list(x) for x in w.matrix_world],'bones':{b.name:{'head':list(r.matrix_world@b.head),'tail':list(r.matrix_world@b.tail),'matrix':[list(x) for x in (r.matrix_world@b.matrix)]} for b in r.pose.bones if any(t in b.name for t in ['hand','thumb','index','middle','ring','pinky'])}}
(P/'Hands/inspect.json').write_text(json.dumps(d,indent=2))
print([(b.name,list(r.matrix_world@b.head),list(r.matrix_world@b.tail)) for b in r.pose.bones if 'index' in b.name or 'hand' in b.name])

import bpy,math,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'Cockpit_Target_v4/Leg_Fit_Candidate.blend'));s=bpy.context.scene;s.frame_set(25);k=bpy.data.objects['SM_CT4_PlayerChassis']
parts=json.loads((P/'parts.json').read_text())
for p in parts:
 if 'Nose_And_Front' in p['name']:
  for i in range(p['start'],p['end']):
   v=k.data.vertices[i];v.co.z-=.24;v.co.x+=.18
s.camera.data.angle=math.radians(85)
s.cycles.samples=12;s.render.resolution_percentage=70;s.render.filepath=str(P/'layout_test.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Layout_Test.blend'));bpy.ops.render.render(write_still=True)

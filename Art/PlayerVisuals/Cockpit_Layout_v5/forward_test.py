import bpy,math,json
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P.parent/'Cockpit_Target_v4/Leg_Fit_Candidate.blend'));s=bpy.context.scene;s.frame_set(25);k=bpy.data.objects['SM_CT4_PlayerChassis']
for p in json.loads((P/'parts.json').read_text()):
 for i in range(p['start'],p['end']):
  v=k.data.vertices[i];name=p['name']
  if 'Seat_' in name:v.co.z-=.08
  elif 'Fuel_Tank' in name or 'Driver_Controls' in name:pass
  else:v.co.x+=.35
  if 'Nose_And_Front' in name:v.co.z-=.24
s.camera.data.angle=math.radians(85);s.cycles.samples=12;s.render.resolution_percentage=70;s.render.filepath=str(P/'forward_test.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'Forward_Test.blend'));bpy.ops.render.render(write_still=True)

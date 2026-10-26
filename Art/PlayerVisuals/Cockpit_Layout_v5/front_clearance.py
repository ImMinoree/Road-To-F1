import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));k=bpy.data.objects['SM_CL5_PlayerChassis']
for p in json.loads((P/'parts.json').read_text()):
 for i in range(p['start'],p['end']):
  v=k.data.vertices[i];name=p['name']
  if 'Nose_And_Front' in name:v.co.z-=.1
  if 'Axles_Steering' in name and v.co.x>.7 and v.co.z>.24:v.co.z-=.08
  if 'Steering_Rod_End' in name:v.co.z-=.08
  if 'Engine_' in name or 'Drivetrain_' in name or 'Exhaust_' in name:v.co.x-=.35
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'))

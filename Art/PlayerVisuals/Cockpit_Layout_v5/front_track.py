import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));s=bpy.context.scene;k=bpy.data.objects['SM_CL5_PlayerChassis']
for p in json.loads((P/'parts.json').read_text()):
 if any(n in p['name'] for n in ['Wheel_FL','Wheel_FR','Axles_Steering','Front_Brake','Steering_Rod_End']):
  for i in range(p['start'],p['end']):
   v=k.data.vertices[i]
   if v.co.x>.65:v.co.y+=(.14 if v.co.y>0 else -.14)*min(1,abs(v.co.y)/.435)
s.render.filepath=str(P/'wide_front.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));bpy.ops.render.render(write_still=True)

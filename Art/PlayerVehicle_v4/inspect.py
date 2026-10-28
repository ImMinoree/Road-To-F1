import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
out={}
for label,path in [('kart','Art/DesertKarting/Kart/Kart_Reference.blend'),('pov','Art/PlayerVisuals/Cockpit_Layout_v5/Kart_Cockpit_Layout_v5.blend'),('driver','Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(P.parents[1]/path));bpy.context.scene.frame_set(25)
 out[label]=[{'name':o.name,'type':o.type,'location':list(o.location),'dimensions':list(o.dimensions),'vertices':len(o.data.vertices) if o.type=='MESH' else 0,'bones':[b.name for b in o.data.bones] if o.type=='ARMATURE' else []} for o in bpy.context.scene.objects]
(P/'inventory.json').write_text(json.dumps(out,indent=2))

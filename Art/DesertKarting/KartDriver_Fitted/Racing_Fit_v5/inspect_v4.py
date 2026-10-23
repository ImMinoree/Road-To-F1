import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P.parent/'Racing_Visual_v4/Kart_With_MakeHuman_Racer_v4.blend'))
arm=bpy.data.objects['Game_engine'];deps=bpy.context.evaluated_depsgraph_get();r={'bones':{},'objects':{}}
for b in arm.pose.bones:r['bones'][b.name]={'head':list(arm.matrix_world@b.head),'tail':list(arm.matrix_world@b.tail),'mode':b.rotation_mode,'parent':b.parent.name if b.parent else ''}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 if not (o.name.startswith(('RACER','HELMET')) or any(t in o.name for t in ['Steering','Pedal','Hose','Seat','Chassis'])):continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();v=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
 r['objects'][o.name]={'bounds':[[min(v[i] for v in v),max(v[i] for v in v)] for i in range(3)],'vertices':len(o.data.vertices),'mods':[(m.name,m.type) for m in o.modifiers]}
(P/'v4_inventory.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)

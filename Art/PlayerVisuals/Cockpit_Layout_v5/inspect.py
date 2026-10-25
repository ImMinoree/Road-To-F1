import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P.parents[2]/'Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend'))
bpy.context.scene.frame_set(25);d=bpy.context.evaluated_depsgraph_get();out=[];off=0
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('SK_Kart_') or o.name.startswith('SK_Kart_Steering_Column_And_Wheel_'):continue
 e=o.evaluated_get(d);m=e.to_mesh();ids={i for p in m.polygons for i in p.vertices};v=[o.matrix_world@m.vertices[i].co for i in ids];out.append(dict(name=o.name,start=off,end=off+len(ids),min=[min(p[a] for p in v) for a in range(3)],max=[max(p[a] for p in v) for a in range(3)]));off+=len(ids);e.to_mesh_clear()
(P/'parts.json').write_text(json.dumps(out,indent=2))

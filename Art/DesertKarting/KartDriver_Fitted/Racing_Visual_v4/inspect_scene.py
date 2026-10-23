import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'Refinement_v3/Kart_With_MakeHuman_Fitted_v3.blend'))
r={}
for n in ['kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh','high-polyMesh','Game_engine']:
 o=bpy.data.objects[n]
 r[n]={'matrix':list(map(list,o.matrix_world)),'dimensions':list(o.dimensions),'modifiers':[(m.name,m.type) for m in o.modifiers]}
 if o.type=='MESH':
  r[n].update(vertices=len(o.data.vertices),faces=len(o.data.polygons),bounds=[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)],groups=[g.name for g in o.vertex_groups],materials=[m.name if m else None for m in o.data.materials],uvs=[u.name for u in o.data.uv_layers])
arm=bpy.data.objects['Game_engine']
r['bones']={b.name:{'head':list(arm.matrix_world@b.head),'tail':list(arm.matrix_world@b.tail),'rest_head':list(b.bone.head_local),'rest_tail':list(b.bone.tail_local)} for b in arm.pose.bones}
r['lights']={o.name:{'type':o.data.type,'energy':o.data.energy,'matrix':list(map(list,o.matrix_world))} for o in bpy.context.scene.objects if o.type=='LIGHT'}
(P/'inspection.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r),flush=True)

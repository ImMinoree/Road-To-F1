import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));bpy.context.scene.frame_set(25);o=bpy.data.objects['SK_CL5_DriverPOV'];k=bpy.data.objects['SM_CL5_PlayerChassis'];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();ids={v.index for v in o.data.vertices if sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(('pelvis','thigh_','calf_','foot_','ball_')))>.5};fs=[tuple(p.vertices) for p in o.data.polygons if all(i in ids for i in p.vertices)];pairs=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],fs).overlap(BVHTree.FromPolygons([v.co for v in k.data.vertices],[tuple(p.vertices) for p in k.data.polygons]));parts=json.loads((P/'parts.json').read_text());out={}
for a,b in pairs:
 p=k.data.polygons[b];n=next((q['name'] for q in parts if q['start']<=p.vertices[0]<q['end']),'shaft');out.setdefault(n,[]).append(sum((k.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices))
print(json.dumps({n:{'min':[min(v[j] for v in vs) for j in range(3)],'max':[max(v[j] for v in vs) for j in range(3)]} for n,vs in out.items()},indent=2))

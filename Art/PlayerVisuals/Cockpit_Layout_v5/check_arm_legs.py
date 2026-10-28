import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));s=bpy.context.scene;o=bpy.data.objects['SK_CL5_DriverPOV'];d=bpy.context.evaluated_depsgraph_get();groups=[('pelvis','thigh_','calf_','foot_','ball_'),('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_')];faces=[]
for prefixes in groups:
 ids={v.index for v in o.data.vertices if sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(prefixes))>.5};faces.append([tuple(p.vertices) for p in o.data.polygons if all(i in ids for i in p.vertices)])
rows=[]
for f in [1,7,13,19,25,31,37,43,49]:
 s.frame_set(f);e=o.evaluated_get(d);m=e.to_mesh();v=[o.matrix_world@v.co for v in m.vertices];trees=[BVHTree.FromPolygons(v,fs) for fs in faces];rows.append({'frame':f,'arm_leg_triangle_pairs':len(trees[0].overlap(trees[1]))});e.to_mesh_clear()
(P/'arm_leg_checks.json').write_text(json.dumps(rows,indent=2));print(rows)

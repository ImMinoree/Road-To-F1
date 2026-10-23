import bpy, json, math, hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'FP_KartArms.blend'))
s=bpy.context.scene;o=bpy.data.objects['SK_FP_KartArms'];deps=bpy.context.evaluated_depsgraph_get()
ids=[]
for v in o.data.vertices:
 names=[o.vertex_groups[g.group].name for g in v.groups if g.weight>.01]
 if any(n.startswith(('hand_','index_','middle_','ring_','pinky_','thumb_')) for n in names):ids.append(v.index)
rows=[]
for frame in range(1,50):
 s.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(deps);me=ev.to_mesh()
 ds=[math.hypot(math.hypot(me.vertices[i].co.y,me.vertices[i].co.z-.70)-.184,me.vertices[i].co.x-.62)-.017 for i in ids]
 rows.append({'frame':frame,'minimum_glove_to_rim_signed_distance_m':min(ds),'vertices_deeper_than_3mm':sum(d<-.003 for d in ds),'vertices_within_5mm_of_rim':sum(abs(d)<.005 for d in ds)})
 ev.to_mesh_clear()
manifest=json.loads((P/'manifest.json').read_text());source=Path(manifest['source'])
r={'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256'],'hand_weighted_vertices_checked':len(ids),'method':'Evaluated glove vertices vs measured analytic wheel torus (R .184m, tube .017m), 49 poses. Vertex distances are not a watertight mesh collision proof.','poses':rows,'worst_signed_distance_m':min(a['minimum_glove_to_rim_signed_distance_m'] for a in rows),'max_vertices_deeper_than_3mm':max(a['vertices_deeper_than_3mm'] for a in rows)}
(P/'steering_geometry_checks.json').write_text(json.dumps(r,indent=2));print('FP_GEOMETRY_CHECK',r['worst_signed_distance_m'],r['max_vertices_deeper_than_3mm'],flush=True)

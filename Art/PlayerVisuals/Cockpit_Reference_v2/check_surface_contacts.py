import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Reference_v2.blend'));s=bpy.context.scene;o=bpy.data.objects['SK_CV2_DriverPOV'];kart=bpy.data.objects['SM_CV2_PlayerChassis'];deps=bpy.context.evaluated_depsgraph_get()
def weight(v,prefix):return sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(prefix))
armids={v.index for v in o.data.vertices if weight(v,('clavicle_','upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))>.5}
legids={v.index for v in o.data.vertices if weight(v,('pelvis','thigh_','calf_','foot_','ball_'))>.5}
armfaces=[tuple(p.vertices) for p in o.data.polygons if all(i in armids for i in p.vertices)];legfaces=[tuple(p.vertices) for p in o.data.polygons if all(i in legids for i in p.vertices)]
leftids={v.index for v in o.data.vertices if any(o.vertex_groups[g.group].name in ['thigh_l','calf_l','foot_l','ball_l'] and g.weight>.5 for g in v.groups)};rightids={v.index for v in o.data.vertices if any(o.vertex_groups[g.group].name in ['thigh_r','calf_r','foot_r','ball_r'] and g.weight>.5 for g in v.groups)}
leftfaces=[tuple(p.vertices) for p in o.data.polygons if all(i in leftids for i in p.vertices)];rightfaces=[tuple(p.vertices) for p in o.data.polygons if all(i in rightids for i in p.vertices)]
carttree=BVHTree.FromPolygons([kart.matrix_world@v.co for v in kart.data.vertices],[tuple(p.vertices) for p in kart.data.polygons]);rows=[]
for frame in range(1,50):
 s.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];a=BVHTree.FromPolygons(vs,armfaces);l=BVHTree.FromPolygons(vs,legfaces);al=a.overlap(l);ac=a.overlap(carttree);lc=l.overlap(carttree)
 lr=BVHTree.FromPolygons(vs,leftfaces).overlap(BVHTree.FromPolygons(vs,rightfaces))
 rows.append({'frame':frame,'arm_leg_surface_pairs':len(al),'arm_chassis_surface_pairs':len(ac),'leg_chassis_surface_pairs':len(lc),'left_right_leg_surface_pairs':len(lr),'leg_leg_sample_face_centers':[list(sum((vs[i] for i in leftfaces[p]),Vector())/len(leftfaces[p])) for p,q in lr[:5]],'arm_leg_sample_face_centers':[list(sum((vs[i] for i in armfaces[p]),Vector())/len(armfaces[p])) for p,q in al[:5]]});ev.to_mesh_clear()
(P/'surface_contacts.json').write_text(json.dumps({'method':'Evaluated triangle surface overlaps, not a signed-volume or cloth simulation test.','rows':rows},indent=2));print('CV2_SURFACE_CONTACTS_MAX',{k:max(x[k] for x in rows) for k in ['arm_leg_surface_pairs','arm_chassis_surface_pairs','leg_chassis_surface_pairs','left_right_leg_surface_pairs']},flush=True)

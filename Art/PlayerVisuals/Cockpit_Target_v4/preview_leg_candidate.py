import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;ROOT=P.parents[2];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend'));bpy.context.scene.frame_set(25);deps=bpy.context.evaluated_depsgraph_get();offset=0;pedal=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or not ob.name.startswith('SK_Kart_') or ob.name.startswith('SK_Kart_Steering_Column_And_Wheel_'):continue
 ev=ob.evaluated_get(deps);me=ev.to_mesh();n=len({v for p in me.polygons for v in p.vertices})
 if ob.name.startswith('SK_Kart_Driver_Controls_And_Pedals_'):pedal.extend(range(offset,offset+n))
 offset+=n;ev.to_mesh_clear()
bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Target_v4.blend'));s=bpy.context.scene;s.frame_set(25);r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CT4_DriverPOV'];k=bpy.data.objects['SM_CT4_PlayerChassis'];deps=bpy.context.evaluated_depsgraph_get();inv=r.matrix_world.inverted();base={b.name:r.matrix_world@b.matrix for b in r.pose.bones}
def aim(m,a,b):
 out=m.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@m;out.translation=a;return out
spine=r.pose.bones['spine_01'].matrix.copy();pel=base['pelvis'].copy();pel.translation.z-=.18;r.pose.bones['pelvis'].matrix=inv@pel;bpy.context.view_layer.update();r.pose.bones['spine_01'].matrix=spine;bpy.context.view_layer.update()
for side in ['l','r']:
 up,lo,foot=['thigh_'+side,'calf_'+side,'foot_'+side];H=(r.matrix_world@r.pose.bones[up].matrix).translation;target=base[foot].copy();target.translation.x+=.4;W=target.translation;L1=(base[lo].translation-base[up].translation).length;L2=(base[foot].translation-base[lo].translation).length;D=(W-H).normalized();d=(W-H).length;a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));pole=Vector((0,0,1));pole=(pole-D*pole.dot(D)).normalized();K=H+D*a+pole*h;r.pose.bones[up].matrix=inv@aim(base[up],H,K);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(base[lo],K,W);bpy.context.view_layer.update();r.pose.bones[foot].matrix=inv@target;bpy.context.view_layer.update()
for b in r.pose.bones:
 for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=25)
for i in pedal:k.data.vertices[i].co.x+=.4
ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];ids={v.index for v in o.data.vertices if sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(('pelvis','thigh_','calf_','foot_','ball_')))>.5};faces=[tuple(p.vertices) for p in o.data.polygons if all(i in ids for i in p.vertices)];kt=BVHTree.FromPolygons([v.co for v in k.data.vertices],[tuple(p.vertices) for p in k.data.polygons]);pairs=BVHTree.FromPolygons(vs,faces).overlap(kt);print('CANDIDATE_CHASSIS_PAIRS',len(pairs),flush=True);(P/'candidate_contacts.json').write_text(json.dumps({'surface_pairs':len(pairs),'centers':[list(sum((vs[i] for i in faces[a]),Vector())/len(faces[a])) for a,b in pairs[:20]],'pedal_vertex_indices':pedal},indent=2));ev.to_mesh_clear()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Leg_Fit_Candidate.blend'));s.cycles.samples=16;s.render.resolution_percentage=70;s.render.filepath=str(P/'leg_fit_candidate.png');bpy.ops.render.render(write_still=True)

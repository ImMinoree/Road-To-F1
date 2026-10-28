import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CL5_DriverPOV'];inv=r.matrix_world.inverted();d=bpy.context.evaluated_depsgraph_get();faces=[]
for prefixes in [('thigh_','calf_','foot_','ball_'),('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_')]:
 ids={v.index for v in o.data.vertices if sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(prefixes))>.5};faces.append([tuple(p.vertices) for p in o.data.polygons if all(i in ids for i in p.vertices)])
def aim(m,a,b):
 out=m.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@m;out.translation=a;return out
rows=[]
for down,polein in [(0,.3),(.03,.2),(.05,.2),(.05,.4)]:
 counts=[]
 for f in [1,49]:
  s.frame_set(f);base={b.name:r.matrix_world@b.matrix for b in r.pose.bones};sp=base['spine_01'].copy();m=base['pelvis'].copy();m.translation.z-=down;r.pose.bones['pelvis'].matrix=inv@m;bpy.context.view_layer.update();r.pose.bones['spine_01'].matrix=inv@sp;bpy.context.view_layer.update()
  for side in ['l','r']:
   up,lo,end=['thigh_'+side,'calf_'+side,'foot_'+side];H=(r.matrix_world@r.pose.bones[up].matrix).translation;target=base[end];W=target.translation;L1=(base[lo].translation-base[up].translation).length;L2=(base[end].translation-base[lo].translation).length;D=(W-H).normalized();dist=(W-H).length;a=(L1*L1-L2*L2+dist*dist)/(2*dist);h=math.sqrt(max(0,L1*L1-a*a));pole=Vector((0,-polein if side=='l' else polein,1));pole=(pole-D*pole.dot(D)).normalized();K=H+D*a+pole*h;r.pose.bones[up].matrix=inv@aim(base[up],H,K);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(base[lo],K,W);bpy.context.view_layer.update();r.pose.bones[end].matrix=inv@target;bpy.context.view_layer.update()
  e=o.evaluated_get(d);me=e.to_mesh();v=[o.matrix_world@v.co for v in me.vertices];trees=[BVHTree.FromPolygons(v,fs) for fs in faces];counts.append(len(trees[0].overlap(trees[1])));e.to_mesh_clear()
 rows.append({'pelvis_down':down,'inward_pole':polein,'contacts':counts});print(rows[-1],flush=True)
(P/'knee_clearance_trials.json').write_text(json.dumps(rows,indent=2))

import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Reference_v2.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CV2_DriverPOV'];deps=bpy.context.evaluated_depsgraph_get();inv=r.matrix_world.inverted();s.frame_set(25);base={b.name:r.matrix_world@b.matrix.copy() for b in r.pose.bones}
def weight(v,prefix):return sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(prefix))
armids={v.index for v in o.data.vertices if weight(v,('clavicle_','upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))>.5};legids={v.index for v in o.data.vertices if weight(v,('pelvis','thigh_','calf_','foot_','ball_'))>.5};af=[tuple(p.vertices) for p in o.data.polygons if all(i in armids for i in p.vertices)];lf=[tuple(p.vertices) for p in o.data.polygons if all(i in legids for i in p.vertices)]
def aim(mat,a,b):
 q=mat.to_3x3().col[1].normalized().rotation_difference((b-a).normalized());m=q.to_matrix().to_4x4()@mat;m.translation=a;return m
for v in o.data.vertices:
 if v.index not in legids:continue
 side='l' if v.co.y>0 else 'r';K=base['calf_'+side].translation;d=v.co-K;w=math.exp(-((d.length/.16)**4));v.co.y-=d.y*.25*w
out=[]
for deg in [-18,-20,-21,-22,-23]:
 row={'degrees':deg,'frames':[]}
 for frame in [1,25,49]:
  s.frame_set(frame);bpy.context.view_layer.update();knees=[]
  for side,sign in [('l',1),('r',-1)]:
   up='thigh_'+side;lo='calf_'+side;foot='foot_'+side;H=base[up].translation;K=base[lo].translation;W=base[foot].translation;D=(W-H).normalized();pivot=H+D*(K-H).dot(D);A=Matrix.Rotation(math.radians(deg),4,D);k1=pivot+A.to_3x3()@(K-pivot)
   if (k1.y-K.y)*sign*(1 if deg>0 else -1)<0:A=Matrix.Rotation(-math.radians(deg),4,D);k1=pivot+A.to_3x3()@(K-pivot)
   r.pose.bones[up].matrix=inv@aim(base[up],H,k1);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(base[lo],k1,W);bpy.context.view_layer.update();r.pose.bones[foot].matrix=inv@base[foot];bpy.context.view_layer.update();knees.append(list(k1))
  ev=o.evaluated_get(deps);me=ev.to_mesh();v=[o.matrix_world@v.co for v in me.vertices];a=BVHTree.FromPolygons(v,af);l=BVHTree.FromPolygons(v,lf);row['frames'].append({'frame':frame,'arm_leg_pairs':len(a.overlap(l)),'knees':knees});ev.to_mesh_clear()
 out.append(row)
(P/'knee_fit_trials.json').write_text(json.dumps(out,indent=2));print('KNEE_TRIALS',out,flush=True)

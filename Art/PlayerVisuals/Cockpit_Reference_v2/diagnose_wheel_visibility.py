"""Read-only camera/mesh/occlusion diagnosis and pose trials. Never saves the source scene."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;OUT=P.parent/'Wheel_Visibility_v3';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Reference_v2.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CV2_DriverPOV'];w=bpy.data.objects['SM_CV2_SteeringWheel'];kart=bpy.data.objects['SM_CV2_PlayerChassis'];deps=bpy.context.evaluated_depsgraph_get();inv=r.matrix_world.inverted();base={b.name:r.matrix_world@b.matrix_local for b in r.data.bones};T=Matrix.Rotation(math.radians(18),4,'Y');C=w.location.copy();eye=s.camera.location.copy()
def weight(v,prefix):return sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(prefix))
armids={v.index for v in o.data.vertices if weight(v,('clavicle_','upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))>.5};legids={v.index for v in o.data.vertices if weight(v,('pelvis','thigh_','calf_','foot_','ball_'))>.5};af=[tuple(p.vertices) for p in o.data.polygons if all(i in armids for i in p.vertices)];lf=[tuple(p.vertices) for p in o.data.polygons if all(i in legids for i in p.vertices)]
karttree=BVHTree.FromPolygons([kart.matrix_world@v.co for v in kart.data.vertices],[tuple(p.vertices) for p in kart.data.polygons])
def aim(mat,a,b):
 m=mat.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@mat;m.translation=a;return m
def setlegs(deg):
 for side,sign in [('l',1),('r',-1)]:
  up='thigh_'+side;lo='calf_'+side;foot='foot_'+side;H=base[up].translation;K=base[lo].translation;W=base[foot].translation;D=(W-H).normalized();pivot=H+D*(K-H).dot(D);R=Matrix.Rotation(math.radians(abs(deg)),4,D);newK=pivot+R.to_3x3()@(K-pivot)
  if (newK.y-K.y)*sign*(1 if deg>=0 else -1)<0:R=Matrix.Rotation(-math.radians(abs(deg)),4,D);newK=pivot+R.to_3x3()@(K-pivot)
  r.pose.bones[up].matrix=inv@aim(base[up],H,newK);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(base[lo],newK,W);bpy.context.view_layer.update();r.pose.bones[foot].matrix=inv@base[foot];bpy.context.view_layer.update()
rows=[]
for deg in [-21,-10,0,10,15,20,25,30,35]:
 for frame in [1,25,49]:
  s.frame_set(frame);setlegs(deg);ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];arm=BVHTree.FromPolygons(vs,af);leg=BVHTree.FromPolygons(vs,lf);A=T@Matrix.Rotation(math.radians((frame-25)/24*25),4,'X')@T.inverted();rim=[C+A@v.co for v in w.data.vertices[:3360]];proj=[world_to_camera_view(s,s.camera,p) for p in rim];masked=0;masked_leg=0;masked_chassis=0;lower=0;hiddenpts=[]
  for i in range(168):
   section=rim[i*20:(i+1)*20];p=min(section,key=lambda p:(p-eye).length);local=T.inverted()@(sum(section,Vector())/20-C)
   if local.z>-.08:continue
   lower+=1;d=(p-eye).length;direction=(p-eye).normalized();lh=leg.ray_cast(eye,direction,d-.001);ah=arm.ray_cast(eye,direction,d-.001);ch=karttree.ray_cast(eye,direction,d-.001)
   masked_leg+=lh[0] is not None;masked_chassis+=ch[0] is not None
   if lh[0] is not None or ah[0] is not None or ch[0] is not None:masked+=1;hiddenpts.append(tuple(p))
  fovs={}
  for fov in [105,107,110]:
   s.camera.data.angle=math.radians(fov);pr=[world_to_camera_view(s,s.camera,p) for p in rim];fovs[str(fov)]={'top':min(1-p.y for p in pr),'bottom':max(1-p.y for p in pr),'out_of_frame_vertices':sum(p.y<0 or p.y>1 or p.x<0 or p.x>1 for p in pr)}
  s.camera.data.angle=math.radians(105)
  rows.append({'knee_angle_from_source_deg':deg,'frame':frame,'lower_rim_sections':lower,'lower_rim_masked':masked,'masked_by_legs':masked_leg,'masked_by_chassis':masked_chassis,'arm_leg_surface_pairs':len(arm.overlap(leg)),'leg_chassis_surface_pairs':len(leg.overlap(karttree)),'min_rim_camera_depth_m':min(p.z for p in proj),'framing':fovs});ev.to_mesh_clear()
# Validate closed rim topology independently of other wheel details.
edges={}
for p in w.data.polygons:
 if all(i<3360 for i in p.vertices):
  for e in p.edge_keys:e=tuple(sorted(e));edges[e]=edges.get(e,0)+1
result={'rim_vertices':3360,'rim_boundary_or_nonmanifold_edges':sum(n!=2 for n in edges.values()),'near_plane_comparison':'Camera depth is in meters. Compare to runtime near clip; the wheel is roughly 0.6m in front of the eye, not on the near plane.','trials':rows}
(OUT/'diagnosis.json').write_text(json.dumps(result,indent=2));print('WHEEL_TRIALS',[(a['knee_angle_from_source_deg'],a['frame'],a['lower_rim_masked'],a['arm_leg_surface_pairs'],round(a['framing']['105']['bottom'],4)) for a in rows],flush=True)

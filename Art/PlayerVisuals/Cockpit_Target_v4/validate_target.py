import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Target_v4.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CT4_DriverPOV'];w=bpy.data.objects['SM_CT4_SteeringWheel'];deps=bpy.context.evaluated_depsgraph_get();T=Matrix.Rotation(math.radians(18),4,'Y');C=w.location.copy();eye=s.camera.location.copy();legids={v.index for v in o.data.vertices if sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(('pelvis','thigh_','calf_','foot_','ball_')))>.5};lf=[tuple(p.vertices) for p in o.data.polygons if all(i in legids for i in p.vertices)];rows=[];bone_samples=[]
for f in range(1,50):
 s.frame_set(f);bpy.context.view_layer.update();A=T@Matrix.Rotation(math.radians((f-25)/24*25),4,'X')@T.inverted();rim=[C+A@v.co for v in w.data.vertices[:3360]];pr=[world_to_camera_view(s,s.camera,p) for p in rim];row={'frame':f,'out_of_frame_rim_vertices':sum(p.x<0 or p.x>1 or p.y<0 or p.y>1 for p in pr),'top_fraction':min(1-p.y for p in pr),'bottom_fraction':max(1-p.y for p in pr),'minimum_rim_camera_depth_m':min(p.z for p in pr)}
 if f in [1,7,13,19,25,31,37,43,49]:
  ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];leg=BVHTree.FromPolygons(vs,lf);hidden=0
  for i in range(168):
   section=rim[i*20:(i+1)*20];p=min(section,key=lambda p:(p-eye).length);local=T.inverted()@(sum(section,Vector())/20-C)
   if local.z<-.08 and leg.ray_cast(eye,(p-eye).normalized(),(p-eye).length-.001)[0] is not None:hidden+=1
  row['lower_rim_occluded_by_legs']=hidden;ev.to_mesh_clear()
 if f in [1,13,25,37,49]:bone_samples.append({'frame':f,'bones':{n:list((r.matrix_world@r.pose.bones[n].matrix).translation) for n in ['hand_l','hand_r','calf_l','calf_r','foot_l','foot_r']}})
 rows.append(row)
edges={}
for p in w.data.polygons:
 if all(i<3360 for i in p.vertices):
  for e in p.edge_keys:e=tuple(sorted(e));edges[e]=edges.get(e,0)+1
out={'rim_nonmanifold_edges':sum(n!=2 for n in edges.values()),'projection_frames':rows,'bone_samples':bone_samples,'limits':'Rim framing all 49 frames; knee line-of-sight sampled at 9 steering poses. Not a full-body penetration or cloth-simulation certification.'};(P/'validation.json').write_text(json.dumps(out,indent=2));print('CT4_VALIDATE',out['rim_nonmanifold_edges'],max(x['out_of_frame_rim_vertices'] for x in rows),max(x.get('lower_rim_occluded_by_legs',0) for x in rows),flush=True)

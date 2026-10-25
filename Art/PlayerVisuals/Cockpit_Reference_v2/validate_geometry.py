import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix,kdtree
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Reference_v2.blend'))
s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CV2_DriverPOV'];wheel=bpy.data.objects['SM_CV2_SteeringWheel'];deps=bpy.context.evaluated_depsgraph_get();manifest=json.loads((P/'manifest.json').read_text());C=Vector(manifest['wheel_center_m']);T=Matrix.Rotation(math.radians(18),4,'Y')
controls=[(-.080,.143),(0,.148),(.080,.143),(.124,.110),(.148,.040),(.146,-.047),(.112,-.120),(.067,-.143),(0,-.147),(-.067,-.143),(-.112,-.120),(-.146,-.047),(-.148,.040),(-.124,.110)]
path=[];N=len(controls)
for i in range(N):
 p0,p1,p2,p3=[Vector(controls[j%N]) for j in [i-1,i,i+1,i+2]]
 for k in range(64):
  t=k/64;v=.5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t);path.append(Vector((0,v.x,v.y)))
tree=kdtree.KDTree(len(path))
for i,p in enumerate(path):tree.insert(p,i)
tree.balance();ids=[v.index for v in o.data.vertices if any(o.vertex_groups[g.group].name.startswith(('hand_','index_','middle_','ring_','pinky_','thumb_')) and g.weight>.01 for g in v.groups)]
rows=[];bones={};bounds={}
for frame in range(1,50):
 s.frame_set(frame);bpy.context.view_layer.update();A=T@Matrix.Rotation(math.radians((frame-25)/24*25),4,'X');inv=A.inverted();ev=o.evaluated_get(deps);me=ev.to_mesh();dist=[];byhand={-1:[],1:[]}
 for i in ids:
  p=inv@(o.matrix_world@me.vertices[i].co-C);d=tree.find(p)[2]-.017;dist.append(d);byhand[1 if p.y>0 else -1].append(d)
 rows.append({'frame':frame,'min_signed_glove_to_grip_m':min(dist),'vertices_deeper_than_3mm':sum(d<-.003 for d in dist),'left_closest_m':min(byhand[1]),'right_closest_m':min(byhand[-1])})
 if frame in [1,13,25,37,49]:bones[str(frame)]={n:[round(v*100,6) for v in (r.matrix_world@r.pose.bones[n].matrix).translation] for n in ['hand_l','hand_r','calf_l','calf_r','foot_l','foot_r']}
 if frame in [1,25,49]:
  verts=[o.matrix_world@v.co for v in me.vertices];verts += [C+A@T.inverted()@v.co for v in wheel.data.vertices];projections=[world_to_camera_view(s,s.camera,p) for p in verts];inframe=[p for p in projections if p.z>0 and 0<=p.x<=1 and 0<=p.y<=1];bounds[str(frame)]={'top_of_driver_or_wheel_fraction':min(1-p.y for p in inframe),'bottom_fraction':max(1-p.y for p in inframe)}
 ev.to_mesh_clear()
result={'method':'49 evaluated poses. Glove vertices compared to densely sampled contoured grip centerline minus 17mm tube radius; not a full triangle/volume collision proof.','hand_vertices':len(ids),'worst_signed_clearance_m':min(x['min_signed_glove_to_grip_m'] for x in rows),'maximum_vertices_deeper_than_3mm':max(x['vertices_deeper_than_3mm'] for x in rows),'projected_driver_wheel_bounds':bounds,'poses':rows,'source_bone_samples_cm':bones}
(P/'geometry_validation.json').write_text(json.dumps(result,indent=2));print('CV2_GEOMETRY',result['worst_signed_clearance_m'],result['maximum_vertices_deeper_than_3mm'],bounds,flush=True)

import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;source=P.parent/'Cockpit_Reference_v2/diagnose_wheel_visibility.py';q={'__file__':str(source)};exec(compile(source.read_text().split('rows=[]')[0],str(source),'exec'),q)
# Retain read-only V2 helper classifications, then inspect the saved revision itself.
bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Wheel_Visibility_v3.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_WV3_DriverPOV'];w=bpy.data.objects['SM_CV2_SteeringWheel'];deps=bpy.context.evaluated_depsgraph_get();T,C,eye=q['T'],q['C'],s.camera.location.copy();rows=[];bones=[]
kart=bpy.data.objects['SM_WV3_PlayerChassis'];q['karttree']=BVHTree.FromPolygons([kart.matrix_world@v.co for v in kart.data.vertices],[tuple(p.vertices) for p in kart.data.polygons])
for f in range(1,50):
 s.frame_set(f);bpy.context.view_layer.update();ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];leg=BVHTree.FromPolygons(vs,q['lf']);arm=BVHTree.FromPolygons(vs,q['af']);A=T@Matrix.Rotation(math.radians((f-25)/24*25),4,'X')@T.inverted();wv=[C+A@v.co for v in w.data.vertices];rim=wv[:3360];hidden=0
 for i in range(168):
  section=rim[i*20:(i+1)*20];p=min(section,key=lambda p:(p-eye).length);local=T.inverted()@(sum(section,Vector())/20-C)
  if local.z<-.08 and leg.ray_cast(eye,(p-eye).normalized(),(p-eye).length-.001)[0] is not None:hidden+=1
 pr=[world_to_camera_view(s,s.camera,p) for p in rim];wheel=BVHTree.FromPolygons(wv,[tuple(p.vertices) for p in w.data.polygons]);rows.append({'frame':f,'lower_rim_hidden_by_legs':hidden,'out_of_frame_rim_vertices':sum(p.x<0 or p.x>1 or p.y<0 or p.y>1 for p in pr),'rim_top_fraction':min(1-p.y for p in pr),'rim_bottom_fraction':max(1-p.y for p in pr),'min_camera_depth_m':min(p.z for p in pr),'wheel_leg_surface_pairs':len(wheel.overlap(leg)),'arm_leg_surface_pairs':len(arm.overlap(leg)),'leg_chassis_surface_pairs':len(leg.overlap(q['karttree']))})
 if f in [1,13,25,37,49]:bones.append({'frame':f,'bones':{n:list((r.matrix_world@r.pose.bones[n].matrix).translation) for n in ['hand_l','hand_r','calf_l','calf_r','foot_l','foot_r']}})
 ev.to_mesh_clear()
report={'method':'All 49 baked frames, actual deformed surfaces and lower-rim line-of-sight probes; triangle overlap counts are not penetration depths.','rows':rows,'bone_samples':bones,'limits':{'field_of_view':110,'wheel_geometry':'unchanged','knee_bend_plane_degrees_from_original_rest':42,'unchanged':'hips, feet, hand matrices, segment lengths, skin weights, materials, kart geometry'},'remaining_contact':'Offscreen outer clothing contacts with inherited seat/chassis remain. Not a full-body fit certification.'};(P/'validation.json').write_text(json.dumps(report,indent=2));print('WV3_MAX', {k:max(row[k] for row in rows) for k in ['lower_rim_hidden_by_legs','out_of_frame_rim_vertices','wheel_leg_surface_pairs','arm_leg_surface_pairs','leg_chassis_surface_pairs']},flush=True)

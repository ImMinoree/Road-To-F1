import bpy,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;F=P/'Kart_With_MakeHuman_Racer_v5.blend';bpy.ops.wm.open_mainfile(filepath=str(F));scene=bpy.context.scene;arm=bpy.data.objects['Game_engine'];ctrl=bpy.data.objects['V5 | STEERING - degrees'];deps=bpy.context.evaluated_depsgraph_get();glove=bpy.data.objects['RACER | anatomical five-finger gloves'];body=bpy.data.objects['kart_driverMesh']
# Match actual render subdivision levels for every geometric check.
for o in scene.objects:
 for m in o.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels
def digest(x):return hashlib.sha256(repr(x).encode()).hexdigest()
pres=json.loads((P/'preservation.json').read_text());old=pres['before']
current={'kart':{o.name:digest((list(map(list,o.matrix_world)),[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])) for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')},'weights':{o.name:digest(([g.name for g in o.vertex_groups],[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices])) for o in scene.objects if o.type=='MESH' and (o.name.startswith(('RACER |','HELMET |')) or o.name=='kart_driverMesh')},'rig':digest([(b.name,b.parent.name if b.parent else '',list(map(list,b.matrix_local))) for b in arm.data.bones]),'lights':{o.name:digest((list(map(list,o.matrix_world)),o.data.energy,tuple(o.data.color))) for o in scene.objects if o.type=='LIGHT'},'body_geometry':digest([tuple(v.co) for v in body.data.vertices])}
assert current==old,'Protected source geometry, bindings, rest skeleton or lights changed'
def geom(o,groups=False):
 ev=o.evaluated_get(deps);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(p.vertices) for p in me.polygons];gs=[[(o.vertex_groups[g.group].name,g.weight) for g in p.groups] for p in me.vertices] if groups else None;ev.to_mesh_clear();return v,f,gs
def tree(o):v,f,_=geom(o);return BVHTree.FromPolygons(v,f)
def head(n):return arm.matrix_world@arm.pose.bones[n].head
bn=['upperarm_l','lowerarm_l','upperarm_r','lowerarm_r'];rest={n:(arm.matrix_world.to_3x3()@(arm.data.bones[n].tail_local-arm.data.bones[n].head_local)).length for n in bn}
samples=[];external={};helm={};outfit=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith(('RACER |','HELMET |')) or o==body)]
for frame in range(1,50):
 scene.frame_set(frame);bpy.context.view_layer.update();v,f,_=geom(glove);a=np.array(v);r=np.sqrt(a[:,1]**2+(a[:,2]-.70)**2);sdf=np.sqrt((a[:,0]-.62)**2+(r-.184)**2)-.017;wt=tree(bpy.data.objects['SK_Kart_Steering_Column_And_Wheel_Rubber_Grip']);bv,bf,_=geom(body);hands={}
 for s,sign in [('l',1),('r',-1)]:
  ss=sdf[a[:,1]*sign>0];q=np.sort(abs(ss));target=bpy.data.objects['V5 | wrist IK '+s];A=head('upperarm_'+s);B=head('lowerarm_'+s);C=head('hand_'+s);actual=(arm.matrix_world@arm.pose.bones['hand_'+s].matrix).to_quaternion();desired=target.matrix_world.to_quaternion()
  hands[s]={'wrist_error_m':(C-target.matrix_world.translation).length,'orientation_error_deg':math.degrees(actual.rotation_difference(desired).angle),'elbow_flex_deg':180-math.degrees((A-B).angle(C-B)),'closest_surface_gap_m':float(min(q)),'closest_2p5_percent_mean_gap_m':float(np.mean(q[:max(1,len(q)//40)])),'glove_max_torus_penetration_m':max(0,-float(min(ss))),'evaluated_points_within_3mm':int(sum(q<.003))}
 sample={'frame':frame,'steering_deg':ctrl['steering_deg'],'hands':hands,'glove_wheel_triangle_pairs':len(BVHTree.FromPolygons(v,f).overlap(wt)),'skin_wheel_triangle_pairs':len(BVHTree.FromPolygons(bv,bf).overlap(wt)),'max_arm_length_delta_m':max(abs((arm.matrix_world.to_3x3()@(arm.pose.bones[n].tail-arm.pose.bones[n].head)).length-rest[n]) for n in bn)};samples.append(sample)
 if frame in [1,25,49]:
  cart={o.name:tree(o) for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')};contacts={};bodytree=BVHTree.FromPolygons(bv,bf);helmet={}
  for o in outfit:
   ot=tree(o);h={n:len(ot.overlap(bt)) for n,bt in cart.items() if ot.overlap(bt)}
   if h:contacts[o.name]=h
   if o.name.startswith('HELMET |'):
    pairs=ot.overlap(bodytree)
    if pairs:helmet[o.name]=len(pairs)
  external[str(frame)]=contacts;helm[str(frame)]=helmet
summary={'tested_degrees':[-25,25],'samples':49,'maximum_wrist_target_error_m':max(h['wrist_error_m'] for s in samples for h in s['hands'].values()),'maximum_arm_length_delta_m':max(s['max_arm_length_delta_m'] for s in samples),'minimum_elbow_flex_deg':min(h['elbow_flex_deg'] for s in samples for h in s['hands'].values()),'maximum_glove_penetration_m':max(h['glove_max_torus_penetration_m'] for s in samples for h in s['hands'].values()),'maximum_nearest_hand_gap_m':max(h['closest_surface_gap_m'] for s in samples for h in s['hands'].values()),'maximum_glove_wheel_triangle_pairs':max(s['glove_wheel_triangle_pairs'] for s in samples),'maximum_skin_wheel_triangle_pairs':max(s['skin_wheel_triangle_pairs'] for s in samples),'minimum_points_near_rim_per_hand':min(h['evaluated_points_within_3mm'] for s in samples for h in s['hands'].values())}
gate=(summary['maximum_wrist_target_error_m']<.0005 and summary['maximum_arm_length_delta_m']<.0001 and summary['minimum_elbow_flex_deg']>15 and summary['maximum_glove_penetration_m']<.001 and summary['maximum_nearest_hand_gap_m']<.003 and summary['maximum_glove_wheel_triangle_pairs']==0 and summary['maximum_skin_wheel_triangle_pairs']==0)
scene.frame_set(25);bpy.context.view_layer.update();boots=tree(bpy.data.objects['RACER | sculpted racing boots']);pedal={str(s):min(boots.find_nearest(Vector((x,s*y,.170)))[3] for x in [.42,.44,.46,.48,.5,.52] for y in [.13,.15,.17,.19]) for s in [-1,1]}
report={'source_v4_unchanged':hashlib.sha256(Path(pres['source']).read_bytes()).hexdigest()==pres['source_sha256'],'all_protected_signatures_match_v4':current==old,'summary':summary,'steering_geometric_gate_passed':gate,'visual_steering_review':'Pending actual rendered inspection','samples':samples,'full_render_resolution_kart_intersections_at_left_center_right':external,'existing_helmet_body_surface_contacts':helm,'sampled_pedal_gap_m':pedal,'limitations':['The tested range is +/-25 degrees of the original steering wheel, not the kart mechanical lock or vehicle handling.','BVH surface-pair tests and analytic wheel clearance are diagnostics, not a physical contact simulation or a volumetric collision certificate.','V4 helmet/neck padding contacts and imperfect full-back seat support are retained; the source gear construction/realism is not upgraded.','The original wheel meshes articulate using non-destructive Hook modifiers; the chassis, tank, seat, pedals, steering shaft and front wheels are otherwise fixed.']}
(P/'validation_final.json').write_text(json.dumps(report,indent=2));print('FINAL_GEOMETRY',json.dumps(summary),'GATE',gate,'EXTERNAL',external,flush=True)
# A new close camera helps assess real fingers/rim contact; source lighting is untouched.
cam=bpy.data.objects.get('V5 | grip inspection')
if cam is None:
 data=bpy.data.cameras.new('V5 | grip inspection');cam=bpy.data.objects.new('V5 | grip inspection',data);scene.collection.objects.link(cam)
cam.location=(2.2,0,1.08);target=Vector((.53,0,.73));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.83
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=960;scene.render.resolution_percentage=100;scene.camera=bpy.data.objects['Refinement | three quarter'];scene['V5 validation']='Geometry sweep complete: '+str(gate)+'. Range +/-25 degrees. See validation_final.json and rendered grip inspections.'
bpy.ops.wm.save_as_mainfile(filepath=str(F))
jobs=[('steering_center',25,'Refinement | front'),('steering_left',1,'Refinement | front'),('steering_right',49,'Refinement | front'),('side',25,'Refinement | side'),('three_quarter',25,'Refinement | three quarter'),('grip_center',25,cam.name),('grip_left',1,cam.name),('grip_right',49,cam.name)]
for name,frame,camera in jobs:
 scene.frame_set(frame);scene.camera=bpy.data.objects[camera];scene.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
print('V5_RENDER_COMPLETE',flush=True)

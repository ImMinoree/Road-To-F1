import bpy,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_With_MakeHuman_Racer_v5.blend'));scene=bpy.context.scene;arm=bpy.data.objects['Game_engine'];ctrl=bpy.data.objects['V5 | STEERING - degrees'];deps=bpy.context.evaluated_depsgraph_get()
def geom(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return v,f
def tree(o):return BVHTree.FromPolygons(*geom(o))
def head(n):return arm.matrix_world@arm.pose.bones[n].head
def length(n):b=arm.pose.bones[n];return (arm.matrix_world.to_3x3()@(b.tail-b.head)).length
restlen={n:(arm.matrix_world.to_3x3()@(arm.data.bones[n].tail_local-arm.data.bones[n].head_local)).length for n in ['upperarm_l','lowerarm_l','upperarm_r','lowerarm_r']}
arms=[]
for frame in range(1,50,2):
 scene.frame_set(frame);bpy.context.view_layer.update();gv,gf=geom(bpy.data.objects['RACER | anatomical five-finger gloves']);hv,hf=geom(bpy.data.objects['kart_driverMesh']);wt=tree(bpy.data.objects['SK_Kart_Steering_Column_And_Wheel_Rubber_Grip']);a=np.array(gv);r=np.sqrt(a[:,1]**2+(a[:,2]-.7)**2);sdf=np.sqrt((a[:,0]-.62)**2+(r-.184)**2)-.017
 stats={}
 for s,sgn in [('l',1),('r',-1)]:
  sel=sdf[a[:,1]*sgn>0];closest=np.sort(abs(sel))[:max(1,len(sel)//40)];target=bpy.data.objects['V5 | wrist IK '+s];A=head('upperarm_'+s);B=head('lowerarm_'+s);C=head('hand_'+s)
  stats[s]={'wrist':list(C),'target':list(target.matrix_world.translation),'target_error_m':(C-target.matrix_world.translation).length,'elbow_flex_deg':180-math.degrees((A-B).angle(C-B)),'glove_max_penetration_m':max(0,-float(min(sel))),'closest_2p5_percent_gap_m':float(np.mean(closest))}
 arms.append({'frame':frame,'angle':ctrl['steering_deg'],'rotation_actual_deg':math.degrees(ctrl.rotation_euler.x),'hands':stats,'glove_wheel_triangle_pairs':len(BVHTree.FromPolygons(gv,gf).overlap(wt)),'skin_wheel_triangle_pairs':len(BVHTree.FromPolygons(hv,hf).overlap(wt)),'max_arm_length_delta_m':max(abs(length(n)-l) for n,l in restlen.items())})
scene.frame_set(25);bpy.context.view_layer.update();cart={o.name:tree(o) for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')};contacts={};bounds={}
for o in scene.objects:
 if o.type!='MESH' or o.hide_render or not(o.name.startswith(('RACER |','HELMET |')) or o.name=='kart_driverMesh'):continue
 v,f=geom(o);t=BVHTree.FromPolygons(v,f);hits={n:len(t.overlap(bt)) for n,bt in cart.items() if t.overlap(bt)}
 if hits:contacts[o.name]=hits
 # Record actual contact regions to distinguish hem/rib/boot errors from general overlap counts.
 for n in hits:
  pairs=t.overlap(cart[n]);ids=set(i for a,b in pairs for i in f[a]);pts=[v[i] for i in ids];bounds[o.name+' :: '+n]=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
boots=tree(bpy.data.objects['RACER | sculpted racing boots']);gap={str(s):min(boots.find_nearest(Vector((x,s*y,.170)))[3] for x in [.42,.44,.46,.48,.5,.52] for y in [.13,.15,.17,.19]) for s in [-1,1]}
r={'steering_samples':arms,'center_contacts':contacts,'contact_regions':bounds,'pedal_contact_gap_m':gap};(P/'v5_checks.json').write_text(json.dumps(r,indent=2));print('V5_CHECKS',json.dumps({'samples':len(arms),'max_target_error':max(h['target_error_m'] for a in arms for h in a['hands'].values()),'max_stretch':max(a['max_arm_length_delta_m'] for a in arms),'max_glove_pairs':max(a['glove_wheel_triangle_pairs'] for a in arms),'max_skin_pairs':max(a['skin_wheel_triangle_pairs'] for a in arms),'worst_penetration':max(h['glove_max_penetration_m'] for a in arms for h in a['hands'].values()),'min_elbowflex':min(h['elbow_flex_deg'] for a in arms for h in a['hands'].values()),'center_contacts':contacts,'pedal_gap':gap}),flush=True)

import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Target_v4.blend'));s=bpy.context.scene;s.frame_set(25);r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CT4_DriverPOV'];w=bpy.data.objects['SM_CT4_SteeringWheel'];deps=bpy.context.evaluated_depsgraph_get();inv=r.matrix_world.inverted();T=Matrix.Rotation(math.radians(18),4,'Y');C=w.location.copy();eye=s.camera.location.copy();base={b.name:r.matrix_world@b.matrix for b in r.pose.bones}
def weight(v,p):return sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(p))
lid={v.index for v in o.data.vertices if weight(v,('pelvis','thigh_','calf_','foot_','ball_'))>.5};aid={v.index for v in o.data.vertices if weight(v,('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))>.5};lf=[tuple(p.vertices) for p in o.data.polygons if all(i in lid for i in p.vertices)];af=[tuple(p.vertices) for p in o.data.polygons if all(i in aid for i in p.vertices)]
def aim(m,a,b):
 out=m.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@m;out.translation=a;return out
kart=bpy.data.objects['SM_CT4_PlayerChassis'];kv=[v.co.copy() for v in kart.data.vertices];kf=[tuple(p.vertices) for p in kart.data.polygons];pedal=set(json.loads((P/'candidate_contacts.json').read_text())['pedal_vertex_indices']);rows=[]
for down in [.18,.21,.24]:
 for forward in [.4,.46,.5]:
  for spread in [0,.2,.4]:
   s.frame_set(25);bpy.context.view_layer.update();spine=r.pose.bones['spine_01'].matrix.copy();pel=base['pelvis'].copy();pel.translation.z-=down;r.pose.bones['pelvis'].matrix=inv@pel;bpy.context.view_layer.update();r.pose.bones['spine_01'].matrix=spine;bpy.context.view_layer.update();knees=[]
   for side,sign in [('l',1),('r',-1)]:
    up,lo,foot=['thigh_'+side,'calf_'+side,'foot_'+side];H=(r.matrix_world@r.pose.bones[up].matrix).translation;target=base[foot].copy();target.translation.x+=forward;W=target.translation;L1=(base[lo].translation-base[up].translation).length;L2=(base[foot].translation-base[lo].translation).length;D=(W-H).normalized();d=(W-H).length;a=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-a*a));pole=Vector((0,sign*spread,1));pole=(pole-D*pole.dot(D)).normalized();K=H+D*a+pole*h;r.pose.bones[up].matrix=inv@aim(base[up],H,K);bpy.context.view_layer.update();r.pose.bones[lo].matrix=inv@aim(base[lo],K,W);bpy.context.view_layer.update();r.pose.bones[foot].matrix=inv@target;bpy.context.view_layer.update();knees.append(list(K))
   ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];leg=BVHTree.FromPolygons(vs,lf);arm=BVHTree.FromPolygons(vs,af);samples=[]
   for angle in [-25,0,25]:
    A=T@Matrix.Rotation(math.radians(angle),4,'X')@T.inverted();wv=[C+A@v.co for v in w.data.vertices];rim=wv[:3360];hidden=0
    for i in range(168):
     section=rim[i*20:(i+1)*20];p=min(section,key=lambda p:(p-eye).length);local=T.inverted()@(sum(section,Vector())/20-C)
     if local.z<-.08 and leg.ray_cast(eye,(p-eye).normalized(),(p-eye).length-.001)[0] is not None:hidden+=1
    wt=BVHTree.FromPolygons(wv,[tuple(p.vertices) for p in w.data.polygons]);samples.append({'angle':angle,'hidden':hidden,'wheel_leg':len(wt.overlap(leg))})
   kt=BVHTree.FromPolygons([p+Vector((forward,0,0)) if i in pedal else p for i,p in enumerate(kv)],kf)
   rows.append({'hip_down':down,'ankle_forward':forward,'spread':spread,'knees':knees,'arm_leg':len(arm.overlap(leg)),'leg_kart':len(leg.overlap(kt)),'samples':samples});ev.to_mesh_clear()
(P/'leg_fit_trials.json').write_text(json.dumps(rows,indent=2));print('LEG_BEST',sorted(rows,key=lambda a:max(s['hidden']*100+s['wheel_leg'] for s in a['samples'])+a['arm_leg']+a['leg_kart'])[:6],flush=True)

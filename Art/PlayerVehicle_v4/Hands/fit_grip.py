"""Fit existing anatomical weighted gloves around the measured wheel rim."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
P=Path(__file__).resolve().parent;V=P.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'BeforeGrip.blend'));s=bpy.context.scene;s.frame_set(25)
rig=bpy.data.objects['FP_KartArms_Rig'];C=Vector((.23,0,.52));N=Vector((math.cos(math.radians(55)),0,-math.sin(math.radians(55))));T=Vector((math.sin(math.radians(55)),0,math.cos(math.radians(55))))
base={b.name:rig.matrix_world@b.matrix for b in rig.pose.bones};lengths={b.name:(rig.matrix_world@b.tail-rig.matrix_world@b.head).length for b in rig.pose.bones};inv=rig.matrix_world.inverted()
def aim(m,a,b):
 out=m.to_3x3().col[1].normalized().rotation_difference((b-a).normalized()).to_matrix().to_4x4()@m;out.translation=a;return out
targets={};shift=-T*.055-N*.015
for side,sign in [('l',1),('r',-1)]:
 radial=Vector((0,sign,0));hand=base['hand_'+side].copy();hand.translation=C-T*.035-N*.080+radial*.214;targets['hand_'+side]=hand
 for finger,h in [('index',.026),('middle',.008),('ring',-.010),('pinky',-.027)]:
  names=[finger+'_'+str(i).zfill(2)+'_'+side for i in [1,2,3]]
  rim=C+T*h+radial*math.sqrt(.184**2-h*h)
  # MCP joints start on the outside of the rim. Fingers curl around its
  # underside toward the inner opening, as in the supplied grip reference.
  angle=math.radians(-25);radius=.026;points=[rim+radial*(radius*math.cos(angle))+N*(radius*math.sin(angle))]
  for name in names:
   angle-=2*math.asin(min(.98,lengths[name]/(2*radius)));points.append(rim+radial*(radius*math.cos(angle))+N*(radius*math.sin(angle)))
  for i,name in enumerate(names):targets[name]=aim(base[name],points[i],points[i+1])
 # Opposed thumb lies on the rear/inner side, rather than opening away from the grip.
 names=['thumb_'+str(i).zfill(2)+'_'+side for i in [1,2,3]]
 a=C-N*.055+radial*.209+T*.020
 goals=[C+T*.045+radial*.211-N*.036,C+T*.054+radial*.192-N*.020,C+T*.042+radial*.175-N*.008]
 for name,g in zip(names,goals):
  b=a+(g-a).normalized()*lengths[name];targets[name]=aim(base[name],a,b);a=b
def solve_arm(side,target):
 up,lo,end=['upperarm_'+side,'lowerarm_'+side,'hand_'+side];H=base[up].translation;W=target.translation;L1=(base[lo].translation-H).length;L2=(base[end].translation-base[lo].translation).length;D=(W-H).normalized();d=(W-H).length
 assert d<L1+L2,(side,d,L1+L2)
 along=(L1*L1-L2*L2+d*d)/(2*d);pole=Vector((-.3,.35 if side=='l' else -.35,-1));pole=(pole-D*pole.dot(D)).normalized();K=H+D*along+pole*math.sqrt(max(0,L1*L1-along*along))
 for name,m in [(up,aim(base[up],H,K)),(lo,aim(base[lo],K,W)),(end,target)]:rig.pose.bones[name].matrix=inv@m;bpy.context.view_layer.update()
errors=[]
for f in range(1,50):
 s.frame_set(f);q=Quaternion(N,math.radians((f-25)/24*45));tr=Matrix.Translation(C)@q.to_matrix().to_4x4()@Matrix.Translation(-C)
 for side in ['l','r']:solve_arm(side,tr@targets['hand_'+side])
 for name,m in targets.items():
  if name.startswith('hand_'):continue
  rig.pose.bones[name].matrix=inv@tr@m;bpy.context.view_layer.update()
 for name in targets:errors.append(((rig.matrix_world@rig.pose.bones[name].matrix).translation-(tr@targets[name]).translation).length)
 for b in rig.pose.bones:
  for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=f)
s.frame_set(25)
exec(compile((P/'glove_surface.py').read_text(),'glove_surface.py','exec'))
for name in ['SK_V4_DriverPOV','SK_V4_DriverFull']:
 skin=bpy.data.objects[name];bpy.ops.object.select_all(action='DESELECT');skin.hide_set(False);skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(V/'Exports'/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
bpy.data.objects['SK_V4_DriverPOV'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(V/'PlayerVehicle_v4.blend'))
(P/'grip_validation.json').write_text(json.dumps({'frames':49,'max_joint_target_error_m':max(errors),'rim_major_radius_m':.184,'finger_joint_arc_radius_m':.026},indent=2))
# Inspection render, not a substitute for the actual Unreal captures.
cam=s.camera;cam.location=C+Vector((.8,-1.1,.75));cam.rotation_euler=(C+Vector((0,0,.02))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=65
s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(P/'grip_preview.png');bpy.ops.render.render(write_still=True)



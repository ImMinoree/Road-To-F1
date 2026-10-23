from pathlib import Path
exec((Path(__file__).resolve().parent/'probe_grip.py').read_text().split("if '--save' not in sys.argv:")[0])
import hashlib
def digest(x):return hashlib.sha256(repr(x).encode()).hexdigest()
def protected():
 return {'kart':{o.name:digest((list(map(list,o.matrix_world)),[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])) for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')},'weights':{o.name:digest(([g.name for g in o.vertex_groups],[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices])) for o in scene.objects if o.type=='MESH' and (o.name.startswith(('RACER |','HELMET |')) or o.name=='kart_driverMesh')},'rig':digest([(b.name,b.parent.name if b.parent else '',list(map(list,b.matrix_local))) for b in arm.data.bones]),'lights':{o.name:digest((list(map(list,o.matrix_world)),o.data.energy,tuple(o.data.color))) for o in scene.objects if o.type=='LIGHT'},'body_geometry':digest([tuple(v.co) for v in body.data.vertices])}
before=protected();sourcehash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
params=json.loads((P/'grip_probe.json').read_text())[1]['params'];assert pose(params)
# Foot candidates were evaluated against the actual chassis/pedal geometry, not the old pivot estimate.
feet=json.loads((P/'feet_probe.json').read_text())[0]
for s,sgn in [('l',1),('r',-1)]:
 mat=arm.matrix_world@pb['foot_'+s].matrix;D=Vector((feet['x'],sgn*feet['y'],feet['z']));pole=head('calf_'+s).copy();pole.y=sgn*.22
 assert two('thigh_'+s,'calf_'+s,D,pole)
 mat.translation=D;pb['foot_'+s].matrix=arm.matrix_world.inverted()@mat;bpy.context.view_layer.update();aim('foot_'+s,D+Vector((.135,sgn*feet['yaw'],feet['pitch'])))
# Cache measured world grips before modifying their shoulder ancestors.
gripmat={s:arm.matrix_world@pb['hand_'+s].matrix for s in ['l','r']}
# Modest scapular protraction/depression keeps elbows bent without changing rest bones or stretching.
for s in ['l','r']:
 n='clavicle_'+s;m=arm.matrix_world@pb[n].matrix;m.translation+=Vector((.018,0,-.012));pb[n].matrix=arm.matrix_world.inverted()@m;bpy.context.view_layer.update()
for s,sgn in [('l',1),('r',-1)]:
 mat=gripmat[s]
 assert two('upperarm_'+s,'lowerarm_'+s,mat.translation,Vector((.22,sgn*.35,.74)))
 pb['hand_'+s].matrix=arm.matrix_world.inverted()@mat;bpy.context.view_layer.update()
# Keep original actions. New action contains fixed fitted body/finger poses plus IK controls.
for b in pb:
 b.keyframe_insert('location',frame=25);b.keyframe_insert('rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=25);b.keyframe_insert('scale',frame=25)
arm.animation_data.action.name='V5 | seated driver with nonstretch arm IK'
col=bpy.data.collections.new('V5 | steering IK controls');scene.collection.children.link(col)
def empty(name,matrix,size=.04):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.matrix_world=matrix;o.empty_display_type='ARROWS';o.empty_display_size=size;o.hide_render=True;return o
ctrl=empty('V5 | STEERING - degrees',Matrix.Translation((.62,0,.70)),.10);ctrl['steering_deg']=0.0;ctrl['tested_limit_deg']=25.0;ctrl.id_properties_ui('steering_deg').update(min=-25,max=25,soft_min=-25,soft_max=25,description='Wheel rotation. Tested driver range is +/-25 degrees; not mechanical lock.')
fc=ctrl.driver_add('rotation_euler',0);fc.driver.expression='angle*pi/180';var=fc.driver.variables.new();var.name='angle';var.type='SINGLE_PROP';var.targets[0].id=ctrl;var.targets[0].data_path='["steering_deg"]'
targets={};poles={};poleangles={}
for s,sgn in [('l',1),('r',-1)]:
 wm=arm.matrix_world@pb['hand_'+s].matrix;rot=wm.to_quaternion().to_matrix().to_4x4();rot.translation=wm.translation;target=empty('V5 | wrist IK '+s,rot);target.parent=ctrl;target.matrix_parent_inverse=Matrix.Identity(4);target.matrix_basis=ctrl.matrix_world.inverted()@rot;targets[s]=target
 desired=head('lowerarm_'+s).copy();pole=empty('V5 | elbow pole '+s,Matrix.Translation((.20,sgn*.48,.73)));poles[s]=pole
 ik=pb['lowerarm_'+s].constraints.new('IK');ik.name='V5 | nonstretch arm IK';ik.target=target;ik.pole_target=pole;ik.chain_count=2;ik.use_stretch=False;ik.iterations=128
 pb['upperarm_'+s].ik_stretch=0;pb['lowerarm_'+s].ik_stretch=0
 cr=pb['hand_'+s].constraints.new('COPY_ROTATION');cr.name='V5 | wrist follows wheel grip';cr.target=target;cr.target_space='WORLD';cr.owner_space='WORLD'
 best=None
 for a in range(-180,181,15):
  ik.pole_angle=math.radians(a);bpy.context.view_layer.update();score=(head('lowerarm_'+s)-desired).length
  if best is None or score<best[0]:best=(score,a)
 ik.pole_angle=math.radians(best[1]);poleangles[s]=best;bpy.context.view_layer.update()
 # Shoulder shifts are limited to 25mm forward/20mm down at the lowered hand side.
 b=pb['clavicle_'+s];localworld=arm.matrix_world@b.parent.matrix@b.parent.bone.matrix_local.inverted()@b.bone.matrix_local;dl=localworld.to_3x3().inverted()@Vector((.025,0,-.020));loc=b.location.copy()
 for i in range(3):
  fc=b.driver_add('location',i);fc.driver.expression=f'{loc[i]:.12f}+({dl[i]:.12f})*max(0,{-sgn}*angle)/25';v=fc.driver.variables.new();v.name='angle';v.type='SINGLE_PROP';v.targets[0].id=ctrl;v.targets[0].data_path='["steering_deg"]'
# Animate only original wheel components. Rest mesh vertices/transforms remain unchanged.
hooks={}
for o in scene.objects:
 if o.type!='MESH' or not o.name.startswith('SK_Kart_Steering_Column_And_Wheel_'):continue
 indices=[]
 if 'Frame_Brushed' in o.name:
  adjacency={v.index:set() for v in o.data.vertices}
  for e in o.data.edges:a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
  seen=set()
  for root in adjacency:
   if root in seen:continue
   pending=[root];part=[];seen.add(root)
   while pending:
    i=pending.pop();part.append(i)
    for j in adjacency[i]-seen:seen.add(j);pending.append(j)
   if sum((o.matrix_world@o.data.vertices[i].co).x for i in part)/len(part)>.60:indices.extend(part)
 else:indices=list(range(len(o.data.vertices)))
 if indices:
  hook=o.modifiers.new('V5 | original wheel steering articulation','HOOK');hook.object=ctrl;hook.matrix_inverse=ctrl.matrix_world.inverted()@o.matrix_world;hook.vertex_indices_set(indices);hooks[o.name]=len(indices)
# Original body, suit, helmet, gloves and boots remain in place, with their original bindings.
for o in [glove,body]:
 for m in o.modifiers:
  if m.type=='SUBSURF':m.levels=2 if o==glove else 1
for angle,frame in [(-25,1),(0,25),(25,49)]:ctrl['steering_deg']=angle;ctrl.keyframe_insert(data_path='["steering_deg"]',frame=frame)
scene.frame_start=1;scene.frame_end=49;scene.frame_set(25);bpy.context.view_layer.update()
after=protected();assert before==after,'Original protected geometry, bindings, rest skeleton or lights changed'
(P/'preservation.json').write_text(json.dumps({'source':str(SOURCE),'source_sha256':sourcehash,'before':before,'protected_unchanged':before==after,'grip_params':params,'feet_params':feet,'pole_calibration':poleangles,'wheel_hook_vertices':hooks},indent=2))
scene['V5 fit status']='Working fit. +/-25 degree steering IK with no bone stretch; geometric and visual validation pending.'
scene.camera=bpy.data.objects['Refinement | three quarter'];scene.cycles.samples=24;scene.render.resolution_x=1200;scene.render.resolution_y=960
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_With_MakeHuman_Racer_v5.blend'));scene.render.filepath=str(P/'v5_center_preview.png');bpy.ops.render.render(write_still=True)
print('V5_RIG_SAVED',json.dumps({'feet':feet,'pole':poleangles}),flush=True)

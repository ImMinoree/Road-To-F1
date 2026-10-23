import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent;F=P/'Kart_With_MakeHuman_Racer_v5.blend';bpy.ops.wm.open_mainfile(filepath=str(F));scene=bpy.context.scene;scene.frame_set(25);arm=bpy.data.objects['Game_engine'];pb=arm.pose.bones
def head(n):return arm.matrix_world@pb[n].head
def tail(n):return arm.matrix_world@pb[n].tail
def aim(n,target):
 h=head(n);q=(tail(n)-h).normalized().rotation_difference((target-h).normalized());m=arm.matrix_world@pb[n].matrix;pb[n].matrix=arm.matrix_world.inverted()@(Matrix.Translation(h)@q.to_matrix().to_4x4()@Matrix.Translation(-h)@m);bpy.context.view_layer.update()
def two(a,b,D,pole):
 A=head(a);u=(D-A).normalized();d=(D-A).length;l1=(tail(a)-A).length;l2=(tail(b)-head(b)).length;v=pole-A;v=(v-u*v.dot(u)).normalized();p=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-p*p));aim(a,A+u*p+v*h);aim(b,D)
for s in ['l','r']:
 mat=arm.matrix_world@pb['foot_'+s].matrix;mat.translation.z-=.002;D=mat.translation.copy();two('thigh_'+s,'calf_'+s,D,head('calf_'+s).copy());pb['foot_'+s].matrix=arm.matrix_world.inverted()@mat;bpy.context.view_layer.update()
 for n in ['thigh_'+s,'calf_'+s,'foot_'+s]:
  b=pb[n];b.keyframe_insert('location',frame=25);b.keyframe_insert('rotation_quaternion',frame=25);b.keyframe_insert('scale',frame=25)
o=bpy.data.objects['RACER | anatomical five-finger gloves'];disabled=[m for m in o.modifiers if m.type!='ARMATURE' and m.show_viewport]
for m in disabled:m.show_viewport=False
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];ev.to_mesh_clear()
for m in disabled:m.show_viewport=True
if not o.data.shape_keys:o.shape_key_add(name='Basis')
key=o.shape_key_add(name='V5 | submillimetre glove rim clearance');key.value=1;changed=0;maximum=0
for ve,p in zip(o.data.vertices,v):
 rad=math.sqrt(p.y*p.y+(p.z-.7)**2);center=Vector((.62,p.y*.184/rad,.7+(p.z-.7)*.184/rad));d=p-center;signed=d.length-.017
 if not -.002<signed<.014 or not .58<p.x<.67:continue
 move=max(0,.0011*(1-max(0,signed)/.018));delta=d.normalized()*move
 lm=Matrix(((0,0,0,0),)*4)
 for g in ve.groups:
  n=o.vertex_groups[g.group].name
  lm+=(arm.matrix_world@pb[n].matrix@arm.data.bones[n].matrix_local.inverted()@arm.matrix_world.inverted()@o.matrix_world)*g.weight
 key.data[ve.index].co+=lm.to_3x3().inverted()@delta;changed+=1;maximum=max(maximum,move)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(F));(P/'micro_clearance.json').write_text(json.dumps({'glove_vertices':changed,'max_glove_world_correction_m':maximum,'ankles_lowered_m':.002},indent=2));print('MICRO_CLEARANCE',changed,maximum,flush=True)

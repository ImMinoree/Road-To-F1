import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;F=P/'Kart_With_MakeHuman_Racer_v4.blend';bpy.ops.wm.open_mainfile(filepath=str(F));scene=bpy.context.scene;arm=bpy.data.objects['Game_engine'];deps=bpy.context.evaluated_depsgraph_get()
def geom(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return v,f
def tree(o):return BVHTree.FromPolygons(*geom(o))
report=json.loads((P/'validation.json').read_text());kart={o.name:tree(o) for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')};report['triangle_intersection_pairs']={}
outfit=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('RACER |','HELMET |'))]
for o in outfit+[bpy.data.objects['kart_driverMesh']]:
 t=tree(o);hits={n:len(t.overlap(bt)) for n,bt in kart.items() if t.overlap(bt)}
 if hits:report['triangle_intersection_pairs'][o.name]=hits
report['tank_wheel_intersection_pairs']={o:{n:c for n,c in h.items() if any(k in n for k in ['Fuel_Tank','Steering_Column'])} for o,h in report['triangle_intersection_pairs'].items()};report['tank_wheel_intersection_pairs']={o:h for o,h in report['tank_wheel_intersection_pairs'].items() if h}
bodytree=tree(bpy.data.objects['kart_driverMesh']);report['helmet_body_triangle_contacts']={o.name:len(tree(o).overlap(bodytree)) for o in outfit if o.name.startswith('HELMET |') and tree(o).overlap(bodytree)}
# Temporary skeletal articulation test; source pose restored, no kart parts animated or moved.
basis={b.name:b.matrix_basis.copy() for b in arm.pose.bones};oldaction=arm.animation_data.action;arm.animation_data.action=None
def head(n):return arm.matrix_world@arm.pose.bones[n].head
def tail(n):return arm.matrix_world@arm.pose.bones[n].tail
def aim(n,target):
 h=head(n);q=(tail(n)-h).normalized().rotation_difference((target-h).normalized());m=arm.matrix_world@arm.pose.bones[n].matrix;arm.pose.bones[n].matrix=arm.matrix_world.inverted()@(Matrix.Translation(h)@q.to_matrix().to_4x4()@Matrix.Translation(-h)@m);bpy.context.view_layer.update()
def two(a,b,D,pole):
 A=head(a);u=(D-A).normalized();d=(D-A).length;l1=(tail(a)-A).length;l2=(tail(b)-head(b)).length
 if not abs(l1-l2)<d<l1+l2:return False
 v=pole-A;v=(v-u*v.dot(u)).normalized();p=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-p*p));aim(a,A+u*p+v*h);aim(b,D);return True
controls={n:arm.matrix_world@arm.pose.bones[n].matrix for n in ['hand_l','hand_r','foot_l','foot_r']};tests=[]
for steering in [-8,8]:
 for b in arm.pose.bones:b.matrix_basis=basis[b.name].copy()
 bpy.context.view_layer.update();q=Quaternion(Vector((1,0,0)),math.radians(steering));pivot=Vector((.62,0,.70));rot=Matrix.Translation(pivot)@q.to_matrix().to_4x4()@Matrix.Translation(-pivot);reached=[]
 for s,sign in [('l',1),('r',-1)]:
  mat=rot@controls['hand_'+s];reached.append(two('upperarm_'+s,'lowerarm_'+s,mat.translation,Vector((.24,sign*.38,.75))));arm.pose.bones['hand_'+s].matrix=arm.matrix_world.inverted()@mat;bpy.context.view_layer.update()
  b=arm.pose.bones['foot_'+s];b.rotation_mode='QUATERNION';b.rotation_quaternion.rotate(Quaternion((1,0,0),math.radians(3*sign)))
 bpy.context.view_layer.update();finite=all(all(math.isfinite(a) for a in v) for o in outfit for v in geom(o)[0]);tests.append({'steering_degrees':steering,'arm_targets_reachable':reached,'pedal_rotation_degrees':3,'evaluated_outfit_finite':finite,'qualification':'Articulation smoke test only; not contact/deformation quality certification.'})
for b in arm.pose.bones:b.matrix_basis=basis[b.name].copy()
arm.animation_data.action=oldaction;scene.frame_set(1);bpy.context.view_layer.update();report['temporary_articulation_tests']=tests;report['grip_fit']=json.loads((P/'grip_validation.json').read_text())['selected'];report['final_status']='Partial visual upgrade. Reference-level realism NOT achieved; garment fit, hand/wheel clearance, shoulder transitions, boot/chassis contacts and seat support still require manual work.'
(P/'validation.json').write_text(json.dumps(report,indent=2))
scene['Visual quality status']=report['final_status'];scene.camera=bpy.data.objects['Refinement | three quarter'];scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=960;scene.render.resolution_percentage=100
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(F))
for name,camera in [('front','Refinement | front'),('side','Refinement | side'),('rear','Racer review | rear'),('three_quarter','Refinement | three quarter')]:
 scene.camera=bpy.data.objects[camera];scene.render.filepath=str(P/('racer_'+name+'.png'));bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['Refinement | three quarter'];scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.54,.54,.54);scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.render.filepath=str(P/'geometry_solid.png');bpy.ops.render.render(write_still=True)
scene.render.engine='CYCLES';print('FINAL_RENDERED',report['tank_wheel_intersection_pairs'],flush=True)

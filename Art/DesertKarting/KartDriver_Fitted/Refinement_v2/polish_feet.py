import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
arm=bpy.data.objects['Game_engine'];pb=arm.pose.bones
if arm.animation_data:arm.animation_data.action=None
deps=bpy.context.evaluated_depsgraph_get()
def head(n):return arm.matrix_world@pb[n].head
def tail(n):return arm.matrix_world@pb[n].tail
def aim(n,t):
 p=head(n);q=(tail(n)-p).normalized().rotation_difference((Vector(t)-p).normalized())
 wm=arm.matrix_world@pb[n].matrix;pb[n].matrix=arm.matrix_world.inverted()@(Matrix.Translation(p)@q.to_matrix().to_4x4()@Matrix.Translation(-p)@wm);bpy.context.view_layer.update()
def two(upper,lower,D,pole):
 A=head(upper);u=(D-A).normalized();d=(D-A).length;l1=(tail(upper)-A).length;l2=(tail(lower)-head(lower)).length
 if not abs(l1-l2)+.001<d<l1+l2-.001:return False
 v=pole-A;v=(v-u*v.dot(u)).normalized();a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-a*a))
 aim(upper,A+u*a+v*h);aim(lower,D);return True
def geometry(o):
 e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,f
trees={o.name:BVHTree.FromPolygons(*geometry(o)) for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')}
v,f=geometry(bpy.data.objects['SK_Kart_Driver_Controls_And_Pedals_Frame_Brushed_Chromoly'])
floor=BVHTree.FromPolygons(v,[p for p in f if all(v[i].z<.18 for i in p)])
shoe=bpy.data.objects['shoes05Mesh'];records={}
for side,s in [('l',1),('r',-1)]:
 groups={g.index for g in shoe.vertex_groups if g.name.endswith('_'+side)}
 ids={v.index for v in shoe.data.vertices if sum(w.weight for w in v.groups if w.group in groups)>.5}
 faces=[tuple(p.vertices) for p in shoe.data.polygons if all(i in ids for i in p.vertices)]
 def apply(x,y,z,angle):
  ankle=Vector((x,s*y,z));r=math.radians(angle)
  if not two('thigh_'+side,'calf_'+side,ankle,Vector((.68,s*.45,.65))):return False
  aim('foot_'+side,ankle+Vector((math.cos(r),-s*.025,math.sin(r))))
  a=math.radians(angle+25)
  aim('ball_'+side,head('ball_'+side)+Vector((math.cos(a),-s*.025,math.sin(a))))
  return True
 def measure():
  v,_=geometry(shoe);t=BVHTree.FromPolygons(v,faces)
  overlaps={n:len(t.overlap(tree)) for n,tree in trees.items() if t.overlap(tree)}
  clears=[]
  for i in ids:
   p=v[i];hit,_,_,_=floor.ray_cast(Vector((p.x,p.y,.42)),Vector((0,0,-1)),.5)
   if hit is not None:clears.append(p.z-hit.z)
  return overlaps,min(clears,default=.5)
 baseline=measure();candidates=[]
 for x in (.39,.41,.43,.45,.47):
  for y in (.17,.19,.21,.23):
   for angle in (-32,-22,-12,-7):
    z=.26
    for _ in range(3):
     if not apply(x,y,z,angle):break
     overlaps,clearance=measure()
     z+=max(-.04,min(.04,.0015-clearance))
    else:
     if not .18<z<.34:continue
     apply(x,y,z,angle);overlaps,clearance=measure()
     pairs=sum(overlaps.values())
     score=pairs+abs(clearance-.0015)*1000+max(0,y-.21)*150+abs(angle+27)*.05
     candidates.append({'params':[x,y,z,angle],'score':score,'pairs':pairs,'clearance_m':clearance,'overlaps':overlaps,'knee':list(head('calf_'+side))})
 candidates.sort(key=lambda p:p['score']);best=candidates[0]
 apply(*best['params']);records[side]={'before_overlaps':baseline[0],'before_clearance_m':baseline[1],'best':best,'top_candidates':candidates[:5]}
 print('FOOT',side,json.dumps(records[side]),flush=True)
for b in pb:
 b.keyframe_insert(data_path='location',frame=1);b.keyframe_insert(data_path='rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1);b.keyframe_insert(data_path='scale',frame=1)
if arm.animation_data and arm.animation_data.action:arm.animation_data.action.name='Kart | seating refinement v2 contact correction'
for side in ('l','r'):
 bpy.data.objects['Ankle fit '+side].location=head('foot_'+side)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_MakeHuman_Fitted_v2.blend'))
(OUT/'feet_polish.json').write_text(json.dumps(records,indent=2))

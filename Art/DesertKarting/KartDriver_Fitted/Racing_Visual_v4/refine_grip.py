import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;F=P/'Kart_With_MakeHuman_Racer_v4.blend';bpy.ops.wm.open_mainfile(filepath=str(F));arm=bpy.data.objects['Game_engine'];scene=bpy.context.scene;glove=bpy.data.objects['RACER | anatomical five-finger gloves'];deps=bpy.context.evaluated_depsgraph_get()
def geom(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return v,f
wheel=bpy.data.objects['SK_Kart_Steering_Column_And_Wheel_Rubber_Grip'];wv,wf=geom(wheel);wt=BVHTree.FromPolygons(wv,wf)
print('RIM_BOUNDS',[[min(p[i] for p in wv),max(p[i] for p in wv)] for i in range(3)],flush=True)
names=[b.name for b in arm.pose.bones if any(b.name.startswith(f) for f in ['hand_','index','middle','ring','pinky','thumb'])];basis={n:arm.pose.bones[n].matrix_basis.copy() for n in names}
def aim(n,target):
 b=arm.pose.bones[n];h=arm.matrix_world@b.head;t=arm.matrix_world@b.tail;q=(t-h).normalized().rotation_difference((Vector(target)-h).normalized());m=arm.matrix_world@b.matrix;b.matrix=arm.matrix_world.inverted()@(Matrix.Translation(h)@q.to_matrix().to_4x4()@Matrix.Translation(-h)@m);bpy.context.view_layer.update()
def pose(offset,xoff):
 for n in names:arm.pose.bones[n].matrix_basis=basis[n].copy()
 bpy.context.view_layer.update()
 for s,sgn in [('l',1),('r',-1)]:
  aim('hand_'+s,(.582,sgn*.201,.713))
  for finger in ['index','middle','ring','pinky']:
   n=finger+'_01_'+s;h=arm.matrix_world@arm.pose.bones[n].head;z=h.z;rim=sgn*math.sqrt(max(.001,.184**2-(z-.70)**2))
   aim(n,(.608+xoff,rim+sgn*offset,z));aim(finger+'_02_'+s,(.633+xoff,rim+sgn*offset*.8,z-.001));aim(finger+'_03_'+s,(.65+xoff,rim+sgn*offset*.15,z-.002))
 bpy.context.view_layer.update()
def hits():return len(BVHTree.FromPolygons(*geom(glove)).overlap(wt))
results=[]
for offset in [.018,.024,.030,.036,.042]:
 for xoff in [-.006,0,.006]:
  pose(offset,xoff);gv,_=geom(glove);gaps=sorted(wt.find_nearest(v)[3] for v in gv);results.append({'offset':offset,'xoff':xoff,'intersections':hits(),'closest_5pct_gap_m':sum(gaps[:max(1,len(gaps)//20)])/max(1,len(gaps)//20)})
results.sort(key=lambda r:r['intersections']*100+r['closest_5pct_gap_m']*1000)
best=results[0];pose(best['offset'],best['xoff'])
for n in names:
 b=arm.pose.bones[n];b.keyframe_insert('rotation_quaternion' if b.rotation_mode=='QUATERNION' else 'rotation_euler',frame=1)
# Darken the sheen layer to keep the suit cloth from appearing pearlescent under unchanged lights.
for name in ['Racer | charcoal woven nylon','Racer | crimson woven panels','Racer | warm white woven panels']:
 p=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF');p.inputs['Sheen Weight'].default_value=.008;p.inputs['Specular IOR Level'].default_value=.04
scene.frame_set(1);bpy.context.view_layer.update();best['final_hits']=hits()
(P/'grip_validation.json').write_text(json.dumps({'tested':results,'selected':best,'limitation':'Finger pose improves rim clearance, but this is not a production hand contact solver.'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(F));print('GRIP_BEST',best,flush=True)

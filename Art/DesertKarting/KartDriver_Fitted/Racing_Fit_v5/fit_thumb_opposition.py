import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;F=P/'Kart_With_MakeHuman_Racer_v5.blend';bpy.ops.wm.open_mainfile(filepath=str(F));scene=bpy.context.scene;scene.frame_set(25);arm=bpy.data.objects['Game_engine'];pb=arm.pose.bones;deps=bpy.context.evaluated_depsgraph_get();glove=bpy.data.objects['RACER | anatomical five-finger gloves'];body=bpy.data.objects['kart_driverMesh']
def geom(o,thumb=False):
 ev=o.evaluated_get(deps);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(p.vertices) for p in me.polygons];tv=[v[p.index] for p in me.vertices if any(o.vertex_groups[g.group].name.startswith('thumb_') and g.weight>.4 for g in p.groups)] if thumb else [];ev.to_mesh_clear();return v,f,tv
v,f,_=geom(bpy.data.objects['SK_Kart_Steering_Column_And_Wheel_Rubber_Grip']);wt=BVHTree.FromPolygons(v,f)
def aim(n,target):
 b=pb[n];h=arm.matrix_world@b.head;t=arm.matrix_world@b.tail;q=(t-h).normalized().rotation_difference((Vector(target)-h).normalized());m=arm.matrix_world@b.matrix;b.matrix=arm.matrix_world.inverted()@(Matrix.Translation(h)@q.to_matrix().to_4x4()@Matrix.Translation(-h)@m);bpy.context.view_layer.update()
names=[n for n in pb.keys() if n.startswith('thumb_')];basis={n:pb[n].matrix_basis.copy() for n in names}
def pose(x,y):
 for n in names:pb[n].matrix_basis=basis[n].copy()
 bpy.context.view_layer.update()
 for s,sgn in [('l',1),('r',-1)]:
  aim('thumb_01_'+s,(.550,sgn*.182,.733));aim('thumb_02_'+s,(.580,sgn*.169,.725));aim('thumb_03_'+s,(x,sgn*y,.708))
records=[]
for x in [.598,.603,.608]:
 for y in [.148,.154,.160]:
  pose(x,y);v,f,tv=geom(glove,True);b,bf,_=geom(body);hits=len(BVHTree.FromPolygons(v,f).overlap(wt));skin=len(BVHTree.FromPolygons(b,bf).overlap(wt));gaps=sorted(wt.find_nearest(p)[3] for p in tv);contact=sum(gaps[:20])/20
  records.append({'x':x,'y':y,'glove_pairs':hits,'skin_pairs':skin,'thumb_near_gap_m':contact,'score':(hits+skin)*100+abs(contact-.0015)*1000})
records.sort(key=lambda r:r['score']);best=records[0];pose(best['x'],best['y'])
for n in names:pb[n].keyframe_insert('rotation_quaternion',frame=25)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(F));(P/'thumb_fit.json').write_text(json.dumps({'selected':best,'candidates':records},indent=2));print('THUMB_OPPOSITION',best,flush=True)

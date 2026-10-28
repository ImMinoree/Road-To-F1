"""Continuous glove surfaces, skinned into the existing grip animation's bind pose.
Executed by fit_grip.py after the centre pose is evaluated.
"""
import bmesh
def tube(points,radii,axes=None):
 verts=[];faces=[];count=16
 for i,p in enumerate(points):
  tangent=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
  x=(T-tangent*T.dot(tangent)).normalized() if axes is None else axes[0]
  y=tangent.cross(x).normalized() if axes is None else axes[1]
  for j in range(count):
   a=math.tau*j/count;verts.append(p+x*math.cos(a)*radii[i][0]+y*math.sin(a)*radii[i][1])
 for i in range(len(points)-1):
  for j in range(count):a=i*count+j;b=i*count+(j+1)%count;faces.append((a,b,b+count,a+count))
 faces.extend([tuple(reversed(range(count))),tuple((len(points)-1)*count+j for j in range(count))])
 mesh=bpy.data.meshes.new('GloveSurface');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new('GloveSurface',mesh);s.collection.objects.link(o);return o
def curved(points,radii):
 # Rounded transitions retain recognizable phalanges, without disconnected capsule tips.
 pp=[];rr=[]
 for i in range(len(points)-1):
  a=points[max(0,i-1)];b=points[i];c=points[i+1];d=points[min(len(points)-1,i+2)]
  for j in range(5):
   t=j/5;pp.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t));r=radii[i]*(1-t)+radii[i+1]*t;rr.append((r,r*.9))
 pp.append(points[-1]);rr.append((.002,.002));return tube(pp,rr)
gloves=[]
for side,sign in [('l',1),('r',-1)]:
 radial=Vector((0,sign,0));w=targets['hand_'+side].translation
 knuckle=C-N*.012+radial*.158;forearm=(w-(rig.matrix_world@rig.pose.bones['lowerarm_'+side].matrix).translation).normalized()
 points=[w-forearm*.023,w-forearm*.012,w,w.lerp(knuckle,.35),w.lerp(knuckle,.72),knuckle]
 pieces=[tube(points,[(.024,.018),(.026,.019),(.027,.018),(.040,.017),(.044,.014),(.037,.010)])]
 segments=[]
 for finger,radius in [('index',.009),('middle',.0095),('ring',.0085),('pinky',.0075),('thumb',.011)]:
  names=[finger+'_'+str(i).zfill(2)+'_'+side for i in [1,2,3]]
  ps=[targets[n].translation for n in names];last=targets[names[-1]];ps.append(last.translation+last.to_3x3().col[1].normalized()*lengths[names[-1]])
  pieces.append(curved(ps,[radius*1.05,radius,radius*.9,radius*.65]))
  segments.extend((n,ps[i],ps[i+1]) for i,n in enumerate(names))
 bpy.ops.object.select_all(action='DESELECT')
 for o in pieces:o.select_set(True)
 bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join();o=pieces[0];o.name='V4_AnatomicalGlove_'+side
 rem=o.modifiers.new('Continuous sewn glove shell','REMESH');rem.mode='VOXEL';rem.voxel_size=.0015;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
 smooth=o.modifiers.new('Soft leather transitions','SMOOTH');smooth.factor=.65;smooth.iterations=4;bpy.ops.object.modifier_apply(modifier=smooth.name)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 # Use existing named glove materials so Unreal can retain the established bindings.
 source=bpy.data.objects['SK_V4_DriverPOV'];red=next(m for m in source.data.materials if m and ('Red' in m.name or 'Crimson' in m.name));black=next(m for m in source.data.materials if m and ('PalmSuede' in m.name or 'GraphiteNomex' in m.name))
 o.data.materials.append(red);o.data.materials.append(black)
 for v in o.data.vertices:
  p=v.co;d=p-C;plane=d-N*d.dot(N)
  if plane.length>.10:
   center=C+plane.normalized()*.184;away=p-center
   if away.length<.0185:v.co=center+away.normalized()*.0185
 for face in o.data.polygons:
  p=sum((o.data.vertices[i].co for i in face.vertices),Vector())/len(face.vertices);face.material_index=1 if (p-C).dot(radial)<.165 or (p-w).dot(N)<.005 else 0;face.use_smooth=True
 bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT');o.data.uv_layers.active.name=source.data.uv_layers[0].name
 names=['hand_'+side]+[n for n,a,b in segments]
 for n in names:o.vertex_groups.new(name=n)
 def distance(p,a,b):
  d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-a-d*t).length
 deform={n:rig.matrix_world@rig.pose.bones[n].matrix@rig.data.bones[n].matrix_local.inverted()@rig.matrix_world.inverted() for n in names}
 for v in o.data.vertices:
  p=v.co.copy();rank=sorted((distance(p,a,b),n) for n,a,b in segments)
  # The palm is bound to the hand; blend smoothly into articulated finger bases.
  nearest,name=rank[0];base_distance=(p-targets[name.split('_')[0]+'_01_'+side].translation).length
  finger_weight=max(0,min(1,((p-C).dot(N)+.035)/.025)) if not name.startswith('thumb') else max(0,min(1,((p-C).dot(N)+.060)/.025))
  if nearest>.020:finger_weight=0
  weights={'hand_'+side:1-finger_weight,name:finger_weight}
  matrix=Matrix([[sum(deform[n][i][j]*weight for n,weight in weights.items()) for j in range(4)] for i in range(4)])
  v.co=matrix.inverted()@p
  for n,weight in weights.items():
   if weight>0:o.vertex_groups[n].add([v.index],weight,'REPLACE')
 gloves.append(o)
for name in ['SK_V4_DriverPOV','SK_V4_DriverFull']:
 skin=bpy.data.objects[name];prefix=('hand_','thumb_','index_','middle_','ring_','pinky_')
 drop={v.index for v in skin.data.vertices if sum(g.weight for g in v.groups if skin.vertex_groups[g.group].name.startswith(prefix))>.20}
 bm=bmesh.new();bm.from_mesh(skin.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index in drop],context='VERTS');bm.to_mesh(skin.data);bm.free()
 bpy.ops.object.select_all(action='DESELECT');skin.hide_set(False);skin.select_set(True)
 for glove in gloves:
  copy=glove.copy();copy.data=glove.data.copy();s.collection.objects.link(copy);copy.select_set(True)
 bpy.context.view_layer.objects.active=skin;bpy.ops.object.join()
for o in gloves:bpy.data.objects.remove(o,do_unlink=True)






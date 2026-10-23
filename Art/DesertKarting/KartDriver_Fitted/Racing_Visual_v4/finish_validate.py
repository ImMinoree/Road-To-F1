import bpy,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;FINAL=P/'Kart_With_MakeHuman_Racer_v4.blend'
bpy.ops.wm.open_mainfile(filepath=str(FINAL));scene=bpy.context.scene;arm=bpy.data.objects['Game_engine'];suit=bpy.data.objects['RACER | fitted one-piece suit']
print('COLOR',scene.view_settings.view_transform,scene.view_settings.look,scene.view_settings.exposure,'OVERRIDE',scene.view_layers[0].material_override,flush=True)
def activate(o):
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
# Real rest-space cloth sculpting on subdivided garment, preserving original body mesh/rig.
activate(suit);sub=next(m for m in suit.modifiers if m.type=='SUBSURF');bpy.ops.object.modifier_move_up(modifier=sub.name);sub.levels=1;bpy.ops.object.modifier_apply(modifier=sub.name)
for v in suit.data.vertices:
 x,y,z=v.co;waist=math.exp(-((y-90)/6.5)**2);knee=math.exp(-((y-46)/7)**2);elbow=math.exp(-((y-108)/4)**2)*min(1,abs(x)/25)
 shape=.32*knee*math.sin(y*2.8+x*.37)+.24*waist*math.sin(y*3.1+abs(x)*.7)+.18*elbow*math.sin(y*3.4+x*.6)
 v.co+=v.normal*shape
suit.data.update();m=suit.modifiers.new('Final smooth fold surface','SUBSURF');m.levels=1;m.render_levels=1
for p in suit.data.polygons:p.material_index=0
deps=bpy.context.evaluated_depsgraph_get()
def geom(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return v,f
def tree(o):return BVHTree.FromPolygons(*geom(o))
suittree=tree(suit)
# Seat/torso panels were fitted in rest space. Reproject them in current pose and inverse-bind
# the correction, removing pose interpolation mismatches without deleting their skin binding.
def lbs_matrix(o,v):
 result=Matrix(((0,0,0,0),)*4);total=0
 for g in v.groups:
  n=o.vertex_groups[g.group].name
  if n in arm.pose.bones:
   result+= (arm.matrix_world@arm.pose.bones[n].matrix@arm.data.bones[n].matrix_local.inverted()@arm.matrix_world.inverted()@o.matrix_world)*g.weight;total+=g.weight
 return result if total else o.matrix_world
corrected=[]
for o in list(scene.objects):
 if o.type!='MESH' or not o.name.startswith('RACER |'):continue
 if not any(k in o.name for k in ['chest','thigh insert','rear red panel','zipper placket']):continue
 for v in o.data.vertices:
  lm=lbs_matrix(o,v);world=lm@v.co;hit,n,_,dist=suittree.find_nearest(world)
  if hit is not None and dist<.08:
   v.co=lm.inverted()@(hit+n*(.0018 if 'sewn edges' not in o.name else .0024))
 o.data.update();corrected.append(o.name)
# Reusable editable shoulder strips; geometry lies on the existing organic garment.
col=bpy.data.collections['RACER V4 | separate editable outfit']
def patch_world(name,points,faces,mat,bind_names):
 verts=[]
 for p,n in zip(points,bind_names):
  b=arm.pose.bones[n];m=arm.data.bones[n].matrix_local@b.matrix.inverted()@arm.matrix_world.inverted();verts.append(m@p)
 me=bpy.data.meshes.new(name+' topology');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);o.matrix_world=arm.matrix_world;me.materials.append(mat)
 for i,n in enumerate(bind_names):g=o.vertex_groups.get(n) or o.vertex_groups.new(name=n);g.add([i],1,'REPLACE')
 m=o.modifiers.new('Original MakeHuman armature','ARMATURE');m.object=arm
 m=o.modifiers.new('Tailored surface','SUBSURF');m.levels=1;m.render_levels=1
 m=o.modifiers.new('Panel thickness','SOLIDIFY');m.thickness=.08;m.offset=-1
 for p in me.polygons:p.use_smooth=True
 uv=me.uv_layers.new(name='UV | panel')
 for p in me.polygons:
  for li in p.loop_indices:
   idx=me.loops[li].vertex_index;uv.data[li].uv=(idx%7/6,idx//7/24)
 return o
for sign,s in [(1,'l'),(-1,'r')]:
 b=arm.pose.bones['upperarm_'+s];shoulder=arm.matrix_world@b.head;clav=arm.matrix_world@arm.pose.bones['clavicle_'+s].head
 points=[];names=[];faces=[]
 for j,t in enumerate(np.linspace(0,1,25)):
  # Sweep from upper chest, across anatomical shoulder cap, to upper back.
  for k,u in enumerate(np.linspace(0,1,7)):
   guess=shoulder+Vector((.085*math.cos(math.pi*t),-sign*(.016+.025*u),.042*math.sin(math.pi*t)+.020))
   hit,n,_,_=suittree.find_nearest(guess);points.append(hit+n*.0021);names.append('upperarm_'+s if t>.25 and t<.75 else 'spine_03')
   if j<24 and k<6:a=j*7+k;faces.append((a,a+1,a+8,a+7))
 patch_world('RACER | smooth shoulder epaulette '+s,points,faces,bpy.data.materials['Racer | crimson woven panels'],names)
# Neck underlayer: retain anatomy, cover exposed neck with the actual weighted skin surface.
body=bpy.data.objects['kart_driverMesh'];inds=[];polys=[]
for p in body.data.polygons:
 if all(sum(g.weight for g in body.data.vertices[i].groups if body.vertex_groups[g.group].name=='neck_01')>.4 for i in p.vertices):polys.append(p)
idx=sorted({i for p in polys for i in p.vertices});mp={i:j for j,i in enumerate(idx)}
if idx:
 me=bpy.data.meshes.new('Balaclava neck topology');me.from_pydata([body.data.vertices[i].co+body.data.vertices[i].normal*.10 for i in idx],[],[tuple(mp[i] for i in p.vertices) for p in polys]);me.update();o=bpy.data.objects.new('RACER | neck underlayer',me);col.objects.link(o);o.matrix_world=body.matrix_world;me.materials.append(bpy.data.materials['Racer | charcoal woven nylon'])
 for j,i in enumerate(idx):
  for g in body.data.vertices[i].groups:
   name=body.vertex_groups[g.group].name;vg=o.vertex_groups.get(name) or o.vertex_groups.new(name=name);vg.add([j],g.weight,'REPLACE')
 m=o.modifiers.new('Original human skin binding','ARMATURE');m.object=arm;m=o.modifiers.new('Neck smooth','SUBSURF');m.levels=2
 for p in me.polygons:p.use_smooth=True
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
# Mesh validity, actual evaluated garment/kart intersections, and rig compatibility diagnostics.
kart={o.name:tree(o) for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')}
visible=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith(('RACER |','HELMET |')))]
intersections={};binding={};quality={}
for o in visible:
 t=tree(o);hits={n:len(t.overlap(bt)) for n,bt in kart.items() if t.overlap(bt)}
 if hits:intersections[o.name]=hits
 binding[o.name]={'armature':any(m.type=='ARMATURE' and m.object==arm for m in o.modifiers),'unweighted_vertices':sum(not any(g.weight>0 for g in v.groups) for v in o.data.vertices),'uv_layers':len(o.data.uv_layers)}
 quality[o.name]={'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'finite':all(math.isfinite(a) for v in o.data.vertices for a in v.co)}
critical={o:{n:c for n,c in hits.items() if any(k in n for k in ['Fuel_Tank','Steering_Column'])} for o,hits in intersections.items()};critical={o:h for o,h in critical.items() if h}
source=json.loads((P/'preservation.json').read_text())
report={'source':source['source'],'original_source_file_unchanged':hashlib.sha256(Path(source['source']).read_bytes()).hexdigest()==source['source_sha256'],'original_human_geometry_weights_rest_skeleton_kart_lighting_unchanged':source['preserved'],'final_protected_recheck':{},'binding':binding,'mesh_quality':quality,'triangle_intersection_pairs':intersections,'tank_wheel_intersection_pairs':critical,'reprojected_panels':corrected,'actions_preserved':[(a.name,a.frame_range[:]) for a in bpy.data.actions],'limitations':['Not photorealistic or equivalent to the reference. Shoulder transitions, suit tailoring, wrinkles, glove fit and helmet graphics remain procedural and need manual refinement.','Surface intersection tests report triangle pairs, not penetration depth or solid containment; they do not certify collision-free geometry.','Existing backrest gap, pedal/shoe/frame fit and some garment/seat/bodywork intersections remain.','The source recline action is a static fitted pose, not a completed gameplay steering/pedal animation. Skin bindings are retained; no Unreal import or animation integration was performed.']}
# Prove protected kart/light/body content again from the saved source signatures.
def h(x):return hashlib.sha256(repr(x).encode()).hexdigest()
now={'kart':{o.name:h((list(map(list,o.matrix_world)),[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])) for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_')},'lighting':{o.name:h((list(map(list,o.matrix_world)),o.data.energy,o.data.color[:],o.data.type,o.data.size if hasattr(o.data,'size') else None)) for o in scene.objects if o.type=='LIGHT'},'rig':h([(b.name,b.parent.name if b.parent else '',list(map(list,b.matrix_local))) for b in arm.data.bones]),'body_weights':h([[(g.group,g.weight) for g in v.groups] for v in body.data.vertices]),'body_geometry':h([tuple(v.co) for v in body.data.vertices])}
report['final_protected_recheck']={k:val==source['protected_signatures'][k] for k,val in now.items()};assert all(report['final_protected_recheck'].values())
assert all(v['finite'] for v in quality.values());assert all(v['armature'] and v['unweighted_vertices']==0 for v in binding.values())
(P/'validation.json').write_text(json.dumps(report,indent=2))
scene['Visual quality status']='Editable outfit upgrade; reference-level photorealism NOT achieved. See README and actual renders. Existing fit and new outfit contacts remain.'
scene.camera=bpy.data.objects['Refinement | three quarter'];scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=960;scene.render.resolution_percentage=100
# Rear camera uses the same framing; original lights and existing cameras remain untouched.
cam=bpy.data.objects.get('Racer review | rear')
if not cam:
 data=bpy.data.cameras.new('Racer review | rear');cam=bpy.data.objects.new('Racer review | rear',data);scene.collection.objects.link(cam)
cam.location=(-3.5,-.15,1.65);target=Vector((.20,0,.72));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.65;cam.data.lens=55
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL))
for name,camera in [('front','Refinement | front'),('side','Refinement | side'),('rear','Racer review | rear'),('three_quarter','Refinement | three quarter')]:
 scene.camera=bpy.data.objects[camera];scene.render.filepath=str(P/('racer_'+name+'.png'));bpy.ops.render.render(write_still=True)
# Workbench inspection is deliberately untextured: silhouette and actual geometry remain visible.
scene.camera=bpy.data.objects['Refinement | three quarter'];scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.54,.54,.54);scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.render.filepath=str(P/'geometry_solid.png');bpy.ops.render.render(write_still=True)
scene.render.engine='CYCLES';scene.cycles.samples=64
print('RACER_VALIDATED',json.dumps({'critical':critical,'protected':report['final_protected_recheck'],'intersection_objects':len(intersections)}),flush=True)

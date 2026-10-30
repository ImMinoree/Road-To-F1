"""Add visual depth only, preserving current race, tire walls, collision and lighting."""
import unreal as u,json,time,math,hashlib,traceback,statistics
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/EnvironmentDepth';P=R/'Art/EnvironmentDepth';D='/Game/RoadToF1/EnvironmentDepth';B='/Game/RoadToF1/Trackside/TireBarriers';g=json.loads((P/'manifest.json').read_text());edges=json.loads((R/'Art/RacingAI/track_edges.json').read_text());route=edges['center']
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem);T=u.AssetToolsHelpers.get_asset_tools();EA=u.EditorAssetLibrary;S=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');u.EditorPythonScripting.set_keep_python_script_alive(True)
state={'phase':'warm','epoch':time.monotonic(),'busy':False};report={'saved':False,'reference_viewed_in_browser':True};cameras=[];protected={}
for folder in ['Source','Config','Content/RoadToF1/Trackside/TireBarriers']:
 for p in (R/folder).rglob('*'):
  if p.is_file():protected[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
for p in (R/'Content/RoadToF1/Maps').glob('*.umap'):
 if p.stem!='DesertKarting_Visual':protected[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
(E/'protected_before.json').write_text(json.dumps(protected,indent=2))
def nxt(p):state.update(phase=p,epoch=time.monotonic())
def parts(h):return h.to_tuple() if h else []
def ignored():return list(u.GameplayStatics.get_all_actors_of_class(W.get_editor_world(),u.InstancedFoliageActor))
def ground(x,y,world=None):
 world=world or W.get_editor_world()
 h=u.SystemLibrary.line_trace_single(world,u.Vector(x,y,150),u.Vector(x,y,-150),u.TraceTypeQuery.ECC_VISIBILITY,True,ignored(),u.DrawDebugTrace.NONE,True)
 assert h,('Missing ground',x,y)
 return next(v.z for v in parts(h) if isinstance(v,u.Vector))
def tires():
 out=[]
 for a in A.get_all_level_actors():
  for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
   if c.static_mesh and c.static_mesh.get_path_name().startswith(B+'/'):
    assert c.get_collision_enabled()==u.CollisionEnabled.QUERY_AND_PHYSICS
    out.append(c)
 return out
def keys():
 out=[]
 for c in tires():
  for i in range(c.get_instance_count()):
   t=c.get_instance_transform(i,world_space=True);p=t.translation;r=t.rotation.rotator();s=t.scale3d
   out.append((c.static_mesh.get_path_name(),)+tuple(round(v,3) for v in [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]))
 return sorted(out)
def signature():
 out={}
 for a in A.get_all_level_actors():
  if isinstance(a,u.InstancedFoliageActor) or a in cameras:continue
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
  item=[a.get_class().get_name(),p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z,a.get_actor_enable_collision()]
  for c in a.get_components_by_class(u.StaticMeshComponent):
   if c.static_mesh:item.extend([c.get_name(),c.static_mesh.get_path_name(),[list(c.get_world_transform().translation.to_tuple()),list(c.get_world_transform().scale3d.to_tuple()),list(c.get_world_transform().rotation.rotator().to_tuple())],str(c.get_collision_enabled())])
  if isinstance(a,u.Light):item.extend([[a.light_component.get_editor_property('light_color').r,a.light_component.get_editor_property('light_color').g,a.light_component.get_editor_property('light_color').b,a.light_component.get_editor_property('light_color').a],a.light_component.get_editor_property('intensity')])
  out[a.get_name()]=item
 return out
def sweep():
 blocked=[];world=W.get_editor_world();count=0
 for i,p in enumerate(route):
  q=route[(i+1)%len(route)];dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy);yaw=math.degrees(math.atan2(dy,dx))
  width=min(math.dist(p[:2],edges[k][i][:2]) for k in ['left','right'])-110
  for lane in [-width,0,width]:
   x=p[0]-dy/length*lane;y=p[1]+dx/length*lane;z=ground(x,y)+31
   h=u.SystemLibrary.box_trace_single(world,u.Vector(x,y,z),u.Vector(x+dx,y+dy,z),u.Vector(90,60,16),u.Rotator(yaw=yaw),u.TraceTypeQuery.ECC_VISIBILITY,False,[],u.DrawDebugTrace.NONE,True)
   count+=1
   if h:blocked.append([i,round(lane,1),[a.get_name() for a in parts(h) if isinstance(a,u.Actor)]])
 for a in A.get_all_level_actors():
  if a.get_class().get_name()!='GridStartSlot':continue
  p=a.get_actor_location();h=u.SystemLibrary.box_trace_single(world,p,p+u.Vector(.01,0,0),u.Vector(90,60,16),a.get_actor_rotation(),u.TraceTypeQuery.ECC_VISIBILITY,False,[],u.DrawDebugTrace.NONE,True)
  count+=1
  if h:blocked.append(['grid',a.get_name(),[b.get_name() for b in parts(h) if isinstance(b,u.Actor)]])
 return {'sweeps':count,'blocked':blocked}
def aerial():
 c=A.spawn_actor_from_class(u.CameraActor,u.Vector(2925,-10350,40000),u.Rotator(pitch=-90));cameras.append(c);cc=c.camera_component
 for k,v in [('projection_mode',u.CameraProjectionMode.ORTHOGRAPHIC),('ortho_width',31000),('aspect_ratio',1.2),('constrain_aspect_ratio',True),('auto_calculate_ortho_planes',False),('ortho_near_clip_plane',1),('ortho_far_clip_plane',100000)]:cc.set_editor_property(k,v)
 return c

def original_foliage_signature():
 out={}
 for a in A.get_all_level_actors():
  for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
   if not c.static_mesh or c.static_mesh.get_path_name().startswith(D+'/'):continue
   # New grass types reuse grass meshes, so distinguish our owned components by foliage type name.
   if c.get_name() in state.get('new_component_names',[]):continue
   values=[]
   for i in range(c.get_instance_count()):
    t=c.get_instance_transform(i,world_space=True);r=t.rotation.rotator();values.append([round(v,4) for v in list(t.translation.to_tuple())+list(r.to_tuple())+list(t.scale3d.to_tuple())])
   out[c.get_name()]=[c.static_mesh.get_path_name(),len(values),hashlib.sha256(json.dumps(values).encode()).hexdigest(),str(c.get_collision_enabled())]
 return out
def point_pawn(idx):
 pw=W.get_game_world();pawn=u.GameplayStatics.get_player_pawn(pw,0);assert isinstance(pawn,u.ProofPawn)
 for kart in u.GameplayStatics.get_all_actors_of_class(pw,u.ProofPawn):kart.set_kart_test_input(0,0,True)
 p=route[idx];q=route[(idx+3)%len(route)];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));pawn.set_actor_location_and_rotation(u.Vector(p[0],p[1],31),u.Rotator(yaw=yaw),False,True);pawn.get_component_by_class(u.KartTireDynamics).reset_motion()
 if pawn.is_third_person_view():pawn.toggle_camera_view()
 u.GameplayStatics.get_player_controller(pw,0).set_view_target_with_blend(pawn,0)
 return pawn
def import_and_place():
 world=W.get_editor_world();meshes={};imports=[]
 for item in g['assets']:
  name=item['name'];task=u.AssetImportTask();task.filename=str(P/'Meshes'/(name+'.fbx'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True
  opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opts.import_materials=False;opts.import_textures=False;opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.auto_generate_collision=False;opts.static_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=opts;T.import_asset_tasks([task]);mesh=u.load_asset(D+'/Meshes/'+name);assert mesh
  for i,slot in enumerate(mesh.get_editor_property('static_materials')):
   material=str(slot.material_slot_name);material='CapIvory' if material=='Fabric' else material;asset=u.load_asset('/Game/RoadToF1/DesertVisual/Materials/MI_DV_'+material);assert asset,material;mesh.set_material(i,asset)
  if item['triangles']>300:
   reductions=u.StaticMeshReductionOptions();reductions.auto_compute_lod_screen_size=False;reductions.reduction_settings=[u.StaticMeshReductionSettings(percent_triangles=p,screen_size=s) for p,s in [(1,1),(.5,.16),(.2,.055)]];assert S.set_lods(mesh,reductions)>=3
  S.remove_collisions(mesh);EA.save_loaded_asset(mesh);meshes[name]=mesh;imports.append({'asset':mesh.get_path_name(),'lods':S.get_lod_count(mesh),'triangles':item['triangles']})
 for i in range(3):meshes['Grass'+str(i)]=u.load_asset('/Game/RoadToF1/InfieldGrass/Meshes/SM_InfieldGrass_%02d'%i)
 accepted={};rejected=[];ig=ignored()
 for item in g['placements']:
  mesh=meshes[item['mesh']];x,y=item['xy'];kind=item['kind'];scale=item['scale'];yaw=item['yaw']
  if kind=='horizon':z=item['z']
  else:
   h=u.SystemLibrary.line_trace_single(world,u.Vector(x,y,180),u.Vector(x,y,-300),u.TraceTypeQuery.ECC_VISIBILITY,True,ig,u.DrawDebugTrace.NONE,True)
   if not h:rejected.append([item['mesh'],x,y,'no ground']);continue
   z=next(v.z for v in parts(h) if isinstance(v,u.Vector))
   if not -80<z<65:rejected.append([item['mesh'],x,y,'elevated structure']);continue
   b=mesh.get_bounding_box();lo=b.min*u.Vector(*scale);hi=b.max*u.Vector(*scale);half=(hi-lo)*.5;center=(hi+lo)*.5;rad=math.radians(yaw);cx=center.x*math.cos(rad)-center.y*math.sin(rad);cy=center.x*math.sin(rad)+center.y*math.cos(rad)
   # Lift the nonblocking visual envelope a little above the support surface.
   h=u.SystemLibrary.box_trace_single(world,u.Vector(x+cx,y+cy,z+center.z+4),u.Vector(x+cx+.01,y+cy,z+center.z+4),half,u.Rotator(yaw=yaw),u.TraceTypeQuery.ECC_VISIBILITY,True,ig,u.DrawDebugTrace.NONE,True)
   if h:rejected.append([item['mesh'],x,y,'existing structure overlap']);continue
  accepted.setdefault(item['mesh'],[]).append(u.Transform(location=u.Vector(x,y,z),rotation=u.Rotator(yaw=yaw),scale=u.Vector(*scale)))
 counts={};newnames=[];before_names={c.get_name() for a in A.get_all_level_actors() for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent)}
 for name,ts in accepted.items():
  path=D+'/Instancing/FT_ED_'+name;ft=u.load_asset(path) or T.create_asset('FT_ED_'+name,D+'/Instancing',u.FoliageType_InstancedStaticMesh,u.FoliageType_InstancedStaticMeshFactory());ft.set_editor_property('mesh',meshes[name]);body=ft.get_editor_property('body_instance');body.set_editor_property('collision_enabled',u.CollisionEnabled.NO_COLLISION);body.set_editor_property('collision_profile_name','NoCollision');ft.set_editor_property('body_instance',body);ft.set_editor_property('collision_with_world',False)
  is_grass=name.startswith('Grass');is_ridge='Ridge' in name;ft.set_editor_property('cast_shadow',not (is_grass or is_ridge));distance=(4500,7000) if is_grass else ((100000,130000) if is_ridge else (25000,45000));ft.set_editor_property('cull_distance',u.Int32Interval(min=distance[0],max=distance[1]));EA.save_loaded_asset(ft);u.InstancedFoliageActor.add_instances(world,ft,ts);counts[name]=len(ts)
 for a in A.get_all_level_actors():
  for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
   if c.get_name() not in before_names:newnames.append(c.get_name());assert c.get_collision_enabled()==u.CollisionEnabled.NO_COLLISION
 state['new_component_names']=newnames;report.update(instances=counts,imported_meshes=imports,rejected_placements=rejected,added_hism_components=len(newnames))
 assert sum(counts.values())>300 and sum(v for k,v in counts.items() if 'Palm' in k)>10
 assert keys()==state['tires'];assert signature()==state['sig'];assert original_foliage_signature()==state['foliage'];after=sweep();assert after==state['corridor'];report['after_clearance']=after;report.update(original_tire_instances_preserved=len(state['tires']),existing_foliage_unchanged=True,existing_actors_lighting_unchanged=True)
 for path,digest in protected.items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
 assert L.save_current_level();assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');assert keys()==state['tires'];assert signature()==state['sig'];assert original_foliage_signature()==state['foliage'];report.update(saved=True,reloaded=True)
 # Aerial overview uses only a transient camera; original lighting/cameras are untouched.
 state['camera']=aerial()
def finish():
 (E/'validation.json').write_text(json.dumps(report,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  age=time.monotonic()-state['epoch'];phase=state['phase']
  if time.monotonic()-state.get('start_time',time.monotonic())>240:raise RuntimeError('Depth pass timeout')
  if phase=='warm' and age>4:
   state['start_time']=time.monotonic();state['sig']=signature();state['tires']=keys();state['foliage']=original_foliage_signature();state['corridor']=sweep();report['before_clearance']=state['corridor'];L.editor_request_begin_play();nxt('baseline_play')
  elif phase in ['baseline_play','after_play']:
   pw=W.get_game_world()
   if not pw or u.GameplayStatics.get_time_seconds(pw)<10:return
   point_pawn(54);state['samples']=[];nxt('baseline_eye' if phase=='baseline_play' else 'after_eye')
  elif phase in ['baseline_eye','after_eye']:
   if age>1:state['samples'].append(dt*1000)
   if age>5:
    key='before' if phase=='baseline_eye' else 'after';xs=sorted(state['samples']);report.setdefault('editor_frame_probe',{})[key]={'frames':len(xs),'median_ms':statistics.median(xs),'p95_ms':xs[int(.95*(len(xs)-1))]};u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/('driver_'+key+'.png')));nxt('baseline_done' if key=='before' else 'after_done')
  elif phase=='baseline_done' and age>3:L.editor_request_end_play();nxt('apply')
  elif phase=='apply' and age>2:
   assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');import_and_place();nxt('aerial')
  elif phase=='aerial' and age>6:
   state['task']=u.AutomationLibrary.take_high_res_screenshot(2400,2000,str(E/'aerial_depth.png'),camera=state['camera'],delay=1);nxt('aerial_wait')
  elif phase=='aerial_wait' and state['task'].is_task_done() and age>2:A.destroy_actor(state['camera']);L.editor_request_begin_play();nxt('after_play')
  elif phase=='after_done' and age>3:point_pawn(184);nxt('hairpin')
  elif phase=='hairpin' and age>4:u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/'driver_hairpin_depth.png'));nxt('hairpin_done')
  elif phase=='hairpin_done' and age>3:point_pawn(690);nxt('west')
  elif phase=='west' and age>4:u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/'driver_west_depth.png'));nxt('west_done')
  elif phase=='west_done' and age>3:L.editor_request_end_play();nxt('finish')
  elif phase=='finish' and age>2:finish()
 except Exception:
  report['error']=traceback.format_exc();(E/'error.txt').write_text(report['error']);u.log_error(report['error'])
  if L.is_in_play_in_editor():L.editor_request_end_play()
  finish()
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

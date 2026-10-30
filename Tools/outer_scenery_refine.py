import unreal as u,json,time,math,hashlib,traceback,statistics,shutil
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/OuterScenery';E.mkdir(parents=True,exist_ok=True);P=R/'Art/OuterScenery';D='/Game/RoadToF1/OuterScenery';B='/Game/RoadToF1/Trackside/TireBarriers'
g=json.loads((P/'manifest.json').read_text());edges=json.loads((R/'Art/RacingAI/track_edges.json').read_text());route=edges['center']
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem);T=u.AssetToolsHelpers.get_asset_tools();EA=u.EditorAssetLibrary;S=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');u.EditorPythonScripting.set_keep_python_script_alive(True)
state={'phase':'warm','epoch':time.monotonic(),'busy':False,'start':time.monotonic(),'view':0,'pass':'before'};report=json.loads((E/'validation.json').read_text());cameras=[]
for c in ['t.MaxFPS 60','t.IdleWhenNotForeground 0','Slate.bAllowThrottling 0']:u.SystemLibrary.execute_console_command(None,c)
views=[('straight',54),('hairpin',184),('west',690)]
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

def point_pawn(idx):
 pw=W.get_game_world();pawn=u.GameplayStatics.get_player_pawn(pw,0);assert isinstance(pawn,u.ProofPawn)
 for kart in u.GameplayStatics.get_all_actors_of_class(pw,u.ProofPawn):kart.set_kart_test_input(0,0,True)
 p=route[idx];q=route[(idx+3)%len(route)];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));pawn.set_actor_location_and_rotation(u.Vector(p[0],p[1],31),u.Rotator(yaw=yaw),False,True);pawn.get_component_by_class(u.KartTireDynamics).reset_motion()
 if pawn.is_third_person_view():pawn.toggle_camera_view()
 u.GameplayStatics.get_player_controller(pw,0).set_view_target_with_blend(pawn,0)
 return pawn
def refine():
 name='SM_OS_RockyMassifs';task=u.AssetImportTask();task.filename=str(P/(name+'.fbx'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True
 opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opts.import_materials=False;opts.import_textures=False;opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.auto_generate_collision=False;opts.static_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=opts;T.import_asset_tasks([task]);mesh=u.load_asset(D+'/Meshes/'+name)
 # Cheap distant-only atmospheric fill, without editing fog, sky or lights.
 mat=T.create_asset('M_OS_DistantRock',D+'/Materials',u.Material,u.MaterialFactoryNew());M=u.MaterialEditingLibrary
 for prop,value in [(u.MaterialProperty.MP_BASE_COLOR,(.22,.20,.18)),(u.MaterialProperty.MP_EMISSIVE_COLOR,(.055,.065,.078))]:
  n=M.create_material_expression(mat,u.MaterialExpressionConstant3Vector);n.set_editor_property('constant',u.LinearColor(*value));M.connect_material_property(n,'',prop)
 n=M.create_material_expression(mat,u.MaterialExpressionConstant);n.set_editor_property('r',1);M.connect_material_property(n,'',u.MaterialProperty.MP_ROUGHNESS);M.recompile_material(mat);EA.save_loaded_asset(mat)
 mesh.set_material(0,mat);S.remove_collisions(mesh);opt=u.StaticMeshReductionOptions();opt.auto_compute_lod_screen_size=False;opt.reduction_settings=[u.StaticMeshReductionSettings(percent_triangles=p,screen_size=s) for p,s in [(1,1),(.45,.35),(.15,.10)]];S.set_lods(mesh,opt);EA.save_loaded_asset(mesh)
 assert signature()==state['sig'];assert keys()==state['tires'];assert L.save_current_level();assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');assert signature()==state['sig'];report['refinement']='Lower irregular mountain ridgelines and distant-only atmospheric material fill; existing fog and lighting unchanged.'

def finish():
 (E/'validation.json').write_text(json.dumps(report,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  age=time.monotonic()-state['epoch'];phase=state['phase']
  if time.monotonic()-state['start']>600:raise RuntimeError('Scenery timeout')
  if phase=='warm' and age>6:
   state['sig']=signature();state['tires']=keys();refine();state['pass']='after';L.editor_request_begin_play();nxt('play')
  elif phase=='play':
   pw=W.get_game_world()
   if not pw or u.GameplayStatics.get_time_seconds(pw)<10:return
   point_pawn(views[state['view']][1]);state['frames']=[];nxt('eye')
  elif phase=='eye':
   if age>2:state['frames'].append(dt*1000)
   if age>7:
    name='final_'+views[state['view']][0];xs=state['frames'];report.setdefault('frame_probe',{})[name]={'median_ms':statistics.median(xs),'frames':len(xs)};u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/(name+'.png')));nxt('shot')
  elif phase=='shot' and age>3:
   state['view']+=1
   if state['view']<len(views):point_pawn(views[state['view']][1]);state['frames']=[];nxt('eye')
   else:L.editor_request_end_play();nxt('apply' if state['pass']=='before' else 'finish')
  elif phase=='apply' and age>3:
   assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');place();state.update(view=0,**{'pass':'after'});L.editor_request_begin_play();nxt('play')
  elif phase=='finish' and age>3:finish()
 except Exception:
  report['error']=traceback.format_exc();u.log_error(report['error']);(E/'error.txt').write_text(report['error'])
  if L.is_in_play_in_editor():L.editor_request_end_play()
  finish()
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

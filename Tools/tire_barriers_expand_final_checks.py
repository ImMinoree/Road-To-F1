"""Final read-only rendered evidence and controlled PIE performance/drive probes."""
import unreal as u,json,time,math,statistics,traceback,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/ExpandedTireBarriers';B='/Game/RoadToF1/Trackside/TireBarriers';L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');u.EditorPythonScripting.set_keep_python_script_alive(True)
original=json.loads((E/'inventory_before.json').read_text());cols=json.loads((E/'placed_columns.json').read_text());edges=json.loads((R/'Art/RacingAI/track_edges.json').read_text());state={'phase':'warm','epoch':time.monotonic(),'busy':False};report={};mapfile=R/'Content/RoadToF1/Maps/DesertKarting_Visual.umap';digest=hashlib.sha256(mapfile.read_bytes()).hexdigest()
def nxt(p):state.update(phase=p,epoch=time.monotonic())
def components(world):
 return [c for a in u.GameplayStatics.get_all_actors_of_class(world,u.InstancedFoliageActor) for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent) if c.static_mesh and c.static_mesh.get_path_name().startswith(B+'/')]
def finish():
 assert hashlib.sha256(mapfile.read_bytes()).hexdigest()==digest
 (E/'final_checks.json').write_text(json.dumps(report,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  age=time.monotonic()-state['epoch'];phase=state['phase']
  if phase=='warm' and age>4:
   world=W.get_editor_world();cs=components(world);assert sum(c.get_instance_count() for c in cs)==1725
   # Temporary expanded cull distances allow the whole circuit's tires to appear in aerial evidence.
   for c in cs:c.set_cull_distances(90000,100000)
   camera=A.spawn_actor_from_class(u.CameraActor,u.Vector(2925,-10350,40000),u.Rotator(pitch=-90));state['camera']=camera;cc=camera.camera_component
   for k,v in [('projection_mode',u.CameraProjectionMode.ORTHOGRAPHIC),('ortho_width',31000),('aspect_ratio',1.2),('constrain_aspect_ratio',True),('auto_calculate_ortho_planes',False),('ortho_near_clip_plane',1),('ortho_far_clip_plane',100000)]:cc.set_editor_property(k,v)
   nxt('aerial')
  elif phase=='aerial' and age>5:
   state['task']=u.AutomationLibrary.take_high_res_screenshot(2400,2000,str(E/'aerial_all_barriers.png'),camera=state['camera'],delay=1);nxt('shot')
  elif phase=='shot' and state['task'].is_task_done() and age>2:
   A.destroy_actor(state['camera']);assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');L.editor_request_begin_play();nxt('play')
  elif phase=='play':
   if age>100:raise RuntimeError('PIE startup timeout')
   world=W.get_game_world()
   if not world or u.GameplayStatics.get_time_seconds(world)<10:return
   pawn=u.GameplayStatics.get_player_pawn(world,0);assert isinstance(pawn,u.ProofPawn)
   for kart in u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn):kart.set_kart_test_input(0,0,True)
   p=edges['center'][54];q=edges['center'][57];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));pawn.set_actor_location_and_rotation(u.Vector(p[0],p[1],40),u.Rotator(yaw=yaw),False,True);pawn.get_component_by_class(u.KartTireDynamics).reset_motion()
   if pawn.is_third_person_view():pawn.toggle_camera_view()
   u.GameplayStatics.get_player_controller(world,0).set_view_target_with_blend(pawn,0);state['pawn']=pawn
   for name in ['Unit','RHI']:u.AutomationLibrary.enable_stat_group(world,name)
   u.SystemLibrary.execute_console_command(world,'t.MaxFPS 0');nxt('settle_full')
  elif phase=='settle_full' and age>4:state['samples']=[];nxt('sample_full')
  elif phase in ['sample_full','sample_baseline']:
   state['samples'].append(dt*1000)
   if age>5:
    xs=sorted(state['samples']);key='expanded' if phase=='sample_full' else 'original_144';report[key]={'frames':len(xs),'median_slate_frame_ms':statistics.median(xs),'p95_slate_frame_ms':xs[int(.95*(len(xs)-1))],'stats':{n:u.AutomationLibrary.get_stat_inc_average(n) for n in ['STAT_FrameTime','STAT_DrawPrimitiveCalls','STAT_RHITriangles']}}
    if phase=='sample_full':
     # Only the unsaved PIE duplicate is altered to compare the exact original 144 instances.
     world=W.get_game_world();removed=0
     for c in components(world):
      originals=[i for item in original['tire_components'] if item['mesh']==c.static_mesh.get_path_name() for i in item['instances']];keep={tuple(round(v,2) for v in i['location']) for i in originals};indices=[]
      for i in range(c.get_instance_count()):
       t=c.get_instance_transform(i,world_space=True)
       if tuple(round(v,2) for v in t.translation.to_tuple()) not in keep:indices.append(i)
      for i in reversed(indices):assert c.remove_instance(i)
      removed+=len(indices)
     assert removed==1581;report['transient_PIE_instances_removed_for_comparison']=removed;nxt('settle_baseline')
    else:
     L.editor_request_end_play();nxt('restart')
  elif phase=='settle_baseline' and age>4:state['samples']=[];nxt('sample_baseline')
  elif phase=='restart' and age>2:
   assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');L.editor_request_begin_play();nxt('drive_ready')
  elif phase=='drive_ready':
   world=W.get_game_world()
   if not world or u.GameplayStatics.get_time_seconds(world)<10:return
   pawn=u.GameplayStatics.get_player_pawn(world,0)
   for kart in u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn):kart.set_kart_test_input(0,0,True)
   p=edges['center'][54];q=edges['center'][57];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));pawn.set_actor_location_and_rotation(u.Vector(p[0],p[1],40),u.Rotator(yaw=yaw),False,True);pawn.get_component_by_class(u.KartTireDynamics).reset_motion();pawn.set_kart_test_input(.5,-.18,False);state['pawn']=pawn;state['drive_start']=list(pawn.get_actor_location().to_tuple());nxt('drive')
  elif phase=='drive' and age>3:
   pawn=state['pawn'];end=list(pawn.get_actor_location().to_tuple());report['PIE_low_speed_corner_probe']={'start':state['drive_start'],'end':end,'distance_cm':math.dist(end,state['drive_start']),'upright_roll':pawn.get_actor_rotation().roll,'duration_seconds':age};assert math.dist(end,state['drive_start'])>100;assert abs(pawn.get_actor_rotation().roll)<5
   pawn.set_kart_test_input(0,0,True);L.editor_request_end_play();nxt('finish')
  elif phase=='finish' and age>2:
   report['limitations']='Slate frame intervals in offscreen editor PIE, not a packaged GPU benchmark. No full lap or high-speed barrier impact test. Temporary aerial culling/PIE comparison changes were never saved.';finish()
 except Exception:
  report['error']=traceback.format_exc();(E/'final_error.txt').write_text(report['error']);u.log_error(report['error'])
  if L.is_in_play_in_editor():L.editor_request_end_play()
  finish()
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

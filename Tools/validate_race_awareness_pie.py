import unreal as u,time,json,traceback,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/RaceAwareness';L=u.get_editor_subsystem(u.LevelEditorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Content/RoadToF1/Maps','Content/RoadToF1/RacingAI'] for p in (R/folder).rglob('*') if p.is_file()}
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
u.EditorPythonScripting.set_keep_python_script_alive(True)
state={'phase':0,'epoch':time.monotonic(),'start':time.monotonic(),'busy':False};result={'input_method':'Existing bound actions invoked via Unreal Python, not synthesized keyboard input.'}
def advance():state.update(phase=state['phase']+1,epoch=time.monotonic())
def shot(n):u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/(n+'.png')))
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  p=state['phase'];age=time.monotonic()-state['epoch']
  if time.monotonic()-state['start']>100:raise RuntimeError('PIE timeout')
  if p==0:
   if age>3:L.editor_request_begin_play();advance()
   return
  if p>=9:
   if age>2:
    result['map_and_route_unchanged']=all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in protected.items())
    (E/'pie_result.json').write_text(json.dumps(result,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
   return
  world=W.get_game_world()
  if not world:return
  pc=u.GameplayStatics.get_player_controller(world,0);pawn=u.GameplayStatics.get_player_pawn(world,0)
  if not pc or not pawn or not pc.get_hud():return
  a=pc.get_hud().get_component_by_class(u.KartRaceAwareness);nav=pc.get_hud().get_component_by_class(u.KartNavigationMap)
  if not a:return
  cams=lambda:{c.get_name():c.is_active() for c in pawn.get_components_by_class(u.CameraComponent)}
  if p==1 and age>3:
   assert a.get_editor_property('rear_capture_count')>0;assert a.get_editor_property('mirror_target').size_x==640
   result['mirror_capture_size']=[640,160];result['kart_count']=len(u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn));shot('rear_mirror_grid');advance()
  elif p==2 and age>2:
   for k in u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn):k.set_kart_test_input(0,0,True)
   others=[k for k in u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn) if k!=pawn]
   origin=pawn.get_actor_location();q=pawn.get_actor_rotation();right=pawn.get_actor_right_vector();forward=pawn.get_actor_forward_vector()
   others[0].set_actor_location(origin+right*190,False,True);others[1].set_actor_location(origin-right*190,False,True);others[2].set_actor_location(origin-forward*550,False,True)
   a.begin_look_back();advance()
  elif p==3 and age>2:
   assert a.get_editor_property('looking_back');assert cams()['KartLookBackCamera'];shot('hold_C_look_back');result['rear_camera_active']=True;advance()
  elif p==4 and age>2:
   a.end_look_back();assert cams()['DriverEye'];pawn.toggle_camera_view();a.begin_look_back();a.end_look_back();assert cams()['ChaseCamera'];pawn.toggle_camera_view();advance()
  elif p==5 and age>2:
   assert cams()['DriverEye'];assert a.get_editor_property('tracked_opponent_count')>=2;shot('nearby_opponents');result['camera_restore_both_modes']=True;result['nearby_count']=a.get_editor_property('tracked_opponent_count');state['sample_count']=a.get_editor_property('rear_capture_count');advance()
  elif p==6 and age>2:
   if not state.get('off_started'):
    result['observed_mirror_hz']=(a.get_editor_property('rear_capture_count')-state['sample_count'])/age;assert result['observed_mirror_hz']<=20.5
    a.toggle_mirror();state['capture']=a.get_editor_property('rear_capture_count');state['off_started']=True;state['epoch']=time.monotonic();return
   assert a.get_editor_property('rear_capture_count')==state['capture'];result['mirror_off_stops_rendering']=True;a.toggle_mirror();a.begin_look_back();nav.toggle_map();advance()
  elif p==7 and age>2:
   assert not a.get_editor_property('looking_back');state['capture']=a.get_editor_property('rear_capture_count');advance()
  elif p==8 and age>2:
   assert a.get_editor_property('rear_capture_count')==state['capture'];nav.close_map();result['map_suppresses_and_restores_camera']=True;result['final_cameras']=cams();L.editor_request_end_play();advance()
 except Exception:
  result['error']=traceback.format_exc();u.log_error(result['error']);L.editor_request_end_play();state.update(phase=9,epoch=time.monotonic())
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

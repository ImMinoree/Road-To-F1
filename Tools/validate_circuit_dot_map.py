import unreal as u,time,json,traceback
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/CircuitDotMap';L=u.get_editor_subsystem(u.LevelEditorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
route=list(u.load_asset('/Game/RoadToF1/RacingAI/DA_DesertTrackEdges').get_editor_property('center'))
u.EditorPythonScripting.set_keep_python_script_alive(True)
s={'phase':0,'epoch':time.monotonic(),'start':time.monotonic(),'busy':False};r={'staging':'Existing AI karts repositioned only in unsaved PIE for dot visibility and close-arrow screenshots.'}
def nxt():s.update(phase=s['phase']+1,epoch=time.monotonic())
def shot(n):u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/(n+'.png')))
def tick(dt):
 if s['busy']:return
 s['busy']=True
 try:
  p=s['phase'];age=time.monotonic()-s['epoch']
  if p>=6:
   if age>2:(E/'result.json').write_text(json.dumps(r,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
   return
  if time.monotonic()-s['start']>100:raise RuntimeError('timeout')
  if p==0:
   if age>3:L.editor_request_begin_play();nxt()
   return
  world=W.get_game_world()
  if not world:return
  pc=u.GameplayStatics.get_player_controller(world,0);pawn=u.GameplayStatics.get_player_pawn(world,0)
  if not pc or not pawn or not pc.get_hud():return
  nav=pc.get_hud().get_component_by_class(u.KartNavigationMap)
  others=[k for k in u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn) if k!=pawn]
  if p==1 and age>4:
   pawn.set_kart_test_input(0,0,True)
   for i,k in enumerate(others):
    k.set_kart_test_input(0,0,True);v=route[int((i+1)*len(route)/(len(others)+1))];k.set_actor_location(u.Vector(v.x,v.y,pawn.get_actor_location().z),False,True)
   nxt()
  elif p==2 and age>3:
   assert nav.get_editor_property('displayed_kart_count')==len(others)+1;r['all_karts_on_map']=len(others)+1;shot('full_circuit_dots');nxt()
  elif p==3 and age>2:
   origin=pawn.get_actor_location();right=pawn.get_actor_right_vector()
   others[0].set_actor_location(origin+right*190,False,True);others[1].set_actor_location(origin-right*190,False,True);nxt()
  elif p==4 and age>2:shot('close_kart_arrows');nxt()
  elif p==5 and age>2:
   nav.toggle_map();assert nav.is_map_open();r['full_screen_map_opens']=True;nav.close_map();L.editor_request_end_play();r['pie_completed']=True;nxt()
 except Exception:
  r['error']=traceback.format_exc();u.log_error(r['error']);L.editor_request_end_play();s.update(phase=6,epoch=time.monotonic())
 finally:s['busy']=False
handle=u.register_slate_post_tick_callback(tick)

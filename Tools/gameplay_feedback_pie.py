import unreal as u,time,json,traceback
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/GameplayCompetition/Feedback';E.mkdir(parents=True,exist_ok=True)
L=u.get_editor_subsystem(u.LevelEditorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
u.EditorPythonScripting.set_keep_python_script_alive(True);assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
s={'start':time.monotonic(),'phase':'start','busy':False,'shots':[]}
for c in ['t.MaxFPS 0','t.IdleWhenNotForeground 0','Slate.bAllowThrottling 0']:u.SystemLibrary.execute_console_command(None,c)
def tick(dt):
 if s['busy']:return
 s['busy']=True
 try:
  if time.monotonic()-s['start']>180:raise RuntimeError('Feedback PIE timeout')
  if s['phase']=='start':L.editor_request_begin_play();s['phase']='play';return
  if s['phase']=='finish':
   if time.monotonic()-s['end']>1:u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
   return
  world=W.get_game_world()
  if not world:return
  gm=u.GameplayStatics.get_game_mode(world);p=u.GameplayStatics.get_player_pawn(world,0)
  if not gm or not p:return
  p.set_kart_test_input(.65,0,False)
  if gm.is_start_gate_closed():
   if gm.red_light_count==5 and 'staged' not in s['shots']:s['shots'].append('staged');u.SystemLibrary.execute_console_command(world,'Shot filename='+str(E/'staged.png'))
   return
  t=gm.get_race_elapsed_seconds()
  if t>7:p.set_kart_test_input(0,0,True)
  if t>5 and 'feedback' not in s['shots']:s['shots'].append('feedback');u.SystemLibrary.execute_console_command(world,'Shot filename='+str(E/'feedback.png'))
  if t>10:
   d={'ui_only_straight_line_test':True,'normal_player_progress_observer':True,'race_seconds':t,'start_events':gm.start_event_count,'pawns':len(u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn)),'player_collisions':p.get_component_by_class(u.KartTireDynamics).collision_count,'shots':s['shots']};(E/'result.json').write_text(json.dumps(d,indent=2));L.editor_request_end_play();s.update(phase='finish',end=time.monotonic())
 except Exception:
  (E/'result.json').write_text(json.dumps({'error':traceback.format_exc()},indent=2));L.editor_request_end_play();s.update(phase='finish',end=time.monotonic())
 finally:s['busy']=False
handle=u.register_slate_post_tick_callback(tick)

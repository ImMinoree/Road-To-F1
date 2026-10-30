"""Real PIE speed-gauge captures: stopped, acceleration, mph, reverse, map."""
import unreal as u,json,time,traceback,hashlib,math
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/SpeedGauge';E.mkdir(exist_ok=True)
protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'Content/RoadToF1/Maps').glob('*.umap')}
L=u.get_editor_subsystem(u.LevelEditorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');u.EditorPythonScripting.set_keep_python_script_alive(True)
for cmd in ['t.MaxFPS 45','r.ScreenPercentage 100','kart.SpeedGauge.Debug 1','kart.SpeedGauge.MPH 0']:u.SystemLibrary.execute_console_command(None,cmd)
state={'phase':'start','epoch':time.monotonic(),'busy':False,'samples':[],'shots':[],'start':time.monotonic()}
def phase(name):state.update(phase=name,epoch=time.monotonic())
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  if time.monotonic()-state['start']>200:raise RuntimeError('Speed gauge PIE timeout')
  age=time.monotonic()-state['epoch'];p=state['phase']
  if p=='start' and age>5:L.editor_request_begin_play();phase('initialize');return
  if not L.is_in_play_in_editor():return
  world=W.get_game_world();pawn=u.GameplayStatics.get_player_pawn(world,0)
  if not isinstance(pawn,u.ProofPawn):return
  pc=u.GameplayStatics.get_player_controller(world,0);dyn=pawn.get_component_by_class(u.KartTireDynamics)
  def snapshot(name):
   v=pawn.get_velocity();t=dyn.get_telemetry();kmh=math.hypot(v.x,v.y)*.036
   state['samples'].append({'phase':name,'kmh':kmh,'longitudinal_mps':t.longitudinal_speed_mps,'expected_kmh_display':int(kmh+.5),'expected_mph_display':int(kmh*.621371192+.5)})
   u.log('SPEED_GAUGE_CAPTURE '+json.dumps(state['samples'][-1]));u.SystemLibrary.execute_console_command(world,'Shot filename='+str(E/(name+'.png')));state['shots'].append(name)
  if p=='initialize':
   if u.GameplayStatics.get_time_seconds(world)<10:return
   if pawn.is_third_person_view():pawn.toggle_camera_view()
   state['origin']=pawn.get_actor_location();state['rotation']=pawn.get_actor_rotation();pawn.set_kart_test_input(0,0,True);phase('rest')
  elif p=='rest' and age>1:
   snapshot('01_stationary');assert state['samples'][-1]['kmh']<.1;pawn.set_kart_test_input(1,0,False);phase('accelerate')
  elif p=='accelerate':
   if age>12:raise AssertionError('Kart did not accelerate')
   if dyn.get_telemetry().longitudinal_speed_mps>6.2:
    snapshot('02_accelerating_kmh');phase('kmh_capture')
  elif p=='kmh_capture' and age>.7:
   u.SystemLibrary.execute_console_command(world,'kart.SpeedGauge.MPH 1');phase('mph')
  elif p=='mph' and age>1.5:
   snapshot('03_accelerating_mph');phase('mph_capture')
  elif p=='mph_capture' and age>.7:
   u.SystemLibrary.execute_console_command(world,'kart.SpeedGauge.MPH 0');pawn.set_actor_location_and_rotation(state['origin'],state['rotation'],False,True);dyn.reset_motion();pawn.set_kart_test_input(-1,0,False);phase('reverse')
  elif p=='reverse':
   if age>12:raise AssertionError('Reverse movement not exercised')
   if age>2 and dyn.get_telemetry().longitudinal_speed_mps<-.75:
    snapshot('04_reverse');phase('reverse_capture')
  elif p=='reverse_capture' and age>.7:
   pawn.set_kart_test_input(0,0,True);phase('brake')
  elif p=='brake' and age>2:
   snapshot('05_braked');phase('braked_capture')
  elif p=='braked_capture' and age>.7:
   nav=pc.get_hud().get_component_by_class(u.KartNavigationMap);assert nav;state['nav']=nav;nav.toggle_map();phase('map')
  elif p=='map' and age>1.5:
   assert state['nav'].is_map_open();snapshot('06_full_map');phase('map_capture')
  elif p=='map_capture' and age>.7:
   state['nav'].close_map();phase('finish')
  elif p=='finish' and age>2:
   assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in protected.items())
   (E/'validation.json').write_text(json.dumps({'actual_pie':True,'passed':True,'samples':state['samples'],'screenshots':state['shots'],'maps_unchanged':True,'source':'AProofPawn::GetVelocity() planar magnitude, cm/s to km/h; optional mph conversion','limits':'Arc is speed, not RPM. No simulated gearbox is displayed.'},indent=2))
   u.SystemLibrary.execute_console_command(world,'kart.SpeedGauge.Debug 0');L.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 except Exception:
  (E/'error.txt').write_text(traceback.format_exc());u.log_error(traceback.format_exc())
  if L.is_in_play_in_editor():L.editor_request_end_play()
  u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

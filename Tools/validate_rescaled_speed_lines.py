"""Real velocity PIE checks plus explicitly labelled >cap shader preview. No physics edits."""
import unreal as u,time,json,traceback,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/AnimeSpeedLines/Rescaled';L=u.get_editor_subsystem(u.LevelEditorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Content/RoadToF1/Maps','Source/Road_To_F1_New'] for p in (R/folder).rglob('*') if p.is_file()}
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');u.EditorPythonScripting.set_keep_python_script_alive(True)
s={'phase':0,'epoch':time.monotonic(),'start':time.monotonic(),'busy':False,'shots':set()};r={'samples':[],'input_method':'Existing development throttle action, real vehicle velocity. No physics parameters changed.','above_cap_preview':'No simulated speed or strength override: actual vehicle velocity drives every capture. Full strength at 61 km/h is covered by the speed-response unit test.'}
def nxt():s.update(phase=s['phase']+1,epoch=time.monotonic())
def shot(name):u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/(name+'.png')))
def tick(dt):
 if s['busy']:return
 s['busy']=True
 try:
  p=s['phase'];age=time.monotonic()-s['epoch']
  if p>=9:
   if age>2:
    r['protected_files_unchanged']=all(hashlib.sha256((R/k).read_bytes()).hexdigest()==v for k,v in protected.items());(E/'pie_result.json').write_text(json.dumps(r,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
   return
  if time.monotonic()-s['start']>130:raise RuntimeError('Speed-lines PIE timeout')
  if p==0:
   if age>3:L.editor_request_begin_play();nxt()
   return
  world=W.get_game_world()
  if not world:return
  pc=u.GameplayStatics.get_player_controller(world,0);pawn=u.GameplayStatics.get_player_pawn(world,0)
  if not pc or not pawn or not pc.get_hud():return
  fx=pc.get_hud().get_component_by_class(u.KartSpeedLines);gm=u.GameplayStatics.get_game_mode(world)
  if not fx or not fx.get_editor_property('material_instance'):return
  mid=fx.get_editor_property('material_instance');speed=fx.get_editor_property('actual_speed_kmh');strength=fx.get_editor_property('smoothed_strength')
  def sample(name):r['samples'].append({'name':name,'actual_kmh':speed,'strength':strength,'material_strength':mid.get_scalar_parameter_value('LineStrength')})
  if p==1 and age>2:
   sample('grid');assert speed<1 and strength==0;shot('01_stationary_no_lines');pawn.set_kart_test_input(1,0,False);nxt()
  elif p==2:
   if gm.is_start_gate_closed():assert speed<1 and strength==0
   elif not s.get('clear_lane'):
    for i,k in enumerate(u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn)):
     if k!=pawn:k.set_actor_location(u.Vector(100000+i*400,100000,100),False,True);k.set_kart_test_input(0,0,True)
    s['clear_lane']=True;r['test_lane']='Other existing karts parked away only in unsaved PIE to remove traffic variability.'
   for threshold,name in [(15,'02_15kmh_no_lines'),(35,'03_35kmh_subtle'),(50,'04_50kmh_noticeable')]:
    if speed>=threshold and threshold not in s['shots']:
     s['shots'].add(threshold);sample(name);shot(name)
     if threshold==15:assert strength==0
   if speed>=50:
    sample('50kmh_driving');shot('05_50kmh_driving');u.GameplayStatics.set_game_paused(world,True);nxt()
   elif age>35:raise RuntimeError('Could not reach 50kmh on the straight; current speed '+str(speed))
  elif p==3 and age>2:
   assert strength>.5;sample('rescaled_strength_at_real_50');nxt()
  elif p==4 and age>2:shot('06_50kmh_rescaled_actual');nxt()
  elif p==5 and age>2:
   fx.toggle_speed_visuals();assert mid.get_scalar_parameter_value('LineStrength')==0;shot('07_F3_realistic_disabled');r['toggle_immediately_clears_lines']=True;nxt()
  elif p==6 and age>2:
   fx.toggle_speed_visuals();u.GameplayStatics.set_game_paused(world,False);pawn.toggle_camera_view();nxt()
  elif p==7 and age>.5:
   assert fx.get_editor_property('smoothed_strength')==0;assert mid.get_scalar_parameter_value('LineStrength')==0;r['third_person_has_no_speed_lines']=True;pawn.toggle_camera_view();gm.restart_race_start();nxt()
  elif p==8 and age>2:
   assert fx.get_editor_property('smoothed_strength')==0;r['restart_clears_lines']=True;r['single_start_controller']=gm.start_event_count==0;L.editor_request_end_play();nxt()
 except Exception:
  r['error']=traceback.format_exc();u.log_error(r['error']);L.editor_request_end_play();s.update(phase=9,epoch=time.monotonic())
 finally:s['busy']=False
handle=u.register_slate_post_tick_callback(tick)


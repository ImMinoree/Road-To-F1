"""Actual PIE articulation and movement checks on a transient pad, no map saves."""
import unreal as u,json,time,traceback,math,csv
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/PlayerVehicle_v4';E.mkdir(exist_ok=True)
u.EditorPythonScripting.set_keep_python_script_alive(True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);ed=u.get_editor_subsystem(u.UnrealEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
floor=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(-60000,-60000,1950));floor.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE);floor.static_mesh_component.set_collision_profile_name('BlockAll');floor.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(u.Vector(500,500,1));floor.tags=['V4TransientPad','SurfaceAsphalt']
camera_actor=actors.spawn_actor_from_class(u.CameraActor,u.Vector());camera_actor.tags=['V4CaptureCamera']
wall_actor=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(-59400,-50000,2100));wall_actor.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE);wall_actor.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));wall_actor.set_actor_scale3d(u.Vector(1,10,4));wall_actor.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);wall_actor.tags=['V4CollisionWall']
for cmd in ['t.MaxFPS 45','r.ScreenPercentage 100','sg.ShadowQuality 2','r.MotionBlurQuality 0']:u.SystemLibrary.execute_console_command(None,cmd)
def spawn(world,cls,location):
 tr=u.Transform(location=location);a=u.GameplayStatics.begin_deferred_actor_spawn_from_class(world,cls,tr,u.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN);return u.GameplayStatics.finish_spawning_actor(a,tr)
state={'start':time.monotonic(),'started':False,'busy':False,'phase':'grid_center','epoch':0,'rows':[],'shots':[],'checks':{},'grips':None,'max_grip_error':0,'max_rod_error':0,'reverse_seen':False,'forward_seen':False,'drift_seen':False,'collision_start':0,'last_rear':None,'wheel_changes':0}
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  if time.monotonic()-state['start']>300:raise RuntimeError('PIE timeout')
  if not state['started'] and time.monotonic()-state['start']>3:state['started']=True;level.editor_request_begin_play()
  if not level.is_in_play_in_editor():return
  world=ed.get_game_world()
  if not world:return
  pawn=u.GameplayStatics.get_player_pawn(world,0)
  if not pawn:return
  mech=pawn.get_component_by_class(u.KartMechanicalVisuals);dyn=pawn.get_component_by_class(u.KartTireDynamics);gm=u.GameplayStatics.get_game_mode(world);pc=u.GameplayStatics.get_player_controller(world,0)
  assert mech and mech.get_editor_property('ready'),'versioned visual assembly failed to initialize'
  t=u.GameplayStatics.get_time_seconds(world);phase=state['phase'];age=t-state['epoch'];pos=pawn.get_actor_location();slip=dyn.get_telemetry()
  if 'grid' not in state:state['grid']=pos
  def next_phase(name):state['phase']=name;state['epoch']=t
  def external():
   if not pawn.is_third_person_view():pawn.toggle_camera_view()
  def cockpit():
   if pawn.is_third_person_view():pawn.toggle_camera_view()
   pc.set_view_target_with_blend(pawn,0)
  def camera(offset,target):
   external()
   if 'camera' not in state:state['camera']=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.CameraActor) if 'V4CaptureCamera' in list(map(str,a.tags)))
   c=state['camera'];tr=pawn.get_actor_transform();where=tr.transform_location(u.Vector(*offset));look=tr.transform_location(u.Vector(*target));c.set_actor_location_and_rotation(where,u.MathLibrary.find_look_at_rotation(where,look),False,True);c.camera_component.set_field_of_view(55);pc.set_view_target_with_blend(c,0)
  def shot(name):
   if name not in state['shots']:u.SystemLibrary.execute_console_command(world,'Shot filename='+str(E/(name+'.png')));state['shots'].append(name)
  parts={c.get_name():c for c in pawn.get_components_by_class(u.StaticMeshComponent)}
  wheel=parts['V4_SteeringWheel_17'];sampler=next(c for c in pawn.get_components_by_class(u.SkeletalMeshComponent) if c.get_name()=='V4_DriverPoseSampler')
  wt=wheel.get_world_transform();grips=[wt.inverse_transform_location(sampler.get_socket_location('hand_'+side)) for side in ['l','r']]
  if not state['grips']:state['grips']=grips
  error=max((grips[i]-state['grips'][i]).length() for i in range(2));state['max_grip_error']=max(state['max_grip_error'],error)
  rod=mech.get_editor_property('maximum_rod_error_cm');state['max_rod_error']=max(state['max_rod_error'],rod);assert rod<.05,('rod length',rod)
  rear=mech.get_editor_property('rear_rolling_degrees')
  if state['last_rear'] is not None and abs(rear-state['last_rear'])>.01:state['wheel_changes']+=1
  state['last_rear']=rear
  row={'t':t,'phase':phase,'u_mps':slip.longitudinal_speed_mps,'steer_deg':slip.steering_degrees,'left_deg':mech.get_editor_property('left_steering_degrees'),'right_deg':mech.get_editor_property('right_steering_degrees'),'column_deg':mech.get_editor_property('column_degrees'),'rear_roll_deg':rear,'rod_error_cm':rod,'grip_error_cm':error,'brake':mech.get_editor_property('brake_pedal'),'throttle':mech.get_editor_property('throttle_pedal'),'rear_slip_deg':slip.rear_slip_degrees,'drifting':slip.drifting,'collision_count':dyn.collision_count,'grounded':slip.grounded_wheels,'x':pos.x,'y':pos.y,'z':pos.z}
  state['rows'].append(row)
  assert (phase=='restart' and age<.1) or abs((row['left_deg']+row['right_deg'])*.5-slip.steering_degrees)<.05,('physics visual disagreement',row)
  if phase=='grid_center':
   pawn.set_kart_test_input(1,0,False);camera((230,-260,130),(0,0,20))
   if age>1.5:shot('01_front_three_quarter')
   if age>2.5:camera((180,0,230),(30,0,0))
   if age>3:shot('02_steering_center');state['checks']['A']=True;next_phase('grid_left')
  elif phase=='grid_left':
   pawn.set_kart_test_input(1,-1,False);camera((160,-150,120),(50,0,0))
   if age>1:assert row['left_deg']<row['right_deg']<0;shot('03_full_left');state['checks']['B']=True;next_phase('grid_right')
  elif phase=='grid_right':
   pawn.set_kart_test_input(1,1,False);camera((160,150,120),(50,0,0))
   if age>1:assert row['right_deg']>row['left_deg']>0;shot('04_full_right');state['checks']['C']=True;next_phase('counter')
  elif phase=='counter':
   pawn.set_kart_test_input(0,math.sin(age*12),False);cockpit()
   if age>1:shot('06_cockpit_countersteer')
   shot('motion_'+str(min(9,int(age*5))).zfill(2))
   if age>2:state['checks']['D']=True;next_phase('cockpit_center')
  elif phase=='cockpit_center':
   pawn.set_kart_test_input(0,0,False);cockpit()
   if age>.8:shot('05_cockpit_center')
   if t>9:
    state['checks']['L']=(pos-state['grid']).length()<1 and gm.start_event_count==1
    pawn.set_actor_location_and_rotation(u.Vector(-60000,-60000,2031),u.Rotator(),False,True);dyn.reset_motion();next_phase('forward')
  elif phase=='forward':
   pawn.set_kart_test_input(1,0,False);external();pc.set_view_target_with_blend(pawn,0)
   if age>6 and slip.longitudinal_speed_mps<=3:raise AssertionError(('acceleration',row))
   if age>3 and slip.longitudinal_speed_mps>3:shot('07_external_driving');state['checks']['E']=True;next_phase('rolling_turn')
  elif phase=='rolling_turn':
   pawn.set_kart_test_input(.8,.25,False)
   if age>2:state['checks']['G']=abs(row['left_deg'])>1 and state['wheel_changes']>30;state['checks']['I']=rod<.05;next_phase('brake')
  elif phase=='brake':
   pawn.set_kart_test_input(0,.25,True);state['drift_seen']=state['drift_seen'] or slip.drifting
   if age>.6:state['checks']['H']=row['brake']>.9;next_phase('recover')
  elif phase=='recover':
   beta=math.radians(slip.sideslip_degrees);yaw=math.radians(slip.yaw_rate_degrees);steer=max(-.9,min(.9,beta*1.5-yaw*.12));pawn.set_kart_test_input(.4,steer,False);state['drift_seen']=state['drift_seen'] or slip.drifting
   if age>4:state['checks']['J']=state['drift_seen'];next_phase('reverse')
  elif phase=='reverse':
   pawn.set_kart_test_input(-1,0,False)
   if slip.longitudinal_speed_mps<-.5:state['reverse_seen']=True
   if age>9:
    state['checks']['F']=state['reverse_seen'];pawn.set_actor_location_and_rotation(u.Vector(-60000,-60000,2031),u.Rotator(),False,True);dyn.reset_motion();state['collision_start']=dyn.collision_count
    wall=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.StaticMeshActor) if 'V4CollisionWall' in list(map(str,a.tags)));wall.set_actor_location(u.Vector(-59400,-60000,2100),False,True);wall.static_mesh_component.set_collision_profile_name('BlockAll');wall.static_mesh_component.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS);next_phase('collision')
  elif phase=='collision':
   pawn.set_kart_test_input(1,0,False)
   if dyn.collision_count>state['collision_start']:
    state['collision_seen']=True;gm.restart_race_start();state['restart_grid']=pawn.get_actor_location();next_phase('restart')
   elif age>7:raise AssertionError('collision not exercised')
  elif phase=='restart':
   pawn.set_kart_test_input(1,1,False)
   if age>1:
    state['checks']['K']=state.get('collision_seen',False) and (pos-state['restart_grid']).length()<1 and abs(slip.longitudinal_speed_mps)<.001
    result={'actual_pie':True,'checks':state['checks'],'maximum_rod_length_error_cm':state['max_rod_error'],'maximum_hand_relative_wheel_error_cm':state['max_grip_error'],'screenshots':state['shots'],'frames':len(state['rows']),'wheel_rotation_frames':state['wheel_changes'],'limits':'Wheel spin uses ground velocity; no tire angular-speed state exists. Mesh surface intersections require visual review.'}
    result['passed']=all(result['checks'].values()) and state['max_grip_error']<.6
    (E/'validation.json').write_text(json.dumps(result,indent=2));next_phase('finish')
  elif phase=='finish' and age>1:
   with (E/'motion.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(state['rows'][0]));w.writeheader();w.writerows(state['rows'])
   level.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 except Exception:
  (E/'attempt_rows.json').write_text(json.dumps(state['rows'],indent=2));(E/'attempt_checks.json').write_text(json.dumps({'checks':state['checks'],'hand_error':state['max_grip_error'],'rod_error':state['max_rod_error']},indent=2));(E/'pie_error.txt').write_text(traceback.format_exc());u.log_error(traceback.format_exc());level.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)







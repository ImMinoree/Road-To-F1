"""Actual ten-kart PIE grid/livery/racing check and isolated shared-speed test. No map saves."""
import unreal as u,json,time,traceback,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/TenKartGrid';E.mkdir(exist_ok=True)
u.EditorPythonScripting.set_keep_python_script_alive(True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);ed=u.get_editor_subsystem(u.UnrealEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
protected={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'Content/RoadToF1/Maps').glob('*.umap')}
camera=actors.spawn_actor_from_class(u.CameraActor,u.Vector());camera.tags=['TenKartCaptureCamera']
pad=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(-60000,-60000,1950));pad.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE);pad.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'));pad.static_mesh_component.set_collision_profile_name('BlockAll');pad.set_actor_scale3d(u.Vector(500,500,1));pad.tags=['SurfaceAsphalt','TenKartTransientTestPad']
for cmd in ['t.MaxFPS 45','r.ScreenPercentage 100','sg.ShadowQuality 2','r.MotionBlurQuality 0']:u.SystemLibrary.execute_console_command(None,cmd)
S={'start':time.monotonic(),'begun':False,'busy':False,'shots':[],'rows':[],'grid':None,'speed_start':None,'done':None,'camera':None,'peaks':{},'motion':{}}
def color(c):return [round(c.r,4),round(c.g,4),round(c.b,4)]
def tick(dt):
 if S['busy']:return
 S['busy']=True
 try:
  if time.monotonic()-S['start']>360:raise RuntimeError('Ten-kart PIE validation timeout')
  if not S['begun'] and time.monotonic()-S['start']>3:S['begun']=True;level.editor_request_begin_play()
  if not level.is_in_play_in_editor():return
  world=ed.get_game_world()
  if not world:return
  player=u.GameplayStatics.get_player_pawn(world,0);gm=u.GameplayStatics.get_game_mode(world)
  if not player or not gm:return
  t=u.GameplayStatics.get_time_seconds(world);pawns=list(u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn));pc=u.GameplayStatics.get_player_controller(world,0)
  if gm.get_editor_property('staged_participant_count')<10:return
  assert len(pawns)==10,len(pawns)
  pawns.sort(key=lambda p:p.get_editor_property('assigned_grid_position'))
  assert [p.get_editor_property('assigned_grid_position') for p in pawns]==list(range(1,11))
  if S['camera'] is None:S['camera']=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.CameraActor) if 'TenKartCaptureCamera' in list(map(str,a.tags)))
  def view(where,target,fov=65):
   c=S['camera'];c.set_actor_location_and_rotation(where,u.MathLibrary.find_look_at_rotation(where,target),False,True);c.camera_component.set_field_of_view(fov);pc.set_view_target_with_blend(c,0)
  def shot(name):
   if name not in S['shots']:u.SystemLibrary.execute_console_command(world,'Shot filename='+str(E/(name+'.png')));S['shots'].append(name)
  if S['grid'] is None:
   rows=[]
   for p in pawns:
    v=p.get_component_by_class(u.KartMechanicalVisuals);assert v and v.get_editor_property('ready'),p.get_name()
    slot=p.get_editor_property('assigned_grid_position');assert v.get_editor_property('livery_slot')==slot
    names=[c.get_name() for c in p.get_components_by_class(u.MeshComponent)]
    assert 'V4_SeatedDriver' in names
    if p!=player:assert 'V4_CockpitDriver' not in names,'AI created owner-only POV'
    assert not any(n.startswith('StaticMeshComponent_') for n in names),'duplicate legacy AI renderer'
    chassis=next(c for c in p.get_components_by_class(u.StaticMeshComponent) if c.get_name()=='V4_Chassis_0')
    assert '/PlayerVehicleV4/' in chassis.static_mesh.get_path_name()
    mids=[chassis.get_material(i) for i in range(chassis.get_num_materials()) if isinstance(chassis.get_material(i),u.MaterialInstanceDynamic)]
    assert mids,('missing actual kart livery',p.get_name())
    actual=color(mids[0].get_vector_parameter_value('LiveryColor'));expected=color(v.get_editor_property('kart_color'));assert actual==expected,(actual,expected)
    dyn=p.get_component_by_class(u.KartTireDynamics);assert abs(dyn.get_editor_property('maximum_forward_speed_mph')-38)<.001
    rows.append({'slot':slot,'player':p==player,'kart_color':expected,'driver_color':color(v.get_editor_property('driver_color')),'chassis':chassis.static_mesh.get_path_name(),'pose_components':names,'grid_cm':[p.get_actor_location().x,p.get_actor_location().y,p.get_actor_location().z],'top_speed_mph':38})
    S['motion'][slot]=p.get_actor_location();S['peaks'][slot]=0
   assert player.get_editor_property('assigned_grid_position')==10
   assert len({tuple(r['kart_color']) for r in rows})==10
   assert len({tuple(r['driver_color']) for r in rows})==10
   assert all(r['kart_color']!=r['driver_color'] for r in rows)
   S['grid']=rows;(E/'grid.json').write_text(json.dumps(rows,indent=2))
  if S['speed_start'] is None:
   positions=[p.get_actor_location() for p in pawns];center=u.Vector(sum(p.x for p in positions)/10,sum(p.y for p in positions)/10,60)
   view(center+u.Vector(-1100,-2200,1700),center,65)
   if t>3:shot('01_ten_kart_grid')
   if 4.5<t<6.5:
    focus=pawns[0].get_actor_location();view(focus+u.Vector(230,-350,150),focus+u.Vector(0,0,20),65);shot('02_matching_ai_model')
   if t>13:shot('03_ten_karts_racing')
   if t>18:
    assert gm.get_editor_property('start_event_count')==1
    movement={p.get_editor_property('assigned_grid_position'):(p.get_actor_location()-S['motion'][p.get_editor_property('assigned_grid_position')]).length() for p in pawns if p!=player}
    assert all(d>50 for d in movement.values()),movement
    (E/'race_movement.json').write_text(json.dumps(movement,indent=2))
    ai=gm.get_component_by_class(u.TrackRacingAI);assert ai;ai.set_component_tick_enabled(False)
    for i,p in enumerate(pawns):
     p.set_actor_location_and_rotation(u.Vector(-60000,-61600+i*400,2031),u.Rotator(),False,True);p.get_component_by_class(u.KartTireDynamics).reset_motion();p.set_kart_test_input(1,0,False)
    S['speed_start']=t
  else:
   for p in pawns:
    p.set_kart_test_input(1,0,False);slot=p.get_editor_property('assigned_grid_position');mph=p.get_component_by_class(u.KartTireDynamics).get_telemetry().longitudinal_speed_mps/.44704;S['peaks'][slot]=max(S['peaks'][slot],mph)
    assert mph<=38.02,(slot,mph)
   focus=player.get_actor_location();view(focus+u.Vector(-600,-2200,1200),focus+u.Vector(300,-1600,0),75)
   if t-S['speed_start']>12:shot('04_shared_38mph_test')
   if t-S['speed_start']>14 and S['done'] is None:
    assert all(37.9<=v<=38.02 for v in S['peaks'].values()),S['peaks']
    result={'passed':True,'actual_pie':True,'kart_count':len(pawns),'ai_count':9,'player_grid_slot':10,'unique_kart_colors':10,'unique_driver_colors':10,'peak_mph_by_slot':S['peaks'],'shots':S['shots'],'maps_unchanged':protected=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'Content/RoadToF1/Maps').glob('*.umap')}}
    assert result['maps_unchanged'];(E/'validation.json').write_text(json.dumps(result,indent=2));S['done']=time.monotonic()
  if S['done'] and time.monotonic()-S['done']>3:
   level.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 except Exception:
  (E/'error.txt').write_text(traceback.format_exc());u.log_error(traceback.format_exc());u.unregister_slate_post_tick_callback(handle);level.editor_request_end_play();u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:S['busy']=False
handle=u.register_slate_post_tick_callback(tick)

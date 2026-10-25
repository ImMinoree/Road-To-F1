"""Short actual PIE presentation/start check; full two-lap checks use the accelerated native run."""
import unreal as u,json,time,traceback,hashlib
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/RacingAI';EV.mkdir(exist_ok=True)
u.EditorPythonScripting.set_keep_python_script_alive(True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
editor_camera=actors.spawn_actor_from_class(u.CameraActor,u.Vector(2000,-1300,1000));editor_camera.tags=['RacingAIValidationCamera']
protected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Content/RoadToF1/Maps').glob('*.umap')}
for command in ['t.MaxFPS 60','r.ScreenPercentage 85','sg.ShadowQuality 2']:u.SystemLibrary.execute_console_command(None,command)
state={'start':time.monotonic(),'wall':time.time(),'started':False,'camera':None,'shot':0,'finish':None,'busy':False}
def tick(dt):
    if state['busy']:return
    state['busy']=True
    try:
        if not state['started'] and time.monotonic()-state['start']>6:
            state['started']=True;level.editor_request_begin_play()
        if not level.is_in_play_in_editor():return
        world=u.EditorLevelLibrary.get_game_world()
        if not world:return
        pawns=u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn);opponents=[p for p in pawns if p.get_editor_property('preferred_grid_position')>=2]
        assert len(pawns)==5 and len(opponents)==4,(len(pawns),len(opponents))
        pc=u.GameplayStatics.get_player_controller(world,0)
        positions=[p.get_actor_location() for p in opponents]
        center=u.Vector(sum(p.x for p in positions)/4,sum(p.y for p in positions)/4,70)
        location=center+u.Vector(-1000,-1350,950)
        rotation=u.MathLibrary.find_look_at_rotation(location,center)
        if state['camera'] is None:
            state['camera']=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.CameraActor) if 'RacingAIValidationCamera' in list(map(str,a.tags)))
            state['camera'].camera_component.set_field_of_view(65)
            pc.set_view_target_with_blend(state['camera'],0)
        state['camera'].set_actor_location_and_rotation(location,rotation,False,False)
        elapsed=u.GameplayStatics.get_time_seconds(world)
        times=[6.7,12,25];names=['four_ai_grid','four_ai_launch','four_ai_racing']
        if state['shot']<3 and elapsed>times[state['shot']]:
            name=names[state['shot']];state['shot']+=1
            u.SystemLibrary.execute_console_command(world,'HighResShot 1600x900 filename='+str(EV/(name+'.png')),pc)
        if elapsed>32 and state['finish'] is None:
            current=json.loads((EV/'progress.json').read_text());assert current['world_type']==3 and current['staged']==5 and current['start_events']==1
            assert all(r['maximum_grid_movement_cm']<1 and r['distance_cm']>2000 and r['driver_visible'] for r in current['racers'])
            state['finish']=time.monotonic();(EV/'pie_validation.json').write_text(json.dumps({'actual_pie':True,'pawns':5,'ai_opponents':4,'all_visible_and_moving':True,'telemetry':current,'maps_unchanged':protected=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Content/RoadToF1/Maps').glob('*.umap')}},indent=2))
        if state['finish'] and time.monotonic()-state['finish']>3:
            level.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
        if time.monotonic()-state['start']>150:raise RuntimeError('PIE validation timed out')
    except Exception:
        (EV/'pie_error.txt').write_text(traceback.format_exc());u.log_error(traceback.format_exc());u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
    finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

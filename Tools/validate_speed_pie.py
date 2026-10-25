"""Actual cockpit PIE check: rest, driving, disable, re-enable and race reset."""
import unreal as u, json, time, traceback, hashlib, math
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve();ev=root/'Evidence/SpeedEffects';ev.mkdir(parents=True,exist_ok=True)
protected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'Content/RoadToF1/Maps').glob('*.umap')}
u.EditorPythonScripting.set_keep_python_script_alive(True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
for command in ['t.MaxFPS 60','r.ScreenPercentage 100','sg.ShadowQuality 2']:
    u.SystemLibrary.execute_console_command(None,command)
state={'start':time.monotonic(),'started':False,'stage':0,'samples':[],'busy':False,'finish':None}
def tick(dt):
    if state['busy']:return
    state['busy']=True
    try:
        if time.monotonic()-state['start']>180:raise RuntimeError('Speed PIE timeout')
        if not state['started'] and time.monotonic()-state['start']>6:
            state['started']=True;level.editor_request_begin_play()
        if not level.is_in_play_in_editor():return
        world=u.EditorLevelLibrary.get_game_world()
        if not world:return
        pc=u.GameplayStatics.get_player_controller(world,0);pawn=u.GameplayStatics.get_player_pawn(world,0)
        if not pawn:return
        cam=pawn.get_component_by_class(u.CameraComponent);visual=pawn.get_component_by_class(u.LocalKartDriverVisuals)
        elapsed=u.GameplayStatics.get_time_seconds(world)
        blendables=cam.post_process_settings.weighted_blendables.array
        mid=next((b.object for b in blendables if isinstance(b.object,u.MaterialInstanceDynamic)),None)
        if mid is None:return
        def sample(name):
            pos=cam.get_editor_property('relative_location');rot=cam.get_editor_property('relative_rotation')
            row={'name':name,'world_seconds':elapsed,'fov':cam.field_of_view,'blur_strength':mid.get_scalar_parameter_value('SpeedStrength'),
                 'camera_location':[pos.x,pos.y,pos.z],'camera_rotation':[rot.pitch,rot.yaw,rot.roll]}
            assert all(math.isfinite(x) for x in row['camera_location']+row['camera_rotation'])
            state['samples'].append(row)
            return row
        def shot(name):u.SystemLibrary.execute_console_command(world,'HighResShot 1600x900 filename='+str(ev/(name+'.png')),pc)
        stage=state['stage']
        if stage==0 and elapsed>5:
            row=sample('pre_start');assert abs(row['fov']-110)<.01 and row['blur_strength']==0
            shot('pre_start');state['stage']=1
        elif stage==1 and elapsed>18:
            row=sample('driving');assert 112<row['fov']<=115 and row['blur_strength']>.1,row
            assert abs(row['camera_rotation'][0]+10)<.05 and abs(row['camera_rotation'][2])<.05
            shot('driving');state['stage']=2
        elif stage==2 and elapsed>20:
            visual.set_editor_property('speed_effects_enabled',False);state['stage']=3
        elif stage==3 and elapsed>21:
            row=sample('disabled');assert abs(row['fov']-110)<.01 and row['blur_strength']==0,row
            assert math.dist(row['camera_location'],[5.,0.,74.])<.001,row
            shot('disabled');visual.set_editor_property('speed_effects_enabled',True);state['stage']=4
        elif stage==4 and elapsed>24:
            row=sample('re_enabled');assert row['fov']>110 and row['blur_strength']>0,row
            gm=u.GameplayStatics.get_game_mode(world);gm.restart_race_start();state['stage']=5
        elif stage==5 and elapsed>25:
            row=sample('reset');assert abs(row['fov']-110)<.01 and row['blur_strength']==0,row
            assert math.dist(row['camera_location'],[5.,0.,74.])<.001,row
            assert len(u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn))==5
            shot('reset');state['stage']=6;state['finish']=time.monotonic()
            unchanged=protected=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'Content/RoadToF1/Maps').glob('*.umap')}
            assert unchanged
            (ev/'pie_validation.json').write_text(json.dumps({'passed':True,'actual_pie':True,'maps_unchanged':unchanged,'samples':state['samples']},indent=2))
        elif stage==6 and time.monotonic()-state['finish']>4:
            level.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
    except Exception:
        (ev/'pie_error.txt').write_text(traceback.format_exc());u.log_error(traceback.format_exc())
        u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
    finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

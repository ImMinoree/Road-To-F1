"""Actual PIE: native starting grid, then a transient off-circuit force-test pad. Never saves a map.
Only the explicit test setup and final race restart reposition the kart; each maneuver uses normal pawn Tick.
"""
import unreal as u, json, csv, time, math, traceback, hashlib
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve();ev=root/'Evidence/TireDynamics';ev.mkdir(parents=True,exist_ok=True)
protected=json.loads((root/'Checkpoints/BeforeTireDynamics_20261024/protected_hashes.json').read_text(encoding='utf-8-sig'))
u.EditorPythonScripting.set_keep_python_script_alive(True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);editor=u.get_editor_subsystem(u.UnrealEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
# The authored desert ground extends far past the circuit. Keep the temporary pad above it.
PAD_Z=2000
floor=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(-60000,-60000,PAD_Z-50))
floor.tags=['KartDynamicsValidationPad','SurfaceAsphalt'];floor.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
floor.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
floor.set_actor_scale3d(u.Vector(500,500,1))
for cmd in ['t.MaxFPS 60','r.ScreenPercentage 100','sg.ShadowQuality 2']:u.SystemLibrary.execute_console_command(None,cmd)
state={'start':time.monotonic(),'started':False,'busy':False,'phase':'grid','phase_time':0,'rows':[],'shots':set(),'max_beta':0,'max_yaw':0,'drift_seen':False,'max_z_error':0,'max_step_cm':0,'last_pos':None,'debris_before':0,'finish':None,'grid':None}
def tick(dt):
    if state['busy']:return
    state['busy']=True
    try:
        if time.monotonic()-state['start']>240:raise RuntimeError('Tire PIE check timeout')
        if not state['started'] and time.monotonic()-state['start']>6:
            state['started']=True;level.editor_request_begin_play()
        if not level.is_in_play_in_editor():return
        world=editor.get_game_world()
        if not world:return
        pawn=u.GameplayStatics.get_player_pawn(world,0)
        if not pawn:return
        dynamics=pawn.get_component_by_class(u.KartTireDynamics);fx=pawn.get_component_by_class(u.KartSurfaceFX)
        t=u.GameplayStatics.get_time_seconds(world);slip=dynamics.get_telemetry();gm=u.GameplayStatics.get_game_mode(world)
        if not state['grid']:state['grid']=pawn.get_actor_location()
        phase=state['phase'];age=t-state['phase_time'];pos=pawn.get_actor_location()
        def shot(name):
            if name not in state['shots']:
                u.SystemLibrary.execute_console_command(world,'Shot filename='+str(ev/(name+'.png')))
                state['shots'].add(name)
        def next_phase(name):state['phase']=name;state['phase_time']=t
        if phase not in ('grid','reset','finish'):
            row={'t':t,'phase':phase,'u_mps':slip.longitudinal_speed_mps,'v_mps':slip.lateral_speed_mps,'beta_deg':slip.sideslip_degrees,'yaw_deg_s':slip.yaw_rate_degrees,
                 'front_slip_deg':slip.front_slip_degrees,'rear_slip_deg':slip.rear_slip_degrees,'front_fy_n':slip.front_lateral_force_n,'rear_fy_n':slip.rear_lateral_force_n,
                 'front_use':slip.front_saturation,'rear_use':slip.rear_saturation,'front_mu':slip.front_grip,'rear_mu':slip.rear_grip,'drifting':slip.drifting,
                 'grounded':slip.grounded_wheels,'x_cm':pos.x,'y_cm':pos.y,'z_cm':pos.z}
            state['rows'].append(row)
            assert all(math.isfinite(v) for k,v in row.items() if isinstance(v,(float,int)))
            expected_z=PAD_Z+31 if phase!='launch' else 31
            state['max_z_error']=max(state['max_z_error'],abs(pos.z-expected_z))
            if state['last_pos']:
                state['max_step_cm']=max(state['max_step_cm'],(pos-state['last_pos']).length())
            state['last_pos']=pos
            assert slip.front_saturation<=1.001 and slip.rear_saturation<=1.001
        if phase=='grid':
            pawn.set_kart_test_input(1,0,False)
            if gm.red_light_count==5 and 'grid' not in state['shots']:
                assert (pos-state['grid']).length()<1 and abs(slip.longitudinal_speed_mps)<.001
                assert gm.staged_participant_count==5
                shot('grid')
            if t>11:
                assert slip.longitudinal_speed_mps>2 and gm.start_event_count==1
                shot('launch');next_phase('launch')
        elif phase=='launch':
            if age>.15:
                pawn.set_actor_location_and_rotation(u.Vector(-60000,-60000,PAD_Z+31),u.Rotator(),False,True)
                dynamics.reset_motion();state['last_pos']=None
                state['pad']=next(a for a in u.GameplayStatics.get_all_actors_of_class(world,u.StaticMeshActor) if 'KartDynamicsValidationPad' in list(map(str,a.tags)))
                next_phase('accelerate')
        elif phase=='accelerate':
            pawn.set_kart_test_input(1,0,False)
            if slip.longitudinal_speed_mps>=11:
                pawn.set_kart_test_input(.8,.12,False);next_phase('turn_entry')
        elif phase=='turn_entry':
            pawn.set_kart_test_input(.8,.12,False)
            if age>=1:pawn.set_kart_test_input(0,.12,True);next_phase('brake')
        elif phase=='brake':
            pawn.set_kart_test_input(0,.12,True)
            if age>=.6:next_phase('recover')
        elif phase=='recover':
            beta=math.radians(slip.sideslip_degrees);yaw=math.radians(slip.yaw_rate_degrees)
            steering=max(-.8,min(.8,beta*1.5-yaw*.12))
            throttle=.3 if abs(beta)>math.radians(2) or abs(yaw)>.15 else .8
            pawn.set_kart_test_input(throttle,steering,False)
            state['max_beta']=max(state['max_beta'],abs(slip.sideslip_degrees));state['max_yaw']=max(state['max_yaw'],abs(slip.yaw_rate_degrees))
            state['drift_seen']=state['drift_seen'] or slip.drifting
            if slip.drifting:shot('rear_slide')
            if age>7:
                assert state['drift_seen'] and 6<state['max_beta']<25,{'drift':state['drift_seen'],'max_beta':state['max_beta']}
                assert abs(slip.sideslip_degrees)<2 and abs(slip.yaw_rate_degrees)<5 and slip.longitudinal_speed_mps>6
                assert state['max_z_error']<1 and state['max_step_cm']<400,{'z_error':state['max_z_error'],'frame_travel':state['max_step_cm']}
                shot('recovered');state['debris_before']=fx.total_emitted
                state['pad'].tags=['KartDynamicsValidationPad','SurfaceDirt'];next_phase('dirt')
        elif phase=='dirt':
            pawn.set_kart_test_input(.3,.07,False)
            if age>2:
                assert abs(slip.rear_grip-.42)<.01 and fx.total_emitted>state['debris_before']
                shot('dirt');state['pad'].tags=['KartDynamicsValidationPad','SurfaceGrass'];next_phase('grass')
        elif phase=='grass':
            pawn.set_kart_test_input(.3,.07,False)
            if age>1.5:
                assert abs(slip.rear_grip-.48)<.01
                gm.restart_race_start();state['grid']=pawn.get_actor_location();next_phase('reset')
        elif phase=='reset':
            pawn.set_kart_test_input(1,.3,False)
            if age>1:
                assert (pos-state['grid']).length()<1 and abs(slip.longitudinal_speed_mps)<.001 and abs(slip.lateral_speed_mps)<.001 and not slip.drifting
                assert len(u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn))==5
                assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()==h.upper() for p,h in protected.items())
                with (ev/'pie_maneuver.csv').open('w',newline='') as f:
                    writer=csv.DictWriter(f,fieldnames=list(state['rows'][0]));writer.writeheader();writer.writerows(state['rows'])
                result={'passed':True,'actual_pie':True,'test_pad_transient':True,'native_grid_and_lights_out_passed':True,'race_restart_passed':True,
                        'max_slide_beta_deg':state['max_beta'],'max_yaw_deg_s':state['max_yaw'],'recovered_at_speed':True,'max_z_error_cm':state['max_z_error'],
                        'maximum_frame_travel_cm':state['max_step_cm'],'surfaces_verified':['asphalt','dirt','grass'],'loose_surface_debris_verified':True,
                        'maps_and_original_repository_unchanged':True,'screenshots':sorted(state['shots'])}
                (ev/'pie_validation.json').write_text(json.dumps(result,indent=2));state['finish']=time.monotonic();next_phase('finish')
        elif phase=='finish' and time.monotonic()-state['finish']>3:
            level.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
    except Exception:
        (ev/'pie_error.txt').write_text(traceback.format_exc());u.log_error(traceback.format_exc())
        if state['rows']:
            with (ev/'pie_attempt.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(state['rows'][0]));writer.writeheader();writer.writerows(state['rows'])
        u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
    finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

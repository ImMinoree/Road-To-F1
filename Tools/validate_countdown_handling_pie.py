"""Actual PIE countdown/handling check. Adds a transient test pad; never saves the map."""
import csv
import hashlib
import json
import math
import time
import traceback
from pathlib import Path
import unreal as u

root = Path(u.Paths.project_dir()).resolve()
evidence = root / 'Evidence' / 'CountdownHandling'
if 'CountdownFinalCapture' in u.SystemLibrary.get_command_line():
    evidence = evidence / 'VerifiedPIE'
evidence.mkdir(parents=True, exist_ok=True)
maps = list((root / 'Content' / 'RoadToF1' / 'Maps').glob('DesertKarting*.umap'))
hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in maps}
u.EditorPythonScripting.set_keep_python_script_alive(True)
level = u.get_editor_subsystem(u.LevelEditorSubsystem)
editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
pad = actors.spawn_actor_from_class(u.StaticMeshActor, u.Vector(-60000, -60000, 1950))
pad.tags = ['CountdownHandlingPad', 'SurfaceAsphalt']
pad.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
pad.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
pad.static_mesh_component.set_collision_profile_name('BlockAll')
pad.set_actor_scale3d(u.Vector(500, 500, 1))
for command in ['t.MaxFPS 45', 'r.ScreenPercentage 100', 'sg.ShadowQuality 1', 'r.MotionBlurQuality 0']:
    u.SystemLibrary.execute_console_command(None, command)
state = dict(start=time.monotonic(), started=False, busy=False, phase='countdown', epoch=0,
             reds=-1, red_epoch=0, numbers=[], shots=[], rows=[], max_beta=0, grid=None,
             held_throttle_blocked=True, released=False, dirt=False, recovered=0)
wait_for_automation = 'CountdownWaitForAutomation' in u.SystemLibrary.get_command_line()


def finish(passed, error=None):
    state['finished'] = True
    if level.is_in_play_in_editor():
        level.editor_request_end_play()
    protected = all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    result = dict(passed=passed and protected, actual_pie=True, map_files_unchanged=protected,
                  numbers=state['numbers'], screenshots=state['shots'], max_beta_degrees=state['max_beta'],
                  held_throttle_blocked=state['held_throttle_blocked'], released=state['released'],
                  dirt_transition=state['dirt'], recoveries_checked=state['recovered'], error=error)
    (evidence / 'pie_result.json').write_text(json.dumps(result, indent=2))
    if state['rows']:
        with (evidence / 'pie_trace.csv').open('w', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=list(state['rows'][0]))
            writer.writeheader()
            writer.writerows(state['rows'])
    u.unregister_slate_post_tick_callback(handle)
    u.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')


def tick(dt):
    if state['busy'] or state.get('finished'):
        return
    state['busy'] = True
    try:
        if time.monotonic() - state['start'] > 240:
            raise RuntimeError('PIE validation timed out')
        if wait_for_automation and not state.get('automation_checked'):
            report = evidence / 'AutomationFinal' / 'index.json'
            if not report.exists():
                return
            summary = json.loads(report.read_text(encoding='utf-8-sig'))
            assert summary['failed'] == 0 and summary['notRun'] == 0, 'Automation failures: ' + str(summary['failed'])
            state['automation_checked'] = True
        if not state['started'] and time.monotonic() - state['start'] > 3:
            state['started'] = True
            level.editor_request_begin_play()
        if not level.is_in_play_in_editor():
            return
        world = editor.get_game_world()
        if not world:
            return
        pawn = u.GameplayStatics.get_player_pawn(world, 0)
        if not pawn:
            return
        dynamics = pawn.get_component_by_class(u.KartTireDynamics)
        gm = u.GameplayStatics.get_game_mode(world)
        t = u.GameplayStatics.get_time_seconds(world)
        slip = dynamics.get_telemetry()
        pos = pawn.get_actor_location()
        phase, age = state['phase'], t - state['epoch']
        if state['grid'] is None:
            state['grid'] = pos
            assert abs(dynamics.get_editor_property('steering_response_seconds') - .16) < .001
            assert abs(dynamics.get_editor_property('rear_lateral_grip_reserve') - .95) < .001
        if gm.red_light_count != state['reds']:
            state['reds'], state['red_epoch'] = gm.red_light_count, t

        def change(name):
            state['phase'], state['epoch'] = name, t

        def shot(name):
            if name not in state['shots']:
                u.SystemLibrary.execute_console_command(world, 'Shot filename=' + str(evidence / (name + '.png')))
                state['shots'].append(name)

        def recover():
            steer = max(-.8, min(.8, math.radians(slip.sideslip_degrees) * 1.5 - math.radians(slip.yaw_rate_degrees) * .12))
            pawn.set_kart_test_input(.35, steer, False)

        state['rows'].append(dict(time=t, phase=phase, reds=gm.red_light_count, gate=gm.is_start_gate_closed(),
                                  start_events=gm.start_event_count, speed=slip.longitudinal_speed_mps,
                                  beta=slip.sideslip_degrees, yaw=slip.yaw_rate_degrees,
                                  steering=slip.steering_degrees, front_force=slip.front_lateral_force_n,
                                  rear_force=slip.rear_lateral_force_n, rear_grip=slip.rear_grip,
                                  x=pos.x, y=pos.y, z=pos.z))
        if phase not in ['countdown', 'restart']:
            state['max_beta'] = max(state['max_beta'], abs(slip.sideslip_degrees))
            assert math.isfinite(slip.yaw_rate_degrees) and abs(slip.sideslip_degrees) < 15
            assert pos.z > 2010, 'Kart dropped through the transient road pad'

        if phase == 'countdown':
            pawn.set_kart_test_input(1, 0, False)
            if gm.is_start_gate_closed():
                stationary = (pos - state['grid']).length() < 1 and abs(slip.longitudinal_speed_mps) < .001
                state['held_throttle_blocked'] &= stationary
                assert stationary, 'Held throttle moved the kart before lights-out'
                red_age = t - state['red_epoch']
                if gm.red_light_count == 1 and .04 < red_age < .12:
                    shot('fade_in_5')
                if gm.red_light_count == 1 and .85 < red_age < .95:
                    shot('fade_out_5')
                if gm.red_light_count > 0 and .28 < red_age < .65:
                    number = 6 - gm.red_light_count
                    if number not in state['numbers']:
                        state['numbers'].append(number)
                    shot('countdown_' + str(number))
            else:
                assert gm.start_event_count == 1
                state['released'] = True
                if .28 < gm.get_race_elapsed_seconds() < .7:
                    shot('start')
                if gm.get_race_elapsed_seconds() > 1.4:
                    assert state['numbers'] == [5, 4, 3, 2, 1] and 'start' in state['shots']
                    assert slip.longitudinal_speed_mps > 1, 'Controls did not release at lights-out'
                    pawn.set_actor_location_and_rotation(u.Vector(-60000, -60000, 2031), u.Rotator(), False, True)
                    dynamics.reset_motion()
                    state['pad'] = next(a for a in u.GameplayStatics.get_all_actors_of_class(world, u.StaticMeshActor)
                                        if 'CountdownHandlingPad' in list(map(str, a.tags)))
                    change('accelerate')
        elif phase == 'accelerate':
            pawn.set_kart_test_input(1, 0, False)
            if slip.longitudinal_speed_mps >= 12:
                change('left')
        elif phase in ['left', 'right']:
            pawn.set_kart_test_input(1, -1 if phase == 'left' else 1, False)
            if age > .6:
                shot('handling_' + phase)
            if age > 1.2:
                change('recover_left' if phase == 'left' else 'recover_right')
        elif phase in ['recover_left', 'recover_right']:
            recover()
            if age > 3:
                assert abs(slip.sideslip_degrees) < 2 and abs(slip.yaw_rate_degrees) < 5
                state['recovered'] += 1
                change('right' if phase == 'recover_left' else 'brake')
        elif phase == 'brake':
            pawn.set_kart_test_input(0, .4, True)
            if age > .55:
                shot('brake_corner')
                state['pad'].tags = ['CountdownHandlingPad', 'SurfaceDirt']
                change('dirt')
        elif phase == 'dirt':
            pawn.set_kart_test_input(.3, .1, False)
            if age > .7:
                assert abs(slip.rear_grip - .42) < .02
                state['dirt'] = True
                gm.restart_race_start()
                state['restart_grid'] = pawn.get_actor_location()
                change('restart')
        elif phase == 'restart':
            pawn.set_kart_test_input(1, 0, False)
            assert gm.is_start_gate_closed() and gm.start_event_count == 0
            assert (pos - state['restart_grid']).length() < 1 and abs(slip.longitudinal_speed_mps) < .001
            if gm.red_light_count == 0 and age > .3:
                shot('restart_pregrid')
            if gm.red_light_count == 1 and t - state['red_epoch'] > .3:
                shot('restart_5')
            if 'restart_5' in state['shots'] and t - state['red_epoch'] > .7:
                finish(True)
    except Exception:
        finish(False, traceback.format_exc())
    finally:
        state['busy'] = False


handle = u.register_slate_post_tick_callback(tick)

"""Final rendered detail and nearer genuine kart-eye evidence; no map edits."""
import unreal as u,time,json,traceback,math
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();P=R/'Art/Trackside/TireBarriers';EV=R/'Evidence/TireBarriers';g=json.loads((P/'placement.json').read_text());route=json.loads((R/'Art/DesertRoute/audit.json').read_text())['route_cm']
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');u.EditorPythonScripting.set_keep_python_script_alive(True)
state={'phase':'wait','epoch':time.monotonic(),'busy':False};tasks=[];report={}
def next_phase(p):state.update(phase=p,epoch=time.monotonic())
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  age=time.monotonic()-state['epoch'];phase=state['phase'];world=W.get_editor_world()
  if phase=='wait' and age>5:
   ignored=list(u.GameplayStatics.get_all_actors_of_class(world,u.InstancedFoliageActor));overlaps=[]
   for path in g['paths']:
    for j,p in enumerate(path['spline_cm']):
     hit=u.SystemLibrary.sphere_trace_single(world,u.Vector(p[0],p[1],31),u.Vector(p[0]+.01,p[1],31),24,u.TraceTypeQuery.ECC_VISIBILITY,True,ignored,u.DrawDebugTrace.NONE,True)
     if hit:overlaps.append({'corner':path['corner'],'column':j,'actors':[a.get_actor_label() for a in hit.to_tuple() if isinstance(a,u.Actor)]})
   report['existing_structure_overlap_probes']=overlaps;assert not overlaps,overlaps
   path=g['paths'][0];p=path['spline_cm'][12];road=route[path['route_index']];dx=road[0]-p[0];dy=road[1]-p[1];length=math.hypot(dx,dy);n=u.Vector(dx/length,dy/length,0)
   where=u.Vector(p[0],p[1],0)+n*270+u.Vector(0,0,105);target=u.Vector(p[0],p[1],27)
   camera=A.spawn_actor_from_class(u.CameraActor,where,u.MathLibrary.find_look_at_rotation(where,target));camera.camera_component.set_field_of_view(60)
   state['camera']=camera;W.set_level_viewport_camera_info(where,u.MathLibrary.find_look_at_rotation(where,target));next_phase('detail')
  elif phase=='detail' and age>10:
   task=u.AutomationLibrary.take_high_res_screenshot(1600,1000,str(EV/'unreal_barrier_detail.png'),camera=state['camera'],delay=1);tasks.append(task);state['task']=task;next_phase('detail_wait')
  elif phase=='detail_wait' and state['task'].is_task_done() and age>2:
   A.destroy_actor(state['camera']);L.editor_request_begin_play();next_phase('play')
  elif phase=='play':
   if age>120:raise RuntimeError('PIE startup timeout')
   pw=W.get_game_world()
   if not pw:return
   pawn=u.GameplayStatics.get_player_pawn(pw,0)
   if not isinstance(pawn,u.ProofPawn) or u.GameplayStatics.get_time_seconds(pw)<10:return
   idx=(g['paths'][0]['route_index']-1)%len(route);p=route[idx];target=g['paths'][0]['spline_cm'][12];yaw=math.degrees(math.atan2(target[1]-p[1],target[0]-p[0]))
   pawn.set_kart_test_input(0,0,True);pawn.set_actor_location_and_rotation(u.Vector(p[0],p[1],31),u.Rotator(yaw=yaw),False,True);pawn.get_component_by_class(u.KartTireDynamics).reset_motion()
   if pawn.is_third_person_view():pawn.toggle_camera_view()
   u.GameplayStatics.get_player_controller(pw,0).set_view_target_with_blend(pawn,0);report['driver_route_index']=idx;next_phase('eye')
  elif phase=='eye' and age>3:
   u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(EV/'driver_eye_near_corner.png'));next_phase('done')
  elif phase=='done' and age>3:
   L.editor_request_end_play();(EV/'capture.json').write_text(json.dumps(report,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 except Exception:
  (EV/'capture_error.txt').write_text(traceback.format_exc());u.log_error(traceback.format_exc());u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

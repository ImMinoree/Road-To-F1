"""Additional hairpin-entry POV and explicit AI guide clearance; no saves."""
import unreal as u,json,time,math,traceback
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/ExpandedTireBarriers';edges=json.loads((R/'Art/RacingAI/track_edges.json').read_text());L=u.get_editor_subsystem(u.LevelEditorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem);assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');u.EditorPythonScripting.set_keep_python_script_alive(True)
report={'AI_guide_segments':len(edges['guide']),'new_tire_hits':[]};world=W.get_editor_world()
for i,p in enumerate(edges['guide']):
 q=edges['guide'][(i+1)%len(edges['guide'])];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));hit=u.SystemLibrary.box_trace_single(world,u.Vector(p[0],p[1],31),u.Vector(q[0],q[1],31),u.Vector(90,60,16),u.Rotator(yaw=yaw),u.TraceTypeQuery.ECC_VISIBILITY,False,[],u.DrawDebugTrace.NONE,True)
 if hit and any(isinstance(c,u.StaticMeshComponent) and c.static_mesh and '/Trackside/TireBarriers/' in c.static_mesh.get_path_name() for c in hit.to_tuple()):report['new_tire_hits'].append(i)
assert not report['new_tire_hits'];L.editor_request_begin_play();state={'phase':'play','epoch':time.monotonic(),'busy':False}
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  age=time.monotonic()-state['epoch']
  if state['phase']=='play':
   world=W.get_game_world()
   if not world or u.GameplayStatics.get_time_seconds(world)<10:return
   pawn=u.GameplayStatics.get_player_pawn(world,0);idx=184;p=edges['center'][idx];q=edges['center'][idx+3];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]))
   for kart in u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn):kart.set_kart_test_input(0,0,True)
   pawn.set_actor_location_and_rotation(u.Vector(p[0],p[1],31),u.Rotator(yaw=yaw),False,True);pawn.get_component_by_class(u.KartTireDynamics).reset_motion()
   if pawn.is_third_person_view():pawn.toggle_camera_view()
   u.GameplayStatics.get_player_controller(world,0).set_view_target_with_blend(pawn,0);report['driver_route_index']=idx;state.update(phase='eye',epoch=time.monotonic())
  elif state['phase']=='eye' and age>4:
   u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/'driver_hairpin_entry.png'));state.update(phase='end',epoch=time.monotonic())
  elif state['phase']=='end' and age>3:
   L.editor_request_end_play();(E/'AI_guide_clearance.json').write_text(json.dumps(report,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 except Exception:
  (E/'hairpin_error.txt').write_text(traceback.format_exc());u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

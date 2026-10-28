"""Live editor ground fit, collision acceptance, additive save and real PIE eye view."""
import unreal as u,json,time,math,hashlib,traceback
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();P=R/'Art/Trackside/TireBarriers';EV=R/'Evidence/TireBarriers';B='/Game/RoadToF1/Trackside/TireBarriers'
g=json.loads((P/'placement.json').read_text());route=json.loads((R/'Art/DesertRoute/audit.json').read_text())['route_cm'];protected=json.loads((EV/'protected_before.json').read_text())
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');world=W.get_editor_world()
u.EditorPythonScripting.set_keep_python_script_alive(True)
for command in ['t.MaxFPS 45','r.ScreenPercentage 100','r.MotionBlurQuality 0']:u.SystemLibrary.execute_console_command(None,command)
state={'phase':'wait','time':time.monotonic(),'busy':False};report={'paths':g['paths'],'tires':len(g['tires']),'map_saved':False};retained=[]
def parts(hit):return hit.to_tuple() if hit else []
def trace(world,x,y):return u.SystemLibrary.line_trace_single(world,u.Vector(x,y,150),u.Vector(x,y,-150),u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True)
def z_at(world,x,y):
 h=trace(world,x,y);assert h,('No support ground',x,y)
 vectors=[v for v in parts(h) if isinstance(v,u.Vector)];assert vectors
 return vectors[0].z
def signature():
 out={}
 for a in A.get_all_level_actors():
  if isinstance(a,u.InstancedFoliageActor):continue
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();out[a.get_path_name()]=[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z,a.get_actor_enable_collision()]
 return out
def corridor():
 blocked=[];roads=[]
 for i,p in enumerate(route):
  q=route[(i+1)%len(route)];hit=u.SystemLibrary.sphere_trace_single(world,u.Vector(p[0],p[1],90),u.Vector(q[0],q[1],90),60,u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True)
  if hit:blocked.append(i)
  h=trace(world,p[0],p[1]);roads.append([a.get_actor_label() for a in parts(h) if isinstance(a,u.Actor)])
 return {'sphere_radius_cm':60,'segments':len(route),'blocked_indices':blocked,'road_support':roads}
def next_phase(name):state.update(phase=name,time=time.monotonic())
def finish():
 (EV/'validation.json').write_text(json.dumps(report,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  age=time.monotonic()-state['time'];phase=state['phase']
  if phase=='wait' and age>5:
   state['signature']=signature();state['before']=corridor();transforms={'Black':[],'Red':[]};column_z={}
   for item in g['tires']:
    x,y,z=item['location_cm'];key=(item['corner'],item['column'])
    if key not in column_z:
     heights=[z_at(world,x+dx,y+dy) for dx,dy in [(0,0),(20,0),(-20,0),(0,20),(0,-20)]]
     assert max(heights)-min(heights)<2.5,('Uneven support',key,heights)
     assert -100<max(heights)<80,('Obstacle under column',key,heights)
     column_z[key]=max(heights)-.1
    transforms[item['color']].append(u.Transform(location=u.Vector(x,y,z+column_z[key]),rotation=u.Rotator(yaw=item['yaw'])))
   for color in ['Black','Red']:
    ft=u.load_asset(B+'/Instancing/FT_TireBarrier_'+color);assert ft;u.InstancedFoliageActor.remove_all_instances(world,ft);u.InstancedFoliageActor.add_instances(world,ft,transforms[color])
   report['ground_fitted_columns']=len(column_z);state['column_z']=column_z;next_phase('accept')
  elif phase=='accept' and age>4:
   after=corridor();assert after==state['before'],'New collision or support change inside kart corridor'
   actual=signature()
   if actual!=state['signature']:
    (EV/'actor_signature_diff.json').write_text(json.dumps({'before':state['signature'],'after':actual},indent=2));raise AssertionError('An existing actor transform/collision setting changed')
   count=0
   for a in A.get_all_level_actors():
    for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
     if c.static_mesh and c.static_mesh.get_path_name().startswith(B+'/'):
      count+=c.get_instance_count();assert c.get_collision_enabled()==u.CollisionEnabled.QUERY_AND_PHYSICS
   assert count==len(g['tires']),(count,len(g['tires']))
   # Horizontal trace through a base tire confirms the instances really block.
   p=g['tires'][0]['location_cm'];z=state['column_z'][(g['tires'][0]['corner'],0)]+9
   hit=u.SystemLibrary.line_trace_single(world,u.Vector(p[0]-80,p[1],z),u.Vector(p[0]+80,p[1],z),u.TraceTypeQuery.ECC_VISIBILITY,False,[],u.DrawDebugTrace.NONE,True)
   assert any(isinstance(c,u.StaticMeshComponent) and c.static_mesh and c.static_mesh.get_path_name().startswith(B+'/') for c in parts(hit)),'Barrier simple collision did not block test trace'
   mesh_tools=u.get_editor_subsystem(u.StaticMeshEditorSubsystem);mesh_report=json.loads((EV/'import.json').read_text())
   for item in mesh_report['meshes']:
    mesh=u.load_asset(B+'/Meshes/'+item['name']);item['convex_collision_count']=mesh_tools.get_convex_collision_count(mesh);assert item['convex_collision_count']>0
   (EV/'import.json').write_text(json.dumps(mesh_report,indent=2))
   report.update(instanced_tires=count,existing_actor_transforms_collision_unchanged=True,new_kart_corridor_obstructions=0,route_segments_tested=len(route),kart_clearance_sweep_radius_cm=60,barrier_collision_trace_passed=True)
   for path,digest in protected.items():
    assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
   assert L.save_current_level();report['map_saved']=True
   # All subsequent capture actors and kart positioning are transient PIE work.
   L.editor_request_begin_play();next_phase('play')
  elif phase=='play':
   if age>150:raise RuntimeError('PIE player startup timeout')
   if not L.is_in_play_in_editor():return
   pw=W.get_game_world();pawn=u.GameplayStatics.get_player_pawn(pw,0)
   if not pawn or not isinstance(pawn,u.ProofPawn):return
   if u.GameplayStatics.get_time_seconds(pw)<10:return
   idx=(g['paths'][0]['route_index']-10)%len(route);p=route[idx];target=g['paths'][0]['spline_cm'][12]
   yaw=math.degrees(math.atan2(target[1]-p[1],target[0]-p[0]));height=z_at(pw,p[0],p[1])
   pawn.set_kart_test_input(0,0,True);pawn.set_actor_location_and_rotation(u.Vector(p[0],p[1],height+31),u.Rotator(yaw=yaw),False,True)
   dyn=pawn.get_component_by_class(u.KartTireDynamics);dyn.reset_motion()
   if pawn.is_third_person_view():pawn.toggle_camera_view()
   pc=u.GameplayStatics.get_player_controller(pw,0);pc.set_view_target_with_blend(pawn,0)
   report['driver_capture']={'pawn':pawn.get_class().get_name(),'route_index':idx,'location_cm':[p[0],p[1],height+31],'yaw_deg':yaw,'stationary_braked':True}
   next_phase('capture')
  elif phase=='capture' and age>3:
   pw=W.get_game_world();u.SystemLibrary.execute_console_command(pw,'Shot filename='+str(EV/'driver_eye_corner.png'));next_phase('done')
  elif phase=='done' and age>3:
   L.editor_request_end_play();report['real_PIE_driver_eye_capture_requested']=True;report['limitations']='Static rigid tire barriers with simplified convex collision; no deformable tire response or full lap validation.';finish()
 except Exception:
  report['error']=traceback.format_exc();(EV/'error.txt').write_text(report['error']);u.log_error(report['error'])
  if L.is_in_play_in_editor():L.editor_request_end_play()
  finish()
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

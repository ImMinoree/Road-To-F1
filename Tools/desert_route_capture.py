"""True orthographic top-down Unreal evidence and full-loop runtime collision probes."""
import unreal as u,json,time,math
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/DesertRoute';EV.mkdir(parents=True,exist_ok=True);g=json.loads((ROOT/'Art/DesertRoute/audit.json').read_text())
after='-RouteAfter' in u.SystemLibrary.get_command_line();phase='After' if after else 'Before'
verify_only='-RouteVerifyOnly' in u.SystemLibrary.get_command_line()
if verify_only:phase='Final'
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
maps=['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual'];state={'i':0,'busy':False,'done':False};tasks=[];reports={}
for cmd in ['sg.ViewDistanceQuality 3','sg.AntiAliasingQuality 3','sg.ShadowQuality 3','sg.GlobalIlluminationQuality 3','sg.ReflectionQuality 3','sg.TextureQuality 3','r.ScreenPercentage 100','r.HighResScreenshotDelay 8','r.SetRes 2400x2000w','t.MaxFPS 60']:u.SystemLibrary.execute_console_command(None,cmd)
def validate():
 world=editor.get_editor_world();road=[];sweeps=[];karts=[];lights={};geometry={};source_pit=[]
 pts=g['route_cm'];n=len(pts)
 for a in actors.get_all_level_actors():
  if isinstance(a,u.StaticMeshActor):
   c=a.static_mesh_component
   if c.get_collision_enabled()!=u.CollisionEnabled.NO_COLLISION:geometry[a.get_actor_label()]=[c.static_mesh.get_path_name(),str(c.get_collision_enabled())]
  if '10 Race karts' in a.get_actor_label() and any(c.is_visible() for c in a.get_components_by_class(u.PrimitiveComponent)):karts.append(a.get_actor_label())
  if isinstance(a,u.Light):
   c=a.light_component;color=c.get_editor_property('light_color');r=a.get_actor_rotation();lights[a.get_actor_label()]=[c.get_editor_property('intensity'),[color.r,color.g,color.b,color.a],[r.pitch,r.yaw,r.roll]]
 for i,p in enumerate(pts):
  q=pts[(i+1)%n];prev=pts[i-1];dx=q[0]-prev[0];dy=q[1]-prev[1];d=math.hypot(dx,dy)
  for off in [-180,0,180]:
   x=p[0]-dy/d*off;y=p[1]+dx/d*off;hit=u.SystemLibrary.line_trace_single(world,u.Vector(x,y,150),u.Vector(x,y,-150),u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True)
   labels=[v.get_actor_label() for v in hit.to_tuple() if isinstance(v,u.StaticMeshActor)] if hit else []
   if not any('02 Track surface' in l and 'asphalt' in l for l in labels):road.append({'index':i,'offset':off,'hit':labels,'location':[x,y]})
  hit=u.SystemLibrary.sphere_trace_single(world,u.Vector(p[0],p[1],31),u.Vector(q[0],q[1],31),28,u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True)
  if hit:
   labels=[v.get_actor_label() for v in hit.to_tuple() if isinstance(v,u.StaticMeshActor)];sweeps.append({'index':i,'hit':labels})
 # Sample the apparent pit merge gaps at both rectangular ends, without guessing a connector.
 for endpoint in g['pit_endpoints_cm']:
  x=endpoint[0]
  for y in range(-1700,1,100):
   hit=u.SystemLibrary.line_trace_single(world,u.Vector(x,y,150),u.Vector(x,y,-150),u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True)
   labels=[v.get_actor_label() for v in hit.to_tuple() if isinstance(v,u.StaticMeshActor)] if hit else []
   source_pit.append({'cm':[x,y],'hit':labels})
 return {'road_rays':n*3,'road_failures':road,'swept_sphere_segments':n,'sweep_radius_cm':28,'sweep_failures':sweeps,'visible_kart_groups':karts,'lights':lights,'collision_actors':geometry,'pit_lateral_probes':source_pit}
def prepare():
 mp=maps[state['i']];assert level.load_level(mp);reports[mp]=validate()
 c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(2500,-7000,40000),u.Rotator(pitch=-90,yaw=0,roll=0));c.set_actor_label('Route_Orthographic_Validation')
 cc=c.camera_component;cc.set_editor_property('projection_mode',u.CameraProjectionMode.ORTHOGRAPHIC);cc.set_editor_property('ortho_width',33500);cc.set_editor_property('aspect_ratio',1.2);cc.set_editor_property('constrain_aspect_ratio',True);cc.set_editor_property('auto_calculate_ortho_planes',False);cc.set_editor_property('ortho_near_clip_plane',1);cc.set_editor_property('ortho_far_clip_plane',100000)
 state.update(camera=c,start=time.monotonic(),task=None,completed=None)
def tick(dt):
 if state['busy'] or state['done']:return
 state['busy']=True
 try:
  if verify_only and time.monotonic()-state['start']>3:
   state['i']+=1
   if state['i']==len(maps):
    state['done']=True;(EV/'Final_validation.json').write_text(json.dumps({'maps':reports,'mode':'Live editor collision-only verification after final nonblocking profile fix'},indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR');return
   prepare();return
  if time.monotonic()-state['start']>20 and state['task'] is None:
   state['task']='pending';path=EV/(phase+'_'+maps[state['i']].rsplit('/',1)[-1]+'_TopDown.png');task=u.AutomationLibrary.take_high_res_screenshot(2400,2000,str(path),camera=state['camera'],delay=2);tasks.append(task);state['task']=task
  task=state['task']
  if task and task!='pending' and task.is_task_done() and state['completed'] is None:state['completed']=time.monotonic()
  if state['completed'] and time.monotonic()-state['completed']>3:
   state['i']+=1
   if state['i']==len(maps):
    state['done']=True;(EV/(phase+'_validation.json')).write_text(json.dumps({'maps':reports,'camera':{'center_cm':[2500,-7000,40000],'rotation':[-90,0,0],'projection':'ORTHOGRAPHIC','ortho_width_cm':33500,'resolution':[2400,2000],'image_right_world_axis':'+Y','image_up_world_axis':'+X'}},indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR');return
   prepare()
 except Exception as e:
  state['done']=True;(EV/(phase+'_error.txt')).write_text(str(e));u.log_error(str(e));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:state['busy']=False
prepare();handle=u.register_slate_post_tick_callback(tick)

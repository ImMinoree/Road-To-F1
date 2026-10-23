"""Real rendered comparison with retained screenshot tasks and unchanged scene lighting."""
import unreal as u,json,time,math
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/DesertVisual';EV.mkdir(exist_ok=True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
shots=[['Track',[800,0,80],[-7,0,0],75],['Pit',[-1800,730,80],[7,65,0],65],['Barriers',[5400,-14600,80],[-2,-85,0],70],['Stands',[5300,300,80],[14,78,0],65],['Aerial',[28000,-25000,20500],[-30,151,0],62]]
jobs=[('Baseline','/Game/RoadToF1/Maps/DesertKarting',s) for s in shots]+[('Visual','/Game/RoadToF1/Maps/DesertKarting_Visual',s) for s in shots]
if '-VisualOnly' in u.SystemLibrary.get_command_line():jobs=[j for j in jobs if j[0]=='Visual']
if '-TrackOnly' in u.SystemLibrary.get_command_line():jobs=[j for j in jobs if j[2][0]=='Track']
if '-GroundCheck' in u.SystemLibrary.get_command_line():jobs=[j for j in jobs if j[2][0] in ['Barriers','Aerial']]
state={'i':0,'busy':False,'done':False};reports={};retained=[]
for cmd in ['sg.ViewDistanceQuality 3','sg.AntiAliasingQuality 3','sg.ShadowQuality 3','sg.GlobalIlluminationQuality 3','sg.ReflectionQuality 3','sg.TextureQuality 3','sg.PostProcessQuality 3','r.ScreenPercentage 100','r.HighResScreenshotDelay 8','r.SetRes 1920x1080w','t.MaxFPS 60']:
 u.SystemLibrary.execute_console_command(None,cmd)
def check_map(name):
 world=editor.get_editor_world();visible=[];lights=[];rays=[]
 for a in actors.get_all_level_actors():
  label=a.get_actor_label()
  if '10 Race karts' in label or label.lower().startswith('kart'):
   if any(c.is_visible() for c in a.get_components_by_class(u.PrimitiveComponent)):visible.append(label)
  if isinstance(a,u.Light):
   c=a.light_component;r=a.get_actor_rotation();color=c.get_editor_property('light_color');lights.append([label,c.get_editor_property('intensity'),[color.r,color.g,color.b,color.a],[r.pitch,r.yaw,r.roll]])
 for x in [800,1500,2500,3500,4500]:
  for y in [-300,0,300]:
   hit=u.SystemLibrary.line_trace_single(world,u.Vector(x,y,200),u.Vector(x,y,-200),u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True)
   labels=[v.get_actor_label() for v in hit.to_tuple() if isinstance(v,u.StaticMeshActor)] if hit else []
   rays.append({'p':[x,y],'road':any('02 Track surface' in l and 'asphalt' in l for l in labels)})
 lights.sort(key=lambda x:x[0])
 reports[name]={'visible_kart_actors':visible,'road_probes':rays,'lights':lights,'game_mode':str(world.get_world_settings().get_editor_property('default_game_mode'))}
 assert not visible,visible;assert all(r['road'] for r in rays),rays
 if name=='Visual' and 'Baseline' in reports:assert reports['Baseline']['lights']==lights,('Light settings changed',reports['Baseline']['lights'],lights)
def prepare():
 label,mp,shot=jobs[state['i']];(EV/label).mkdir(exist_ok=True)
 if state.get('camera'):
  actors.destroy_actor(state['camera']);state['camera']=None
 if state.get('map')!=mp:
  assert level.load_level(mp);state['map']=mp;check_map(label)
 # Transient validation camera, never save edits to either map.
 name,p,r,fov=shot;c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(*p),u.Rotator(pitch=r[0],yaw=r[1],roll=r[2]));c.set_actor_label('Validation_'+name);c.camera_component.set_field_of_view(fov)
 state.update(camera=c,start=time.monotonic(),task=None,completed=None,positioned=False)
def tick(dt):
 if state['busy'] or state['done']:return
 state['busy']=True
 try:
  elapsed=time.monotonic()-state['start'];label,mp,shot=jobs[state['i']];name,p,r,fov=shot
  if not state['positioned'] and elapsed>5:
   state['positioned']=True
   editor.set_level_viewport_camera_info(u.Vector(*p),u.Rotator(pitch=r[0],yaw=r[1],roll=r[2]))
  if elapsed>18 and state['task'] is None:
   state['task']='pending'
   task=u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(EV/label/(name+'.png')),camera=state['camera'],delay=2)
   retained.append(task);state['task']=task
  task=state['task']
  if task and task!='pending' and task.is_task_done() and state['completed'] is None:state['completed']=time.monotonic()
  if state['completed'] is not None and time.monotonic()-state['completed']>3:
   state['i']+=1
   if state['i']==len(jobs):
    state['done']=True;(EV/'render_validation.json').write_text(json.dumps({'maps':reports,'shots':shots,'quality':'Epic scalability 3, 1920x1080, 100% render scale','lighting_changed':False},indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR');return
   prepare()
 except Exception as e:
  state['done']=True;(EV/'capture_error.txt').write_text(str(e));(EV/'capture_partial.json').write_text(json.dumps(reports,indent=2));u.log_error(str(e));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:state['busy']=False
if '-VisualOnly' in u.SystemLibrary.get_command_line():
 assert level.load_level('/Game/RoadToF1/Maps/DesertKarting');check_map('Baseline')
prepare();handle=u.register_slate_post_tick_callback(tick)

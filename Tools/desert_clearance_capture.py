"""Capture matching before/after views without saving camera or lighting edits."""
import unreal as u,time,json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/DesertClearance';EV.mkdir(parents=True,exist_ok=True)
phase='After' if '-ClearanceAfter' in u.SystemLibrary.get_command_line() else 'Before'
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(-6500,2500,3800),u.Rotator(pitch=-37,yaw=-48));c.camera_component.set_field_of_view(80)
for cmd in ['r.ScreenPercentage 100','r.SetRes 1920x1080w','r.HighResScreenshotDelay 8','t.MaxFPS 60']:u.SystemLibrary.execute_console_command(None,cmd)
state={'start':time.monotonic(),'task':None,'busy':False,'done':False};retained=[]
def tick(dt):
 if state['busy'] or state['done']:return
 state['busy']=True
 try:
  if time.monotonic()-state['start']>18 and state['task'] is None:
   state['task']='pending';task=u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(EV/(phase+'.png')),camera=c,delay=2);state['task']=task;retained.append(task)
  if state['task'] and state['task']!='pending' and state['task'].is_task_done():
   state['done']=True;u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

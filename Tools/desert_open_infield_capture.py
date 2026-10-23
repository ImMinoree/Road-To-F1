"""Live collision checks and actual aerial/driver-height rendering of cleared maps."""
import unreal as u,json,time
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/DesertOpenInfield';EV.mkdir(parents=True,exist_ok=True)
scope={};exec((ROOT/'Tools/desert_route_capture.py').read_text().split('def prepare():')[0],scope)
level=scope['level'];actors=scope['actors'];views=[('DesertKarting','Aerial'),('DesertKarting_Visual','Aerial'),('DesertKarting_Visual','Driver')];reports={};state={'i':0,'busy':False,'done':False};tasks=[]
def prepare():
 name,view=views[state['i']];assert level.load_level('/Game/RoadToF1/Maps/'+name)
 if view=='Aerial':
  c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(2500,-7000,40000),u.Rotator(pitch=-90,yaw=0));cc=c.camera_component;cc.set_editor_property('projection_mode',u.CameraProjectionMode.ORTHOGRAPHIC);cc.set_editor_property('ortho_width',33500);cc.set_editor_property('aspect_ratio',1.2);cc.set_editor_property('constrain_aspect_ratio',True);cc.set_editor_property('auto_calculate_ortho_planes',False);cc.set_editor_property('ortho_near_clip_plane',1);cc.set_editor_property('ortho_far_clip_plane',100000);size=(2400,2000)
 else:
  c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(-3600,0,85),u.Rotator(pitch=-6,yaw=-24));c.camera_component.set_field_of_view(85);size=(1920,1080)
 state.update(camera=c,start=time.monotonic(),task=None,completed=None,validated=False,size=size)
 u.SystemLibrary.execute_console_command(None,'r.SetRes %dx%dw'%size)
def tick(dt):
 if state['busy'] or state['done']:return
 state['busy']=True
 try:
  elapsed=time.monotonic()-state['start'];name,view=views[state['i']]
  if elapsed>5 and not state['validated']:
   result=scope['validate']();result['visible_paddock']=[a.get_actor_label() for a in actors.get_all_level_actors() if a.get_actor_label().startswith(('DK_09 ','DV_09 ')) and a.static_mesh_component.is_visible()];reports[name]=result;state['validated']=True
  if elapsed>18 and state['task'] is None:
   state['task']='pending';task=u.AutomationLibrary.take_high_res_screenshot(*state['size'],str(EV/(name+'_'+view+'.png')),camera=state['camera'],delay=2);tasks.append(task);state['task']=task
  task=state['task']
  if task and task!='pending' and task.is_task_done() and state['completed'] is None:state['completed']=time.monotonic()
  if state['completed'] and time.monotonic()-state['completed']>3:
   state['i']+=1
   if state['i']==len(views):
    state['done']=True;(EV/'validation.json').write_text(json.dumps(reports,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR');return
   prepare()
 except Exception as e:
  state['done']=True;(EV/'capture_error.txt').write_text(str(e));u.log_error(str(e));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:state['busy']=False
prepare();handle=u.register_slate_post_tick_callback(tick)


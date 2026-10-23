"""Live collision/persistence verification and actual overview/pole renders."""
import unreal as u,json,time
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/Grid20';g=json.loads((ROOT/'Art/Grid20/layout.json').read_text());scope={};exec((ROOT/'Tools/desert_route_capture.py').read_text().split('def prepare():')[0],scope)
L=scope['level'];A=scope['actors'];W=scope['editor'];views=[('DesertKarting','Overhead'),('DesertKarting_Visual','Overhead'),('DesertKarting_Visual','Pole')];reports={};state={'i':0,'busy':False,'done':False};tasks=[]
def validate():
 world=W.get_editor_world();slots=sorted([a for a in A.get_all_level_actors() if isinstance(a,u.GridStartSlot)],key=lambda a:a.get_editor_property('position_number'));assert [a.get_editor_property('position_number') for a in slots]==list(range(1,21));result=scope['validate']();result['slots']=[];result['slot_failures']=[]
 for actor,entry in zip(slots,g['slots']):
  p=actor.get_actor_location();assert abs(p.x-entry['location_cm'][0])<.1 and abs(p.y-entry['location_cm'][1])<.1;assert not actor.get_actor_enable_collision()
  hits=[]
  for pt in entry['surface_samples_cm']:
   hit=u.SystemLibrary.line_trace_single(world,u.Vector(pt[0],pt[1],150),u.Vector(pt[0],pt[1],-100),u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True);labels=[v.get_actor_label() for v in hit.to_tuple() if isinstance(v,u.Actor)] if hit else []
   if not any('DK_02 ' in label and 'asphalt' in label for label in labels):hits.append({'point':pt,'hit':labels})
  sweep=u.SystemLibrary.box_trace_multi(world,u.Vector(p.x,p.y,85),u.Vector(p.x,p.y,85.1),u.Vector(110,90,70),actor.get_actor_rotation(),u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True)
  obstacles=[]
  for hit in (sweep or []):
   obstacles.extend(v.get_actor_label() for v in hit.to_tuple() if isinstance(v,u.Actor))
  if hits or obstacles:result['slot_failures'].append({'number':entry['number'],'unsupported':hits,'obstructions':obstacles})
  result['slots'].append({'number':entry['number'],'location_cm':[p.x,p.y,p.z],'yaw_deg':actor.get_actor_rotation().yaw,'footprint_support_rays':9,'full_envelope_box_obstructions':obstacles})
 result['existing_checkpoint_actor_classes']=[a.get_class().get_name() for a in A.get_all_level_actors() if 'checkpoint' in a.get_class().get_name().lower()]
 return result

def prepare():
 name,view=views[state['i']];assert L.load_level('/Game/RoadToF1/Maps/'+name)
 if view=='Overhead':
  camera=A.spawn_actor_from_class(u.CameraActor,u.Vector(2500,60,12000),u.Rotator(pitch=-90,yaw=0));cc=camera.camera_component;cc.set_editor_property('projection_mode',u.CameraProjectionMode.ORTHOGRAPHIC);cc.set_editor_property('ortho_width',3700);cc.set_editor_property('aspect_ratio',2/3);cc.set_editor_property('constrain_aspect_ratio',True);cc.set_editor_property('auto_calculate_ortho_planes',False);cc.set_editor_property('ortho_near_clip_plane',1);cc.set_editor_property('ortho_far_clip_plane',50000);size=(1600,2400)
 else:
  p=g['slots'][0]['location_cm'];camera=A.spawn_actor_from_class(u.CameraActor,u.Vector(p[0],p[1],p[2]+40),u.Rotator(yaw=g['slots'][0]['yaw_deg']));camera.camera_component.set_field_of_view(85);size=(1920,1080)
 state.update(camera=camera,start=time.monotonic(),validated=False,task=None,completed=None,size=size);u.SystemLibrary.execute_console_command(None,'r.SetRes %dx%dw'%size)
def tick(dt):
 if state['busy'] or state['done']:return
 state['busy']=True
 try:
  elapsed=time.monotonic()-state['start'];name,view=views[state['i']]
  if elapsed>5 and not state['validated']:reports[name]=validate();state['validated']=True
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


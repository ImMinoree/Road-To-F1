"""Run in the real editor: road-collision validation and repeatable rendered views."""
import unreal as u,json,time,math
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/DesertKarting'
level=u.get_editor_subsystem(u.LevelEditorSubsystem);assert level.load_level('/Game/RoadToF1/Maps/DesertKarting')
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
# Preserve GLB double-sided surfaces on this first import too.
for path in u.EditorAssetLibrary.list_assets('/Game/RoadToF1/DesertKarting/Materials',recursive=False):
 m=u.load_asset(path)
 if isinstance(m,u.Material) and not m.get_editor_property('two_sided'):
  m.set_editor_property('two_sided',True);u.MaterialEditingLibrary.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if isinstance(a,u.CameraActor):actors.destroy_actor(a)
 if isinstance(a,u.DirectionalLight):
  a.light_component.set_mobility(u.ComponentMobility.MOVABLE);a.set_actor_rotation(u.Rotator(pitch=-32,yaw=145),False);a.light_component.set_editor_property('intensity',65000);a.light_component.set_light_color(u.LinearColor(1,.88,.72))
 if isinstance(a,u.SkyLight):
  a.light_component.set_mobility(u.ComponentMobility.MOVABLE);a.light_component.set_editor_property('intensity',1.3);a.light_component.set_editor_property('real_time_capture',True);a.light_component.recapture_sky()
shots=[['Driver',[800,0,80],[-3,0,0]],['Ground',[3700,650,60],[-3,-15,0]],['Overview',[32800,27800,18500],[-22,-128,0]]]
(EV/'shots.json').write_text(json.dumps(shots,indent=2))
cameras={}
for name,p,r in shots:
 c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(*p),u.Rotator(pitch=r[0],yaw=r[1],roll=r[2]));c.set_actor_label('Desert_'+name);c.camera_component.set_field_of_view(85)
 cameras[name]=c
assert level.save_current_level()
if '-DesertGroundOnly' in u.SystemLibrary.get_command_line():shots=[s for s in shots if s[0]=='Ground']
for cmd in ['sg.ViewDistanceQuality 3','sg.AntiAliasingQuality 3','sg.ShadowQuality 3','sg.GlobalIlluminationQuality 3','sg.ReflectionQuality 3','sg.TextureQuality 3','sg.PostProcessQuality 3','r.ScreenPercentage 100','r.HighResScreenshotDelay 8','r.SetRes 1920x1080w']:
 u.SystemLibrary.execute_console_command(None,cmd)
def camera(i):
 p,r=shots[i][1:];editor.set_level_viewport_camera_info(u.Vector(*p),u.Rotator(pitch=r[0],yaw=r[1],roll=r[2]))
camera(0);state={'i':0,'time':time.monotonic(),'shot':False,'tested':False,'positioned':False}
def validate():
 world=editor.get_editor_world();results=[]
 # Along the aligned starting straight, plus transverse road probes.
 for x in [800,1500,2500,3500,4500]:
  for y in [-300,0,300]:
   hit=u.SystemLibrary.line_trace_single(world,u.Vector(x,y,200),u.Vector(x,y,-200),u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True)
   parts=hit.to_tuple() if hit else []
   labels=[v.get_actor_label() for v in parts if isinstance(v,u.StaticMeshActor)]
   results.append({'point':[x,y],'actors':labels,'road':any('02 Track surface' in l and 'asphalt' in l for l in labels)})
 (EV/'collision.json').write_text(json.dumps({'rays':len(results),'passed':sum(r['road'] for r in results),'results':results},indent=2))
def tick(dt):
 if state.get('busy') or state.get('done'):return
 state['busy']=True
 try:
  elapsed=time.monotonic()-state['time']
  if not state['positioned']:
   if elapsed<5:return
   # Editor startup restores its saved viewport after executing ExecCmds.
   camera(state['i']);state['positioned']=True;state['time']=time.monotonic();return
  if elapsed>5 and not state['tested']:state['tested']=True;validate()
  if elapsed>22 and not state['shot']:
   state['shot']=True;state['requested_at']=time.time();u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(EV/(shots[state['i']][0]+'.png')),camera=cameras[shots[state['i']][0]])
  output=EV/(shots[state['i']][0]+'.png')
  if state['shot'] and output.exists() and output.stat().st_mtime>=state['requested_at'] and 'completed_at' not in state:state['completed_at']=time.monotonic()
  # Wait for actual screenshot completion before moving the viewport. A queued
  # high-res capture can otherwise restore the previous camera after a stall.
  if 'completed_at' in state and time.monotonic()-state['completed_at']>5:
   state['i']+=1
   if state['i']>=len(shots):
    state['done']=True;u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR');return
   state['time']=time.monotonic();state['shot']=False;state.pop('completed_at',None);camera(state['i'])
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

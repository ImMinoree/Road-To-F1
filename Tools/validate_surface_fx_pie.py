"""Bounded actual PIE effects checks. Diagnostic movement is transient; no map is saved."""
import unreal as u,json,time,traceback,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/SurfaceFX';E.mkdir(parents=True,exist_ok=True)
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);Ed=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'Content/RoadToF1/Maps').glob('*.umap')}
cam=A.spawn_actor_from_class(u.CameraActor,u.Vector(0,0,300));cam.tags=['SurfaceFXEvidenceCamera'];cam.camera_component.set_field_of_view(65)
mesh=u.load_asset('/Game/RoadToF1/PlayerVisuals/CockpitReferenceV2/SM_CV2_PlayerChassis') or u.load_asset('/Game/RoadToF1/PlayerVisuals/FirstPerson/SM_PlayerKartChassis');assert mesh
preview_body=A.spawn_actor_from_class(u.StaticMeshActor,u.Vector(-50000,-50000,0));preview_body.tags=['SurfaceFXEvidenceBody'];preview_body.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE);preview_body.static_mesh_component.set_static_mesh(mesh);preview_body.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);preview_body.set_actor_enable_collision(False)
g=json.loads((R/'Art/InfieldGrass/scatter.json').read_text());base=min(g['placements'],key=lambda p:(p['location'][0]-2000)**2+(p['location'][1]+3500)**2)['location']
state=dict(start=time.monotonic(),started=False,ready=False,busy=False,shots=set(),samples=[],finished=None);tasks=[]
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  if not state['started'] and time.monotonic()-state['start']>5:state['started']=True;L.editor_request_begin_play()
  if not L.is_in_play_in_editor():return
  w=Ed.get_game_world()
  if not w:return
  if not state['ready']:
   if u.GameplayStatics.get_time_seconds(w)<11:return
   pc=u.GameplayStatics.get_player_controller(w,0);p=u.GameplayStatics.get_player_pawn(w,0);fx=p.get_component_by_class(u.KartSurfaceFX);assert fx
   p.set_actor_tick_enabled(False);p.set_actor_enable_collision(False)
   camera=next(a for a in u.GameplayStatics.get_all_actors_of_class(w,u.CameraActor) if 'SurfaceFXEvidenceCamera' in list(map(str,a.tags)))
   body=next(a for a in u.GameplayStatics.get_all_actors_of_class(w,u.StaticMeshActor) if 'SurfaceFXEvidenceBody' in list(map(str,a.tags)))
   pc.set_view_target_with_blend(camera,0)
   for cmd in ['r.ScreenPercentage 100','r.SetRes 1600x900w','t.MaxFPS 60']:u.SystemLibrary.execute_console_command(w,cmd,pc)
   state.update(ready=True,pc=pc,pawn=p,fx=fx,camera=camera,body=body,test_start=u.GameplayStatics.get_time_seconds(w))
  t=u.GameplayStatics.get_time_seconds(w)-state['test_start'];p=state['pawn'];fx=state['fx'];phase='Grass'
  if t<3:pos=u.Vector(base[0]+t*550,base[1],base[2]+31)
  elif t<4.6:phase='Stopped';pos=u.Vector(base[0]+3*550,base[1],base[2]+31)
  elif t<7:phase='Asphalt';pos=u.Vector(-800+(t-4.6)*550,0,31)
  elif t<8.2:phase='Airborne';pos=u.Vector(base[0]+(t-7)*550,base[1],base[2]+231)
  else:phase='Reverse';pos=u.Vector(base[0]+1200-(t-8.2)*550,base[1],base[2]+31)
  p.set_actor_location_and_rotation(pos,u.Rotator(),False,False);state['body'].set_actor_location_and_rotation(pos-u.Vector(0,0,31),u.Rotator(),False,False)
  eye=pos+u.Vector(-340,120,110);target=pos+u.Vector(-100,0,-15);state['camera'].set_actor_location_and_rotation(eye,u.MathLibrary.find_look_at_rotation(eye,target),False,False)
  state['samples'].append(dict(phase=phase,t=t,wheels=fx.get_editor_property('emitting_wheels'),live=fx.get_editor_property('live_particles'),total=fx.get_editor_property('total_emitted')))
  for name,when in [('GrassTrail',2.5),('Stopped',4.4),('Asphalt',6.7),('ReverseTrail',10.5)]:
   if t>when and name not in state['shots']:
    state['shots'].add(name);u.SystemLibrary.execute_console_command(w,'HighResShot 1600x900 filename='+str(E/(name+'.png')),state['pc'])
  if t>11 and state['finished'] is None:
   samples=state['samples'];checks={}
   for phase,lo,hi in [('Grass',.5,2.8),('Stopped',4.1,4.5),('Asphalt',5.1,6.8),('Airborne',7.3,8.1),('Reverse',8.7,10.7)]:
    rows=[s for s in samples if s['phase']==phase and lo<s['t']<hi];assert rows,phase
    checks[phase]=dict(max_wheels=max(s['wheels'] for s in rows),max_live=max(s['live'] for s in rows),emitted=rows[-1]['total']-rows[0]['total'])
   assert checks['Grass']['emitted']>0 and checks['Reverse']['emitted']>0,checks
   assert all(checks[p]['max_wheels']==0 and checks[p]['emitted']==0 for p in ['Stopped','Asphalt','Airborne']),checks
   assert checks['Stopped']['max_live']==0,checks
   assert max(s['live'] for s in samples)<=96
   assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'Content/RoadToF1/Maps').glob('*.umap')}
   (E/'pie_validation.json').write_text(json.dumps(dict(actual_pie=True,world_type=str(w.world_type) if hasattr(w,'world_type') else 'PIE',checks=checks,max_live=max(s['live'] for s in samples),maps_unchanged=True,note='Transient diagnostic motion tests FX only, not off-track handling or tire slip'),indent=2));state['finished']=time.monotonic()
  if state['finished'] and time.monotonic()-state['finished']>3:L.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
  if time.monotonic()-state['start']>150:raise RuntimeError('Surface FX validation timed out')
 except Exception:
  (E/'pie_error.txt').write_text(traceback.format_exc());u.log_error(traceback.format_exc());u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

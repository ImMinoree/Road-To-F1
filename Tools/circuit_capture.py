"""Read capture_phase.txt, capture the same three views, exit this editor only."""
import unreal as u,json,time,math
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EVIDENCE=ROOT/'Evidence/CircuitDevelopment'
phase=(EVIDENCE/'capture_phase.txt').read_text().strip();dest=EVIDENCE/phase;dest.mkdir(exist_ok=True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);assert level.load_level('/Game/RoadToF1/Maps/CircuitDevelopment')
shots=json.loads((EVIDENCE/'shots.json').read_text());editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
filter_path=EVIDENCE/'capture_views.json'
if filter_path.exists():shots=[s for s in shots if s[0] in json.loads(filter_path.read_text())]
for cmd in ['sg.ViewDistanceQuality 3','sg.AntiAliasingQuality 3','sg.ShadowQuality 3','sg.GlobalIlluminationQuality 3','sg.ReflectionQuality 3','sg.PostProcessQuality 3','sg.TextureQuality 3','r.ScreenPercentage 100','r.Shadow.Virtual.Enable 0','r.HighResScreenshotDelay 8','r.SetRes 1920x1080w']:
 u.SystemLibrary.execute_console_command(None,cmd)
def camera(i):
 if phase=='Phase3' and shots[i][0]=='Overview':
  # Validation-only overview: show all placed scenery above the runtime cull envelope.
  for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
   for component in actor.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):component.set_cull_distances(50000,65000)
 p,r=shots[i][1:];editor.set_level_viewport_camera_info(u.Vector(*p),u.Rotator(pitch=r[0],yaw=r[1],roll=r[2]))
camera(0);state={'i':0,'time':time.monotonic(),'shot':False,'tested':False}
def collision_gate():
 if phase not in ['Phase1','Phase3']:return
 report_path=EVIDENCE/('phase1.json' if phase=='Phase1' else 'phase3.json')
 report=json.loads(report_path.read_text())
 if report.get('collision_rays',0)>0:return
 g=json.loads((ROOT/'Art/CircuitDevelopment/geometry.json').read_text());route=g['route'];world=editor.get_editor_world();failures=[];checked=0;types=[]
 if phase=='Phase3':
  static=u.get_editor_subsystem(u.StaticMeshEditorSubsystem);assert static
  for name in ['TireRed','TireWhite','TireBlack']:
   mesh=u.load_asset('/Game/RoadToF1/CircuitDevelopment/Props/'+name)
   if static.get_simple_collision_count(mesh)==0:assert static.add_simple_collisions(mesh,u.ScriptCollisionShapeType.BOX)>=0
   u.EditorAssetLibrary.save_loaded_asset(mesh)
  for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
   for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
    if c.static_mesh and c.static_mesh.get_name().startswith('Tire'):
     c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);c.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS)
 for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
  if isinstance(a,u.StaticMeshActor) and a.get_actor_label().startswith('CD_'):
   a.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
   a.static_mesh_component.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS)
 for i in range(0,len(route),8):
  p=route[i];q=route[(i+1)%len(route)];dx=q[0]-p[0];dy=q[1]-p[1];l=math.hypot(dx,dy)
  for offset in [-300,0,300]:
   x=p[0]-dy/l*offset;y=p[1]+dx/l*offset
   result=u.SystemLibrary.line_trace_single(world,u.Vector(x,y,p[2]+200),u.Vector(x,y,p[2]-200),u.TraceTypeQuery.ECC_VISIBILITY,True,[],u.DrawDebugTrace.NONE,True)
   hit=result if isinstance(result,u.HitResult) else next((v for v in (result or []) if isinstance(v,u.HitResult)),None)
   if len(types)<2:types.append(str(type(result)))
   parts=hit.to_tuple() if hit else []
   road_hit=any(isinstance(v,u.StaticMeshActor) and v.get_actor_label().startswith('CD_Road_') for v in parts)
   checked+=1
   if not road_hit:failures.append([i,offset])
 report.update(collision_rays=checked,collision_failures=failures,trace_return_types=types)
 if phase=='Phase3':
  placements=json.loads((ROOT/'Art/CircuitDevelopment/environment.json').read_text())['placements'];tests=0;hits=0
  for entry in [p for p in placements if p['mesh'].startswith('Tire')][::300]:
   p=entry['location_cm'];hit=u.SystemLibrary.line_trace_single(world,u.Vector(p[0],p[1],p[2]+200),u.Vector(p[0],p[1],p[2]-100),u.TraceTypeQuery.ECC_VISIBILITY,False,[],u.DrawDebugTrace.NONE,True)
   parts=hit.to_tuple() if hit else [];tests+=1
   if any(isinstance(v,u.HierarchicalInstancedStaticMeshComponent) and v.static_mesh.get_name().startswith('Tire') for v in parts):hits+=1
  report.update(tire_collision_probes=tests,tire_collision_hits=hits)
 report_path.write_text(json.dumps(report,indent=2))
def tick(dt):
 if state.get('busy') or state.get('done'):return
 state['busy']=True
 try:
  elapsed=time.monotonic()-state['time']
  if not state['tested'] and elapsed>5:
   state['tested']=True;collision_gate()
  if elapsed>20 and not state['shot']:
   state['shot']=True
   u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(dest/(shots[state['i']][0]+'.png')))
  if elapsed>27:
   state['i']+=1
   if state['i']>=len(shots):
    state['done']=True;u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR');return
   state['time']=time.monotonic();state['shot']=False;camera(state['i'])
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

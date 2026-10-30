"""Replace tire placement with closer full-edge runs; assets and race systems retained."""
import unreal as u,json,time,math,hashlib,traceback
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/FullPaceAndTireGaps';B='/Game/RoadToF1/Trackside/TireBarriers';plan=json.loads((E/'edge_plan.json').read_text());edges=json.loads((R/'Art/RacingAI/track_edges.json').read_text());route=edges['center']
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem);assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');u.EditorPythonScripting.set_keep_python_script_alive(True)
state={'pass':'before','view':0,'phase':'warm','epoch':time.monotonic(),'busy':False};report={'saved':False};cameras=[]
def nxt(p):state.update(phase=p,epoch=time.monotonic())
def parts(h):return h.to_tuple() if h else []
def ignored():return list(u.GameplayStatics.get_all_actors_of_class(W.get_editor_world(),u.InstancedFoliageActor))
def ground(x,y,world=None):
 world=world or W.get_editor_world()
 h=u.SystemLibrary.box_trace_single(world,u.Vector(x,y,200),u.Vector(x,y,-200),u.Vector(.5,.5,.5),u.Rotator(),u.TraceTypeQuery.ECC_VISIBILITY,True,ignored(),u.DrawDebugTrace.NONE,True)
 assert h,('Missing ground',x,y)
 return next(v.z for v in parts(h) if isinstance(v,u.Vector))-.5
def tires():
 out=[]
 for a in A.get_all_level_actors():
  for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
   if c.static_mesh and c.static_mesh.get_path_name().startswith(B+'/'):
    assert c.get_collision_enabled()==u.CollisionEnabled.QUERY_AND_PHYSICS
    out.append(c)
 return out
def keys():
 out=[]
 for c in tires():
  for i in range(c.get_instance_count()):
   t=c.get_instance_transform(i,world_space=True);p=t.translation;r=t.rotation.rotator();s=t.scale3d
   out.append((c.static_mesh.get_path_name(),)+tuple(round(v,3) for v in [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]))
 return sorted(out)
def signature():
 out={}
 for a in A.get_all_level_actors():
  if isinstance(a,u.InstancedFoliageActor) or a in cameras:continue
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
  item=[a.get_class().get_name(),p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z,a.get_actor_enable_collision()]
  for c in a.get_components_by_class(u.StaticMeshComponent):
   if c.static_mesh:item.extend([c.get_name(),c.static_mesh.get_path_name(),[list(c.get_world_transform().translation.to_tuple()),list(c.get_world_transform().scale3d.to_tuple()),list(c.get_world_transform().rotation.rotator().to_tuple())],str(c.get_collision_enabled())])
  if isinstance(a,u.Light):item.extend([[a.light_component.get_editor_property('light_color').r,a.light_component.get_editor_property('light_color').g,a.light_component.get_editor_property('light_color').b,a.light_component.get_editor_property('light_color').a],a.light_component.get_editor_property('intensity')])
  out[a.get_name()]=item
 return out
def sweep():
 blocked=[];world=W.get_editor_world();count=0
 for i,p in enumerate(route):
  q=route[(i+1)%len(route)];dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy);yaw=math.degrees(math.atan2(dy,dx))
  width=min(math.dist(p[:2],edges[k][i][:2]) for k in ['left','right'])-110
  for lane in [-width,0,width]:
   x=p[0]-dy/length*lane;y=p[1]+dx/length*lane;z=ground(x,y)+31
   h=u.SystemLibrary.box_trace_single(world,u.Vector(x,y,z),u.Vector(x+dx,y+dy,z),u.Vector(90,60,16),u.Rotator(yaw=yaw),u.TraceTypeQuery.ECC_VISIBILITY,False,[],u.DrawDebugTrace.NONE,True)
   count+=1
   if h:blocked.append([i,round(lane,1),[a.get_name() for a in parts(h) if isinstance(a,u.Actor)]])
 for a in A.get_all_level_actors():
  if a.get_class().get_name()!='GridStartSlot':continue
  p=a.get_actor_location();h=u.SystemLibrary.box_trace_single(world,p,p+u.Vector(.01,0,0),u.Vector(90,60,16),a.get_actor_rotation(),u.TraceTypeQuery.ECC_VISIBILITY,False,[],u.DrawDebugTrace.NONE,True)
  count+=1
  if h:blocked.append(['grid',a.get_name(),[b.get_name() for b in parts(h) if isinstance(b,u.Actor)]])
 return {'sweeps':count,'blocked':blocked}
def aerial():
 c=A.spawn_actor_from_class(u.CameraActor,u.Vector(2925,-10350,40000),u.Rotator(pitch=-90));cameras.append(c);cc=c.camera_component
 for k,v in [('projection_mode',u.CameraProjectionMode.ORTHOGRAPHIC),('ortho_width',31000),('aspect_ratio',1.2),('constrain_aspect_ratio',True),('auto_calculate_ortho_planes',False),('ortho_near_clip_plane',1),('ortho_far_clip_plane',100000)]:cc.set_editor_property(k,v)
 return c

def finish():
 (E/'validation.json').write_text(json.dumps(report,indent=2));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')

def point_pawn(idx):
 pw=W.get_game_world();pawn=u.GameplayStatics.get_player_pawn(pw,0);assert isinstance(pawn,u.ProofPawn)
 for kart in u.GameplayStatics.get_all_actors_of_class(pw,u.ProofPawn):kart.set_kart_test_input(0,0,True)
 p=route[idx];q=route[(idx+3)%len(route)];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));pawn.set_actor_location_and_rotation(u.Vector(p[0],p[1],31),u.Rotator(yaw=yaw),False,True);pawn.get_component_by_class(u.KartTireDynamics).reset_motion()
 if pawn.is_third_person_view():pawn.toggle_camera_view()
 u.GameplayStatics.get_player_controller(pw,0).set_view_target_with_blend(pawn,0)
 return pawn
asphalt_polygons=json.loads((E/'asphalt_polygons.json').read_text())
def asphalt_clearance(x,y):
 best=1.e30
 for poly in asphalt_polygons:
  inside=False
  for i,a in enumerate(poly):
   b=poly[(i+1)%len(poly)]
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
   dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(.0001,dx*dx+dy*dy)));best=min(best,(x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2)
  if inside:return 0
 return math.sqrt(best)

rim_offsets=[(24*math.cos(i*math.tau/8),24*math.sin(i*math.tau/8)) for i in range(8)]
def supported(heights):
 top=max(heights)
 return max(heights)-min(heights)<=2.5 or (top-min(heights)<=25 and sum(top-h<=2.5 for h in heights)>=6)

def above_support(hit,heights):
 # The stack is cylindrical: box corners may graze the supporting grass beyond its round footprint.
 actors=[a for a in parts(hit) if isinstance(a,u.Actor)]
 return bool(actors) and supported(heights) and all('grass' in a.get_actor_label().lower() for a in actors)

def place():
 state['sig']=signature();state['before']=sweep();report['before_corridor']=state['before'];report['previous_instances']=len(keys());world=W.get_editor_world();ig=ignored();used=[];runs=[];rejected=[];grid=[a.get_actor_location() for a in A.get_all_level_actors() if a.get_class().get_name()=='GridStartSlot']
 for section in plan['sections']:
  rows=[]
  for j,col in enumerate(section['columns']):
   x,y=col['xy'];reason=None
   if col['access_opening']:reason='service opening'
   elif col['clearance_cm']<62.5 and col.get('asphalt_clearance_cm',0)<100:reason='road/curb/runoff clearance'
   elif any(math.hypot(x-p.x,y-p.y)<350 for p in grid):reason='grid clearance'
   elif any(math.hypot(x-p[0],y-p[1])<50 for p in used):reason='opposing edge wall clearance'
   if reason:rows.append(None);rejected.append([section['side'],j,reason]);continue
   heights=[ground(x+dx,y+dy) for dx,dy in rim_offsets];z=max(heights)
   # Full stack envelope plus a little clearance; do not tuck tires under booths.
   # The bottom of a zero-distance box can touch ground; lift it 3 cm.
   h=u.SystemLibrary.box_trace_single(world,u.Vector(x,y,z+58),u.Vector(x+.01,y,z+58),u.Vector(27,27,55),u.Rotator(yaw=col['yaw']),u.TraceTypeQuery.ECC_VISIBILITY,True,ig,u.DrawDebugTrace.NONE,True)
   if h and above_support(h,heights):h=None
   if (not supported(heights) or h) and -100<z<80:
    for shift,along in [(12,0),(-12,0),(24,0),(-24,0),(48,0),(72,0),(48,24),(48,-24),(60,24),(60,-24),(72,24),(72,-24)]:
     normal=col.get('normal',[0,0]);xx=x+normal[0]*shift-normal[1]*along;yy=y+normal[1]*shift+normal[0]*along
     neighbors=[section['columns'][(j-1)%len(section['columns'])]['xy'],section['columns'][(j+1)%len(section['columns'])]['xy']]
     if along and any(math.hypot(xx-p[0],yy-p[1])<50 for p in neighbors):continue
     if (abs(shift)>24 or along) and asphalt_clearance(xx,yy)<75:continue
     hs=[ground(xx+dx,yy+dy) for dx,dy in rim_offsets];zz=max(hs)
     if not supported(hs) or not -100<zz<80:continue
     hh=u.SystemLibrary.box_trace_single(world,u.Vector(xx,yy,zz+58),u.Vector(xx+.01,yy,zz+58),u.Vector(27,27,55),u.Rotator(yaw=col['yaw']),u.TraceTypeQuery.ECC_VISIBILITY,True,ig,u.DrawDebugTrace.NONE,True)
     if hh and above_support(hh,hs):hh=None
     if not hh:
      x,y,z,heights,h=xx,yy,zz,hs,hh;col=dict(col,xy=[xx,yy]);report['terrain_adjustments']=report.get('terrain_adjustments',0)+1;break
   if not supported(heights) or not -100<z<80 or h:
    rows.append(None);rejected.append([section['side'],j,'fixed object or uneven ground'])
    hit_names=','.join(a.get_name() for a in parts(h) if isinstance(a,u.Actor)) or 'height_variation';counts=report.setdefault('obstacle_counts',{});counts[hit_names]=counts.get(hit_names,0)+1
    if len(report.setdefault('obstacle_examples',[]))<40:report['obstacle_examples'].append({'xy':[x,y],'heights':heights,'hits':[a.get_name() for a in parts(h) if isinstance(a,u.Actor)]})
    continue
   rows.append(dict(col,z=z-.1,side=section['side']));used.append((x,y))
  run=[]
  for col in rows+[None]:
   if col is None:
    if len(run)>=1:runs.append({'side':section['side'],'columns':run})
    run=[]
   else:run.append(col)
 transforms={'Black':[],'Red':[]}
 for section in runs:
  for j,col in enumerate(section['columns']):
   x,y=col['xy'];color='Black' if (j//5)%2==0 else 'Red'
   for layer in range(3):transforms[color].append(u.Transform(location=u.Vector(x,y,col['z']+layer*18.4),rotation=u.Rotator(yaw=col['yaw']+(j*137.508+layer*79.3)%360)))
 report['planned_columns']=sum(len(s['columns']) for s in plan['sections']);report['rejected_columns']=rejected;report['sections']=[{'side':s['side'],'columns':len(s['columns']),'first_route_index':s['columns'][0]['route_index'],'last_route_index':s['columns'][-1]['route_index']} for s in runs];report['colors']={k:len(v) for k,v in transforms.items()};state['runs']=runs
 (E/'placed_columns.json').write_text(json.dumps(runs,indent=2));(E/'candidate_report.json').write_text(json.dumps(report,indent=2));assert sum(len(v) for v in transforms.values())>=report['previous_instances']*.95,'Coverage regression: do not save'
 for color,ts in transforms.items():
  ft=u.load_asset(B+'/Instancing/FT_TireBarrier_'+color);u.InstancedFoliageActor.remove_all_instances(world,ft);u.InstancedFoliageActor.add_instances(world,ft,ts)
 nxt('validate')


views=[('gap_west',330),('gap_hairpin',500),('gap_sweeper',615)]
def foliage_signature():
 out={}
 for a in A.get_all_level_actors():
  for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
   if not c.static_mesh or c.static_mesh.get_path_name().startswith(B+'/'):continue
   ts=[]
   for i in range(c.get_instance_count()):
    t=c.get_instance_transform(i,world_space=True);ts.append([round(v,4) for v in list(t.translation.to_tuple())+list(t.rotation.rotator().to_tuple())+list(t.scale3d.to_tuple())])
   out[c.get_name()]=[c.static_mesh.get_path_name(),len(ts),hashlib.sha256(json.dumps(ts).encode()).hexdigest()]
 return out

def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  age=time.monotonic()-state['epoch'];phase=state['phase']
  if phase=='warm' and age>4:
   state['foliage']=foliage_signature();state['pass']='after';place()
  elif phase=='play':
   pw=W.get_game_world()
   if pw and u.GameplayStatics.get_time_seconds(pw)>10:point_pawn(views[state['view']][1]);nxt('eye')
  elif phase=='eye' and age>4:
   u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/(state['pass']+'_'+views[state['view']][0]+'.png')));nxt('shot')
  elif phase=='shot' and age>2:
   state['view']+=1
   if state['view']<len(views):point_pawn(views[state['view']][1]);nxt('eye')
   else:L.editor_request_end_play();nxt('apply' if state['pass']=='before' else 'finish')
  elif phase=='apply' and age>3:
   assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');place()
  elif phase=='validate' and age>3:
   assert signature()==state['sig'];after=sweep();report['after_corridor']=after;assert after==state['before'],'New kart/grid obstruction'
   checks=[]
   for s in state['runs']:
    col=s['columns'][len(s['columns'])//2];x,y=col['xy'];z=col['z']+27.6;h=u.SystemLibrary.line_trace_single(W.get_editor_world(),u.Vector(x-80,y,z),u.Vector(x+80,y,z),u.TraceTypeQuery.ECC_VISIBILITY,False,[],u.DrawDebugTrace.NONE,True)
    assert any(isinstance(c,u.StaticMeshComponent) and c.static_mesh and c.static_mesh.get_path_name().startswith(B+'/') for c in parts(h));checks.append(True)
   expected=keys();report.update(instances=len(expected),hism_components=len(tires()),collision_sections_passed=len(checks),unchanged_existing_actors=True)
   assert L.save_current_level();assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');assert keys()==expected;report.update(saved=True,reload_verified=True)
   for c in tires():c.set_cull_distances(90000,100000)
   state['camera']=aerial();nxt('aerial')
   assert foliage_signature()==state['foliage'];report['other_foliage_preserved']=True
  elif phase=='aerial' and age>6:
   state['task']=u.AutomationLibrary.take_high_res_screenshot(2400,2000,str(E/'all_repaired_edges.png'),camera=state['camera'],delay=1);nxt('aerial_wait')
  elif phase=='aerial_wait' and state['task'].is_task_done() and age>2:
   A.destroy_actor(state['camera']);assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');state.update(view=0,**{'pass':'after'});L.editor_request_begin_play();nxt('play')
  elif phase=='finish' and age>3:finish()
 except Exception:
  report['error']=traceback.format_exc();(E/'error.txt').write_text(report['error']);u.log_error(report['error'])
  if L.is_in_play_in_editor():L.editor_request_end_play()
  finish()
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)

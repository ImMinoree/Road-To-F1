"""Add existing tire foliage along measured outer edges, validate and save/reload."""
import unreal as u,json,time,math,hashlib,traceback,statistics
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/ExpandedTireBarriers';B='/Game/RoadToF1/Trackside/TireBarriers'
plan=json.loads((E/'placement_plan.json').read_text());before=json.loads((E/'inventory_before.json').read_text());edges=json.loads((R/'Art/RacingAI/track_edges.json').read_text());route=edges['center']
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
u.EditorPythonScripting.set_keep_python_script_alive(True)
state={'phase':'warm','epoch':time.monotonic(),'busy':False};report={'saved':False,'sections':[]};cameras=[]
def nxt(p):state.update(phase=p,epoch=time.monotonic())
def parts(h):return h.to_tuple() if h else []
def ignored():return list(u.GameplayStatics.get_all_actors_of_class(W.get_editor_world(),u.InstancedFoliageActor))
def ground(x,y,world=None):
 world=world or W.get_editor_world()
 h=u.SystemLibrary.line_trace_single(world,u.Vector(x,y,150),u.Vector(x,y,-150),u.TraceTypeQuery.ECC_VISIBILITY,True,ignored(),u.DrawDebugTrace.NONE,True)
 assert h,('Missing ground',x,y)
 return next(v.z for v in parts(h) if isinstance(v,u.Vector))
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
def tick(dt):
 if state['busy']:return
 state['busy']=True
 try:
  age=time.monotonic()-state['epoch'];phase=state['phase']
  if phase=='warm' and age>5:
   state['sig']=signature();state['original']=keys();assert len(state['original'])==144
   state['corridor']=sweep();report['baseline_corridor']=state['corridor'];transforms={'Black':[],'Red':[]};accepted=[];rejected=[]
   originalxy=list({(k[1],k[2]) for k in state['original']});used=list(originalxy);world=W.get_editor_world();ig=ignored()
   for section in plan['sections']:
    rows=[]
    for j,col in enumerate(section['columns']):
     x,y=col['xy']
     if col['existing']:rows.append(dict(col,z=ground(x,y)-.1));continue
     if any(math.hypot(x-p[0],y-p[1])<53.8 for p in used):rejected.append([section['id'],j,'near another column']);rows.append(None);continue
     heights=[ground(x+dx,y+dy) for dx,dy in [(0,0),(20,0),(-20,0),(0,20),(0,-20)]];z=max(heights)
     h=u.SystemLibrary.sphere_trace_single(world,u.Vector(x,y,z+31),u.Vector(x+.01,y,z+31),26,u.TraceTypeQuery.ECC_VISIBILITY,True,ig,u.DrawDebugTrace.NONE,True)
     if max(heights)-min(heights)>2.5 or not -100<z<80 or h:
      rejected.append([section['id'],j,'terrain or fixed object',heights,[a.get_name() for a in parts(h) if isinstance(a,u.Actor)]]);rows.append(None);continue
     rows.append(dict(col,z=z-.1));used.append((x,y))
    # Runs split at obstructions; only substantial continuous walls are retained.
    runs=[];run=[]
    for col in rows+[None]:
     if col is None:
      if len(run)>=12:runs.append(run)
      run=[]
     else:run.append(col)
    for n,run in enumerate(runs):
     for j,col in enumerate(run):
      if col['existing']:continue
      x,y=col['xy'];color='Red' if ((j//4+section['corner'])%2) else 'Black'
      for layer in range(3):transforms[color].append(u.Transform(location=u.Vector(x,y,col['z']+18.4*layer),rotation=u.Rotator(yaw=col['yaw']+(j*137.508+layer*79.3)%360)))
     accepted.append(dict(id=section['id']+'_'+str(n+1),corner=section['corner'],route_index=section['route_index'],side=section['side'],columns=run))
   (E/'candidate_diagnostics.json').write_text(json.dumps({'accepted_runs':[(s['id'],len(s['columns'])) for s in accepted],'counts':{k:len(v) for k,v in transforms.items()},'rejected':rejected},indent=2))
   assert sum(len(v) for v in transforms.values())>1200
   report['rejected_columns']=rejected;report['added_by_color']={k:len(v) for k,v in transforms.items()}
   report['sections']=[{'id':s['id'],'columns':len(s['columns']),'corner':s['corner'],'side':s['side']} for s in accepted]
   (E/'placed_columns.json').write_text(json.dumps(accepted,indent=2));state['accepted']=accepted
   for color,ts in transforms.items():u.InstancedFoliageActor.add_instances(world,u.load_asset(B+'/Instancing/FT_TireBarrier_'+color),ts)
   nxt('validate')
  elif phase=='validate' and age>3:
   actual=keys();assert set(state['original']).issubset(set(actual));assert len(actual)==144+sum(report['added_by_color'].values())
   sig=signature();(E/'signature_diff.json').write_text(json.dumps({k:[state['sig'].get(k),sig.get(k)] for k in set(sig)|set(state['sig']) if sig.get(k)!=state['sig'].get(k)},indent=2));assert sig==state['sig']
   after=sweep();report['after_corridor']=after;assert after==state['corridor'],'New driving corridor obstruction'
   collision=[]
   for s in state['accepted']:
    col=s['columns'][len(s['columns'])//2];x,y=col['xy'];z=col['z']+27.6
    h=u.SystemLibrary.line_trace_single(W.get_editor_world(),u.Vector(x-80,y,z),u.Vector(x+80,y,z),u.TraceTypeQuery.ECC_VISIBILITY,False,[],u.DrawDebugTrace.NONE,True)
    assert any(isinstance(c,u.StaticMeshComponent) and c.static_mesh and c.static_mesh.get_path_name().startswith(B+'/') for c in parts(h)),s['id']
    collision.append(s['id'])
   report.update(total_instances=len(actual),hism_components=len(tires()),simple_collision_sections_passed=collision,original_144_preserved=True,existing_actors_lighting_unchanged=True)
   for path,digest in before['protected'].items():
    assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
   assert L.save_current_level();report['saved']=True;assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');assert keys()==actual;assert signature()==state['sig'];report['reload_verified']=True
   state['camera']=aerial();nxt('aerial')
  elif phase=='aerial' and age>8:
   state['task']=u.AutomationLibrary.take_high_res_screenshot(2400,2000,str(E/'aerial_after.png'),camera=state['camera'],delay=1);nxt('aerial_wait')
  elif phase=='aerial_wait' and state['task'].is_task_done() and age>2:
   A.destroy_actor(state['camera']);s=next(s for s in state['accepted'] if s['corner']==2);col=s['columns'][len(s['columns'])//2];p=route[s['route_index']];x,y=col['xy'];d=math.hypot(p[0]-x,p[1]-y);pos=u.Vector(x+(p[0]-x)/d*280,y+(p[1]-y)/d*280,col['z']+115);target=u.Vector(x,y,col['z']+27)
   c=A.spawn_actor_from_class(u.CameraActor,pos,u.MathLibrary.find_look_at_rotation(pos,target));c.camera_component.set_field_of_view(60);cameras.append(c);state['camera']=c;nxt('detail')
  elif phase=='detail' and age>6:
   state['task']=u.AutomationLibrary.take_high_res_screenshot(1800,1100,str(E/'curved_barrier_detail.png'),camera=state['camera'],delay=1);nxt('detail_wait')
  elif phase=='detail_wait' and state['task'].is_task_done() and age>2:
   A.destroy_actor(state['camera']);L.editor_request_begin_play();state['view']=0;nxt('play')
  elif phase=='play':
   if age>120:raise RuntimeError('PIE startup timeout')
   pw=W.get_game_world()
   if not pw:return
   pawn=u.GameplayStatics.get_player_pawn(pw,0)
   if not isinstance(pawn,u.ProofPawn) or u.GameplayStatics.get_time_seconds(pw)<10:return
   idx=[210,54][state['view']];p=route[idx];q=route[idx+3];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));z=ground(p[0],p[1],pw)+31
   pawn.set_kart_test_input(0,0,True);pawn.set_actor_location_and_rotation(u.Vector(p[0],p[1],z),u.Rotator(yaw=yaw),False,True);pawn.get_component_by_class(u.KartTireDynamics).reset_motion()
   if pawn.is_third_person_view():pawn.toggle_camera_view()
   u.GameplayStatics.get_player_controller(pw,0).set_view_target_with_blend(pawn,0);report.setdefault('PIE_driver_views',[]).append({'index':idx,'position':[p[0],p[1],z],'yaw':yaw});nxt('eye')
  elif phase=='eye' and age>4:
   name=['driver_hairpin.png','driver_sweeper.png'][state['view']];u.SystemLibrary.execute_console_command(W.get_game_world(),'Shot filename='+str(E/name));nxt('eye_wait')
  elif phase=='eye_wait' and age>3:
   state['view']+=1
   if state['view']<2:nxt('play')
   else:L.editor_request_end_play();nxt('finish')
  elif phase=='finish' and age>2:finish()
 except Exception:
  report['error']=traceback.format_exc();(E/'apply_error.txt').write_text(report['error']);u.log_error(report['error'])
  if L.is_in_play_in_editor():L.editor_request_end_play()
  finish()
 finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)





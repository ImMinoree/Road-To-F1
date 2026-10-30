"""Repeatable five-kart races on the real map. No in-race repositioning or physics changes."""
import unreal as u,time,json,math,traceback,itertools
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/CompetitiveAI/Scale4';L=u.get_editor_subsystem(u.LevelEditorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem)
cmd=u.SystemLibrary.get_command_line();label='baseline' if '-RacecraftBaseline' in cmd else 'after';seconds=60.;orders=1
if '-RacecraftSmoke' in cmd:label='smoke';seconds=60.;orders=1
if '-RacecraftBlockedTest' in cmd:label='blocked';seconds=65.;orders=1
u.EditorPythonScripting.set_keep_python_script_alive(True)
E.mkdir(exist_ok=True)
cdo=u.get_default_object(u.ProofGameMode).get_editor_property('racing_ai');cdo.set_editor_property('opponent_count',4)
for command in ['t.MaxFPS 0','t.IdleWhenNotForeground 0','Slate.bAllowThrottling 0']:u.SystemLibrary.execute_console_command(None,command)
data=u.load_asset('/Game/RoadToF1/RacingAI/DA_DesertTrackEdges');center=[(v.x,v.y) for v in data.get_editor_property('center')];left=[(v.x,v.y) for v in data.get_editor_property('left')];right=[(v.x,v.y) for v in data.get_editor_property('right')];N=len(center);arcs=[0.]
for i,p in enumerate(center):q=center[(i+1)%N];arcs.append(arcs[-1]+math.hypot(q[0]-p[0],q[1]-p[1]))
length=arcs[-1];s={'phase':'load','order':0,'busy':False,'wall':time.monotonic(),'epoch':0};report={'label':label,'race_seconds':seconds,'route_length_cm':length,'runs':[],'stuck_definition':'Speed below 30cm/s with target above 150cm/s, or any continuous stop over 5s; commanded short yields separately counted as stationary time.','metric_definition':'Pairwise order exchanges require +/-250 cm longitudinal clearance and 1s confirmation, counted after 5s. Collision episodes are per-kart starts of non-ground swept contacts, separated by 0.5s. Off-track episodes use projected collider half-extents and 0.3s confirmation. Player uses the existing opt-in AI diagnostic driver.'}
def nearest(x,y,prev):
 best=(1e30,0,0,0)
 for j in (range(N) if prev is None else range(prev-12,prev+22)):
  i=j%N;a=center[i];b=center[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];t=max(0.,min(1.,((x-a[0])*dx+(y-a[1])*dy)/max(1e-6,dx*dx+dy*dy)));qx=a[0]+dx*t;qy=a[1]+dy*t;d=(x-qx)**2+(y-qy)**2
  if d<best[0]:best=(d,i,t,arcs[i]+t*(arcs[i+1]-arcs[i]))
 return best[1:]
def persist(): (E/(label+'.json')).write_text(json.dumps(report,indent=2))
def tick(dt):
 if s['busy']:return
 s['busy']=True
 try:
  if time.monotonic()-s['wall']>900:raise RuntimeError('Racecraft harness wall timeout')
  if s['phase']=='finish':
   if time.monotonic()-s['epoch']>1:
    if s['order']>=orders:persist();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR');return
    s['phase']='load'
   return
  if s['phase']=='load':
   assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
   mode=W.get_editor_world().get_world_settings().get_editor_property('default_game_mode')
   if mode:u.get_default_object(mode).get_editor_property('racing_ai').set_editor_property('opponent_count',4)
   slots=[a for a in A.get_all_level_actors() if isinstance(a,u.GridStartSlot) and a.get_editor_property('position_number')<=4]
   if s['order']==1:
    for a in slots:a.set_editor_property('position_number',5-a.get_editor_property('position_number'))
   L.editor_request_begin_play();s['phase']='race';s['agents']={};s['pairs']={};s['sample']=-1;s['started']=False;s['epoch']=time.monotonic();return
  world=W.get_game_world()
  if not world:return
  gm=u.GameplayStatics.get_game_mode(world);pawns=u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn)
  if not gm or not pawns:return
  report.setdefault('initial_spawn_count',len(pawns))
  if False:
   for p in pawns:
    if p.get_editor_property('racing_ai') and p.get_editor_property('preferred_grid_position')>4:p.destroy_actor()
   report['pre_grid_setup']='Excess default opponents removed before countdown; no in-race repositioning.'
   return
  assert len(pawns)==4,('Expected four racers',len(pawns))
  if not s['started']:
   fields=['mass_kg','engine_force_n','maximum_forward_speed_mph','maximum_steering_degrees','front_cornering_stiffness','rear_cornering_stiffness']
   values=[{k:p.get_component_by_class(u.KartTireDynamics).get_editor_property(k) for k in fields} for p in pawns];assert all(v==values[0] for v in values);report['identical_physics']=values[0];s['started']=True
  if gm.is_start_gate_closed():return
  elapsed=gm.get_race_elapsed_seconds()
  if elapsed-s['sample']<.1:return
  sample_dt=max(0,elapsed-max(0,s['sample']));s['sample']=elapsed
  for p in pawns:
   name=p.get_name();pos=p.get_actor_location();d=s['agents'].setdefault(name,{'segment':None,'distance':0.,'laps':0,'stuck_seconds':0.,'collision_episodes':0,'contact_count':0,'offtrack_events':0,'offtrack_seconds':0.,'offclock':0.,'offactive':False,'last_hit':-100,'max_speed_kmh':0.,'samples':0,'lane_square':0.})
   i,t,arc=nearest(pos.x,pos.y,d['segment']);old=d.get('arc',arc);old_laps=d['laps'];advance=(arc-old+length*.5)%length-length*.5;d['distance']+=advance;d.update(segment=i,arc=arc,laps=max(d['laps'],int(max(0,d['distance'])/length)))
   
   if d['laps']>old_laps:d.setdefault('lap_times',[]).append(elapsed-d.get('last_lap',0));d['last_lap']=elapsed
   speed=p.get_velocity().length();d['max_speed_kmh']=max(d['max_speed_kmh'],speed*.036);d['stationary_clock']=d.get('stationary_clock',0)+sample_dt if speed<30 else 0;d['stationary_seconds']=d.get('stationary_seconds',0)+(sample_dt if elapsed>5 and speed<30 else 0);d['longest_stop_seconds']=max(d.get('longest_stop_seconds',0),d['stationary_clock']);commands={v['id']:v for v in json.loads(gm.get_component_by_class(u.TrackRacingAI).get_racecraft_telemetry())};d['stuck_seconds']+=sample_dt if elapsed>5 and speed<30 and (commands.get(name,{}).get('target_cms',0)>150 or d['stationary_clock']>5) else 0
   tangent=(center[(i+1)%N][0]-center[(i-1)%N][0],center[(i+1)%N][1]-center[(i-1)%N][1]);mag=math.hypot(*tangent);normal=(-tangent[1]/mag,tangent[0]/mag);lat=(pos.x-center[i][0])*normal[0]+(pos.y-center[i][1])*normal[1];d['samples']+=1;d['lane_square']+=lat*lat
   f=p.get_actor_forward_vector();rr=p.get_actor_right_vector();half=90*abs(f.x*normal[0]+f.y*normal[1])+60*abs(rr.x*normal[0]+rr.y*normal[1]);le=(left[i][0]-center[i][0])*normal[0]+(left[i][1]-center[i][1])*normal[1];re=(right[i][0]-center[i][0])*normal[0]+(right[i][1]-center[i][1])*normal[1];off=lat+half>le+5 or lat-half<re-5
   d['offclock']=d['offclock']+sample_dt if off else 0
   if d['offclock']>.3 and not d['offactive']:d['offtrack_events']+=1;d['offactive']=True
   if not off:d['offactive']=False
   if off:d['offtrack_seconds']+=sample_dt
   excess=max(lat+half-le,re-lat+half);d['maximum_body_edge_excess_cm']=max(d.get('maximum_body_edge_excess_cm',0),excess)
   if lat>le+5 or lat<re-5:d['center_offtrack_seconds']=d.get('center_offtrack_seconds',0)+sample_dt
   if off and 'first_body_edge_excursion' not in d:d['first_body_edge_excursion']={'time':elapsed,'segment':i,'excess_cm':excess}
   dynamics=p.get_component_by_class(u.KartTireDynamics);contacts=dynamics.get_editor_property('collision_count')
   if contacts>d['contact_count']:
    d.setdefault('contact_events',[]).append({'time':elapsed,'segment':i,'speed':speed,'impulse_ns':dynamics.get_editor_property('last_contact_impulse_ns')})
    if elapsed-d['last_hit']>.5:d['collision_episodes']+=1
    d['last_hit']=elapsed
   state=commands.get(name,{});a=center[(i-3)%N];b=center[i];c=center[(i+3)%N];ab=(b[0]-a[0],b[1]-a[1]);ac=(c[0]-a[0],c[1]-a[1]);bc=(c[0]-b[0],c[1]-b[1]);curve=2*(ab[0]*ac[1]-ab[1]*ac[0])/max(1,math.hypot(*ab)*math.hypot(*ac)*math.hypot(*bc));d['side_by_side_corner_seconds']=d.get('side_by_side_corner_seconds',0)+(sample_dt if state.get('state')=='SIDE_BY_SIDE' and abs(curve)>.0003 else 0);d['maximum_steering_step']=max(d.get('maximum_steering_step',0),abs(state.get('steering',0)-d.get('last_steering',0)));d['last_steering']=state.get('steering',0);d['braking_seconds']=d.get('braking_seconds',0)+(sample_dt if state.get('brake',0)>.05 else 0)
   d['contact_count']=contacts;d['maximum_impulse_ns']=dynamics.get_editor_property('maximum_contact_impulse_ns')
  if label=='blocked':
   if elapsed>=0 and not s.get('blocker'):
    leader=next(p for p in pawns if p.get_editor_property('racing_ai') and p.get_editor_property('preferred_grid_position')==1);s['blocker']=leader;s['block_position']=leader.get_actor_location();leader.get_component_by_class(u.KartTireDynamics).reset_motion();leader.set_actor_tick_enabled(False);report['blocked_test']={'kart':leader.get_name(),'stop_at':elapsed,'method':'Stalled grid leader held in place from lights-out, without repositioning; restored at 18s. Separate diagnostic, excluded from competition comparison.'}
   if s.get('blocker') and elapsed<18:assert (s['blocker'].get_actor_location()-s['block_position']).length()<1
   elif s.get('blocker') and not s.get('released'):
    s['blocker'].set_actor_tick_enabled(True);s['released']=True;report['blocked_test']['released_at']=elapsed
  for a,b in itertools.combinations(sorted(s['agents']),2):
   da=s['agents'][a];db=s['agents'][b];gap=da['distance']-db['distance'] # corrected below by initial grid arcs
   gap+=(da.setdefault('initial_arc',da['arc'])-db.setdefault('initial_arc',db['arc']))
   sign=1 if gap>250 else -1 if gap<-250 else 0;key=a+'|'+b;v=s['pairs'].setdefault(key,{'sign':sign,'changes':0,'candidate':0,'since':elapsed})
   if sign and sign!=v['sign']:
    if sign!=v['candidate']:v.update(candidate=sign,since=elapsed)
    elif elapsed-v['since']>=1:
     if v['sign'] and elapsed>5:v['changes']+=1
     v.update(sign=sign,candidate=0)
   else:v['candidate']=0
  if elapsed>=seconds:
   row={'grid_order':'normal' if s['order']==0 else 'reversed_AI_grid','elapsed':elapsed,'start_events':gm.start_event_count,'staged':gm.staged_participant_count,'racers':s['agents'],'pairwise_position_changes':sum(v['changes'] for v in s['pairs'].values()),'pairs':s['pairs']}
   ai=gm.get_component_by_class(u.TrackRacingAI)
   if hasattr(ai,'get_racecraft_telemetry'):row['decisions']=json.loads(ai.get_racecraft_telemetry());row['track_plan']=json.loads(ai.get_track_plan_telemetry())
   report['runs'].append(row);persist();L.editor_request_end_play();s['order']+=1;s.update(phase='finish',epoch=time.monotonic())
   if label=='after' and any(v['collision_episodes']>0 or v['offtrack_events']>0 or v['stuck_seconds']>1 for v in s['agents'].values()):report['safety_failure']='Stop before broader testing: contacts, sustained off-track or stuck time';s['order']=orders;persist()
  elif int(elapsed)%20==0:
   progress={'order':s['order'],'seconds':elapsed,'racers':s['agents']}
   ai=gm.get_component_by_class(u.TrackRacingAI)
   if hasattr(ai,'get_racecraft_telemetry'):progress['decisions']=json.loads(ai.get_racecraft_telemetry())
   (E/(label+'_progress.json')).write_text(json.dumps(progress,indent=2))
 except Exception:
  report['error']=traceback.format_exc();u.log_error(report['error']);persist();L.editor_request_end_play();s['order']=orders;s.update(phase='finish',epoch=time.monotonic())
 finally:s['busy']=False
handle=u.register_slate_post_tick_callback(tick)




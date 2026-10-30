"""Real in-editor 20-kart race. Optional existing diagnostic player, no repositioning.
Collects genuine simulated AI pace, launch commands, contacts and corridor excursions.
Leaves the editor/map open and does not save assets.
"""
import unreal as u,json,time,csv,math,traceback
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/TwentyKartLaunch';E.mkdir(exist_ok=True)
u.EditorPythonScripting.set_keep_python_script_alive(True)
L=u.get_editor_subsystem(u.LevelEditorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not W.get_game_world()
if 'DesertKarting_Visual' not in W.get_editor_world().get_path_name():
 assert '-Kart20Batch' in u.SystemLibrary.get_command_line(),'Do not replace a user level'
 assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
cdo=u.get_default_object(u.ProofGameMode).get_editor_property('racing_ai')
assert cdo.get_editor_property('opponent_count')==19,'Native game mode must default to 19 opponents'
mode=W.get_editor_world().get_world_settings().get_editor_property('default_game_mode')
if mode:assert u.get_default_object(mode).get_editor_property('racing_ai').get_editor_property('opponent_count')==19
old_fps=u.SystemLibrary.get_console_variable_float_value('t.MaxFPS')
u.SystemLibrary.execute_console_command(None,'t.MaxFPS 60')
route=u.load_asset('/Game/RoadToF1/RacingAI/DA_DesertTrackEdges')
center=[(v.x,v.y) for v in route.get_editor_property('center')]
left=[(v.x,v.y) for v in route.get_editor_property('left')];right=[(v.x,v.y) for v in route.get_editor_property('right')]
N=len(center);arcs=[0.]
for i,a in enumerate(center):b=center[(i+1)%N];arcs.append(arcs[-1]+math.dist(a,b))
length=arcs[-1]
def nearest(x,y,prev):
 best=(1e30,0,0)
 for j in (range(N) if prev is None else range(prev-12,prev+22)):
  i=j%N;a=center[i];b=center[(i+1)%N];dx=b[0]-a[0];dy=b[1]-a[1];t=max(0.,min(1.,((x-a[0])*dx+(y-a[1])*dy)/max(1e-6,dx*dx+dy*dy)));d=(x-a[0]-dx*t)**2+(y-a[1]-dy*t)**2
  if d<best[0]:best=(d,i,arcs[i]+t*(arcs[i+1]-arcs[i]))
 return best[1:]
def triangle(p,a,b,c):
 cross=lambda a,b,p:(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 q=[cross(a,b,p),cross(b,c,p),cross(c,a,p)];return min(q)>=-1 or max(q)<=1
def inside(p,index):
 for j in range(index-8,index+9):
  i=j%N;k=(i+1)%N
  if triangle(p,left[i],right[i],right[k]) or triangle(p,left[i],right[k],left[k]):return True
 return False
report={'scenario':'19 simulated AI plus existing opt-in reference player driver' if '-RacingAIPlayerTest' in u.SystemLibrary.get_command_line() else '19 simulated AI, stationary human in slot 10', 'timing':'real-time PIE, capped at 60 FPS, unchanged 240 Hz solver','racers':{},'gated_max_displacement_cm':0.,'runs':[]}
s={'sample':-1.,'busy':False,'wall':time.monotonic(),'epoch':0,'phase':'race','run':0}
telemetry=(E/'telemetry.csv').open('w',newline='');writer=csv.writer(telemetry);writer.writerow(['run','seconds','kart','speed_kmh','target_kmh','throttle','brake','state','segment'])
def persist():
 telemetry.flush();(E/'validation.json').write_text(json.dumps(report,indent=2))
def finish():
 persist();u.unregister_slate_post_tick_callback(handle);L.editor_request_end_play();u.SystemLibrary.execute_console_command(None,'t.MaxFPS '+str(old_fps));telemetry.close()
 if '-Kart20Batch' in u.SystemLibrary.get_command_line():u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
def tick(dt):
 if s['busy']:return
 s['busy']=True
 try:
  if time.monotonic()-s['wall']>900:raise RuntimeError('Validation timeout')
  world=W.get_game_world()
  if not world:return
  gm=u.GameplayStatics.get_game_mode(world);pawns=u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn)
  if not gm:return
  assert len(pawns)==20,('Expected 20 karts',len(pawns))
  ai=gm.get_component_by_class(u.TrackRacingAI)
  commands={v['id']:v for v in json.loads(ai.get_racecraft_telemetry())}
  if any(p.get_component_by_class(u.KartMechanicalVisuals).get_editor_property('livery_slot')<=0 for p in pawns):return
  if not report.get('colors'):
   colors={};slots=[];caps={};power=[]
   for p in pawns:
    visual=p.get_component_by_class(u.KartMechanicalVisuals)
    assert visual.get_editor_property('ready')
    c=visual.get_editor_property('kart_color');colors[p.get_name()]=[c.r,c.g,c.b,c.a]
    slots.append(p.get_editor_property('assigned_grid_position'))
    d=p.get_component_by_class(u.KartTireDynamics);caps[p.get_name()]=d.get_editor_property('maximum_forward_speed_mph')*1.609344
    power.append([d.get_editor_property(k) for k in ['mass_kg','engine_force_n','linear_drag_per_second','maximum_steering_degrees']])
   assert len(set(tuple(c) for c in colors.values()))==20,colors
   assert sorted(slots)==list(range(1,21)),slots
   assert all(v==power[0] for v in power),power
   assert all(abs(caps[p.get_name()]-(61.155072 if p.is_player_controlled() else 70))<.02 for p in pawns),caps
   report.update(colors=colors,slots=slots,governors_kmh=caps,shared_power_and_steering=power[0],command_line=u.SystemLibrary.get_command_line())
  elapsed=gm.get_race_elapsed_seconds()
  if gm.is_start_gate_closed():
   for p in pawns:
    key=p.get_name();pos=p.get_actor_location();d=report['racers'].setdefault(key,{});initial=d.setdefault('grid',[pos.x,pos.y,pos.z]);report['gated_max_displacement_cm']=max(report['gated_max_displacement_cm'],math.dist(initial,[pos.x,pos.y,pos.z]))
   if gm.red_light_count==3 and not s.get('grid_capture'):
    s['grid_capture']=True;u.AutomationLibrary.take_high_res_screenshot(1280,720,str(E/'grid_first_person.png'))
   return
  if elapsed-s['sample']<.1:return
  sample_dt=max(0.,elapsed-max(0.,s['sample']));s['sample']=elapsed
  for p in pawns:
   name=p.get_name();d=report['racers'].setdefault(name,{});pos=p.get_actor_location();i,arc=nearest(pos.x,pos.y,d.get('segment'));old=d.get('arc',arc);advance=(arc-old+length*.5)%length-length*.5
   d['distance_cm']=d.get('distance_cm',0.)+advance;d.update(arc=arc,segment=i)
   laps=int(max(0.,d['distance_cm'])/length)
   if laps>d.get('laps',0):d.setdefault('lap_times',[]).append(elapsed-d.get('last_lap',0.));d['last_lap']=elapsed
   d['laps']=max(laps,d.get('laps',0));speed=p.get_velocity().length()*.036;d['peak_kmh']=max(speed,d.get('peak_kmh',0.));control=commands.get(name,{})
   if not p.is_player_controlled() and control:
    if elapsed>=.05 and control.get('target_cms',0)>0:d.setdefault('first_control',{'seconds':elapsed,'throttle':control['throttle'],'brake':control['brake'],'speed_kmh':speed})
    d['seconds_65_70']=d.get('seconds_65_70',0.)+(sample_dt if 65<=speed<=70.05 else 0.)
    d['full_throttle_seconds']=d.get('full_throttle_seconds',0.)+(sample_dt if control['throttle']>=.999 else 0.)
    d['low_speed_seconds']=d.get('low_speed_seconds',0.)+(sample_dt if elapsed>5 and speed<1.08 and control.get('target_cms',0)>150 else 0.)
   dynamics=p.get_component_by_class(u.KartTireDynamics);contacts=dynamics.get_editor_property('collision_count')
   if contacts>d.get('contacts',0) and elapsed-d.get('last_hit',-100)>.5:d['collision_episodes']=d.get('collision_episodes',0)+1;d['last_hit']=elapsed
   d['contacts']=contacts;d['max_impulse_ns']=dynamics.get_editor_property('maximum_contact_impulse_ns');d['dropped_simulation_seconds']=dynamics.get_editor_property('dropped_simulation_seconds')
   f=p.get_actor_forward_vector();r=p.get_actor_right_vector();off=any(not inside((pos.x+f.x*x+r.x*y,pos.y+f.y*x+r.y*y),i) for x in [-90,0,90] for y in [-60,0,60])
   d['offclock']=d.get('offclock',0.)+sample_dt if off else 0.
   if d['offclock']>.3 and not d.get('offactive',False):
    d['offtrack_events']=d.get('offtrack_events',0)+1;d['offactive']=True
    d.setdefault('offtrack_examples',[]).append({'seconds':elapsed,'segment':i,'position':[pos.x,pos.y,pos.z],'speed_kmh':speed,'state':control.get('state')})
   if not off:d['offactive']=False
   writer.writerow([s['run'],elapsed,name,speed,control.get('target_cms',0)*.036,control.get('throttle'),control.get('brake'),control.get('state'),i])
  if elapsed>=150 or s['run']==1 and elapsed>=8:
   report['runs'].append({'run':s['run'],'elapsed':elapsed,'start_events':gm.start_event_count,'staged':gm.staged_participant_count,'racers':report['racers'],'decisions':json.loads(ai.get_racecraft_telemetry()),'plan':json.loads(ai.get_track_plan_telemetry())})
   if s['run']==0:
    persist();s.update(run=1,sample=-1.);report['racers']={};gm.restart_race_start()
   else:report['completed']=True;finish()
  elif int(elapsed)%10==0:persist()
 except Exception:
  report['error']=traceback.format_exc();u.log_error(report['error']);finish()
 finally:s['busy']=False
handle=u.register_slate_post_tick_callback(tick)
L.editor_request_begin_play()

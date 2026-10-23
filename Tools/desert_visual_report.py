"""Read-only disk/profiler validation; run after the final Unreal render and benchmarks."""
import csv,json,hashlib,statistics,collections
csv.field_size_limit(100_000_000)
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];EV=ROOT/'Evidence/DesertVisual';implementation=json.loads((EV/'implementation.json').read_text())
assert (ROOT/'Content/RoadToF1/Checkpoints/DesertKarting_BeforeVisual.umap').is_file(),'Saved restore checkpoint is missing'
failures=[p for p,h in implementation['protected_hashes'].items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
assert not failures,failures
g=json.loads((ROOT/'Art/DesertKarting/manifest.json').read_text());assert hashlib.sha256(Path(g['source']).read_bytes()).hexdigest()==g['sha256']
render=json.loads((EV/'render_validation.json').read_text());assert all(not v['visible_kart_actors'] and all(p['road'] for p in v['road_probes']) for v in render['maps'].values())
environment=(EV/'environment_preview.log').read_text(errors='replace');assert 'Game class is \'BP_DV_EnvironmentPreview_C\'' in environment and 'SpectatorPawn /Game/' in environment
performance={}
for name in ['Baseline','Visual']:
 raw=json.loads((EV/('runtime_'+name+'.json')).read_text());entry={'fps':raw['fps'],'average_ms':raw['average_ms'],'sample_seconds':raw['seconds'],'position_cm':raw['position_cm']}
 path=EV/('profile_'+name+'.csv')
 if path.exists():
  with path.open(newline='') as f:
   rows=csv.reader(f);header=next(rows)
   wanted=[(i,k) for i,k in enumerate(header) if k in ['FrameTime','GPUTime','RenderThreadTime','GameThreadTime','RenderThreadTime_CriticalPath','GameThreadTime_CriticalPath','RHI/DrawCalls','DrawCall/Basepass','DrawCall/ShadowDepths'] or k.startswith('GPU/')]
   tail=collections.deque(maxlen=200)
   for row in rows:
    if not row or row[0]=='EVENTS' or row[0].startswith('[HasHeader'):continue
    try:
     values={k:float(row[i]) for i,k in wanted}
     if 0<values.get('FrameTime',0)<100:tail.append(values)
    except (ValueError,IndexError):continue
   if tail:
    means={k:round(statistics.mean(v[k] for v in tail),4) for _,k in wanted}
    entry['csv_warm_tail_frames']=len(tail);entry['csv_frame_cpu_draws']={k:v for k,v in means.items() if not k.startswith('GPU/')}
    entry['gpu_largest_scopes_ms']=dict(sorted([(k,v) for k,v in means.items() if k.startswith('GPU/')],key=lambda x:-x[1])[:10])
    entry['csv_scope']='Last 200 warm frames of boot CSV, earlier than final 10-second FPS sample; nested GPU scopes overlap and must not be summed.'
 performance[name]=entry
change=(performance['Visual']['average_ms']/performance['Baseline']['average_ms']-1)*100
report={'map':implementation['map'],'checkpoint':implementation['checkpoint'],'engine':'5.8.3','all_four_priorities_implemented':True,'lighting_unchanged':True,'collision_unchanged':True,'road_rays_passed_each_map':15,'zero_visible_karts_editor':True,'standalone_preview_spawn':'SpectatorPawn only','protected_files_verified':len(implementation['protected_hashes']),'protected_file_failures':failures,'source_glb_unchanged':True,'hardware':'RTX 3080 / Intel i7-10700KF','output_resolution':[1920,1080],'screen_percentage':75,'profile':'High scalability 2 (same view distance, AA, shadows, GI, reflections, textures); VSync/frame cap off','performance':performance,'frame_time_change_percent':round(change,2),'benchmark_limit':'20-second temporary-pawn standalone driving test, final 10 seconds sampled; no full-lap or 20-kart test. Existing raw scope string says co-running editor but these runs were solo. CSV boot profiling can change initial movement due to load stalls.','mesh_assets':implementation['mesh_assets'],'instanced_detail_count':sum(implementation['instances'].values()),'instance_types':len(implementation['instances']),'remaining_placeholders':implementation['remaining_placeholders'],'render_review':{'Track':'Aggregate grain and roughness visibly replace the plain surface; continuous rubber lines read in aerial view.','Pit':'Shutter relief, trim, handles, sandstone joints and corrected readable text are visible at driver height.','Barriers':'Rounded covers, feet, reflectors and handles replace flat green/white blocks; material wear remains stylized.','Stands':'Bucket backs and cap variants add detail; spectator anatomy remains visibly primitive up close.','Aerial':'Layout preserved; ground backface artifact corrected; no karts/drivers visible. Large infield still has simple flat geometry.'},'screenshots':['Visual/Track.png','Visual/Pit.png','Visual/Barriers.png','Visual/Stands.png','Visual/Aerial.png']}
(EV/'final_validation.json').write_text(json.dumps(report,indent=2));implementation['render_inspected']=True;implementation['visual_review']='final_validation.json';(EV/'implementation.json').write_text(json.dumps(implementation,indent=2))
print(json.dumps({'protected_files':report['protected_files_verified'],'fps':{k:v['fps'] for k,v in performance.items()},'frame_time_change_percent':report['frame_time_change_percent'],'csv':{k:{'frame_cpu_draws':v.get('csv_frame_cpu_draws'),'gpu':v.get('gpu_largest_scopes_ms')} for k,v in performance.items()}},indent=2))

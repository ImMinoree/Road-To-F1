"""Summarize actual 20-kart PIE evidence; never infers a clean race from spawn count."""
import csv,json,statistics,difflib,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];E=R/'Evidence/TwentyKartLaunch'
p=json.loads((E/'validation.json').read_text());assert p.get('completed') and not p.get('error'),p.get('error')
rows=list(csv.DictReader((E/'telemetry.csv').open()))
summary={'scenario':p['scenario'],'launch_sample_definition':'First sampled positive target at least 0.05s after lights-out; ignores stale gate telemetry before the first 20 Hz control update. Sampling cadence approximately 0.1s.','grid_count':len(p['slots']),'unique_colors':len(set(tuple(c) for c in p['colors'].values())),'gated_max_displacement_cm':p['gated_max_displacement_cm'],'runs':[]}
for run in p['runs']:
 ai={k:v for k,v in run['racers'].items() if k!='ProofPawn_0'}
 samples=[v for v in rows if int(v['run'])==run['run'] and v['kart'] in ai]
 first={}
 for row in samples:
  if float(row['seconds'])>=.05 and float(row['target_kmh'])>0:first.setdefault(row['kart'],row)
 lap_times=[v['lap_times'][0] for v in ai.values() if v.get('lap_times')]
 result={'run':run['run'],'seconds':run['elapsed'],'staged':run['staged'],'lights_out_events':run['start_events'],'ai_with_lap_completed':len(lap_times),'full_throttle_first_decisions':sum(float(v['throttle'])==1 and float(v['brake'])==0 for v in first.values()),'first_decision_samples':len(first),'peak_kmh':max(v.get('peak_kmh',0) for v in ai.values()),'seconds_65_70_percent':100*sum(v.get('seconds_65_70',0) for v in ai.values())/(19*run['elapsed']),'full_throttle_percent':100*sum(v.get('full_throttle_seconds',0) for v in ai.values())/(19*run['elapsed']),'contact_count':sum(v.get('contacts',0) for v in ai.values()),'offtrack_events':sum(v.get('offtrack_events',0) for v in ai.values()),'low_speed_seconds':sum(v.get('low_speed_seconds',0) for v in ai.values()),'max_dropped_simulation_seconds':max(v.get('dropped_simulation_seconds',0) for v in ai.values()),'ai_cpu_mean_ms':run['plan']['ai_cpu_mean_ms'],'ai_cpu_max_ms':run['plan']['ai_cpu_max_ms']}
 if lap_times:result.update(first_lap_min=min(lap_times),first_lap_max=max(lap_times),first_lap_mean=statistics.mean(lap_times))
 summary['runs'].append(result)
protected=json.loads((E/'protected_before_validation.json').read_text(encoding='utf-8-sig'))
summary['protected_files_unchanged']=all(hashlib.sha256(Path(v['Path']).read_bytes()).hexdigest().lower()==v['Hash'].lower() for v in protected)
patch=''
for old in sorted((E/'Checkpoint').glob('*')):
 if old.suffix not in ('.h','.cpp'):continue
 current=next((R/'Source/Road_To_F1_New').rglob(old.name))
 patch+=''.join(difflib.unified_diff(old.read_text().splitlines(True),current.read_text().splitlines(True),fromfile='before/'+old.name,tofile=str(current.relative_to(R))))
(E/'task_changes.patch').write_text(patch)
(E/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

import json,statistics,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];E=R/'Evidence/AI70';out={}
for label in ['Baseline','After','TenKart']:
 p=E/label/('baseline.json' if label=='Baseline' else 'after.json')
 if not p.exists():continue
 d=json.loads(p.read_text());runs=[];laps=[];first=[]
 for r in d['runs']:
  ai=[v for k,v in r['racers'].items() if k!='ProofPawn_0'];times=[v['lap_times'][0] for v in ai if v.get('lap_times')];first+=times;laps += [t for v in ai for t in v.get('lap_times',[])]
  runs.append({'order':r['grid_order'],'ai_first_laps':times,'player_first_lap':r['racers']['ProofPawn_0'].get('lap_times',[None])[0],'fastest_first_lap_kart':min(((v.get('lap_times') or [float('inf')])[0],k) for k,v in r['racers'].items())[1],'contacts':sum(v['collision_episodes'] for v in r['racers'].values()),'offtrack':sum(v['offtrack_events'] for v in r['racers'].values()),'stuck_seconds':sum(v['stuck_seconds'] for v in r['racers'].values()),'completed_ai_laps':sum(v['laps'] for v in ai),'ai_max_kmh':max(v['max_speed_kmh'] for v in ai),'player_max_kmh':r['racers']['ProofPawn_0']['max_speed_kmh'],'position_changes':r['pairwise_position_changes'],'start_events':r['start_events'],'participants':r['staged'],'cpu':r['track_plan']})
 out[label]={'runs':runs,'first_lap_median':statistics.median(first) if first else None,'all_lap_median':statistics.median(laps) if laps else None,'error':d.get('error'),'safety_failure':d.get('safety_failure'),'governors_kmh':d.get('governors_kmh')}
protected=json.loads((E/'Checkpoint/protected.json').read_text());out['protected_changes']=[n for n,h in protected.items() if hashlib.sha256((R/n).read_bytes()).hexdigest()!=h]
(E/'summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

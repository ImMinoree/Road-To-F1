"""Summarize observed Unreal results; does not mark failed scale tests as passed."""
from pathlib import Path
import json,statistics,hashlib
R=Path(__file__).resolve().parents[1];E=R/'Evidence/CompetitiveAI'
cases=['Baseline','FinalPack','FinalPassing','FinalDefense','Systems','Scale4','Scale20','Restart','KnownLowGrip','Rendered'];summary={}
for case in cases:
 p=E/case/('baseline.json' if case=='Baseline' else 'after.json')
 if not p.exists():continue
 d=json.loads(p.read_text(encoding='utf-8-sig'));runs=[]
 for row in d.get('runs',[]):
  racers=row['racers'];lap_times=[t for name,v in racers.items() if name!='ProofPawn_0' for t in v.get('lap_times',[])];runs.append({'seconds':row['elapsed'],'participants':len(racers),'staged':row['staged'],'start_events':row['start_events'],'total_laps':sum(v['laps'] for v in racers.values()),'ai_laps':sum(v['laps'] for name,v in racers.items() if name!='ProofPawn_0'),'position_exchanges':row['pairwise_position_changes'],'ai_position_exchanges':sum(v['changes'] for key,v in row['pairs'].items() if 'ProofPawn_0' not in key),'defensive_holds':sum(v['defensive_holds'] for v in row.get('decisions',[])),'aborted_maneuvers':sum(v['aborted'] for v in row.get('decisions',[])),'collision_episodes':sum(v['collision_episodes'] for v in racers.values()),'offtrack_episodes':sum(v['offtrack_events'] for v in racers.values()),'stuck_seconds':sum(v['stuck_seconds'] for v in racers.values()),'longest_stop_seconds':max(v.get('longest_stop_seconds',0) for v in racers.values()),'side_by_side_corner_kart_seconds':sum(v.get('side_by_side_corner_seconds',0) for v in racers.values()),'lap_time_range_seconds':[min(lap_times),max(lap_times)] if lap_times else None,'lap_time_median_seconds':statistics.median(lap_times) if lap_times else None,'planning':row.get('track_plan')})
 summary[case]={'error':d.get('error'),'safety_failure':d.get('safety_failure'),'runs':runs,'surface_test':d.get('surface_test'),'restart':d.get('before_restart') is not None}
summary['source_hashes']={name:hashlib.sha256((R/'Source/Road_To_F1_New'/name).read_bytes()).hexdigest() for name in ['TrackRacingAI.cpp','TrackRacingAI.h','KartRacecraft.cpp','KartAITrackPlan.cpp','KartAIPerception.cpp','KartAIDifficulty.cpp','KartAIDebug.cpp']}
(E/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:v['runs'] for k,v in summary.items() if k!='source_hashes'},indent=2))

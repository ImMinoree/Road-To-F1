from pathlib import Path
import json,csv,math,statistics,itertools
E=Path('Evidence/GameplayCompetition');route=json.loads(Path('Art/RacingAI/track_edges.json').read_text());C=route['center'];N=len(C);arcs=[0.]
for i in range(N):arcs.append(arcs[-1]+math.dist(C[i],C[(i+1)%N]))
curvature=[]
for i in range(N):
 a=C[(i-3)%N];b=C[i];c=C[(i+3)%N];ab=(b[0]-a[0],b[1]-a[1]);ac=(c[0]-a[0],c[1]-a[1]);bc=(c[0]-b[0],c[1]-b[1]);curvature.append(abs(2*(ab[0]*ac[1]-ab[1]*ac[0])/max(1,math.hypot(*ab)*math.hypot(*ac)*math.hypot(*bc))))
summary={}
for case,file in [('Baseline','baseline.json'),('After','after.json')]:
 p=E/case/file
 if not p.exists():continue
 d=json.loads(p.read_text());runs=d.get('runs',[]);ai_ids={x['id'] for r in runs for x in r['decisions'] if x['slot']>0};player_ids={x['id'] for r in runs for x in r['decisions'] if x['slot']==0};laps=[t for r in runs for k,v in r['racers'].items() if k in ai_ids for t in v.get('lap_times',[])];flying=[t for r in runs for k,v in r['racers'].items() if k in ai_ids for t in v.get('lap_times',[])[1:]];rows=list(csv.DictReader((E/case/'telemetry.csv').open()));speed=[];corners=[];brakes=[];near=alone=0;last={};initial_ahead={}
 for (order,t),group in itertools.groupby(rows,key=lambda r:(r['order'],r['seconds'])):
  group=list(group);time=float(t)
  if time<5:continue
  dt=min(.2,time-last.get(order,time));last[order]=time
  p=next((r for r in group if r['kart'] in player_ids),None)
  if p:
   pa=arcs[int(p['segment'])]
   if order not in initial_ahead:initial_ahead[order]=all((arcs[int(r['segment'])]-pa+arcs[-1]/2)%arcs[-1]-arcs[-1]/2>250 for r in group if r['kart'] in ai_ids)
   gaps=[abs((arcs[int(r['segment'])]-pa+arcs[-1]/2)%arcs[-1]-arcs[-1]/2) for r in group if r['kart'] in ai_ids]
   if gaps and min(gaps)<=2000:near+=dt
   else:alone+=dt
  for r in group:
   if r['kart'] not in ai_ids:continue
   v=float(r['speed_cms'])*.036;speed.append(v);brakes.append(float(r['brake'])>.05)
   if curvature[int(r['segment'])]>.001:corners.append(v)
 summary[case]={'runs':len(runs),'actual_planning_budgets':[r['track_plan']['lateral_budget_cms2'] for r in runs],'reference_player_budgets':[r['track_plan'].get('reference_player_corner_budget') for r in runs],'ai_laps':len(laps),'ai_lap_median':statistics.median(laps) if laps else None,'ai_lap_range':[min(laps),max(laps)] if laps else [],'ai_flying_median':statistics.median(flying) if flying else None,'player_lap_samples':[t for r in runs for k,v in r['racers'].items() if k in player_ids for t in v.get('lap_times',[])],'ai_exchanges':sum(v['changes'] for r in runs for key,v in r['pairs'].items() if all(p not in key for p in player_ids)),'all_exchanges':sum(r['pairwise_position_changes'] for r in runs),'defensive_holds':sum(v['defensive_holds'] for r in runs for v in r['decisions'] if v['slot']>0),'committed_passes':sum(v['completed'] for r in runs for v in r['decisions'] if v['slot']>0),'abort_events':sum(v['aborted'] for r in runs for v in r['decisions'] if v['slot']>0),'contacts':sum(v['collision_episodes'] for r in runs for v in r['racers'].values()),'offtrack':sum(v['offtrack_events'] for r in runs for v in r['racers'].values()),'stuck_seconds':sum(v['stuck_seconds'] for r in runs for v in r['racers'].values()),'mean_speed_kmh':statistics.mean(speed) if speed else None,'tight_corner_mean_kmh':statistics.mean(corners) if corners else None,'braking_fraction':statistics.mean(brakes) if brakes else None,'player_nearby_20m_seconds':near,'player_alone_seconds':alone,'nearby_fraction':near/(near+alone) if near+alone else None,'ai_retakes_after_player_pass':sum(v['changes']//2 for r in runs for key,v in r['pairs'].items() if any(p in key for p in player_ids)) if all(initial_ahead.values()) else None,'initial_player_behind_all_opponents_verified':all(initial_ahead.values()),'completion_rate':sum(1 for r in runs for k,v in r['racers'].items() if k in ai_ids and v['laps']>=2)/max(1,len(runs)*4),'error':d.get('error'),'safety_failure':d.get('safety_failure')}
(E/'comparison.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

import json,re,sys,statistics
from pathlib import Path
root=Path(__file__).parent
out=['# Automated pace comparison','', 'Units: speeds in mph; times in simulated seconds. Moving means speed >1 mph; reason durations use the dominant instantaneous limit, so overlapping limits are not double-counted. Headless fixtures are not human telemetry.','']
for name in sys.argv[1:]:
 p=root/name/'index.json'
 if not p.exists(): continue
 r=json.loads(p.read_text(encoding='utf-8-sig'));msgs=[e['event']['message'] for t in r['tests'] for e in t.get('entries',[])]
 rows=[]
 for m in msgs:
  if m.startswith('PACE racer'):
   n=int(re.search(r'racer(\d+)',m)[1]);d={k:float(v) for k,v in re.findall(r'(\w+)=([\d.-]+)',m)};rows.append((n,d))
 out+=['## '+name,'',f"Suites: {r['succeeded']} passed, {r['failed']} failed.",'','| NPC | Peak | Moving avg | <20 % | <25 % | >30 % | Traffic s | Corner s | Obstruction s | Guidance s | Recovery s | Brake events | Brake s | Longest queue s |','|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
 keys=['peak_mph','moving_avg_mph','under20_pct','under25_pct','over30_pct','traffic_s','corner_s','obstruction_s','guidance_s','recovery_s','brake_events','brake_s','longest_queue_s']
 for n,d in rows: out+=['| '+str(n)+' | '+' | '.join(str(d.get(k,0)) for k in keys)+' |']
 if rows:out+=['| Field mean | '+' | '.join(f'{statistics.mean(d.get(k,0) for _,d in rows):.2f}' for k in keys)+' |']
 contacts=[int(re.search(r'contacts (\d+)',m)[1]) for m in msgs if m.startswith('AI:')]
 finishes=[float(re.search(r'finish([\d.]+)s',m)[1]) for m in msgs if m.startswith('Racer')]
 if finishes:out+=['',f'Field: mean finish {statistics.mean(finishes):.2f}s; last finisher {max(finishes):.2f}s; summed per-kart contacts {sum(contacts)} (not unique collision pairs).']
 if rows:out+=['', '| NPC | Tracked pass attempts | Tracked completions |','|---|---|---|']+[f"| {n} | {int(d['pass_attempts']) if 'pass_attempts' in d else 'not instrumented'} | {int(d['completed_passes']) if 'completed_passes' in d else 'not instrumented'} |" for n,d in rows]
 out+=['','### Scenario measurements and finish/contact diagnostics','','```']
 out += [m for m in msgs if m.startswith(('CLEAR','EXIT','TRAIN','PASS ','Racer','AI:','MISSED','20-kart','RELEASE'))]
 out+=['```','']
(root/'METRICS.md').write_text('\n'.join(out),encoding='utf-8')

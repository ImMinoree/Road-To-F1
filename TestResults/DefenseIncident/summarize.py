"""Summarize actual Unreal automation exports; no training or inferred human performance."""
import json,re,statistics,sys
from pathlib import Path
root=Path(__file__).parent
out=['# Battle regression metrics','','Contacts are summed per-kart counters, not unique incidents. Moving speed means >1 mph. Automated fixtures are not a human competitive benchmark.','']
for name in sys.argv[1:]:
 d=json.loads((root/name/'index.json').read_text(encoding='utf-8-sig'))
 msgs=[e['event']['message'] for t in d['tests'] for e in t.get('entries',[])]
 pace={};battle={};finish={};contacts=[];contain=[]
 for m in msgs:
  if m.startswith('CONTAIN racer'):contain.append({k:float(v) for k,v in re.findall(r'(\w+)=([\d.-]+)',m)})
  if m.startswith(('PACE racer','BATTLE racer')):
   n=int(re.search(r'racer(\d+)',m)[1]);(pace if m.startswith('PACE') else battle)[n]={k:float(v) for k,v in re.findall(r'(\w+)=([\d.-]+)',m)}
  if m.startswith('Racer'):finish[int(re.search(r'Racer(\d+)',m)[1])]=float(re.search(r'finish([\d.]+)s',m)[1])
  if m.startswith('AI:'):contacts.append(int(re.search(r'contacts (\d+)',m)[1]))
 out += [f'## {name}','',f"Suites: {d['succeeded']} passed / {d['failed']} failed.",'']
 if finish:
  attempts=sum(p.get('pass_attempts',0) for p in pace.values());completed=sum(p.get('completed_passes',0) for p in pace.values())
  out += [f'Mean finish {statistics.mean(finish.values()):.2f}s; last {max(finish.values()):.2f}s; contacts {sum(contacts)}.',f'Mean moving speed {statistics.mean(p["moving_avg_mph"] for p in pace.values()):.2f} mph; mean time above 30 mph {statistics.mean(p["over30_pct"] for p in pace.values()):.2f}%.',f'Pass attempts {int(attempts)}; completions {int(completed)}; ratio {completed/max(1,attempts):.3f}.',f'Defenses {int(sum(b.get("defenses",0) for b in battle.values()))}; repass attempts/completions {int(sum(b.get("repass_attempts",0) for b in battle.values()))}/{int(sum(b.get("repass_completed",0) for b in battle.values()))}. Player is parked during full-field test, so player repass counts should be zero.','', '| NPC | Finish s | Avg mph | Peak mph | >30 % | Traffic s | Brakes | Contacts | Pass attempts/completions | Defense | Alongside s | Loss | Repass attempts/completions |','|---|---|---|---|---|---|---|---|---|---|---|---|---|']
  for n,p in pace.items():
   b=battle.get(n,{})
   out += [f'| {n} | {finish.get(n,0)} | {p["moving_avg_mph"]} | {p["peak_mph"]} | {p["over30_pct"]} | {p["traffic_s"]} | {p["brake_events"]} | {contacts[n-1]} | {int(p.get("pass_attempts",0))}/{int(p.get("completed_passes",0))} | {int(b.get("defenses",0))} | {b.get("alongside_s",0)} | {int(b.get("losses",0))} | {int(b.get("repass_attempts",0))}/{int(b.get("repass_completed",0))} |']
 if contain:
  totals={k:sum(c.get(k,0) for c in contain) for k in contain[0]}
  out += ['', 'Defense outcomes / containment: '+', '.join(f'{k}={v:.2f}' for k,v in totals.items() if k!='longest_queue')+'.', f"Mean cleared episode {totals['incident_clear_sum']/max(1,totals['clears']):.2f}s; mean completed recovery {totals['recovery_sum']/max(1,totals['recoveries']):.2f}s. Unresolved episodes/recoveries are excluded from these means. Incident count means per-NPC low-speed obstruction episodes, not unique crashes."]
 else:out += ['', 'Detailed defense/incident diagnostics were not present in this baseline; unavailable, not zero.']
 if battle:out += ['', 'Abort totals: '+', '.join(f'{key}={int(sum(b.get(key,0) for b in battle.values()))}' for key in ['occupied','corner','guidance','speed_loss','timeout','contact_risk','rival_unavailable'])+'.', 'Corner/guidance/speed-loss outcomes remain zero when there is no explicit cancellation for that reason; speed limits are recorded separately.']
 out += ['', '### Captured scenarios and outcomes','','```']+[m for m in msgs if m.startswith(('CONTAIN','DEFENSE_CAP','INCIDENT ','INCIDENT_NPC','BATTLE','SIDE','REPASS','PASS ','20-kart','CLEAR','EXIT','TRAIN','RELEASE'))]+['```','']
 for t in d['tests']:
  if t['state']!='Success':out += [t['testDisplayName']+': '+t['state']]+[e['event']['message'] for e in t.get('entries',[]) if e['event']['type']=='Error']
(root/'METRICS.md').write_text('\n'.join(out),encoding='utf-8')

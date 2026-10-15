"""Evaluation-only heuristic labels for battle v1/v2 sidecars; never trains NPCs."""
import csv,json,sys,collections
from pathlib import Path
p=Path(sys.argv[1]);rows=list(csv.DictReader(p.open(encoding='utf-8-sig')))
if not rows or any(r.get('schema') not in {'1','2'} for r in rows):raise SystemExit('Expected battle schema 1 or 2')
frames={}
for r in rows:frames.setdefault(float(r['time']),[]).append(r)
milestones={};events=[];history=collections.deque();previous=None;labels=collections.Counter();defenses=0;prior_defends={};consumed_crossings={}
for t,group in sorted(frames.items()):
 place=int(group[0]['player_position']);contacts=int(group[0]['player_contacts'])
 for rank in [20,15,10,5,1]:
  if place<=rank:milestones.setdefault(str(rank),t)
 while history and history[0][0]<t-2:history.popleft()
 for r in group:
  n=int(r['npc']);d=int(r['defends']);delta=max(0,d-prior_defends.get(n,0));prior_defends[n]=d
  if int(r.get('rival',0))==20:defenses+=delta
 if previous and place<previous[1]:
  count=previous[1]-place;old={int(r['npc']):r for _,g in history for r in g if float(r['ahead_cm'])<0}
  candidates=[r for r in group if consumed_crossings.get(int(r['npc']),-1)<max((ht for ht,hg in history if any(int(hr['npc'])==int(r['npc']) and float(hr['ahead_cm'])<0 for hr in hg)),default=-1) and int(r['npc']) in old and 0<float(r['ahead_cm'])<1500 and float(r['distance_cm'])<1500]
  candidates.sort(key=lambda r:abs(float(r['ahead_cm'])))
  categories=[]
  recent_contact=any(contacts>int(g[0]['player_contacts']) for _,g in history)
  for r in candidates[:count]:
   earlier=old[int(r['npc'])];consumed_crossings[int(r['npc'])]=t
   if recent_contact:label='CONTACT_GAIN'
   elif int(r['contacts'])>int(earlier['contacts']) or int(r.get('burning',0)) or int(earlier.get('burning',0)):label='INCIDENT_GAIN'
   elif int(earlier.get('defend',0))==1 or any(int(r.get(k,0))>int(earlier.get(k,0)) for k in ['defense_late','defense_alongside','defense_occupied','defense_lost_speed','defense_contact_risk']):label='DEFENSE_FAILED'
   elif min(float(r['speed_kmh']),float(earlier['speed_kmh']))<20:label='AI_STOPPED_OR_SLOWED'
   else:label='CLEAN_OVERTAKE'
   categories.append({'npc':int(r['npc']),'label':label,'confidence':'heuristic','speed_kmh':float(r['speed_kmh'])})
  categories += [{'npc':None,'label':'UNKNOWN','confidence':'insufficient matched crossing'} for _ in range(count-len(categories))]
  labels.update(c['label'] for c in categories)
  events.append({'time_s':t,'from':previous[1],'to':place,'gains':categories})
 history.append((t,group));previous=(t,place,contacts)
last={int(r['npc']):r for r in rows}
summary={'schema':2,'source':str(p),'first_reached_position_s':milestones,'labels':dict(labels),'defenses_against_player':defenses,
 'repass_attempts':sum(int(r['repass_attempts']) for r in last.values()),'repass_completions':sum(int(r['repass_completed']) for r in last.values()),
 'defense_outcomes':{k:sum(int(r.get(k,0)) for r in last.values()) for k in ['defense_held','defense_late','defense_alongside','defense_occupied','defense_cleared','defense_lost_speed','defense_wide','defense_contact_risk']},
 'position_gain_events':events,'limitations':'Diagnostic classification, not causal proof. Contact context uses a 2-second window and cannot identify the collision partner. Low-speed obstruction flags alone are not proof of an incident. Defense holds are controller outcomes, not proof the player was delayed. Unknown gains remain unknown. Time is relative to F9, not video/race start. Defense outcomes include all rivals; activation count against player uses rival number 20. No training performed.'}
print(json.dumps(summary,indent=2))

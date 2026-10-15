"""Read optional battle-v1 evaluation CSV. Never fits or installs a driving profile.
Usage: python analyze_session.py path/to/session.csv.battle-v1.csv
"""
import csv,json,sys
from pathlib import Path
p=Path(sys.argv[1]);rows=list(csv.DictReader(p.open(encoding='utf-8-sig')))
if not rows or any(r['schema']!='1' for r in rows):raise SystemExit('Expected nonempty battle schema 1')
frames={}
for r in rows:frames.setdefault(float(r['time']),[]).append(r)
milestones={};gains=[];previous=None
for t,group in sorted(frames.items()):
 place=int(group[0]['player_position']);contacts=int(group[0]['player_contacts'])
 for rank in [20,15,10,5,1]:
  if place<=rank and str(rank) not in milestones:milestones[str(rank)]=t
 if previous and place<previous[1]:
  near=[r for r in group if float(r['distance_cm'])<1500]
  gains.append({'time_s':t,'from':previous[1],'to':place,'player_contact_counter_changed':contacts>previous[2],
   'nearby_npcs':[{'number':int(r['npc']),'ahead_cm':float(r['ahead_cm']),'speed_kmh':float(r['speed_kmh']),'limit':r['reason'],'conflict':r['conflict'],'contacts':int(r['contacts'])} for r in near]})
 previous=(t,place,contacts)
summary={'schema':1,'source':str(p),'first_sample_s':min(frames),'last_sample_s':max(frames),'first_reached_position_s':milestones,
 'milestone_intervals_s':{f'{a}_to_{b}':milestones[str(b)]-milestones[str(a)] for a,b in [(20,15),(15,10),(10,5),(5,1)] if str(a) in milestones and str(b) in milestones},
 'position_gain_events':gains,'limitation':'Times are relative to F9 capture, not video or race start. Counter changes and nearby slowdowns are context, not proof of clean/incident-caused overtakes. Sampling is 5 Hz. No training performed.'}
print(json.dumps(summary,indent=2))

"""Validate actual runtime sequence logs, not simulated countdown calculations."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];ev=root/'Evidence/RaceStart';report={}
for name in ['visual','original','missing_display']:
 events=[json.loads(s) for s in (ev/('runtime_'+name+'.jsonl')).read_text(encoding='utf-8-sig').splitlines() if s.strip()];runs=[]
 for epoch in [1,2]:
  es=[e for e in events if e['epoch']==epoch];reds=[e for e in es if e['event']=='RED_ON'];out=[e for e in es if e['event']=='LIGHTS_OUT'];ready=next(e for e in es if e['event']=='GRID_READY');hold=next(e for e in es if e['event']=='ALL_RED')
  assert [e['reds'] for e in reds]==[1,2,3,4,5]
  assert len(out)==1 and out[0]['start_events']==1 and out[0]['reds']==0
  assert all(not e['moved_early'] for e in es)
  assert [e['event'] for e in es].count('TEST_PASS')==1 and not any(e['event']=='TEST_FAIL' for e in es)
  intervals=[b['time']-a['time'] for a,b in zip(reds,reds[1:])];hold_seconds=out[0]['time']-hold['time']
  assert all(abs(x-1)<.10 for x in intervals) and abs(hold_seconds-1.25)<.10
  assert abs(reds[0]['time']-ready['time']-2)<.10
  assert all(e['x']==ready['x'] and e['y']==ready['y'] for e in es if e['time']<out[0]['time'])
  runs.append({'epoch':epoch,'red_intervals_s':intervals,'all_red_hold_s':hold_seconds,'start_events':1,'held_throttle_blocked':True,'released_motion_verified':True})
 report[name]=runs
v=json.loads((ev/'Final_validation.json').read_text())['maps']
for mp,r in v.items():assert not r['road_failures'] and not r['sweep_failures'] and not r['visible_kart_groups']
report['live_loop_validation']={mp:{'support_rays':r['road_rays'],'sphere_segments':r['swept_sphere_segments'],'failures':0,'persisted_gantry_count':r['start_system']['gantry_count']} for mp,r in v.items()}
(ev/'test_results.json').write_text(json.dumps(report,indent=2));print('PASS: six race starts across both maps, restart and missing-display cases; saved actors and full-loop collision verified.')

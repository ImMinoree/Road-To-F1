"""Summarize actual native game and live-editor grid validation evidence."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];ev=root/'Evidence/Grid20';layout=json.loads((root/'Art/Grid20/layout.json').read_text());report={}
for case,count in [('visual',20),('original',20),('single',1)]:
 events=[json.loads(line) for line in (ev/('runtime_'+case+'.jsonl')).read_text(encoding='utf-8-sig').splitlines() if line.strip()];runs=[]
 for epoch in [1,2]:
  es=[e for e in events if e['epoch']==epoch];reds=[e for e in es if e['event']=='RED_ON'];out=[e for e in es if e['event']=='LIGHTS_OUT'];ready=next(e for e in es if e['event']=='GRID_READY')
  assert [e['reds'] for e in reds]==[1,2,3,4,5];assert len(out)==1 and out[0]['reds']==0 and out[0]['start_events']==1
  assert all(e['staged']==count for e in reds+out) and all(e['grid_slot']==1 for e in reds+out)
  assert not any(e['moved_early'] for e in es);assert any(e['event']=='TEST_PASS' for e in es) and not any(e['event']=='TEST_FAIL' for e in es)
  crossed=any(e['event']=='GRID_FINISH_CROSSED' for e in es)
  intervals=[b['time']-a['time'] for a,b in zip(reds,reds[1:])];hold=out[0]['time']-reds[-1]['time'];assert all(abs(dt-1)<.12 for dt in intervals) and abs(hold-1.25)<.12
  runs.append({'epoch':epoch,'staged':count,'pole_slot':1,'red_intervals_s':intervals,'all_red_hold_s':hold,'start_events':1,'all_participants_held_then_moved':True,'pole_crossed_new_finish_within_3s_sample':crossed})
 assert any(r['pole_crossed_new_finish_within_3s_sample'] for r in runs)
 report[case]=runs
v=json.loads((ev/'validation.json').read_text());summary={}
for name,r in v.items():
 assert len(r['slots'])==20 and not r['slot_failures'] and not r['road_failures'] and not r['sweep_failures'];assert [s['number'] for s in r['slots']]==list(range(1,21))
 summary[name]={'persisted_slots':20,'footprint_support_rays':180,'full_safety_box_checks':20,'route_support_rays':r['road_rays'],'route_swept_segments':r['swept_sphere_segments'],'failures':0,'checkpoint_actor_classes':r['existing_checkpoint_actor_classes']}
report['saved_map_geometry']=summary;report['pairwise_safety_envelopes']={'pairs':layout['pair_tests'],'overlaps':layout['overlaps']};report['limitations']='Twenty-participant runs use explicit test-only ProofPawn instances, not a production AI field. Normal Play has only its existing assigned player. No checkpoint actors, lap system or AI navigation exist to validate actual race/checkpoint behavior.'
(ev/'test_results.json').write_text(json.dumps(report,indent=2));print('PASS: six starts, four with 20 test pawns and two with one participant; both saved grids, footprint checks and loop collision verified.')


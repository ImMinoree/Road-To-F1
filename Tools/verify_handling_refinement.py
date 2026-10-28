"""Verify saved engine results and decode actual PIE captures; does not run gameplay."""
from pathlib import Path
import hashlib,json
from PIL import Image

root=Path(__file__).resolve().parents[1]
ev=root/'Evidence/HandlingRefinement'
report=json.loads((ev/'AutomationFinal/index.json').read_text(encoding='utf-8-sig'))
assert report['failed']==0 and report['notRun']==0
assert report['succeeded']+report['succeededWithWarnings']==7
contact=json.loads((ev/'ContactFinal/index.json').read_text(encoding='utf-8-sig'))
assert contact['failed']==0 and contact['notRun']==0
for name in ['race_result.json','race_stationary_result.json']:
    result=json.loads((ev/name).read_text(encoding='utf-8-sig'))
    assert result['passed'] and result['final'] and result['start_events']==1
    assert all(r['laps']>=2 and r['maximum_edge_excess_cm']<5 for r in result['racers'])
pie=json.loads((ev/'pie_validation.json').read_text(encoding='utf-8-sig'))
assert pie['passed'] and pie['actual_pie'] and pie['cockpit_and_chase_toggled']
captures=[]
for label in pie['screenshots']:
    paths=list(ev.glob(label+'[0-9]*.png'))
    assert paths,label
    for path in paths:
        with Image.open(path) as im:
            im.load();assert im.width>=800 and im.height>=400
            captures.append({'file':path.name,'width':im.width,'height':im.height,'bytes':path.stat().st_size})
hashes=json.loads((root/'Checkpoints/BeforeHandlingRefinement_20261026/map_hashes.json').read_text(encoding='utf-8-sig'))
for entry in hashes:
    assert hashlib.sha256(Path(entry['Path']).read_bytes()).hexdigest().upper()==entry['Hash'].upper()
old=json.loads((root/'Checkpoints/BeforeTireDynamics_20261024/protected_hashes.json').read_text(encoding='utf-8-sig'))
original={p:h for p,h in old.items() if '/Road-To-F1/RoadToF1/' in p}
assert len(original)==4
for path,digest in original.items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()==digest.upper()
summary={'verified':True,'automation_suites':7,'automation_failures':0,'automation_warning_suites':report['succeededWithWarnings'],
         'contact_final_passed':True,'moving_and_stationary_player_ai_races_passed':True,
         'maps_unchanged':True,'original_physics_sources_unchanged':True,'screenshots':captures,
         'contact_metrics':json.loads((ev/'world_contact_metrics.json').read_text(encoding='utf-8-sig'))}
(ev/'verification.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

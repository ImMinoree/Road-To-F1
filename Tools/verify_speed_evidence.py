"""Decode saved cockpit captures and check the actual PIE validation report."""
from pathlib import Path
import json
from PIL import Image

ev=Path(__file__).resolve().parents[1]/'Evidence/SpeedEffects'
result=json.loads((ev/'pie_validation.json').read_text())
assert result['passed'] and result['actual_pie'] and result['maps_unchanged']
rows={r['name']:r for r in result['samples']}
for name in ['pre_start','disabled','reset']:
    assert abs(rows[name]['fov']-110)<.01 and rows[name]['blur_strength']==0
assert 112<rows['driving']['fov']<=115
assert rows['driving']['blur_strength']>.1
assert rows['re_enabled']['fov']>110
automation=json.loads((ev/'Automation/index.json').read_text(encoding='utf-8-sig'))
assert automation['succeeded']==1 and automation['failed']==0
shots=[]
for name in ['pre_start','driving','disabled','reset']:
    path=ev/(name+'.png')
    with Image.open(path) as img:img.verify()
    with Image.open(path) as img:
        img.load();assert img.size==(1600,900) and img.format=='PNG'
        shots.append({'file':path.name,'dimensions':list(img.size),'decoded':True})
report={'actual_pie_passed':True,'ownership_and_steering_regression_passed':True,'screenshots':shots}
(ev/'verified_captures.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

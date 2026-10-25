"""Verify saved Unreal test evidence; does not run or simulate a race."""
import json
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
evidence = root / 'Evidence/RacingAI'
summary = {}
for name in ('moving_player', 'stopped_player'):
    result = json.loads((evidence / f'race_result_{name}.json').read_text())
    assert result['final'] and result['passed']
    assert result['opponents'] == 4 and result['staged'] == 5
    assert result['start_events'] == 1 and result['five_red_gate_captured']
    assert len(result['racers']) == 4
    for racer in result['racers']:
        assert racer['laps'] >= 2 and racer['visited_sectors'] == 64
        assert racer['maximum_grid_movement_cm'] < 1
        assert racer['off_track_frames'] == 0
    summary[name] = {'passed': True, 'race_seconds': result['race_seconds'],
                     'recoveries': [r['recoveries'] for r in result['racers']]}
automation = json.loads((evidence / 'AutomationFinal/index.json').read_text(encoding='utf-8-sig'))
assert automation['succeeded'] == 2 and automation['failed'] == 0
summary['automation_tests_passed'] = automation['succeeded']
pie = json.loads((evidence / 'pie_validation.json').read_text())
assert pie['actual_pie'] and pie['pawns'] == 5 and pie['ai_opponents'] == 4
assert pie['all_visible_and_moving'] and pie['maps_unchanged']
assert pie['telemetry']['world_type'] == 3
summary['rendered_pie_passed'] = True
summary['screenshots'] = []
for name in ('four_ai_grid.png', 'four_ai_launch.png', 'four_ai_racing.png'):
    path = evidence / name
    with Image.open(path) as img:
        img.verify()
    with Image.open(path) as img:
        img.load()
        assert img.size == (1600, 900) and img.format == 'PNG'
    summary['screenshots'].append({'file': name, 'width': 1600, 'height': 900, 'valid': True})
(evidence / 'validation_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))

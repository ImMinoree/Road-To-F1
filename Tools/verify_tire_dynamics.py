"""Verify final Unreal results, decode actual captures and recheck protected checkpoint hashes."""
from pathlib import Path
import csv, hashlib, json, math
from PIL import Image
root=Path(__file__).resolve().parents[1];ev=root/'Evidence/TireDynamics'
protected=json.loads((root/'Checkpoints/BeforeTireDynamics_20261024/protected_hashes.json').read_text(encoding='utf-8-sig'))
for path,digest in protected.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()==digest.upper(),path
automation=json.loads((ev/'AutomationFinal/index.json').read_text(encoding='utf-8-sig'))
assert automation['failed']==0 and automation['succeeded']+automation['succeededWithWarnings']==5
assert all(test['state']=='Success' for test in automation['tests'])
race=json.loads((ev/'race_result_final.json').read_text())
assert race['final'] and race['passed'] and race['start_events']==1 and race['staged']==5 and race['five_red_gate_captured']
for racer in race['racers']:
    assert racer['laps']>=2 and racer['visited_sectors']==64 and racer['maximum_grid_movement_cm']<1 and racer['off_track_frames']==0
pie=json.loads((ev/'pie_validation.json').read_text())
assert pie['passed'] and pie['actual_pie'] and pie['race_restart_passed'] and pie['maps_and_original_repository_unchanged']
assert 6<pie['max_slide_beta_deg']<25 and pie['max_z_error_cm']<1 and pie['maximum_frame_travel_cm']<400
rows=list(csv.DictReader((ev/'pie_maneuver.csv').open()))
for row in rows:
    assert all(math.isfinite(float(row[key])) for key in ['u_mps','v_mps','beta_deg','yaw_deg_s','front_fy_n','rear_fy_n','z_cm'])
    assert float(row['front_use'])<=1.001 and float(row['rear_use'])<=1.001
assert any(row['drifting']=='True' for row in rows)
captures=[]
for name in pie['screenshots']:
    path=max(ev.glob(name+'*.png'),key=lambda p:p.stat().st_mtime)
    with Image.open(path) as img:img.verify()
    with Image.open(path) as img:
        img.load();assert img.width>800 and img.height>600
        captures.append({'path':str(path),'dimensions':list(img.size),'valid':True})
warnings=[entry['event']['message'] for test in automation['tests'] for entry in test['entries'] if entry['event']['type']=='Warning']
summary={'passed':True,'protected_files_unchanged':True,'automation_suites_passed':5,'automation_warnings':warnings,
         'ai_racers_completed_two_laps':4,'race_seconds':race['race_seconds'],'actual_pie':True,'max_slide_beta_deg':pie['max_slide_beta_deg'],
         'recovered_at_speed':pie['recovered_at_speed'],'max_z_error_cm':pie['max_z_error_cm'],'screenshots':captures}
(ev/'validation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

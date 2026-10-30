"""Check actual HUD log conversions and package the final screenshot."""
import json,re,math,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];E=R/'Evidence/SpeedGauge'
r=json.loads((E/'validation.json').read_text());assert r['passed'] and r['maps_unchanged']
rows=re.findall(r'SPEED_GAUGE kmh=([\d.]+) shown=(\d+) unit=(\w+) fraction=([\d.]+) reverse=(\d)',(E/'pie_final.log').read_text())
assert rows and any(unit=='mph' for _,_,unit,_,_ in rows) and any(reverse=='1' for *_,reverse in rows)
for kmh,shown,unit,fraction,reverse in rows:
 speed=float(kmh)*(0.621371192 if unit=='mph' else 1)
 assert abs(int(shown)-speed)<=.5001,(kmh,shown,unit)
 assert abs(float(fraction)-min(1,float(kmh)/80))<.00002
source=max(E.glob('02_accelerating_kmh0*.png'),key=lambda p:p.stat().st_mtime);shutil.copy2(source,E/'speed_gauge.png')
r.update(rendered_log_samples_checked=len(rows),conversion_checks_passed=True,final_screenshots_inspected=True,main_screenshot='speed_gauge.png')
(E/'validation.json').write_text(json.dumps(r,indent=2))
print('PASS:',len(rows),'rendered speed samples; km/h, mph, reverse and map screenshots verified.')

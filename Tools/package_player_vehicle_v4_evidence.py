"""Package existing Unreal captures; never synthesize validation or rendered frames."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1];E=R/'Evidence/PlayerVehicle_v4'
result=json.loads((E/'validation.json').read_text());assert result['passed']
for name in result['screenshots']:
 candidates=list(E.glob(name+'0*.png'))
 assert candidates,name
 shutil.copy2(max(candidates,key=lambda p:p.stat().st_mtime),E/(name+'.png'))
frames=[name+'.png' for name in result['screenshots'] if name.startswith('motion_')]
(E/'steering_sequence.html').write_text('<!doctype html><meta charset="utf-8"><title>Actual Unreal steering capture</title><style>body{background:#111;color:white;font:18px sans-serif}img{max-width:100%;max-height:85vh}</style><p>Actual PIE cockpit steering frames; approximately 5 fps. Click image to pause.</p><img id="frame"><script>const frames='+json.dumps(frames)+';let i=0,playing=true;const img=document.getElementById("frame");img.onclick=()=>playing=!playing;setInterval(()=>{if(playing){img.src=frames[i++%frames.length]}},200);</script>')
protected=json.loads((E/'import.json').read_text())['protected_hashes']
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest for p,digest in protected.items())
(E/'RESULTS.md').write_text('''# Actual Unreal validation

See `validation.json`, `motion.csv`, `pie_final.log` and `build_final_link.log` for the final run. Earlier failed attempts remain for diagnosis; their error files are historical and do not describe the final run.

The A–L checks exercised centre/left/right steering, rapid steering, acceleration, reverse, simultaneous steer/roll, braking, sustained turning, drift recovery, collision/restart and countdown gating. This is a functional validation, not certification of anatomical surface fit. Ground-speed wheel roll does not simulate tire angular slip. The separate fixed-rod automation swept 481 steering values.

The seven numbered PNGs are actual Unreal viewport captures. `steering_sequence.html` plays the captured cockpit frames. Driver garment seams, finger/rim surface contact, seat contact and inherited body proportions need manual art refinement. There is no performance/LOD certification. Physics and map hashes still match the recorded baseline.
''')
print(json.dumps(result,indent=2))

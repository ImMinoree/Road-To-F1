from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1];E=R/'Evidence/PlayerVehicle_v4/Hands'
r=json.loads((E/'validation.json').read_text());assert r['passed']
for pattern,name in [('02_steering_center0*.png','hands_center.png'),('03_full_left0*.png','hands_left.png'),('04_full_right0*.png','hands_right.png'),('05_cockpit_center0*.png','cockpit.png')]:
 p=max(E.glob(pattern),key=lambda x:x.stat().st_mtime);shutil.copy2(p,E/name)
frames=[]
for name in r['screenshots']:
 if name.startswith('motion_'):
  p=max(E.glob(name+'0*.png'),key=lambda x:x.stat().st_mtime);frames.append(p.name)
(E/'steering_sequence.html').write_text('<!doctype html><meta charset="utf-8"><title>Gloved grip — actual Unreal capture</title><style>body{background:#111;color:#fff;font:18px sans-serif}img{max-width:100%;max-height:85vh}</style><p>Actual Unreal cockpit frames, played at 5 fps. Capture cadence varies. Click to pause.</p><img id="f"><script>let a='+json.dumps(frames)+',i=0,play=true;const f=document.getElementById("f");f.onclick=()=>play=!play;setInterval(()=>{if(play)f.src=a[i++%a.length]},200)</script>')
(E/'RESULTS.md').write_text('# Gloved grip validation\n\nActual PIE run: '+str(r['frames'])+' samples. All A–L functional checks passed. The wrist and distal joints of all five fingers on both hands were tracked against the wheel; maximum relative drift was '+str(round(r['maximum_hand_relative_wheel_error_cm'],5))+' cm. This measures joint alignment rather than certifying every surface intersection.\n\nSee hands_center.png, hands_left.png, hands_right.png, cockpit.png and steering_sequence.html for actual Unreal evidence. The glove revision is saved in the editable Blender assembly and both driver skins. The original driver suit still has inherited seam/tailoring limitations. These are modeled game gloves, not photorealistic scanned hands.\n')
print(r['frames'],r['maximum_hand_relative_wheel_error_cm'])
report=(E/'RESULTS.md').read_text()
report+='\nHand structure revision (2026-10-28): outside-to-inside finger wrap, fuller tapered palm, repositioned opposed thumb and wrist. The original steering wheel is preserved. The final runtime log is pie_structure_20261028.log. Imported grip normals retain smooth glove lighting. Original suit seams remain. structure_static_hash_verification.json checks all 18 versioned static kart meshes against this revision\'s backup. protected_hash_verification.json compares maps and tire sources against the older integration baseline: maps and tire CPP files match; two tire headers differ from that older baseline and were not edited or reverted by this hand revision.\n'
(E/'RESULTS.md').write_text(report,encoding='utf-8')

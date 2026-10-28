import json,hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];P=R/'Art/PlayerVisuals/Cockpit_Layout_v5';E=R/'Evidence/Cockpit_Layout_v5';validation=json.loads((P/'validation.json').read_text());arms=json.loads((P/'arm_leg_checks.json').read_text())
out={'final_scene':str(P/'Kart_Cockpit_Layout_v5.blend'),'files':{},'rim_nonmanifold_edges':validation['rim_nonmanifold_edges'],'max_rim_vertices_outside_frame':max(x['out_of_frame_rim_vertices'] for x in validation['projection_frames']),'maximum_sampled_arm_leg_triangle_contacts':max(x['arm_leg_triangle_pairs'] for x in arms),'limitations':'Residual seat/frame/boot-linkage contacts are recorded in contacts.json. Visual reference quality is not fully matched.'}
for f in [P/'Kart_Cockpit_Layout_v5.blend',*sorted((P/'Exports').glob('*.fbx'))]:out['files'][str(f.relative_to(R))]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
out['unreal_screenshots']={f.name:list(Image.open(f).size) for f in sorted((E/'After').glob('*.png'))};(E/'verification.json').write_text(json.dumps(out,indent=2))

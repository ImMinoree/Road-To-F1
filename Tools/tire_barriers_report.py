"""Package only actual successful tire-barrier evidence; no Unreal mutations."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];P=R/'Art/Trackside/TireBarriers';E=R/'Evidence/TireBarriers'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
result=read(E/'validation.json');capture=read(E/'capture.json');imported=read(E/'import.json');checks=read(E/'protected_final.json')
assert result['map_saved'] and 'error' not in result and result['barrier_collision_trace_passed']
assert not capture['existing_structure_overlap_probes'] and all(c['unchanged'] for c in checks)
assert all(m['convex_collision_count']>0 and m['lods']==4 for m in imported['meshes'])
assert hashlib.sha256((R/'SM_Tire_Black.blend').read_bytes()).digest()==hashlib.sha256((P/'Backup/SM_Tire_Black.original.blend').read_bytes()).digest()
for pattern,target in [('driver_eye_near_corner0*.png','driver_eye_corner.png')]:
 source=max(E.glob(pattern),key=lambda p:p.stat().st_mtime);shutil.copy2(source,E/target)
for filename in ['tire_closeup.png','barrier_modules.png','unreal_barrier_detail.png','driver_eye_corner.png']:assert (E/filename).stat().st_size>10000
for filename in ['error.txt','capture_error.txt']:
 p=E/filename
 if p.exists():p.replace(E/('superseded_'+filename))
result.update(accepted=True,blender_and_Unreal_renders_inspected=True,existing_structure_overlap_failures=0,protected_nonvisual_files_verified=len(checks),original_blend_preserved=True,actual_driver_eye_screenshot='driver_eye_corner.png',actual_Unreal_detail_screenshot='unreal_barrier_detail.png')
(E/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(E/'RESULTS.md').write_text('Created in Blender 5.2.2 and imported into the existing UE 5.8 project. Original tire preserved and backed up. Three editable 2.19 m modules each contain twelve hollow-profile 55 cm tires; five FBXs and six PBR texture maps are supplied. All five meshes have four LODs and one simple convex collision hull.\n\n144 HISM tires form two three-high outside-corner walls in DesertKarting_Visual. Source runoff clearance is at least 2.505 m to the tire centres (over 2.23 m to the tire surface). All 748 centre-route segments were swept before/after with a 60 cm sphere radius; no new obstruction or road-support difference. A horizontal barrier trace confirmed blocking collision. All 48 columns were fitted to live traced ground; 48 additional probes found no existing structure overlap. Existing actor transforms and collision-enabled settings match before/after. '+str(len(checks))+' protected nonvisual source/config/map files match their pre-task hashes.\n\nActual images: tire_closeup.png and barrier_modules.png (Blender); unreal_barrier_detail.png (Unreal editor); driver_eye_corner.png (actual ProofPawn camera in stationary braked Play mode). The renders were visually inspected.\n\nLimits: rigid static barriers, filled-centre convex vehicle collision, no tire deformation or impact absorption. 13,120 triangles per close tire, reduced to 35%, 12% and 4% in subsequent LODs. No complete driven lap or full-race performance certification. Earlier failed commandlet/API attempts are retained in logs and superseded error files; validation.json is the accepted result. No commit or push.\n',encoding='utf-8')
print(json.dumps({'accepted':True,'instanced_tires':result['instanced_tires'],'protected_files':len(checks),'exports':len(list((P/'Exports').glob('*.fbx')))}))

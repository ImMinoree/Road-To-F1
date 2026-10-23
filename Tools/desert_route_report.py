"""Read-only final verification and concise machine-readable route review."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];EV=ROOT/'Evidence/DesertRoute';g=json.loads((ROOT/'Art/DesertRoute/audit.json').read_text());apply=json.loads((EV/'apply.json').read_text());before=json.loads((EV/'Before_validation.json').read_text());after=json.loads((EV/'Final_validation.json').read_text())
failures=[]
for p,h in apply['protected_hashes'].items():
 file=Path(p) if Path(p).is_absolute() else ROOT/p
 if hashlib.sha256(file.read_bytes()).hexdigest()!=h:failures.append(p)
assert not failures,failures
summary={}
for mp,result in after['maps'].items():
 old=before['maps'][mp];assert result['lights']==old['lights'],'Lighting settings changed'
 assert not result['road_failures'] and not result['sweep_failures'] and not result['visible_kart_groups'],result
 expected={k:v for k,v in old['collision_actors'].items() if '10 Race karts' not in k};actual={k:v for k,v in result['collision_actors'].items() if not k.startswith('RR_')};assert actual==expected,('Unexpected collision changes',mp,set(actual)^set(expected))
 cp=ROOT/'Content/RoadToF1/Checkpoints'/(mp.rsplit('/',1)[-1]+'_BeforeRoute.umap');assert cp.is_file(),cp
 for phase in ['Before','After']:
  for suffix in ['TopDown','Annotated']:assert (EV/(phase+'_'+mp.rsplit('/',1)[-1]+'_'+suffix+'.png')).is_file()
 summary[mp]={'before_failed_support_rays':len(old['road_failures']),'before_obstructed_sweep_segments':len(old['sweep_failures']),'final_support_rays_passed':result['road_rays'],'final_swept_segments_clear':result['swept_sphere_segments'],'final_visible_kart_groups':0,'lighting_unchanged':True,'other_collision_actors_unchanged':True}
report={'length_m':g['length_m'],'source_geometry':g['native_blend_comparison'],'connected_main_surface_components':g['connected_components'],'boundary_loops':g['boundary_loops'],'nonlocal_asphalt_overlaps':len(g['nonlocal_surface_overlaps']),'minimum_source_width_m':g['min_source_width_m'],'direction':'User-confirmed +X main straight / increasing source route index','corner_numbering':'C1-C7 analytical turn complexes, not official corner numbers','maps':summary,'new_readability_assets':3,'route_arrows':22,'corner_boards':7,'finish':'Existing gantry station; new full-width paint above road. Original hidden checker geometry preserved.','barrier_relocations':0,'pit':{'proposed_entry_A':g['pit_geometry_sections'][0],'proposed_exit_B':g['pit_geometry_sections'][1],'junctions_modified':False,'status':'No verified entry-to-exit pit route; A has an overlap but no designed taper, B has a 5.74m asphalt gap.'},'shortcuts':'Infield/runoff remain drivable with no checkpoint enforcement. Off-track shortcuts cannot be ruled out or claimed fixed.','protected_files_verified':len(apply['protected_hashes']),'protected_file_failures':failures,'original_meshes_lighting_gameplay_preserved':True,'validation_scope':'Live editor line traces at 748 samples x 3 lateral positions and 28cm-radius sphere sweeps along all 748 segments. Not a completed timed lap or a full-size vehicle dynamics certification.','raw_topdown_projection':'Orthographic pitch -90°, 2400x2000; identical before/after cameras','renders_inspected':True}
(EV/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'loop_m':report['length_m'],'maps':summary,'protected_files':report['protected_files_verified'],'pit_B_gap_m':g['pit_geometry_sections'][1]['lateral_asphalt_gap_m']},indent=2))

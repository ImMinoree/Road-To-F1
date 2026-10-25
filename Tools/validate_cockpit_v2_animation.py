import unreal as u,json,math
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();source=json.loads((ROOT/'Art/PlayerVisuals/Cockpit_Reference_v2/geometry_validation.json').read_text())['source_bone_samples_cm'];anim=u.load_asset('/Game/RoadToF1/PlayerVisuals/CockpitReferenceV2/A_CV2_Steering');assert anim
options=u.AnimPoseEvaluationOptions();options.should_retarget=False;options.evaluation_type=u.AnimDataEvalType.COMPRESSED
rows=[]
for frame,bones in source.items():
 pose=u.AnimPoseExtensions.get_anim_pose_at_time(anim,(int(frame)-1)/24,options)
 for name,xyz in bones.items():
  tr=u.AnimPoseExtensions.get_bone_pose(pose,name,u.AnimPoseSpaces.WORLD);p=tr.translation;expected=[xyz[0],-xyz[1],xyz[2]];actual=[p.x,p.y,p.z];error=math.dist(actual,expected);rows.append({'frame':int(frame),'bone':name,'expected_cm':expected,'actual_cm':actual,'error_cm':error})
out={'max_error_cm':max(r['error_cm'] for r in rows),'samples':rows};(ROOT/'Evidence/Cockpit_Reference_v2/animation_pose_check.json').write_text(json.dumps(out,indent=2));assert out['max_error_cm']<.5,out;u.log('CV2_HAND_AND_KNEE_POSES_VERIFIED '+str(out['max_error_cm']))

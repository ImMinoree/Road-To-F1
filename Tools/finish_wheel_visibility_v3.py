import unreal as u,json,math
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/PlayerVisuals/Wheel_Visibility_v3';OUT='/Game/RoadToF1/PlayerVisuals/WheelVisibilityV3';OLD='/Game/RoadToF1/PlayerVisuals/CockpitReferenceV2'
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');t=u.AssetImportTask();t.filename=str(ART/'Exports/SM_WV3_PlayerChassis.fbx');t.destination_path=OUT;t.destination_name='SM_WV3_PlayerChassis';t.automated=True;t.save=True;t.replace_existing=True
o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_as_skeletal=False;o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;o.static_mesh_import_data.convert_scene_unit=True;t.options=o;u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);mesh=u.load_asset(OUT+'/SM_WV3_PlayerChassis');assert mesh
original=u.load_asset(OLD+'/SM_CV2_PlayerChassis');mats={str(x.material_slot_name):x.material_interface for x in original.get_editor_property('static_materials')}
for i,slot in enumerate(mesh.get_editor_property('static_materials')):
 name=str(slot.material_slot_name);mat=mats.get(name) or u.load_asset(OLD+'/'+name);assert mat,name;mesh.set_material(i,mat)
u.EditorAssetLibrary.save_asset(mesh.get_path_name(),only_if_is_dirty=False)
anim=u.load_asset(OUT+'/A_WV3_Steering');source=json.loads((ART/'validation.json').read_text())['bone_samples'];options=u.AnimPoseEvaluationOptions();options.should_retarget=False;options.evaluation_type=u.AnimDataEvalType.COMPRESSED;rows=[]
for sample in source:
 frame=sample['frame'];pose=u.AnimPoseExtensions.get_anim_pose_at_time(anim,(frame-1)/24,options)
 for name,xyz in sample['bones'].items():
  p=u.AnimPoseExtensions.get_bone_pose(pose,name,u.AnimPoseSpaces.WORLD).translation;expected=[xyz[0]*100,-xyz[1]*100,xyz[2]*100];actual=[p.x,p.y,p.z];rows.append({'frame':frame,'bone':name,'error_cm':math.dist(actual,expected)})
report={'max_error_cm':max(r['error_cm'] for r in rows),'samples':rows};(ROOT/'Evidence/Wheel_Visibility_v3/animation_pose_check.json').write_text(json.dumps(report,indent=2));assert report['max_error_cm']<.5,report;u.log('WV3_IMPORTED_POSES_VERIFIED '+str(report['max_error_cm']))

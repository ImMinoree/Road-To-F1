"""Import separate POV revision; reuse unchanged V2 materials/wheel/chassis. No map saves."""
import unreal as u,json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/PlayerVisuals/Wheel_Visibility_v3';OUT='/Game/RoadToF1/PlayerVisuals/WheelVisibilityV3';OLD='/Game/RoadToF1/PlayerVisuals/CockpitReferenceV2';tools=u.AssetToolsHelpers.get_asset_tools()
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
t=u.AssetImportTask();t.filename=str(ART/'Exports/SK_WV3_DriverPOV.fbx');t.destination_path=OUT;t.destination_name='SK_WV3_DriverPOV';t.automated=True;t.save=True;t.replace_existing=True
opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH;opts.import_as_skeletal=True;opts.import_mesh=True;opts.import_animations=False;opts.import_materials=False;opts.import_textures=False;opts.create_physics_asset=False;opts.skeletal_mesh_import_data.convert_scene=True;opts.skeletal_mesh_import_data.convert_scene_unit=True;t.options=opts;tools.import_asset_tasks([t]);mesh=u.load_asset(OUT+'/SK_WV3_DriverPOV');assert mesh
t=u.AssetImportTask();t.filename=str(ART/'Exports/SK_WV3_DriverPOV.fbx');t.destination_path=OUT;t.destination_name='A_WV3_Steering';t.automated=True;t.save=True;t.replace_existing=True
opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION;opts.import_as_skeletal=True;opts.import_mesh=False;opts.import_animations=True;opts.skeleton=mesh.get_editor_property('skeleton');opts.override_animation_name='A_WV3_Steering';opts.import_materials=False;opts.import_textures=False;t.options=opts;tools.import_asset_tasks([t]);anim=u.load_asset(OUT+'/A_WV3_Steering');assert anim
slots=list(mesh.get_editor_property('materials'))
for slot in slots:
 mat=u.load_asset(OLD+'/'+str(slot.material_slot_name));assert mat,str(slot.material_slot_name);slot.material_interface=mat
mesh.set_editor_property('materials',slots)
label=tools.create_asset('PAL_WheelVisibilityV3',OUT,u.PrimaryAssetLabel,u.DataAssetFactory()) if not u.EditorAssetLibrary.does_asset_exist(OUT+'/PAL_WheelVisibilityV3') else u.load_asset(OUT+'/PAL_WheelVisibilityV3');label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',True);rules=label.get_editor_property('rules');rules.set_editor_property('cook_rule',u.PrimaryAssetCookRule.ALWAYS_COOK);label.set_editor_property('rules',rules)
for p in u.EditorAssetLibrary.list_assets(OUT):u.EditorAssetLibrary.save_asset(p,only_if_is_dirty=False)
(ROOT/'Evidence/Wheel_Visibility_v3/import.json').write_text(json.dumps({'assets':list(u.EditorAssetLibrary.list_assets(OUT)),'animation_seconds':anim.get_editor_property('sequence_length'),'wheel_chassis_materials':'reuse unchanged V2'},indent=2));u.log('WV3_IMPORT_COMPLETE')

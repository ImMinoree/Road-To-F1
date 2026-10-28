"""Replace only the backed-up driver skins and their shared grip animation."""
import unreal as u
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();src=(R/'Tools/import_player_vehicle_v4.py').read_text();src=src.replace('if not skin:d.combine_meshes=True;', 'if skin:d.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS\n if not skin:d.combine_meshes=True;');exec(src[:src.index("full=imp('SK_V4_DriverFull'")])
sk=u.load_asset(O+'/SK_V4_DriverFull_Skeleton');assert sk
for name in ['SK_V4_DriverFull','SK_V4_DriverPOV']:
 a=u.load_asset(O+'/'+name)
 subsystem=u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
 settings=subsystem.get_lod_build_settings(a,0)
 u.log(name+' previous build settings: '+str(settings))
 a.get_editor_property('asset_import_data').set_editor_property('normal_import_method',u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
 settings.set_editor_property('recompute_normals',False)
 subsystem.set_lod_build_settings(a,0,settings)
 mats={str(slot.material_slot_name):slot.material_interface for slot in a.get_editor_property('materials')};a=imp(name,True,sk);slots=list(a.get_editor_property('materials'))
 settings=subsystem.get_lod_build_settings(a,0);settings.set_editor_property('recompute_normals',False);subsystem.set_lod_build_settings(a,0,settings)
 for slot in slots:slot.material_interface=mats[str(slot.material_slot_name)]
 a.set_editor_property('materials',slots);assert u.EditorAssetLibrary.save_loaded_asset(a)
t=u.AssetImportTask();t.filename=str(P/'Exports/SK_V4_DriverPOV.fbx');t.destination_path=O;t.destination_name='A_V4_Steering';t.automated=True;t.save=True;t.replace_existing=True
o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION;o.import_mesh=False;o.import_animations=True;o.import_as_skeletal=True;o.skeleton=sk;o.override_animation_name='A_V4_Steering';o.import_materials=False;o.import_textures=False;t.options=o;A.import_asset_tasks([t])
assert u.EditorAssetLibrary.save_loaded_asset(u.load_asset(O+'/A_V4_Steering'))
u.log('V4_GLOVED_GRIP_IMPORTED')

import unreal as u,json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();OUT='/Game/RoadToF1/PlayerVisuals/CockpitTargetV4';u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');t=u.AssetImportTask();t.filename=str(ROOT/'Art/PlayerVisuals/Cockpit_Target_v4/Exports/SM_CT4_SteeringWheel.fbx');t.destination_path=OUT;t.destination_name='SM_CT4_SteeringWheel';t.automated=True;t.save=True;t.replace_existing=True;o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_as_skeletal=False;o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;o.static_mesh_import_data.convert_scene_unit=True;t.options=o;u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);mesh=u.load_asset(OUT+'/SM_CT4_SteeringWheel');assert mesh
for i,slot in enumerate(mesh.get_editor_property('static_materials')):
 m=u.load_asset(OUT+'/'+str(slot.material_slot_name));assert m;mesh.set_material(i,m)
u.EditorAssetLibrary.save_loaded_asset(mesh);u.log('CT4_NORMALS_FINISHED')

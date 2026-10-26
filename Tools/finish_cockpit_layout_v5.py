"""Separate local-player art; no maps or existing assets are saved."""
import unreal as u,json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/PlayerVisuals/Cockpit_Layout_v5';OUT='/Game/RoadToF1/PlayerVisuals/CockpitLayoutV5';AT=u.AssetToolsHelpers.get_asset_tools();ME=u.MaterialEditingLibrary;report={};u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
def fbx(name,skin=False):
 t=u.AssetImportTask();t.filename=str(ART/'Exports'/(name+'.fbx'));t.destination_path=OUT;t.destination_name=name;t.automated=True;t.save=True;t.replace_existing=True;o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH if skin else u.FBXImportType.FBXIT_STATIC_MESH;o.import_as_skeletal=skin;o.import_mesh=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False
 d=o.skeletal_mesh_import_data if skin else o.static_mesh_import_data;d.convert_scene=True;d.convert_scene_unit=True
 if not skin:d.combine_meshes=True;d.auto_generate_collision=False
 t.options=o;AT.import_asset_tasks([t]);a=u.load_asset(OUT+'/'+name);assert a,name;return a
kart=fbx('SM_CL5_PlayerChassis')
for i,slot in enumerate(kart.get_editor_property('static_materials')):kart.set_material(i,u.load_asset('/Game/RoadToF1/PlayerVisuals/CockpitTargetV4/'+str(slot.material_slot_name)))
assert u.EditorAssetLibrary.save_loaded_asset(kart)

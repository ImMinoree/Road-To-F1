"""Separate local-player art; no maps or existing assets are saved."""
import unreal as u,json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/PlayerVisuals/Cockpit_Layout_v5';OUT='/Game/RoadToF1/PlayerVisuals/CockpitLayoutV5';AT=u.AssetToolsHelpers.get_asset_tools();ME=u.MaterialEditingLibrary;report={};u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
def fbx(name,skin=False):
 t=u.AssetImportTask();t.filename=str(ART/'Exports'/(name+'.fbx'));t.destination_path=OUT;t.destination_name=name;t.automated=True;t.save=True;t.replace_existing=True;o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH if skin else u.FBXImportType.FBXIT_STATIC_MESH;o.import_as_skeletal=skin;o.import_mesh=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False
 d=o.skeletal_mesh_import_data if skin else o.static_mesh_import_data;d.convert_scene=True;d.convert_scene_unit=True
 if not skin:d.combine_meshes=True;d.auto_generate_collision=False
 t.options=o;AT.import_asset_tasks([t]);a=u.load_asset(OUT+'/'+name);assert a,name;return a
arms=fbx('SK_CL5_DriverPOV',True);wheel=fbx('SM_CL5_SteeringWheel');kart=fbx('SM_CL5_PlayerChassis')
t=u.AssetImportTask();t.filename=str(ART/'Exports/SK_CL5_DriverPOV.fbx');t.destination_path=OUT;t.destination_name='A_CL5_Steering';t.automated=True;t.save=True;t.replace_existing=True;o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION;o.import_mesh=False;o.import_animations=True;o.import_as_skeletal=True;o.skeleton=arms.get_editor_property('skeleton');o.override_animation_name='A_CL5_Steering';o.import_materials=False;o.import_textures=False;t.options=o;AT.import_asset_tasks([t]);anim=u.load_asset(OUT+'/A_CL5_Steering');assert anim
materials='/Game/RoadToF1/PlayerVisuals/CockpitTargetV4/'
slots=list(arms.get_editor_property('materials'))
for slot in slots:
 slot.material_interface=u.load_asset(materials+str(slot.material_slot_name));assert slot.material_interface
arms.set_editor_property('materials',slots)
for ob in [wheel,kart]:
 for i,slot in enumerate(ob.get_editor_property('static_materials')):
  m=u.load_asset(materials+str(slot.material_slot_name));assert m;ob.set_material(i,m)
label=AT.create_asset('PAL_CockpitLayoutV5',OUT,u.PrimaryAssetLabel,u.DataAssetFactory()) if not u.EditorAssetLibrary.does_asset_exist(OUT+'/PAL_CockpitLayoutV5') else u.load_asset(OUT+'/PAL_CockpitLayoutV5')
label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',True);rules=label.get_editor_property('rules');rules.set_editor_property('cook_rule',u.PrimaryAssetCookRule.ALWAYS_COOK);label.set_editor_property('rules',rules)
for p in u.EditorAssetLibrary.list_assets(OUT):assert u.EditorAssetLibrary.save_asset(p,only_if_is_dirty=True)
u.log('CL5_IMPORT_COMPLETE')

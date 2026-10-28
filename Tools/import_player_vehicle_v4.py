"""Import only the versioned assembly; maps, physics assets and prior art are untouched."""
import unreal as u,json,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();P=R/'Art/PlayerVehicle_v4';O='/Game/RoadToF1/PlayerVehicleV4';A=u.AssetToolsHelpers.get_asset_tools();M=u.MaterialEditingLibrary
manifest=json.loads((P/'manifest.json').read_text());u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
protected=[*list((R/'Content/RoadToF1/Maps').glob('*.umap')),*list((R/'Source/Road_To_F1_New').glob('KartTire*'))]
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
def imp(name,skin=False,skeleton=None):
 t=u.AssetImportTask();t.filename=str(P/'Exports'/(name+'.fbx'));t.destination_path=O;t.destination_name=name;t.automated=True;t.save=True;t.replace_existing=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH if skin else u.FBXImportType.FBXIT_STATIC_MESH;o.import_as_skeletal=skin;o.import_mesh=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False
 if skeleton:o.skeleton=skeleton
 d=o.skeletal_mesh_import_data if skin else o.static_mesh_import_data;d.convert_scene=True;d.convert_scene_unit=True
 if not skin:d.combine_meshes=True;d.auto_generate_collision=False
 t.options=o;A.import_asset_tasks([t]);a=u.load_asset(O+'/'+name);assert a,name;return a
full=imp('SK_V4_DriverFull',True);sk=full.get_editor_property('skeleton');assert sk;assert u.EditorAssetLibrary.save_loaded_asset(sk);pov=imp('SK_V4_DriverPOV',True,sk)
t=u.AssetImportTask();t.filename=str(P/'Exports/SK_V4_DriverPOV.fbx');t.destination_path=O;t.destination_name='A_V4_Steering';t.automated=True;t.save=True;t.replace_existing=True;o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION;o.import_mesh=False;o.import_animations=True;o.import_as_skeletal=True;o.skeleton=sk;o.override_animation_name='A_V4_Steering';o.import_materials=False;o.import_textures=False;t.options=o;A.import_asset_tasks([t]);assert u.load_asset(O+'/A_V4_Steering')
assets=[full,pov]+[imp(f.stem) for f in sorted((P/'Exports').glob('SM_*.fbx'))]
norm=lambda s:''.join(c for c in s.lower() if c.isalnum()).rstrip('0123456789')
existing={}
for folder in ['/Game/RoadToF1/PlayerVisuals/CockpitTargetV4','/Game/RoadToF1/PlayerVisuals/FirstPerson/ChassisMaterials','/Game/RoadToF1/RacingAI/Materials']:
 for path in u.EditorAssetLibrary.list_assets(folder,recursive=True):
  if path.split('/')[-1].startswith('M_'):
   m=u.load_asset(path)
   if isinstance(m,u.MaterialInterface):existing[norm(m.get_name())]=m
materials={}
for name,data in manifest['materials'].items():
 match=existing.get(norm(name)) or existing.get(norm('M_AI_'+name))
 if not match:
  safe='M_V4_'+''.join(c if c.isalnum() else '_' for c in name);path=O+'/Materials/'+safe
  match=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else A.create_asset(safe,O+'/Materials',u.Material,u.MaterialFactoryNew())
  M.delete_all_material_expressions(match);color=M.create_material_expression(match,u.MaterialExpressionConstant3Vector);color.constant=u.LinearColor(*data['color']);M.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
  for value,prop in [(data['roughness'],u.MaterialProperty.MP_ROUGHNESS),(data['metallic'],u.MaterialProperty.MP_METALLIC)]:
   n=M.create_material_expression(match,u.MaterialExpressionConstant);n.r=value;M.connect_material_property(n,'',prop)
  M.set_material_usage(match,u.MaterialUsage.MATUSAGE_SKELETAL_MESH);M.recompile_material(match);u.EditorAssetLibrary.save_loaded_asset(match)
 materials[norm(name)]=match
for a in assets:
 if isinstance(a,u.SkeletalMesh):
  slots=list(a.get_editor_property('materials'))
  for slot in slots:
   slot.material_interface=materials[norm(str(slot.material_slot_name))]
  a.set_editor_property('materials',slots)
 else:
  for i,slot in enumerate(a.get_editor_property('static_materials')):a.set_material(i,materials[norm(str(slot.material_slot_name))])
 assert u.EditorAssetLibrary.save_loaded_asset(a)
label=A.create_asset('PAL_PlayerVehicleV4',O,u.PrimaryAssetLabel,u.DataAssetFactory()) if not u.EditorAssetLibrary.does_asset_exist(O+'/PAL_PlayerVehicleV4') else u.load_asset(O+'/PAL_PlayerVehicleV4');label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',True);rules=label.get_editor_property('rules');rules.set_editor_property('cook_rule',u.PrimaryAssetCookRule.ALWAYS_COOK);label.set_editor_property('rules',rules);u.EditorAssetLibrary.save_loaded_asset(label)
assert hashes=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
(R/'Evidence/PlayerVehicle_v4/import.json').write_text(json.dumps({'assets':[a.get_path_name() for a in assets],'shared_skeleton':sk.get_path_name(),'protected_hashes':hashes,'maps_and_physics_unchanged':True},indent=2));u.log('PLAYER_VEHICLE_V4_IMPORTED')

exec(compile((R/'Tools/finish_player_vehicle_v4_materials.py').read_text(), 'finish_player_vehicle_v4_materials.py', 'exec'))

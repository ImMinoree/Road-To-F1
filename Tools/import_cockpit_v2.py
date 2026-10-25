"""Import only the reversible CV2 local-player art folder; never load/save a map."""
import unreal as u,json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/PlayerVisuals/Cockpit_Reference_v2';OUT='/Game/RoadToF1/PlayerVisuals/CockpitReferenceV2';OLD='/Game/RoadToF1/PlayerVisuals/FirstPerson';report={'assets':[],'missing_chassis_materials':[]}
tools=u.AssetToolsHelpers.get_asset_tools();u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
def load_fbx(name,skin=False):
 t=u.AssetImportTask();t.filename=str(ART/'Exports'/(name+'.fbx'));t.destination_path=OUT;t.destination_name=name;t.automated=True;t.save=True;t.replace_existing=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH if skin else u.FBXImportType.FBXIT_STATIC_MESH;o.import_as_skeletal=skin;o.import_mesh=True;o.import_animations=skin;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False
 if skin:o.override_animation_name='A_CV2_Steering'
 data=o.skeletal_mesh_import_data if skin else o.static_mesh_import_data;data.convert_scene=True;data.convert_scene_unit=True;data.force_front_x_axis=False
 if not skin:data.combine_meshes=True;data.auto_generate_collision=False
 t.options=o;tools.import_asset_tasks([t]);report['assets']+=list(t.imported_object_paths);return u.load_asset(OUT+'/'+name)
finish='-CV2FinishOnly' in u.SystemLibrary.get_command_line()
driver_only='-CV2DriverOnly' in u.SystemLibrary.get_command_line()
mesh=u.load_asset(OUT+'/SK_CV2_DriverPOV') if finish else load_fbx('SK_CV2_DriverPOV',True)
if not finish:
 # Skeletal mesh reimport may retain old clips: explicitly import the baked animation too.
 t=u.AssetImportTask();t.filename=str(ART/'Exports/SK_CV2_DriverPOV.fbx');t.destination_path=OUT;t.destination_name='A_CV2_Steering';t.automated=True;t.save=True;t.replace_existing=True
 opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION;opts.import_as_skeletal=True;opts.import_mesh=False;opts.import_animations=True;opts.skeleton=mesh.get_editor_property('skeleton');opts.override_animation_name='A_CV2_Steering';opts.import_materials=False;opts.import_textures=False;t.options=opts;tools.import_asset_tasks([t]);report['explicit_animation_import']=list(t.imported_object_paths)
wheel=u.load_asset(OUT+'/SM_CV2_SteeringWheel') if finish or driver_only else load_fbx('SM_CV2_SteeringWheel')
chassis=u.load_asset(OUT+'/SM_CV2_PlayerChassis') if finish or driver_only else load_fbx('SM_CV2_PlayerChassis')
assert mesh and wheel and chassis
anims=[u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(OUT) if isinstance(u.load_asset(p),u.AnimSequence)]
assert anims,'No imported animation';anim=anims[0]
if anim.get_name()!='A_CV2_Steering':
 assert u.EditorAssetLibrary.rename_asset(anim.get_path_name(),OUT+'/A_CV2_Steering')
 anim=u.load_asset(OUT+'/A_CV2_Steering')
assert anim.get_editor_property('skeleton')==mesh.get_editor_property('skeleton')
manifest=json.loads((ART/'manifest.json').read_text());ME=u.MaterialEditingLibrary;materials={};normal=u.load_asset(OLD+'/T_FP_Microfiber_N')
for name,entry in manifest['materials'].items():
 m=u.load_asset(OUT+'/'+name) if u.EditorAssetLibrary.does_asset_exist(OUT+'/'+name) else tools.create_asset(name,OUT,u.Material,u.MaterialFactoryNew());ME.delete_all_material_expressions(m)
 c=ME.create_material_expression(m,u.MaterialExpressionConstant3Vector,-400,0);c.constant=u.LinearColor(*entry['color']);ME.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
 for value,prop,y in [(entry['roughness'],u.MaterialProperty.MP_ROUGHNESS,150),(entry['metallic'],u.MaterialProperty.MP_METALLIC,250)]:
  n=ME.create_material_expression(m,u.MaterialExpressionConstant,-300,y);n.r=value;ME.connect_material_property(n,'',prop)
 if any(x in name for x in ['Textile','Graphite','Suede','BlueGrip']):
  uv=ME.create_material_expression(m,u.MaterialExpressionTextureCoordinate,-850,400);uv.u_tiling=5;uv.v_tiling=5;tx=ME.create_material_expression(m,u.MaterialExpressionTextureSample,-600,400);tx.texture=normal;tx.sampler_type=u.MaterialSamplerType.SAMPLERTYPE_NORMAL;ME.connect_material_expressions(uv,'',tx,'UVs');ME.connect_material_property(tx,'RGB',u.MaterialProperty.MP_NORMAL)
 if 'LED' in name:ME.connect_material_property(c,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
 ME.set_material_usage(m,u.MaterialUsage.MATUSAGE_SKELETAL_MESH);ME.recompile_material(m);materials[name]=m
slots=list(mesh.get_editor_property('materials'))
for slot in slots:slot.material_interface=materials.get(str(slot.material_slot_name),materials['M_CV2_SuitGraphite'])
mesh.set_editor_property('materials',slots)
for obj in [wheel,chassis]:
 for i,slot in enumerate(obj.get_editor_property('static_materials')):
  name=str(slot.material_slot_name);mat=materials.get(name)
  if not mat:mat=u.load_asset(OLD+'/ChassisMaterials/'+name) if u.EditorAssetLibrary.does_asset_exist(OLD+'/ChassisMaterials/'+name) else None
  if not mat:report['missing_chassis_materials'].append(name);mat=materials['M_CV2_TrimRubber']
  obj.set_material(i,mat)
label=u.load_asset(OUT+'/PAL_CockpitV2') if u.EditorAssetLibrary.does_asset_exist(OUT+'/PAL_CockpitV2') else tools.create_asset('PAL_CockpitV2',OUT,u.PrimaryAssetLabel,u.DataAssetFactory());label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',True);rules=label.get_editor_property('rules');rules.set_editor_property('cook_rule',u.PrimaryAssetCookRule.ALWAYS_COOK);label.set_editor_property('rules',rules)
for p in u.EditorAssetLibrary.list_assets(OUT):u.EditorAssetLibrary.save_asset(p,only_if_is_dirty=False)
report.update(animation_seconds=anim.get_editor_property('sequence_length'),skeletal_materials=[str(x.material_slot_name) for x in slots],saved=list(u.EditorAssetLibrary.list_assets(OUT)))
(ROOT/'Evidence/Cockpit_Reference_v2/import.json').write_text(json.dumps(report,indent=2));u.log('CV2_IMPORT_COMPLETE '+json.dumps(report))

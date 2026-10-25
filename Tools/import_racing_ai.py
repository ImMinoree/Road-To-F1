"""Import existing V5 presentation and measured edges. Never edit either circuit map."""
import unreal as u,json,hashlib
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/RacingAI';EV=ROOT/'Evidence/RacingAI';OUT='/Game/RoadToF1/RacingAI'
tools=u.AssetToolsHelpers.get_asset_tools();ME=u.MaterialEditingLibrary
maps={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Content/RoadToF1/Maps').glob('*.umap')}
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
task=u.AssetImportTask();task.filename=str(ART/'SK_AI_KartDriver.fbx');task.destination_path=OUT;task.destination_name='SK_AI_KartDriver';task.automated=True;task.save=True;task.replace_existing=True
o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH;o.import_as_skeletal=True;o.import_mesh=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False
o.skeleton=u.load_asset('/Game/RoadToF1/PlayerVisuals/FirstPerson/SK_FP_KartArms_Skeleton');assert o.skeleton
o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True;task.options=o;tools.import_asset_tasks([task])
mesh=u.load_asset(OUT+'/SK_AI_KartDriver');assert mesh and mesh.get_editor_property('skeleton')==o.skeleton
manifest=json.loads((ART/'driver_export.json').read_text());materials={}
for name,data in manifest['materials'].items():
    safe='M_AI_'+''.join(c if c.isalnum() else '_' for c in name)
    mat=u.load_asset(OUT+'/Materials/'+safe) if u.EditorAssetLibrary.does_asset_exist(OUT+'/Materials/'+safe) else tools.create_asset(safe,OUT+'/Materials',u.Material,u.MaterialFactoryNew())
    ME.delete_all_material_expressions(mat);color=ME.create_material_expression(mat,u.MaterialExpressionConstant3Vector);color.constant=u.LinearColor(*data['color']);ME.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
    for value,prop in [(data['roughness'],u.MaterialProperty.MP_ROUGHNESS),(data['metallic'],u.MaterialProperty.MP_METALLIC)]:
        node=ME.create_material_expression(mat,u.MaterialExpressionConstant);node.r=value;ME.connect_material_property(node,'',prop)
    ME.set_material_usage(mat,u.MaterialUsage.MATUSAGE_SKELETAL_MESH);ME.recompile_material(mat);u.EditorAssetLibrary.save_loaded_asset(mat);materials[name]=mat
slots=list(mesh.get_editor_property('materials'))
for slot in slots:
    name=str(slot.material_slot_name)
    # FBX sanitizes spaces and pipes in source material slot names.
    normalized=lambda s:''.join(c for c in s.lower() if c.isalnum())
    matches=[m for key,m in materials.items() if normalized(key)==normalized(name)]
    assert len(matches)==1,(name,list(materials))
    slot.material_interface=matches[0]
mesh.set_editor_property('materials',slots);u.EditorAssetLibrary.save_loaded_asset(mesh)
edges=json.loads((ART/'track_edges.json').read_text());factory=u.DataAssetFactory();factory.set_editor_property('data_asset_class',u.TrackEdgeRoute)
route=u.load_asset(OUT+'/DA_DesertTrackEdges') if u.EditorAssetLibrary.does_asset_exist(OUT+'/DA_DesertTrackEdges') else tools.create_asset('DA_DesertTrackEdges',OUT,u.TrackEdgeRoute,factory)
for key in ['center','left','right','guide']:route.set_editor_property(key,[u.Vector(*p) for p in edges[key]])
u.EditorAssetLibrary.save_loaded_asset(route)
label=tools.create_asset('PAL_RacingAI',OUT,u.PrimaryAssetLabel,u.DataAssetFactory()) if not u.EditorAssetLibrary.does_asset_exist(OUT+'/PAL_RacingAI') else u.load_asset(OUT+'/PAL_RacingAI')
label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',True);rules=label.get_editor_property('rules');rules.set_editor_property('cook_rule',u.PrimaryAssetCookRule.ALWAYS_COOK);label.set_editor_property('rules',rules);u.EditorAssetLibrary.save_loaded_asset(label)
assert maps=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Content/RoadToF1/Maps').glob('*.umap')}
(EV/'import.json').write_text(json.dumps({'mesh':mesh.get_path_name(),'skeleton':o.skeleton.get_path_name(),'material_slots':len(slots),'parts':len(manifest['parts']),'route':route.get_path_name(),'edge_samples':len(edges['center']),'maps_unchanged':True,'source_unchanged':manifest['source_unchanged']},indent=2))
u.log('RACING_AI_IMPORT_COMPLETE')

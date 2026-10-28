import unreal as u,json
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();O='/Game/RoadToF1/RaceLiveries';M=u.MaterialEditingLibrary;A=u.AssetToolsHelpers.get_asset_tools();report={}
for name,src in [('M_GridPaint','M_CT4_BodyGraphite'),('M_GridFabric','M_CT4_RedKnit')]:
 path=O+'/'+name;m=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else u.EditorAssetLibrary.duplicate_asset('/Game/RoadToF1/PlayerVisuals/CockpitTargetV4/'+src,path);assert m
 color=M.create_material_expression(m,u.MaterialExpressionVectorParameter,-400,-250);color.set_editor_property('parameter_name','LiveryColor');color.set_editor_property('default_value',u.LinearColor(.7,.1,.05,1))
 if name=='M_GridFabric':
  tx=M.create_material_expression(m,u.MaterialExpressionTextureSample,-650,-100);tx.texture=u.load_asset('/Game/RoadToF1/PlayerVisuals/CockpitTargetV4/Textures/T_CT4_Weave_C');assert tx.texture
  uv=M.create_material_expression(m,u.MaterialExpressionTextureCoordinate,-850,-100);uv.u_tiling=12;uv.v_tiling=12;M.connect_material_expressions(uv,'',tx,'UVs');mult=M.create_material_expression(m,u.MaterialExpressionMultiply,-150,-250);M.connect_material_expressions(color,'RGB',mult,'A');M.connect_material_expressions(tx,'RGB',mult,'B');M.connect_material_property(mult,'',u.MaterialProperty.MP_BASE_COLOR)
 else:M.connect_material_property(color,'RGB',u.MaterialProperty.MP_BASE_COLOR)
 M.set_material_usage(m,u.MaterialUsage.MATUSAGE_SKELETAL_MESH);M.set_material_usage(m,u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);M.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m);report[name]=m.get_path_name()
label=u.load_asset(O+'/PAL_RaceLiveries') or A.create_asset('PAL_RaceLiveries',O,u.PrimaryAssetLabel,u.DataAssetFactory());label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',True);rules=label.get_editor_property('rules');rules.set_editor_property('cook_rule',u.PrimaryAssetCookRule.ALWAYS_COOK);label.set_editor_property('rules',rules);assert u.EditorAssetLibrary.save_loaded_asset(label)
(R/'Evidence/TenKartGrid/materials.json').write_text(json.dumps(report,indent=2));u.log('TEN_KART_LIVERIES_CREATED')


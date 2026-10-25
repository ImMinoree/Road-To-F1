import unreal as u
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();BASE='/Game/RoadToF1/SurfaceFX';T=u.AssetToolsHelpers.get_asset_tools();E=u.EditorAssetLibrary;M=u.MaterialEditingLibrary
def material(name,color,dust=False):
 path=BASE+'/Materials/'+name;mat=u.load_asset(path) or T.create_asset(name,BASE+'/Materials',u.Material,u.MaterialFactoryNew());M.delete_all_material_expressions(mat)
 mat.set_editor_property('two_sided',True);mat.set_editor_property('used_with_instanced_static_meshes',True)
 def n(c):return M.create_material_expression(mat,c)
 def link(a,b,p,out=''):
  inputs=M.get_material_expression_input_names(b)
  if p not in inputs and len(inputs)==1:p=inputs[0]
  assert M.connect_material_expressions(a,out,b,p)
 c=n(u.MaterialExpressionConstant3Vector);c.set_editor_property('constant',u.LinearColor(*color))
 if dust:
  mat.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT);mat.set_editor_property('shading_model',u.MaterialShadingModel.MSM_DEFAULT_LIT)
  M.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
  uv=n(u.MaterialExpressionTextureCoordinate);fade=n(u.MaterialExpressionPerInstanceCustomData);fade.set_editor_property('data_index',0)
  interp=n(u.MaterialExpressionVertexInterpolator);link(fade,interp,'Input')
  soft=n(u.MaterialExpressionCustom);soft.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT1);inputs=[]
  for name in ['UV','Fade']:
   x=u.CustomInput();x.set_editor_property('input_name',name);inputs.append(x)
  soft.set_editor_property('inputs',inputs);soft.set_editor_property('code','float2 p=UV*2-1; float r=dot(p,p); float edge=saturate(1-r); float noise=0.8+0.2*sin(UV.x*27+sin(UV.y*18)); return edge*edge*noise*Fade*0.38;');link(uv,soft,'UV');link(interp,soft,'Fade');M.connect_material_property(soft,'',u.MaterialProperty.MP_OPACITY)
 else:
  M.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR);v=n(u.MaterialExpressionConstant);v.set_editor_property('r',.95);M.connect_material_property(v,'',u.MaterialProperty.MP_ROUGHNESS)
 M.recompile_material(mat);assert E.save_loaded_asset(mat);return mat
mats=[material('M_SoilChip',[.12,.065,.026]),material('M_GrassClipping',[.04,.09,.012]),material('M_TireDust',[.21,.145,.075],True)]
for name,mat in zip(['SM_SoilChip','SM_GrassClipping','SM_DustQuad'],mats):
 task=u.AssetImportTask();task.filename=str(R/'Art/SurfaceFX/Meshes'/(name+'.fbx'));task.destination_path=BASE+'/Meshes';task.automated=True;task.save=True;task.replace_existing=True
 opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opt.import_materials=False;opt.import_textures=False;opt.static_mesh_import_data.set_editor_property('auto_generate_collision',False);opt.static_mesh_import_data.set_editor_property('combine_meshes',True);task.options=opt;T.import_asset_tasks([task]);mesh=u.load_asset(BASE+'/Meshes/'+name);assert mesh;mesh.set_material(0,mat);assert E.save_loaded_asset(mesh)
label=u.load_asset(BASE+'/PAL_SurfaceFX') or T.create_asset('PAL_SurfaceFX',BASE,u.PrimaryAssetLabel,u.DataAssetFactory());label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',True);rules=label.get_editor_property('rules');rules.set_editor_property('cook_rule',u.PrimaryAssetCookRule.ALWAYS_COOK);label.set_editor_property('rules',rules);assert E.save_loaded_asset(label)

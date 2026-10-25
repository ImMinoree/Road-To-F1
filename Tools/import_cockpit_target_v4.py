"""Separate local-player art; no maps or existing assets are saved."""
import unreal as u,json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/PlayerVisuals/Cockpit_Target_v4';OUT='/Game/RoadToF1/PlayerVisuals/CockpitTargetV4';AT=u.AssetToolsHelpers.get_asset_tools();ME=u.MaterialEditingLibrary;report={};u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
def fbx(name,skin=False):
 t=u.AssetImportTask();t.filename=str(ART/'Exports'/(name+'.fbx'));t.destination_path=OUT;t.destination_name=name;t.automated=True;t.save=True;t.replace_existing=True;o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH if skin else u.FBXImportType.FBXIT_STATIC_MESH;o.import_as_skeletal=skin;o.import_mesh=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False
 d=o.skeletal_mesh_import_data if skin else o.static_mesh_import_data;d.convert_scene=True;d.convert_scene_unit=True
 if not skin:d.combine_meshes=True;d.auto_generate_collision=False
 t.options=o;AT.import_asset_tasks([t]);a=u.load_asset(OUT+'/'+name);assert a,name;return a
arms=fbx('SK_CT4_DriverPOV',True);wheel=fbx('SM_CT4_SteeringWheel');kart=fbx('SM_CT4_PlayerChassis')
t=u.AssetImportTask();t.filename=str(ART/'Exports/SK_CT4_DriverPOV.fbx');t.destination_path=OUT;t.destination_name='A_CT4_Steering';t.automated=True;t.save=True;t.replace_existing=True;o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION;o.import_mesh=False;o.import_animations=True;o.import_as_skeletal=True;o.skeleton=arms.get_editor_property('skeleton');o.override_animation_name='A_CT4_Steering';o.import_materials=False;o.import_textures=False;t.options=o;AT.import_asset_tasks([t]);anim=u.load_asset(OUT+'/A_CT4_Steering');assert anim
def texture(path):
 name=path.stem;a=u.load_asset(OUT+'/Textures/'+name)
 if not a:
  t=u.AssetImportTask();t.filename=str(path);t.destination_path=OUT+'/Textures';t.automated=True;t.save=True;AT.import_asset_tasks([t]);a=u.load_asset(OUT+'/Textures/'+name)
 if name.endswith('_N') or name.endswith('_Normal'):a.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP);a.set_editor_property('srgb',False);a.set_editor_property('flip_green_channel',True)
 elif name.endswith('_R') or name.endswith('_Roughness'):a.set_editor_property('srgb',False);a.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
 u.EditorAssetLibrary.save_loaded_asset(a);return a
textures={p.stem:texture(p) for p in (ART/'Textures').glob('*.png')};manifest=json.loads((ART/'manifest.json').read_text());materials={}
def sample(mat,tx,uv=None,normal=False):
 n=ME.create_material_expression(mat,u.MaterialExpressionTextureSample,-600,300);n.texture=tx
 if normal:n.sampler_type=u.MaterialSamplerType.SAMPLERTYPE_NORMAL
 elif not tx.get_editor_property('srgb'):n.sampler_type=u.MaterialSamplerType.SAMPLERTYPE_MASKS
 if uv:ME.connect_material_expressions(uv,'',n,'UVs')
 return n
for name,d in manifest['materials'].items():
 m=u.load_asset(OUT+'/'+name) or AT.create_asset(name,OUT,u.Material,u.MaterialFactoryNew());ME.delete_all_material_expressions(m);materials[name]=m
 c=ME.create_material_expression(m,u.MaterialExpressionConstant3Vector,-500,0);c.constant=u.LinearColor(*d['color']);ME.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
 for v,prop in [(d['roughness'],u.MaterialProperty.MP_ROUGHNESS),(d['metallic'],u.MaterialProperty.MP_METALLIC)]:
  n=ME.create_material_expression(m,u.MaterialExpressionConstant,-300,120);n.r=v;ME.connect_material_property(n,'',prop)
 if d.get('tile'):
  uv=ME.create_material_expression(m,u.MaterialExpressionTextureCoordinate,-850,400);uv.u_tiling=d['tile'];uv.v_tiling=d['tile'];tx=sample(m,textures['T_CT4_Weave_C'],uv);mult=ME.create_material_expression(m,u.MaterialExpressionMultiply,-300,0);ME.connect_material_expressions(c,'',mult,'A');ME.connect_material_expressions(tx,'RGB',mult,'B');ME.connect_material_property(mult,'',u.MaterialProperty.MP_BASE_COLOR);tx=sample(m,textures['T_CT4_Weave_N'],uv,True);ME.connect_material_property(tx,'RGB',u.MaterialProperty.MP_NORMAL);tx=sample(m,textures['T_CT4_Weave_R'],uv);ME.connect_material_property(tx,'R',u.MaterialProperty.MP_ROUGHNESS)
 surface={'M_CT4_SlickRubber':'SlickRubber','M_CT4_Chromoly':'BrushedAlloy','M_CT4_BodyGraphite':'Graphite','M_CT4_BucketComposite':'MouldedSeat','M_CT4_TankPolymer':'CloudedPolymer'}.get(name)
 if surface:
  for suffix,prop,out in [('BaseColor',u.MaterialProperty.MP_BASE_COLOR,'RGB'),('Roughness',u.MaterialProperty.MP_ROUGHNESS,'R'),('Normal',u.MaterialProperty.MP_NORMAL,'RGB')]:
   tx=texture(ROOT/'Art/DesertKarting/Kart/Textures'/('T_Kart_'+surface+'_'+suffix+'.png'));n=sample(m,tx,normal=suffix=='Normal');ME.connect_material_property(n,out,prop)
 if d.get('screen_texture'):
  n=sample(m,textures['T_CT4_LCD']);ME.connect_material_property(n,'RGB',u.MaterialProperty.MP_BASE_COLOR)
 if d.get('emission'):
  ME.connect_material_property(c,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
 ME.set_material_usage(m,u.MaterialUsage.MATUSAGE_SKELETAL_MESH);ME.recompile_material(m)
slots=list(arms.get_editor_property('materials'))
for slot in slots:slot.material_interface=materials[str(slot.material_slot_name)]
arms.set_editor_property('materials',slots)
for ob in [wheel,kart]:
 for i,slot in enumerate(ob.get_editor_property('static_materials')):ob.set_material(i,materials[str(slot.material_slot_name)])
label=u.load_asset(OUT+'/PAL_CockpitTargetV4') or AT.create_asset('PAL_CockpitTargetV4',OUT,u.PrimaryAssetLabel,u.DataAssetFactory());label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',True);rules=label.get_editor_property('rules');rules.set_editor_property('cook_rule',u.PrimaryAssetCookRule.ALWAYS_COOK);label.set_editor_property('rules',rules)
for p in u.EditorAssetLibrary.list_assets(OUT):u.EditorAssetLibrary.save_asset(p,only_if_is_dirty=True)
report={'assets':list(u.EditorAssetLibrary.list_assets(OUT)),'animation_seconds':anim.get_editor_property('sequence_length')};(ROOT/'Evidence/Cockpit_Target_v4/import.json').write_text(json.dumps(report,indent=2));u.log('CT4_IMPORT_COMPLETE')

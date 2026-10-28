"""Import new tire assets only; placement/acceptance run in the live editor."""
import unreal as u,json,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();P=R/'Art/Trackside/TireBarriers';EV=R/'Evidence/TireBarriers';B='/Game/RoadToF1/Trackside/TireBarriers'
E=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();M=u.MaterialEditingLibrary;S=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Source','Config'] for p in (R/folder).rglob('*') if p.is_file()}
protected.update({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'Content/RoadToF1/Maps').glob('*.umap')})
(EV/'protected_before.json').write_text(json.dumps(protected,indent=2))
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
tasks=[]
for p in (P/'Textures').glob('*.png'):
 if p.stem.endswith('NormalGL'):continue
 t=u.AssetImportTask();t.filename=str(p);t.destination_path=B+'/Textures';t.automated=True;t.save=True;t.replace_existing=True;tasks.append(t)
T.import_asset_tasks(tasks)
for t in tasks:
 a=u.load_asset(B+'/Textures/'+Path(t.filename).stem)
 if not a.get_name().endswith('BaseColor'):a.set_editor_property('srgb',False)
 if a.get_name().endswith('NormalDX'):a.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
 E.save_loaded_asset(a)
master=u.load_asset(B+'/Materials/M_TireBarrier_PBR') or T.create_asset('M_TireBarrier_PBR',B+'/Materials',u.Material,u.MaterialFactoryNew())
M.delete_all_material_expressions(master);master.set_editor_property('used_with_instanced_static_meshes',True)
def node(cls):return M.create_material_expression(master,cls)
def link(a,b,p,out=''):assert M.connect_material_expressions(a,out,b,p)
for param,file,prop,stype in [('BaseColor','T_Tire_Black_BaseColor',u.MaterialProperty.MP_BASE_COLOR,u.MaterialSamplerType.SAMPLERTYPE_COLOR),('Roughness','T_Tire_Black_Roughness',u.MaterialProperty.MP_ROUGHNESS,u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR),('Normal','T_Tire_NormalDX',u.MaterialProperty.MP_NORMAL,u.MaterialSamplerType.SAMPLERTYPE_NORMAL)]:
 t=node(u.MaterialExpressionTextureSampleParameter2D);t.set_editor_property('parameter_name',param);t.set_editor_property('texture',u.load_asset(B+'/Textures/'+file));t.set_editor_property('sampler_type',stype)
 if param=='BaseColor':
  r=node(u.MaterialExpressionPerInstanceRandom);mul=node(u.MaterialExpressionMultiply);mul.set_editor_property('const_b',.2);link(r,mul,'A');add=node(u.MaterialExpressionAdd);add.set_editor_property('const_b',.9);link(mul,add,'A');color=node(u.MaterialExpressionMultiply);link(t,color,'A','RGB');link(add,color,'B');assert M.connect_material_property(color,'',prop)
 else:assert M.connect_material_property(t,'RGB' if param=='Normal' else 'R',prop)
for value,prop in [(0,u.MaterialProperty.MP_METALLIC),(.25,u.MaterialProperty.MP_SPECULAR)]:
 c=node(u.MaterialExpressionConstant);c.set_editor_property('r',value);M.connect_material_property(c,'',prop)
M.recompile_material(master);E.save_loaded_asset(master);materials={}
for color in ['Black','Red']:
 name='MI_Tire_'+color;a=u.load_asset(B+'/Materials/'+name) or T.create_asset(name,B+'/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew());M.set_material_instance_parent(a,master)
 for param,suffix in [('BaseColor','BaseColor'),('Roughness','Roughness')]:M.set_material_instance_texture_parameter_value(a,param,u.load_asset(B+'/Textures/T_Tire_'+color+'_'+suffix))
 E.save_loaded_asset(a);materials[color]=a
meshes={};report=[]
for p in sorted((P/'Exports').glob('*.fbx')):
 t=u.AssetImportTask();t.filename=str(p);t.destination_path=B+'/Meshes';t.destination_name=p.stem;t.automated=True;t.save=True;t.replace_existing=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False
 d=o.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;t.options=o;T.import_asset_tasks([t])
 a=u.load_asset(B+'/Meshes/'+p.stem);assert a
 for i,slot in enumerate(a.get_editor_property('static_materials')):a.set_material(i,materials['Red' if 'Red' in str(slot.material_slot_name) else 'Black'])
 opts=u.StaticMeshReductionOptions();opts.auto_compute_lod_screen_size=False;opts.reduction_settings=[u.StaticMeshReductionSettings(percent_triangles=percent,screen_size=screen) for percent,screen in [(1,1),(.35,.22),(.12,.09),(.04,.025)]]
 assert S.set_lods(a,opts)>=3
 S.remove_collisions(a);assert S.add_simple_collisions(a,u.ScriptCollisionShapeType.NDOP18)>=0
 a.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_SIMPLE_AND_COMPLEX)
 E.save_loaded_asset(a);meshes[p.stem]=a
 bounds=a.get_bounding_box();size=bounds.max-bounds.min
 if p.stem.startswith('SM_TB_Tire_'):assert abs(size.x-55)<.1 and abs(size.z-18.4)<.1,(p.stem,size)
 report.append({'name':p.stem,'dimensions_cm':[size.x,size.y,size.z],'lods':S.get_lod_count(a),'simple_collision_count':S.get_simple_collision_count(a),'convex_collision_count':S.get_convex_collision_count(a)})
for color in ['Black','Red']:
 name='FT_TireBarrier_'+color;ft=u.load_asset(B+'/Instancing/'+name) or T.create_asset(name,B+'/Instancing',u.FoliageType_InstancedStaticMesh,u.FoliageType_InstancedStaticMeshFactory())
 ft.set_editor_property('mesh',meshes['SM_TB_Tire_'+color]);ft.set_editor_property('cull_distance',u.Int32Interval(min=20000,max=25000));ft.set_editor_property('collision_with_world',False)
 body=ft.get_editor_property('body_instance');body.set_editor_property('collision_enabled',u.CollisionEnabled.QUERY_AND_PHYSICS);body.set_editor_property('collision_profile_name','BlockAll');ft.set_editor_property('body_instance',body);E.save_loaded_asset(ft)
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in protected.items())
(EV/'import.json').write_text(json.dumps({'meshes':report,'materials':[a.get_path_name() for a in materials.values()],'import_succeeded':True,'protected_files_unchanged':len(protected)},indent=2))
u.log('TIRE_BARRIERS_IMPORTED')

"""Import original start-light assets, mount at the verified finish and stage one real PlayerStart."""
import unreal as u,json,hashlib
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/RaceStart';EV=ROOT/'Evidence/RaceStart';BASE='/Game/RoadToF1/RaceStart';E=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();M=u.MaterialEditingLibrary;L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem)
g=json.loads((ART/'manifest.json').read_text());tasks=[]
protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Content').rglob('*.uasset') if '/RaceStart/' not in p.as_posix()}
for folder in ['Meshes','Textures','Audio']:
 for p in (ART/folder).glob('*'):
  if E.does_asset_exist(BASE+'/'+folder+'/'+p.stem):continue
  t=u.AssetImportTask();t.filename=str(p);t.destination_path=BASE+'/'+folder;t.automated=True;t.save=True
  if folder=='Meshes':
   o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.set_editor_property('combine_meshes',True);o.static_mesh_import_data.set_editor_property('auto_generate_collision',False);o.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False);t.options=o
  tasks.append(t)
T.import_asset_tasks(tasks)
tex=u.load_asset(BASE+'/Textures/T_RS_LEDMask');assert tex;tex.set_editor_property('srgb',False);E.save_loaded_asset(tex)
def make(name):
 m=u.load_asset(BASE+'/Materials/'+name) or T.create_asset(name,BASE+'/Materials',u.Material,u.MaterialFactoryNew());M.delete_all_material_expressions(m);return m
def scalar(m,value):
 n=M.create_material_expression(m,u.MaterialExpressionConstant);n.set_editor_property('r',value);return n
def color(m,c):
 n=M.create_material_expression(m,u.MaterialExpressionConstant3Vector);n.set_editor_property('constant',u.LinearColor(*c));return n
mats={}
for name,c,rough,metal in [('Charcoal',[.012,.018,.024],.42,.15),('Hardware',[.17,.19,.21],.32,.72)]:
 m=make('M_RS_'+name)
 for prop,n in [(u.MaterialProperty.MP_BASE_COLOR,color(m,c)),(u.MaterialProperty.MP_ROUGHNESS,scalar(m,rough)),(u.MaterialProperty.MP_METALLIC,scalar(m,metal))]:M.connect_material_property(n,'',prop)
 M.recompile_material(m);E.save_loaded_asset(m);mats[name]=m
lens=make('M_RS_Lens');lens.set_editor_property('two_sided',True)
M.connect_material_property(color(lens,[.018,.0003,.0002]),'',u.MaterialProperty.MP_BASE_COLOR);M.connect_material_property(scalar(lens,.27),'',u.MaterialProperty.MP_ROUGHNESS)
sample=M.create_material_expression(lens,u.MaterialExpressionTextureSample);sample.set_editor_property('texture',tex);sample.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
param=M.create_material_expression(lens,u.MaterialExpressionScalarParameter);param.set_editor_property('parameter_name','Emission');param.set_editor_property('default_value',.015)
a=M.create_material_expression(lens,u.MaterialExpressionMultiply);M.connect_material_expressions(sample,'RGB',a,'A');M.connect_material_expressions(param,'',a,'B')
b=M.create_material_expression(lens,u.MaterialExpressionMultiply);M.connect_material_expressions(a,'',b,'A');M.connect_material_expressions(color(lens,[1,.0003,.0001]),'',b,'B');M.connect_material_property(b,'',u.MaterialProperty.MP_EMISSIVE_COLOR);M.recompile_material(lens);E.save_loaded_asset(lens);mats['Lens']=lens
meshes={}
for entry in g['assets']:
 mesh=u.load_asset(BASE+'/Meshes/'+entry['mesh']);assert mesh
 for i,slot in enumerate(entry['slots']):mesh.set_material(i,mats[slot])
 E.save_loaded_asset(mesh);meshes[entry['mesh']]=mesh
cls=u.load_class(None,'/Script/Road_To_F1_New.RaceStartGantry');gm=u.load_class(None,'/Script/Road_To_F1_New.ProofGameMode');assert cls and gm
report={}
for name in ['DesertKarting','DesertKarting_Visual']:
 mp='/Game/RoadToF1/Maps/'+name;assert L.load_level(mp);cp='/Game/RoadToF1/Checkpoints/'+name+'_BeforeRaceStart'
 if not E.does_asset_exist(cp):copy=E.duplicate_asset(mp,cp);assert copy and E.save_loaded_asset(copy)
 labels={a.get_actor_label():a for a in A.get_all_level_actors()}
 finish=labels['RR_SM_Route_Finish'];origin,extent=finish.get_actor_bounds(False);assert abs(origin.x+1800)<1 and extent.y>550
 starts=sorted([a for a in A.get_all_level_actors() if isinstance(a,u.PlayerStart)],key=lambda a:a.get_actor_label());assert starts
 start=starts[0];start.set_actor_location(u.Vector(-3400,200,40),False,False);start.set_actor_rotation(u.Rotator(yaw=0),False);start.tags=list(set([str(t) for t in start.tags]+['RaceGridStart']))
 display=next((a for a in A.get_all_level_actors() if a.get_class()==cls),None)
 if not display:display=A.spawn_actor_from_class(cls,u.Vector(-1840,0,0),u.Rotator());display.set_actor_label('RS_FiveRedStartGantry')
 for key,value in {'housing_mesh':meshes['SM_RS_Housing'],'lens_mesh':meshes['SM_RS_RedLens'],'frame_mesh':meshes['SM_RS_MountFrame'],'lens_material':lens,'countdown_sound':u.load_asset(BASE+'/Audio/RS_Countdown'),'lights_out_sound':u.load_asset(BASE+'/Audio/RS_LightsOut'),'preview_red_lights':0,'lit_emission':1000.}.items():display.set_editor_property(key,value)
 display.refresh_display();display.set_actor_enable_collision(False);display.set_folder_path('RaceStart')
 old=labels.get('DK_14 Timing gantry signs and pit furniture | amber')
 if old:old.set_actor_hidden_in_game(True);old.set_actor_enable_collision(False);old.static_mesh_component.set_visibility(False,True);old.static_mesh_component.set_collision_profile_name('NoCollision');old.set_folder_path('_Hidden_ReplacedStartDisplay')
 u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_world_settings().set_editor_property('default_game_mode',gm)
 saved=L.save_current_level();report[name]={'saved':saved,'checkpoint':cp,'stage_cm':[-3400,200,40],'finish_x_cm':origin.x,'display_origin_cm':[-1840,0,0],'lens_center_z_cm':560,'lens_bottom_z_cm':536.8,'audio':'Original procedural waveform assets','default_game_mode':'ProofGameMode'}
for p,h in protected.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
(EV/'implementation.json').write_text(json.dumps(report,indent=2));assert all(r['saved'] for r in report.values())


"""Apply only the defects found in real renders: mirrored text and backface normals."""
import unreal as u,json,ast
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/DesertVisual';G=json.loads((ART/'manifest.json').read_text());BASE='/Game/RoadToF1/DesertVisual'
E=u.EditorAssetLibrary;L=u.MaterialEditingLibrary;T=u.AssetToolsHelpers.get_asset_tools()
task=u.AssetImportTask();task.filename=str(ART/'Textures/RoadMask.png');task.destination_path=BASE+'/Textures';task.automated=True;task.save=True;task.replace_existing=True;T.import_asset_tasks([task])
tex=u.load_asset(BASE+'/Textures/RoadMask');tex.set_editor_property('srgb',False);tex.set_editor_property('address_x',u.TextureAddress.TA_CLAMP);tex.set_editor_property('address_y',u.TextureAddress.TA_CLAMP);E.save_loaded_asset(tex)
tree=ast.parse((ROOT/'Tools/desert_visual_import.py').read_text())
for definition in tree.body:
 if isinstance(definition,ast.FunctionDef):exec(compile(ast.Module(body=[definition],type_ignores=[]),'visual_material_helpers','exec'))
masters={k:master(k,k in ['Masonry','Metal','Fabric']) for k in ['Asphalt','Paint','Masonry','Metal','Fabric','Rubber']}
masters['GroundCover']=master('Paint',False,True)
source=json.loads((ROOT/'Art/DesertKarting/manifest.json').read_text())['materials']
for name in ['grass','grassdark']:instance(name,'GroundCover',source[name]['base'][:3])
for name in ['SM_DV_PitBay','SM_DV_Banner','SM_DV_PitSignPod']:
 t=u.AssetImportTask();t.filename=str(ART/'Meshes'/(name+'.fbx'));t.destination_path=BASE+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.set_editor_property('combine_meshes',True);o.static_mesh_import_data.set_editor_property('auto_generate_collision',False);t.options=o
 T.import_asset_tasks([t]);mesh=u.load_asset(BASE+'/Meshes/'+name)
 slots=next(a['slots'] for a in G['assets'] if a['name']==name)
 for i,s in enumerate(slots):mesh.set_material(i,u.load_asset(BASE+'/Materials/MI_DV_'+s))
 E.save_loaded_asset(mesh)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual');world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
for a in actors.get_all_level_actors():
 if a.get_actor_label()=='DK_14 Timing gantry signs and pit furniture | red':a.static_mesh_component.set_visibility(False,True)
name='SM_DV_PitSignPod';path=BASE+'/Instancing/FT_'+name;f=u.load_asset(path) if E.does_asset_exist(path) else T.create_asset('FT_'+name,BASE+'/Instancing',u.FoliageType_InstancedStaticMesh,u.FoliageType_InstancedStaticMeshFactory());u.InstancedFoliageActor.remove_all_instances(world,f);f.set_editor_property('mesh',u.load_asset(BASE+'/Meshes/'+name));body=f.get_editor_property('body_instance');body.set_editor_property('collision_enabled',u.CollisionEnabled.NO_COLLISION);body.set_editor_property('collision_profile_name','NoCollision');f.set_editor_property('body_instance',body);f.set_editor_property('collision_with_world',False);f.set_editor_property('cull_distance',u.Int32Interval(min=18000,max=35000));E.save_loaded_asset(f)
ps=[p for p in G['placements'] if p['mesh']==name];u.InstancedFoliageActor.add_instances(world,f,[u.Transform(location=u.Vector(*p['location_cm']),rotation=u.Rotator(yaw=p['yaw']),scale=u.Vector(*p['scale'])) for p in ps]);assert level.save_current_level()
report_path=ROOT/'Evidence/DesertVisual/implementation.json';report=json.loads(report_path.read_text());report['instances'][name]=len(ps);report['mesh_assets']=len(G['assets']);report['new_mesh_triangles']=sum(a['triangles'] for a in G['assets']);report_path.write_text(json.dumps(report,indent=2))
(ROOT/'Evidence/DesertVisual/refinement.json').write_text(json.dumps({'render_observed_defects':['Mirrored pit lettering','Black grass caused by world-space normals on backfaces','Stretched plastic detail on vertical faces'],'corrections':['Reflected text orientation corrected in two source-derived detail meshes','Ground-cover master retains native two-sided geometry normals','World-space normals include two-sided sign','Paint and rubber UVs project vertically on walls'],'lighting_changes':False,'collision_changes':False},indent=2))
u.log('DESERT_RENDER_DEFECTS_CORRECTED')

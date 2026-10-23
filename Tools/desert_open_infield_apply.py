"""Reversibly clear only the central paddock and its service pavement."""
import unreal as u,json,hashlib
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/DesertOpenInfield';EV.mkdir(parents=True,exist_ok=True);BASE='/Game/RoadToF1/DesertOpenInfield'
E=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);worlds=u.get_editor_subsystem(u.UnrealEditorSubsystem)
protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Source','Config','Content'] for p in (ROOT/folder).rglob('*') if p.is_file() and (p.suffix=='.uasset' or folder!='Content') and 'DesertOpenInfield' not in str(p)}
tasks=[]
for name in ['SM_OI_StartingGridRetained','SM_OI_InfieldTerrain']:
 if E.does_asset_exist(BASE+'/Meshes/'+name):continue
 t=u.AssetImportTask();t.filename=str(ROOT/'Art/DesertOpenInfield/Meshes'/(name+'.fbx'));t.destination_path=BASE+'/Meshes';t.automated=True;t.save=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.set_editor_property('combine_meshes',True);o.static_mesh_import_data.set_editor_property('auto_generate_collision',False);o.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False);t.options=o;tasks.append(t)
T.import_asset_tasks(tasks)
statefile=EV/'restore.json';state=json.loads(statefile.read_text()) if statefile.exists() else {};report={}
for mp in ['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual']:
 assert level.load_level(mp);cp='/Game/RoadToF1/Checkpoints/'+mp.rsplit('/',1)[-1]+'_BeforeOpenInfield'
 if not E.does_asset_exist(cp):copy=E.duplicate_asset(mp,cp);assert copy and E.save_loaded_asset(copy)
 snapshot={};changed=[];labels={a.get_actor_label():a for a in actors.get_all_level_actors()}
 def snap(a):
  c=a.static_mesh_component;snapshot[a.get_actor_label()]={'mesh':c.static_mesh.get_path_name(),'visible':c.is_visible(),'actor_collision':a.get_actor_enable_collision(),'profile':str(c.get_collision_profile_name()),'folder':str(a.get_folder_path())}
 for label,a in labels.items():
  if not (label.startswith(('DK_09 ','DV_09 ')) or label=='DK_03 Infield lawns and pit lane | asphalt'):continue
  snap(a);a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False);a.static_mesh_component.set_visibility(False,True);a.static_mesh_component.set_collision_profile_name('NoCollision');a.set_folder_path('_Hidden_CentralPaddock');changed.append(label)
 a=labels['DK_03 Infield lawns and pit lane | white'];snap(a);c=a.static_mesh_component;mat=c.get_material(0);mesh=u.load_asset(BASE+'/Meshes/SM_OI_StartingGridRetained');c.set_static_mesh(mesh);c.set_material(0,mat);a.set_actor_enable_collision(False);c.set_collision_profile_name('NoCollision')
 removed={}
 for name in ['SM_DV_ToolChest','SM_DV_TireStack']:
  ft=u.load_asset('/Game/RoadToF1/DesertVisual/Instancing/FT_'+name)
  if not ft:continue
  removed[name]=[]
  for fa in actors.get_all_level_actors():
   for comp in fa.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
    if comp.static_mesh and comp.static_mesh.get_name()==name:
     for i in range(comp.get_instance_count()):
      t=comp.get_instance_transform(i,world_space=True);removed[name].append(str(t))
  u.InstancedFoliageActor.remove_all_instances(worlds.get_editor_world(),ft)
 if 'OI_NaturalInfield' not in labels:
  a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector());a.set_actor_label('OI_NaturalInfield');a.tags=['OpenInfieldVisual'];a.set_folder_path('OpenInfield')
 else:a=labels['OI_NaturalInfield']
 a.static_mesh_component.set_static_mesh(u.load_asset(BASE+'/Meshes/SM_OI_InfieldTerrain'));a.static_mesh_component.set_material(0,labels['DK_03 Infield lawns and pit lane | grassdark'].static_mesh_component.get_material(0));a.set_actor_enable_collision(False);a.static_mesh_component.set_collision_profile_name('NoCollision')
 if mp not in state:state[mp]={'checkpoint':cp,'actors':snapshot,'removed_instances':removed}
 
 for label,entry in snapshot.items():
  if label not in state[mp]['actors']:state[mp]['actors'][label]=entry
 statefile.write_text(json.dumps(state,indent=2));saved=level.save_current_level();report[mp]={'saved':saved,'hidden':changed,'removed_instances':{k:len(v) for k,v in removed.items()},'checkpoint':cp}
for p,h in protected.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
(EV/'applied.json').write_text(json.dumps({'maps':report,'protected_hashes':protected},indent=2));assert all(r['saved'] for r in report.values()),'Map locked; close preview/editor then rerun'


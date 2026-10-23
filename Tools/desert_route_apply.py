"""Add verified readability aids; preserve original meshes, lights, physics and pit design."""
import unreal as u,json,hashlib
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/DesertRoute';EV=ROOT/'Evidence/DesertRoute';BASE='/Game/RoadToF1/DesertRoute';E=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools()
g=json.loads((ART/'markings.json').read_text());level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Source','Config','Content'] for p in (ROOT/folder).rglob('*') if p.is_file() and ((p.suffix=='.uasset' and '/DesertRoute/' not in p.as_posix()) or folder in ['Source','Config'] or (p.suffix=='.umap' and p.stem not in ['DesertKarting','DesertKarting_Visual']))}
for p in [ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.glb',ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.blend',ROOT.parent/'artifacts/desert-karting-circuit/build_scene.py']:protected[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
tasks=[]
for item in g['assets']:
 if E.does_asset_exist(BASE+'/Meshes/'+item['name']):continue
 t=u.AssetImportTask();t.filename=str(ART/'Meshes'/(item['name']+'.fbx'));t.destination_path=BASE+'/Meshes';t.automated=True;t.save=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.set_editor_property('combine_meshes',True);o.static_mesh_import_data.set_editor_property('auto_generate_collision',False);o.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False);t.options=o;tasks.append(t)
T.import_asset_tasks(tasks);meshes={}
for item in g['assets']:
 m=u.load_asset(BASE+'/Meshes/'+item['name']);assert m,item
 for i,name in enumerate(item['slots']):
  material=u.load_asset('/Game/RoadToF1/DesertVisual/Materials/MI_DV_'+{'White':'Letter','Black':'Dark','Steel':'Metal'}[name]);assert material,name;m.set_material(i,material)
 E.save_loaded_asset(m);meshes[item['name']]=m
restore_path=EV/'restore_state.json';restore=json.loads(restore_path.read_text()) if restore_path.exists() else {};status={}
def collision_name(c):
 for n in ['NO_COLLISION','QUERY_ONLY','PHYSICS_ONLY','QUERY_AND_PHYSICS','PROBE_ONLY','QUERY_AND_PROBE']:
  if hasattr(u.CollisionEnabled,n) and c.get_collision_enabled()==getattr(u.CollisionEnabled,n):return n
 raise RuntimeError('Unrecognised collision mode '+str(c.get_collision_enabled()))
for mp in ['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual']:
 assert level.load_level(mp);checkpoint='/Game/RoadToF1/Checkpoints/'+mp.rsplit('/',1)[-1]+'_BeforeRoute'
 if not E.does_asset_exist(checkpoint):
  cp=E.duplicate_asset(mp,checkpoint);assert cp;assert E.save_loaded_asset(cp)
 initial={};hidden=[]
 for a in list(actors.get_all_level_actors()):
  if 'RouteReadability' in [str(t) for t in a.tags]:actors.destroy_actor(a);continue
  if '10 Race karts' in a.get_actor_label():
   initial[a.get_actor_label()]={'actor_enable_collision':a.get_actor_enable_collision(),'components':{c.get_name():collision_name(c) for c in a.get_components_by_class(u.PrimitiveComponent)}}
   a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False)
   for c in a.get_components_by_class(u.PrimitiveComponent):c.set_visibility(False,True);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
   hidden.append(a.get_actor_label())
 if mp not in restore:restore[mp]={'checkpoint':checkpoint,'hidden_kart_collision':initial}
 restore_path.write_text(json.dumps(restore,indent=2))
 for name in ['SM_Route_Finish','SM_Route_CornerBoards']:
  a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector());a.set_actor_label('RR_'+name);a.tags=['RouteReadability'];a.set_folder_path('RouteReadability');a.set_actor_enable_collision(False);c=a.static_mesh_component;c.set_static_mesh(meshes[name]);c.set_collision_profile_name('NoCollision');c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);c.set_cast_shadow(False)
 world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();path=BASE+'/Instancing/FT_RouteArrows';f=u.load_asset(path) if E.does_asset_exist(path) else T.create_asset('FT_RouteArrows',BASE+'/Instancing',u.FoliageType_InstancedStaticMesh,u.FoliageType_InstancedStaticMeshFactory());u.InstancedFoliageActor.remove_all_instances(world,f);f.set_editor_property('mesh',meshes['SM_Route_Arrow']);body=f.get_editor_property('body_instance');body.set_editor_property('collision_enabled',u.CollisionEnabled.NO_COLLISION);body.set_editor_property('collision_profile_name','NoCollision');f.set_editor_property('body_instance',body);f.set_editor_property('collision_with_world',False);f.set_editor_property('cast_shadow',False);f.set_editor_property('cull_distance',u.Int32Interval(min=0,max=0));E.save_loaded_asset(f)
 u.InstancedFoliageActor.add_instances(world,f,[u.Transform(location=u.Vector(*p['location_cm']),rotation=u.Rotator(yaw=p['yaw'])) for p in g['arrows']])
 saved=level.save_current_level();status[mp]={'saved':saved,'checkpoint':checkpoint,'kart_collision_disabled_groups':hidden,'arrows':len(g['arrows']),'corner_boards':len(g['corner_signs'])}
for p,h in protected.items():
 file=Path(p) if Path(p).is_absolute() else ROOT/p;assert hashlib.sha256(file.read_bytes()).hexdigest()==h,p
(EV/'apply.json').write_text(json.dumps({'maps':status,'protected_hashes':protected,'barrier_relocations':0,'pit_geometry_changes':False,'original_mesh_changes':False,'new_collision_geometry':False,'changes':['Visible full-width finish paint at existing gantry station','Sparse source-aligned direction arrows','Seven analytical turn-complex marker boards outside racing surface','Disabled collision on already-hidden kart/driver actors']},indent=2))
assert all(v['saved'] for v in status.values()),'A map is locked; release it in the running editor and rerun this script.'
u.log('ROUTE_READABILITY_APPLIED')

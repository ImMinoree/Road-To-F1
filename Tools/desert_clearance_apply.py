"""Remove the screenshot's obstacles using filtered mesh copies and reversible visibility."""
import unreal as u,json,hashlib
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/DesertClearance';EV=ROOT/'Evidence/DesertClearance';EV.mkdir(parents=True,exist_ok=True);BASE='/Game/RoadToF1/DesertClearance';g=json.loads((ART/'manifest.json').read_text())
E=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Content').rglob('*.uasset') if '/DesertClearance/' not in p.as_posix()}
tasks=[]
for entry in g['filtered']:
 if E.does_asset_exist(BASE+'/Meshes/'+entry['mesh']):continue
 t=u.AssetImportTask();t.filename=str(ART/'Meshes'/(entry['mesh']+'.fbx'));t.destination_path=BASE+'/Meshes';t.automated=True;t.save=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.set_editor_property('combine_meshes',True);o.static_mesh_import_data.set_editor_property('auto_generate_collision',False);o.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False);t.options=o;tasks.append(t)
T.import_asset_tasks(tasks);results={};state_path=EV/'restore.json';state=json.loads(state_path.read_text()) if state_path.exists() else {}
for mp in ['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual']:
 assert level.load_level(mp);cp='/Game/RoadToF1/Checkpoints/'+mp.rsplit('/',1)[-1]+'_BeforeClearance'
 if not E.does_asset_exist(cp):copy=E.duplicate_asset(mp,cp);assert copy and E.save_loaded_asset(copy)
 changed=[];snapshot={};labels={a.get_actor_label():a for a in actors.get_all_level_actors()}
 for entry in g['filtered']:
  label='DK_'+entry['source_object'];a=labels[label];c=a.static_mesh_component;old=c.static_mesh;new=u.load_asset(BASE+'/Meshes/'+entry['mesh']);assert new
  snapshot[label]={'mesh':old.get_path_name(),'collision_profile':str(c.get_collision_profile_name()),'actor_collision':a.get_actor_enable_collision()}
  materials=[c.get_material(i) for i in range(c.get_num_materials())];profile=c.get_collision_profile_name();mode=c.get_collision_enabled()
  # Retain the original asset-level collision type on the filtered copy.
  new.get_editor_property('body_setup').set_editor_property('collision_trace_flag',old.get_editor_property('body_setup').get_editor_property('collision_trace_flag'))
  for i in range(new.get_num_sections(0)):
   if i<len(materials):new.set_material(i,old.get_material(i))
  E.save_loaded_asset(new);c.set_static_mesh(new)
  for i,m in enumerate(materials):c.set_material(i,m)
  c.set_collision_profile_name(profile);c.set_collision_enabled(mode);changed.append(label)
 base=labels.get('DK_14 Timing gantry signs and pit furniture | red')
 if base:
  snapshot[base.get_actor_label()]={'visible':base.static_mesh_component.is_visible(),'actor_collision':base.get_actor_enable_collision()};base.set_actor_hidden_in_game(True);base.set_actor_enable_collision(False);base.static_mesh_component.set_visibility(False,True);base.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);base.set_folder_path('_Hidden_TrackClutter');changed.append(base.get_actor_label())
 ft=u.load_asset('/Game/RoadToF1/DesertVisual/Instancing/FT_SM_DV_PitSignPod')
 if ft:u.InstancedFoliageActor.remove_all_instances(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),ft)
 if mp not in state:state[mp]={'checkpoint':cp,'actors':snapshot,'removed_instance_type':ft.get_path_name() if ft else None}
 state_path.write_text(json.dumps(state,indent=2));saved=level.save_current_level();results[mp]={'saved':saved,'changed':changed,'checkpoint':cp}
for p,h in protected.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
(EV/'applied.json').write_text(json.dumps({'maps':results,'protected_asset_hashes':protected,'removed':'13 pit-sign bases, their boards/posts, replacement sign pods, and the one booth at UE (-4500,-2000) cm','preserved':'Other two booths, gantry, paddock, track, parked kart hiding, lighting, route markings and gameplay'},indent=2))
assert all(x['saved'] for x in results.values()),'Map is locked by the running Unreal preview/editor; release it and rerun.'
u.log('PICTURED_TRACK_OBSTACLES_REMOVED')

"""Save twenty real spawn actors and relocate only the approved start infrastructure."""
import unreal as u,json,math
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/Grid20';EV=ROOT/'Evidence/Grid20';BASE='/Game/RoadToF1/Grid20';g=json.loads((ART/'layout.json').read_text());E=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
tasks=[]
for ent in g['assets']:
 if E.does_asset_exist(BASE+'/Meshes/'+ent['name']):continue
 task=u.AssetImportTask();task.filename=str(ART/'Meshes'/(ent['name']+'.fbx'));task.destination_path=BASE+'/Meshes';task.automated=True;task.save=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.set_editor_property('combine_meshes',True);o.static_mesh_import_data.set_editor_property('auto_generate_collision',False);o.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False);task.options=o;tasks.append(task)
T.import_asset_tasks(tasks);white=u.load_asset('/Game/RoadToF1/DesertVisual/Materials/MI_DV_white');black=u.load_asset('/Game/RoadToF1/DesertKarting/Materials/M_DK_dark');assert white and black
meshes={}
for ent in g['assets']:
 m=u.load_asset(BASE+'/Meshes/'+ent['name']);assert m
 for i,name in enumerate(ent['materials']):m.set_material(i,black if name=='Black' else white)
 E.save_loaded_asset(m);meshes[ent['name']]=m
report={};fx,fy,fz=g['finish_cm'];angle=g['finish_yaw_deg'];c=math.cos(math.radians(angle));s=math.sin(math.radians(angle));tx=fx-(c*-1800-s*-150);ty=fy-(s*-1800+c*-150)
for name in ['DesertKarting','DesertKarting_Visual']:
 mp='/Game/RoadToF1/Maps/'+name;assert L.load_level(mp);cp='/Game/RoadToF1/Checkpoints/'+name+'_BeforeGrid20'
 if not E.does_asset_exist(cp):copy=E.duplicate_asset(mp,cp);assert copy and E.save_loaded_asset(copy)
 labels={a.get_actor_label():a for a in A.get_all_level_actors()};oldfinish=labels.get('RR_SM_Route_Finish');assert oldfinish
 def hide(a):
  a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False);a.set_folder_path('_Hidden_ReplacedGrid')
  if isinstance(a,u.StaticMeshActor):a.static_mesh_component.set_visibility(False,True);a.static_mesh_component.set_collision_profile_name('NoCollision')
 for label in ['RR_SM_Route_Finish','DK_03 Infield lawns and pit lane | white']:
  if label in labels:hide(labels[label])
 original=labels['DK_14 Timing gantry signs and pit furniture | white'];cm=original.static_mesh_component;old=cm.static_mesh;new=meshes['SM_Grid20_RetainedBooths'];new.get_editor_property('body_setup').set_editor_property('collision_trace_flag',old.get_editor_property('body_setup').get_editor_property('collision_trace_flag'));E.save_loaded_asset(new);mat=cm.get_material(0);cm.set_static_mesh(new);cm.set_material(0,mat)
 for label in ['DK_14 Timing gantry signs and pit furniture | metal','DK_14 Timing gantry signs and pit furniture | dark','DK_DESERT KARTING']:
  if label in labels:labels[label].set_actor_location(u.Vector(tx,ty,0),False,False);labels[label].set_actor_rotation(u.Rotator(yaw=angle),False)
 def visual(label,mesh):
  a=labels.get(label) or A.spawn_actor_from_class(u.StaticMeshActor,u.Vector());a.set_actor_label(label);a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('NoCollision');a.set_actor_enable_collision(False);a.set_folder_path('Grid20/Markings');return a
 for label,mesh in [('Grid20_Boxes','SM_Grid20_BoxPaint'),('Grid20_Numbers','SM_Grid20_Numbers'),('Grid20_StartFinish','SM_Grid20_Finish')]:
  a=visual(label,meshes[mesh]);a.tags=['Grid20']+(['GridFinish'] if 'StartFinish' in label else [])
 beam=visual('Grid20_RelocatedOriginalBeam',meshes['SM_Grid20_OriginalBeam']);beam.static_mesh_component.set_material(0,mat);beam.set_actor_location(u.Vector(tx,ty,0),False,False);beam.set_actor_rotation(u.Rotator(yaw=angle),False);beam.set_folder_path('Grid20/Gantry')
 display=next(a for a in A.get_all_level_actors() if isinstance(a,u.RaceStartGantry));display.set_actor_location(u.Vector(fx-40*c,fy-40*s,0),False,False);display.set_actor_rotation(u.Rotator(yaw=angle),False);display.refresh_display()
 for a in A.get_all_level_actors():
  if isinstance(a,u.PlayerStart) and not isinstance(a,u.GridStartSlot):a.tags=[str(t) for t in a.tags if str(t)!='RaceGridStart'];a.set_folder_path('_Hidden_LegacyPlayerStarts')
 for slot in g['slots']:
  label='Grid20_Slot_%02d'%slot['number'];a=labels.get(label) or A.spawn_actor_from_class(u.GridStartSlot,u.Vector());a.set_actor_label(label);a.set_editor_property('position_number',slot['number']);a.set_actor_location(u.Vector(*slot['location_cm']),False,False);a.set_actor_rotation(u.Rotator(yaw=slot['yaw_deg']),False);a.set_actor_enable_collision(False);a.set_folder_path('Grid20/StartSlots');a.tags=['RaceGridSlot']+(['RaceGridStart'] if slot['number']==1 else [])
 mode=W.get_editor_world().get_world_settings().get_editor_property('default_game_mode');assert mode and isinstance(u.get_default_object(mode),u.ProofGameMode),'Current game mode must extend the existing ProofGameMode; do not replace a custom controller'
 saved=L.save_current_level();report[name]={'saved':saved,'slots':20,'pole_cm':g['slots'][0]['location_cm'],'finish_cm':g['finish_cm'],'finish_yaw':angle,'checkpoint':cp,'existing_mode_preserved':mode.get_path_name(),'participants_auto_spawned':0}
(EV/'implementation.json').write_text(json.dumps(report,indent=2));assert all(x['saved'] for x in report.values())

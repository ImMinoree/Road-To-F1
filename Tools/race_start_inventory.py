import unreal as u,json
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve();ev=root/'Evidence/RaceStart';ev.mkdir(parents=True,exist_ok=True)
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem);out={}
for mp in ['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual']:
 assert L.load_level(mp);world=W.get_editor_world();d={'game_mode':str(world.get_world_settings().get_editor_property('default_game_mode')),'actors':[]}
 for a in A.get_all_level_actors():
  label=a.get_actor_label()
  if isinstance(a,u.PlayerStart) or label.startswith(('DK_14 ','RR_')):
   p=a.get_actor_location();r=a.get_actor_rotation();item={'label':label,'class':a.get_class().get_name(),'location':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll]}
   if isinstance(a,u.StaticMeshActor):
    c=a.static_mesh_component;item.update(mesh=c.static_mesh.get_path_name(),visible=c.is_visible(),collision=a.get_actor_enable_collision());origin,extent=a.get_actor_bounds(False);item.update(bounds_center=[origin.x,origin.y,origin.z],bounds_extent=[extent.x,extent.y,extent.z])
   d['actors'].append(item)
 out[mp]=d
(ev/'before.json').write_text(json.dumps(out,indent=2))

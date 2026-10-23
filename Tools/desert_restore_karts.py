"""Explicit opt-in restoration: execute in Unreal Python to show retained kart groups."""
import unreal as u
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
for path in ['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual']:
 assert level.load_level(path)
 for a in actors.get_all_level_actors():
  if 'DV_RestoreKart' in [str(t) for t in a.tags]:
   a.set_actor_hidden_in_game(False);a.set_folder_path('Restored_Karts')
   for c in a.get_components_by_class(u.PrimitiveComponent):c.set_visibility(True,True)
 assert level.save_current_level()
u.log('Original kart assets restored in DesertKarting and its visual variant. Gameplay code unchanged.')

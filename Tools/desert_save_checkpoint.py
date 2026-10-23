"""Ensure the restore checkpoint is serialized as a real map on disk."""
import unreal as u
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();CHECK='/Game/RoadToF1/Checkpoints/DesertKarting_BeforeVisual';E=u.EditorAssetLibrary
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
if not E.does_asset_exist(CHECK):assert E.duplicate_asset('/Game/RoadToF1/Maps/DesertKarting',CHECK)
assert level.load_level(CHECK)
restored=[]
for a in actors.get_all_level_actors():
 if 'DV_RestoreKart' in [str(t) for t in a.tags]:
  a.set_actor_hidden_in_game(False);a.set_folder_path('');a.tags=[t for t in a.tags if str(t)!='DV_RestoreKart']
  for c in a.get_components_by_class(u.PrimitiveComponent):c.set_visibility(True,True)
  restored.append(a.get_actor_label())
assert len(restored)==8,restored
assert level.save_current_level();assert (ROOT/'Content/RoadToF1/Checkpoints/DesertKarting_BeforeVisual.umap').is_file()
u.log('RESTORE_CHECKPOINT_SAVED_WITH_8_ORIGINAL_KART_GROUPS')

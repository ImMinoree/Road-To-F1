"""Save a separate camera-only review map; never modify the playable map."""
import json
from pathlib import Path
import unreal
root = Path(__file__).resolve().parents[1]
world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/RoadToF1/SouthGarda_KartRace')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    if isinstance(a, unreal.CameraActor):
        a.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.DISABLED)
gate = json.loads((root / 'Art/KartLab/exports/manifest.json').read_text())['gates'][10]
target = unreal.Vector(*gate['location'])
location = target + unreal.Vector(-700, -1600, 1000)
camera = actors.spawn_actor_from_class(unreal.CameraActor, location, unreal.MathLibrary.find_look_at_rotation(location, target))
camera.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
camera.camera_component.set_editor_property('field_of_view', 75)
assert unreal.EditorLoadingAndSavingUtils.save_map(world, '/Game/RoadToF1/Validation/CornerReview')

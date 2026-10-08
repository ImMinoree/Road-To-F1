"""Save a separate close-up camera map; retain the playable map unchanged."""
import json
from pathlib import Path
import unreal
root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'Art/KartLab/exports/manifest.json').read_text())
world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/RoadToF1/SouthGarda_KartRace')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    if isinstance(a, unreal.CameraActor): a.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.DISABLED)
slot = data['grid'][19]
rotation = unreal.Rotator(pitch=0, yaw=slot['yaw'], roll=0)
p = unreal.Vector(*slot['location'])
forward = unreal.MathLibrary.get_forward_vector(rotation)
right = unreal.MathLibrary.get_right_vector(rotation)
location = p + forward * 230 - right * 230 + unreal.Vector(0, 0, 150)
target = p + unreal.Vector(0, 0, 35)
camera = actors.spawn_actor_from_class(unreal.CameraActor, location, unreal.MathLibrary.find_look_at_rotation(location, target))
camera.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
camera.camera_component.field_of_view = 43
assert unreal.EditorLoadingAndSavingUtils.save_map(world, '/Game/RoadToF1/Validation/DriverReview')

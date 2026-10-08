"""Create the playable map from art preview after the new native classes are built."""
import json
from pathlib import Path
import unreal
root = Path(__file__).resolve().parents[1]
target = '/Game/RoadToF1/SouthGarda_KartRace'
if unreal.EditorAssetLibrary.does_asset_exist(target):
    raise RuntimeError('Existing playable map preserved; inspect it before changing.')
manifest = json.loads((root / 'Art/KartLab/exports/manifest.json').read_text())
world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/RoadToF1/SouthGarda_ArtPreview')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
gate_class = unreal.load_class(None, '/Script/RoadToF1.RaceTrackGate')
game_mode = unreal.load_class(None, '/Script/RoadToF1.KartGameMode')
assert gate_class and game_mode, 'Build native kart classes first'
start_gate = manifest['gates'][0]
rotation = unreal.Rotator(pitch=0, yaw=start_gate['yaw'], roll=0)
start_location = unreal.Vector(*start_gate['location']) - unreal.MathLibrary.get_forward_vector(rotation) * 850
start_location.z = 24.5
for actor in actors.get_all_level_actors():
    if isinstance(actor, unreal.CameraActor):
        actor.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.DISABLED)
    if isinstance(actor, unreal.PlayerStart):
        actor.set_actor_location(start_location, False, False)
        actor.set_actor_rotation(rotation, False)
    if actor.get_actor_label().startswith('SG_Kart_'):
        actor.set_actor_location(unreal.Vector(-4500, -6000, 20), False, False)
for entry in manifest['gates']:
    actor = actors.spawn_actor_from_class(gate_class, unreal.Vector(*entry['location']), unreal.Rotator(pitch=0, yaw=entry['yaw'], roll=0))
    actor.set_editor_property('order', entry['order'])
    actor.set_actor_label('Race_START_FINISH' if entry['order'] == 0 else 'Race_CP_%02d' % entry['order'])
    actor.set_folder_path('Race/OrderedGates')
world.get_world_settings().set_editor_property('default_game_mode', game_mode)
assert unreal.EditorLoadingAndSavingUtils.save_map(world, target), 'Map save failed'
report = {'map': target, 'gameMode': game_mode.get_path_name(), 'gates': manifest['gates'], 'playerStart': [start_location.x, start_location.y, start_location.z], 'status': 'Saved; requires gameplay verification.'}
(root / 'TestResults/SouthGardaGameplay').mkdir(parents=True, exist_ok=True)
(root / 'TestResults/SouthGardaGameplay/map-report.json').write_text(json.dumps(report, indent=2))
unreal.log('ROADTOF1_KART_MAP=' + json.dumps(report))

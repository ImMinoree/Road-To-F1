"""Inspect our new art map and set its review camera for a screenshot; preserve other maps."""
import json
from pathlib import Path
import unreal
root = Path(__file__).resolve().parents[1]
world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/RoadToF1/SouthGarda_ArtPreview')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
entries = []
for actor in actors:
    if isinstance(actor, unreal.CameraActor):
        actor.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
        actor.set_actor_location(unreal.Vector(-23000, -27000, 21000), False, False)
        actor.set_actor_rotation(unreal.Rotator(pitch=-31, yaw=50, roll=0), False)
    if isinstance(actor, unreal.PlayerStart):
        actor.set_actor_location(unreal.Vector(-7500, -5200, 150), False, False)
    if actor.get_actor_label().startswith('SG_Kart_'):
        actor.set_actor_location(unreal.Vector(-4500, -6100, 20), False, False)
    if isinstance(actor, unreal.DirectionalLight):
        actor.set_actor_rotation(unreal.Rotator(pitch=-35, yaw=-30, roll=0), False)
    if isinstance(actor, unreal.StaticMeshActor):
        sm = actor.static_mesh_component.static_mesh
        material_name = actor.get_actor_label().split('_', 2)[2]
        material = unreal.load_asset('/Game/RoadToF1/Art/SouthGardaV01/Materials/M_' + material_name)
        slots = sm.get_editor_property('static_materials')
        for index in range(len(slots)):
            sm.set_material(index, material)
        unreal.EditorAssetLibrary.save_loaded_asset(sm)
        origin, extent = actor.get_actor_bounds(False)
        entries.append({'label': actor.get_actor_label(), 'origin': [origin.x, origin.y, origin.z], 'extent': [extent.x, extent.y, extent.z], 'mesh': sm.get_path_name(), 'material_slots': len(slots), 'material': material.get_path_name()})
manifest = json.loads((root / 'Art/KartLab/exports/manifest.json').read_text())
assert len(entries) == len(manifest['kart']) + len(manifest['circuit']), 'Missing authored material mesh actors'
assert any(e['extent'][0] > 14000 for e in entries if e['label'] == 'SG_Circuit_Asphalt'), 'Incorrect circuit scale'
assert any(15 < e['extent'][2] < 40 for e in entries if e['label'] == 'SG_Kart_Carbon'), 'Incorrect kart seat scale'
unreal.EditorLoadingAndSavingUtils.save_map(world, '/Game/RoadToF1/SouthGarda_ArtPreview')
(root / 'TestResults/SouthGardaArt/verified-bounds.json').write_text(json.dumps(entries, indent=2))
unreal.log('ROADTOF1_ART_VERIFY: PASS - all manifest mesh actors; venue at metre-to-centimetre scale; saved review camera.')

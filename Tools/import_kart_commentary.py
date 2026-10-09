from pathlib import Path
import unreal
root = Path(__file__).resolve().parents[1]
dest = '/Game/RoadToF1/Audio/CommentaryV01'
tools = unreal.AssetToolsHelpers.get_asset_tools()
clips = {}
for name in ['Start', 'Lap', 'Overtake', 'Incident', 'Finish']:
    path = dest + '/' + name
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        task = unreal.AssetImportTask()
        task.filename = str(root / 'Art/Audio/Commentary' / (name + '.wav'))
        task.destination_path = dest
        task.destination_name = name
        task.automated = True
        task.save = True
        tools.import_asset_tasks([task])
    clip = unreal.load_asset(path)
    assert isinstance(clip, unreal.SoundWave), path
    clips[name] = clip
world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/RoadToF1/SouthGarda_KartRace')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
cls = unreal.load_class(None, '/Script/RoadToF1.KartRaceDirector')
director = next(a for a in actors.get_all_level_actors() if a.get_class() == cls)
director.set_editor_property('commentary_clips', clips)
assert unreal.EditorLoadingAndSavingUtils.save_map(world, '/Game/RoadToF1/SouthGarda_KartRace')
unreal.log('ROADTOF1_AUDIO: five commentary clips imported and assigned to race director.')

"""Persist grass-free recovery maps without altering the saved playable maps."""
import unreal as u
L=u.get_editor_subsystem(u.LevelEditorSubsystem);W=u.get_editor_subsystem(u.UnrealEditorSubsystem);E=u.EditorAssetLibrary
for name in ['DesertKarting','DesertKarting_Visual']:
    path='/Game/RoadToF1/Maps/'+name;assert L.load_level(path)
    cp='/Game/RoadToF1/Checkpoints/'+name+'_BeforeInfieldGrass'
    if E.does_asset_exist(cp):continue
    for i in range(3):
        ft=u.load_asset('/Game/RoadToF1/InfieldGrass/Foliage/FT_SM_InfieldGrass_%02d'%i)
        u.InstancedFoliageActor.remove_all_instances(W.get_editor_world(),ft)
    checkpoint=E.duplicate_asset(path,cp);assert checkpoint and E.save_loaded_asset(checkpoint)
    # Discard only the transient grass removal; the disk map retains its grass.
    assert L.load_level(path)

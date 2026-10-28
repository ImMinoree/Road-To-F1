"""Remove only this task's placed tire instances; preserve all other level edits."""
import unreal as u
L=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
for color in ['Black','Red']:
 ft=u.load_asset('/Game/RoadToF1/Trackside/TireBarriers/Instancing/FT_TireBarrier_'+color)
 if ft:u.InstancedFoliageActor.remove_all_instances(world,ft)
assert L.save_current_level()

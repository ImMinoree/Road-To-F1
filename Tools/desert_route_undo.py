"""Remove only this pass's paint and signs; leave hidden karts safely non-colliding."""
import unreal as u
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);E=u.EditorAssetLibrary
for mp in ['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual']:
 assert level.load_level(mp)
 for a in list(actors.get_all_level_actors()):
  if 'RouteReadability' in [str(t) for t in a.tags]:actors.destroy_actor(a)
 f=u.load_asset('/Game/RoadToF1/DesertRoute/Instancing/FT_RouteArrows')
 if f:u.InstancedFoliageActor.remove_all_instances(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),f)
 assert level.save_current_level()
u.log('Route readability overlay removed; source assets unchanged and parked karts remain hidden/non-colliding.')

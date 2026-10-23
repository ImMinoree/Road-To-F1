"""Persist nonblocking paint/sign actor profiles, avoiding static-mesh default collision resets."""
import unreal as u
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
for mp in ['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual']:
 assert level.load_level(mp)
 for a in actors.get_all_level_actors():
  if 'RouteReadability' in [str(t) for t in a.tags]:
   a.set_actor_enable_collision(False)
   for c in a.get_components_by_class(u.PrimitiveComponent):c.set_collision_profile_name('NoCollision');c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
 assert level.save_current_level()
u.log('ROUTE_PAINT_AND_SIGNS_EXPLICITLY_NONBLOCKING')

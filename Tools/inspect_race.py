"""Read-only inspection of the saved prototype; run with Unreal Python commandlet."""
import json
import unreal

world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/RoadToF1/RacePrototype')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
result = []
for actor in actors:
    location = actor.get_actor_location()
    entry = {'name': actor.get_name(), 'label': actor.get_actor_label(),
             'class': actor.get_class().get_path_name(),
             'location': [location.x, location.y, location.z],
             'rotation': str(actor.get_actor_rotation())}
    if 'StartFinish' in actor.get_class().get_name():
        entry['properties'] = {}
        for name in ['CompletedLaps']:
            try:
                entry['properties'][name] = actor.get_editor_property(name)
            except Exception:
                entry['properties'][name] = 'not present'
        entry['boxes'] = []
        for box in actor.get_components_by_class(unreal.BoxComponent):
            loc = box.get_world_location()
            ext = box.get_editor_property('box_extent')
            entry['boxes'].append({'name': box.get_name(), 'location': [loc.x, loc.y, loc.z],
                                   'extent': [ext.x, ext.y, ext.z], 'rotation': str(box.get_world_rotation())})
    result.append(entry)
    for component in actor.get_components_by_class(unreal.LandscapeSplinesComponent):
        for mesh in component.get_spline_mesh_components():
            transform = mesh.get_world_transform()
            start = transform.transform_location(mesh.get_start_position())
            end = transform.transform_location(mesh.get_end_position())
            unreal.log('ROADTOF1_SPLINE=' + json.dumps({'name': mesh.get_name(), 'start': [start.x, start.y, start.z], 'end': [end.x, end.y, end.z]}))
unreal.log('ROADTOF1_INSPECTION=' + json.dumps(result))

"""Read-only live level inventory and aerial capture; no asset or map saves."""
import hashlib, json, time, traceback
from pathlib import Path
import unreal as u

root=Path(u.Paths.project_dir()).resolve()
ev=root/'Evidence/ExpandedTireBarriers';ev.mkdir(parents=True,exist_ok=True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
u.EditorPythonScripting.set_keep_python_script_alive(True)
inventory={'actors':[],'tire_components':[],'tire_assets':{},'protected':{}}
for folder in ['Source','Config','Content/RoadToF1/Trackside/TireBarriers']:
    for p in (root/folder).rglob('*'):
        if p.is_file():inventory['protected'][str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
for p in (root/'Content/RoadToF1/Maps').glob('*.umap'):
    inventory['protected'][str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
for a in actors.get_all_level_actors():
    p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
    item={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),
          'transform':[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z],
          'collision':a.get_actor_enable_collision(),'meshes':[]}
    if isinstance(a,u.Light):
        c=a.light_component;color=c.get_editor_property('light_color')
        item['light']=[c.get_editor_property('intensity'),color.r,color.g,color.b,color.a]
    for c in a.get_components_by_class(u.StaticMeshComponent):
        if not c.static_mesh:continue
        mesh=c.static_mesh;path=mesh.get_path_name();bounds=mesh.get_bounding_box()
        item['meshes'].append({'component':c.get_name(),'asset':path,'bounds_min':list(bounds.min.to_tuple()),
                              'bounds_max':list(bounds.max.to_tuple()),'collision':str(c.get_collision_enabled()),
                              'world_transform':str(c.get_world_transform())})
        if '/Trackside/TireBarriers/' in path and isinstance(c,u.InstancedStaticMeshComponent):
            transforms=[]
            for i in range(c.get_instance_count()):
                t=c.get_instance_transform(i,world_space=True);p=t.translation;r=t.rotation.rotator();s=t.scale3d
                transforms.append({'location':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll],'scale':[s.x,s.y,s.z]})
            inventory['tire_components'].append({'actor':a.get_name(),'component':c.get_name(),'mesh':path,
                                                'instances':transforms,'collision':str(c.get_collision_enabled())})
            tools=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
            inventory['tire_assets'][path]={'lods':tools.get_lod_count(mesh),'convex_hulls':tools.get_convex_collision_count(mesh),
                                           'min':list(bounds.min.to_tuple()),'max':list(bounds.max.to_tuple())}
    inventory['actors'].append(item)
(ev/'inventory_before.json').write_text(json.dumps(inventory,indent=2))
camera=actors.spawn_actor_from_class(u.CameraActor,u.Vector(2925,-10350,40000),u.Rotator(pitch=-90))
cc=camera.camera_component
cc.set_editor_property('projection_mode',u.CameraProjectionMode.ORTHOGRAPHIC)
cc.set_editor_property('ortho_width',31000)
cc.set_editor_property('aspect_ratio',1.2)
cc.set_editor_property('constrain_aspect_ratio',True)
cc.set_editor_property('auto_calculate_ortho_planes',False)
cc.set_editor_property('ortho_near_clip_plane',1)
cc.set_editor_property('ortho_far_clip_plane',100000)
state={'time':time.monotonic(),'task':None}
def tick(dt):
    try:
        if state['task'] is None and time.monotonic()-state['time']>5:
            state['task']=u.AutomationLibrary.take_high_res_screenshot(2400,2000,str(ev/'aerial_before.png'),camera=camera,delay=1)
        elif state['task'] is not None and state['task'].is_task_done():
            actors.destroy_actor(camera)
            u.unregister_slate_post_tick_callback(handle)
            u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
    except Exception:
        (ev/'probe_error.txt').write_text(traceback.format_exc())
        u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
handle=u.register_slate_post_tick_callback(tick)

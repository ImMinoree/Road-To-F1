"""Read-only combined-project PIE inventory. Does not save maps/assets or supply driving input."""
import unreal as u,json,time,traceback,hashlib
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve();ev=root/'Evidence/NoDrift';ev.mkdir(parents=True,exist_ok=True)
u.EditorPythonScripting.set_keep_python_script_alive(True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
protected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'Content/RoadToF1/Maps').glob('*.umap')}
assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
state={'start':time.monotonic(),'started':False,'finished':None,'busy':False}
def tick(dt):
    if state['busy']:return
    state['busy']=True
    try:
        if time.monotonic()-state['start']>120:raise RuntimeError('Combined audit timeout')
        if not state['started'] and time.monotonic()-state['start']>4:
            state['started']=True;level.editor_request_begin_play()
        if not level.is_in_play_in_editor():return
        world=editor.get_game_world()
        if not world:return
        if u.GameplayStatics.get_time_seconds(world)<3:return
        if state['finished'] is not None:
            if time.monotonic()-state['finished']>2:
                level.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
            return
        pawn=u.GameplayStatics.get_player_pawn(world,0)
        if not pawn:return
        gm=u.GameplayStatics.get_game_mode(world);camera=pawn.get_component_by_class(u.CameraComponent)
        visuals=pawn.get_component_by_class(u.LocalKartDriverVisuals);dynamics=pawn.get_component_by_class(u.KartTireDynamics)
        sk=pawn.get_components_by_class(u.SkeletalMeshComponent);static=pawn.get_components_by_class(u.StaticMeshComponent)
        player_meshes=[{'component':c.get_name(),'asset':c.get_skinned_asset().get_path_name() if c.get_skinned_asset() else None,'visible':c.is_visible()} for c in sk]
        player_static=[{'component':c.get_name(),'asset':c.static_mesh.get_path_name() if c.static_mesh else None,'visible':c.is_visible()} for c in static]
        grass=0;floodlights=0
        for actor in u.GameplayStatics.get_all_actors_of_class(world,u.Actor):
            if actor.get_actor_label().startswith('GH_FloodPool_'):floodlights+=1
            for comp in actor.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
                if comp.static_mesh and '/InfieldGrass/' in comp.static_mesh.get_path_name():grass+=comp.get_instance_count()
        pos=camera.get_editor_property('relative_location');rot=camera.get_editor_property('relative_rotation')
        result={'actual_pie':True,'map':world.get_path_name(),'game_mode':gm.get_class().get_path_name(),'player_class':pawn.get_class().get_path_name(),
                'pawns':len(u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn)),
                'ai_opponents':len([p for p in u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn) if p.get_editor_property('racing_ai')]),
                'grid_slots':len(u.GameplayStatics.get_all_actors_of_class(world,u.GridStartSlot)),
                'start_gantries':len(u.GameplayStatics.get_all_actors_of_class(world,u.RaceStartGantry)),
                'grass_instances':grass,'aimed_floodlight_actors':floodlights,
                'cockpit_active':visuals.is_first_person_active(),'skeletal_meshes':player_meshes,'static_meshes':player_static,
                'camera':{'position_cm':[pos.x,pos.y,pos.z],'rotation':[rot.pitch,rot.yaw,rot.roll],'fov':camera.field_of_view},
                'all_kart_tire_dynamics':[p.get_editor_property('use_tire_dynamics') for p in u.GameplayStatics.get_all_actors_of_class(world,u.ProofPawn)],'tire_dynamics_enabled':pawn.get_editor_property('use_tire_dynamics'),'dynamics_component':dynamics is not None,
                'surface_effects_component':pawn.get_component_by_class(u.KartSurfaceFX) is not None,
                'speed_blendables':len(camera.post_process_settings.weighted_blendables.array),
                'maps_unchanged':protected=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'Content/RoadToF1/Maps').glob('*.umap')}}
        assert not any(result['all_kart_tire_dynamics']) and result['pawns']==5 and result['ai_opponents']==4 and result['cockpit_active'] and result['maps_unchanged'],result
        (ev/'runtime_inventory.json').write_text(json.dumps(result,indent=2));state['finished']=time.monotonic()
    except Exception:
        (ev/'audit_error.txt').write_text(traceback.format_exc());u.log_error(traceback.format_exc());u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
    finally:state['busy']=False
handle=u.register_slate_post_tick_callback(tick)


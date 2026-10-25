"""Import the V5 chassis, save/reload the existing visual map, and capture genuine PIE."""
import unreal as u, json, time, traceback
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve(); EV=ROOT/'Evidence/Integration';EV.mkdir(exist_ok=True)
u.EditorPythonScripting.set_keep_python_script_alive(True)
OUT='/Game/RoadToF1/PlayerVisuals/FirstPerson'
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
tools=u.AssetToolsHelpers.get_asset_tools()
task=u.AssetImportTask();task.filename=str(ROOT/'Art/PlayerVisuals/FirstPerson/Exports/SM_PlayerKartChassis.fbx')
task.destination_path=OUT;task.destination_name='SM_PlayerKartChassis';task.automated=True;task.save=True;task.replace_existing=True
opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
opts.import_materials=False;opts.import_textures=False;opts.static_mesh_import_data.combine_meshes=True
opts.static_mesh_import_data.auto_generate_collision=False;opts.static_mesh_import_data.convert_scene=True;opts.static_mesh_import_data.convert_scene_unit=True
task.options=opts;tools.import_asset_tasks([task]);mesh=u.load_asset(OUT+'/SM_PlayerKartChassis');assert mesh
source=json.loads((EV/'chassis_export.json').read_text());ME=u.MaterialEditingLibrary
textures={}
for data in source['materials'].values():
    for channel,name in data.get('textures',{}).items():
        if name in textures:continue
        file=ROOT/'Art/DesertKarting/Kart/Textures'/(name+'.png')
        assert file.is_file(),file
        t=u.AssetImportTask();t.filename=str(file);t.destination_path=OUT+'/ChassisMaterials';t.automated=True;t.save=True;t.replace_existing=True
        tools.import_asset_tasks([t]);tex=u.load_asset(t.imported_object_paths[0]);textures[name]=tex
        tex.set_editor_property('srgb',channel=='BaseColor')
        if channel=='Normal':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
        u.EditorAssetLibrary.save_loaded_asset(tex)
for i,slot in enumerate(mesh.get_editor_property('static_materials')):
    name=str(slot.material_slot_name); data=source['materials'].get(name)
    assert data, name
    path=OUT+'/ChassisMaterials';mat=u.load_asset(path+'/'+name)
    if not mat:mat=tools.create_asset(name,path,u.Material,u.MaterialFactoryNew())
    ME.delete_all_material_expressions(mat)
    color=ME.create_material_expression(mat,u.MaterialExpressionConstant3Vector,-300,0);color.constant=u.LinearColor(*data['color']);ME.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
    for j,(value,prop) in enumerate([(data['roughness'],u.MaterialProperty.MP_ROUGHNESS),(data['metallic'],u.MaterialProperty.MP_METALLIC)]):
        node=ME.create_material_expression(mat,u.MaterialExpressionConstant,-300,150+j*100);node.r=value;ME.connect_material_property(node,'',prop)
    for channel,name in data.get('textures',{}).items():
        tex=ME.create_material_expression(mat,u.MaterialExpressionTextureSample,-600,0);tex.texture=textures[name]
        tex.sampler_type=u.MaterialSamplerType.SAMPLERTYPE_NORMAL if channel=='Normal' else (u.MaterialSamplerType.SAMPLERTYPE_COLOR if channel=='BaseColor' else u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
        prop={'BaseColor':u.MaterialProperty.MP_BASE_COLOR,'Roughness':u.MaterialProperty.MP_ROUGHNESS,'Metallic':u.MaterialProperty.MP_METALLIC,'Normal':u.MaterialProperty.MP_NORMAL}[channel]
        ME.connect_material_property(tex,'RGB' if channel in ['BaseColor','Normal'] else 'R',prop)
    ME.recompile_material(mat);mesh.set_material(i,mat);u.EditorAssetLibrary.save_loaded_asset(mat)
u.EditorAssetLibrary.save_loaded_asset(mesh)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
MAP='/Game/RoadToF1/Maps/DesertKarting_Visual';assert level.load_level(MAP)
def snapshot():
    rows=[]
    for a in actors.get_all_level_actors():
        p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
        row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_path_name(),'transform':[round(v,5) for v in [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]],'tags':sorted(map(str,a.tags))}
        if isinstance(a,u.StaticMeshActor):
            c=a.static_mesh_component;row.update(mesh=c.static_mesh.get_path_name() if c.static_mesh else None,materials=[m.get_path_name() if m else None for m in c.get_materials()],collision=str(c.get_collision_enabled()))
        rows.append(row)
    return sorted(rows,key=lambda a:a['name'])
before=snapshot(); world=editor.get_editor_world();ws=world.get_world_settings();old_mode=str(ws.get_editor_property('default_game_mode'))
ws.set_editor_property('default_game_mode',u.ProofGameMode.static_class())
assert len([a for a in actors.get_all_level_actors() if isinstance(a,u.RaceStartGantry)])==1
assert len([a for a in actors.get_all_level_actors() if isinstance(a,u.GridStartSlot)])==20
assert not [a for a in actors.get_all_level_actors() if isinstance(a,u.ProofPawn)]
assert level.save_current_level();assert level.load_level('/Game/RoadToF1/Maps/DesertKarting');assert level.load_level(MAP)
after=snapshot()
(EV/'map_before.json').write_text(json.dumps(before,indent=2));(EV/'map_after.json').write_text(json.dumps(after,indent=2))
assert before==after,'Map actors changed during save/reload'
report={'map':MAP,'before_game_mode':old_mode,'game_mode':str(editor.get_editor_world().get_world_settings().get_editor_property('default_game_mode')),'actors_preserved':len(after),'save_reload_passed':True,'one_gantry':True,'grid_slots':20,'placed_pawns':0,'chassis':mesh.get_path_name(),'chassis_bounds':str(mesh.get_bounds())}
(EV/'map_validation.json').write_text(json.dumps(report,indent=2))
for cmd in ['sg.ViewDistanceQuality 3','sg.AntiAliasingQuality 3','sg.ShadowQuality 3','sg.GlobalIlluminationQuality 3','sg.ReflectionQuality 3','sg.TextureQuality 3','r.ScreenPercentage 100','t.MaxFPS 60']:
    u.SystemLibrary.execute_console_command(None,cmd)
state={'start':time.monotonic(),'wall':time.time(),'started':False,'finished':False,'end':None}
def tick(dt):
    try:
        if not state['started'] and time.monotonic()-state['start']>12:
            state['started']=True;level.editor_request_begin_play()
        if state['started'] and not state['finished'] and (EV/'driving_later.json').is_file() and (EV/'driving_later.json').stat().st_mtime>=state['wall']:
            assert level.is_in_play_in_editor(),'Capture was not PIE'
            state['finished']=True;state['end']=time.monotonic()
            (EV/'pie_confirmed.json').write_text(json.dumps({'is_in_play_in_editor':True,'completed':True}))
        if state['finished'] and time.monotonic()-state['end']>3:
            level.editor_request_end_play();u.unregister_slate_post_tick_callback(handle)
            u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
        elif time.monotonic()-state['start']>150:raise RuntimeError('PIE capture timed out')
    except Exception:
        (EV/'error.txt').write_text(traceback.format_exc());u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
handle=u.register_slate_post_tick_callback(tick)

"""Add seated driver assets, replace grid paint, and configure the saved race field."""
import json
from pathlib import Path
import unreal
root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'Art/KartLab/exports/manifest.json').read_text())
tools = unreal.AssetToolsHelpers.get_asset_tools()
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for entry in data['driver'] + [e for e in data['circuit'] if e['material'] == 'RoadPaint']:
    driver = entry in data['driver']
    dest = '/Game/RoadToF1/Art/' + ('DriversV01' if driver else 'SouthGardaV01')
    name = Path(entry['file']).stem
    task = unreal.AssetImportTask()
    task.filename = str(root / 'Art/KartLab/exports' / entry['file'])
    task.destination_path = dest + '/Meshes'
    task.destination_name = name
    task.automated = task.save = task.replace_existing = True
    ui = unreal.FbxImportUI()
    ui.automated_import_should_detect_type = False
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    ui.import_mesh = True
    ui.import_materials = ui.import_textures = False
    ui.static_mesh_import_data.combine_meshes = True
    ui.static_mesh_import_data.auto_generate_collision = False
    ui.static_mesh_import_data.convert_scene = False
    task.options = ui
    tools.import_asset_tasks([task])
    sm = unreal.load_asset(dest + '/Meshes/' + name)
    mat_path = dest + '/Materials/M_' + entry['material']
    mat = unreal.load_asset(mat_path) if unreal.EditorAssetLibrary.does_asset_exist(mat_path) else None
    if mat is None:
        mat = tools.create_asset('M_' + entry['material'], dest + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
        lib = unreal.MaterialEditingLibrary
        customizable = entry['material'] in ['Suit', 'SuitAccent', 'Helmet', 'Gloves']
        color = lib.create_material_expression(mat, unreal.MaterialExpressionVectorParameter if customizable else unreal.MaterialExpressionConstant3Vector, -300, 0)
        def linear(c): return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
        value = unreal.LinearColor(*(linear(c) for c in entry['color']), 1)
        if customizable:
            color.set_editor_property('parameter_name', 'LiveryColor')
            color.set_editor_property('default_value', value)
        else: color.constant = value
        lib.connect_material_property(color, '', unreal.MaterialProperty.MP_BASE_COLOR)
        for prop, value in [(unreal.MaterialProperty.MP_ROUGHNESS, entry['roughness']), (unreal.MaterialProperty.MP_METALLIC, entry['metalness'])]:
            node = lib.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 150)
            node.r = value
            lib.connect_material_property(node, '', prop)
        lib.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
    for slot in range(len(sm.get_editor_property('static_materials'))): sm.set_material(slot, mat)
    unreal.EditorAssetLibrary.save_loaded_asset(sm)

world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/RoadToF1/SouthGarda_KartRace')
all_actors = actors.get_all_level_actors()
director_class = unreal.load_class(None, '/Script/RoadToF1.KartRaceDirector')
assert director_class, 'Build the native race director first'
director = next((a for a in all_actors if a.get_class() == director_class), None)
if director is None:
    director = actors.spawn_actor_from_class(director_class, unreal.Vector())
    director.set_actor_label('Race_20KartField')
    director.set_folder_path('Race')
director.set_editor_property('route_points', [unreal.Vector(*p) for p in data['drivePath']])
transforms = [unreal.Transform(location=unreal.Vector(*p['location']), rotation=unreal.Rotator(pitch=0, yaw=p['yaw'], roll=0)) for p in data['grid']]
director.set_editor_property('grid', transforms)
for actor in all_actors:
    if isinstance(actor, unreal.PlayerStart): actor.set_actor_transform(transforms[19], False, False)
assert unreal.EditorLoadingAndSavingUtils.save_map(world, '/Game/RoadToF1/SouthGarda_KartRace')
unreal.log('ROADTOF1_DRIVER_AI: imported six driver parts; 20 grid slots; 19 runtime opponents.')

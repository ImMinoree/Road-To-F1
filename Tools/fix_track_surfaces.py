"""Reimport our revised surface meshes, retaining map actors and user edits."""
import json
from pathlib import Path
import unreal
root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'Art/KartLab/exports/manifest.json').read_text())
dest = '/Game/RoadToF1/Art/SouthGardaV01'
tools = unreal.AssetToolsHelpers.get_asset_tools()
changed = {'Asphalt', 'White', 'Kerb_blue', 'Rubber', 'Kerb_white', 'Kerb_blue_surface', 'RoadPaint'}
assets = {}
for entry in manifest['circuit']:
    if entry['material'] not in changed:
        continue
    task = unreal.AssetImportTask()
    task.filename = str(root / 'Art/KartLab/exports' / entry['file'])
    task.destination_path = dest + '/Meshes'
    task.destination_name = Path(entry['file']).stem
    task.automated = True
    task.replace_existing = True
    task.save = True
    options = unreal.FbxImportUI()
    options.set_editor_property('automated_import_should_detect_type', False)
    options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    options.import_mesh = True
    options.import_materials = False
    options.import_textures = False
    options.static_mesh_import_data.combine_meshes = True
    options.static_mesh_import_data.auto_generate_collision = False
    options.static_mesh_import_data.convert_scene = False
    task.options = options
    tools.import_asset_tasks([task])
    sm = unreal.load_asset(dest + '/Meshes/' + task.destination_name)
    assert isinstance(sm, unreal.StaticMesh), 'Failed surface import'
    material_path = dest + '/Materials/M_' + entry['material']
    mat = unreal.load_asset(material_path)
    if not mat:
        mat = tools.create_asset('M_' + entry['material'], dest + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
        lib = unreal.MaterialEditingLibrary
        color = lib.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
        def linear(c):
            return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
        color.constant = unreal.LinearColor(*(linear(c) for c in entry['color']), 1)
        lib.connect_material_property(color, '', unreal.MaterialProperty.MP_BASE_COLOR)
        roughness = lib.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 200)
        roughness.r = .85
        lib.connect_material_property(roughness, '', unreal.MaterialProperty.MP_ROUGHNESS)
        lib.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
    for index in range(len(sm.get_editor_property('static_materials'))):
        sm.set_material(index, mat)
    body = sm.get_editor_property('body_setup')
    if body:
        body.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(sm)
    assets[task.destination_name] = sm

actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for map_path in ['/Game/RoadToF1/SouthGarda_ArtPreview', '/Game/RoadToF1/SouthGarda_KartRace']:
    world = unreal.EditorLoadingAndSavingUtils.load_map(map_path)
    existing = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    for name, sm in assets.items():
        label = 'SG_' + name
        actor = existing.get(label)
        if actor is None:
            actor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector())
            actor.set_actor_label(label)
            actor.set_folder_path('SouthGarda/Environment')
        actor.static_mesh_component.set_static_mesh(sm)
        actor.static_mesh_component.set_collision_profile_name('NoCollision' if name in ['Circuit_RoadPaint', 'Circuit_Rubber', 'Circuit_Kerb_white', 'Circuit_Kerb_blue_surface'] else 'BlockAll')
    if map_path.endswith('SouthGarda_KartRace'):
        # Keep ordered gates and spawn aligned with the revised road. Preserve
        # every other actor, including user additions and scene transforms.
        for entry in manifest['gates']:
            label = 'Race_START_FINISH' if entry['order'] == 0 else 'Race_CP_%02d' % entry['order']
            actor = existing.get(label)
            assert actor, 'Missing existing gate: ' + label
            actor.set_actor_location(unreal.Vector(*entry['location']), False, False)
            actor.set_actor_rotation(unreal.Rotator(pitch=0, yaw=entry['yaw'], roll=0), False)
        first = manifest['gates'][0]
        rotation = unreal.Rotator(pitch=0, yaw=first['yaw'], roll=0)
        spawn = unreal.Vector(*first['location']) - unreal.MathLibrary.get_forward_vector(rotation) * 850
        spawn.z = 24.5
        for actor in existing.values():
            if isinstance(actor, unreal.PlayerStart):
                actor.set_actor_location(spawn, False, False)
                actor.set_actor_rotation(rotation, False)
    assert unreal.EditorLoadingAndSavingUtils.save_map(world, map_path)
unreal.log('ROADTOF1_SURFACE_FIX: PASS - flush, non-colliding markings; continuous kerbs; existing map actors preserved.')

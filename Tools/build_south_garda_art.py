"""Import the authored kart/circuit art into NEW assets only. Unreal Python commandlet."""
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / 'Art' / 'KartLab' / 'exports'
DEST = '/Game/RoadToF1/Art/SouthGardaV01'
MAP = '/Game/RoadToF1/SouthGarda_ArtPreview'
if unreal.EditorAssetLibrary.does_asset_exist(MAP):
    raise RuntimeError('Existing preview map preserved. Use a new version path before regenerating.')
manifest = json.loads((EXPORTS / 'manifest.json').read_text())
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)

def imported_mesh(entry):
    name = Path(entry['file']).stem
    path = DEST + '/Meshes/' + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError('Refusing to overwrite existing asset: ' + path)
    task = unreal.AssetImportTask()
    task.filename = str(EXPORTS / entry['file'])
    task.destination_path = DEST + '/Meshes'
    task.destination_name = name
    task.automated = True
    task.save = True
    task.replace_existing = False
    options = unreal.FbxImportUI()
    options.set_editor_property('automated_import_should_detect_type', False)
    options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)
    options.import_mesh = True
    options.import_materials = False
    options.import_textures = False
    options.static_mesh_import_data.set_editor_property('combine_meshes', True)
    options.static_mesh_import_data.set_editor_property('auto_generate_collision', False)
    options.static_mesh_import_data.set_editor_property('convert_scene', False)
    options.static_mesh_import_data.set_editor_property('import_uniform_scale', 1.0)
    task.options = options
    asset_tools.import_asset_tasks([task])
    loaded = unreal.load_asset(path)
    if not isinstance(loaded, unreal.StaticMesh):
        raise RuntimeError('Mesh import failed: ' + path + ' ' + str(task.imported_object_paths))
    return loaded

materials = {}
def create_material(entry):
    name = entry['material']
    if name in materials:
        return materials[name]
    path = DEST + '/Materials'
    if unreal.EditorAssetLibrary.does_asset_exist(path + '/M_' + name):
        raise RuntimeError('Existing material preserved: ' + name)
    mat = asset_tools.create_asset('M_' + name, path, unreal.Material, unreal.MaterialFactoryNew())
    lib = unreal.MaterialEditingLibrary
    color = lib.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    def linear(c):
        return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
    color.constant = unreal.LinearColor(*(linear(c) for c in entry['color']), 1)
    lib.connect_material_property(color, '', unreal.MaterialProperty.MP_BASE_COLOR)
    for prop, value in [(unreal.MaterialProperty.MP_ROUGHNESS, entry['roughness']), (unreal.MaterialProperty.MP_METALLIC, entry['metalness'])]:
        constant = lib.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 200)
        constant.r = value
        lib.connect_material_property(constant, '', prop)
    if name == 'Asphalt':
        tex_task = unreal.AssetImportTask()
        tex_task.filename = str(ROOT / 'Art/KartLab/assets/asphalt_track_diff_1k.jpg')
        tex_task.destination_path = DEST + '/Textures'
        tex_task.automated = True
        tex_task.save = True
        asset_tools.import_asset_tasks([tex_task])
        tex = unreal.load_asset(DEST + '/Textures/asphalt_track_diff_1k')
        if tex:
            sample = lib.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -400, -200)
            sample.texture = tex
            lib.connect_material_property(sample, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
    lib.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    materials[name] = mat
    return mat

report = {'map': MAP, 'notice': manifest['notice'], 'meshes': []}
for category in ['circuit', 'kart']:
    for entry in manifest[category]:
        sm = imported_mesh(entry)
        for index in range(len(sm.get_editor_property('static_materials'))):
            sm.set_material(index, create_material(entry))
        body = sm.get_editor_property('body_setup')
        if body:
            body.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(sm)
        position = unreal.Vector(0, 0, 0) if category == 'circuit' else unreal.Vector(-4500, -6100, 20)
        actor = actors.spawn_actor_from_class(unreal.StaticMeshActor, position)
        actor.set_actor_label('SG_' + Path(entry['file']).stem)
        actor.static_mesh_component.set_static_mesh(sm)
        decorative_surface = entry['material'] in ['RoadPaint', 'Rubber', 'Kerb_white', 'Kerb_blue_surface']
        actor.static_mesh_component.set_collision_profile_name('BlockAll' if category == 'circuit' and not decorative_surface else 'NoCollision')
        actor.set_folder_path('SouthGarda/Environment' if category == 'circuit' else 'SouthGarda/KartDisplay')
        report['meshes'].append({'asset': sm.get_path_name(), 'material': entry['material'], 'actor': actor.get_actor_label()})

sun = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 18000), unreal.Rotator(pitch=-35, yaw=-30, roll=0))
sun.set_actor_label('SG_AfternoonSun')
sun.light_component.set_editor_property('intensity', 6.0)
sun.light_component.set_editor_property('light_color', unreal.Color(255, 242, 215, 255))
sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1000))
sky.light_component.set_editor_property('real_time_capture', True)
actors.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector())
actors.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, -300))
start = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-7500, -5200, 150), unreal.Rotator(pitch=0, yaw=0, roll=0))
start.set_actor_label('SG_PlayerStart')
camera = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(-23000, -27000, 21000), unreal.Rotator(pitch=-31, yaw=50, roll=0))
camera.set_actor_label('SG_VenueReviewCamera')
camera.camera_component.set_editor_property('field_of_view', 50)
camera.set_editor_property('auto_activate_for_player', unreal.AutoReceiveInput.PLAYER0)
world = unreal.EditorLevelLibrary.get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode', unreal.load_class(None, '/Game/VehicleTemplate/Blueprints/BP_VehicleAdvGameMode.BP_VehicleAdvGameMode_C'))
if not unreal.EditorLoadingAndSavingUtils.save_map(world, MAP):
    raise RuntimeError('Map save failed')
report['actors'] = len(actors.get_all_level_actors())
report['status'] = 'Imported and saved; driving gameplay and race loop not validated in this art map.'
target = ROOT / 'TestResults/SouthGardaArt'
target.mkdir(parents=True, exist_ok=True)
(target / 'import-report.json').write_text(json.dumps(report, indent=2))
unreal.log('ROADTOF1_ART_IMPORT=' + json.dumps(report))

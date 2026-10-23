"""Import only the separate local-player cockpit assets; never edit a map."""
import unreal as u
import json
from pathlib import Path

ROOT = Path(u.Paths.project_dir()).resolve()
ART = ROOT / 'Art/PlayerVisuals/FirstPerson'
OUT = '/Game/RoadToF1/PlayerVisuals/FirstPerson'
tools = u.AssetToolsHelpers.get_asset_tools()
u.SystemLibrary.execute_console_command(None, 'Interchange.FeatureFlags.Import.FBX 0')
report = {'destination': OUT, 'imports': [], 'errors': []}

def import_fbx(name, skeletal):
    task = u.AssetImportTask()
    task.filename = str(ART / 'Exports' / (name + '.fbx'))
    task.destination_path = OUT
    task.destination_name = name
    task.automated = True
    task.save = True
    task.replace_existing = True
    opts = u.FbxImportUI()
    opts.automated_import_should_detect_type = False
    opts.mesh_type_to_import = u.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else u.FBXImportType.FBXIT_STATIC_MESH
    opts.import_as_skeletal = skeletal
    opts.import_mesh = True
    opts.import_animations = skeletal
    opts.import_materials = False
    opts.import_textures = False
    opts.create_physics_asset = False
    if skeletal:
        opts.override_animation_name = 'A_FP_KartSteering'
    data = opts.skeletal_mesh_import_data if skeletal else opts.static_mesh_import_data
    data.convert_scene = True
    data.convert_scene_unit = True
    data.force_front_x_axis = False
    if not skeletal:
        data.combine_meshes = True
        data.auto_generate_collision = False
    task.options = opts
    tools.import_asset_tasks([task])
    paths = list(task.imported_object_paths)
    assert paths, 'No imports: ' + name
    report['imports'] += paths
    return [u.load_asset(p) for p in paths]

finish_only = '-FPFinishOnly' in u.SystemLibrary.get_command_line()
assets = [u.load_asset(OUT+'/SK_FP_KartArms'), u.load_asset(OUT+'/A_FP_KartSteering')] if finish_only else import_fbx('SK_FP_KartArms', True)
mesh = next(a for a in assets if isinstance(a, u.SkeletalMesh))
animations = [a for a in assets if isinstance(a, u.AnimSequence)]
if not animations:
    animations = [u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(OUT) if isinstance(u.load_asset(p), u.AnimSequence)]
assert animations, 'FBX did not contain the baked steering action'
anim = animations[0]
anim_path = OUT + '/A_FP_KartSteering'
if anim.get_path_name().split('.')[0] != anim_path:
    if u.EditorAssetLibrary.does_asset_exist(anim_path):
        u.EditorAssetLibrary.delete_asset(anim_path)
    assert u.EditorAssetLibrary.rename_asset(anim.get_path_name(), anim_path)
anim = u.load_asset(anim_path)
wheel = u.load_asset(OUT+'/SM_FP_SteeringWheel') if finish_only else next(a for a in import_fbx('SM_FP_SteeringWheel', False) if isinstance(a, u.StaticMesh))

textures = {}
for suffix in ['N', 'R']:
    t = u.AssetImportTask()
    t.filename = str(ART / 'Textures' / ('T_FP_Microfiber_' + suffix + '.png'))
    t.destination_path = OUT
    t.automated = True
    t.save = True
    t.replace_existing = True
    tools.import_asset_tasks([t])
    tex = u.load_asset(t.imported_object_paths[0])
    tex.set_editor_property('srgb', False)
    if suffix == 'N':
        tex.set_editor_property('compression_settings', u.TextureCompressionSettings.TC_NORMALMAP)
    textures[suffix] = tex

palette = {
    'M_FP_Leather': ((.018,.021,.025), .46, 0),
    'M_FP_RedSuede': ((.32,.012,.019), .65, 0),
    'M_FP_WhiteFabric': ((.65,.68,.70), .68, 0),
    'M_FP_Rubber': ((.012,.013,.015), .68, 0),
    'M_FP_Stitch': ((.50,.50,.46), .70, 0),
    'M_FP_BlackFabric': ((.015,.018,.022), .72, 0),
    'M_FP_Metal': ((.24,.26,.28), .29, 1),
}
materials = {}
ME = u.MaterialEditingLibrary
for name, (color, rough, metal) in palette.items():
    mat = u.load_asset(OUT+'/'+name) if u.EditorAssetLibrary.does_asset_exist(OUT+'/'+name) else tools.create_asset(name, OUT, u.Material, u.MaterialFactoryNew())
    ME.delete_all_material_expressions(mat)
    c = ME.create_material_expression(mat, u.MaterialExpressionConstant3Vector, -500, -150)
    c.constant = u.LinearColor(*color, 1)
    ME.connect_material_property(c, '', u.MaterialProperty.MP_BASE_COLOR)
    for value, prop, y in [(rough, u.MaterialProperty.MP_ROUGHNESS, 50), (metal, u.MaterialProperty.MP_METALLIC, 150)]:
        node = ME.create_material_expression(mat, u.MaterialExpressionConstant, -250, y)
        node.r = value
        ME.connect_material_property(node, '', prop)
    if metal == 0 and 'Stitch' not in name:
        uv = ME.create_material_expression(mat, u.MaterialExpressionTextureCoordinate, -850, 300)
        uv.u_tiling = 9
        uv.v_tiling = 9
        tex = ME.create_material_expression(mat, u.MaterialExpressionTextureSample, -550, 300)
        tex.texture = textures['N']
        tex.sampler_type = u.MaterialSamplerType.SAMPLERTYPE_NORMAL
        ME.connect_material_expressions(uv, '', tex, 'UVs')
        ME.connect_material_property(tex, 'RGB', u.MaterialProperty.MP_NORMAL)
    ME.recompile_material(mat)
    ME.set_material_usage(mat, u.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    materials[name] = mat

slots = list(mesh.get_editor_property('materials'))
for slot in slots:
    name = str(slot.material_slot_name)
    slot.material_interface = materials.get(name, materials['M_FP_Leather'])
mesh.set_editor_property('materials', slots)
report['skeletal_material_slots'] = [str(s.material_slot_name) for s in slots]
for i, slot in enumerate(wheel.get_editor_property('static_materials')):
    name = str(slot.material_slot_name)
    wheel.set_material(i, materials['M_FP_Metal' if 'metal' in name.lower() else 'M_FP_Rubber'])

# Soft object references in the native component need explicit packaged-build inclusion.
label_name = 'PAL_LocalCockpit'
label = u.load_asset(OUT+'/'+label_name) if u.EditorAssetLibrary.does_asset_exist(OUT+'/'+label_name) else tools.create_asset(label_name, OUT, u.PrimaryAssetLabel, u.DataAssetFactory())
if label:
    label.set_editor_property('is_runtime_label', True)
    label.set_editor_property('label_assets_in_my_directory', True)
    rules = label.get_editor_property('rules')
    rules.set_editor_property('cook_rule', u.PrimaryAssetCookRule.ALWAYS_COOK)
    label.set_editor_property('rules', rules)

for path in u.EditorAssetLibrary.list_assets(OUT, recursive=True, include_folder=False):
    u.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
report['skeletal_mesh'] = mesh.get_path_name()
report['animation'] = anim.get_path_name()
report['animation_length_seconds'] = anim.get_editor_property('sequence_length')
report['skeleton'] = mesh.get_editor_property('skeleton').get_path_name()
report['wheel'] = wheel.get_path_name()
report['saved_assets'] = list(u.EditorAssetLibrary.list_assets(OUT, recursive=True, include_folder=False))
(ROOT/'Evidence/FirstPerson/import.json').write_text(json.dumps(report, indent=2))
u.log('FIRST_PERSON_IMPORT_COMPLETE: ' + json.dumps(report))

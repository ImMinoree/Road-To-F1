"""Create original lightweight flame/smoke materials; retain existing materials."""
import unreal
tools = unreal.AssetToolsHelpers.get_asset_tools()
lib = unreal.MaterialEditingLibrary
dest = '/Game/RoadToF1/Art/IncidentV01'
for name, color, opacity in [('Flame', (8, 1.4, .02), 1), ('Smoke', (.07, .08, .09), .22)]:
    path = dest + '/M_' + name
    if unreal.EditorAssetLibrary.does_asset_exist(path): continue
    mat = tools.create_asset('M_' + name, dest, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    color_node = lib.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
    color_node.constant = unreal.LinearColor(*color, 1)
    lib.connect_material_property(color_node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    if opacity < 1:
        mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
        value = lib.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 100)
        value.r = opacity
        lib.connect_material_property(value, '', unreal.MaterialProperty.MP_OPACITY)
    lib.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.log('ROADTOF1_INCIDENT_MATERIALS: PASS')

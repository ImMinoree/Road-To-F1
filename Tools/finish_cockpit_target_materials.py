import unreal as u
OUT='/Game/RoadToF1/PlayerVisuals/CockpitTargetV4/';ME=u.MaterialEditingLibrary
def scalar(m,value,prop):
 n=ME.create_material_expression(m,u.MaterialExpressionConstant,-200,100);n.r=value;ME.connect_material_property(n,'',prop);return n
m=u.load_asset(OUT+'M_CT4_SatinAlloy');assert m;ME.delete_all_material_expressions(m);c=ME.create_material_expression(m,u.MaterialExpressionConstant3Vector,-300,0);c.constant=u.LinearColor(.62,.66,.70,1);ME.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR);scalar(m,.72,u.MaterialProperty.MP_METALLIC);scalar(m,.4,u.MaterialProperty.MP_ROUGHNESS);ME.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
m=u.load_asset(OUT+'M_CT4_LCD');ME.delete_all_material_expressions(m);tx=ME.create_material_expression(m,u.MaterialExpressionTextureSample,-500,0);tx.texture=u.load_asset(OUT+'Textures/T_CT4_LCD');ME.connect_material_property(tx,'RGB',u.MaterialProperty.MP_BASE_COLOR);mult=ME.create_material_expression(m,u.MaterialExpressionMultiply,-100,-100);strength=ME.create_material_expression(m,u.MaterialExpressionConstant,-400,-180);strength.r=.55;ME.connect_material_expressions(strength,'',mult,'B');ME.connect_material_expressions(tx,'RGB',mult,'A');ME.connect_material_property(mult,'',u.MaterialProperty.MP_EMISSIVE_COLOR);scalar(m,.42,u.MaterialProperty.MP_ROUGHNESS);scalar(m,0,u.MaterialProperty.MP_METALLIC);ME.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m);u.log('CT4_MATERIAL_RESPONSE_COMPLETE')



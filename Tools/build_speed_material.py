"""Build the local camera's depth-masked, peripheral-only speed blur. No map edits."""
import unreal as u, json, hashlib
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve(); ev=root/'Evidence/SpeedEffects';ev.mkdir(parents=True,exist_ok=True)
maps={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'Content/RoadToF1/Maps').glob('*.umap')}
base='/Game/RoadToF1/SpeedEffects'; tools=u.AssetToolsHelpers.get_asset_tools(); m=u.MaterialEditingLibrary;e=u.EditorAssetLibrary
mat=u.load_asset(base+'/M_KartPeripheralSpeed') or tools.create_asset('M_KartPeripheralSpeed',base,u.Material,u.MaterialFactoryNew())
m.delete_all_material_expressions(mat)
mat.set_editor_property('material_domain',u.MaterialDomain.MD_POST_PROCESS)
mat.set_editor_property('blendable_location',u.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
def node(cls):return m.create_material_expression(mat,cls)
def link(a,out,b,p):assert m.connect_material_expressions(a,out,b,p),(str(a),str(b),p)
scene=node(u.MaterialExpressionSceneTexture);scene.set_editor_property('scene_texture_id',u.SceneTextureId.PPI_POST_PROCESS_INPUT0)
depth=node(u.MaterialExpressionSceneDepth)
strength=node(u.MaterialExpressionScalarParameter);strength.set_editor_property('parameter_name','SpeedStrength');strength.set_editor_property('default_value',0)
custom=node(u.MaterialExpressionCustom);custom.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
inputs=[]
for name in ['Color','Depth','Strength']:
    inp=u.CustomInput();inp.set_editor_property('input_name',name);inputs.append(inp)
custom.set_editor_property('inputs',inputs)
custom.set_editor_property('code',r'''
float2 uv=GetViewportUV(Parameters);
float2 ray=uv-float2(0.5,0.42);
float peripheral=smoothstep(0.40,0.95,length(ray*2));
float worldMask=smoothstep(200.0,450.0,Depth);
float amount=saturate(Strength)*peripheral*worldMask;
if(amount<0.0001) return Color.rgb;
float3 sum=Color.rgb; float weight=1;
// Only a few pixels of radial travel, never the large streaks of an arcade boost.
for(int i=1;i<=3;i++) {
 float2 tap=saturate(uv-ray*(0.0045*amount*(i/3.0)));
 float2 texUV=ClampSceneTextureUV(ViewportUVToSceneTextureUV(tap,14),14);
 float tapDepth=CalcSceneDepth(ViewportUVToSceneTextureUV(tap,1));
 float valid=smoothstep(200.0,450.0,tapDepth);
 sum+=SceneTextureLookup(texUV,14,true).rgb*valid;weight+=valid;
}
return lerp(Color.rgb,sum/weight,0.35*amount);
''')
link(scene,'Color',custom,'Color');link(depth,'',custom,'Depth');link(strength,'',custom,'Strength')
assert m.connect_material_property(custom,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
m.recompile_material(mat);assert e.save_loaded_asset(mat)
label=u.load_asset(base+'/PAL_SpeedEffects') or tools.create_asset('PAL_SpeedEffects',base,u.PrimaryAssetLabel,u.DataAssetFactory())
label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',True)
rules=label.get_editor_property('rules');rules.set_editor_property('cook_rule',u.PrimaryAssetCookRule.ALWAYS_COOK);label.set_editor_property('rules',rules);e.save_loaded_asset(label)
assert maps=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'Content/RoadToF1/Maps').glob('*.umap')}
(ev/'material_build.json').write_text(json.dumps({'material':mat.get_path_name(),'maps_unchanged':True},indent=2))
u.log('SPEED_MATERIAL_BUILT')

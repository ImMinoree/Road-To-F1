"""One procedural post-process pass. No imported images, particles or map changes."""
import unreal as u,json
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve();ev=root/'Evidence/AnimeSpeedLines';ev.mkdir(parents=True,exist_ok=True)
base='/Game/RoadToF1/SpeedEffects';tools=u.AssetToolsHelpers.get_asset_tools();m=u.MaterialEditingLibrary
mat=u.load_asset(base+'/M_KartAnimeSpeedLines') or tools.create_asset('M_KartAnimeSpeedLines',base,u.Material,u.MaterialFactoryNew())
m.delete_all_material_expressions(mat);mat.set_editor_property('material_domain',u.MaterialDomain.MD_POST_PROCESS);mat.set_editor_property('blendable_location',u.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
def node(c):return m.create_material_expression(mat,c)
scene=node(u.MaterialExpressionSceneTexture);scene.set_editor_property('scene_texture_id',u.SceneTextureId.PPI_POST_PROCESS_INPUT0)
depth=node(u.MaterialExpressionSceneDepth)
custom=node(u.MaterialExpressionCustom);custom.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
sources={'Color':(scene,'Color'),'Depth':(depth,'')}
for name,value in dict(LineStrength=0,LineCount=80,Thickness=1,LineOpacity=.42,AnimationTime=0,Blur=.15).items():
 p=node(u.MaterialExpressionScalarParameter);p.set_editor_property('parameter_name',name);p.set_editor_property('default_value',value);sources[name]=(p,'')
vp=node(u.MaterialExpressionVectorParameter);vp.set_editor_property('parameter_name','VanishingPoint');vp.set_editor_property('default_value',u.LinearColor(.5,.42,0,0));sources['VanishingPoint']=(vp,'')
inputs=[]
for name in sources:
 i=u.CustomInput();i.set_editor_property('input_name',name);inputs.append(i)
custom.set_editor_property('inputs',inputs)
custom.set_editor_property('code',r'''
if(LineStrength<=0.0001) return Color.rgb;
float2 uv=GetViewportUV(Parameters);
float2 ray=uv-VanishingPoint.xy;
float radius=length(ray*2.0);
// Preserve the racing sightline and all close cockpit surfaces.
float mask=smoothstep(0.60,1.03,radius)*smoothstep(250.0,550.0,Depth);
mask*=1.0-smoothstep(0.68,0.87,uv.y);
if(mask<0.0001) return Color.rgb;
float angular=(atan2(ray.y,ray.x)/6.2831853+0.5)*LineCount;
float cell=floor(angular);
float seed=frac(sin(cell*127.1+31.7)*43758.5453);
float seed2=frac(sin(cell*269.5+17.1)*22578.1459);
float center=0.2+0.6*seed;
float aa=max(fwidth(angular),0.00001);
float width=0.5*Thickness*aa;
float streakCoverage=1.0-smoothstep(width,width+aa,abs(frac(angular)-center));
float strength=saturate(LineStrength);
float phase=frac(AnimationTime*(0.75+seed2*0.5)+seed);
float head=0.66+phase*1.1;
float len=lerp(0.07,0.48,strength)*(0.6+seed2*0.8);
float segment=smoothstep(head-len,head-len+0.055,radius)*(1.0-smoothstep(head-0.025,head,radius));
float alpha=streakCoverage*segment*mask*LineOpacity*strength*(0.55+seed*0.45);
float3 result=Color.rgb;
// Two restrained, depth-aware peripheral blur taps; zero blur at the central view.
float amount=saturate(Blur)*strength*mask;
if(amount>0.0001){
 float3 sum=Color.rgb;float weight=1;
 for(int j=1;j<=2;j++){
  float2 tap=saturate(uv-ray*(0.004*amount*j));
  float valid=smoothstep(250.0,550.0,CalcSceneDepth(ViewportUVToSceneTextureUV(tap,1)));
  sum+=SceneTextureLookup(ClampSceneTextureUV(ViewportUVToSceneTextureUV(tap,14),14),14,true).rgb*valid;weight+=valid;
 }
 result=lerp(result,sum/weight,amount*0.25);
}
return lerp(result,float3(1,1,1),saturate(alpha));
''')
for name,(src,out) in sources.items():assert m.connect_material_expressions(src,out,custom,name)
assert m.connect_material_property(custom,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
m.recompile_material(mat);assert u.EditorAssetLibrary.save_loaded_asset(mat)
(ev/'material.json').write_text(json.dumps({'asset':mat.get_path_name(),'procedural':True,'scene_color_taps_max':3},indent=2))
u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')

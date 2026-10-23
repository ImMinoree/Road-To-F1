"""Reversible golden-hour art direction; no geometry/gameplay/source edits."""
import unreal as u,json,hashlib,math
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/DesertGoldenHour';EV.mkdir(parents=True,exist_ok=True);BASE='/Game/RoadToF1/DesertGoldenHour'
E=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();M=u.MaterialEditingLibrary;level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Source','Config','Content'] for p in (ROOT/folder).rglob('*') if p.is_file() and (folder!='Content' or p.suffix=='.uasset') and 'DesertGoldenHour' not in str(p)}
def material(name):
 path=BASE+'/Materials/'+name
 return u.load_asset(path) if E.does_asset_exist(path) else T.create_asset(name,BASE+'/Materials',u.Material,u.MaterialFactoryNew())
cloudpath=BASE+'/Materials/MI_GH_Clouds';cloud=u.load_asset(cloudpath)
if not cloud:cloud=T.duplicate_asset('MI_GH_Clouds',BASE+'/Materials',u.load_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst'))
assert cloud
for n,v in [('Cloud_GlobalCoverage',.30),('Cloud_GlobalDensity',.65),('StormClouds',0),('Layout_CloudGlobalScale',M.get_material_instance_scalar_parameter_value(u.load_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst'),'Layout_CloudGlobalScale'))]:M.set_material_instance_scalar_parameter_value(cloud,n,v)
E.save_loaded_asset(cloud)
lamp=material('M_GH_LampLens');M.delete_all_material_expressions(lamp);lamp.set_editor_property('two_sided',True)
for prop,col in [(u.MaterialProperty.MP_BASE_COLOR,[.72,.68,.53]),(u.MaterialProperty.MP_EMISSIVE_COLOR,[1800,1510,1100])]:
 n=M.create_material_expression(lamp,u.MaterialExpressionConstant3Vector);n.set_editor_property('constant',u.LinearColor(*col));M.connect_material_property(n,'',prop)
r=M.create_material_expression(lamp,u.MaterialExpressionConstant);r.set_editor_property('r',.38);M.connect_material_property(r,'',u.MaterialProperty.MP_ROUGHNESS);M.recompile_material(lamp);E.save_loaded_asset(lamp)
report={}
for mp in ['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual']:
 assert level.load_level(mp);cp='/Game/RoadToF1/Checkpoints/'+mp.rsplit('/',1)[-1]+'_BeforeGoldenHour'
 if not E.does_asset_exist(cp):copy=E.duplicate_asset(mp,cp);assert copy and E.save_loaded_asset(copy)
 allactors=list(actors.get_all_level_actors());changes=[]
 def disable(a,comp):
  a.set_actor_hidden_in_game(True);comp.set_visibility(False,True);a.set_folder_path('_Disabled_DuplicateAtmosphere');changes.append('Disabled duplicate '+a.get_actor_label())
 suns=sorted([a for a in allactors if isinstance(a,u.DirectionalLight)],key=lambda a:a.get_actor_label())
 assert suns
 for a in suns[1:]:
  a.light_component.set_editor_property('intensity',0);a.light_component.set_editor_property('atmosphere_sun_light',False);disable(a,a.light_component)
 sun=suns[0];c=sun.light_component;sun.set_actor_hidden_in_game(False);c.set_visibility(True);sun.set_actor_rotation(u.Rotator(pitch=-17,yaw=120),False)
 for k,v in {'intensity':28000.,'use_temperature':True,'temperature':5500.,'light_source_angle':1.2,'atmosphere_sun_light':True,'atmosphere_sun_light_index':0,'forward_shading_priority':1,'cast_cloud_shadows':False}.items():c.set_editor_property(k,v)
 c.set_light_color(u.LinearColor(1,1,1));changes.append('Sun: elevation 17deg, yaw120, 28000lux, 5500K, source angle1.2deg')
 skies=sorted([a for a in allactors if isinstance(a,u.SkyLight)],key=lambda a:a.get_actor_label())
 if not skies:
  sky=actors.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,100));sky.set_actor_label('GH_SkyFill');skies=[sky]
 for a in skies[1:]:a.light_component.set_editor_property('intensity',0);disable(a,a.light_component)
 sky=skies[0];sky.set_actor_hidden_in_game(False);c=sky.light_component;c.set_visibility(True);c.set_mobility(u.ComponentMobility.MOVABLE);c.set_editor_property('intensity',1.25);c.set_editor_property('real_time_capture',True);c.set_editor_property('lower_hemisphere_is_black',False);c.recapture_sky()
 for cls,ctype in [(u.SkyAtmosphere,u.SkyAtmosphereComponent),(u.ExponentialHeightFog,u.ExponentialHeightFogComponent)]:
  aa=sorted([a for a in allactors if isinstance(a,cls)],key=lambda a:a.get_actor_label())
  for a in aa[1:]:disable(a,a.get_component_by_class(ctype))
  if aa:
   c=aa[0].get_component_by_class(ctype)
   if cls==u.SkyAtmosphere:
    c.set_editor_property('mie_scattering_scale',.003);c.set_editor_property('mie_anisotropy',.75)
   else:
    for k,v in {'fog_density':.002,'fog_height_falloff':.25,'start_distance':25000.,'fog_max_opacity':.22,'enable_volumetric_fog':False}.items():c.set_editor_property(k,v)
 pp=sorted([a for a in allactors if isinstance(a,u.PostProcessVolume)],key=lambda a:a.get_actor_label())
 for a in pp[1:]:a.set_editor_property('enabled',False);a.set_folder_path('_Disabled_DuplicateAtmosphere')
 p=pp[0] if pp else actors.spawn_actor_from_class(u.PostProcessVolume,u.Vector());p.set_editor_property('unbound',True);p.set_editor_property('priority',10.);p.set_editor_property('enabled',True);s=p.get_editor_property('settings')
 def setting(k,v):s.set_editor_property('override_'+k,True);s.set_editor_property(k,v)
 for k,v in {'auto_exposure_method':u.AutoExposureMethod.AEM_MANUAL,'auto_exposure_apply_physical_camera_exposure':True,'camera_iso':100.,'camera_shutter_speed':125.,'depth_of_field_fstop':5.6,'auto_exposure_bias':0.,'bloom_intensity':.12,'lens_flare_intensity':0.,'vignette_intensity':.10,'film_grain_intensity':0.,'scene_fringe_intensity':0.,'color_saturation':u.Vector4(1.02,1.02,1.02,1.),'color_contrast':u.Vector4(1.025,1.025,1.025,1.),'color_gain_highlights':u.Vector4(1.015,1.,.985,1.)}.items():setting(k,v)
 p.set_editor_property('settings',s)
 ca=next((a for a in allactors if isinstance(a,u.VolumetricCloud)),None)
 if not ca:ca=actors.spawn_actor_from_class(u.VolumetricCloud,u.Vector());ca.set_actor_label('GH_FairWeatherClouds')
 cc=ca.get_component_by_class(u.VolumetricCloudComponent)
 for k,v in {'material':cloud,'layer_bottom_altitude':2.5,'layer_height':1.2,'view_sample_count_scale':.6,'shadow_view_sample_count_scale':.4}.items():cc.set_editor_property(k,v)
 for a in allactors:
  if isinstance(a,u.StaticMeshActor) and a.get_actor_label().startswith(('DK_11 ','DK_13 ')) and a.get_actor_label().endswith(' | lamp'):
   a.static_mesh_component.set_material(0,lamp)
 # Four restrained local pools, not one dynamic light per fixture. No new shadow maps.
 for idx,x,y,h in [(11,-111,-65,18),(12,-111,-10,22),(17,-18,-64,18),(16,60,-26,18)]:
  label='GH_FloodPool_%02d'%idx;a=next((a for a in allactors if a.get_actor_label()==label),None)
  pos=u.Vector((y+28)*100,(-x-103)*100,(h-.76)*100);target=u.Vector((y*.7+28)*100,(-x*.7-103)*100,0);d=target-pos
  rot=u.Rotator(pitch=math.degrees(math.atan2(d.z,math.hypot(d.x,d.y))),yaw=math.degrees(math.atan2(d.y,d.x)))
  if not a:a=actors.spawn_actor_from_class(u.SpotLight,pos,rot);a.set_actor_label(label)
  c=a.light_component;c.set_mobility(u.ComponentMobility.MOVABLE)
  for k,v in {'intensity_units':u.LightUnits.LUMENS,'intensity':35000.,'use_temperature':True,'temperature':4800.,'attenuation_radius':3500.,'inner_cone_angle':30.,'outer_cone_angle':55.,'cast_shadows':False,'source_radius':8.}.items():c.set_editor_property(k,v)
  a.set_folder_path('GoldenHour/ExistingFixtureLightPools')
 # Small overrides only on existing visual PBR materials; source assets untouched.
 tuning={}
 if mp.endswith('_Visual'):
  for a in allactors:
   if not isinstance(a,u.StaticMeshActor) or not a.get_actor_label().startswith('DK_02 '):continue
   c=a.static_mesh_component;old=c.get_material(0)
   if not isinstance(old,u.MaterialInstanceConstant):continue
   name=a.get_actor_label().rsplit(' | ',1)[-1]
   if name not in ['asphalt','runoff']:continue
   path=BASE+'/Materials/MI_GH_'+name;new=u.load_asset(path) or E.duplicate_asset(old.get_path_name(),path)
   tint=M.get_material_instance_vector_parameter_value(u.load_asset('/Game/RoadToF1/DesertVisual/Materials/MI_DV_'+name),'Tint');original=[tint.r,tint.g,tint.b]
   if name=='asphalt':color=[tint.r*.94,tint.g*.94,tint.b*.94]
   else:
    grey=(tint.r+tint.g+tint.b)/3;color=[(v*.85+grey*.15)*.90 for v in original]
   M.set_material_instance_vector_parameter_value(new,'Tint',u.LinearColor(*color));E.save_loaded_asset(new);c.set_material(0,new);tuning[name]={'before':original,'after':color}
 saved=level.save_current_level();report[mp]={'saved':saved,'checkpoint':cp,'changes':changes,'material_tuning':tuning,'local_lights':4}
for p,h in protected.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
(EV/'applied.json').write_text(json.dumps({'maps':report,'source_config_existing_assets_unchanged':True},indent=2));assert all(r['saved'] for r in report.values())




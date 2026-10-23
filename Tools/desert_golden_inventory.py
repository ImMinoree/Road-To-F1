import unreal as u,json
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve();ev=root/'Evidence/DesertGoldenHour';ev.mkdir(parents=True,exist_ok=True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);assert level.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
def props(o,keys):
 d={}
 for k in keys:
  try:d[k]=str(o.get_editor_property(k))
  except Exception as e:d[k]='UNAVAILABLE'
 return d
report=[]
for a in actors.get_all_level_actors():
 if isinstance(a,u.Light):
  c=a.light_component;report.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'rotation':str(a.get_actor_rotation()),'props':props(c,['intensity','visible','light_color','use_temperature','temperature','cast_shadows','mobility','atmosphere_sun_light','atmosphere_sun_light_index','forward_shading_priority','light_source_angle','source_angle','source_soft_angle','real_time_capture','lower_hemisphere_is_black','sky_distance_threshold'])})
 elif isinstance(a,u.PostProcessVolume):report.append({'label':a.get_actor_label(),'settings':a.get_editor_property('settings').export_text()})
 elif isinstance(a,u.SkyAtmosphere):report.append({'label':a.get_actor_label(),'props':props(a.get_component_by_class(u.SkyAtmosphereComponent),['mie_scattering_scale','mie_anisotropy','aerial_perspective_view_distance_scale','rayleigh_scattering_scale'])})
 elif isinstance(a,u.ExponentialHeightFog):report.append({'label':a.get_actor_label(),'props':props(a.get_component_by_class(u.ExponentialHeightFogComponent),['fog_density','fog_height_falloff','start_distance','fog_max_opacity','volumetric_fog'])})
 elif isinstance(a,u.VolumetricCloud):report.append({'label':a.get_actor_label(),'props':props(a.get_component_by_class(u.VolumetricCloudComponent),['material','layer_bottom_altitude','layer_height'])})
cloud=u.load_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst')
if cloud:report.append({'cloud_asset':cloud.get_path_name(),'scalar_parameters':[str(n) for n in u.MaterialEditingLibrary.get_scalar_parameter_names(cloud)]})
(ev/'inventory.json').write_text(json.dumps(report,indent=2))

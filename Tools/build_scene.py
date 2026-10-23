"""Run in Unreal Editor with: py <absolute path>. Rebuilds only VisualProof."""
import unreal as u, math, json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve()
BASE='/Game/RoadToF1'
assets=u.AssetToolsHelpers.get_asset_tools()
def material(name,color,rough=.85,photo=False):
    path=BASE+'/Materials/'+name
    m=u.load_asset(path) or assets.create_asset(name,BASE+'/Materials',u.Material,u.MaterialFactoryNew())
    u.MaterialEditingLibrary.delete_all_material_expressions(m)
    c=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector)
    c.set_editor_property('constant',u.LinearColor(*color))
    u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
    r=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant)
    r.set_editor_property('r',rough)
    u.MaterialEditingLibrary.connect_material_property(r,'',u.MaterialProperty.MP_ROUGHNESS)
    if photo:
        tex=u.load_asset(BASE+'/Textures/asphalt_track_diff_1k')
        if tex:
            e=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionTextureSample)
            e.set_editor_property('texture',tex)
            u.MaterialEditingLibrary.connect_material_property(e,'RGB',u.MaterialProperty.MP_BASE_COLOR)
        for suffix,prop in [('nor_dx',u.MaterialProperty.MP_NORMAL),('rough',u.MaterialProperty.MP_ROUGHNESS)]:
            tex=u.load_asset(BASE+'/Textures/asphalt_track_'+suffix+'_1k')
            if tex:
                tex.set_editor_property('srgb',False)
                if suffix=='nor_dx': tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
                e=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionTextureSample)
                e.set_editor_property('texture',tex)
                e.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL if suffix=='nor_dx' else u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
                u.MaterialEditingLibrary.connect_material_property(e,'RGB' if suffix=='nor_dx' else 'R',prop)
                u.EditorAssetLibrary.save_loaded_asset(tex)
    u.MaterialEditingLibrary.recompile_material(m)
    u.EditorAssetLibrary.save_loaded_asset(m)
    return m
tasks=[]
for source,dest in [(p,BASE+'/Meshes') for p in (ROOT/'Art'/'Exports').glob('*.fbx')]+[(p,BASE+'/Textures') for p in (ROOT/'Art'/'Textures').glob('*.jpg')]:
    t=u.AssetImportTask();t.filename=str(source);t.destination_path=dest;t.automated=True;t.replace_existing=True;t.save=True
    if source.suffix=='.fbx':
        opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False
        opts.static_mesh_import_data.set_editor_property('combine_meshes',True)
        opts.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False)
        t.options=opts
    tasks.append(t)
assets.import_asset_tasks(tasks)
mats={'Road':material('M_Asphalt',(.1,.1,.1),photo=True),'VergeLeft':material('M_UnfinishedSoil',(.14,.11,.07))}
mats['VergeRight']=mats['VergeLeft']
red=material('M_CurbRed',(.3,.035,.025));white=material('M_CurbWhite',(.48,.46,.41))
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
level.new_level(BASE+'/Maps/VisualProof')
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
for name in ['Road','CurbLeft','CurbRight','VergeLeft','VergeRight']:
    mesh=u.load_asset(BASE+'/Meshes/'+name)
    if not mesh: raise RuntimeError('Missing mesh '+name)
    body=mesh.get_editor_property('body_setup')
    body.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0));a.set_actor_label(name)
    a.static_mesh_component.set_static_mesh(mesh)
    a.static_mesh_component.set_material(0,red if name.startswith('Curb') else mats[name])
    if name.startswith('Curb'): a.static_mesh_component.set_material(1,white)
    u.EditorAssetLibrary.save_loaded_asset(mesh)
sun=actors.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,1000),u.Rotator(pitch=-38,yaw=-35,roll=0))
sun.light_component.set_editor_property('intensity',65000)
sun.light_component.set_editor_property('atmosphere_sun_light',True)
actors.spawn_actor_from_class(u.SkyAtmosphere,u.Vector())
sky=actors.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,300))
sky.light_component.set_editor_property('real_time_capture',True)
actors.spawn_actor_from_class(u.ExponentialHeightFog,u.Vector(0,0,-500))
pp=actors.spawn_actor_from_class(u.PostProcessVolume,u.Vector())
pp.set_editor_property('unbound',True)
s=pp.get_editor_property('settings')
s.set_editor_property('override_auto_exposure_method',True)
s.set_editor_property('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL)
s.set_editor_property('override_auto_exposure_bias',True);s.set_editor_property('auto_exposure_bias',0)
s.set_editor_property('override_auto_exposure_apply_physical_camera_exposure',True)
s.set_editor_property('auto_exposure_apply_physical_camera_exposure',True)
s.set_editor_property('override_camera_iso',True);s.set_editor_property('camera_iso',100)
s.set_editor_property('override_camera_shutter_speed',True);s.set_editor_property('camera_shutter_speed',125)
s.set_editor_property('override_depth_of_field_fstop',True);s.set_editor_property('depth_of_field_fstop',8)
pp.set_editor_property('settings',s)
actors.spawn_actor_from_class(u.PlayerStart,u.Vector(800,0,31),u.Rotator())
shots=[('01_DriverEye',(1200,0,80),(-3,3,0)),('02_Ground',(3900,-550,45),(-2,30,0)),('03_Wide',(6200,-1700,750),(-18,42,0))]
for name,pos,rot in shots:
    c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(*pos),u.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]));c.set_actor_label(name)
    c.camera_component.set_field_of_view(85)
level.save_current_level()
u.EditorAssetLibrary.save_directory(BASE)
(ROOT/'Evidence'/'scene.json').write_text(json.dumps({'length_m':150,'width_m':8,'eye_height_m':.8,'shots':shots,'status':'Foundation only; vegetation, barriers, soil PBR and cockpit absent'},indent=2))
u.log('VISUAL_PROOF_BUILD_COMPLETE')

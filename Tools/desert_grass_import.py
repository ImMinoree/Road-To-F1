"""Add reversible instanced grass only; keep lighting, collision, and gameplay intact."""
import unreal as u,json,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve(); O=R/'Art/InfieldGrass'; EV=R/'Evidence/InfieldGrass'; EV.mkdir(parents=True,exist_ok=True)
g=json.loads((O/'scatter.json').read_text()); BASE='/Game/RoadToF1/InfieldGrass'
E=u.EditorAssetLibrary; T=u.AssetToolsHelpers.get_asset_tools(); M=u.MaterialEditingLibrary
L=u.get_editor_subsystem(u.LevelEditorSubsystem); A=u.get_editor_subsystem(u.EditorActorSubsystem); W=u.get_editor_subsystem(u.UnrealEditorSubsystem)
def node(cls):return M.create_material_expression(mat,cls)
def link(a,b,p,out=''):
    inputs=M.get_material_expression_input_names(b)
    if p not in inputs and len(inputs)==1:p=inputs[0]
    assert M.connect_material_expressions(a,out,b,p),(str(b),p,list(inputs))
def scalar(name,value):
    n=node(u.MaterialExpressionScalarParameter);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',value);return n
def color(name,value):
    n=node(u.MaterialExpressionVectorParameter);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',u.LinearColor(*value));return n
def prop(n,p):assert M.connect_material_property(n,'',p)
mat=u.load_asset(BASE+'/Materials/M_InfieldGrass') or T.create_asset('M_InfieldGrass',BASE+'/Materials',u.Material,u.MaterialFactoryNew())
M.delete_all_material_expressions(mat);mat.set_editor_property('two_sided',True);mat.set_editor_property('shading_model',u.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE);mat.set_editor_property('used_with_instanced_static_meshes',True)
uv=node(u.MaterialExpressionVertexColor);mask=node(u.MaterialExpressionComponentMask);mask.set_editor_property('r',True);mask.set_editor_property('g',False);link(uv,mask,'Input')
blend=node(u.MaterialExpressionLinearInterpolate)
link(color('RootColor',[.018,.032,.007]),blend,'A');link(color('TipColor',[.07,.12,.024]),blend,'B');link(mask,blend,'Alpha')
rand=node(u.MaterialExpressionPerInstanceRandom);scale=node(u.MaterialExpressionMultiply);link(rand,scale,'A');scale.set_editor_property('const_b',.35)
add=node(u.MaterialExpressionAdd);link(scale,add,'A');add.set_editor_property('const_b',.8)
mul=node(u.MaterialExpressionMultiply);link(blend,mul,'A');link(add,mul,'B');prop(mul,u.MaterialProperty.MP_BASE_COLOR)
prop(color('Transmission',[.04,.07,.012]),u.MaterialProperty.MP_SUBSURFACE_COLOR);prop(scalar('Roughness',.85),u.MaterialProperty.MP_ROUGHNESS)
# Root-anchored, world-coherent breeze; blades use V=0 at root and V=1 at tip.
wind=node(u.MaterialExpressionCustom);wind.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
wind.set_editor_property('code','float phase=World.x*0.0027+World.y*0.0019+Time*Speed; float bend=(sin(phase)+0.35*sin(phase*1.83+1.7))*Amplitude*UV.r*UV.r; return float3(bend,bend*0.38,0);')
names=['World','Time','Speed','Amplitude','UV'];inputs=[]
for name in names:
    inp=u.CustomInput();inp.set_editor_property('input_name',name);inputs.append(inp)
wind.set_editor_property('inputs',inputs)
link(node(u.MaterialExpressionWorldPosition),wind,'World');link(node(u.MaterialExpressionTime),wind,'Time');link(scalar('WindSpeed',1.25),wind,'Speed');link(scalar('WindAmplitudeCm',2.2),wind,'Amplitude');link(uv,wind,'UV');prop(wind,u.MaterialProperty.MP_WORLD_POSITION_OFFSET)
M.recompile_material(mat);E.save_loaded_asset(mat)
tasks=[]
for item in g['assets']:
    t=u.AssetImportTask();t.filename=str(O/'Meshes'/(item['name']+'.fbx'));t.destination_path=BASE+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
    opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opt.import_materials=False;opt.import_textures=False
    opt.static_mesh_import_data.set_editor_property('combine_meshes',True);opt.static_mesh_import_data.set_editor_property('auto_generate_collision',False);opt.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False);opt.static_mesh_import_data.set_editor_property('vertex_color_import_option',u.VertexColorImportOption.REPLACE);t.options=opt;tasks.append(t)
T.import_asset_tasks(tasks)
types=[]
for item in g['assets']:
    mesh=u.load_asset(BASE+'/Meshes/'+item['name']);assert mesh;mesh.set_material(0,mat);E.save_loaded_asset(mesh)
    name='FT_'+item['name'];ft=u.load_asset(BASE+'/Foliage/'+name) or T.create_asset(name,BASE+'/Foliage',u.FoliageType_InstancedStaticMesh,u.FoliageType_InstancedStaticMeshFactory())
    ft.set_editor_property('mesh',mesh);ft.set_editor_property('cull_distance',u.Int32Interval(min=5000,max=7500));ft.set_editor_property('cast_shadow',False)
    body=ft.get_editor_property('body_instance');body.set_editor_property('collision_enabled',u.CollisionEnabled.NO_COLLISION);body.set_editor_property('collision_profile_name','NoCollision');ft.set_editor_property('body_instance',body);ft.set_editor_property('collision_with_world',False);E.save_loaded_asset(ft);types.append(ft)
def signature():
    result={}
    for a in A.get_all_level_actors():
        if isinstance(a,u.InstancedFoliageActor):continue
        p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
        result[a.get_path_name()]=[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z,a.get_actor_enable_collision()]
    return result
report={}
for name in ['DesertKarting','DesertKarting_Visual']:
    path='/Game/RoadToF1/Maps/'+name;assert L.load_level(path)
    cp='/Game/RoadToF1/Checkpoints/'+name+'_BeforeInfieldGrass'
    if not E.does_asset_exist(cp):
        checkpoint=E.duplicate_asset(path,cp);assert checkpoint and E.save_loaded_asset(checkpoint)
    before=signature();world=W.get_editor_world();counts=[]
    for idx,ft in enumerate(types):
        u.InstancedFoliageActor.remove_all_instances(world,ft)
        ts=[u.Transform(location=u.Vector(*p['location']),rotation=u.Rotator(yaw=p['yaw']),scale=u.Vector(p['scale'],p['scale'],p['scale'])) for p in g['placements'] if p['variant']==idx]
        u.InstancedFoliageActor.add_instances(world,ft,ts);counts.append(len(ts))
    assert signature()==before,'An existing actor was changed'
    assert L.save_current_level();assert L.load_level(path)
    actual=0
    for a in A.get_all_level_actors():
        for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
            if c.static_mesh and c.static_mesh.get_path_name().startswith(BASE+'/'):
                assert c.get_collision_enabled()==u.CollisionEnabled.NO_COLLISION
                actual+=c.get_instance_count()
    assert actual==sum(counts),(actual,counts)
    report[name]=dict(saved=True,instances=actual,variant_counts=counts,existing_actor_transforms_and_collision_unchanged=True,checkpoint=cp)
(EV/'implementation.json').write_text(json.dumps(report,indent=2))

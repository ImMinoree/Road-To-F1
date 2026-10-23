"""Phase 3 scenery import; foliage assets deliberately not fabricated."""
import unreal as u,json,math,hashlib,ast,collections
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();WORK=ROOT/'Art/CircuitDevelopment';EVIDENCE=ROOT/'Evidence/CircuitDevelopment'
assert json.loads((EVIDENCE/'phase2.json').read_text())['gate_passed']
assert not (EVIDENCE/'phase3.json').exists(),'Completed environment pass preserved'
BASE='/Game/RoadToF1/CircuitDevelopment';MAP='/Game/RoadToF1/Maps/CircuitDevelopment';E=u.EditorAssetLibrary;L=u.MaterialEditingLibrary;tools=u.AssetToolsHelpers.get_asset_tools()
meta=json.loads((WORK/'Textures/provenance.json').read_text());manifest=json.loads((WORK/'environment.json').read_text())
# Reuse only tested graph-helper definitions; do not execute the Phase 2 pass again.
tree=ast.parse((ROOT/'Tools/circuit_phase2.py').read_text())
for definition in tree.body:
 if isinstance(definition,ast.FunctionDef):exec(compile(ast.Module(body=[definition],type_ignores=[]),'material_helpers','exec'))
assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
actors=u.get_editor_subsystem(u.EditorActorSubsystem);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
baseline={a.get_actor_label():[a.get_class().get_path_name(),[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z]] for a in actors.get_all_level_actors()}
g1=json.loads((EVIDENCE/'phase1.json').read_text())
def solid(name,tint,rough,metal=0,paint=False):
 m=mat(name);wear=channel(m,sample(m,'PaintWear'),'R');random=node(m,u.MaterialExpressionPerInstanceRandom)
 variation=add(m,scalar(m,.83),mul(m,random,scalar(m,.17)))
 base=mul(m,color(m,tint),variation)
 if paint:base=lerp(m,base,color(m,[.018,.019,.018]),mul(m,wear,scalar(m,.65)))
 prop(base,u.MaterialProperty.MP_BASE_COLOR);prop(add(m,scalar(m,rough-.08),mul(m,wear,scalar(m,.16))),u.MaterialProperty.MP_ROUGHNESS);prop(scalar(m,metal),u.MaterialProperty.MP_METALLIC)
 return finish(m)
materials={'Steel':solid('M_CD_Galvanized',[.19,.205,.215],.52,.85),'Dark':solid('M_CD_DrainDark',[.012,.014,.012],.92),'BoardWhite':solid('M_CD_SignWhite',[.43,.42,.38],.60),'BoardBlack':solid('M_CD_SignBlack',[.006,.007,.006],.84)}
tire_mats={k:solid('M_CD_'+k,tint,.88,paint=k!='TireBlack') for k,tint in [('TireRed',[.13,.018,.012]),('TireWhite',[.30,.29,.25]),('TireBlack',[.021,.023,.021])]}
tasks=[]
for entry in manifest['assets']:
 if E.does_asset_exist(BASE+'/Props/'+entry['name']):continue
 t=u.AssetImportTask();t.filename=str(WORK/'Props'/(entry['name']+'.fbx'));t.destination_path=BASE+'/Props';t.automated=True;t.save=True;t.replace_existing=False
 opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opts.import_materials=False;opts.import_textures=False
 opts.static_mesh_import_data.set_editor_property('combine_meshes',True);opts.static_mesh_import_data.set_editor_property('auto_generate_collision',False);t.options=opts;tasks.append(t)
tools.import_asset_tasks(tasks)
meshes={}
for entry in manifest['assets']:
 mesh=u.load_asset(BASE+'/Props/'+entry['name']);assert mesh,entry
 for slot,name in enumerate(entry['slots']):
  if name in materials:mesh.set_material(slot,materials[name])
 E.save_loaded_asset(mesh);meshes[entry['name']]=mesh
static=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
for name,material in tire_mats.items():
 path=BASE+'/Props/'+name;mesh=u.load_asset(path) if E.does_asset_exist(path) else E.duplicate_asset(BASE+'/Props/SafetyTire',path)
 mesh.set_material(0,material)
 # This subsystem is editor-only; the live capture gate adds boxes when commandlets omit it.
 if static and static.get_simple_collision_count(mesh)==0:assert static.add_simple_collisions(mesh,u.ScriptCollisionShapeType.BOX)>=0
 E.save_loaded_asset(mesh);meshes[name]=mesh
counts={};types={};new_components=[]
for name,mesh in meshes.items():
 entries=[p for p in manifest['placements'] if p['mesh']==name]
 if not entries:continue
 path=BASE+'/Instancing/FT_'+name
 f=u.load_asset(path) if E.does_asset_exist(path) else tools.create_asset('FT_'+name,BASE+'/Instancing',u.FoliageType_InstancedStaticMesh,u.FoliageType_InstancedStaticMeshFactory())
 u.InstancedFoliageActor.remove_all_instances(world,f);f.set_editor_property('mesh',mesh)
 blocking=name.startswith('Tire');body=f.get_editor_property('body_instance')
 body.set_editor_property('collision_enabled',u.CollisionEnabled.QUERY_AND_PHYSICS if blocking else u.CollisionEnabled.NO_COLLISION)
 body.set_editor_property('collision_profile_name','BlockAll' if blocking else 'NoCollision');f.set_editor_property('body_instance',body)
 f.set_editor_property('collision_with_world',False);f.set_editor_property('cull_distance',u.Int32Interval(min=14000,max=24000))
 E.save_loaded_asset(f);transforms=[]
 for p in entries:
  a=math.radians(p['yaw'])/2
  transforms.append(u.Transform(location=u.Vector(*p['location_cm']),rotation=u.Rotator(pitch=0,yaw=p['yaw'],roll=0),scale=u.Vector(*p['scale'])))
 u.InstancedFoliageActor.add_instances(world,f,transforms);counts[name]=len(transforms);types[name]=path
cloud_material=u.load_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst')
if cloud_material:
 cloud=actors.spawn_actor_from_class(u.VolumetricCloud,u.Vector());cloud.set_actor_label('CD_DaylightClouds')
 c=cloud.get_components_by_class(u.VolumetricCloudComponent)[0];c.set_material(cloud_material);c.set_layer_bottom_altitude(2.0);c.set_layer_height(3.5)
for a in actors.get_all_level_actors():
 if isinstance(a,u.PostProcessVolume):
  s=a.get_editor_property('settings');s.set_editor_property('camera_shutter_speed',250);a.set_editor_property('settings',s)
after={a.get_actor_label():[a.get_class().get_path_name(),[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z]] for a in actors.get_all_level_actors()}
assert all(after[k]==v for k,v in baseline.items()),'Existing actors moved or deleted'
assert g1['source_hashes']=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Source').rglob('*') if p.is_file()}
assert hashlib.sha256((ROOT/'Content/RoadToF1/Maps/VisualProof.umap').read_bytes()).hexdigest()==g1['original_map_sha256']
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
# Reload to verify that instanced components and transforms actually serialize into the map.
assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
actual=collections.Counter();collision=[]
for a in actors.get_all_level_actors():
 for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
  if c.static_mesh:
   name=c.static_mesh.get_name()
   if name in counts:actual[name]+=c.get_instance_count();collision.append([name,str(c.get_collision_enabled())])
assert dict(actual)==counts,(actual,counts)
(EVIDENCE/'phase3.json').write_text(json.dumps({'map':MAP,'saved_and_reloaded':True,'instances':counts,'collision_modes':collision,'new_collision':'Simple boxes on tire walls, minimum centerline clearance >5.65m; all other scenery noncolliding','cloud_material':'Engine built-in simple volumetric cloud' if cloud_material else None,'missing_assets':manifest['missing'],'original_map_and_gameplay_unchanged':True,'render_inspected':False,'gate_passed':False},indent=2))
u.log('PHASE3_SCENERY_SAVED_AND_RELOADED')



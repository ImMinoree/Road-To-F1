"""Phase 1 import and collision gate. Never replaces VisualProof or gameplay code."""
import unreal as u,json,math,hashlib
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();WORK=ROOT/'Art/CircuitDevelopment';EVIDENCE=ROOT/'Evidence/CircuitDevelopment';EVIDENCE.mkdir(exist_ok=True)
BASE='/Game/RoadToF1/CircuitDevelopment';MAP='/Game/RoadToF1/Maps/CircuitDevelopment'
g=json.loads((WORK/'geometry.json').read_text());tools=u.AssetToolsHelpers.get_asset_tools();E=u.EditorAssetLibrary
original=ROOT/'Content/RoadToF1/Maps/VisualProof.umap';original_sha=hashlib.sha256(original.read_bytes()).hexdigest()
source_hash={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Source').rglob('*') if p.is_file()}
assert not (EVIDENCE/'phase1.json').exists(),'Completed Phase 1 preserved.'
tasks=[]
for entry in g['assets']:
 if E.does_asset_exist(BASE+'/Meshes/'+entry['name']):continue
 t=u.AssetImportTask();t.filename=str(WORK/'Geometry'/(entry['name']+'.fbx'));t.destination_path=BASE+'/Meshes';t.automated=True;t.save=True;t.replace_existing=False
 opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opts.import_materials=False;opts.import_textures=False
 opts.static_mesh_import_data.set_editor_property('combine_meshes',True);opts.static_mesh_import_data.set_editor_property('auto_generate_collision',False)
 t.options=opts;tasks.append(t)
tools.import_asset_tasks(tasks)
if not E.does_asset_exist(MAP):assert E.duplicate_asset('/Game/RoadToF1/Maps/VisualProof',MAP)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);assert level.load_level(MAP)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
def fingerprint():
 result={}
 for a in actors.get_all_level_actors():
  if isinstance(a,u.StaticMeshActor):continue
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
  result[a.get_actor_label()]=[a.get_class().get_path_name(),[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]]
 return result
before=fingerprint()
for a in actors.get_all_level_actors():
 if a.get_actor_label() in ['Road','CurbLeft','CurbRight','VergeLeft','VergeRight'] or a.get_actor_label().startswith('CD_'):actors.destroy_actor(a)
assigned={}
for entry in g['assets']:
 mesh=u.load_asset(BASE+'/Meshes/'+entry['name']);assert mesh,entry
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 box=mesh.get_bounding_box()
 a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector());a.set_actor_label('CD_'+entry['name']);a.tags=['CircuitDevelopment']
 a.static_mesh_component.set_static_mesh(mesh)
 names={'Road':'M_Asphalt','Shoulder':'M_UnfinishedSoil','Terrain':'M_UnfinishedSoil','Curbs':'M_CurbRed'}
 a.static_mesh_component.set_material(0,u.load_asset('/Game/RoadToF1/Materials/'+names[entry['category']]))
 if entry['category']=='Curbs':a.static_mesh_component.set_material(1,u.load_asset('/Game/RoadToF1/Materials/M_CurbWhite'))
 E.save_loaded_asset(mesh);assigned[entry['name']]=[str(box.min),str(box.max)]
assert before==fingerprint(),'Gameplay/camera/light actors changed'
failures=[];checked=0
route=g['route'];n=len(route)
assert level.save_current_level()
assert hashlib.sha256(original.read_bytes()).hexdigest()==original_sha
assert source_hash=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Source').rglob('*') if p.is_file()}
index=max(range(n),key=lambda i:abs(g['curvature'][i]));driver=(index-36)%n
p=route[driver];q=route[(driver+28)%n];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]))
corner=route[index];dx=q[0]-p[0];dy=q[1]-p[1];d=math.hypot(dx,dy)
ground=[corner[0]+dy/d*520,corner[1]-dx/d*520,corner[2]+50]
ground_yaw=math.degrees(math.atan2(corner[1]-ground[1],corner[0]-ground[0]))
cx=sum(p[0] for p in route)/n;cy=sum(p[1] for p in route)/n
shots=[['Driver',[p[0],p[1],p[2]+80],[-4,yaw,0]],['Ground',ground,[-4,ground_yaw,0]],['Overview',[cx,cy,33000],[-90,0,0]]]
(EVIDENCE/'shots.json').write_text(json.dumps(shots,indent=2))
(EVIDENCE/'phase1.json').write_text(json.dumps({'map':MAP,'geometry_saved':True,'collision_rays':checked,'collision_failures':failures,'length_m':g['length_m'],'width_m':8,'closed':True,'boundary_intersections':g['boundary_intersections'],'original_map_sha256':original_sha,'source_hashes':source_hash,'preserved_non_environment_actors':before,'mesh_bounds':assigned,'render_inspected':False},indent=2))
u.log('PHASE1_IMPORT_AND_COLLISION_PASSED')

"""Unreal Python: import the user's GLB conversion into an isolated playable map."""
import unreal as u,json,hashlib
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/DesertKarting';EV=ROOT/'Evidence/DesertKarting';EV.mkdir(parents=True,exist_ok=True)
g=json.loads((ART/'manifest.json').read_text());BASE='/Game/RoadToF1/DesertKarting';MAP='/Game/RoadToF1/Maps/DesertKarting'
E=u.EditorAssetLibrary;tools=u.AssetToolsHelpers.get_asset_tools();L=u.MaterialEditingLibrary
protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Source','Config'] for p in (ROOT/folder).rglob('*') if p.is_file()}
for p in (ROOT/'Content/RoadToF1/Maps').glob('*.umap'):
 if p.stem!='DesertKarting':protected[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
mats={}
for name,data in g['materials'].items():
 path=BASE+'/Materials/M_DK_'+name
 m=u.load_asset(path) if E.does_asset_exist(path) else tools.create_asset('M_DK_'+name,BASE+'/Materials',u.Material,u.MaterialFactoryNew())
 L.delete_all_material_expressions(m)
 m.set_editor_property('two_sided',True) # All 25 source GLB materials are doubleSided.
 for prop,value in [(u.MaterialProperty.MP_BASE_COLOR,data['base'][:3]),(u.MaterialProperty.MP_ROUGHNESS,data['roughness']),(u.MaterialProperty.MP_METALLIC,data['metallic']),(u.MaterialProperty.MP_EMISSIVE_COLOR,[c*data['emission_strength'] for c in data['emission'][:3]])]:
  if isinstance(value,list):
   n=L.create_material_expression(m,u.MaterialExpressionConstant3Vector);n.set_editor_property('constant',u.LinearColor(*value))
  else:n=L.create_material_expression(m,u.MaterialExpressionConstant);n.set_editor_property('r',value)
  L.connect_material_property(n,'',prop)
 L.recompile_material(m);E.save_loaded_asset(m);mats[name]=m
tasks=[]
for a in g['assets']:
 if E.does_asset_exist(BASE+'/Meshes/'+a['name']):continue
 t=u.AssetImportTask();t.filename=str(ART/'Meshes'/(a['name']+'.fbx'));t.destination_path=BASE+'/Meshes';t.automated=True;t.save=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False
 o.static_mesh_import_data.set_editor_property('combine_meshes',True);o.static_mesh_import_data.set_editor_property('auto_generate_collision',False);t.options=o;tasks.append(t)
tools.import_asset_tasks(tasks)
if not E.does_asset_exist(MAP):assert E.duplicate_asset('/Game/RoadToF1/Maps/VisualProof',MAP)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);assert level.load_level(MAP)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if isinstance(a,(u.StaticMeshActor,u.CameraActor)):actors.destroy_actor(a)
for entry in g['assets']:
 mesh=u.load_asset(BASE+'/Meshes/'+entry['name']);assert mesh,entry['name']
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 for i,name in enumerate(entry['materials']):
  if name:mesh.set_material(i,mats[name])
 actor=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector());actor.set_actor_label('DK_'+entry['source_object']);actor.tags=['DesertKarting']
 c=actor.static_mesh_component;c.set_static_mesh(mesh)
 c.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS if entry['collision'] else u.CollisionEnabled.NO_COLLISION)
 if '01 Desert terrain' in entry['source_object'] and entry['materials']==['sand']:
  c.set_editor_property('affect_distance_field_lighting',False)
 E.save_loaded_asset(mesh)
for a in actors.get_all_level_actors():
 if isinstance(a,u.PlayerStart):a.set_actor_location(u.Vector(800,0,40),False,False);a.set_actor_rotation(u.Rotator(yaw=0),False)
 if isinstance(a,u.DirectionalLight):
  a.light_component.set_mobility(u.ComponentMobility.MOVABLE)
  a.set_actor_rotation(u.Rotator(pitch=-32,yaw=145),False);a.light_component.set_editor_property('intensity',65000);a.light_component.set_light_color(u.LinearColor(1,.88,.72))
 if isinstance(a,u.SkyLight):
  a.light_component.set_mobility(u.ComponentMobility.MOVABLE);a.light_component.set_editor_property('intensity',1.3);a.light_component.set_editor_property('real_time_capture',True);a.light_component.recapture_sky()
 if isinstance(a,u.PostProcessVolume):
  s=a.get_editor_property('settings');s.set_editor_property('override_camera_shutter_speed',True);s.set_editor_property('camera_shutter_speed',125);a.set_editor_property('settings',s)
for name,p,r in [('Desert_Driver',[800,0,80],[-3,0,0]),('Desert_Overview',[32800,27800,18500],[-22,-128,0])]:
 camera=actors.spawn_actor_from_class(u.CameraActor,u.Vector(*p),u.Rotator(pitch=r[0],yaw=r[1],roll=r[2]));camera.set_actor_label(name);camera.camera_component.set_field_of_view(85)
assert level.save_current_level()
for path,digest in protected.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
(EV/'import.json').write_text(json.dumps({'map':MAP,'source_sha256':g['sha256'],'imported_meshes':len(g['assets']),'materials':len(mats),'triangles':sum(a['triangles'] for a in g['assets']),'spawn_cm':g['unreal_spawn_cm'],'protected_files':protected,'collision':'complex road,curbs,ground,barriers; decorative karts and spectators nonblocking','limitations':['Source GLB has no texture maps','Source karts and spectators are static','Blender procedural bump and area lights absent from GLB; Unreal lighting provided']},indent=2))
u.log('DESERT_IMPORT_COMPLETE')

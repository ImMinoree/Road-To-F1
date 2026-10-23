"""Unreal Python. Reversible four-priority visual pass; no light or collision edits."""
import unreal as u,json,hashlib,collections
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/DesertVisual';EV=ROOT/'Evidence/DesertVisual';EV.mkdir(parents=True,exist_ok=True)
G=json.loads((ART/'manifest.json').read_text());OLD='/Game/RoadToF1/Maps/DesertKarting';MAP=OLD+'_Visual';CHECK='/Game/RoadToF1/Checkpoints/DesertKarting_BeforeVisual';BASE='/Game/RoadToF1/DesertVisual'
E=u.EditorAssetLibrary;L=u.MaterialEditingLibrary;T=u.AssetToolsHelpers.get_asset_tools();level=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['Source','Config','Content/RoadToF1/DesertKarting'] for p in (ROOT/folder).rglob('*') if p.is_file()}
for p in (ROOT/'Content/RoadToF1/Maps').glob('*.umap'):
 if p.stem not in ['DesertKarting','DesertKarting_Visual']:protected[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
def hashcheck():
 for p,h in protected.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
def kart(a):
 label=a.get_actor_label()
 if '10 Race karts' in label or label.lower().startswith(('kart','racekart')):return True
 if isinstance(a,u.StaticMeshActor):
  m=a.static_mesh_component.static_mesh
  if m and ('/Kart/' in m.get_path_name() or m.get_name().startswith('SM_Kart_')):return True
 return False
def hide_karts():
 hidden=[]
 for a in actors.get_all_level_actors():
  if kart(a):
   a.set_actor_hidden_in_game(True);a.set_folder_path('_Hidden_Restore_Karts');a.tags=list(a.tags)+['DV_RestoreKart'] if 'DV_RestoreKart' not in [str(t) for t in a.tags] else a.tags
   for c in a.get_components_by_class(u.PrimitiveComponent):c.set_visibility(False,True)
   hidden.append(a.get_actor_label())
 return hidden
def signature():
 collision={};lighting={}
 for a in actors.get_all_level_actors():
  if isinstance(a,u.StaticMeshActor):
   c=a.static_mesh_component
   if c.get_collision_enabled()!=u.CollisionEnabled.NO_COLLISION:
    collision[a.get_actor_label()]=[c.static_mesh.get_path_name(),str(c.get_collision_enabled()),str(c.static_mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag'))]
  if isinstance(a,(u.Light,u.SkyAtmosphere,u.ExponentialHeightFog,u.PostProcessVolume)):
   p=a.get_actor_location();r=a.get_actor_rotation();item=[a.get_class().get_name(),[p.x,p.y,p.z,r.pitch,r.yaw,r.roll]]
   if isinstance(a,u.Light):
    c=a.light_component;color=c.get_editor_property('light_color');item += [c.get_editor_property('intensity'),[color.r,color.g,color.b,color.a],str(c.get_editor_property('mobility'))]
   lighting[a.get_actor_label()]=item
 return collision,lighting
assert level.load_level(OLD)
if not E.does_asset_exist(CHECK):
 checkpoint=E.duplicate_asset(OLD,CHECK);assert checkpoint;assert E.save_loaded_asset(checkpoint)
hidden_original=hide_karts();assert level.save_current_level()
if not E.does_asset_exist(MAP):assert E.duplicate_asset(OLD,MAP)
assert level.load_level(MAP);hide_karts();before_collision,before_lights=signature()
# Environment preview defaults to an invisible free-fly spectator, never a vehicle.
bp=u.load_asset(BASE+'/BP_DV_EnvironmentPreview')
if not bp:
 f=u.BlueprintFactory();f.set_editor_property('parent_class',u.GameModeBase);bp=T.create_asset('BP_DV_EnvironmentPreview',BASE,u.Blueprint,f)
u.get_default_object(bp.generated_class()).set_editor_property('default_pawn_class',u.SpectatorPawn)
u.BlueprintEditorLibrary.compile_blueprint(bp);E.save_loaded_asset(bp)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',bp.generated_class())
for a in list(actors.get_all_level_actors()):
 if a.get_actor_label().startswith('DV_'):actors.destroy_actor(a)
tasks=[]
for p in (ART/'Textures').glob('*.png'):
 if E.does_asset_exist(BASE+'/Textures/'+p.stem):continue
 t=u.AssetImportTask();t.filename=str(p);t.destination_path=BASE+'/Textures';t.automated=True;t.save=True;tasks.append(t)
T.import_asset_tasks(tasks)
for p in (ART/'Textures').glob('*.png'):
 t=u.load_asset(BASE+'/Textures/'+p.stem)
 if not p.stem.endswith('BaseColor'):
  t.set_editor_property('srgb',False)
  if p.stem.endswith('NormalDX'):t.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
 if p.stem=='RoadMask':t.set_editor_property('address_x',u.TextureAddress.TA_CLAMP);t.set_editor_property('address_y',u.TextureAddress.TA_CLAMP)
 E.save_loaded_asset(t)
def node(m,cls):return L.create_material_expression(m,cls)
def scalar(m,v):n=node(m,u.MaterialExpressionConstant);n.set_editor_property('r',v);return n
def color(m,v):n=node(m,u.MaterialExpressionConstant3Vector);n.set_editor_property('constant',u.LinearColor(*v));return n
def v2(m,x,y):n=node(m,u.MaterialExpressionConstant2Vector);n.set_editor_property('r',x);n.set_editor_property('g',y);return n
def connect(a,b,p,out=''):
 inputs=L.get_material_expression_input_names(b)
 if p not in inputs and len(inputs)==1:p=inputs[0]
 assert L.connect_material_expressions(a,out,b,p),(str(b),p,list(inputs))
def op(m,cls,a,b):n=node(m,cls);connect(a,n,'A');connect(b,n,'B');return n
def mul(m,a,b):return op(m,u.MaterialExpressionMultiply,a,b)
def add(m,a,b):return op(m,u.MaterialExpressionAdd,a,b)
def mask(m,n,channels):
 x=node(m,u.MaterialExpressionComponentMask)
 for p in ['r','g','b','a']:x.set_editor_property(p,p.upper() in channels)
 connect(n,x,'Input');return x
def lerp(m,a,b,t):n=node(m,u.MaterialExpressionLinearInterpolate);connect(a,n,'A');connect(b,n,'B');connect(t,n,'Alpha');return n
def sample(m,name,uv):
 n=node(m,u.MaterialExpressionTextureSample);n.set_editor_property('texture',u.load_asset(BASE+'/Textures/'+name));n.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL if name.endswith('NormalDX') else (u.MaterialSamplerType.SAMPLERTYPE_COLOR if name.endswith('BaseColor') else u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR));connect(uv,n,'UVs');return n
def prop(n,p,out=''):assert L.connect_material_property(n,out,p)
def master(flavor,vertical=False,ground=False):
 name='M_DV_'+flavor+('Wall' if vertical else '')+('Ground' if ground else '');path=BASE+'/Materials/'+name
 m=u.load_asset(path) if E.does_asset_exist(path) else T.create_asset(name,BASE+'/Materials',u.Material,u.MaterialFactoryNew());L.delete_all_material_expressions(m)
 m.set_editor_property('two_sided',True);m.set_editor_property('tangent_space_normal',ground)
 w=node(m,u.MaterialExpressionWorldPosition)
 if flavor!='Asphalt':
  a=add(m,mask(m,w,'R'),mask(m,w,'G'));b=mask(m,w,'B');coords=node(m,u.MaterialExpressionAppendVector);connect(a,coords,'A');connect(b,coords,'B')
  up=mask(m,node(m,u.MaterialExpressionVertexNormalWS),'B');absolute=node(m,u.MaterialExpressionAbs);connect(up,absolute,'Input');coords=lerp(m,coords,mask(m,w,'RG'),absolute)
 else:coords=mask(m,w,'RG')
 uv=mul(m,coords,v2(m,.005,.005))
 tint=node(m,u.MaterialExpressionVectorParameter);tint.set_editor_property('parameter_name','Tint');tint.set_editor_property('default_value',u.LinearColor(1,1,1))
 base=mul(m,sample(m,flavor+'_BaseColor',uv),tint)
 rough=mask(m,sample(m,flavor+'_Roughness',uv),'R')
 if flavor=='Asphalt':
  xy=mask(m,w,'RG');coord=add(m,xy,v2(m,-G['mask_origin_cm'][0],-G['mask_origin_cm'][1]));coord=mul(m,coord,v2(m,1/G['mask_span_cm'][0],1/G['mask_span_cm'][1]));rubber=mask(m,sample(m,'RoadMask',coord),'R')
  base=lerp(m,base,mul(m,base,scalar(m,.35)),rubber);rough=lerp(m,rough,scalar(m,.73),rubber)
 if flavor=='Paint':
  wear=mask(m,sample(m,'Wear',uv),'R');base=lerp(m,base,mul(m,sample(m,'Paint_BaseColor',uv),color(m,[.38,.34,.29])),mul(m,wear,scalar(m,.40)))
 prop(base,u.MaterialProperty.MP_BASE_COLOR);prop(rough,u.MaterialProperty.MP_ROUGHNESS)
 metal=node(m,u.MaterialExpressionScalarParameter);metal.set_editor_property('parameter_name','Metallic');metal.set_editor_property('default_value',0);prop(metal,u.MaterialProperty.MP_METALLIC)
 perturb=add(m,sample(m,flavor+'_NormalDX',uv),color(m,[0,0,-1]));normal=mul(m,node(m,u.MaterialExpressionVertexNormalWS),node(m,u.MaterialExpressionTwoSidedSign));n=add(m,normal,mul(m,perturb,scalar(m,.45 if flavor=='Asphalt' else .20)))
 unit=node(m,u.MaterialExpressionNormalize);connect(n,unit,'Input')
 if not ground:prop(unit,u.MaterialProperty.MP_NORMAL)
 L.recompile_material(m);E.save_loaded_asset(m);return m
masters={k:master(k,k in ['Masonry','Metal','Fabric']) for k in ['Asphalt','Paint','Masonry','Metal','Fabric','Rubber']}
masters['GroundCover']=master('Paint',False,True)
def instance(name,flavor,tint,metal=0):
 path=BASE+'/Materials/MI_DV_'+name;m=u.load_asset(path) if E.does_asset_exist(path) else T.create_asset('MI_DV_'+name,BASE+'/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
 L.set_material_instance_parent(m,masters[flavor]);L.set_material_instance_vector_parameter_value(m,'Tint',u.LinearColor(*tint));L.set_material_instance_scalar_parameter_value(m,'Metallic',metal);E.save_loaded_asset(m);return m
source=json.loads((ROOT/'Art/DesertKarting/manifest.json').read_text())['materials'];mats={}
for name,data in source.items():
 flavor='Masonry' if name in ['cream','stone','sand','sandlight'] else ('Metal' if name in ['metal','glass','dark'] else ('Fabric' if name in ['canvas','shirt','skin'] else ('Rubber' if name in ['rubber','rubbermark'] else ('Asphalt' if name=='asphalt' else 'Paint'))))
 if name in ['grass','grassdark']:flavor='GroundCover'
 tint=data['base'][:3]
 if flavor=='Masonry':tint=[c*.64 for c in tint]
 if name=='asphalt':tint=[.88,.94,1]
 if name in ['rubber','rubbermark']:tint=[.25,.29,.32]
 mats[name]=instance(name,flavor,tint,data['metallic'])
special={'Shutter':('Metal',[.025,.12,.15],.32),'Trim':('Metal',[.022,.055,.075],.40),'Stone':('Masonry',[.58,.39,.20],0),'Metal':('Metal',[.30,.34,.37],.70),'Letter':('Paint',[.85,.82,.70],0),'Dark':('Rubber',[.16,.19,.23],0),'Teal':('Paint',[.025,.38,.29],0),'Ivory':('Paint',[.75,.73,.62],0),'Rubber':('Rubber',[.22,.24,.26],0),'Red':('Paint',[.58,.018,.012],0),'SeatBlue':('Paint',[.018,.16,.42],0),'SeatRed':('Paint',[.62,.025,.018],0),'SeatGold':('Paint',[.94,.44,.035],0),'CapBlue':('Fabric',[.02,.10,.30],0),'CapRed':('Fabric',[.60,.025,.02],0),'CapIvory':('Fabric',[.66,.63,.49],0)}
for name,args in special.items():mats[name]=instance(name,*args)
def override(actor):
 label=actor.get_actor_label()
 if not isinstance(actor,u.StaticMeshActor) or ' | ' not in label:return
 name=label.rsplit(' | ',1)[-1]
 if name in ['lamp','amber']:return # Emissive source fixtures and all lights preserved.
 mat=mats.get(name)
 if mat:actor.static_mesh_component.set_material(0,mat)
# 1: racing surface only; immutable original road mesh/body setup.
for a in actors.get_all_level_actors():
 if a.get_actor_label().startswith(('DK_01 ','DK_02 ','DK_03 ')):override(a)
assert signature()==(before_collision,before_lights)
assert level.save_current_level();(EV/'01_Track.json').write_text(json.dumps({'complete':True,'road_geometry_and_collision_unchanged':True,'world_tile_cm':200,'new_pbr_sets':6},indent=2))
# Import visual-only meshes. All new geometry is nonblocking.
tasks=[]
for a in G['assets']:
 if E.does_asset_exist(BASE+'/Meshes/'+a['name']):continue
 t=u.AssetImportTask();t.filename=str(ART/'Meshes'/(a['name']+'.fbx'));t.destination_path=BASE+'/Meshes';t.automated=True;t.save=True
 o=u.FbxImportUI();o.automated_import_should_detect_type=False;o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;o.import_materials=False;o.import_textures=False;o.static_mesh_import_data.set_editor_property('combine_meshes',True);o.static_mesh_import_data.set_editor_property('auto_generate_collision',False);o.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False);t.options=o;tasks.append(t)
T.import_asset_tasks(tasks)
meshes={}
for a in G['assets']:
 m=u.load_asset(BASE+'/Meshes/'+a['name']);assert m,a['name']
 for i,s in enumerate(a['slots']):
  if s in mats:m.set_material(i,mats[s])
 E.save_loaded_asset(m);meshes[a['name']]=m
counts={};types={}
def instances(names):
 for name in names:
  entries=[p for p in G['placements'] if p['mesh']==name]
  if not entries:continue
  path=BASE+'/Instancing/FT_'+name;f=u.load_asset(path) if E.does_asset_exist(path) else T.create_asset('FT_'+name,BASE+'/Instancing',u.FoliageType_InstancedStaticMesh,u.FoliageType_InstancedStaticMeshFactory())
  u.InstancedFoliageActor.remove_all_instances(world,f);f.set_editor_property('mesh',meshes[name]);body=f.get_editor_property('body_instance');body.set_editor_property('collision_enabled',u.CollisionEnabled.NO_COLLISION);body.set_editor_property('collision_profile_name','NoCollision');f.set_editor_property('body_instance',body);f.set_editor_property('collision_with_world',False);f.set_editor_property('cull_distance',u.Int32Interval(min=18000,max=35000));E.save_loaded_asset(f)
  ts=[u.Transform(location=u.Vector(*p['location_cm']),rotation=u.Rotator(yaw=p['yaw']),scale=u.Vector(*p['scale'])) for p in entries]
  u.InstancedFoliageActor.add_instances(world,f,ts);counts[name]=len(entries);types[name]=path
def replace_and_shade(prefixes):
 for a in list(actors.get_all_level_actors()):
  label=a.get_actor_label()
  if not label.startswith(prefixes):continue
  override(a);key=label.removeprefix('DK_')
  if key not in G['replacements']:continue
  # Original collision and source mesh remain on the invisible source actor.
  a.static_mesh_component.set_visibility(False,True);nm=G['replacements'][key]
  if nm:
   b=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector());b.set_actor_label('DV_'+key);b.set_folder_path('VisualUpgrade/Geometry');b.static_mesh_component.set_static_mesh(meshes[nm]);b.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
# 2: pit buildings and paddock, then 3: safety/service props, then 4: stands.
replace_and_shade(('DK_07 ','DK_09 ','DK_06 '));instances(['SM_DV_PitBay','SM_DV_Banner'])
assert signature()==(before_collision,before_lights);assert level.save_current_level();(EV/'02_Pit.json').write_text(json.dumps({'complete':True,'bevel_width_m':.025,'pit_modules':counts.get('SM_DV_PitBay',0)},indent=2))
replace_and_shade(('DK_04 ','DK_12 ','DK_13 ','DK_14 '));instances(['SM_DV_BarrierTeal','SM_DV_BarrierIvory','SM_DV_ToolChest','SM_DV_TireStack','SM_DV_Drain','SM_DV_Extinguisher','SM_DV_PitSignPod'])
assert signature()==(before_collision,before_lights);assert level.save_current_level();(EV/'03_Props.json').write_text(json.dumps({'complete':True,'barrier_replacements':G['barrier_count'],'instances':dict(counts)},indent=2))
replace_and_shade(('DK_05 ',));instances(['SM_DV_SeatBlue','SM_DV_SeatRed','SM_DV_SeatGold','SM_DV_CapBlue','SM_DV_CapRed','SM_DV_CapIvory'])
assert signature()==(before_collision,before_lights);assert level.save_current_level();assert level.load_level(MAP)
actual=collections.Counter();visible_karts=[]
for a in actors.get_all_level_actors():
 if kart(a) and any(c.is_visible() for c in a.get_components_by_class(u.PrimitiveComponent)):visible_karts.append(a.get_actor_label())
 for c in a.get_components_by_class(u.HierarchicalInstancedStaticMeshComponent):
  if c.static_mesh and c.static_mesh.get_name() in counts:actual[c.static_mesh.get_name()]+=c.get_instance_count()
assert dict(actual)==counts,(actual,counts);assert not visible_karts,visible_karts
hashcheck()
report={'map':MAP,'checkpoint':CHECK,'original_map_change':'Kart actors hidden only; original driving game mode retained','hidden_original_kart_actors':hidden_original,'visible_kart_actors_after_reload':visible_karts,'environment_default_pawn':'SpectatorPawn (invisible, no vehicle spawning)','lighting_unchanged':True,'original_collision_signature':before_collision,'lighting_signature':before_lights,'instances':counts,'mesh_assets':len(meshes),'new_mesh_triangles':sum(a['triangles'] for a in G['assets']),'protected_hashes':protected,'remaining_placeholders':['Source spectators retain simple bodies/heads; new seat backs and cap variety improve distance presentation','Source palms/shrubs and parked road cars retain original silhouettes','Garage shutters have modeled relief; no new garage interiors','Perimeter fence retains original wire spacing'],'sources':G['sources'],'render_inspected':False}
(EV/'04_Stands.json').write_text(json.dumps({'complete':True,'instances':counts,'saved_and_reloaded':True},indent=2));(EV/'implementation.json').write_text(json.dumps(report,indent=2))
u.log('DESERT_VISUAL_FOUR_PRIORITIES_COMPLETE')

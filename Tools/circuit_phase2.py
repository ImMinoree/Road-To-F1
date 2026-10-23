"""Phase 2 only: new material assets and actor overrides on the actual circuit."""
import unreal as u,json,hashlib,shutil
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EVIDENCE=ROOT/'Evidence/CircuitDevelopment';WORK=ROOT/'Art/CircuitDevelopment'
assert json.loads((EVIDENCE/'phase1.json').read_text())['gate_passed']
assert not (EVIDENCE/'phase2.json').exists() or not json.loads((EVIDENCE/'phase2.json').read_text()).get('gate_passed'),'Accepted material pass preserved'
BASE='/Game/RoadToF1/CircuitDevelopment';MAP='/Game/RoadToF1/Maps/CircuitDevelopment';E=u.EditorAssetLibrary;L=u.MaterialEditingLibrary;tools=u.AssetToolsHelpers.get_asset_tools()
assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
actors=u.get_editor_subsystem(u.EditorActorSubsystem);original=ROOT/'Content/RoadToF1/Maps/VisualProof.umap';original_sha=hashlib.sha256(original.read_bytes()).hexdigest()
tasks=[]
for p in (WORK/'Textures').glob('*.png'):
 if E.does_asset_exist(BASE+'/Textures/'+p.stem):continue
 t=u.AssetImportTask();t.filename=str(p);t.destination_path=BASE+'/Textures';t.automated=True;t.save=True;t.replace_existing=True;tasks.append(t)
tools.import_asset_tasks(tasks)
for p in (WORK/'Textures').glob('*.png'):
 tex=u.load_asset(BASE+'/Textures/'+p.stem)
 if 'BaseColor' not in p.stem:
  tex.set_editor_property('srgb',False)
  if p.stem.endswith('NormalDX'):tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
 if p.stem=='TrackMask':
  tex.set_editor_property('address_x',u.TextureAddress.TA_CLAMP);tex.set_editor_property('address_y',u.TextureAddress.TA_CLAMP)
 E.save_loaded_asset(tex)
meta=json.loads((WORK/'Textures/provenance.json').read_text())
def mat(name):
 m=u.load_asset(BASE+'/Materials/'+name) if E.does_asset_exist(BASE+'/Materials/'+name) else tools.create_asset(name,BASE+'/Materials',u.Material,u.MaterialFactoryNew())
 L.delete_all_material_expressions(m);return m
def node(m,cls):return L.create_material_expression(m,cls)
def scalar(m,v):
 n=node(m,u.MaterialExpressionConstant);n.set_editor_property('r',v);return n
def color(m,c):
 n=node(m,u.MaterialExpressionConstant3Vector);n.set_editor_property('constant',u.LinearColor(*c));return n
def vector2(m,a,b):
 n=node(m,u.MaterialExpressionConstant2Vector);n.set_editor_property('r',a);n.set_editor_property('g',b);return n
def connect(a,b,pin,out=''):
 inputs=L.get_material_expression_input_names(b)
 if pin=='Coordinates' and pin not in inputs and inputs:pin=inputs[0]
 if pin not in inputs and len(inputs)==1:pin=inputs[0]
 assert L.connect_material_expressions(a,out,b,pin),(b.get_class().get_name(),pin,list(inputs))
def op(m,cls,a,b):
 n=node(m,cls);connect(a,n,'A');connect(b,n,'B');return n
def mul(m,a,b):return op(m,u.MaterialExpressionMultiply,a,b)
def add(m,a,b):return op(m,u.MaterialExpressionAdd,a,b)
def lerp(m,a,b,t):
 n=node(m,u.MaterialExpressionLinearInterpolate);connect(a,n,'A');connect(b,n,'B');connect(t,n,'Alpha');return n
def sample(m,name,uv=None):
 path=('/Game/RoadToF1/Textures/' if name.startswith('asphalt_track') else BASE+'/Textures/')+name
 tex=u.load_asset(path);assert tex,path;n=node(m,u.MaterialExpressionTextureSample);n.set_editor_property('texture',tex)
 n.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL if ('NormalDX' in name or 'nor_dx' in name) else (u.MaterialSamplerType.SAMPLERTYPE_COLOR if ('BaseColor' in name or 'diff' in name) else u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR))
 if uv:connect(uv,n,'Coordinates')
 return n
def channel(m,n,name):
 c=node(m,u.MaterialExpressionComponentMask)
 for p in ['r','g','b','a']:c.set_editor_property(p,p.upper() in name)
 connect(n,c,'Input');return c
def worlduv(m,size,origin=(0,0)):
 w=node(m,u.MaterialExpressionWorldPosition);xy=channel(m,w,'RG')
 offset=add(m,xy,vector2(m,-origin[0],-origin[1]))
 return mul(m,offset,vector2(m,1/size[0],1/size[1]))
def atlas(m):return sample(m,'TrackMask',worlduv(m,meta['world_mask_size_cm'],meta['world_mask_origin_cm']))
def prop(n,p,out=''):assert L.connect_material_property(n,out,p)
def finish(m):L.recompile_material(m);E.save_loaded_asset(m);return m
def softened_normal(m,name,strength,uv=None):
 n=mul(m,sample(m,name,uv),color(m,[strength,strength,1]));unit=node(m,u.MaterialExpressionNormalize);connect(n,unit,'Input');return unit
asphalt=mat('M_CD_Asphalt');m=asphalt;mask=atlas(m)
base=sample(m,'asphalt_track_diff_1k');rubber=channel(m,mask,'R');patch=channel(m,mask,'G')
base=mul(m,base,color(m,[.74,.76,.78]));base=lerp(m,base,mul(m,base,scalar(m,.55)),rubber);base=lerp(m,base,mul(m,base,color(m,[.72,.73,.75])),patch)
prop(base,u.MaterialProperty.MP_BASE_COLOR);prop(sample(m,'asphalt_track_nor_dx_1k'),u.MaterialProperty.MP_NORMAL,'RGB')
rough=sample(m,'asphalt_track_rough_1k');prop(lerp(m,channel(m,rough,'R'),scalar(m,.56),rubber),u.MaterialProperty.MP_ROUGHNESS);finish(m)
curbs=[]
for name,tint in [('M_CD_CurbRed',[.26,.025,.018]),('M_CD_CurbWhite',[.44,.42,.38])]:
 m=mat(name);wear=channel(m,sample(m,'PaintWear'),'R');concrete=sample(m,'Concrete_BaseColor');paint=mul(m,color(m,tint),add(m,scalar(m,.8),mul(m,channel(m,concrete,'R'),scalar(m,.4))))
 prop(lerp(m,paint,concrete,wear),u.MaterialProperty.MP_BASE_COLOR);prop(softened_normal(m,'Concrete_NormalDX',.15),u.MaterialProperty.MP_NORMAL);prop(sample(m,'Concrete_Roughness'),u.MaterialProperty.MP_ROUGHNESS,'R');curbs.append(finish(m))
m=mat('M_CD_Runoff');prop(sample(m,'Gravel_BaseColor'),u.MaterialProperty.MP_BASE_COLOR,'RGB');prop(softened_normal(m,'Gravel_NormalDX',.4),u.MaterialProperty.MP_NORMAL);prop(sample(m,'Gravel_Roughness'),u.MaterialProperty.MP_ROUGHNESS,'R');gravel=finish(m)
m=mat('M_CD_GrassSoil');uv=worlduv(m,[200,200]);mask=channel(m,atlas(m),'B')
for suffix,p in [('BaseColor',u.MaterialProperty.MP_BASE_COLOR),('NormalDX',u.MaterialProperty.MP_NORMAL),('Roughness',u.MaterialProperty.MP_ROUGHNESS)]:
 soil=sample(m,'Soil_'+suffix,uv);sward=sample(m,'Sward_'+suffix,uv)
 a=channel(m,soil,'R') if suffix=='Roughness' else soil;b=channel(m,sward,'R') if suffix=='Roughness' else sward
 blended=lerp(m,a,b,mask)
 if suffix=='BaseColor':
  large_uv=worlduv(m,[1379,1531],[59,-137]);large=lerp(m,sample(m,'Soil_BaseColor',large_uv),sample(m,'Sward_BaseColor',large_uv),mask)
  blended=mul(m,lerp(m,blended,large,scalar(m,.55)),color(m,[.68,.68,.65]))
 elif suffix=='NormalDX':
  blended=mul(m,blended,color(m,[.45,.45,1]));unit=node(m,u.MaterialExpressionNormalize);connect(blended,unit,'Input');blended=unit
 prop(blended,p)
terrain=finish(m)
counts={}
for a in actors.get_all_level_actors():
 if not isinstance(a,u.StaticMeshActor) or not a.get_actor_label().startswith('CD_'):continue
 name=a.get_actor_label()[3:];comp=a.static_mesh_component
 if name.startswith('Road_'):comp.set_material(0,asphalt)
 elif name.startswith('Shoulder'):comp.set_material(0,gravel)
 elif name.startswith('Curbs'):
  comp.set_material(0,curbs[0]);comp.set_material(1,curbs[1])
 elif name.startswith('Terrain_'):comp.set_material(0,terrain)
 counts[name]=[comp.get_material(i).get_path_name() for i in range(comp.get_num_materials())]
assert len(counts)==82,len(counts)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
assert hashlib.sha256(original.read_bytes()).hexdigest()==original_sha
(EVIDENCE/'phase2.json').write_text(json.dumps({'map':MAP,'materials_saved':True,'assigned_meshes':len(counts),'assignments':counts,'tile_m':2,'textures':'Existing Poly Haven asphalt complete PBR plus original authored concrete/gravel/soil/sward sets; no marketplace imports','render_inspected':False,'gate_passed':False},indent=2))
u.log('PHASE2_MATERIALS_SAVED')

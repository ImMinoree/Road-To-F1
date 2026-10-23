"""Run in the open Unreal Editor: Tools > Execute Python Script > this file.
Imports the standalone, component-separated kart as Static Mesh assets in a new folder.
It does not create a level or modify an existing map/gameplay actor.
"""
import unreal as u, json
from pathlib import Path

ROOT=Path(u.Paths.project_dir()).resolve()
FBX=ROOT/'Art/DesertKarting/Kart/Exports/SM_Kart_Reference.fbx'
OUT='/Game/RoadToF1/DesertKarting/Kart'
assert FBX.is_file(),FBX
tasks=[]
t=u.AssetImportTask();t.filename=str(FBX);t.destination_path=OUT
t.automated=True;t.save=True;t.replace_existing=True
o=u.FbxImportUI();o.automated_import_should_detect_type=False
o.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
o.import_materials=True;o.import_textures=True
o.static_mesh_import_data.set_editor_property('combine_meshes',False)
o.static_mesh_import_data.set_editor_property('auto_generate_collision',False)
o.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',True)
t.options=o;tasks.append(t)
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
paths=list(t.imported_object_paths)
assert paths,'Unreal did not import any objects from '+str(FBX)
missing=[p for p in paths if not u.EditorAssetLibrary.does_asset_exist(p)]
assert not missing,missing
manifest=json.loads((FBX.parent.parent/'kart_manifest.json').read_text())
report={'fbx':str(FBX),'destination':OUT,'imported_assets':paths,'mesh_object_count':len(paths),'source_triangles':manifest['triangles'],'dimensions_m':{'length':manifest['overall_length_m'],'wheelbase':manifest['wheelbase_m'],'width':manifest['overall_width_m']},'materials_and_textures':'Import from the FBX embedded PBR texture maps; review the imported material instances in Unreal after import.','gameplay':'Wheel and component mesh pivots are exported separately. Create/attach a Blueprint and configure wheel collision and physics for gameplay.'}
ev=ROOT/'Evidence/DesertKarting';ev.mkdir(parents=True,exist_ok=True)
(ev/'KartImport.json').write_text(json.dumps(report,indent=2))
u.log('KART_IMPORT_COMPLETE: '+json.dumps({'destination':OUT,'assets':len(paths)}))

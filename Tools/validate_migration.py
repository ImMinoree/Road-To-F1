"""Verify the migrated level and repair source paths for future reimports."""
import unreal as u
import json
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve()
assert root.name=='Road_To_F1_New',str(root)
assert u.load_class(None,'/Script/Road_To_F1_New.ProofPawn')
assert u.load_class(None,'/Script/Road_To_F1_New.ProofGameMode')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/RoadToF1/Maps/VisualProof')
updated=[]
for folder,source,extension in [('Meshes','Exports','.fbx'),('Textures','Textures','.jpg')]:
    for path in u.EditorAssetLibrary.list_assets('/Game/RoadToF1/'+folder,recursive=True,include_folder=False):
        asset=u.load_asset(path)
        source_path=root/'Art'/source/(asset.get_name()+extension)
        assert source_path.is_file(),str(source_path)
        data=asset.get_editor_property('asset_import_data')
        data.scripted_add_filename(str(source_path),0,'')
        u.EditorAssetLibrary.save_loaded_asset(asset)
        updated.append(str(source_path))
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
labels=[a.get_actor_label() for a in actors]
assert all(x in labels for x in ['Road','CurbLeft','CurbRight','VergeLeft','VergeRight'])
(root/'Evidence'/'MigrationValidation.json').write_text(json.dumps({'project':str(root),'map':'/Game/RoadToF1/Maps/VisualProof','classes_loaded':True,'actors':labels,'reimport_sources':updated},indent=2))
u.log('MIGRATION_VALIDATION_PASSED')

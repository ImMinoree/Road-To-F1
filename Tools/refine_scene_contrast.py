"""Small reversible global color-contrast adjustment; preserves all scene actors."""
import unreal as u,json,shutil
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/ContrastRefinement';L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem)
mapfile=R/'Content/RoadToF1/Maps/DesertKarting_Visual.umap';backup=E/'Checkpoint/DesertKarting_Visual.umap'
assert not backup.exists(),'Do not apply twice; checkpoint already exists'
shutil.copy2(mapfile,backup)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
volumes=[a for a in A.get_all_level_actors() if isinstance(a,u.PostProcessVolume) and a.get_editor_property('enabled') and a.get_editor_property('unbound')]
assert volumes,'Expected the existing global color-grading volume'
p=max(volumes,key=lambda a:a.get_editor_property('priority'));s=p.get_editor_property('settings');old=s.get_editor_property('color_contrast');old_override=s.get_editor_property('override_color_contrast')
new=u.Vector4(old.x*.94,old.y*.94,old.z*.94,old.w)
report={'volume':p.get_actor_label(),'old_override':old_override,'before':[old.x,old.y,old.z,old.w],'after':[new.x,new.y,new.z,new.w],'contrast_scale':.94}
s.set_editor_property('override_color_contrast',True);s.set_editor_property('color_contrast',new);p.set_editor_property('settings',s);assert L.save_current_level();assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
(E/'contrast.json').write_text(json.dumps(report,indent=2));u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')

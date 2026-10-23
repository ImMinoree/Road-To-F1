import unreal as u,traceback
from pathlib import Path
r=Path(u.Paths.project_dir()).resolve()
try:
    exec(compile((r/'Tools/desert_grass_import.py').read_text(),'desert_grass_import.py','exec'),globals())
    exec(compile((r/'Tools/desert_grass_capture.py').read_text(),'desert_grass_capture.py','exec'),globals())
except Exception:
    (r/'Evidence/InfieldGrass/import_error.txt').write_text(traceback.format_exc())
    u.log_error(traceback.format_exc());u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')

"""Run through the live Unreal Editor, where mesh/physics subsystems exist."""
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
try:
 for script in ['tire_barriers_import.py','tire_barriers_place_validate.py']:
  p=root/'Tools'/script;exec(compile(p.read_text(),str(p),'exec'),globals())
except Exception:
 import traceback
 (root/'Evidence/TireBarriers/run_error.txt').write_text(traceback.format_exc())
 u.log_error(traceback.format_exc());u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')

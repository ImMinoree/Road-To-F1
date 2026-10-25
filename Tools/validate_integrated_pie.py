"""Repeat save/reload and PIE validation using the already imported assets."""
import unreal as u, json, time, traceback
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();EV=ROOT/'Evidence/Integration'
u.EditorPythonScripting.set_keep_python_script_alive(True)
mesh=u.load_asset('/Game/RoadToF1/PlayerVisuals/FirstPerson/SM_PlayerKartChassis');assert mesh
source=(ROOT/'Tools/integrate_kart_unreal.py').read_text()
# Share exactly the same map-preservation and PIE checks without reimporting art.
exec(compile(source[source.index('\nlevel=u.get_editor_subsystem')+1:],str(ROOT/'Tools/integrate_kart_unreal.py'),'exec'))

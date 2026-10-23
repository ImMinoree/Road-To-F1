from pathlib import Path
import unreal
folder=Path(unreal.Paths.project_dir()).resolve()/'Tools'
exec(compile((folder/'build_scene.py').read_text(),str(folder/'build_scene.py'),'exec'))
exec(compile((folder/'capture_scene.py').read_text(),str(folder/'capture_scene.py'),'exec'))

"""Render the current cleared visual map from the repeatable orthographic camera."""
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
src=(root/'Tools/desert_route_capture.py').read_text()
src=src.replace("EV=ROOT/'Evidence/DesertRoute'", "EV=ROOT/'Evidence/DesertClearance'")
src=src.replace("maps=['/Game/RoadToF1/Maps/DesertKarting','/Game/RoadToF1/Maps/DesertKarting_Visual']", "maps=['/Game/RoadToF1/Maps/DesertKarting_Visual']")
src=src.replace("reports[mp]=validate()", "reports[mp]={}")
src=src.replace("phase='After' if after else 'Before'", "phase='Current'")
exec(compile(src,__file__,'exec'))

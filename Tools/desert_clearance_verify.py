"""Run full-loop collision checks in a live editor world after map loading."""
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
src=(root/'Tools/desert_route_capture.py').read_text()
src=src.replace("EV=ROOT/'Evidence/DesertRoute'", "EV=ROOT/'Evidence/DesertClearance'")
src=src.replace("verify_only='-RouteVerifyOnly' in u.SystemLibrary.get_command_line()", 'verify_only=True')
src=src.replace("reports[mp]=validate()", "reports[mp]={}")
src=src.replace("if verify_only and time.monotonic()-state['start']>3:", "if verify_only and time.monotonic()-state['start']>5:\n   reports[maps[state['i']]]=validate()")
exec(compile(src,__file__,'exec'))


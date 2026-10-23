"""Repeatable golden-hour render review and live racing-loop validation."""
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
src=(root/'Tools/desert_open_infield_capture.py').read_text()
src=src.replace("EV=ROOT/'Evidence/DesertOpenInfield'", "EV=ROOT/'Evidence/DesertGoldenHour'")
src=src.replace("('DesertKarting_Visual','Driver')]", "('DesertKarting_Visual','Driver'),('DesertKarting_Visual','Corner')]")
start=src.index("  c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(2500")
end=src.index("\n else:",start)
src=src[:start]+"  c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(22000,13000,20000),u.Rotator(pitch=-34,yaw=-136));c.camera_component.set_field_of_view(75);size=(2400,1600)"+src[end:]
needle=" else:\n  c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(-3600"
replace=" elif view=='Corner':\n  import math\n  pts=scope['g']['route_cm'];p=pts[170];q=pts[177];yaw=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(p[0],p[1],85),u.Rotator(pitch=-4,yaw=yaw));c.camera_component.set_field_of_view(85);size=(1920,1080)\n else:\n  c=actors.spawn_actor_from_class(u.CameraActor,u.Vector(-3600"
src=src.replace(needle,replace)
exec(compile(src,__file__,'exec'))

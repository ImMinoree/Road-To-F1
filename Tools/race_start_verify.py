"""Read back the saved start actors and run existing live loop-clearance probes."""
from pathlib import Path
import unreal as u,json
root=Path(u.Paths.project_dir()).resolve()
src=(root/'Tools/desert_route_capture.py').read_text().replace("EV=ROOT/'Evidence/DesertRoute'","EV=ROOT/'Evidence/RaceStart'").replace("verify_only='-RouteVerifyOnly' in u.SystemLibrary.get_command_line()",'verify_only=True')
src=src.replace('reports[mp]=validate()','reports[mp]={}')
src=src.replace("if verify_only and time.monotonic()-state['start']>3:","if verify_only and time.monotonic()-state['start']>5:\n   result=validate();gantries=[a for a in actors.get_all_level_actors() if isinstance(a,u.RaceStartGantry)];assert len(gantries)==1\n   g=gantries[0];assert not g.get_actor_enable_collision();assert g.get_editor_property('housing_mesh') and g.get_editor_property('lens_material')\n   starts=[a for a in actors.get_all_level_actors() if isinstance(a,u.PlayerStart) and 'RaceGridStart' in [str(t) for t in a.tags]];assert len(starts)==1\n   result['start_system']={'gantry_count':len(gantries),'stage':str(starts[0].get_actor_location()),'preview_reds':g.get_editor_property('preview_red_lights'),'game_mode':str(editor.get_editor_world().get_world_settings().get_editor_property('default_game_mode'))}\n   reports[maps[state['i']]]=result")
exec(compile(src,__file__,'exec'))

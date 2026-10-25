import unreal as u,json
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve();data=json.loads((root/'Art/RacingAI/track_edges.json').read_text())
route=u.load_asset('/Game/RoadToF1/RacingAI/DA_DesertTrackEdges');assert route
for key in ['center','left','right','guide']:route.set_editor_property(key,[u.Vector(*p) for p in data[key]])
u.EditorAssetLibrary.save_loaded_asset(route);u.log('AI_ROUTE_UPDATED')

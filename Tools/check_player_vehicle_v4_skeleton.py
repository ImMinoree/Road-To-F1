import unreal as u,json
from pathlib import Path
O='/Game/RoadToF1/PlayerVehicleV4';result={}
for name in ['SK_V4_DriverFull','SK_V4_DriverPOV','A_V4_Steering']:
 a=u.load_asset(O+'/'+name);sk=a.get_editor_property('skeleton');result[name]=sk.get_path_name() if sk else None
Path(u.Paths.project_dir(),'Evidence/PlayerVehicle_v4/skeleton_reload.json').write_text(json.dumps(result,indent=2));assert all(result.values()),result;u.log('V4_SKELETON_RELOAD_PASS')

import unreal as u,json
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();src=(R/'Tools/import_player_vehicle_v4.py').read_text();exec(src[:src.index("full=imp('SK_V4_DriverFull'")])
a=u.load_asset(O+'/SK_V4_DriverFull');sk=a.get_editor_property('skeleton');mats={str(slot.material_slot_name):slot.material_interface for slot in a.get_editor_property('materials')};a=imp('SK_V4_DriverFull',True,sk);slots=list(a.get_editor_property('materials'))
for slot in slots:slot.material_interface=mats[str(slot.material_slot_name)]
a.set_editor_property('materials',slots);assert u.EditorAssetLibrary.save_loaded_asset(a);u.log('V4_DRIVER_FINISHED')

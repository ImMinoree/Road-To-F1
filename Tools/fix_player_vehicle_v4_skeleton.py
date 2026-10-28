import unreal as u
O='/Game/RoadToF1/PlayerVehicleV4';path=O+'/SK_V4_DriverFull_Skeleton'
sk=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else u.EditorAssetLibrary.duplicate_asset('/Game/RoadToF1/PlayerVisuals/CockpitLayoutV5/SK_CL5_DriverPOV_Skeleton',path)
assert sk;assert u.EditorAssetLibrary.save_loaded_asset(sk)
for name in ['SK_V4_DriverFull','SK_V4_DriverPOV','A_V4_Steering']:
 asset=u.load_asset(O+'/'+name);assert asset.get_editor_property('skeleton')==sk
u.log('V4_PERSISTENT_SKELETON_FIXED')


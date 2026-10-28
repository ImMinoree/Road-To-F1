"""Versioned mechanical PBR materials; never edits the reused source materials."""
import unreal as u
O='/Game/RoadToF1/PlayerVehicleV4';M=u.MaterialEditingLibrary
def copy(name,source):
 path=O+'/Materials/'+name
 a=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else u.EditorAssetLibrary.duplicate_asset(source,path)
 assert a;M.set_material_usage(a,u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);M.recompile_material(a);assert u.EditorAssetLibrary.save_loaded_asset(a);return a
metal=copy('M_V4_MechanicalMetal','/Game/RoadToF1/PlayerVisuals/CockpitTargetV4/M_CT4_SatinAlloy')
dark=copy('M_V4_Anodised','/Game/RoadToF1/PlayerVisuals/CockpitTargetV4/M_CT4_Anodised')
for name in ['Column','Pitman','TieRod','KnuckleFL','KnuckleFR','RearAxle','Sprocket','BrakeDisc','Caliper','Pedall','Pedalr','ChainLink']:
 mesh=u.load_asset(O+'/SM_V4_'+name);assert mesh
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):mesh.set_material(i,dark if name=='Caliper' else metal)
 assert u.EditorAssetLibrary.save_loaded_asset(mesh)
u.log('V4_MECHANICAL_MATERIALS_SAVED')

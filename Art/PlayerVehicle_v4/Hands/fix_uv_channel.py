import bpy
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'));bpy.context.scene.frame_set(25);rig=bpy.data.objects['FP_KartArms_Rig']
for name in ['SK_V4_DriverFull','SK_V4_DriverPOV']:
 o=bpy.data.objects[name];src=o.data.uv_layers.get('UVMap');dst=o.data.uv_layers[0];count=0
 for f in o.data.polygons:
  if any(src.data[i].uv.length_squared>0 for i in f.loop_indices):
   for i in f.loop_indices:dst.data[i].uv=src.data[i].uv;count+=1
 print(name,'copied glove UV loops',count)
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(P/'Exports'/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'))

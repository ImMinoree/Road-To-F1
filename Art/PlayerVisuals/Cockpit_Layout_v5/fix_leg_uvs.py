import bpy
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));o=bpy.data.objects['SK_CL5_DriverPOV'];r=bpy.data.objects['FP_KartArms_Rig'];a=o.data.uv_layers[0];src=o.data.uv_layers['SourceUV'];pad=o.data.uv_layers['UV_FP_Pads'];count=0
for p in o.data.polygons:
 name=o.data.materials[p.material_index].name
 layer=src if name in ['M_CT4_LegNomex','M_CT4_PalmSuede'] else None
 if layer:
  for li in p.loop_indices:a.data[li].uv=layer.data[li].uv;count+=1
print('RESTORED_LEG_BOOT_UV_LOOPS',count);a.active_render=True;o.data.uv_layers.active_index=0;bpy.context.scene.frame_set(25);bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));bpy.ops.object.select_all(action='DESELECT');o.select_set(True);r.select_set(True);bpy.context.view_layer.objects.active=r
bpy.ops.export_scene.fbx(filepath=str(P/'Exports/SK_CL5_DriverPOV.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,mesh_smooth_type='FACE',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0)

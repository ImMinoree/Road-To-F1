import bpy,math
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Reference_v2.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CV2_DriverPOV'];s.frame_set(25)
for v in o.data.vertices:
 side='l' if v.co.y>0 else 'r';tw=sum(g.weight for g in v.groups if o.vertex_groups[g.group].name=='thigh_'+side)
 if tw<=0:continue
 H=(r.matrix_world@r.data.bones['thigh_'+side].matrix_local).translation;K=(r.matrix_world@r.data.bones['calf_'+side].matrix_local).translation;D=K-H;t=max(0,min(1,(v.co-H).dot(D)/D.length_squared));axis=H+D*t;v.co.y-=(v.co.y-axis.y)*.17*tw
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Reference_v2.blend'));bpy.ops.object.select_all(action='DESELECT');o.select_set(True);r.select_set(True);bpy.context.view_layer.objects.active=r
bpy.ops.export_scene.fbx(filepath=str(P/'Exports/SK_CV2_DriverPOV.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,mesh_smooth_type='FACE',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
print('CLOTH_THIGH_CLEARANCE_EXPORT_COMPLETE',flush=True)

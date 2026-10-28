"""Export smooth posed glove normals through inverse linear skinning for UE.

The grip was modeled in its seated pose, then inverse-skinned. Computing
normals on that folded bind shape produces lighting cracks despite a smooth
posed surface. Preserve original normals outside the new gloves.
"""
import bpy
import numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'))
bpy.context.scene.frame_set(25)
rig=bpy.data.objects['FP_KartArms_Rig']
for name in ['SK_V4_DriverFull','SK_V4_DriverPOV']:
 o=bpy.data.objects[name];o.hide_set(False)
 bpy.context.view_layer.update()
 evaluated=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
 assert len(evaluated.vertices)==len(o.data.vertices)
 # Geometric normals from the actual posed surface, not deformed bind normals.
 surface=bpy.data.meshes.new('GripNormalReference')
 surface.from_pydata([v.co[:] for v in evaluated.vertices],[],[list(p.vertices) for p in evaluated.polygons])
 surface.update()
 transforms={g.index:np.array(o.matrix_world.inverted()@rig.matrix_world@rig.pose.bones[g.name].matrix@rig.data.bones[g.name].matrix_local.inverted()@rig.matrix_world.inverted()@o.matrix_world)[:3,:3] for g in o.vertex_groups if g.name in rig.pose.bones}
 prefix=('hand_','thumb_','index_','middle_','ring_','pinky_')
 corrected={}
 for v in o.data.vertices:
  if sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(prefix))<.99:continue
  weights=[g for g in v.groups if g.group in transforms]
  matrix=sum((transforms[g.group]*g.weight for g in weights),np.zeros((3,3)))/sum(g.weight for g in weights)
  normal=np.linalg.solve(matrix,np.array(surface.vertices[v.index].normal))
  normal/=max(np.linalg.norm(normal),1e-10)
  corrected[v.index]=normal.tolist()
 normals=[corrected.get(loop.vertex_index,o.data.corner_normals[loop.index].vector[:]) for loop in o.data.loops]
 o.data.normals_split_custom_set(normals)
 bpy.data.meshes.remove(surface)
 o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
 print(name,'corrected glove vertices',len(corrected),flush=True)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(P/'Exports'/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,mesh_smooth_type='FACE')
# Keep the canonical Blender modeling file untouched; this is an export variant.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Hands/PlayerVehicle_v4_ExportNormals.blend'))

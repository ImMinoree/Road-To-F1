"""Update mechanical materials and normalized exports without rebuilding driver geometry."""
import bpy
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'))
bpy.context.scene.frame_set(25)
for name in ['Column','Pitman','TieRod','KnuckleFL','KnuckleFR','RearAxle','Sprocket','BrakeDisc','Caliper','Pedall','Pedalr','ChainLink']:
 o=bpy.data.objects['SM_V4_'+name]
 for i in range(len(o.data.materials)):o.data.materials[i]=bpy.data.materials['M_CT4_Anodised' if name=='Caliper' else 'M_CT4_SatinAlloy']
 # A data-sharing temporary object exports just the pivot-local geometry.
 c=bpy.data.objects.new(o.name+'_Export',o.data);bpy.context.scene.collection.objects.link(c)
 bpy.ops.object.select_all(action='DESELECT');c.select_set(True);bpy.context.view_layer.objects.active=c
 bpy.ops.export_scene.fbx(filepath=str(P/'Exports'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',bake_anim=False,mesh_smooth_type='FACE')
 bpy.data.objects.remove(c,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'PlayerVehicle_v4.blend'))

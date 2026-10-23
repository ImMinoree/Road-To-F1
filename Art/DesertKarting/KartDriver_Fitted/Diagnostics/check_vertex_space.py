import bpy,os
from mathutils import Matrix
root=r'D:\Boring\GitHub\Road-To-F1-New\Road_To_F1_New\Art\HumanBase'
bpy.ops.wm.open_mainfile(filepath=root+'/KartDriver_Base.blend')
base=bpy.data.objects['kart_driverMesh']
print('BASE', [list(v.co) for v in list(base.data.vertices)[:3]])
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=root+'/KartDriver_Rigged.fbx')
for o in set(bpy.data.objects)-before:
 if o.type=='MESH':print('SOURCE',o.name, [list(v.co) for v in list(o.data.vertices)[:3]],'GROUPS',len(o.vertex_groups))

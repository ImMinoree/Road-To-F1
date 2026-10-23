import bpy,json,os
root=r'D:\Boring\GitHub\Road-To-F1-New\Road_To_F1_New\Art\HumanBase'
result={}
def dump(label):
 result[label]=[{'name':o.name,'type':o.type,'location':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'verts':len(o.data.vertices) if o.type=='MESH' else 0,'groups':len(o.vertex_groups) if o.type=='MESH' else 0,'mods':[(m.name,m.type) for m in o.modifiers],'parent':o.parent.name if o.parent else None,'bones':[(b.name,list(b.head_local),list(b.tail_local)) for b in o.data.bones] if o.type=='ARMATURE' else None} for o in bpy.context.scene.objects]
bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'KartDriver_Base.blend'));dump('blend')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(root,'KartDriver_Rigged.fbx'));dump('fbx')
with open(os.path.join(root,'binding_inspection.json'),'w') as f: json.dump(result,f,indent=2)

import bpy, json, os
from mathutils import Vector
root=r'D:\Boring\GitHub\Road-To-F1-New\Road_To_F1_New\Art'
result={}
for label,path in [('human','HumanBase/KartDriver_Base.blend'),('kart','DesertKarting/Kart/Kart_Reference.blend')]:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(root,path))
 data={'units':bpy.context.scene.unit_settings.scale_length,'objects':[]}
 for o in bpy.data.objects:
  entry={'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale),'rotation':list(o.rotation_euler)}
  if o.type=='MESH':
   pts=[o.matrix_world@Vector(p) for p in o.bound_box]
   entry.update(bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],verts=len(o.data.vertices),parent=o.parent.name if o.parent else None,groups=[g.name for g in o.vertex_groups])
  if o.type=='ARMATURE':
   entry['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(o.matrix_world@b.head_local),'tail':list(o.matrix_world@b.tail_local)} for b in o.data.bones]
  data['objects'].append(entry)
 result[label]=data
with open(os.path.join(root,'HumanBase/fit_inspection.json'),'w') as f:json.dump(result,f,indent=2)

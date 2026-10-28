import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));k=bpy.data.objects['SM_CL5_PlayerChassis'];parts=json.loads((P/'parts.json').read_text());nose=[i for p in parts if 'Nose_And_Front' in p['name'] for i in range(p['start'],p['end'])];minx=min(k.data.vertices[i].co.x for i in nose);maxx=max(k.data.vertices[i].co.x for i in nose);minz=min(k.data.vertices[i].co.z for i in nose);maxz=max(k.data.vertices[i].co.z for i in nose)
for i in nose:
 v=k.data.vertices[i];v.co.x=1.10+(v.co.x-minx)/(maxx-minx)*.38;v.co.z=.05+(v.co.z-minz)/(maxz-minz)*.10
for p in parts:
 if 'Axles_Steering_And_Hardware_Frame' in p['name']:
  for i in range(p['start'],p['end']):
   v=k.data.vertices[i]
   if v.co.x>.7:v.co.z-=.04*max(0,min(1,(.55-abs(v.co.y))/.2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));bpy.ops.object.select_all(action='DESELECT');k.select_set(True);bpy.context.view_layer.objects.active=k;bpy.ops.export_scene.fbx(filepath=str(P/'Exports/SM_CL5_PlayerChassis.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',bake_anim=False)

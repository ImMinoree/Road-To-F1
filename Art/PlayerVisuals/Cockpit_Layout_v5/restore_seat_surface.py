import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;parts=json.loads((P/'parts.json').read_text());ids=[i for p in parts if 'Seat_' in p['name'] for i in range(p['start'],p['end'])];bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend1'));seat={i:bpy.data.objects['SM_CL5_PlayerChassis'].data.vertices[i].co.copy() for i in ids};bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));o=bpy.data.objects['SM_CL5_PlayerChassis']
for i,co in seat.items():o.data.vertices[i].co=co
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(P/'Exports/SM_CL5_PlayerChassis.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',bake_anim=False)

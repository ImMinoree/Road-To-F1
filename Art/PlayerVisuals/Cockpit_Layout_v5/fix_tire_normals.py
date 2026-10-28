import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));o=bpy.data.objects['SM_CL5_PlayerChassis'];bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table();out=[]
for q in json.loads((P/'parts.json').read_text()):
 if 'Wheel_F' not in q['name']:continue
 fs=[f for f in bm.faces if all(q['start']<=v.index<q['end'] for v in f.verts)];vol=sum(f.calc_center_median().dot(f.normal)*f.calc_area()/3 for f in fs);out.append({'part':q['name'],'signed_volume':vol,'faces':len(fs)})
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();(P/'normals_check.json').write_text(json.dumps(out,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(P/'Exports/SM_CL5_PlayerChassis.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',bake_anim=False)

"""Close measured 20mm hub/column gap only in the new local cockpit copy."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Wheel_Visibility_v3.blend'));s=bpy.context.scene;k=bpy.data.objects['SM_CV2_PlayerChassis'];w=bpy.data.objects['SM_CV2_SteeringWheel'];axis=Matrix.Rotation(math.radians(18),4,'Y')@Vector((1,0,0));C=w.location.copy()
metal=next(m for m in w.data.materials if 'metal' in m.name.lower() or 'alum' in m.name.lower())
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.009,depth=.037,location=C+axis*.0155);stub=bpy.context.object;stub.name='Upper steering shaft hub engagement';stub.rotation_euler=axis.to_track_quat('Z','Y').to_euler();stub.data.materials.append(metal)
for p in stub.data.polygons:p.use_smooth=len(p.vertices)==4
bpy.ops.object.select_all(action='DESELECT');k.select_set(True);stub.select_set(True);bpy.context.view_layer.objects.active=k;bpy.ops.object.join();k.name='SM_WV3_PlayerChassis'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Wheel_Visibility_v3.blend'))
bpy.ops.object.select_all(action='DESELECT');k.select_set(True);bpy.context.view_layer.objects.active=k
bpy.ops.export_scene.fbx(filepath=str(P/'Exports/SM_WV3_PlayerChassis.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',bake_anim=False,path_mode='COPY',embed_textures=True)
(P/'column_fix.json').write_text(json.dumps({'previous_upper_shaft_start_gap_m':.02,'new_upper_stub_length_m':.037,'shaft_radius_m':.009,'stub_starts_m_behind_hub_plane':-.003,'end_m':.034,'kart_other_vertices':'unchanged; short connector added only to local cosmetic copy'},indent=2))

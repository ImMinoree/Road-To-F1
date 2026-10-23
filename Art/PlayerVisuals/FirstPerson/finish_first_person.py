import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'FP_KartArms.blend'));scene=bpy.context.scene;scene.frame_set(25);rig=bpy.data.objects['FP_KartArms_Rig'];mesh=bpy.data.objects['SK_FP_KartArms'];wheel=bpy.data.objects['SM_FP_SteeringWheel']
errors={b.name:(b.matrix.translation-b.bone.matrix_local.translation).length for b in rig.pose.bones};print('BIND_CHECK',max(errors.values()),flush=True)
# Runtime LOD: retain the authored source surfaces in .blend1; reduce redundant subdivision.
bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);bpy.context.view_layer.objects.active=mesh
m=mesh.modifiers.new('Runtime surface reduction','DECIMATE');m.ratio=.30;m.delimit={'MATERIAL','UV'}
while list(mesh.modifiers).index(m)>0:bpy.ops.object.modifier_move_up(modifier=m.name)
bpy.ops.object.modifier_apply(modifier=m.name)
cam=scene.camera;cam.location=(0,0,.95);cam.rotation_euler=Vector((math.cos(math.radians(12)),0,-math.sin(math.radians(12)))).to_track_quat('-Z','Y').to_euler()
wheel.rotation_euler.x=0;scene.frame_set(25)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'FP_KartArms.blend'))
bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(P/'Exports/SK_FP_KartArms.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
r=json.loads((P/'manifest.json').read_text());r['vertices']=len(mesh.data.vertices);r['triangles']=sum(len(p.vertices)-2 for p in mesh.data.polygons);r['source_camera_anchor_cm']=[0,0,95];r['source_view_pitch_down_deg']=12;r['grip_bind_max_position_error_source_units']=max(errors.values());(P/'manifest.json').write_text(json.dumps(r,indent=2))
for name,frame in [('center',25),('left',1),('right',49)]:
 scene.frame_set(frame);wheel.rotation_euler.x=math.radians((frame-25)/24*25);scene.render.filepath=str(P/('fp_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('FP_RUNTIME_MESH',r['vertices'],r['triangles'],flush=True)

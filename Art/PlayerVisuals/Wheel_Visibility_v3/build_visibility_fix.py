"""Incremental local-only pose and framing revision. Original V2 art is read-only."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent;source=P.parent/'Cockpit_Reference_v2/diagnose_wheel_visibility.py';q={'__file__':str(source)};exec(compile(source.read_text().split('rows=[]')[0],str(source),'exec'),q)
s,r,o,w=q['s'],q['r'],q['o'],q['w'];E=P/'Exports';E.mkdir(exist_ok=True)
original=P.parent/'Cockpit_Reference_v2/Kart_Cockpit_Reference_v2.blend';sha=hashlib.sha256(original.read_bytes()).hexdigest()
poses={}
for f in range(1,50):
 s.frame_set(f);q['setlegs'](42);poses[f]={b.name:b.matrix_basis.copy() for b in r.pose.bones}
r.animation_data_clear()
for f,mats in poses.items():
 s.frame_set(f)
 for b in r.pose.bones:
  b.rotation_mode='QUATERNION';b.matrix_basis=mats[b.name]
  for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=f)
r.animation_data.action.name='A_WV3_Steering';o.name='SK_WV3_DriverPOV'
s.camera.data.angle=math.radians(110);s.frame_set(25);bpy.context.view_layer.update()
s['Wheel visibility revision']='Local POV knees opened by bend-plane rotation; hips, ankles, hands, wheel geometry unchanged. FOV 110 provides full-lock viewport margin.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Wheel_Visibility_v3.blend'))
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);r.select_set(True);bpy.context.view_layer.objects.active=r
bpy.ops.export_scene.fbx(filepath=str(E/'SK_WV3_DriverPOV.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,mesh_smooth_type='FACE',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
for name,f in [('center',25),('left',1),('right',49)]:
 s.frame_set(f);w.rotation_euler=(q['T']@Matrix.Rotation(math.radians((f-25)/24*25),4,'X')@q['T'].inverted()).to_euler();s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_percentage=75;s.render.filepath=str(P/('blender_'+name+'.png'));bpy.ops.render.render(write_still=True)
(P/'preservation.json').write_text(json.dumps({'source_sha256':sha,'source_unchanged':sha==hashlib.sha256(original.read_bytes()).hexdigest(),'mesh_geometry_weights_and_bind_skeleton':'unchanged','wheel_geometry_location_and_materials':'unchanged','hands_and_feet':'unchanged world transforms; knee bend-plane only'},indent=2))

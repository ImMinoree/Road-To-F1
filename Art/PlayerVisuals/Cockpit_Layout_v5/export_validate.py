import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));s=bpy.context.scene;r=bpy.data.objects['FP_KartArms_Rig'];o=bpy.data.objects['SK_CL5_DriverPOV'];w=bpy.data.objects['SM_CL5_SteeringWheel'];k=bpy.data.objects['SM_CL5_PlayerChassis'];d=bpy.context.evaluated_depsgraph_get();parts=json.loads((P/'parts.json').read_text());T=Matrix.Rotation(math.radians(18),4,'Y')
ids={v.index for v in o.data.vertices if sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(('pelvis','thigh_','calf_','foot_','ball_')))>.5};fs=[tuple(p.vertices) for p in o.data.polygons if all(i in ids for i in p.vertices)];kt=BVHTree.FromPolygons([v.co for v in k.data.vertices],[tuple(p.vertices) for p in k.data.polygons]);reports=[]
for f in [1,25,49]:
 s.frame_set(f);bpy.context.view_layer.update();e=o.evaluated_get(d);m=e.to_mesh();v=[o.matrix_world@v.co for v in m.vertices];pairs=BVHTree.FromPolygons(v,fs).overlap(kt);counts={}
 for a,b in pairs:
  i=k.data.polygons[b].vertices[0];name=next((p['name'] for p in parts if p['start']<=i<p['end']),'shaft');counts[name]=counts.get(name,0)+1
 reports.append({'frame':f,'leg_chassis_triangle_pairs':counts});e.to_mesh_clear();w.rotation_euler=(T@Matrix.Rotation(math.radians((f-25)/24*25),4,'X')@T.inverted()).to_euler();s.render.filepath=str(P/('blender_'+str(f)+'.png'));bpy.ops.render.render(write_still=True)
(P/'contacts.json').write_text(json.dumps(reports,indent=2));w.rotation_euler=(0,0,0);s.frame_set(25)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);r.select_set(True);bpy.context.view_layer.objects.active=r
bpy.ops.export_scene.fbx(filepath=str(P/'Exports/SK_CL5_DriverPOV.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,mesh_smooth_type='FACE',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0)
for ob in [w,k]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;loc=ob.location.copy();ob.location=(0,0,0);bpy.ops.export_scene.fbx(filepath=str(P/'Exports'/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',bake_anim=False);ob.location=loc

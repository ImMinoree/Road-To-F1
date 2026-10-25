"""Finish surface UVs and load the existing kart PBR maps into the editable copy."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parent;ROOT=P.parents[2];bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Target_v4.blend'));s=bpy.context.scene;w=bpy.data.objects['SM_CT4_SteeringWheel'];T=Matrix.Rotation(math.radians(18),4,'Y');uv=w.data.uv_layers[0];s.frame_set(25)
for p in w.data.polygons:
 if 'LCD'!=w.data.materials[p.material_index].name.removeprefix('M_CT4_'):continue
 for li in p.loop_indices:
  co=T.inverted()@w.data.vertices[w.data.loops[li].vertex_index].co;uv.data[li].uv=((.057-co.y)/.114,(co.z-.053)/.068)
w.data.uv_layers.active_index=0;uv.active_render=True
surfaces={'SlickRubber':'SlickRubber','Chromoly':'BrushedAlloy','BodyGraphite':'Graphite','BucketComposite':'MouldedSeat','TankPolymer':'CloudedPolymer'}
for name,group in surfaces.items():
 m=bpy.data.materials['M_CT4_'+name];nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
 for suffix,prop in [('BaseColor','Base Color'),('Roughness','Roughness'),('Normal','Normal')]:
  tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(ROOT/'Art/DesertKarting/Kart/Textures'/('T_Kart_'+group+'_'+suffix+'.png')),check_existing=True)
  if suffix=='Normal':tx.image.colorspace_settings.name='Non-Color';n=nt.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.4;nt.links.new(tx.outputs[0],n.inputs['Color']);nt.links.new(n.outputs[0],bs.inputs[prop])
  else:
   if suffix=='Roughness':tx.image.colorspace_settings.name='Non-Color'
   nt.links.new(tx.outputs[0],bs.inputs[prop])
manifest=json.loads((P/'manifest.json').read_text())
for i in range(9):
 m=bpy.data.materials['M_CT4_LED_'+str(i)];color=(.8,.008,.01,1) if i<2 else (.8,.45,.008,1) if i<4 else (.012,.65,.035,1);m.diffuse_color=color;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Emission Color'].default_value=color;manifest['materials'][m.name]['color']=list(color)
(P/'manifest.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Target_v4.blend'));bpy.ops.object.select_all(action='DESELECT');w.select_set(True);bpy.context.view_layer.objects.active=w;w.location=(0,0,0)
bpy.ops.export_scene.fbx(filepath=str(P/'Exports/SM_CT4_SteeringWheel.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',bake_anim=False);w.location=(.62,0,.67)
s.cycles.samples=24;s.render.filepath=str(P/'blender_center_finished.png');bpy.ops.render.render(write_still=True)

"""Original tiny soil fragment, grass clipping and dust billboard meshes."""
import bpy,json,random
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'Art/SurfaceFX';(O/'Meshes').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);rng=random.Random(78)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.008);soil=bpy.context.object;soil.name='SM_SoilChip'
for v in soil.data.vertices:v.co*=rng.uniform(.65,1.3)
me=bpy.data.meshes.new('GrassClipping');me.from_pydata([(-.003,0,0),(.003,0,0),(.002,.025,.006),(-.002,.025,.006)],[],[(0,1,2),(0,2,3)]);me.update();grass=bpy.data.objects.new('SM_GrassClipping',me);bpy.context.collection.objects.link(grass)
me=bpy.data.meshes.new('DustQuad');me.from_pydata([(-.01,-.01,0),(.01,-.01,0),(.01,.01,0),(-.01,.01,0)],[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new()
for i,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
dust=bpy.data.objects.new('SM_DustQuad',me);bpy.context.collection.objects.link(dust)
for ob in [soil,grass,dust]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(O/'Meshes'/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'SurfaceFX.blend'))
(O/'measurements.json').write_text(json.dumps(dict(rear_axle_cm=-55,rear_wheel_lateral_cm=53.5,source='Art/DesertKarting/Kart/build_kart.py, isolated rear wheel centers',authorship='Original procedural fragment meshes; no external textures'),indent=2))

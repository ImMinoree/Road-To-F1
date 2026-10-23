"""Run with installed Blender: convert the supplied GLB without changing its source."""
import bpy, json, hashlib, re
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.glb'
OUT=ROOT/'Art/DesertKarting'; (OUT/'Meshes').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
# Rigid site alignment: source straight meets the existing pawn's reset point.
alignment=Matrix(((0,1,0,28),(-1,0,0,103),(0,0,1,-.16),(0,0,0,1)))
materials={}
for m in bpy.data.materials:
 p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not p:continue
 materials[m.name]={'base':list(p.inputs['Base Color'].default_value),'roughness':p.inputs['Roughness'].default_value,'metallic':p.inputs['Metallic'].default_value,'emission':list(p.inputs['Emission Color'].default_value),'emission_strength':p.inputs['Emission Strength'].default_value}
assets=[]
for index,obj in enumerate(sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.name)):
 original=obj.name; name='SM_DK_'+re.sub('[^A-Za-z0-9]+','_',original).strip('_')
 slots=[s.material.name if s.material else None for s in obj.material_slots]
 obj.data=obj.data.copy();obj.data.transform(alignment@obj.matrix_world);obj.matrix_world=Matrix.Identity(4)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(OUT/'Meshes'/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False)
 collision=original.startswith(('01 ','02 ','03 ','04 '))
 assets.append({'name':name,'source_object':original,'materials':slots,'collision':collision,'triangles':sum(len(p.vertices)-2 for p in obj.data.polygons),'vertices':len(obj.data.vertices)})
manifest={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_units':'metres','alignment_blender': [list(r) for r in alignment],'unreal_spawn_cm':[800,0,31],'assets':assets,'materials':materials,'source_texture_count':0}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('DESERT_EXPORT_COMPLETE',len(assets),flush=True)

"""Export evaluated original V5 kart, without the independently animated wheel. Never save source."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.scene.frame_set(25)
deps=bpy.context.evaluated_depsgraph_get()
parts=[]; materials={}; names=[]
for obj in list(bpy.context.scene.objects):
    if obj.type!='MESH' or not obj.name.startswith('SK_Kart_'): continue
    ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
    excluded=set()
    if obj.name.startswith('SK_Kart_Steering_Column_And_Wheel_'):
        hook=next((m for m in obj.modifiers if m.type=='HOOK'),None)
        if hook: excluded=set(hook.vertex_indices)
        else:
            ev.to_mesh_clear(); continue
    polygons=[p for p in mesh.polygons if not excluded or not all(i in excluded for i in p.vertices)]
    ids=sorted({i for p in polygons for i in p.vertices}); remap={v:i for i,v in enumerate(ids)}
    if not ids: ev.to_mesh_clear(); continue
    me=bpy.data.meshes.new(obj.name+'_cockpit')
    me.from_pydata([obj.matrix_world@mesh.vertices[i].co for i in ids],[],[tuple(remap[i] for i in p.vertices) for p in polygons])
    for mat in mesh.materials:
        me.materials.append(mat)
        bs=mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes else None
        materials[mat.name]={'color':list(bs.inputs['Base Color'].default_value if bs else mat.diffuse_color),'roughness':float(bs.inputs['Roughness'].default_value if bs else .6),'metallic':float(bs.inputs['Metallic'].default_value if bs else 0),'textures':{n.label:n.image.name for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image} if mat.use_nodes else {}}
    for dst,src in zip(me.polygons,polygons): dst.material_index=src.material_index; dst.use_smooth=src.use_smooth
    for source_uv in mesh.uv_layers:
        uv=me.uv_layers.new(name=source_uv.name)
        for dst,src in zip(me.polygons,polygons):
            for dl,sl in zip(dst.loop_indices,src.loop_indices):uv.data[dl].uv=source_uv.data[sl].uv
    part=bpy.data.objects.new(obj.name+'_cockpit',me); bpy.context.collection.objects.link(part);parts.append(part);names.append(obj.name)
    ev.to_mesh_clear()
assert len(parts)>20, names
bpy.ops.object.select_all(action='DESELECT')
for obj in parts: obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join()
kart=parts[0];kart.name='SM_PlayerKartChassis';kart.matrix_world=Matrix.Identity(4)
out=ROOT/'Art/PlayerVisuals/FirstPerson/Exports/SM_PlayerKartChassis.fbx'
bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',bake_anim=False,path_mode='AUTO')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(ROOT/'Evidence/Integration').mkdir(exist_ok=True)
(ROOT/'Evidence/Integration/chassis_export.json').write_text(json.dumps({'source':str(source),'source_sha256':digest,'source_unchanged':True,'parts':names,'materials':materials,'export':str(out)},indent=2))
print('CHASSIS_EXPORT_COMPLETE',len(parts))

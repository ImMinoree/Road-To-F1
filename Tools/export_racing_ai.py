"""Read existing asphalt edges and export the V5 driver onto the existing FP skeleton."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/RacingAI';OUT.mkdir(exist_ok=True)
road_source=ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.blend'
bpy.ops.wm.open_mainfile(filepath=str(road_source))
road=bpy.data.objects['02 Track surface curbs and runoff | asphalt']
audit=json.loads((ROOT/'Art/DesertRoute/audit.json').read_text());n=len(audit['route_cm'])
assert len(road.data.vertices)==n*2
left=[];right=[]
for i in range(n):
    pair=[]
    for j in [0,1]:
        p=road.matrix_world@road.data.vertices[2*i+j].co
        pair.append(Vector(((p.y+28)*100,(p.x-103)*100,(p.z-.16)*100)))
    c=Vector(audit['route_cm'][i]);t=Vector(audit['route_cm'][(i+1)%n])-Vector(audit['route_cm'][i-1]);normal=Vector((-t.y,t.x,0)).normalized()
    pair.sort(key=lambda p:(p-c).dot(normal))
    right.append(list(pair[0]));left.append(list(pair[1]))
    assert ((pair[0]+pair[1])*.5-c).length<400
(OUT/'track_edges.json').write_text(json.dumps({'source':str(road_source),'source_sha256':hashlib.sha256(road_source.read_bytes()).hexdigest(),'center':audit['route_cm'],'guide':audit['route_cm'],'left':left,'right':right,'length_cm':audit['length_m']*100,'coordinate_space':'Unreal centimeters, existing site alignment; polygon boundary vertices, not walls'},indent=2))

source=ROOT/'Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(25);deps=bpy.context.evaluated_depsgraph_get()
parts=[];materials={};names=[]
for obj in list(bpy.context.scene.objects):
    if obj.type!='MESH' or obj.hide_render or obj.name.startswith('SK_Kart_') or 'Studio' in obj.name:continue
    if not (obj.name.startswith(('RACER','HELMET')) or obj.name in ['kart_driverMesh','male_casualsuit04Mesh','shoes05Mesh','high-polyMesh']):continue
    ev=obj.evaluated_get(deps);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps);me.transform(obj.matrix_world)
    part=bpy.data.objects.new('AI | '+obj.name,me);bpy.context.collection.objects.link(part);names.append(obj.name)
    for group in obj.vertex_groups:part.vertex_groups.new(name=group.name)
    if not len(obj.vertex_groups):
        group=part.vertex_groups.new(name='head');group.add(list(range(len(me.vertices))),1,'REPLACE')
    for mat in me.materials:
        bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if mat.use_nodes else None
        materials[mat.name]={'color':list(bs.inputs['Base Color'].default_value if bs else mat.diffuse_color),'roughness':float(bs.inputs['Roughness'].default_value if bs else .6),'metallic':float(bs.inputs['Metallic'].default_value if bs else 0)}
    parts.append(part)
assert len(parts)>5,names
with bpy.data.libraries.load(str(ROOT/'Art/PlayerVisuals/FirstPerson/FP_KartArms.blend'),link=False) as (lib,data):data.objects=['FP_KartArms_Rig']
rig=data.objects[0];bpy.context.collection.objects.link(rig);rig.animation_data_clear()
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();driver=parts[0];driver.name='SK_AI_KartDriver'
mod=driver.modifiers.new('Existing FP grip-bind skeleton','ARMATURE');mod.object=rig
rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(OUT/'SK_AI_KartDriver.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=False)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(OUT/'driver_export.json').write_text(json.dumps({'source':str(source),'source_sha256':digest,'source_unchanged':True,'parts':names,'materials':materials,'bones':[b.name for b in rig.data.bones]},indent=2))
print('AI_EXPORT_COMPLETE',n,len(names))

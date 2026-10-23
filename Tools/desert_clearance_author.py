"""Filter only the pictured pit-sign assemblies and one green-roof marshal booth."""
import bpy,bmesh,json,re
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Art/DesertClearance';(OUT/'Meshes').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT.parent/'artifacts/desert-karting-circuit/desert_karting.glb'))
alignment=Matrix(((0,1,0,28),(-1,0,0,103),(0,0,1,-.16),(0,0,0,1)));items=[]
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or not ob.name.startswith('14 Timing gantry'):continue
 material=ob.name.rsplit(' | ',1)[-1]
 if material not in ['white','metal','green','glass']:continue
 original=ob.name;ob.data=ob.data.copy();ob.data.transform(alignment@ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);seen=set();remove=[];removed=[]
 for v in bm.verts:
  if v in seen:continue
  stack=[v];group=[];seen.add(v)
  while stack:
   q=stack.pop();group.append(q)
   for e in q.link_edges:
    w=e.other_vert(q)
    if w not in seen:seen.add(w);stack.append(w)
  lo=Vector([min(v.co[i] for v in group) for i in range(3)]);hi=Vector([max(v.co[i] for v in group) for i in range(3)]);c=(lo+hi)/2;d=hi-lo
  # Here c.y is Blender Y: Unreal Y = -c.y. Target booth = UE (-45,-20) m.
  booth=abs(c.x+45)<2.1 and abs(c.y-20)<2.1 and (material in ['green','glass'] or (material=='white' and abs(d.z-2.4)<.01))
  board=material=='white' and abs(d.x-1.1)<.01 and abs(d.y-.12)<.01 and abs(d.z-.45)<.01 and abs(c.y-11.1)<.02
  post=material=='metal' and abs(d.z-1.1)<.01 and abs(c.y-11.1)<.02 and -46<c.x<52
  if booth or board or post:remove.extend(group);removed.append({'kind':'booth' if booth else ('pit_sign_board' if board else 'pit_sign_post'),'center_ue_m':[c.x,-c.y,c.z]})
 assert removed,original
 bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(ob.data);bm.free();ob.data.update()
 name='SM_Clear_'+re.sub('[^A-Za-z0-9]+','_',original).strip('_');ob.name=name
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(OUT/'Meshes'/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False)
 items.append({'source_object':original,'mesh':name,'removed':removed,'remaining_triangles':sum(len(p.vertices)-2 for p in ob.data.polygons)})
assert sum(len([r for r in a['removed'] if r['kind']=='pit_sign_board']) for a in items)==13
assert sum(len([r for r in a['removed'] if r['kind']=='pit_sign_post']) for a in items)==13
assert sum(len([r for r in a['removed'] if r['kind']=='booth']) for a in items)==3
(OUT/'manifest.json').write_text(json.dumps({'filtered':items,'booth_ue_cm':[-4500,-2000,0],'pit_sign_bases':13,'retained':'Start/finish gantry, two other marshal booths, paddock buildings, track, route markings'},indent=2));print('CLEARANCE_FILTER_COMPLETE',flush=True)

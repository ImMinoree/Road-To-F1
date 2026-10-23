import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;F=P/'Kart_With_MakeHuman_Racer_v5.blend';bpy.ops.wm.open_mainfile(filepath=str(F));scene=bpy.context.scene;scene.frame_set(25);suit=bpy.data.objects['RACER | fitted one-piece suit'];done=[]
parts=['continuous red chest panel','white chest accent','red thigh insert','rear red panel','central zipper placket','smooth shoulder epaulette']
for o in scene.objects:
 if o.type!='MESH' or not o.name.startswith('RACER |') or not any(p in o.name for p in parts):continue
 m=o.modifiers.new('V5 | panels follow fitted garment','SHRINKWRAP');m.target=suit;m.wrap_method='NEAREST_SURFACEPOINT';m.wrap_mode='OUTSIDE_SURFACE';m.offset=(.0026 if 'sewn edges' in o.name else .0018)/o.matrix_world.to_scale().x
 # Preserve panel thickness by conforming its surface before the Solidify modifier.
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
 while list(o.modifiers).index(m)>0 and o.modifiers[list(o.modifiers).index(m)-1].type=='SOLIDIFY':bpy.ops.object.modifier_move_up(modifier=m.name)
 done.append(o.name)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(F));(P/'conformed_panels.json').write_text(json.dumps(done,indent=2));print('CONFORMED_PANELS',len(done),flush=True)

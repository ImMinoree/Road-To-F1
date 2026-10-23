import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent;F=P/'Kart_With_MakeHuman_Racer_v5.blend';bpy.ops.wm.open_mainfile(filepath=str(F));scene=bpy.context.scene;scene.frame_set(25);arm=bpy.data.objects['Game_engine'];o=bpy.data.objects['RACER | fitted one-piece suit'];deps=bpy.context.evaluated_depsgraph_get()
key=o.shape_key_add(name='V5 | supported fabric above raised seat ribs');key.value=1;stats=[]
for iteration in range(2):
 disabled=[m for m in o.modifiers if m.type!='ARMATURE' and m.show_viewport]
 for m in disabled:m.show_viewport=False
 bpy.context.view_layer.update();ev=o.evaluated_get(deps);me=ev.to_mesh();points=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
 for m in disabled:m.show_viewport=True
 count=0;maxmove=0
 for v,p in zip(o.data.vertices,points):
  x,y,z=p;u=abs(y)/.20;cx=.08-.03*u;top=.465+.007*(1-u)+.004+.004
  if not abs(y)<.19 or not abs(x-cx)<.023 or not top-.022<z<top:continue
  delta=Vector((0,0,min(.012,top-z)));lm=Matrix(((0,0,0,0),)*4)
  for g in v.groups:
   n=o.vertex_groups[g.group].name;lm+=(arm.matrix_world@arm.pose.bones[n].matrix@arm.data.bones[n].matrix_local.inverted()@arm.matrix_world.inverted()@o.matrix_world)*g.weight
  key.data[v.index].co+=lm.to_3x3().inverted()@delta;count+=1;maxmove=max(maxmove,delta.z)
 bpy.context.view_layer.update();stats.append({'pass':iteration,'vertices':count,'maximum_world_lift_m':maxmove})
bpy.data.objects['RACER | anatomical five-finger gloves'].data.shape_keys.key_blocks['V5 | submillimetre glove rim clearance'].name='V5 | small glove rim clearance'
bpy.ops.wm.save_as_mainfile(filepath=str(F));(P/'seat_rib_fit.json').write_text(json.dumps(stats,indent=2));print('RIB_FIT',stats,flush=True)

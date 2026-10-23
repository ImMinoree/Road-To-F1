import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;F=P/'Kart_With_MakeHuman_Racer_v5.blend';bpy.ops.wm.open_mainfile(filepath=str(F));scene=bpy.context.scene;scene.frame_set(25);arm=bpy.data.objects['Game_engine'];suit=bpy.data.objects['RACER | fitted one-piece suit'];deps=bpy.context.evaluated_depsgraph_get()
if not suit.data.shape_keys:suit.shape_key_add(name='Basis')
key=suit.shape_key_add(name='V5 | seated tailoring - original mesh and weights retained');key.value=1
inv=suit.matrix_world.inverted();segments={n:(inv@(arm.matrix_world@arm.data.bones[n].head_local),inv@(arm.matrix_world@arm.data.bones[n].tail_local)) for n in ['thigh_l','thigh_r','calf_l','calf_r']}
changed=0
for ve in suit.data.vertices:
 ws={suit.vertex_groups[g.group].name:g.weight for g in ve.groups};candidates=[(w,n) for n,w in ws.items() if n in segments]
 if not candidates:continue
 weight,n=max(candidates)
 if weight<.35:continue
 a,b=segments[n];axis=b-a;t=(ve.co-a).dot(axis)/axis.length_squared;center=a+axis*t;radial=ve.co-center
 if n.startswith('calf'):
  # Narrow loose fabric and tuck the long trouser hem into the existing boot cuff.
  scale=.87;newt=.88+(t-.88)*.22 if t>.88 else t
 else:scale=.96;newt=t
 p=a+axis*newt+radial*scale;key.data[ve.index].co=p;changed+=1
bpy.context.view_layer.update()
def lbs(v):
 m=Matrix(((0,0,0,0),)*4);total=0
 for g in v.groups:
  name=suit.vertex_groups[g.group].name
  if name in arm.pose.bones:
   m+=(arm.matrix_world@arm.pose.bones[name].matrix@arm.data.bones[name].matrix_local.inverted()@arm.matrix_world.inverted()@suit.matrix_world)*g.weight;total+=g.weight
 return m if total else suit.matrix_world
def baseworld():
 disabled=[m for m in suit.modifiers if m.type!='ARMATURE' and m.show_viewport]
 for m in disabled:m.show_viewport=False
 bpy.context.view_layer.update();ev=suit.evaluated_get(deps);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
 for m in disabled:m.show_viewport=True
 bpy.context.view_layer.update();return pts
seat=bpy.data.objects['SK_Kart_Seat_Sculpted_Tub_Seat_Moulded_Polymer'];sv=[seat.matrix_world@v.co for v in seat.data.vertices];sf=[tuple(p.vertices) for p in seat.data.polygons if all(i<759 for i in p.vertices)];st=BVHTree.FromPolygons(sv,sf)
hose=bpy.data.objects['SK_Kart_Brake_Hydraulic_Lines_And_Cable_Guides_Hydraulic_Brake_Hose'];ht=BVHTree.FromPolygons([hose.matrix_world@v.co for v in hose.data.vertices],[tuple(p.vertices) for p in hose.data.polygons]);corrections=[]
for iteration in range(2):
 pts=baseworld();count=0;maximum=0
 for ve,p in zip(suit.data.vertices,pts):
  delta=Vector();x,y,z=p
  if -.15<x<.10 and .43<z<.63:
   near,n,_,d=st.find_nearest(p)
   if n.x<0:n=-n
   signed=(p-near).dot(n)
   if -.012<signed<.002:delta+=n*min(.008,.003-signed)
  # Raise a few millimetres where the trousers cross the upper anti-slip rib.
  if .025<x<.10 and abs(y)<.15 and .450<z<.480:
   delta.z+=min(.006,max(0,.472-z))*.8
  if .10<x<.55 and .28<z<.55 and abs(y)>.20:
   near,n,_,d=ht.find_nearest(p)
   if d<.015:delta.y-=math.copysign(min(.012,.016-d),y)
  if delta.length:
   key.data[ve.index].co+=lbs(ve).to_3x3().inverted()@delta;count+=1;maximum=max(maximum,delta.length)
 corrections.append({'iteration':iteration,'vertices_adjusted':count,'max_world_correction_m':maximum});bpy.context.view_layer.update()
scene['V5 clothing fit']='Non-destructive seated tailoring shape key: narrowed trousers, tucked hems, local seat/rib/hose clearance. Original garment mesh and skin weights retained.'
bpy.ops.wm.save_as_mainfile(filepath=str(F));(P/'tailoring.json').write_text(json.dumps({'radial_vertices':changed,'local_corrections':corrections,'rest_segments':{n:[list(a),list(b)] for n,(a,b) in segments.items()}},indent=2));print('TAILORED',changed,corrections,flush=True)

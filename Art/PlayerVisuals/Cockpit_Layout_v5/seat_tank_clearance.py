import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));s=bpy.context.scene;s.frame_set(25);o=bpy.data.objects['SK_CL5_DriverPOV'];k=bpy.data.objects['SM_CL5_PlayerChassis'];parts=json.loads((P/'parts.json').read_text());e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();ids={v.index for v in o.data.vertices if sum(g.weight for g in v.groups if o.vertex_groups[g.group].name.startswith(('pelvis','thigh_','calf_','foot_','ball_')))>.5};fs=[tuple(p.vertices) for p in me.polygons if all(i in ids for i in p.vertices)];tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],fs);changes=0;maxmove=0
for part in parts:
 for i in range(part['start'],part['end']):
  v=k.data.vertices[i];name=part['name']
  if 'Fuel_Tank_And_Cap' in name:v.co=Vector((.30,0,.18))+(v.co-Vector((.30,0,.18)))*.65+Vector((.25,0,-.04))
  if 'Seat_' in name:
   hit,n,idx,dist=tree.find_nearest(v.co)
   if hit is not None and (v.co-hit).dot(n)<.004 and dist<.09:
    delta=hit+n*.005-v.co;maxmove=max(maxmove,delta.length);v.co+=delta;changes+=1
  if 'Chassis_MainFrame_Frame_Brushed_Chromoly' in name and v.co.x<.4:v.co.z-=.035
(P/'seat_tank_adjustment.json').write_text(json.dumps({'seat_vertices_adjusted':changes,'max_seat_vertex_move_m':maxmove,'tank_uniform_scale':.65,'tank_translation_m':[.25,0,-.04],'scope':'local cosmetic V5 copy only'},indent=2));e.to_mesh_clear();bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'))

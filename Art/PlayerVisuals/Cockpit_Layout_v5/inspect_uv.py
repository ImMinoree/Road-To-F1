import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'));o=bpy.data.objects['SK_CL5_DriverPOV'];out={}
for layer in o.data.uv_layers:
 out[layer.name]={}
 for mi,m in enumerate(o.data.materials):
  ps=[p for p in o.data.polygons if p.material_index==mi];area=sum(abs(sum(layer.data[p.loop_indices[i]].uv.x*layer.data[p.loop_indices[(i+1)%len(p.loop_indices)]].uv.y-layer.data[p.loop_indices[(i+1)%len(p.loop_indices)]].uv.x*layer.data[p.loop_indices[i]].uv.y for i in range(len(p.loop_indices))))/2 for p in ps)
  out[layer.name][m.name]=area
print('UV_AREAS',json.dumps(out))

import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P.parent/'Wheel_Visibility_v3/Kart_Cockpit_Wheel_Visibility_v3.blend'));s=bpy.context.scene;w=bpy.data.objects['SM_CV2_SteeringWheel'];T=Matrix.Rotation(math.radians(18),4,'Y');rows=[]
for h in [.90,.95,1.0]:
 for fov in [90,95,100]:
  for pitch in [10,12,15]:
   s.camera.location.z=h;s.camera.data.angle=math.radians(fov);s.camera.rotation_euler=Vector((math.cos(math.radians(pitch)),0,-math.sin(math.radians(pitch)))).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();cases=[]
   for a in [-25,0,25]:
    A=T@Matrix.Rotation(math.radians(a),4,'X')@T.inverted();pr=[world_to_camera_view(s,s.camera,w.location+A@v.co) for v in w.data.vertices[:3360]];cases.append({'steering':a,'top':min(1-p.y for p in pr),'bottom':max(1-p.y for p in pr),'width':max(p.x for p in pr)-min(p.x for p in pr)})
   rows.append({'eye_z':h,'fov':fov,'pitch':pitch,'cases':cases,'cost':abs(cases[1]['top']-.475)+abs(cases[1]['bottom']-.88)+max(0,max(x['bottom'] for x in cases)-.97)*5})
(P/'camera_choices.json').write_text(json.dumps(rows,indent=2));print('BEST',sorted(rows,key=lambda x:x['cost'])[:5],flush=True)
print('KART',[(o.name,len(o.data.vertices),list(o.dimensions)) for o in s.objects if o.type=='MESH' and 'Chassis' in o.name],flush=True)
src=P.parents[2]/'Art/DesertKarting/KartDriver_Fitted/Racing_Fit_v5/Kart_With_MakeHuman_Racer_v5.blend';bpy.ops.wm.open_mainfile(filepath=str(src));report=[{'name':o.name,'type':o.type,'dimensions':list(o.dimensions),'location':list(o.location)} for o in bpy.context.scene.objects if o.type=='MESH' and 'Kart' in o.name];(P/'kart_inventory.json').write_text(json.dumps(report,indent=2));print('KART_OBJECTS',len(report),flush=True)

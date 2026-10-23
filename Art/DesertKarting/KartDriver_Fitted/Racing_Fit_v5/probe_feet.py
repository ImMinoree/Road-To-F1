from pathlib import Path
exec((Path(__file__).resolve().parent/'probe_grip.py').read_text().split("if '--save' not in sys.argv:")[0])
boots=bpy.data.objects['RACER | sculpted racing boots'];trees={o.name:BVHTree.FromPolygons(*geom(o)) for o in scene.objects if o.type=='MESH' and o.name.startswith('SK_Kart_') and any(k in o.name for k in ['Chassis_Main','Axles_Steering','Driver_Controls','Hydraulic_Lines','Bodywork','Seat','Fuel_Tank'])}
footmat={s:arm.matrix_world@pb['foot_'+s].matrix for s in ['l','r']};poles={s:head('calf_'+s).copy() for s in ['l','r']}
for m in boots.modifiers:
 if m.type=='SUBSURF':m.levels=1
records=[]
for x in [.29,.30]:
 for y in [.17,.18]:
  for z in [.276,.280,.284]:
   for yaw,pitch in [(.060,-.100)]:
    reset();ok=True
    for s,sgn in [('l',1),('r',-1)]:
     D=Vector((x,sgn*y,z));ok=two('thigh_'+s,'calf_'+s,D,poles[s]) and ok
     mat=footmat[s].copy();mat.translation=D;pb['foot_'+s].matrix=arm.matrix_world.inverted()@mat;bpy.context.view_layer.update();aim('foot_'+s,D+Vector((.135,sgn*yaw,pitch)))
    if not ok:continue
    v,f=geom(boots);t=BVHTree.FromPolygons(v,f);hits={n:len(t.overlap(bt)) for n,bt in trees.items() if t.overlap(bt)}
    contact=[]
    for s in [-1,1]:
     # Distances from top of actual pedal plate to evaluated boot surface.
     contact.append(min(t.find_nearest(Vector((xx,s*yy,.170)))[3] for xx in [.42,.44,.46,.48,.50,.52] for yy in [.13,.15,.17,.19]))
    knee=[list(head('calf_'+s)) for s in ['l','r']]
    score=sum(hits.values())+max(contact)*500+max(0,max(k[2] for k in knee)-.72)*500
    records.append({'x':x,'y':y,'z':z,'yaw':yaw,'pitch':pitch,'hits':hits,'pedal_gap_m':contact,'knees':knee,'score':score})
records.sort(key=lambda r:r['score']);(P/'feet_probe.json').write_text(json.dumps(records,indent=2));print('TOP_FEET',json.dumps(records[:5]),flush=True)

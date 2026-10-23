"""Build a detailed, component-separated 125cc sprint kart with authored PBR maps."""
import bpy, math, random, json, re
import numpy as np
import tempfile
from pathlib import Path
from collections import defaultdict
from mathutils import Vector

OUT=Path(__file__).resolve().parent
TEMP=OUT/'_tmp';TEMP.mkdir(exist_ok=True);tempfile.tempdir=str(TEMP)
random.seed(301)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name=='Collection':bpy.data.collections.remove(c)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
root=bpy.data.collections.new('Kart | Reference build');scene.collection.children.link(root)
collections={}
def collection(name):
    c=collections.get(name)
    if not c:c=bpy.data.collections.new(name);root.children.link(c);collections[name]=c
    return c

M={}
TEX=OUT/'Textures';TEX.mkdir(exist_ok=True)
def surface_images(key,base,kind,size=1024):
    """Author reusable, packed, exportable PBR maps with fine-scale surface breakup."""
    rng=np.random.default_rng({'body':17,'rubber':23,'seat':31,'metal':41,'engine':53,'clear':67}.get(kind,71))
    h=w=size
    noise=rng.random((h,w),dtype=np.float32)
    # Layered noise at several scales avoids the sterile flat surfaces of the source mesh.
    for step,amp in [(2,.08),(8,.035),(32,.014)]:
        small=rng.random((max(1,h//step),max(1,w//step)),dtype=np.float32)
        yy=np.minimum(np.arange(h)//step,small.shape[0]-1);xx=np.minimum(np.arange(w)//step,small.shape[1]-1)
        noise+=(small[yy[:,None],xx[None,:]]-.5)*amp
    height=noise.copy()
    rough=np.full((h,w),{'body':.32,'rubber':.73,'seat':.52,'metal':.32,'engine':.48,'clear':.25}.get(kind,.5),np.float32)
    if kind in ('body','seat'):
        # Random fine stone chips and directional polishing scratches, restrained at model scale.
        for _ in range(1000 if kind=='body' else 450):
            y=int(rng.integers(h));x=int(rng.integers(w));length=int(rng.integers(2,17));
            noise[y:y+1,x:min(w,x+length)]+=.018; height[y:y+1,x:min(w,x+length)]+=.025
        rough+=rng.normal(0,.045,(h,w)).astype(np.float32)
    elif kind=='rubber':
        for row in range(0,h,128):
            noise[row:row+2,:]-=.09;height[row:row+2,:]-=.15
        rough+=rng.normal(0,.055,(h,w)).astype(np.float32)
    elif kind in ('metal','engine'):
        grain=rng.normal(0,.025,(h,w)).astype(np.float32);height+=grain;noise+=grain*.5
        rough+=rng.normal(0,.035,(h,w)).astype(np.float32)
    noise=np.clip(noise,0,1);rough=np.clip(rough,.08,.92);height=np.clip(height,0,1)
    dx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*.045
    dy=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*.045
    normal=np.stack([np.clip(.5-dx,.0,1.),np.clip(.5-dy,.0,1.),np.ones_like(dx)],axis=2)
    arrays={'BaseColor':np.stack([np.clip(base[i]*(.90+noise*.20),0,1) for i in range(3)]+[np.ones((h,w),np.float32)],axis=2),
            'Roughness':np.stack([rough,rough,rough,np.ones_like(rough)],axis=2),
            'Normal':np.concatenate([normal,np.ones((h,w,1),np.float32)],axis=2),
            'Metallic':np.full((h,w,4),({'metal':.82,'engine':.68,'rubber':.02,'body':.08,'seat':.04,'clear':.12}.get(kind,.1)),np.float32)}
    result={}
    for channel,arr in arrays.items():
        im=bpy.data.images.new('T_Kart_'+key+'_'+channel,width=w,height=h,alpha=True,float_buffer=False)
        im.colorspace_settings.name='Non-Color' if channel!='BaseColor' else 'sRGB'
        im.pixels.foreach_set(np.asarray(arr,dtype=np.float32).ravel());im.file_format='PNG';im.filepath_raw=str(TEX/(im.name+'.png'));im.save()
        saved_path=im.filepath_raw;bpy.data.images.remove(im)
        im=bpy.data.images.load(saved_path,check_existing=False);im.name='T_Kart_'+key+'_'+channel
        im.colorspace_settings.name='Non-Color' if channel!='BaseColor' else 'sRGB';im.pack()
        result[channel]=im
    return result

SURF={
 'body':surface_images('Graphite',(.006,.008,.010),'body'),
 'rubber':surface_images('SlickRubber',(.006,.007,.008),'rubber'),
 'seat':surface_images('MouldedSeat',(.010,.012,.014),'seat'),
 'metal':surface_images('BrushedAlloy',(.28,.30,.31),'metal'),
 'engine':surface_images('CastAlloy',(.20,.22,.22),'engine'),
 'clear':surface_images('CloudedPolymer',(.37,.34,.26),'clear')}

def material(name,color,rough=.55,metal=0,trans=0):
    m=bpy.data.materials.new('M_Kart_'+name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes.clear()
    p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.location=(0,0);p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if 'Specular IOR Level' in p.inputs:p.inputs['Specular IOR Level'].default_value=.28
    if 'Transmission Weight' in p.inputs:p.inputs['Transmission Weight'].default_value=trans
    out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');out.location=(360,0);m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
    m.diffuse_color=(*color,1);M[name]=m
    category=(None if name.startswith(('Chassis_Powder_Black','Hub_Black_Anodised','Studio_Charcoal')) else
      'body' if name in ('Body_Satin_Graphite','Body_Edge_Wear') else
      'rubber' if name in ('Tire_Slick_Rubber','Tire_Molded_Sidewall','Rubber_Grip') else
      'seat' if name=='Seat_Moulded_Polymer' else
      'clear' if name=='Fuel_Tank_Clouded_Polymer' else
      'engine' if name.startswith('Engine_') else
      'metal' if metal>.2 or name in ('Chain_Hardened_Steel','Exhaust_Heat_Titanium','Frame_Brushed_Chromoly','Fastener_Stainless') else None)
    if category:
        imgs=SURF[category];nodes=m.node_tree.nodes;links=m.node_tree.links
        uv=nodes.new('ShaderNodeUVMap');uv.uv_map='Kart_UV';uv.location=(-900,0)
        for channel,img in imgs.items():
            tex=nodes.new('ShaderNodeTexImage');tex.image=img;tex.label=channel;tex.location=(-650,{'BaseColor':240,'Roughness':70,'Metallic':-100,'Normal':-350}[channel]);tex.extension='EXTEND';links.new(uv.outputs['UV'],tex.inputs['Vector'])
            if channel=='BaseColor':links.new(tex.outputs['Color'],p.inputs['Base Color'])
            elif channel=='Roughness':links.new(tex.outputs['Color'],p.inputs['Roughness'])
            elif channel=='Metallic':links.new(tex.outputs['Color'],p.inputs['Metallic'])
            else:
                nm=nodes.new('ShaderNodeNormalMap');nm.location=(-350,-350);links.new(tex.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
    return m

material('Body_Satin_Graphite',(.008,.010,.013),.47,.10)
material('Body_Edge_Wear',(.075,.083,.091),.49,.22)
material('Chassis_Powder_Black',(.018,.022,.025),.37,.68)
material('Frame_Brushed_Chromoly',(.24,.27,.28),.27,.82)
material('Tire_Slick_Rubber',(.013,.015,.017),.59,.03)
material('Tire_Molded_Sidewall',(.024,.027,.029),.50,.04)
material('Rim_Satin_Aluminium',(.30,.32,.32),.26,.83)
material('Hub_Black_Anodised',(.045,.052,.058),.29,.78)
material('Fastener_Stainless',(.52,.56,.57),.20,.88)
material('Engine_Cast_Aluminium',(.23,.24,.23),.38,.66)
material('Engine_Fins_Dark_Alloy',(.09,.10,.105),.28,.75)
material('Engine_Ignition_Red',(.48,.035,.018),.33,.37)
material('Exhaust_Heat_Titanium',(.30,.27,.22),.25,.82)
material('Fuel_Tank_Clouded_Polymer',(.48,.45,.37),.3,.02,.16)
material('Seat_Moulded_Polymer',(.027,.031,.034),.44,.12)
material('Chain_Hardened_Steel',(.10,.115,.12),.29,.77)
material('Hydraulic_Brake_Hose',(.019,.021,.022),.43,.04)
material('Rubber_Grip',(.023,.025,.025),.72,.0)

B=defaultdict(lambda:[[],[]]);PIVOT={};part='Frame'
def addmesh(v,faces,ma):
    bucket=B[(part,ma)];start=len(bucket[0]);bucket[0].extend([tuple(p) for p in v]);bucket[1].extend(tuple(start+i for i in f) for f in faces)
def box(center,size,ma,ang=0):
    x,y,z=center;a,b,c=(q*.5 for q in size);co=math.cos(ang);si=math.sin(ang)
    v=[(x+i*co-j*si,y+i*si+j*co,z+k) for k in (-c,c) for j in (-b,b) for i in (-a,a)]
    addmesh(v,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],ma)
def rod(a,b,r,ma,n=12,r2=None):
    a=Vector(a);b=Vector(b);d=b-a
    if d.length<1e-7:return
    d.normalize();u=d.cross(Vector((0,0,1)))
    if u.length<1e-5:u=d.cross(Vector((0,1,0)))
    u.normalize();v=d.cross(u);r2=r if r2 is None else r2
    verts=[tuple(c+rr*(u*math.cos(j*math.tau/n)+v*math.sin(j*math.tau/n))) for c,rr in [(a,r),(b,r2)] for j in range(n)]
    addmesh(verts,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],ma)
def ball(center,size,ma,n=24,k=14):
    x,y,z=center;sx,sy,sz=(q*.5 for q in size)
    v=[(x+sx*math.sin(j*math.pi/k)*math.cos(i*math.tau/n),y+sy*math.sin(j*math.pi/k)*math.sin(i*math.tau/n),z+sz*math.cos(j*math.pi/k)) for j in range(k+1) for i in range(n)]
    f=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(k) for i in range(n)]
    addmesh(v,f,ma)
def cyl(a,b,r,ma,n=32,r2=None):rod(a,b,r,ma,n,r2)
def torus_axis_y(center,R,t,ma,nu=48,nv=16):
    x,y,z=center;v=[]
    for i in range(nu):
        a=i*math.tau/nu
        for j in range(nv):
            b=j*math.tau/nv;rr=R+t*math.cos(b)
            v.append((x+rr*math.cos(a),y+t*math.sin(b),z+rr*math.sin(a)))
    addmesh(v,[(i*nv+j,((i+1)%nu)*nv+j,((i+1)%nu)*nv+(j+1)%nv,i*nv+(j+1)%nv) for i in range(nu) for j in range(nv)],ma)
def tire_tread(center,radius,width,ma,nu=72,nv=24):
    x,y,z=center;major=radius*.72;minor=radius*.28;half=width*.5;v=[]
    for i in range(nu):
        a=i*math.tau/nu
        for j in range(nv):
            b=j*math.tau/nv;rr=major+minor*math.cos(b)
            v.append((x+rr*math.cos(a),y+half*math.sin(b),z+rr*math.sin(a)))
    addmesh(v,[(i*nv+j,((i+1)%nu)*nv+j,((i+1)%nu)*nv+(j+1)%nv,i*nv+(j+1)%nv) for i in range(nu) for j in range(nv)],ma)
def tire(center,radius,width,front=False):
    x,y,z=center;label=('FL' if y<0 else 'FR') if front else ('RL' if y<0 else 'RR');part='Wheel_'+label
    tire_tread(center,radius,width,'Tire_Slick_Rubber')
    # Crisp sidewall shoulder and molded concentric bead lettering rings.
    for s in [-1,1]:
        torus_axis_y((x,y+s*width*.25,z),radius*.82,radius*.035,'Tire_Molded_Sidewall',56,8)
        torus_axis_y((x,y+s*width*.20,z),radius*.94,radius*.012,'Tire_Molded_Sidewall',56,6)
        torus_axis_y((x,y+s*width*.295,z),radius*.72,radius*.014,'Tire_Molded_Sidewall',56,6)
    # Radial race-slick mold lines on the tread, deliberately shallow.
    for s in [-.30,.30]:torus_axis_y((x,y+s*width,z),radius*.985,.0045,'Tire_Molded_Sidewall',64,6)
    hubpart='Wheel_'+label
    cyl((x,y-width*.50,z),(x,y+width*.50,z),radius*.43,'Hub_Black_Anodised',48)
    # Pressed dish and rolled alloy bead, at both visible faces.
    for s in [-1,1]:
        torus_axis_y((x,y+s*width*.37,z),radius*.49,.018,'Rim_Satin_Aluminium',48,8)
        cyl((x,y+s*width*.46,z),(x,y+s*width*.49,z),radius*.42,'Rim_Satin_Aluminium',48)
        # Five sculpted, swept wheel spokes and stainless lug nuts.
        for k in range(5):
            a=k*math.tau/5+.19;edge=(x+math.sin(a)*radius*.40,z+math.cos(a)*radius*.40)
            hub=(x+math.sin(a+.36)*radius*.13,z+math.cos(a+.36)*radius*.13)
            rod((x+math.sin(a)*radius*.12,y+s*width*.485,z+math.cos(a)*radius*.12),(edge[0],y+s*width*.475,edge[1]),.018,'Rim_Satin_Aluminium',10)
            ball((x+math.sin(a)*radius*.24,y+s*width*.486,z+math.cos(a)*radius*.24),(.034,.020,.034),'Fastener_Stainless',12,8)
        ball((x,y+s*width*.495,z),(.10,.025,.10),'Fastener_Stainless',20,10)
    part='Wheel_'+label

def rounded_polyline(points,r,ma,n=10):
    for i in range(len(points)-1):rod(points[i],points[i+1],r*.60,ma,max(n,18))

# 1. Welded, powder-coated chromoly chassis, measured on a typical 1.8 m sprint kart.
part='Chassis_MainFrame';PIVOT[part]=(0,0,0)
for y in [-.325,.325]:
    rounded_polyline([(-.70,y,.19),(-.56,y,.18),(-.35,y,.17),(.27,y,.17),(.49,y,.19),(.68,y,.21)],.022,'Chassis_Powder_Black')
    rounded_polyline([(-.56,y,.18),(-.44,y*.77,.20),(-.28,y*.78,.20),(.28,y*.78,.19),(.46,y,.18)],.018,'Frame_Brushed_Chromoly')
for x,z,r in [(-.57,.19,.30),(.56,.18,.25),(-.04,.19,.29),(.48,.2,.25)]:
    rounded_polyline([(x,-r,z),(x,0,z-.025),(x,r,z)],.020,'Chassis_Powder_Black')
rounded_polyline([(-.66,-.30,.22),(-.39,-.18,.24),(-.28,0,.23),(-.39,.18,.24),(-.66,.30,.22)],.018,'Frame_Brushed_Chromoly')
rounded_polyline([(.36,-.32,.18),(.19,-.21,.23),(-.19,-.21,.23),(-.39,-.32,.18)],.020,'Chassis_Powder_Black')
rounded_polyline([(.36,.32,.18),(.19,.21,.23),(-.19,.21,.23),(-.39,.32,.18)],.020,'Chassis_Powder_Black')
# Weld beads represented as regularly spaced weld tacks around critical tube joints.
for x in [-.57,-.39,-.23,.25,.44,.57]:
    for y in [-.326,.326]:
        ball((x,y,.205),(.052,.029,.025),'Frame_Brushed_Chromoly',12,6)
# Reinforcing gussets, tabs and deck mounts.
for x in [-.51,-.28,.30,.48]:
    for y in [-.325,.325]:
        box((x,y,.225),(.13,.08,.014),'Hub_Black_Anodised')
        cyl((x,y-.05,.235),(x,y+.05,.235),.013,'Fastener_Stainless',12)

# 2. Distinct front and rear axles, uprights, stub axles and steering kingpins.
part='Axles_Steering_And_Hardware';PIVOT[part]=(0,0,0)
rod((.56,-.57,.19),(.56,.57,.19),.022,'Frame_Brushed_Chromoly',20)
rod((-.55,-.58,.205),(-.55,.58,.205),.034,'Frame_Brushed_Chromoly',24)
for side in [-1,1]:
    y=side
    rod((.55,y*.37,.18),(.57,y*.50,.22),.014,'Hub_Black_Anodised')
    rod((.56,y*.38,.18),(.56,y*.51,.36),.015,'Frame_Brushed_Chromoly')
    rod((.56,y*.48,.22),(.56,y*.51,.33),.020,'Fastener_Stainless')
    rod((.48,y*.34,.13),(.66,y*.34,.13),.015,'Frame_Brushed_Chromoly')
    # Adjustable tie rod with spherical rose-joint ends.
    rod((.50,y*.31,.29),(.65,y*.46,.30),.010,'Frame_Brushed_Chromoly')
    for x0,yy in [(.50,y*.31),(.65,y*.46)]:ball((x0,yy,.30),(.043,.032,.043),'Hub_Black_Anodised',16,10)
    # Rear bearing carrier, circular flange, cap screws and axle collar.
    for x0 in [-.55]:
        cyl((x0,y*.31,.205),(x0,y*.38,.205),.071,'Hub_Black_Anodised',32)
        torus_axis_y((x0,y*.38,.205),.056,.009,'Rim_Satin_Aluminium',32,7)
        for k in range(6):
            a=k*math.tau/6;ball((x0+math.cos(a)*.057,y*.391,.205+math.sin(a)*.057),(.013,.015,.013),'Fastener_Stainless',10,6)
    # Front brake discs, vent slots and calipers.
    if y<0:
        part='Front_Brake_Discs'
        cyl((.56,y*.55,.19),(.56,y*.59,.19),.105,'Engine_Cast_Aluminium',48)
        torus_axis_y((.56,y*.59,.19),.092,.007,'Rim_Satin_Aluminium',48,7)
        for k in range(10):
            a=k*math.tau/10;rod((.56+math.cos(a)*.067,y*.595,.19+math.sin(a)*.067),(.56+math.cos(a+.2)*.067,y*.595,.19+math.sin(a+.2)*.067),.004,'Hub_Black_Anodised',6)
        part='Front_Brake_Calipers';box((.60,y*.60,.26),(.085,.068,.095),'Engine_Ignition_Red')
        for x0 in [.575,.625]:cyl((x0,y*.635,.26),(x0,y*.65,.26),.008,'Fastener_Stainless',10)

# 3. Four isolated wheels; each has an object origin at its axle for animation in UE.
for front,x,r,w in [(True,.56,.174,.16),(False,-.55,.208,.245)]:
    for side in [-1,1]:
        center=(x,side*(.515 if front else .535),r+.012);label=('F' if front else 'R')+('L' if side<0 else 'R')
        part='Wheel_'+label;PIVOT[part]=center;tire(center,r,w,front)

# 4. Proper deep molded bucket: concave seating pan, rear shell, rolled rim and deep bolsters.
part='Seat_Sculpted_Tub';PIVOT[part]=(-.055,0,.39)
nu=32;rows=22;seat=[]
for j in range(rows+1):
    t=j/rows
    for i in range(nu+1):
        u=-1+2*i/nu;edge=max(0,1-u*u)**.55
        z=.365+t*.48
        x=-.015-.31*t+.075*(1-t)*(1-u*u)-.105*(abs(u)**2.2)*t
        y=.295*u*(.78+.22*t)
        # The center of the bucket falls below its raised hips; its back rises and leans aft.
        x+=.115*(u*u)*(1-t)**2
        seat.append((x,y,z+.018*edge*math.sin(t*math.pi)))
faces=[]
for j in range(rows):
    for i in range(nu):q=j*(nu+1)+i;faces.append((q,q+1,q+nu+2,q+nu+1))
addmesh(seat,[tuple(reversed(f)) for f in faces],'Seat_Moulded_Polymer')
# Underside shell gives the tub real thickness and a clean outer silhouette.
outer=[(x-.025,y,z-.022) for x,y,z in seat]
addmesh(outer,[tuple(f) for f in faces],'Chassis_Powder_Black')
# Raised lateral bolsters follow the tub rather than floating as isolated primitives.
for s in [-1,1]:
    points=[]
    for j in range(4,rows+1,2):
        i=nu if s>0 else 0;points.append(seat[j*(nu+1)+i])
    rounded_polyline([(x+.01,y-s*.004,z) for x,y,z in points],.026,'Seat_Moulded_Polymer')
# Rolled perimeter at the backrest and seat opening.
for s in [-1,1]:
    rounded_polyline([(.08,s*.235,.39),(-.04,s*.285,.43),(-.22,s*.30,.58),(-.30,s*.30,.77),(-.36,s*.25,.84)],.013,'Seat_Moulded_Polymer')
for x in [-.24,-.15,.20]:
    for y in [-.24,.24]:cyl((x,y,.34),(x,y,.39),.018,'Fastener_Stainless',14)
# Upholstered anti-slip cross-ribs in the seating pan.
part='Seat_Texture_And_Mounts'
for z in [.405,.425,.445,.465]:rounded_polyline([(.05,-.20,z),(.08,0,z+.007),(.05,.20,z)],.004,'Rubber_Grip')
for s in [-1,1]:
    box((-.12,s*.28,.34),(.36,.045,.075),'Hub_Black_Anodised')
    for x in [-.23,-.01]:cyl((x,s*.305,.34),(x,s*.325,.34),.010,'Fastener_Stainless',10)

# 5. Front nose cone, molded black; variable width, crowned upper skin, return lip, edge scuffs.
part='Bodywork_Nose_And_Front_Fairing';PIVOT[part]=(0,0,0)
stations=[(.46,.25,.345),(.53,.32,.38),(.62,.375,.415),(.75,.405,.455),(.87,.385,.475),(.96,.335,.465),(1.025,.245,.425),(1.04,.18,.405)]
vs=[];nf=52
for x,w,z in stations:
    for j in range(nf+1):
        u=-1+2*j/nf;vs.append((x,w*u,z+.065*max(0,1-u*u)**.8))
fs=[]
for i in range(len(stations)-1):
    for j in range(nf):q=i*(nf+1)+j;fs.append((q,q+1,q+nf+2,q+nf+1))
addmesh(vs,fs,'Body_Satin_Graphite')
for s in [-1,1]:
    for i in range(len(stations)-1):
        x,w,z=stations[i];xx,ww,zz=stations[i+1]
        rod((x,s*w,z-.02),(xx,s*ww,zz-.02),.011,'Body_Edge_Wear',8)
# Subtle worn leading edge and hand-fastened nose lip.
rounded_polyline([(.94,-.25,.405),(1.005,-.18,.397),(1.012,0,.392),(1.005,.18,.397),(.94,.25,.405)],.012,'Body_Edge_Wear')
for y in [-.23,.23]:
    ball((.91,y,.515),(.025,.025,.012),'Fastener_Stainless',12,8)

# Sculpted side pods with a broad top, rolled lower return, tapered ends, service louvers and fasteners.
for s,label in [(-1,'Left'),(1,'Right')]:
    part='Bodywork_'+label+'_Sidepod'
    stations=[(-.56,.015,.025),(-.50,.12,.095),(-.40,.17,.135),(-.27,.18,.15),(.17,.18,.145),(.31,.16,.13),(.43,.11,.09),(.48,.025,.025)]
    pod=[];nring=40
    for x,hw,hh in stations:
        for j in range(nring):
            a=j*math.tau/nring;z=.255+hh*math.sin(a);y=s*(.405+hw*math.cos(a))
            # Flatten underside and carry a slight outboard shoulder at the widest section.
            if z<.17:z=.17+(z-.17)*.35
            pod.append((x,y,z))
    podfaces=[]
    for k in range(len(stations)-1):
        for j in range(nring):a=k*nring+j;b=k*nring+(j+1)%nring;podfaces.append((a,b,b+nring,a+nring))
    addmesh(pod,podfaces,'Body_Satin_Graphite')
    # Lower edge reveal and raised upper character line track the molded part.
    rounded_polyline([(.34,s*.47,.205),(.24,s*.545,.315),(-.25,s*.555,.325),(-.44,s*.49,.29)],.008,'Body_Edge_Wear')
    for x in [-.42,.28]:
        ball((x,s*.585,.275),(.024,.013,.024),'Fastener_Stainless',16,10)
    # Four recessed cooling louvers, each set back into a shallow dark pocket.
    part='Bodywork_'+label+'_Vent_Details'
    for i in range(4):
        x=-.22+i*.072
        box((x,s*.565,.25),(.043,.012,.055),'Hub_Black_Anodised',-.10)
        rod((x-.014,s*.574,.254),(x+.014,s*.574,.254),.003,'Body_Edge_Wear',8)
    part='Bodywork_'+label+'_Sidepod'
    for i in range(14):
        x=random.uniform(-.45,.30);z=random.uniform(.17,.27)
        rod((x,s*.594,z),(x+random.uniform(.018,.065),s*.594,z+random.uniform(-.006,.006)),random.uniform(.0008,.0015),'Body_Edge_Wear',5)

# 6. Full perimeter bumpers: front hoop, side protection bars, and rear crash bar.
part='Bumpers_And_Barwork'
rounded_polyline([(.56,-.59,.20),(.79,-.62,.20),(.99,-.55,.205),(1.045,-.38,.20),(1.055,0,.20),(1.045,.38,.20),(.99,.55,.205),(.79,.62,.20),(.56,.59,.20)],.026,'Frame_Brushed_Chromoly')
for s in [-1,1]:
    rounded_polyline([(.54,s*.55,.20),(.31,s*.58,.17),(-.34,s*.59,.17),(-.68,s*.54,.19),(-.91,s*.46,.22)],.024,'Frame_Brushed_Chromoly')
rounded_polyline([(-.80,-.50,.205),(-.94,-.40,.20),(-.98,0,.20),(-.94,.40,.20),(-.80,.50,.205)],.025,'Frame_Brushed_Chromoly')
for s in [-1,1]:rod((.56,s*.45,.20),(.79,s*.62,.20),.019,'Chassis_Powder_Black')

# 7. Rear engine carrier, air-cooled 125 cc single, crankcase, clutch, head fins, carburettor.
part='Engine_Crankcase_125cc';PIVOT[part]=(-.40,0,.43)
ball((-.43,0,.42),(.40,.46,.31),'Engine_Cast_Aluminium',36,18)
ball((-.39,-.246,.42),(.25,.043,.23),'Engine_Cast_Aluminium',32,18)
torus_axis_y((-.39,-.273,.42),.102,.012,'Frame_Brushed_Chromoly',36,8)
for k in range(10):
    a=k*math.tau/10;ball((-.39+math.cos(a)*.087,-.291,.42+math.sin(a)*.087),(.021,.016,.021),'Fastener_Stainless',12,8)
box((-.44,-.08,.59),(.22,.30,.29),'Engine_Cast_Aluminium')
for i in range(10):
    z=.60+i*.026
    rounded_polyline([(-.60,-.22,z),(-.58,-.12,z+.01),(-.25,-.12,z+.01),(-.23,-.22,z)],.012,'Engine_Fins_Dark_Alloy')
box((-.44,-.05,.855),(.24,.35,.065),'Engine_Cast_Aluminium')
for i in range(5):box((-.44,-.20+i*.075,.89),(.23,.022,.03),'Engine_Fins_Dark_Alloy')
for y in [-.12,.12]:cyl((-.44,y,.90),(-.44,y,.922),.016,'Fastener_Stainless',14)
# Spark plug, copper washer, ceramic boot and ignition coil.
part='Engine_Ignition_And_Carburettor'
rod((-.44,-.03,.90),(-.44,-.03,.99),.023,'Fastener_Stainless')
rod((-.44,-.03,.96),(-.44,-.03,1.025),.014,'Engine_Ignition_Red')
ball((-.44,-.03,1.03),(.044,.044,.034),'Hub_Black_Anodised',16,8)
ball((-.67,-.22,.43),(.15,.10,.11),'Engine_Cast_Aluminium',24,12)
cyl((-.67,-.278,.43),(-.67,-.31,.43),.046,'Hub_Black_Anodised')
rod((-.67,-.31,.43),(-.67,-.37,.43),.015,'Fastener_Stainless')
box((-.31,-.30,.43),(.16,.09,.12),'Engine_Ignition_Red')
for k in range(3):rod((-.30,-.35,.40+k*.03),(-.23,-.39,.40+k*.03),.006,'Hydraulic_Brake_Hose',6)

# 8. Chain drive, toothed rear sprocket, engine clutch, rollers and paired steel side plates.
def sprocket(cx,cy,cz,r,teeth,width):
    part='Drivetrain_Rear_Sprocket' if teeth>20 else 'Drivetrain_Engine_Clutch'
    v=[];outline=[]
    for k in range(teeth*4):
        a=k*math.tau/(teeth*4);idx=k%4;rr=r*(1.12 if idx in [1,2] else .94)
        outline.append((cx+rr*math.cos(a),cz+rr*math.sin(a)))
    q=len(outline)
    for yy in [cy-width/2,cy+width/2]:v.extend([(x,yy,z) for x,z in outline])
    faces=[tuple(range(q-1,-1,-1)),tuple(range(q,2*q))]
    faces += [(i,(i+1)%q,(i+1)%q+q,i+q) for i in range(q)]
    addmesh(v,faces,'Chain_Hardened_Steel')
    torus_axis_y((cx,cy-width*.52,cz),r*.52,.012,'Frame_Brushed_Chromoly',40,7)
sprocket(-.55,-.38,.42,.171,42,.045);sprocket(-.25,-.38,.43,.074,12,.045)
for cx,cz,r in [(-.55,.42,.171),(-.25,.43,.074)]:
    for k in range(12 if r<.1 else 21):
        a=k*math.tau/(12 if r<.1 else 21);rod((cx+r*.8*math.cos(a),-.411,cz+r*.8*math.sin(a)),(cx+r*.98*math.cos(a),-.411,cz+r*.98*math.sin(a)),.007,'Fastener_Stainless',6)
# Capsule shaped chain loop around two unequal gears.
chain=[]
chain.extend([(-.55+.171*math.cos(a),.42+.171*math.sin(a)) for a in [math.pi/2+i*math.pi/32 for i in range(17)]])
chain.extend([(-.25+.074*math.cos(a),.43+.074*math.sin(a)) for a in [-math.pi/2+i*math.pi/24 for i in range(13)]])
part='Drivetrain_Chain_Links';yy=-.415
for i,p in enumerate(chain):
    nxt=chain[(i+1)%len(chain)]
    rod((p[0],yy-.012,p[1]),(nxt[0],yy-.012,nxt[1]),.008,'Chain_Hardened_Steel',8)
    rod((p[0],yy+.012,p[1]),(nxt[0],yy+.012,nxt[1]),.008,'Chain_Hardened_Steel',8)
    rod((p[0],yy-.014,p[1]),(p[0],yy+.014,p[1]),.010,'Rim_Satin_Aluminium',8)
part='Drivetrain_Bearing_Collars'
for s in [-1,1]:
    cyl((-.55,s*.28,.205),(-.55,s*.37,.205),.071,'Hub_Black_Anodised')
    torus_axis_y((-.55,s*.37,.205),.058,.009,'Fastener_Stainless',32,7)

# 9. Exhaust header with fabricated bends, welded seams, silencer and tailpipe.
part='Exhaust_Header_And_Muffler'
path=[(-.46,.16,.62),(-.51,.18,.54),(-.58,.20,.47),(-.63,.22,.39),(-.73,.25,.36),(-.85,.27,.41),(-.94,.28,.51),(-.99,.29,.60)]
for a,b in zip(path,path[1:]):rod(a,b,.013,'Exhaust_Heat_Titanium',20)
for i in [1,3,5,7]:ball(path[i],(.052,.052,.052),'Exhaust_Heat_Titanium',16,9)
rod((-.92,.30,.64),(-.59,.30,.66),.050,'Exhaust_Heat_Titanium',40,r2=.040)
torus_axis_y((-.60,.30,.66),.038,.006,'Frame_Brushed_Chromoly',40,8)
rod((-.59,.30,.66),(-.48,.30,.66),.022,'Frame_Brushed_Chromoly',28,r2=.018)
for x in [-.84,-.68]:torus_axis_y((x,.30,.66),.044,.004,'Fastener_Stainless',36,6)
box((-.77,.40,.53),(.38,.035,.065),'Hub_Black_Anodised')

# 10. Compact clouded nylon fuel tank, raised screw cap, moulded seam and filter hose.
part='Fuel_Tank_And_Cap'
cross=[(-.04,.23,.44),(.25,.23,.44),(.27,.16,.69),(.20,.16,.74),(.02,.16,.67)]
v=[]
for x,w,z in cross:
    for s in [-1,1]:v.append((x,s*w,z))
f=[(0,2,3,1),(2,4,5,3),(4,6,7,5),(6,8,9,7),(8,0,1,9),(0,8,6,4,2),(1,3,5,7,9)]
addmesh(v,f,'Fuel_Tank_Clouded_Polymer')
rounded_polyline([(-.02,-.23,.46),(.24,-.23,.46),(.255,-.16,.69),(.20,-.16,.74)],.007,'Frame_Brushed_Chromoly')
cyl((.15,0,.715),(.15,0,.75),.071,'Hub_Black_Anodised',32)
torus_axis_y((.15,0,.741),.052,.006,'Fastener_Stainless',24,6)
ball((.15,0,.758),(.098,.098,.025),'Hub_Black_Anodised',24,10)
for a in range(8):
    t=a*math.tau/8;rod((.15+.045*math.cos(t),.046*math.sin(t),.77),(.15+.045*math.cos(t+.16),.046*math.sin(t+.16),.77),.0035,'Fastener_Stainless',6)
part='Fuel_Line_And_Clamps'
rounded_polyline([(.05,-.20,.48),(-.11,-.25,.44),(-.26,-.28,.46),(-.36,-.30,.50)],.009,'Hydraulic_Brake_Hose')
for x in [-.09,-.29]:torus_axis_y((x,-.265,.45),.017,.004,'Fastener_Stainless',16,6)

# 11. Feet, pedals, brake and throttle linkages, steering wheel and front spindle linkage.
part='Driver_Controls_And_Pedals'
box((.53,-.14,.15),(.20,.13,.036),'Frame_Brushed_Chromoly',-.14)
box((.53,.14,.15),(.20,.13,.036),'Frame_Brushed_Chromoly',-.14)
for s in [-1,1]:
    for i in range(6):box((.53,s*.14,.171),(.018,.018,.006),'Hub_Black_Anodised',-.14)
rod((.42,-.13,.17),(.43,-.13,.33),.017,'Frame_Brushed_Chromoly')
rod((.42,.13,.17),(.43,.13,.32),.017,'Frame_Brushed_Chromoly')
part='Steering_Column_And_Wheel'
rod((.20,0,.24),(.46,0,.45),.019,'Frame_Brushed_Chromoly')
rod((.44,0,.43),(.61,0,.69),.023,'Frame_Brushed_Chromoly')
# Steering ring lies in the vertical YZ plane, axis X.
def torus_axis_x(center,R,t,ma,nu=48,nv=12):
    x,y,z=center;v=[]
    for i in range(nu):
        a=i*math.tau/nu
        for j in range(nv):
            b=j*math.tau/nv;r=R+t*math.cos(b);v.append((x+t*math.sin(b),y+r*math.cos(a),z+r*math.sin(a)))
    addmesh(v,[(i*nv+j,((i+1)%nu)*nv+j,((i+1)%nu)*nv+(j+1)%nv,i*nv+(j+1)%nv) for i in range(nu) for j in range(nv)],ma)
torus_axis_x((.62,0,.70),.184,.017,'Rubber_Grip',64,12)
rod((.62,0,.69),(.62,0,.84),.020,'Frame_Brushed_Chromoly')
for s in [-1,1]:
    rod((.62,0,.70),(.62,s*.09,.70),.015,'Frame_Brushed_Chromoly')
cyl((.645,0,.70),(.667,0,.70),.056,'Hub_Black_Anodised',24)
for y in [-.055,.055]:ball((.668,y,.70),(.012,.012,.012),'Fastener_Stainless',10,6)
part='Steering_Rod_End_Joints'
for y in [-.31,.31]:ball((.64,y,.30),(.042,.044,.042),'Hub_Black_Anodised',18,10)
rod((.64,-.31,.30),(.64,.31,.30),.012,'Frame_Brushed_Chromoly')

# 12. Rear crash plate, chain guards, engine hanger bolts, cable guides, hose routing.
part='Guards_And_Fasteners'
for s in [-1,1]:
    box((-.43,s*.37,.36),(.34,.045,.16),'Chassis_Powder_Black')
    for x in [-.56,-.30]:
        cyl((x,s*.388,.36),(x,s*.42,.36),.013,'Fastener_Stainless',12)
    for x in [-.59,-.23]:
        torus_axis_y((x,s*.34,.44),.023,.006,'Fastener_Stainless',16,6)
part='Brake_Hydraulic_Lines_And_Cable_Guides'
rounded_polyline([(.54,-.22,.34),(.43,-.25,.42),(.31,-.27,.47),(.19,-.27,.49),(.12,-.24,.54)],.008,'Hydraulic_Brake_Hose')
rounded_polyline([(.43,.22,.32),(.32,.26,.31),(.15,.28,.32),(.01,.28,.38),(-.16,.29,.44)],.006,'Hydraulic_Brake_Hose')
for x,y,z in [(.39,-.24,.40),(.24,-.27,.46),(.10,.28,.35),(-.07,.29,.41)]:torus_axis_y((x,y,z),.016,.004,'Fastener_Stainless',16,6)

# Keep meshes separate by moving component origins to the wheel axle or component centroid.
for (component,ma),(v,f) in B.items():
    col=collection(component)
    pivot=Vector(PIVOT.get(component,(0,0,0)))
    me=bpy.data.meshes.new('GEO_'+component+'_'+ma);me.from_pydata([tuple(Vector(q)-pivot) for q in v],[],f);me.materials.append(M[ma]);me.update()
    obj=bpy.data.objects.new('SK_Kart_'+component+'_'+ma,me);col.objects.link(obj);obj.location=pivot
    if component.startswith('Wheel_'):obj['AnimationPivot']='Wheel axle; parent part mesh groups to matching wheel pivot.'
    for poly in me.polygons:poly.use_smooth=(component.startswith('Wheel_') or ma in ['Body_Satin_Graphite','Seat_Moulded_Polymer','Tire_Slick_Rubber','Engine_Cast_Aluminium','Fuel_Tank_Clouded_Polymer'])

# Consistent texel coordinates for all authored PBR maps. These maps are packed in the .blend
# and also written as PNGs for direct Unreal material setup.
for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and obj.name!='Studio Ground (render only)':
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.cube_project(cube_size=1.0,correct_aspect=True,clip_to_bounds=False,scale_to_bounds=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        if obj.data.uv_layers:obj.data.uv_layers.active.name='Kart_UV'

# Light studio render with a dark neutral ground and soft but crisp shadows.
def area(name,loc,power,color,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
ground_mat=material('Studio_Charcoal',(.045,.050,.056),.83)
me=bpy.data.meshes.new('StudioGround');me.from_pydata([(-200,-200,-.012),(200,-200,-.012),(200,200,-.012),(-200,200,-.012)],[],[(0,1,2,3)]);me.materials.append(ground_mat)
o=bpy.data.objects.new('Studio Ground (render only)',me);scene.collection.objects.link(o);o.hide_set(True)
area('Key softbox',(1.8,-3.8,4.4),1000,(1,.84,.68),3.1,(0,0,.36))
area('Cool fill',(1.2,3.3,2.8),700,(.64,.76,1),2.8,(0,0,.40))
area('Rear rim',(-3.0,.3,3.1),1200,(1,.65,.39),2.3,(-.2,0,.45))
area('Front strip',(.6,-.5,2.8),320,(1,1,1),1.3,(.6,0,.36))
world=bpy.data.worlds.new('Neutral studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.145,.18,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.30
def camera(name,loc,target,lens=58):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=1000;return o
cam=camera('Camera | hero 3-4',(2.35,-3.55,2.18),(-.02,0,.40),58);scene.camera=cam
cameras={
 'front':camera('Camera | front detail',(3.35,-2.25,1.48),(.18,0,.38),66),
 'side':camera('Camera | profile detail',(.15,-3.65,1.38),(-.02,0,.43),62),
 'rear':camera('Camera | rear mechanical detail',(-3.1,-2.25,1.44),(-.20,0,.43),66),
 'driver':camera('Camera | driver cockpit',(-.85,-1.15,1.0),(.65,0,.40),50)}
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_x=1440;scene.render.resolution_y=960;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX';scene.render.film_transparent=False
scene['Reference']='User-provided reference photograph of a weathered, unsponsored black 125cc sprint kart.'
scene['Scale']='Metric; front is +X, kart width is Y, Z is up. Estimated wheelbase 1.11 m.'
scene['UE']='Separated component meshes. Four wheels use individual axle pivots. FBX exported in metric with standard Unreal axis conversion.'
for s in bpy.data.screens:
    for a in s.areas:
        if a.type=='VIEW_3D':a.spaces.active.region_3d.view_distance=4.2
fbx=OUT/'Exports'/'SM_Kart_Reference.fbx';fbx.parent.mkdir(parents=True,exist_ok=True);renders=OUT/'Renders';renders.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and obj.name!='Studio Ground (render only)':obj.select_set(True)
bpy.context.view_layer.objects.active=next(obj for obj in bpy.context.scene.objects if obj.select_get())
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_Reference.blend'))
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True,use_custom_props=True)
for view,c in cameras.items():
    scene.camera=c;scene.render.filepath=str(renders/(view+'.png'));bpy.ops.render.render(write_still=True)
scene.camera=cam;scene.render.filepath=str(OUT/'Kart_Reference.png');bpy.ops.render.render(write_still=True)
objects=[x for x in bpy.context.scene.objects if x.type=='MESH' and x.name!='Studio Ground (render only)']
stats={'mesh_objects':len(objects),'materials':len(M),'triangles':sum(sum(len(p.vertices)-2 for p in x.data.polygons) for x in objects),'wheel_components':4,'units':'meters','front_axis':'+X','overall_length_m':2.04,'wheelbase_m':1.11,'overall_width_m':1.31,'fbx':'Exports/SM_Kart_Reference.fbx','reference':str(OUT/'Kart_Reference.blend'),'renders':['Renders/front.png','Renders/side.png','Renders/rear.png','Renders/driver.png'],'pbr_textures':'Textures/*.png'}
(OUT/'kart_manifest.json').write_text(json.dumps(stats,indent=2));print('KART_COMPLETE',stats,flush=True)

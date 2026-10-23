"""Phase 3 original secondary props and track-aligned placement; no fake foliage."""
import bpy,math,json
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'Art/CircuitDevelopment';OUT=WORK/'Props';OUT.mkdir(exist_ok=True)
assert json.loads((ROOT/'Evidence/CircuitDevelopment/phase2.json').read_text())['gate_passed']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.scene.unit_settings.system='METRIC'
assets=[]
def make(name,vs,fs,slots=['Steel'],indices=None):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 uv=me.uv_layers.new(name='PhysicalUV')
 for p in me.polygons:
  p.use_smooth=True;p.material_index=indices[p.index] if indices else 0
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/2,v.z/2+v.y/2)
 for s in slots:me.materials.append(bpy.data.materials.get(s) or bpy.data.materials.new(s))
 return ob
def export(ob,name):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',add_leaf_bones=False)
 assets.append({'name':name,'slots':[s.name for s in ob.data.materials],'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons)})
def box(vs,fs,c,size):
 base=len(vs);x,y,z=c;a,b,d=[s/2 for s in size]
 vs.extend([(x+sx*a,y+sy*b,z+sz*d) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]])
 fs.extend([tuple(base+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
def tube(vs,fs,a,b,r,sides=8):
 a=Vector(a);b=Vector(b);v=(b-a).normalized();helper=Vector((0,0,1)) if abs(v.z)<.9 else Vector((0,1,0));u=v.cross(helper).normalized();w=v.cross(u);base=len(vs)
 for c in [a,b]:
  for j in range(sides):vs.append(tuple(c+r*(u*math.cos(j*math.tau/sides)+w*math.sin(j*math.tau/sides))))
 for j in range(sides):k=(j+1)%sides;fs.append((base+j,base+k,base+k+sides,base+j+sides))
 fs.append(tuple(base+j for j in reversed(range(sides))));fs.append(tuple(base+sides+j for j in range(sides)))
profile=[(.16,-.08),(.17,-.10),(.20,-.106),(.25,-.10),(.285,-.075),(.308,-.045),(.314,-.031),(.308,-.026),(.315,-.020),(.315,-.005),(.309,0),(.315,.005),(.315,.020),(.308,.026),(.314,.031),(.308,.045),(.285,.075),(.25,.10),(.20,.106),(.17,.10),(.16,.08)]
vs=[];fs=[];R=64
for radius,h in profile:
 for j in range(R):a=j*math.tau/R;vs.append((radius*math.cos(a),radius*math.sin(a),h))
for i in range(len(profile)):
 for j in range(R):k=(j+1)%R;n=(i+1)%len(profile);fs.append((i*R+j,i*R+k,n*R+k,n*R+j))
export(make('SafetyTire',vs,fs,['Rubber']),'SafetyTire')
vs=[];fs=[]
for sign in [-1,1]:
 for c in np.arange(-3,5,.10):
  # z = sign*x + c, clipped to 0 <= x <= 3 and .15 <= z <= 1.75.
  candidates=[]
  for x in [0,3]:
   z=sign*x+c
   if .15<=z<=1.75:candidates.append((x,0,z))
  for z in [.15,1.75]:
   x=(z-c)/sign
   if 0<x<3:candidates.append((x,0,z))
  if len(candidates)==2:tube(vs,fs,candidates[0],candidates[1],.0018,5)
export(make('FenceWire',vs,fs),'FenceWire')
vs=[];fs=[];tube(vs,fs,(0,0,0),(0,0,1.85),.027,12);tube(vs,fs,(0,0,1.77),(3,0,1.77),.016,8);tube(vs,fs,(0,0,.14),(3,0,.14),.012,8)
export(make('FenceFrame',vs,fs),'FenceFrame')
vs=[];fs=[];indices=[]
box(vs,fs,(0,0,-.025),(.74,.34,.05));indices.extend([0]*6)
for y in [-.155,.155]:box(vs,fs,(0,y,.002),(.74,.025,.022));indices.extend([1]*6)
for x in [-.355,.355]:box(vs,fs,(x,0,.002),(.025,.30,.022));indices.extend([1]*6)
for x in np.arange(-.32,.34,.028):box(vs,fs,(float(x),0,.004),(.009,.29,.018));indices.extend([1]*6)
export(make('DrainGrate',vs,fs,['Dark','Steel'],indices),'DrainGrate')
for text in ['50','100']:
 vs=[];fs=[];box(vs,fs,(0,0,.95),(.04,.8,.65));board=make('Board'+text,vs,fs,['BoardWhite']);parts=[board]
 vs=[];fs=[];tube(vs,fs,(.05,0,0),(.05,0,.85),.02,10);parts.append(make('Mount'+text,vs,fs))
 bpy.ops.object.text_add(location=(-.027,0,.95),rotation=(math.pi/2,0,-math.pi/2));letters=bpy.context.object;letters.data.body=text;letters.data.align_x='CENTER';letters.data.align_y='CENTER';letters.data.size=.38;letters.data.extrude=.001
 letters.data.materials.append(bpy.data.materials.get('BoardBlack') or bpy.data.materials.new('BoardBlack'));bpy.ops.object.convert(target='MESH');parts.append(bpy.context.object)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in parts:ob.select_set(True)
 bpy.context.view_layer.objects.active=board;bpy.ops.object.join();export(board,'BrakingBoard'+text)
g=json.loads((WORK/'geometry.json').read_text());route=np.array(g['route'])/100;xy=route[:,:2];curv=np.array(g['curvature']);N=len(route)
tangent=np.roll(xy,-1,axis=0)-np.roll(xy,1,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];normal=np.c_[-tangent[:,1],tangent[:,0]]
def distance(p):return float(np.linalg.norm(xy-p,axis=1).min())
def height(p):
 dists=np.linalg.norm(xy-p,axis=1);i=int(dists.argmin());d=float(dists[i]);f=np.clip((d-5.2)/14,0,1);f=f*f*(3-2*f);bank=np.clip((d-28)/32,0,1);bank=bank*bank*(3-2*bank);x,y=p
 return float(route[i,2]-.045+f*(.18*math.sin(x*.19)*math.sin(y*.13)+.22*math.sin(y*.11+x*.07))+bank*(1.9+.7*math.sin(x*.032+y*.018)))
placements=[];minimum=100.;rng=np.random.default_rng(8421)
def place(name,p,yaw=0,scale=(1,1,1),z=None):
 global minimum
 d=distance(p);minimum=min(minimum,d)
 placements.append({'mesh':name,'location_cm':[float(p[0]*100),float(p[1]*100),float((height(p) if z is None else z)*100)],'yaw':float(yaw),'scale':list(scale),'road_center_distance_m':d})
# Three tires per stack, touching at ~0.64m pitch on the outside of bends.
carry=0;ordinal=0;occupied={}
for i in range(N):
 if abs(curv[i])<.012:carry=0;continue
 side=-1 if curv[i]>0 else 1;j=(i+1)%N;a=xy[i]+normal[i]*6.4*side;b=xy[j]+normal[j]*6.4*side;length=float(np.linalg.norm(b-a))
 while carry<length:
  p=a+(b-a)*carry/max(length,1e-6)
  cell=tuple(np.floor(p/.64).astype(int));near=[q for x in range(cell[0]-1,cell[0]+2) for y in range(cell[1]-1,cell[1]+2) for q in occupied.get((x,y),[])]
  if distance(p)>5.65 and all(float(np.linalg.norm(p-q))>.63 for q in near):
   occupied.setdefault(cell,[]).append(p.copy())
   color=['TireRed','TireWhite','TireBlack'][(ordinal//5)%3];ground=height(p)
   for k in range(3):place(color,p,yaw=float(rng.random()*360),z=ground+.106+k*.212)
   ordinal+=1
  carry+=.64
 carry-=length
# Fence modules fit between sampled endpoints; omit narrow inter-lane spaces.
for side in [-1,1]:
 for i in range(0,N,6):
  j=(i+6)%N;a=xy[i]+normal[i]*8.3*side;b=xy[j]+normal[j]*8.3*side;length=float(np.linalg.norm(b-a))
  if min(distance(a),distance(b),distance((a+b)/2))<6.25 or length>7:continue
  yaw=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
  for name in ['FenceWire','FenceFrame']:place(name,a,yaw,(length/3,1,1))
for i in range(40,N,100):
 p=xy[i]+normal[i]*4.9;place('DrainGrate',p,math.degrees(math.atan2(tangent[i,1],tangent[i,0])),z=float(route[i,2]-.035))
for i in range(0,N,160):
 if abs(curv[(i+80)%N])<.018:continue
 p=xy[i]-normal[i]*6.1
 if distance(p)>5.7:place('BrakingBoard50',p,math.degrees(math.atan2(tangent[i,1],tangent[i,0])))
 p=xy[(i-100)%N]-normal[(i-100)%N]*6.1
 if distance(p)>5.7:place('BrakingBoard100',p,math.degrees(math.atan2(tangent[(i-100)%N,1],tangent[(i-100)%N,0])))
(WORK/'environment.json').write_text(json.dumps({'assets':assets,'placements':placements,'minimum_object_anchor_to_center_m':minimum,'missing':['Licensed 3D wild grass clumps and bushes','European deciduous/cypress trees with LODs','Reference-backed paddock architecture'],'provenance':'All props newly authored by circuit_environment.py. No marketplace imports. Placement follows recorded route.','collision_policy':'Tire barriers: simple blocking boxes outside racing corridor. Fence, signs and drains: NoCollision.'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'Environment.blend'));print('PHASE3_PROPS_BUILT',len(placements))

"""Phase 1. Blender 5.2; original geometry from the recorded game route, metres."""
import bpy,math,json,hashlib
import numpy as np
from pathlib import Path
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'Art/CircuitDevelopment';OUT=WORK/'Geometry';OUT.mkdir(exist_ok=True)
data=json.loads((WORK/'layout.json').read_text());raw=np.array(data['route_cm'],dtype=float)[:,:2]/100
origin=raw[0].copy();raw=raw-origin+np.array([8.,0.]);points=[]
for i in range(len(raw)):
 p0,p1,p2,p3=[raw[j%len(raw)] for j in [i-1,i,i+1,i+2]]
 for k in range(4):
  t=k/4;points.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
xy=np.array(points);N=len(xy);lengths=np.linalg.norm(np.roll(xy,-1,axis=0)-xy,axis=1);s=np.r_[0,np.cumsum(lengths)[:-1]];length=float(sum(lengths))
tang=np.roll(xy,-1,axis=0)-np.roll(xy,1,axis=0);tang/=np.linalg.norm(tang,axis=1)[:,None];norm=np.c_[-tang[:,1],tang[:,0]]
z=.12*np.sin(s/length*2*math.pi)+.06*np.sin(s/length*4*math.pi)
curv=(tang[:,0]*np.roll(tang,-1,axis=0)[:,1]-tang[:,1]*np.roll(tang,-1,axis=0)[:,0])/lengths
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.scene.unit_settings.system='METRIC'
curve=bpy.data.curves.new('EditableRecordedCenterline','CURVE');curve.dimensions='3D';sp=curve.splines.new('POLY');sp.points.add(N-1)
for i,p in enumerate(sp.points):p.co=(float(xy[i,0]),float(-xy[i,1]),float(z[i]),1)
sp.use_cyclic_u=True;ob=bpy.data.objects.new('SOURCE_Centerline_NotExported',curve);bpy.context.collection.objects.link(ob);ob.hide_render=True
assets=[]
def mesh(name,verts,faces,uvs,category,slots=None,indices=None):
 # Reflect UE Y into Blender Y and reverse winding, then standard FBX reconstitutes UE axes.
 verts=[(float(x),float(-y),float(h)) for x,y,h in verts];faces=[tuple(reversed(f)) for f in faces]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();obj=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(obj)
 uv=me.uv_layers.new(name='PhysicalMetres')
 for poly in me.polygons:
  poly.use_smooth=True
  if indices:poly.material_index=indices[poly.index]
  for li in poly.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
 for slot in slots or [category]:
  mat=bpy.data.materials.get(slot) or bpy.data.materials.new(slot);me.materials.append(mat)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',add_leaf_bones=False)
 assets.append({'name':name,'category':category,'vertices':len(verts),'faces':len(faces)})
def ribbon(name,a,b,start,count,category):
 verts=[];uv=[];faces=[];cols=4 if category=='Road' else 2
 for k in range(count+1):
  i=(start+k)%N;distance=float(s[i])+(length if start+k>=N else 0)
  for j in range(cols+1):
   d=a+(b-a)*j/cols;p=xy[i]+norm[i]*d
   h=float(z[i]) if category=='Road' else float(z[i])-.005-.015*(abs(d)-4)
   verts.append((*p,h));uv.append((distance/2,d/2))
 for k in range(count):
  for j in range(cols):
   q=k*(cols+1)+j;faces.append((q,q+cols+1,q+cols+2,q+1))
 mesh(name,verts,faces,uv,category)
for k,start in enumerate(range(0,N,150)):
 ribbon(f'Road_{k:02}',-4,4,start,min(150,N-start),'Road')
 ribbon(f'ShoulderL_{k:02}',4,5.1,start,min(150,N-start),'Shoulder')
 ribbon(f'ShoulderR_{k:02}',-5.1,-4,start,min(150,N-start),'Shoulder')
# Finite curb runs at meaningful bends. Cross section meets the road, with buried outer skirt.
for side in [-1,1]:
 verts=[];uv=[];faces=[];mats=[]
 for i in range(N):
  if abs(curv[i])<.018:continue
  for k in [0,1]:
   j=(i+k)%N
   for d,h in [(4,0),(4.12,.045),(4.48,.035),(4.5,-.04)]:
    p=xy[j]+norm[j]*d*side;verts.append((*p,float(z[j])+h));uv.append((float(s[i]+k*lengths[i])/2,d/2))
  q=len(verts)-8
  for j in range(3):
   f=(q+j,q+j+4,q+j+5,q+j+1);faces.append(f if side==1 else tuple(reversed(f)));mats.append(int(s[i])%2)
 mesh('CurbsL' if side==1 else 'CurbsR',verts,faces,uv,'Curbs',['CurbRed','CurbWhite'],mats)
tree=KDTree(N)
for i,p in enumerate(xy):tree.insert((float(p[0]),float(p[1]),0),i)
tree.balance()
def height(x,y):
 _,i,d=tree.find((x,y,0));f=max(0,min(1,(d-5.2)/14));f=f*f*(3-2*f)
 bank=max(0,min(1,(d-28)/32));bank=bank*bank*(3-2*bank)
 return float(z[i])-.045+f*(.18*math.sin(x*.19)*math.sin(y*.13)+.22*math.sin(y*.11+x*.07))+bank*(1.9+.7*math.sin(x*.032+y*.018))
x0=math.floor((min(xy[:,0])-55)/64)*64;y0=math.floor((min(xy[:,1])-55)/64)*64
x1=math.ceil((max(xy[:,0])+55)/64)*64;y1=math.ceil((max(xy[:,1])+55)/64)*64
for tx,x in enumerate(range(x0,x1,64)):
 for ty,y in enumerate(range(y0,y1,64)):
  verts=[];uv=[];faces=[]
  for j in range(33):
   for i in range(33):
    a=x+i*2;b=y+j*2;verts.append((a,b,height(a,b)));uv.append((a/2,b/2))
  for j in range(32):
   for i in range(32):q=j*33+i;faces.append((q,q+1,q+34,q+33))
  mesh(f'Terrain_{tx:02}_{ty:02}',verts,faces,uv,'Terrain')
# Detect ribbon boundary intersections in 2D, including across the lap seam.
intersections=[]
for side in [-1,1]:
 edge=xy+norm*4*side;delta=np.roll(edge,-1,axis=0)-edge
 def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
 for i in range(N):
  diff=edge-edge[i];den=cross(delta[i],delta);mask=np.abs(den)>1e-9
  t=np.divide(cross(diff,delta),den,out=np.zeros(N),where=mask);v=np.divide(cross(diff,delta[i]),den,out=np.zeros(N),where=mask)
  hits=np.where(mask&(t>1e-6)&(t<1-1e-6)&(v>1e-6)&(v<1-1e-6))[0]
  for j in hits:
   if j>i and min(j-i,N-j+i)>2:intersections.append([side,i,int(j)])
assert not intersections,intersections[:10]
report={'length_m':length,'width_m':8,'samples':N,'closed':True,'boundary_intersections':intersections,'road_modules':16,'world_translation_m':(np.array([8,0])-origin).tolist(),'source':data['source'],'assets':assets,'route':[{'p':[float(*())] } ] if False else [[float(xy[i,0]*100),float(xy[i,1]*100),float(z[i]*100)] for i in range(N)],'curvature':curv.tolist()}
(WORK/'geometry.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'CircuitDevelopment.blend'))
print('PHASE1_GEOMETRY_BUILT',length,len(assets))

import bpy, math, random,json
from mathutils import noise,Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'Art/OuterScenery';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
rng=random.Random(291026);assets=[]
def export(name,vs,fs,material):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 me.materials.append(bpy.data.materials.get(material) or bpy.data.materials.new(material))
 uv=me.uv_layers.new(name='WorldScale')
 for p in me.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.04,v.y*.04)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,axis_forward='-Y',axis_up='Z',bake_anim=False)
 assets.append(dict(name=name,material=material,triangles=sum(len(p.vertices)-2 for p in me.polygons)))
# Continuous irregular terrain aprons, in metres; inner footprint stays >280m from venue centre.
# Asymmetric wind-shaped dune ridges, then eroded mountain massifs with open saddles.
for band,(inner,outer,peaks,baseheight,mat) in enumerate([(280,720,13,36,'sand'),(610,1380,11,82,'sand'),(1200,2900,9,115,'sandlight')]):
 centers=[(rng.uniform(0,math.tau),rng.uniform(.30,.70),rng.uniform(.08,.21),rng.uniform(.55,1.3)) for _ in range(peaks)]
 vs=[];fs=[];na=384;nr=48
 for j in range(nr+1):
  t=j/nr
  for i in range(na):
   a=i*math.tau/na;r=inner+(outer-inner)*t
   h=0
   for ca,ct,w,amp in centers:
    da=math.atan2(math.sin(a-ca),math.cos(a-ca));shift=.07*math.sin(a*3+band)
    sigma=.16 if t<ct+shift else .26
    h+=baseheight*amp*math.exp(-.5*(da/w)**2-.5*((t-ct-shift)/sigma)**2)
   edge=math.sin(math.pi*t)**1.2
   if band==2:h*=.88+.30*noise.fractal(Vector((math.cos(a)*7,math.sin(a)*7,t*4)),1.0,2.0,4)
   else:h*=1+.08*math.sin(a*23+t*8)
   h=h*edge-4
   vs.append((r*math.cos(a),r*math.sin(a),h))
 for j in range(nr):
  for i in range(na):
   k=(i+1)%na;a=j*na+i;b=j*na+k;c=(j+1)*na+k;d=(j+1)*na+i;fs.extend([(a,c,b),(a,d,c)])
 export('SM_OS_'+['DuneApron','DuneRange','RockyMassifs'][band],vs,fs,mat)
# Low, open-branched desert scrub: opaque geometry, no alpha cards/overdraw.
from mathutils import Vector
for variant in range(2):
 vs=[];fs=[]
 def branch(a,b,r):
  a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u);base=len(vs)
  for p,rr in [(a,r),(b,r*.35)]:
   for j in range(5):vs.append(tuple(p+rr*(math.cos(j*math.tau/5)*u+math.sin(j*math.tau/5)*v)))
  for j in range(5):k=(j+1)%5;fs.append((base+j,base+k,base+5+k,base+5+j))
 for i in range(18):
  a=i*2.399;end=(math.cos(a)*rng.uniform(.3,.8),math.sin(a)*rng.uniform(.3,.8),rng.uniform(.25,.65));branch((0,0,.04),end,.024)
  for k in range(3):branch(tuple(Vector(end)*.6),(end[0]+rng.uniform(-.16,.16),end[1]+rng.uniform(-.16,.16),end[2]+rng.uniform(.05,.15)),.012)
 export('SM_OS_Scrub_'+str(variant),vs,fs,'grassdark')
placements=[]
# Sparse cluster composition outside the enclosing venue footprint; no objects inside 240m radius.
for cluster in range(19):
 a=rng.uniform(0,math.tau);r=rng.uniform(250,390);cx=30+r*math.cos(a);cy=-105+r*math.sin(a)
 for k in range(rng.randint(4,8)):
  x=cx+rng.uniform(-12,12);y=cy+rng.uniform(-12,12)
  if math.hypot(x-30,y+105)<240:continue
  placements.append(dict(mesh='SM_OS_Scrub_'+str(k%2),xy=[x*100,y*100],scale=rng.uniform(.7,1.5),yaw=rng.uniform(0,360)))
 for k in range(2):placements.append(dict(mesh='SM_ED_Rock',xy=[(cx+rng.uniform(-15,15))*100,(cy+rng.uniform(-15,15))*100],scale=rng.uniform(.8,2.2),yaw=rng.uniform(0,360)))
(O/'manifest.json').write_text(json.dumps(dict(assets=assets,placements=placements),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'OuterScenery.blend'))

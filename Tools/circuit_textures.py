"""Phase 2 original authored 2m PBR surrogates; not scanned marketplace content."""
import numpy as np,json,math,zlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'Evidence/CircuitDevelopment'
assert json.loads((E/'phase1.json').read_text())['gate_passed']
OUT=ROOT/'Art/CircuitDevelopment/Textures';OUT.mkdir(exist_ok=True)
N=1024;rng=np.random.default_rng(20261021)
def noise(cells):
 grid=rng.random((cells,cells));t=np.arange(N)*cells/N;i=t.astype(int);f=t-i;f=f*f*(3-2*f)
 a=grid[i[:,None]%cells,i[None,:]%cells];b=grid[i[:,None]%cells,(i[None,:]+1)%cells];c=grid[(i[:,None]+1)%cells,i[None,:]%cells];d=grid[(i[:,None]+1)%cells,(i[None,:]+1)%cells]
 return (a*(1-f[None,:])+b*f[None,:])*(1-f[:,None])+(c*(1-f[None,:])+d*f[None,:])*f[:,None]
def png(name,image):
 a=np.asarray(np.clip(image,0,1)*255,dtype=np.uint8)
 if a.ndim==2:a=np.repeat(a[:,:,None],3,axis=2)
 h,w,_=a.shape
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 raw=b''.join(b'\0'+row.tobytes() for row in a)
 (OUT/(name+'.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b''))
def pbr(name,base,height,rough):
 dx=(np.roll(height,-1,1)-np.roll(height,1,1))*N/4;dy=(np.roll(height,-1,0)-np.roll(height,1,0))*N/4
 v=np.stack([-dx,dy,np.ones_like(dx)],axis=2);v/=np.linalg.norm(v,axis=2)[:,:,None]
 png(name+'_BaseColor',base);png(name+'_NormalDX',v*.5+.5);png(name+'_Roughness',rough)
fine=noise(384);medium=noise(96);coarse=noise(12);grain=rng.random((N,N));pits=np.clip((fine-.62)*5,0,1)
concrete=np.clip(.48+(coarse-.5)*.09+(medium-.5)*.12+(grain-.5)*.07-pits*.15,0,1)
pbr('Concrete',np.repeat(concrete[:,:,None],3,axis=2)*np.array([1.01,1.,.96]),.001*medium-.002*pits,.77+.18*medium)
wear=np.clip((noise(80)-.60)*4,0,.65)*(.45+.55*noise(280));png('PaintWear',wear)
soilheight=.008*noise(60)+.0018*noise(300)
soil=np.array([.29,.245,.18])[None,None,:]*(.65+.55*coarse[:,:,None]+.15*grain[:,:,None])
pbr('Soil',soil,soilheight,.88+.10*medium)
grass=np.array([.22,.27,.115])[None,None,:]*(.58+.65*noise(24)[:,:,None]+.3*grain[:,:,None])
# Thin litter fibres embedded in a ground texture; these do not replace 3D grass.
for _ in range(16000):
 x,y=rng.integers(N,size=2);length=int(rng.integers(3,22));angle=rng.random()*math.tau
 ids=np.arange(length);xx=(x+ids*math.cos(angle)).astype(int)%N;yy=(y+ids*math.sin(angle)).astype(int)%N
 grass[yy,xx]=np.array([.32,.31,.17])*(.5+rng.random()*.5)
pbr('Sward',grass,.003*noise(180)+.001*grain,.86+.12*medium)
gravelh=.006*noise(140);gravel=np.ones((N,N,3))*np.array([.30,.275,.23])
for _ in range(4200):
 x,y=rng.integers(N,size=2);rad=int(rng.integers(2,10));yy,xx=np.mgrid[-rad:rad+1,-rad:rad+1];mask=(xx*xx+(yy*1.4)**2)/rad**2;weight=np.clip(1-mask,0,1)
 iy=(y+yy)%N;ix=(x+xx)%N;h=weight*.013
 gravelh[iy,ix]=np.maximum(gravelh[iy,ix],h)
 tint=np.array([.35,.335,.30])*(.65+rng.random()*.65)
 gravel[iy,ix]=gravel[iy,ix]*(1-weight[:,:,None])+tint*weight[:,:,None]
pbr('Gravel',gravel*(.88+.2*grain[:,:,None]),gravelh,.78+.18*medium)
# World-space painted mask for restrained racing rubber, repairs and macro ground variation.
g=json.loads((ROOT/'Art/CircuitDevelopment/geometry.json').read_text());route=np.array(g['route'])/100
lo=route[:,:2].min(axis=0)-64;hi=route[:,:2].max(axis=0)+64;size=hi-lo;M=2048;mask=np.zeros((M,M,3),dtype=float)
for i,p in enumerate(route):
 q=route[(i+1)%len(route)];v=q[:2]-p[:2];v/=np.linalg.norm(v);normal=np.array([-v[1],v[0]]);c=g['curvature'][i]
 intensity=min(.4,abs(c)*4+.025);offset=np.sign(c)*min(1.1,abs(c)*14)
 for wheel in [-.44,.44]:
  loc=p[:2]+normal*(offset+wheel);pixel=((loc-lo)/size*M).astype(int);x,y=pixel
  yy,xx=np.mgrid[-4:5,-4:5];worlddelta=np.stack([xx*size[0]/M,yy*size[1]/M],axis=2)
  along=worlddelta@v;across=worlddelta@normal;stamp=np.exp(-(along/.42)**2-(across/.16)**2)*intensity
  iy=np.clip(y+yy,0,M-1);ix=np.clip(x+xx,0,M-1);mask[iy,ix,0]=np.maximum(mask[iy,ix,0],stamp)
for i in [135,805,1560]:
 p=route[i];q=route[(i+1)%len(route)];v=q[:2]-p[:2];v/=np.linalg.norm(v);normal=np.array([-v[1],v[0]])
 pixel=((p[:2]-lo)/size*M).astype(int);x,y=pixel;yy,xx=np.mgrid[-18:19,-18:19]
 delta=np.stack([xx*size[0]/M,yy*size[1]/M],axis=2);a=delta@v;b=delta@normal;w=np.clip((1.7-np.abs(a))*8,0,1)*np.clip((.75-np.abs(b))*8,0,1)
 mask[np.clip(y+yy,0,M-1),np.clip(x+xx,0,M-1),1]=w*.65
# Macro patchiness is stored separately, across the whole footprint, rather than tiled.
Y,X=np.mgrid[0:M,0:M];wx=lo[0]+X/M*size[0];wy=lo[1]+Y/M*size[1]
mask[:,:,2]=np.clip(.52+.22*np.sin(wx*.14+np.sin(wy*.08))+.17*np.sin(wy*.19+wx*.06),0,1)
png('TrackMask',mask)
(OUT/'provenance.json').write_text(json.dumps({'authorship':'Original deterministic procedural texture art. Not photogrammetry and not acquired marketplace assets.','tile_m':2,'normal_convention':'DirectX tangent normal from physical height derivatives','world_mask_origin_cm':(lo*100).tolist(),'world_mask_size_cm':(size*100).tolist(),'limitations':'Sward is a ground surface, not 3D foliage. Scanned ground and curb surfaces would improve quality.'},indent=2))
print('PHASE2_TEXTURES_BUILT')

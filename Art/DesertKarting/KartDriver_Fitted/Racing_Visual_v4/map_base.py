import numpy as np,bpy,json
from pathlib import Path
P=Path('C:/Users/GBURG-4/AppData/Local/makehuman-community/makehuman/data')
z=np.load(P/'3dobjs/base.npz');print([(k,z[k].shape) for k in z.files]);print(z['fgstr'].tobytes(),z['fgidx'])
groups=z['fgstr'].tobytes();idx=z['fgidx'];start=0
for g,end in enumerate(idx):
 name=groups[start:start+int(end)].decode();start+=int(end)
 print(g,name,len(np.where(z['group']==g)[0]))
delete=np.load(P/'clothes/male_casualsuit04/male_casualsuit04.mhpxy')['deleteVerts']|np.load(P/'clothes/shoes05/shoes05.mhpxy')['deleteVerts']
f=z['fvert'];mask=~np.any(delete[f],axis=1)
print('visiblefaces',sum(mask),'usedvertices',len(np.unique(f[mask])))
for mode in ['any','all']:
 mask=(z['group']==0)&(~getattr(np,mode)(delete[f],axis=1))
 print(mode,sum(mask),len(np.unique(f[mask])))

import numpy as np,json
from pathlib import Path
P=Path('C:/Users/GBURG-4/AppData/Local/makehuman-community/makehuman/data/clothes')
for name in ['male_worksuit01','male_casualsuit04','shoes05']:
 for ext in ['npz','mhpxy','mhw']:
  p=P/name/(name+'.'+ext)
  if not p.exists():continue
  try:
   z=np.load(p)
   print(name,ext,[(k,z[k].shape,str(z[k].dtype)) for k in z.files])
   for k in z.files:
    if any(t in k for t in ['lic_','ref_v','weights','offset','scale','coord','fvert']):print(k,str(z[k])[:1100])
  except Exception:print(p.read_text()[:1000])

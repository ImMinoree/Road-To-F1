import bpy
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];bpy.ops.wm.open_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'))
for im in bpy.data.images:
 if im.source!='FILE':continue
 path=Path(bpy.path.abspath(im.filepath))
 if not path.exists():
  candidates=list((ROOT/'Art').rglob(path.name))
  if candidates:im.filepath=str(candidates[0]);im.reload()
 if Path(bpy.path.abspath(im.filepath)).exists():im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Kart_Cockpit_Layout_v5.blend'))

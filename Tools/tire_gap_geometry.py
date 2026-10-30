"""Plan both full measured boundaries, closer to runoff without altering assets."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];E=R/'Evidence/FullPaceAndTireGaps';data=json.loads((R/'Art/RacingAI/track_edges.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);trees=[]
for p in sorted((R/'Art/DesertKarting/Meshes').glob('SM_DK_02_*.fbx')):
 if p.stem.endswith('_runoff'):continue  # Use the outer runoff strip for the closer wall; keep asphalt and curbs clear.
 old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(p))
 for obj in set(bpy.data.objects)-old:
  if obj.type=='MESH':trees.append(BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[list(f.vertices) for f in obj.data.polygons]))
def clearance(p):return min(t.find_nearest(Vector((p.x*.01,-p.y*.01,.16)))[3]*100 for t in trees)


polygons=[];asphalt=[]
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 vs=[obj.matrix_world@v.co for v in obj.data.vertices]
 for f in obj.data.polygons:
  ps=[vs[i] for i in f.vertices];xy=[[v.x*100,-v.y*100] for v in ps]
  area=abs(sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy))))*.5
  if area>.1:
   polygons.append(xy)
   if 'asphalt' in obj.name.lower():asphalt.append(xy)
(E/'road_polygons.json').write_text(json.dumps(polygons));(E/'asphalt_polygons.json').write_text(json.dumps(asphalt));print('EXPORTED',len(polygons),flush=True)

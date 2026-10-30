"""Plan both full measured boundaries, closer to runoff without altering assets."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];E=R/'Evidence/TrackEdgeRefinement';data=json.loads((R/'Art/RacingAI/track_edges.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);trees=[]
for p in sorted((R/'Art/DesertKarting/Meshes').glob('SM_DK_02_*.fbx')):
 if p.stem.endswith('_runoff'):continue  # Use the outer runoff strip for the closer wall; keep asphalt and curbs clear.
 old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(p))
 for obj in set(bpy.data.objects)-old:
  if obj.type=='MESH':trees.append(BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[list(f.vertices) for f in obj.data.polygons]))
def clearance(p):return min(t.find_nearest(Vector((p.x*.01,-p.y*.01,.16)))[3]*100 for t in trees)
center=[Vector((p[0],p[1],0)) for p in data['center']];n=len(center);sections=[]
for side in ['left','right']:
 edge=[Vector((p[0],p[1],0)) for p in data[side]];offsets=[]
 for c,p in zip(center,edge):
  normal=(p-c).normalized();offset=next((s for s in range(250,441,10) if clearance(p+normal*s)>=65),None)
  offsets.append(offset if offset is not None else 250)
 # Conservative smooth envelope avoids inward kinks around wider runoff areas.
 offsets=[max(offsets[(i+j)%n]-abs(j)*20 for j in range(-4,5)) for i in range(n)]
 curve=[edge[i]+(edge[i]-center[i]).normalized()*offsets[i] for i in range(n)];lengths=[(curve[(i+1)%n]-curve[i]).length for i in range(n)];total=sum(lengths);count=math.ceil(total/54.7);pitch=total/count;rows=[];i=0;acc=0
 for j in range(count):
  dist=j*pitch
  while i<n-1 and acc+lengths[i]<dist:acc+=lengths[i];i+=1
  p=curve[i].lerp(curve[(i+1)%n],(dist-acc)/lengths[i]);t=curve[(i+1)%n]-curve[i]
  # Preserve two service openings on straights, in addition to fixed-object clearance.
  opening=any(abs((i-k+n//2)%n-n//2)<=2 for k in [20,660])
  rows.append({'xy':[p.x,p.y],'yaw':math.degrees(math.atan2(t.y,t.x)),'route_index':i,'clearance_cm':clearance(p),'access_opening':opening})
 sections.append({'side':side,'columns':rows,'pitch_cm':pitch,'offset_min_cm':min(offsets),'offset_max_cm':max(offsets)})
(E/'edge_plan.json').write_text(json.dumps({'sections':sections,'tire_diameter_cm':55,'stack_height_cm':55.2,'minimum_asphalt_and_curb_footprint_margin_cm':37.5},indent=2));print('FULL_EDGES',[(s['side'],len(s['columns']),s['offset_min_cm'],s['offset_max_cm']) for s in sections],flush=True)



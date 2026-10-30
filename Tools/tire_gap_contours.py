import sys,os,json,math
from pathlib import Path
sys.path.insert(0,str(Path(os.environ['TEMP'])/'roadf1_geometry'))
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union,nearest_points
R=Path(__file__).resolve().parents[1];E=R/'Evidence/FullPaceAndTireGaps';raw=json.loads((E/'road_polygons.json').read_text());road=unary_union([Polygon(p).buffer(0) for p in raw]);asphalt=unary_union([Polygon(p).buffer(0) for p in json.loads((E/'asphalt_polygons.json').read_text())]);outline=road.buffer(100,quad_segs=16);expanded=Polygon(outline.exterior,[max(outline.interiors,key=lambda h:Polygon(h).area)]).buffer(-220,quad_segs=16);polys=list(expanded.geoms) if expanded.geom_type=='MultiPolygon' else [expanded];center=np.array(json.loads((R/'Art/RacingAI/track_edges.json').read_text())['center'])[:,:2];sections=[]
for poly in polys:
 for ring in [poly.exterior,*[h for h in poly.interiors if Polygon(h).area/h.length>100]]:
  if ring.length<200:continue
  count=math.ceil(ring.length/54.5);pitch=ring.length/count;pts=np.array([[ring.interpolate(j*pitch).x,ring.interpolate(j*pitch).y] for j in range(count)])
  indices=np.argmin(((pts[:,None,:]-center[None,:,:])**2).sum(axis=2),axis=1)
  rows=[]
  for j,p in enumerate(pts):
   point=__import__('shapely').geometry.Point(float(p[0]),float(p[1]));near=nearest_points(point,asphalt)[1];away=np.array([p[0]-near.x,p[1]-near.y]);away=away/max(.001,float(np.linalg.norm(away)));idx=int(indices[j]);nxt=pts[(j+1)%count];prev=pts[(j-1)%count]
   rows.append({'xy':p.tolist(),'normal':away.tolist(),'yaw':math.degrees(math.atan2(nxt[1]-prev[1],nxt[0]-prev[0])),'route_index':idx,'clearance_cm':road.distance(__import__('shapely').geometry.Point(float(p[0]),float(p[1]))),'asphalt_clearance_cm':asphalt.distance(__import__('shapely').geometry.Point(float(p[0]),float(p[1]))),'access_opening':any(abs((idx-k+len(center)//2)%len(center)-len(center)//2)<=2 for k in [20,660])})
  sections.append({'side':'outer' if ring==poly.exterior else 'island_'+str(len(sections)),'columns':rows,'pitch_cm':pitch})
(E/'edge_plan.json').write_text(json.dumps({'sections':sections,'source':'Union of actual road/curb mesh footprints, offset within existing runoff, 120cm inside its outer outline; continuous closed contours','road_area_cm2':road.area},indent=2));print('CONTINUOUS_CONTOURS',[(s['side'],len(s['columns'])) for s in sections])

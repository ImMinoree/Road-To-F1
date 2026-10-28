"""Read-only Blender geometry analysis; reuse imported tires and measured track edges."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[1]
ev=root/'Evidence/ExpandedTireBarriers';ev.mkdir(parents=True,exist_ok=True)
data=json.loads((root/'Art/RacingAI/track_edges.json').read_text())
audit=json.loads((root/'Art/DesertRoute/audit.json').read_text())
old=json.loads((root/'Art/Trackside/TireBarriers/placement.json').read_text())
center=[Vector((p[0],p[1],0)) for p in data['center']]
edges={name:[Vector((p[0],p[1],0)) for p in data[name]] for name in ['left','right']}
n=len(center);pitch=54.7;radius=27.5
inventory=json.loads((ev/'inventory_before.json').read_text())
for folder in ['Art/Trackside/TireBarriers']:
    for p in (root/folder).rglob('*'):
        if p.is_file():inventory['protected'][str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
(ev/'inventory_before.json').write_text(json.dumps(inventory,indent=2))
grid=[Vector(a['transform'][:3]) for a in inventory['actors'] if a['class']=='GridStartSlot']
existing_xy={tuple(round(v,2) for v in t['location'][:2]) for c in inventory['tire_components'] for t in c['instances']}

bpy.ops.wm.read_factory_settings(use_empty=True)
trees=[]
for path in sorted((root/'Art/DesertKarting/Meshes').glob('SM_DK_02_*.fbx')):
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(path))
    for obj in set(bpy.data.objects)-before:
        if obj.type=='MESH':
            trees.append(BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                                            [list(f.vertices) for f in obj.data.polygons]))
assert len(trees)>=5

def clearance(p):
    # Source FBX imports in Blender metres with the Unreal Y reflection.
    q=Vector((p.x*.01,-p.y*.01,.16))
    return min(tree.find_nearest(q)[3]*100 for tree in trees)

def sample(poly,start=0,stop=None):
    lengths=[(poly[i+1]-poly[i]).length for i in range(len(poly)-1)]
    total=sum(lengths);stop=total if stop is None else min(stop,total)
    result=[];distance=start;j=0;accum=0
    while distance<=stop+1e-5:
        while j<len(lengths)-1 and accum+lengths[j]<distance:
            accum+=lengths[j];j+=1
        if lengths[j]>1e-6:result.append(poly[j].lerp(poly[j+1],(distance-accum)/lengths[j]))
        distance+=pitch
    return result

def safe(p):
    return clearance(p)>=135 and min(math.hypot(p.x-q.x,p.y-q.y) for q in grid)>=2000

def runs(points):
    result=[];run=[]
    for p in points:
        if safe(p):run.append(p)
        else:
            if len(run)>=12:result.append(run)
            run=[]
    if len(run)>=12:result.append(run)
    return result

sections=[];rejected=[]
windows={1:(24,43),2:(38,40),3:(32,33),4:(31,31),5:(25,25),6:(35,38),7:(30,26)}
for corner in audit['corners']:
    number=corner['number'];idx=corner['index'];pre,post=windows[number]
    side='left' if corner['angle_deg']<0 else 'right'
    indices=list(range(idx-pre,idx+post+1))
    if number==1:indices=[i for i in indices if i>=40]  # Keep the full start/grid approach open.
    old_path=next((p for p in old['paths'] if p['corner']==number),None)
    candidates=[]
    for offset in ([620] if old_path else [330,380,430,480,530,580,620]):
        curve=[]
        for i in indices:
            c=center[i%n];edge=edges[side][i%n]
            curve.append(edge+(edge-c).normalized()*offset)
        if old_path:
            anchor=[Vector(p) for p in old_path['spline_cm']]
            first=min(range(len(curve)),key=lambda j:(curve[j]-anchor[0]).length)
            last=min(range(len(curve)),key=lambda j:(curve[j]-anchor[-1]).length)
            # Extend from the exact original endpoints; never relocate the 144 existing tires.
            prefix=curve[:first]+[anchor[0]]
            suffix=[anchor[-1]]+curve[last+1:]
            points=list(reversed(sample(list(reversed(prefix)),pitch)))+anchor+sample(suffix,pitch)
        else:
            points=sample(curve)
        groups=runs(points)
        total=sum(len(group) for group in groups)
        candidates.append((total/len(points),offset,groups,len(points)))
        if total/len(points)>.90:break
    fraction,offset,groups,attempted=max(candidates,key=lambda x:(x[0],-x[1]))
    if not groups:
        rejected.append({'corner':number,'reason':'No continuous safe band outside all road/curb/runoff surfaces'})
        continue
    for part,points in enumerate(groups):
        # De-duplicate close joins and retain uniform, continuous stack spacing.
        clean=[]
        for p in points:
            if not clean or (p-clean[-1]).length>53.8:clean.append(p)
        if len(clean)<12:continue
        rows=[]
        for j,p in enumerate(clean):
            tangent=clean[min(j+1,len(clean)-1)]-clean[max(j-1,0)]
            is_existing=any(math.hypot(p.x-x,p.y-y)<.5 for x,y in existing_xy)
            rows.append({'xy':[p.x,p.y],'yaw':math.degrees(math.atan2(tangent.y,tangent.x)),
                         'existing':is_existing,'surface_clearance_cm':clearance(p)})
        sections.append({'id':'corner_%d_%d'%(number,part+1),'corner':number,'route_index':idx,'side':side,
                         'edge_offset_cm':offset,'outer_turn_degrees':corner['angle_deg'],
                         'columns':rows,'coverage_fraction':fraction})

assert len(sections)>=5,'Insufficient corner coverage: inspect geometry before placement'
report={'source':'Measured left/right asphalt boundaries plus BVHs of all actual source asphalt/curb/runoff meshes',
        'spacing_cm':pitch,'tire_diameter_cm':55,'stack_height_cm':55.2,'levels':3,
        'minimum_surface_footprint_clearance_cm':135-radius,'grid_exclusion_radius_cm':2000,
        'original_tires':144,'sections':sections,'rejected_corners':rejected}
(ev/'placement_plan.json').write_text(json.dumps(report,indent=2))
print('EXPANSION_PLAN',[(s['id'],len(s['columns']),s['edge_offset_cm']) for s in sections],flush=True)
print('NEW_COLUMN_CANDIDATES',sum(not p['existing'] for s in sections for p in s['columns']),flush=True)

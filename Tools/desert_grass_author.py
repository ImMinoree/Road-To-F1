"""Original tapered grass clumps, ground-conforming seeded infield scatter."""
import bpy,json,math,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]; O=R/'Art/InfieldGrass'; (O/'Meshes').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
# Use exported lawn surfaces, not an invented rectangular grass footprint.
trees=[];roadtrees=[]
for name in ['SM_DK_03_Infield_lawns_and_pit_lane_grass','SM_DK_03_Infield_lawns_and_pit_lane_grassdark']:
    before=set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=str(R/'Art/DesertKarting/Meshes'/(name+'.fbx')))
    for ob in set(bpy.data.objects)-before:
        if ob.type=='MESH':
            trees.append(BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]))
for f in (R/'Art/DesertKarting/Meshes').glob('SM_DK_02_*.fbx'):
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(f))
    for ob in set(bpy.data.objects)-before:
        if ob.type=='MESH':roadtrees.append(BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]))
assert trees and roadtrees,'Missing lawn or racing-surface source meshes'
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
route=json.loads((R/'Art/DesertRoute/audit.json').read_text())['route_cm']
rng=random.Random(42117); placements=[]
# A compact spatial lookup keeps a conservative 7.5 m centerline exclusion.
bins={}
for x,y,*_ in route:bins.setdefault((int(x//1000),int(y//1000)),[]).append((x,y))
for x in range(-5400,14500,75):
    for y in range(-15500,1800,75):
        xx=x+rng.uniform(-24,24); yy=y+rng.uniform(-24,24)
        nearby=[p for bx in range(int(xx//1000)-1,int(xx//1000)+2) for by in range(int(yy//1000)-1,int(yy//1000)+2) for p in bins.get((bx,by),[])]
        if nearby and min((xx-a)**2+(yy-b)**2 for a,b in nearby)<750**2:continue
        # Check the whole clump footprint against actual asphalt, curbs and runoff.
        if any(tree.ray_cast(Vector((xx/100+ox,-yy/100+oy,5)),Vector((0,0,-1)),10)[0] is not None for ox,oy in [(0,0),(.6,0),(-.6,0),(0,.6),(0,-.6)] for tree in roadtrees):continue
        hits=[tree.ray_cast(Vector((xx/100,-yy/100,5)),Vector((0,0,-1)),10)[0] for tree in trees]
        hits=[p for p in hits if p is not None]
        if not hits:continue
        # Soft patches rather than a uniform manufactured carpet.
        density=.78+.15*math.sin(xx*.0021)*math.cos(yy*.0017)
        if rng.random()>density:continue
        z=max(p.z for p in hits)*100
        placements.append(dict(variant=rng.randrange(3),location=[xx,yy,z-.35],yaw=rng.uniform(0,360),scale=rng.uniform(.8,1.25)))
assets=[]
for variant in range(3):
    vs=[]; fs=[]; uv=[]; rr=random.Random(800+variant)
    for blade in range(56):
        angle=rr.uniform(0,math.tau); radius=.39*math.sqrt(rr.random()); bx=math.cos(angle)*radius; by=math.sin(angle)*radius
        h=rr.uniform(.10,.22); width=rr.uniform(.010,.022); heading=rr.uniform(0,math.tau); lean=rr.uniform(.025,.10)
        start=len(vs)
        for k in range(4):
            t=k/3; cx=bx+math.cos(heading)*lean*t*t;cy=by+math.sin(heading)*lean*t*t; w=width*(1-t)**.8 if k<3 else .0001
            for side in [-1,1]:vs.append((cx+side*math.sin(heading)*w/2,cy-side*math.cos(heading)*w/2,h*t));uv.append(((side+1)/2,t))
        for k in range(3):
            a=start+k*2;fs.extend([(a,a+1,a+3),(a,a+3,a+2)])
    name='SM_InfieldGrass_%02d'%variant;me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();layer=me.uv_layers.new(name='BladeUV')
    colors=me.color_attributes.new(name='RootToTip',type='FLOAT_COLOR',domain='CORNER')
    for poly in me.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:
            layer.data[li].uv=uv[me.loops[li].vertex_index]
            t=uv[me.loops[li].vertex_index][1];colors.data[li].color=(t,t,t,1)
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.export_scene.fbx(filepath=str(O/'Meshes'/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,mesh_smooth_type='FACE',bake_anim=False)
    assets.append(dict(name=name,triangles=len(fs),blades=56))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'InfieldGrass.blend'))
(O/'scatter.json').write_text(json.dumps(dict(seed=42117,route_exclusion_cm=750,spacing_cm=75,assets=assets,placements=placements),separators=(',',':')))
print('GRASS_AUTHORED',len(placements),flush=True)

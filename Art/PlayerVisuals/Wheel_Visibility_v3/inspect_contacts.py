from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;source=P.parent/'Cockpit_Reference_v2/diagnose_wheel_visibility.py';q={'__file__':str(source)};exec(compile(source.read_text().split('rows=[]')[0],str(source),'exec'),q)
s,r,o=q['s'],q['r'],q['o'];s.frame_set(25);q['setlegs'](42);ev=o.evaluated_get(q['deps']);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];tree=BVHTree.FromPolygons(vs,q['lf']);pairs=tree.overlap(q['karttree']);ids={i for a,b in pairs for i in q['lf'][a]};pts=[vs[i] for i in ids];print('BOUNDS',[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)],flush=True);print('CENTERS',sorted(set(tuple(round(x,2) for x in sum((vs[i] for i in q['lf'][a]),Vector())/len(q['lf'][a])) for a,b in pairs)),flush=True)
s.camera.data.angle=__import__('math').radians(110);s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_percentage=50;s.render.filepath=str(P/'trial_knees42.png');bpy.ops.render.render(write_still=True)

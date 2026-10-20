"""Blender 5.2: metre-space source, FBX centimetres through standard exporter."""
import bpy, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
def center(s):
    t=max(0,s-35)/115*0.65
    if s<=35: return s,0,0
    r=115/0.65
    return 35+r*math.sin(t),r*(1-math.cos(t)),t
def strip(name,a,b,terrain=False,curb=False):
    verts=[]; faces=[]; uvs=[]
    n=300; cols=12 if terrain else 2
    for i in range(n+1):
        s=150*i/n; x,y,t=center(s)
        for j in range(cols+1):
            d=a+(b-a)*j/cols
            z=0
            if terrain:
                f=min(1,max(0,(abs(d)-4.6)/7))
                z=-.025+f*(.24*math.sin(s*.08+d*.14)+.18*math.sin(d*.45+s*.04))
            if curb: z=.015+.035*math.sin(math.pi*j/cols)
            verts.append((x-math.sin(t)*d,y+math.cos(t)*d,z))
            uvs.append((s/2,d/2))
    for i in range(n):
        for j in range(cols):
            q=i*(cols+1)+j; faces.append((q,q+cols+1,q+cols+2,q+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    uv=mesh.uv_layers.new(name='UVMap')
    for p in mesh.polygons:
        p.use_smooth=terrain
        p.material_index=(p.index//cols//2)%2 if curb else 0
        for li in p.loop_indices: uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
    for matname in (['CurbRed','CurbWhite'] if curb else [name]):
        mat=bpy.data.materials.get(matname) or bpy.data.materials.new(matname); obj.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    if curb:
        solid=obj.modifiers.new('ConcreteDepth','SOLIDIFY');solid.thickness=.06;solid.offset=-1
        bpy.ops.object.modifier_apply(modifier=solid.name)
    bpy.ops.export_scene.fbx(filepath=str(ROOT/'Art'/'Exports'/f'{name}.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE')
strip('Road',-4,4)
strip('CurbLeft',-4.5,-4,curb=True)
strip('CurbRight',4,4.5,curb=True)
strip('VergeLeft',-22,-4.5,terrain=True)
strip('VergeRight',4.5,22,terrain=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Art'/'VisualProof.blend'))

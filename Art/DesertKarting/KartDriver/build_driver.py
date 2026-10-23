"""Build a seated, rigged kart driver in a copy of the existing kart Blender scene.

Run: D:\\Boring\\blender.exe -b --python build_driver.py
The source Kart_Reference.blend is opened read-only by this script; all deliverables
are written to this directory.
"""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector, Matrix

OUT=Path(__file__).resolve().parent
PROJECT=OUT.parents[2]
KART=PROJECT/'Art'/'DesertKarting'/'Kart'/'Kart_Reference.blend'
assert KART.exists(),KART
random.seed(8104)
bpy.ops.wm.open_mainfile(filepath=str(KART))
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.0

def bounds(tokens):
    objs=[o for o in bpy.data.objects if o.type=='MESH' and any(t in o.name for t in tokens)]
    pts=[o.matrix_world@Vector(corner) for o in objs for corner in o.bound_box]
    return tuple((min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3))

seat_bounds=bounds(('Seat_Sculpted_Tub_Seat_Moulded_Polymer',))
wheel_bounds=bounds(('Steering_Column_And_Wheel_Rubber_Grip',))
pedal_bounds=bounds(('Driver_Controls_And_Pedals_Frame_Brushed_Chromoly',))
assert len(seat_bounds)==len(wheel_bounds)==len(pedal_bounds)==3
assert seat_bounds[0][0]<-.25 and seat_bounds[2][1]>.75
assert .58<(wheel_bounds[0][0]+wheel_bounds[0][1])/2<.66
assert wheel_bounds[1][1]-wheel_bounds[1][0]>.36 and wheel_bounds[2][1]-wheel_bounds[2][0]>.36
assert pedal_bounds[2][0]<.25

# Human fit is tuned to the measured kart, front +X, left/right +/-Y, Z up.
HIP=Vector((-.145,0,.435)); HEAD=Vector((-.17,0,1.035))
# The wheel lies in the Y/Z plane at X=.62. Place the grip points at its sides,
# then solve the elbows between them and the shoulder line to avoid locked arms.
SHOULDER={-1:Vector((0,-.205,.755)),1:Vector((0,.205,.755))}
ELBOW={-1:Vector((.33,-.29,.755)),1:Vector((.33,.29,.755))}
WRIST={-1:Vector((.62,-.145,.70)),1:Vector((.62,.145,.70))}
KNEE={-1:Vector((.22,-.145,.505)),1:Vector((.22,.145,.505))}
ANKLE={-1:Vector((.44,-.14,.205)),1:Vector((.44,.14,.205))}
TOE={-1:Vector((.66,-.14,.18)),1:Vector((.66,.14,.18))}

driver_col=bpy.data.collections.new('KART DRIVER | Rigged Adult')
scene.collection.children.link(driver_col)
details_col=bpy.data.collections.new('DRIVER | Suit seams, helmet hardware, animation controls')
scene.collection.children.link(details_col)

def mat(name,color,rough,metal=0.0,coat=0.0,fabric=False,transmission=0.0):
    m=bpy.data.materials.new('M_DRV_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes;n.clear();p=n.new('ShaderNodeBsdfPrincipled');out=n.new('ShaderNodeOutputMaterial')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if 'Specular IOR Level' in p.inputs:p.inputs['Specular IOR Level'].default_value=.20 if fabric or 'Rubber' in name or 'Nomex' in name else .38
    if 'Coat Weight' in p.inputs:p.inputs['Coat Weight'].default_value=coat
    if 'Coat Roughness' in p.inputs:p.inputs['Coat Roughness'].default_value=.13 if coat else .35
    if 'Transmission Weight' in p.inputs:p.inputs['Transmission Weight'].default_value=transmission
    m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);out.location=(500,0);p.location=(220,0)
    if fabric:
        tc=n.new('ShaderNodeTexCoord');tc.location=(-800,0)
        noise=n.new('ShaderNodeTexNoise');noise.location=(-580,0);noise.inputs['Scale'].default_value=235;noise.inputs['Detail'].default_value=2.2;noise.inputs['Roughness'].default_value=.72
        wave=n.new('ShaderNodeTexWave');wave.location=(-580,-220);wave.wave_type='BANDS';wave.bands_direction='X';wave.inputs['Scale'].default_value=250;wave.inputs['Distortion'].default_value=3
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.28;mix.location=(-300,-40)
        bump=n.new('ShaderNodeBump');bump.location=(-40,-80);bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.003
        m.node_tree.links.new(tc.outputs['Generated'],noise.inputs['Vector']);m.node_tree.links.new(tc.outputs['Generated'],wave.inputs['Vector'])
        m.node_tree.links.new(noise.outputs['Fac'],mix.inputs[1]);m.node_tree.links.new(wave.outputs['Color'],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    else:
        noise=n.new('ShaderNodeTexNoise');noise.location=(-420,-90);noise.inputs['Scale'].default_value=320;noise.inputs['Detail'].default_value=2
        bump=n.new('ShaderNodeBump');bump.location=(-80,-100);bump.inputs['Strength'].default_value=.045;bump.inputs['Distance'].default_value=.0007
        m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m

MAT={
 'suit':mat('Nomex_Black_Fabric',(.009,.012,.016),.78,fabric=True),
 'red':mat('Suit_Racing_Red',(.31,.012,.025),.69,fabric=True),
 'white':mat('Suit_Off_White',(.48,.52,.54),.69,fabric=True),
 'panel':mat('Suit_Reinforced_Charcoal',(.024,.029,.034),.72,fabric=True),
 'stitch':mat('Stitching_Silver',(.22,.24,.26),.64),
 'glove':mat('Glove_Leather',(.014,.018,.022),.5),
 'glove_red':mat('Glove_Red_Grip',(.34,.018,.026),.55),
 'rubber':mat('Boot_Rubber',(.009,.011,.013),.8),
 'sole':mat('Boot_Sole',(.02,.023,.026),.77),
 'helmet':mat('Helmet_Gloss_Black',(.009,.012,.018),.20,.24,.62),
 'helmet_red':mat('Helmet_Crimson_Lacquer',(.33,.012,.027),.22,.20,.55),
 'helmet_white':mat('Helmet_Pearl_White',(.63,.66,.67),.23,.12,.5),
 'visor':mat('Visor_Smoke_Polycarbonate',(.006,.012,.020),.115,.42,.85,transmission=.08),
 'hardware':mat('Helmet_Anodised_Hardware',(.17,.19,.21),.24,.78),
 'balaclava':mat('Balaclava_Knit',(.008,.010,.012),.78,fabric=True),
 'patch':mat('Suit_Label_Charcoal',(.04,.05,.06),.7,fabric=True)}

def link_obj(obj,collection=driver_col):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def new_mesh(name,verts,faces,material,collection=driver_col,subd=1):
    me=bpy.data.meshes.new(name+'_GEO');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
    ob=bpy.data.objects.new(name,me);collection.objects.link(ob)
    for p in me.polygons:p.use_smooth=True
    if subd:
        mod=ob.modifiers.new('Smooth anatomical surface','SUBSURF');mod.levels=subd;mod.render_levels=subd
    return ob

def ellipsoid(name,center,radii,material,collection=driver_col,segments=32,rings=20,subd=1):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=center)
    ob=bpy.context.object;ob.name=name
    for v in ob.data.vertices:v.co.x*=radii[0];v.co.y*=radii[1];v.co.z*=radii[2]
    ob.data.materials.clear();ob.data.materials.append(material)
    for p in ob.data.polygons:p.use_smooth=True
    if subd:
        mod=ob.modifiers.new('Silhouette refinement','SUBSURF');mod.levels=subd;mod.render_levels=subd
    return link_obj(ob,collection)

def tube_mesh(name,points,radius,material,collection=details_col,segments=8):
    curve=bpy.data.curves.new(name+'_curve','CURVE');curve.dimensions='3D';curve.resolution_u=2;curve.bevel_depth=radius;curve.bevel_resolution=3
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):p.co=(*co,1)
    ob=bpy.data.objects.new(name,curve);collection.objects.link(ob);ob.data.materials.append(material);return ob

def loft_segment(name,a,b,profile,material,bones,collection=driver_col,radial=24,subd=2):
    a=Vector(a);b=Vector(b);axis=(b-a).normalized();ref=Vector((0,1,0));u=ref-axis*ref.dot(axis)
    if u.length<.05:u=Vector((1,0,0))-axis*axis.x
    u.normalize();v=axis.cross(u).normalized()
    verts=[];faces=[];ts=[]
    for t,ru,rv,bulge in profile:
        center=a.lerp(b,t)+v*bulge
        for j in range(radial):
            q=j*math.tau/radial
            verts.append(tuple(center+u*(ru*math.cos(q))+v*(rv*math.sin(q))))
        ts.extend([t]*radial)
    for r in range(len(profile)-1):
        for j in range(radial):q=r*radial+j;n=r*radial+(j+1)%radial;faces.append((q,n,n+radial,q+radial))
    faces += [tuple(range(radial-1,-1,-1)),tuple((len(profile)-1)*radial+j for j in range(radial))]
    ob=new_mesh(name,verts,faces,material,collection,subd)
    if bones:SEGMENTS[ob.name]=(bones,ts)
    return ob

def curve_path(name,points,bevel,material,parent_bone=None):
    ob=tube_mesh(name,points,bevel,material)
    if parent_bone:rigid_bind(ob,parent_bone)
    return ob

def rigid_bind(obj,bone):
    world=obj.matrix_world.copy();obj.parent=rig;obj.parent_type='BONE';obj.parent_bone=bone;obj.matrix_world=world

SEGMENTS={};TORSO_OBJS=[];HARD_OBJS=[]

# The rest pose is the actual kart-driving pose. Names match UE5 mannequin conventions where practical.
armdata=bpy.data.armatures.new('SKEL_KartDriver');rig=bpy.data.objects.new('SK_KartDriver_Armature',armdata);driver_col.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
eb={}
def bone(name,head,tail,parent=None,deform=True,connected=False):
    b=armdata.edit_bones.new(name);b.head=Vector(head);b.tail=Vector(tail);b.use_deform=deform
    if parent:b.parent=eb[parent];b.use_connect=connected
    eb[name]=b;return b

bone('root',(0,0,.35),(0,0,.45),None,False)
bone('pelvis',(-.145,0,.435),(-.15,0,.49),'root')
bone('spine_01',(-.15,0,.49),(-.155,0,.57),'pelvis',True,True)
bone('spine_02',(-.155,0,.57),(-.165,0,.665),'spine_01',True,True)
bone('spine_03',(-.165,0,.665),(-.17,0,.745),'spine_02',True,True)
bone('spine_04',(-.17,0,.745),(-.17,0,.80),'spine_03',True,True)
bone('neck_01',(-.17,0,.80),(-.17,0,.89),'spine_04',True,True)
bone('head',(-.17,0,.89),(-.17,0,1.09),'neck_01',True,True)
for s,suffix in [(-1,'l'),(1,'r')]:
    bone('clavicle_'+suffix,(-.13,0,.75),SHOULDER[s],'spine_03')
    bone('upperarm_'+suffix,SHOULDER[s],ELBOW[s],'clavicle_'+suffix,True,True)
    bone('lowerarm_'+suffix,ELBOW[s],WRIST[s],'upperarm_'+suffix,True,True)
    palm=WRIST[s]+Vector((.065,0,.006))
    bone('hand_'+suffix,WRIST[s],palm,'lowerarm_'+suffix,True,True)
    for fi,finger in enumerate(('thumb','index','middle','ring','pinky')):
        yoff=s*(.042-.020*fi)
        rootp=palm+Vector((.018,yoff,0))
        sign=1 if finger=='thumb' else 0
        endp=rootp+Vector((.018, s*(.020 if finger=='thumb' else -.002), -.018 if finger=='thumb' else -.012))
        bname=f'{finger}_01_{suffix}';bone(bname,rootp,endp,'hand_'+suffix,True)
        prev=bname
        for j in (2,3):
            p0=eb[prev].tail.copy();p1=p0+Vector((.018,s*.006,-.012 if j==2 else -.006))
            bname=f'{finger}_{j:02d}_{suffix}';bone(bname,p0,p1,prev,True,True);prev=bname
    hip=HIP+Vector((0,s*.115,0));knee=KNEE[s];ankle=ANKLE[s];toe=TOE[s]
    bone('thigh_'+suffix,hip,knee,'pelvis')
    bone('calf_'+suffix,knee,ankle,'thigh_'+suffix,True,True)
    bone('foot_'+suffix,ankle,toe,'calf_'+suffix,True,True)
    ball=toe+Vector((.065,0,-.008));bone('ball_'+suffix,toe,ball,'foot_'+suffix,True,True)
    for i in range(5):
        yoff=s*(.033-.015*i);p0=ball+Vector((0,yoff,0));p1=p0+Vector((.025,s*.004,-.004));bone(f'toe_{i+1:02d}_{suffix}',p0,p1,'ball_'+suffix)
    # Eye lines are hidden by the smoke visor, but preserve the full biped hierarchy.
    bone('eye_'+suffix,(-.02,s*.035,1.015),(.015,s*.035,1.015),'head',False)
    bone('CTRL_ElbowPole_'+suffix,ELBOW[s]+Vector((0,s*.24,.02)),ELBOW[s]+Vector((0,s*.24,.12)),'root',False)
    bone('CTRL_HandIK_'+suffix,WRIST[s],WRIST[s]+Vector((.02,0,0)),'root',False)
    bone('CTRL_KneePole_'+suffix,knee+Vector((-.05,s*.20,.12)),knee+Vector((-.05,s*.20,.20)),'root',False)
    bone('CTRL_FootIK_'+suffix,ankle,ankle+Vector((.03,0,0)),'root',False)
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=False;armdata.display_type='BBONE'

def armature_modifier(ob):
    ob.parent=rig;mod=ob.modifiers.new('UE5 deform skeleton','ARMATURE');mod.object=rig;mod.use_vertex_groups=True
    # Keep skinning ahead of final subdivision for smooth bending.
    if ob.modifiers and ob.modifiers[-1].type=='SUBSURF':ob.modifiers.move(len(ob.modifiers)-1,0)

def add_weights(ob,weights):
    groups={}
    for name in set(k for d in weights for k in d):groups[name]=ob.vertex_groups.new(name=name)
    for i,d in enumerate(weights):
        total=sum(max(0,w) for w in d.values())
        if total:
            for k,w in d.items():
                if w>1e-5:groups[k].add([i],max(0,w)/total,'REPLACE')
    armature_modifier(ob)

def segweights(ts,b0,b1,split=.72):
    out=[]
    for t in ts:
        w=max(0,min(1,(t-split)/(1-split)))
        out.append({b0:1-w,b1:w})
    return out

def torso_weights(z):
    chain=[('pelvis',.45),('spine_01',.525),('spine_02',.615),('spine_03',.705),('spine_04',.775),('neck_01',.845)]
    if z<=chain[0][1]:return {chain[0][0]:1.0}
    if z>=chain[-1][1]:return {chain[-1][0]:1.0}
    for i in range(len(chain)-1):
        n0,z0=chain[i];n1,z1=chain[i+1]
        if z0<=z<=z1:
            t=(z-z0)/(z1-z0);t=t*t*(3-2*t)
            return {n0:1-t,n1:t}

def torso_mesh(name,material):
    # Sculpted torso cross-sections: lumbar taper, rib cage, shoulder shelf and asymmetric seated lean.
    sections=[(.405,-.145,.105,.142),(.435,-.145,.135,.18),(.475,-.15,.138,.18),(.515,-.16,.122,.158),(.555,-.165,.132,.174),(.605,-.17,.151,.204),(.65,-.17,.157,.215),(.69,-.17,.15,.213),(.725,-.17,.133,.196),(.75,-.17,.108,.145),(.772,-.17,.087,.095),(.79,-.17,.076,.072)]
    verts=[];faces=[];weights=[];nr=48
    for z,cx,rx,ry in sections:
        for j in range(nr):
            a=j*math.tau/nr
            # Front of the suit faces +X. A shallow chest/sternum contour softens the silhouette.
            x=cx+rx*math.cos(a);y=ry*math.sin(a)
            if math.cos(a)>.65 and .57<z<.72:x+=.012*math.cos((z-.645)*math.pi*3)
            verts.append((x,y,z));weights.append(torso_weights(z))
    for k in range(len(sections)-1):
        for j in range(nr):q=k*nr+j;n=k*nr+(j+1)%nr;faces.append((q,n,n+nr,q+nr))
    faces += [tuple(range(nr-1,-1,-1)),tuple((len(sections)-1)*nr+j for j in range(nr))]
    ob=new_mesh(name,verts,faces,material,driver_col,2);add_weights(ob,weights);TORSO_OBJS.append(ob);return ob,sections

# Smooth torso and seated trouser/pant forms.
torso,torso_sections=torso_mesh('DRV_Suit_Torso_And_Pelvis',MAT['suit'])
for s,suffix in [(-1,'l'),(1,'r')]:
    hip=HIP+Vector((0,s*.115,0));knee=KNEE[s];ankle=ANKLE[s];toe=TOE[s]
    # Gentle joint overlap prevents visible gaps during IK motion; profiles model padded fabric over anatomy.
    thigh=loft_segment('DRV_Suit_Thigh_'+suffix,hip,knee,[(0,.046,.048,0),(.08,.078,.080,0),(.25,.094,.088,.006),(.48,.10,.084,.012),(.68,.088,.075,.006),(.88,.074,.065,0),(1,.053,.055,0)],MAT['suit'],('thigh_'+suffix,'calf_'+suffix),radial=32)
    add_weights(thigh,segweights(SEGMENTS[thigh.name][1],'thigh_'+suffix,'calf_'+suffix,.84))
    # Knee shell/pad and curved upper seam.
    pad=ellipsoid('DRV_Knee_Pad_'+suffix,knee+Vector((.012,0,0)),(.09,.078,.070),MAT['panel'],segments=32,rings=18)
    add_weights(pad,[{'thigh_'+suffix:.58,'calf_'+suffix:.42} for _ in pad.data.vertices])
    calf=loft_segment('DRV_Suit_Calf_'+suffix,knee,ankle,[(0,.052,.052,0),(.08,.067,.067,0),(.25,.074,.071,-.005),(.48,.070,.067,-.006),(.68,.061,.059,0),(.88,.050,.050,0),(1,.038,.042,0)],MAT['suit'],('calf_'+suffix,'foot_'+suffix),radial=28)
    add_weights(calf,segweights(SEGMENTS[calf.name][1],'calf_'+suffix,'foot_'+suffix,.86))
    # Shin guard and elastic gaiter.
    guard=ellipsoid('DRV_Shin_Guard_'+suffix,knee.lerp(ankle,.43)+Vector((.040,0,0)),(.067,.061,.105),MAT['panel'],segments=24,rings=16)
    add_weights(guard,[{'calf_'+suffix:1} for _ in guard.data.vertices])
    # Driver boots are a multi-section anatomical last with raised heel and rounded toe.
    footprof=[(0,.025,.035,0),(.10,.042,.048,0),(.34,.056,.056,.008),(.62,.061,.053,.012),(.83,.052,.045,.006),(.97,.034,.032,0),(1,.014,.018,0)]
    boot=loft_segment('DRV_Race_Boot_'+suffix,ankle,toe+Vector((.025,0,0)),footprof,MAT['rubber'],('foot_'+suffix,'ball_'+suffix),radial=32)
    add_weights(boot,segweights(SEGMENTS[boot.name][1],'foot_'+suffix,'ball_'+suffix,.88))
    # Ribbed ankle gaiter, layered sole and toe reinforcement.
    gaiter=ellipsoid('DRV_Boot_Cuff_'+suffix,ankle+Vector((-.015,0,.025)),(.060,.055,.066),MAT['panel'],segments=24,rings=16);add_weights(gaiter,[{'foot_'+suffix:.75,'calf_'+suffix:.25} for _ in gaiter.data.vertices])
    sole=loft_segment('DRV_Boot_Sole_'+suffix,ankle+Vector((-.03,0,-.027)),toe+Vector((.035,0,-.030)),[(0,.031,.016,0),(.2,.052,.018,0),(.78,.056,.018,0),(1,.026,.014,0)],MAT['sole'],('foot_'+suffix,'ball_'+suffix),radial=24,subd=1);add_weights(sole,segweights(SEGMENTS[sole.name][1],'foot_'+suffix,'ball_'+suffix,.9))
    # Stitching and molded panel seams follow the trouser and shoe shapes.
    for offset in [-.045,.045]:
        pts=[tuple(knee.lerp(ankle,t)+Vector((.064,offset*(1-t*.45),0))) for t in (.12,.30,.50,.70,.88)]
        curve_path('DRV_Shin_Stitch_'+suffix+str(offset),pts,.0014,MAT['stitch'],'calf_'+suffix)
    # Toe cap, red heel flashes and stitched boot panels.
    heel=ellipsoid('DRV_Boot_Red_Heel_'+suffix,ankle+Vector((-.038,s*.003,-.005)),(.043,.050,.033),MAT['red'],segments=24,rings=14);rigid_bind(heel,'foot_'+suffix)

# Broad shoulders and segmented arms, shaped with biceps/triceps and padded forearms.
for s,suffix in [(-1,'l'),(1,'r')]:
    shoulder=SHOULDER[s];elbow=ELBOW[s];wrist=WRIST[s]
    cap=ellipsoid('DRV_Shoulder_Cap_'+suffix,shoulder,(.085,.081,.086),MAT['suit'],segments=32,rings=20);add_weights(cap,[{'clavicle_'+suffix:.45,'upperarm_'+suffix:.55} for _ in cap.data.vertices])
    upper=loft_segment('DRV_Suit_UpperArm_'+suffix,shoulder,elbow,[(0,.055,.058,0),(.10,.074,.071,0),(.30,.081,.077,.006),(.52,.075,.072,.008),(.72,.063,.061,.004),(.90,.054,.052,0),(1,.047,.049,0)],MAT['suit'],('upperarm_'+suffix,'lowerarm_'+suffix),radial=28)
    add_weights(upper,segweights(SEGMENTS[upper.name][1],'upperarm_'+suffix,'lowerarm_'+suffix,.83))
    fore=loft_segment('DRV_Suit_Forearm_'+suffix,elbow,wrist,[(0,.049,.050,0),(.08,.058,.059,0),(.24,.069,.066,.004),(.48,.063,.061,.006),(.69,.056,.055,.004),(.86,.047,.048,0),(1,.040,.043,0)],MAT['suit'],('lowerarm_'+suffix,'hand_'+suffix),radial=28)
    add_weights(fore,segweights(SEGMENTS[fore.name][1],'lowerarm_'+suffix,'hand_'+suffix,.87))
    # Integrated cuff and hand in black/red leather; raised palms are fitted around the steering rim.
    cuff=loft_segment('DRV_Glove_Cuff_'+suffix,wrist-Vector((.05,0,0)),wrist+Vector((.025,0,0)),[(0,.044,.044,0),(.35,.049,.046,0),(.72,.049,.046,0),(1,.043,.043,0)],MAT['glove'],('lowerarm_'+suffix,'hand_'+suffix),radial=24,subd=1);add_weights(cuff,segweights(SEGMENTS[cuff.name][1],'lowerarm_'+suffix,'hand_'+suffix,.68))
    palmcenter=wrist+Vector((.025,s*.004,.005));palm=ellipsoid('DRV_Glove_Palm_'+suffix,palmcenter,(.073,.061,.052),MAT['glove'],segments=28,rings=18);add_weights(palm,[{'hand_'+suffix:1} for _ in palm.data.vertices])
    # Curled fingers hook around the wheel rim. Separate digit bones support later grip edits.
    for fi,finger in enumerate(('thumb','index','middle','ring','pinky')):
        yoff=s*(.043-.020*fi)
        start=palmcenter+Vector((.025,yoff,.002))
        if finger=='thumb':
            points=[start,start+Vector((.025,s*.018,.015)),start+Vector((.006,s*.031,.040))]
        else:
            points=[start,start+Vector((.018,s*.003,-.010)),start+Vector((.015,s*.003,-.027)),start+Vector((-.002,s*.001,-.034))]
        name='DRV_Glove_'+finger+'_'+suffix
        digitprof=[(0,.010,.011,0),(.18,.013,.013,0),(.42,.012,.012,0),(.68,.010,.010,0),(.9,.008,.008,0),(1,.004,.005,0)]
        proximal=loft_segment(name+'_Proximal',points[0],points[1],digitprof,MAT['glove'],(f'{finger}_01_{suffix}',),radial=16,subd=1);rigid_bind(proximal,f'{finger}_01_{suffix}')
        distal=loft_segment(name+'_Curled_Distal',points[1],points[-1],digitprof,MAT['glove'],(f'{finger}_02_{suffix}',),radial=16,subd=1);rigid_bind(distal,f'{finger}_02_{suffix}')
        knuckle=ellipsoid('DRV_Glove_Knuckle_'+finger+'_'+suffix,points[1],(.013,.012,.011),MAT['glove_red'],segments=16,rings=10,subd=0);rigid_bind(knuckle,f'{finger}_01_{suffix}')
    grip=ellipsoid('DRV_Glove_Red_Grip_'+suffix,palmcenter+Vector((.045,0,.015)),(.035,.050,.014),MAT['glove_red'],segments=20,rings=12);rigid_bind(grip,'hand_'+suffix)
    # Suit red/white identity bands and fine double-stitched seam lines.
    curve_path('DRV_Arm_Red_Stripe_'+suffix,[tuple(shoulder.lerp(elbow,t)+Vector((.025,s*.046,0))) for t in (.12,.30,.50,.70,.88)],.006,MAT['red'],'upperarm_'+suffix)
    curve_path('DRV_Arm_White_Piping_'+suffix,[tuple(elbow.lerp(wrist,t)+Vector((.008,s*.047,0))) for t in (.12,.30,.52,.74,.91)],.0035,MAT['white'],'lowerarm_'+suffix)
    for t in (.22,.28,.34):
        base=elbow.lerp(wrist,t)
        curve_path('DRV_Elbow_Fold_'+suffix+str(t),[tuple(base+Vector((.012,s*y,z))) for y,z in [(-.035,-.018),(-.018,.004),(0,.012),(.018,.004),(.035,-.018)]],.002,MAT['panel'],'lowerarm_'+suffix)

# Tailored chest panels, zipper tape, collar, belt and seam piping are real surface meshes/curves.
def torso_patch(name,z0,z1,a0,a1,material):
    verts=[];faces=[];nr=10;rows=8
    def section(z):
        return min(torso_sections,key=lambda r:abs(r[0]-z))
    for i in range(rows+1):
        z=z0+(z1-z0)*i/rows;_,cx,rx,ry=section(z)
        for j in range(nr+1):
            a=a0+(a1-a0)*j/nr;x=cx+(rx+.003)*math.cos(a);y=(ry+.003)*math.sin(a);verts.append((x,y,z))
    for i in range(rows):
        for j in range(nr):q=i*(nr+1)+j;faces.append((q,q+1,q+nr+2,q+nr+1))
    ob=new_mesh(name,verts,faces,material,driver_col,1);add_weights(ob,[torso_weights(v[2]) for v in verts]);TORSO_OBJS.append(ob);return ob

torso_patch('DRV_Chest_Crimson_Racing_Panel',.615,.752,-.62,.62,MAT['red'])
torso_patch('DRV_Chest_White_Left_Panel',.55,.72,.72,1.19,MAT['white'])
torso_patch('DRV_Chest_White_Right_Panel',.55,.72,-1.19,-.72,MAT['white'])
curve_path('DRV_Suit_Central_Zipper',[(-.325,0,.75),(-.328,0,.71),(-.335,0,.66),(-.312,0,.61),(-.29,0,.56)],.0025,MAT['stitch'],'spine_02')
for s,suffix in [(-1,'l'),(1,'r')]:
    curve_path('DRV_Suit_Torso_Seam_'+suffix,[(-.24,s*.18,.74),(-.22,s*.20,.69),(-.19,s*.207,.63),(-.16,s*.17,.57),(-.13,s*.13,.51)],.002,MAT['stitch'],'spine_03')
    belt=loft_segment('DRV_Suit_Waist_Belt_'+suffix,(-.15,s*.15,.48),(-.15,s*.15,.50),[(0,.018,.025,0),(.4,.023,.024,0),(.8,.023,.024,0),(1,.018,.02,0)],MAT['panel'],('pelvis','spine_01'),radial=20,subd=1);add_weights(belt,[{'pelvis':.7,'spine_01':.3} for _ in SEGMENTS[belt.name][1]])

# Helmet neck skirt, aerodynamic shell, smoked visor, gasket and realistic side hardware.
collar=ellipsoid('DRV_Balaclava_And_Neck_Collar',(-.16,0,.855),(.092,.102,.073),MAT['balaclava'],segments=32,rings=20);add_weights(collar,[{'neck_01':.6,'head':.4} for _ in collar.data.vertices])
helmet_center=Vector((-.17,0,1.025));rx=.155;ry=.139;rz=.177
helmet=ellipsoid('DRV_FullFace_Helmet_Shell',helmet_center,(rx,ry,rz),MAT['helmet'],segments=64,rings=40,subd=1);add_weights(helmet,[{'head':1} for _ in helmet.data.vertices]);HARD_OBJS.append(helmet)
# Chin bar volume gives a proper full-face silhouette below the visor.
chin=ellipsoid('DRV_Helmet_Chin_Guard',(-.045,0,.925),(.103,.111,.070),MAT['helmet'],segments=40,rings=24,subd=1);add_weights(chin,[{'head':1} for _ in chin.data.vertices]);HARD_OBJS.append(chin)

def helmet_surface_patch(name,theta0,theta1,phi0,phi1,material,nu=28,nv=24):
    verts=[];faces=[]
    for i in range(nv+1):
        th=theta0+(theta1-theta0)*i/nv
        for j in range(nu+1):
            ph=phi0+(phi1-phi0)*j/nu
            verts.append((helmet_center.x+(rx+.002)*math.cos(th),helmet_center.y+(ry+.002)*math.sin(th)*math.cos(ph),helmet_center.z+(rz+.002)*math.sin(th)*math.sin(ph)))
    for i in range(nv):
        for j in range(nu):q=i*(nu+1)+j;faces.append((q,q+1,q+nu+2,q+nu+1))
    ob=new_mesh(name,verts,faces,material,driver_col,1);add_weights(ob,[{'head':1} for _ in verts]);HARD_OBJS.append(ob);return ob

# Visor is a curved polycarbonate cap over the complete eye port; oval gasket sits at its edge.
helmet_surface_patch('DRV_Smoked_Tinted_Visor',.14,1.04,0,math.tau,MAT['visor'],40,30)
visorline=[]
for i in range(81):
    ph=math.tau*i/80;th=1.045
    visorline.append((helmet_center.x+(rx+.006)*math.cos(th),helmet_center.y+(ry+.006)*math.sin(th)*math.cos(ph),helmet_center.z+(rz+.006)*math.sin(th)*math.sin(ph)))
curve_path('DRV_Visor_Seal_Gasket',visorline,.006,MAT['panel'],'head')
for s,suffix in [(-1,'l'),(1,'r')]:
    # Ratchet pivots and chin fasteners.
    pivot=ellipsoid('DRV_Visor_Pivot_'+suffix,(-.025,s*.132,1.005),(.027,.012,.027),MAT['hardware'],segments=24,rings=14,subd=1);rigid_bind(pivot,'head')
    screw=ellipsoid('DRV_Visor_Fastener_'+suffix,(-.014,s*.141,1.005),(.009,.004,.009),MAT['white'],segments=16,rings=10,subd=0);rigid_bind(screw,'head')
    # Shell color panels and hand-applied racing stripes.
    helmet_surface_patch('DRV_Helmet_Red_Cheek_'+suffix,.93,1.48,(-.94 if s<0 else .94),(-.14 if s<0 else .14),MAT['helmet_red'],18,16)
    for j in range(4):
        x=-.045+j*.026
        vent=ellipsoid('DRV_Chin_Vent_'+suffix+str(j),(x,s*.087,.909),(.010,.006,.004),MAT['panel'],segments=12,rings=8,subd=0);rigid_bind(vent,'head')
# White crown stripe and red pinline follow the curved shell instead of floating decals.
for s,suffix in [(-1,'l'),(1,'r')]:
    pts=[]
    for i in range(15):
        th=.30+i*.086;ph=s*.16
        pts.append((helmet_center.x+(rx+.004)*math.cos(th),helmet_center.y+(ry+.004)*math.sin(th)*math.cos(ph),helmet_center.z+(rz+.004)*math.sin(th)*math.sin(ph)))
    curve_path('DRV_Helmet_Crown_White_'+suffix,pts,.009,MAT['helmet_white'],'head')
    curve_path('DRV_Helmet_Crown_Red_'+suffix,[tuple(Vector(p)+Vector((.002,s*.014,0))) for p in pts],.0035,MAT['helmet_red'],'head')
# Rear shell vent, top intake and moulded center brow.
for i in range(3):
    vent=ellipsoid('DRV_Helmet_Top_Exhaust_'+str(i),(-.218+i*.018,0,1.169),(.018,.038,.005),MAT['panel'],segments=20,rings=10,subd=0);rigid_bind(vent,'head')
intake=ellipsoid('DRV_Helmet_Crown_Intake',(-.17,0,1.183),(.054,.051,.018),MAT['helmet_red'],segments=28,rings=16);rigid_bind(intake,'head')

# Tiny suit panels and padded shoulder tabs, all attached to deforming bones.
for s,suffix in [(-1,'l'),(1,'r')]:
    tab=ellipsoid('DRV_Shoulder_White_Tab_'+suffix,SHOULDER[s]+Vector((.008,s*.015,.053)),(.063,.047,.019),MAT['white'],segments=24,rings=14);add_weights(tab,[{'clavicle_'+suffix:.45,'upperarm_'+suffix:.55} for _ in tab.data.vertices])
    stripe=curve_path('DRV_Shoulder_Red_Accent_'+suffix,[tuple(SHOULDER[s]+Vector((.026,s*y,z))) for y,z in [(.00,.060),(.035,.048),(.055,.018),(.072,-.012)]],.006,MAT['red'],'clavicle_'+suffix)
    label=ellipsoid('DRV_Arm_Patch_'+suffix,ELBOW[s]+Vector((.025,s*.04,.048)),(.029,.004,.019),MAT['patch'],segments=20,rings=12);rigid_bind(label,'lowerarm_'+suffix)

# Ensure all driver geometry is rigged and uses clean, named UV channels for Unreal.
for ob in [o for o in driver_col.objects if o.type=='MESH']:
    if ob.name not in SEGMENTS and not any(vg.name in ('pelvis','spine_01') for vg in ob.vertex_groups):
        # Hard shell/trim is rigidly skinned to the head or its host bone by its preassigned group.
        pass
    if not any(m.type=='ARMATURE' for m in ob.modifiers):
        if not ob.vertex_groups:
            group=ob.vertex_groups.new(name='head');group.add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
        armature_modifier(ob)
    if ob.data.uv_layers.active is None:
        uv=ob.data.uv_layers.new(name='Driver_UV');bpy.context.view_layer.objects.active=ob;ob.select_set(True)
        try:bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(68),island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            if ob.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')

# Fuse the padded suit volumes into continuous sculpt-like geometry. This replaces
# the old capsule seams at shoulders, elbows, hips and knees instead of decorating them.
body_names={
 'DRV_Suit_Torso_And_Pelvis',
 'DRV_Suit_Thigh_l','DRV_Suit_Thigh_r','DRV_Suit_Calf_l','DRV_Suit_Calf_r',
 'DRV_Shoulder_Cap_l','DRV_Shoulder_Cap_r',
 'DRV_Suit_UpperArm_l','DRV_Suit_UpperArm_r','DRV_Suit_Forearm_l','DRV_Suit_Forearm_r',
}
body_parts=[bpy.data.objects[n] for n in body_names if n in bpy.data.objects]
for part in body_parts:
    bpy.ops.object.select_all(action='DESELECT');part.select_set(True);bpy.context.view_layer.objects.active=part
    for mod in list(part.modifiers):
        if mod.type=='SUBSURF':bpy.ops.object.modifier_apply(modifier=mod.name)
    for mod in list(part.modifiers):
        if mod.type=='ARMATURE':part.modifiers.remove(mod)
bpy.ops.object.select_all(action='DESELECT')
for part in body_parts:part.select_set(True)
body=bpy.data.objects['DRV_Suit_Torso_And_Pelvis'];bpy.context.view_layer.objects.active=body
bpy.ops.object.join();body.name='DRV_Sculpted_Continuous_Suit'
for group in list(body.vertex_groups):body.vertex_groups.remove(group)
body.data.materials.clear();body.data.materials.append(MAT['suit'])
remesh=body.modifiers.new('Continuous tailored suit sculpt','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.010;remesh.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth=body.modifiers.new('Cloth form relaxation','SMOOTH');smooth.factor=.55;smooth.iterations=4
bpy.ops.object.modifier_apply(modifier=smooth.name)
for poly in body.data.polygons:poly.use_smooth=True

def point_segment_distance(point,a,b):
    ab=b-a;den=max(ab.length_squared,1e-12);t=max(0.0,min(1.0,(point-a).dot(ab)/den))
    return (point-(a+ab*t)).length

bone_segments={}
for name in ['pelvis','spine_01','spine_02','spine_03','spine_04','neck_01',
            'clavicle_l','clavicle_r','upperarm_l','upperarm_r','lowerarm_l','lowerarm_r','hand_l','hand_r',
            'thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r']:
    b=armdata.bones.get(name)
    if b:bone_segments[name]=(b.head_local.copy(),b.tail_local.copy())
weights=[]
for vertex in body.data.vertices:
    p=vertex.co
    side='l' if p.y<0 else 'r'
    if p.z>.565 and abs(p.y)>.112:
        candidates=[f'clavicle_{side}',f'upperarm_{side}',f'lowerarm_{side}',f'hand_{side}']
    elif p.z<.555 and abs(p.y)>.072 and p.x>-.28:
        candidates=[f'thigh_{side}',f'calf_{side}',f'foot_{side}']
    else:
        weights.append(torso_weights(p.z));continue
    ranked=sorted((point_segment_distance(p,*bone_segments[n]),n) for n in candidates if n in bone_segments)[:2]
    raw=[1.0/(d+.018)**3 for d,_ in ranked];total=sum(raw) or 1.0
    weights.append({n:w/total for w,(_,n) in zip(raw,ranked)})
add_weights(body,weights)
sub=body.modifiers.new('Subdivision - soft fabric silhouette','SUBSURF');sub.levels=1;sub.render_levels=1
body.data.uv_layers.new(name='Driver_UV')
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
try:bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(68),island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
except Exception:
    if body.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')

# Steering pivot moves the copied kart wheel and hand targets together; source kart file is untouched.
steer=bpy.data.objects.new('CTRL_SteeringPivot',None);details_col.objects.link(steer);steer.location=(.62,0,.70);steer.empty_display_type='CIRCLE';steer.empty_display_size=.07;steer.hide_render=True
bpy.context.view_layer.update()  # Evaluate its world matrix before computing parent inverses.
for ob in list(bpy.data.objects):
    if ob.name.startswith('SK_Kart_Steering_Column_And_Wheel_'):
        # Preserve the mesh's absolute-coordinate vertex data while letting the parent rotate about wheel center.
        ob.parent=steer;ob.matrix_parent_inverse=steer.matrix_world.inverted()

hand_targets={};foot_targets={};pole_targets={}
for s,suffix in [(-1,'l'),(1,'r')]:
    target=bpy.data.objects.new('CTRL_HandTarget_'+suffix,None);details_col.objects.link(target);target.location=WRIST[s];target.empty_display_type='SPHERE';target.empty_display_size=.025;target.hide_render=True
    target.parent=steer;target.matrix_parent_inverse=steer.matrix_world.inverted();hand_targets[suffix]=target
    pole=bpy.data.objects.new('CTRL_ElbowPole_'+suffix,None);details_col.objects.link(pole);pole.location=ELBOW[s]+Vector((0,s*.22,.04));pole.empty_display_type='CIRCLE';pole.empty_display_size=.035;pole.hide_render=True;pole_targets[suffix]=pole
    ik=rig.pose.bones['lowerarm_'+suffix].constraints.new('IK');ik.name='Steering grip IK';ik.target=target;ik.pole_target=pole;ik.chain_count=2;ik.use_stretch=False
    rot=rig.pose.bones['hand_'+suffix].constraints.new('COPY_ROTATION');rot.name='Follow steering wheel grip';rot.target=target;rot.owner_space='WORLD';rot.target_space='WORLD';rot.mix_mode='REPLACE'
    ft=bpy.data.objects.new('CTRL_FootTarget_'+suffix,None);details_col.objects.link(ft);ft.location=ANKLE[s];ft.empty_display_type='SPHERE';ft.empty_display_size=.025;ft.hide_render=True;foot_targets[suffix]=ft
    fp=bpy.data.objects.new('CTRL_KneePole_'+suffix,None);details_col.objects.link(fp);fp.location=KNEE[s]+Vector((-.06,s*.22,.02));fp.empty_display_type='CIRCLE';fp.empty_display_size=.04;fp.hide_render=True
    fik=rig.pose.bones['calf_'+suffix].constraints.new('IK');fik.name='Pedal foot IK';fik.target=ft;fik.pole_target=fp;fik.chain_count=2;fik.use_stretch=False

# Simple animation: wheel steer oscillation, control-linked hands, pedal heel flex and subtle head/torso lean.
scene.frame_start=1;scene.frame_end=48;scene.render.fps=24
for frame,angle in [(1,0),(13,.23),(25,0),(37,-.23),(49,0)]:
    scene.frame_set(frame);steer.rotation_euler[0]=angle;steer.keyframe_insert(data_path='rotation_euler',frame=frame,group='Steering | wheel and hands')
    for sfx,sgn in [('l',-1),('r',1)]:
        ft=foot_targets[sfx];ft.location.z=ANKLE[sgn].z+(.012 if frame in (13,37) else 0);ft.location.x=ANKLE[sgn].x+(.012 if frame in (13,37) else 0);ft.keyframe_insert(data_path='location',frame=frame,group='Pedals | foot targets')
    head=rig.pose.bones['head'];head.rotation_mode='XYZ';head.rotation_euler=(0,0,angle*.14);head.keyframe_insert(data_path='rotation_euler',frame=frame,group='Driver | cornering')
    spine=rig.pose.bones['spine_03'];spine.rotation_mode='XYZ';spine.rotation_euler=(0,0,-angle*.11);spine.keyframe_insert(data_path='rotation_euler',frame=frame,group='Driver | cornering')
if rig.animation_data and rig.animation_data.action:rig.animation_data.action.name='Driving_Steer_Pedals_48f'

# Static details, seamless studio render rig, four requested views.
def add_area(name,loc,power,color,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
    ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();return ob

def add_camera(name,loc,target,lens=52):
    d=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;return ob

ground=bpy.data.objects.get('Studio Ground (render only)')
if not ground:
    gm=bpy.data.meshes.new('DriverStudioGround');gm.from_pydata([(-100,-100,-.025),(100,-100,-.025),(100,100,-.025),(-100,100,-.025)],[],[(0,1,2,3)])
    ground=bpy.data.objects.new('Studio Ground (render only)',gm);scene.collection.objects.link(ground)
    gmat=mat('Driver_Studio_Ground',(.035,.043,.052),.84);gm.materials.append(gmat)
ground.hide_set(True)
add_area('DRV_Studio_Key',(2.6,-3.5,3.0),750,(1.0,.82,.68),2.8,(0,0,.58))
add_area('DRV_Studio_Fill',(1.6,3.2,2.7),590,(.68,.80,1),2.7,(0,0,.63))
add_area('DRV_Studio_Rim',(-2.8,.3,2.8),900,(1,.58,.42),2.3,(-.15,0,.64))
add_area('DRV_Studio_Soft',(0,-.3,4.2),450,(1,1,1),2.0,(0,0,.62))
if not scene.world:scene.world=bpy.data.worlds.new('Kart driver studio')
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.15,.19,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.30

cams={
 'front':add_camera('DRV_Camera_Front_ThreeQuarter',(2.8,-3.9,2.05),(-.02,0,.57),52),
 'side':add_camera('DRV_Camera_Side_Profile',(.05,-4.0,1.28),(-.02,0,.59),56),
 'rear':add_camera('DRV_Camera_Rear_ThreeQuarter',(-3.15,-2.8,1.75),(-.18,0,.55),54),
 'cockpit':add_camera('DRV_Camera_Cockpit_OverShoulder',(1.25,-1.25,1.42),(.02,0,.62),48),
 'driver_perspective':add_camera('DRV_Camera_Driver_Eye_POV',(-.12,0,1.015),(.95,0,.54),38)}
hero=add_camera('DRV_Camera_Animation_Preview',(2.8,-3.9,2.05),(-.02,0,.57),52)
scene.camera=hero;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1280;scene.render.resolution_y=880;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene['KartDriver']='Procedural adult kart driver fitted to the existing kart; rigged and animated.'
scene['Fit']='Metric; +X forward; hand IK follows steering-wheel pivot; foot IK follows pedal target controls.'
scene['Fit_Measurements']={
 'seat_dimensions_m': [round(seat_bounds[i][1]-seat_bounds[i][0],3) for i in range(3)],
 'steering_center_m': [.62,0,.70],
 'pedal_region_center_m': [.53,0,.15],
 'driver_pose': {'pelvis_m':list(HIP),'left_hand_m':list(WRIST[-1]),'right_hand_m':list(WRIST[1]),'left_knee_m':list(KNEE[-1]),'right_knee_m':list(KNEE[1]),'left_ankle_m':list(ANKLE[-1]),'right_ankle_m':list(ANKLE[1])},
}

renders=OUT/'Renders';renders.mkdir(exist_ok=True)
helmet_objects=[o for o in bpy.data.objects if any(t in o.name.lower() for t in ('helmet','visor','balaclava'))]
for name,camera_ob in cams.items():
    scene.camera=camera_ob;scene.render.filepath=str(renders/(name+'.png'));scene.frame_set(1)
    # A driver's-eye view starts inside the helmet; hide helmet shell/trim only for this camera.
    saved_visibility=[ob.hide_render for ob in helmet_objects]
    if name=='driver_perspective':
        for ob in helmet_objects:ob.hide_render=True
    bpy.ops.render.render(write_still=True)
    if name=='driver_perspective':
        for ob,hidden in zip(helmet_objects,saved_visibility):ob.hide_render=hidden

# This Blender build omits FFmpeg encoding, so render an actual image sequence for the preview.
scene.camera=hero;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=480;scene.render.resolution_y=330;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';preview_dir=OUT/'AnimationPreview';preview_dir.mkdir(exist_ok=True)
scene.render.filepath=str(preview_dir/'frame_');scene.frame_start=1;scene.frame_end=48;bpy.ops.render.render(animation=True)

# Save the full fitted scene separately; the source kart asset remains unchanged.
scene.camera=hero;scene.frame_start=1;scene.frame_end=49;scene.frame_set(1)
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1280;scene.render.resolution_y=880;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'Kart_With_Driver.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_With_Driver.blend'))

# Export only the rigged driver for UE5.8.3, with baked steering/pedal animation and embedded textures.
driver_meshes=[o for o in driver_col.objects if o.type=='MESH']
# Curved seams and piping are authored as editable Blender curves; make temporary mesh copies for FBX.
export_curves=[]
for source in [o for o in details_col.objects if o.type=='CURVE']:
    duplicate=source.copy();duplicate.data=source.data.copy();scene.collection.objects.link(duplicate);export_curves.append(duplicate)
bpy.ops.object.select_all(action='DESELECT')
for ob in export_curves:ob.select_set(True)
if export_curves:
    bpy.context.view_layer.objects.active=export_curves[0];bpy.ops.object.convert(target='MESH')
export_detail_meshes=[o for o in scene.objects if o.type=='MESH' and o.name not in {m.name for m in driver_meshes} and o.name.startswith('DRV_')]
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for ob in driver_meshes+export_detail_meshes:ob.select_set(True)
bpy.context.view_layer.objects.active=rig
fbx=OUT/'Kart_Driver_UE58.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_anim=True,bake_anim_use_all_bones=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=True,bake_anim_step=1,add_leaf_bones=False,mesh_smooth_type='FACE',use_mesh_modifiers=True,path_mode='COPY',embed_textures=True,use_custom_props=True)
for ob in export_detail_meshes:
    if ob.name in bpy.data.objects:bpy.data.objects.remove(ob,do_unlink=True)

# A standalone editable driver .blend contains only the character, skeleton, controls, and their materials.
keep=set(driver_col.objects)|set(details_col.objects)|{rig}
for ob in list(bpy.data.objects):
    if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
for col in list(bpy.data.collections):
    if col not in (driver_col,details_col):bpy.data.collections.remove(col)
for child in list(scene.collection.children):
    if child not in (driver_col,details_col):
        scene.collection.children.unlink(child)
        if child.users==0:bpy.data.collections.remove(child)
for ob in list(scene.objects):
    if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
scene.camera=None;scene.render.filepath='//';scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Kart_Driver_Rig.blend'))

manifest={
 'source_kart':str(KART),'units':'meters','forward_axis':'+X','mesh_objects':len(driver_meshes),
 'armature':'SK_KartDriver_Armature','deform_bones':sum(1 for b in armdata.bones if b.use_deform),
 'all_driver_meshes_skinned':all(any(m.type=='ARMATURE' and m.object==rig for m in ob.modifiers) for ob in driver_meshes),
 'seat_bounds_m':seat_bounds,'steering_wheel_bounds_m':wheel_bounds,'pedal_bounds_m':pedal_bounds,
 'hand_ik_controls':['CTRL_HandTarget_l','CTRL_HandTarget_r'],'foot_ik_controls':['CTRL_FootTarget_l','CTRL_FootTarget_r'],
 'animation':'Driving_Steer_Pedals_48f','fbx':fbx.name,'renders':['Renders/front.png','Renders/side.png','Renders/rear.png','Renders/cockpit.png','Renders/driver_perspective.png'],'animation_preview':'AnimationPreview/frame_0001.png through frame_0048.png'}
(OUT/'driver_manifest.json').write_text(json.dumps(manifest,indent=2))
print('DRIVER_BUILD_COMPLETE',json.dumps(manifest),flush=True)

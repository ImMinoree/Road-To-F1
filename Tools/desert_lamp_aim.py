"""Aim existing floodlights at the verified racing loop; preserve all other actors."""
import unreal as u, json, math
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve(); E=R/'Evidence/LampAim'; E.mkdir(parents=True,exist_ok=True)
L=u.get_editor_subsystem(u.LevelEditorSubsystem); A=u.get_editor_subsystem(u.EditorActorSubsystem)
route=json.loads((R/'Art/DesertRoute/audit.json').read_text())['route_cm']
report={}
for name in ['DesertKarting','DesertKarting_Visual']:
    path='/Game/RoadToF1/Maps/'+name
    assert L.load_level(path)
    cp='/Game/RoadToF1/Checkpoints/'+name+'_BeforeLampAim'
    if not u.EditorAssetLibrary.does_asset_exist(cp):
        assert u.EditorAssetLibrary.duplicate_asset(path,cp)
    entries=[]
    for a in A.get_all_level_actors():
        if not isinstance(a,u.SpotLight) or not a.get_actor_label().startswith('GH_FloodPool_'): continue
        p=a.get_actor_location(); old=a.get_actor_rotation(); target=None; nearest=float('inf')
        for i,q in enumerate(route):
            b=route[(i+1)%len(route)]; dx=b[0]-q[0]; dy=b[1]-q[1]
            t=max(0.,min(1.,((p.x-q[0])*dx+(p.y-q[1])*dy)/max(dx*dx+dy*dy,1e-8)))
            x=q[0]+dx*t; y=q[1]+dy*t; d=(p.x-x)**2+(p.y-y)**2
            if d<nearest: nearest=d; target=u.Vector(x,y,0)
        delta=target-p; dist=math.sqrt(delta.x**2+delta.y**2+delta.z**2)
        rot=u.Rotator(pitch=math.degrees(math.atan2(delta.z,math.hypot(delta.x,delta.y))),yaw=math.degrees(math.atan2(delta.y,delta.x)))
        a.set_actor_rotation(rot,False); a.set_actor_hidden_in_game(False)
        c=a.light_component; c.set_visibility(True)
        c.set_editor_property('attenuation_radius',max(3500.,dist+1600.))
        c.set_editor_property('inner_cone_angle',24.); c.set_editor_property('outer_cone_angle',42.)
        # Existing 35,000 lm / 4800 K output and shadow budget remain unchanged.
        entries.append(dict(actor=a.get_actor_label(),position_cm=[p.x,p.y,p.z],old_rotation=str(old),new_rotation=str(rot),target_cm=[target.x,target.y,target.z],distance_cm=dist,intensity=c.get_editor_property('intensity'),radius_cm=c.get_editor_property('attenuation_radius')))
    assert len(entries)==4,entries
    assert L.save_current_level()
    report[name]=entries
(E/'aim.json').write_text(json.dumps(report,indent=2))
